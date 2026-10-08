"""Completed BEV runs must satisfy range and mass/energy balance together."""

from copy import deepcopy
from unittest.mock import patch

import numpy as np
import pytest
import xarray as xr
from carculator_utils.energy_consumption import EnergyConsumptionModel
from carculator_utils.numerical import ConvergenceError

from carculator import (
    CarInputParameters,
    CarModel,
    InventoryCar,
    fill_xarray_from_input_parameters,
)

CHEMISTRIES = ["LFP", "NMC-111", "NMC-622", "NMC-811"]


def inputs(years=(2020, 2025), powertrains=("BEV",), samples=False):
    parameters = CarInputParameters()
    parameters.static()
    _, array = fill_xarray_from_input_parameters(
        parameters,
        scope={
            "size": ["Medium"],
            "powertrain": list(powertrains),
            "year": list(years),
        },
    )
    if samples:
        array = array.isel(value=[0, 0]).assign_coords(value=["reference", "loaded"])
        array.loc[dict(parameter="cargo mass", value="loaded")] += 300
    return array


def run(array, **kwargs):
    model = CarModel(array, cycle="WLTC", **kwargs)
    model.set_all()
    return model


def assert_energy_consistent(model):
    # Freeze the completed vehicle, recompute only its cycle energy, and check
    # that the published pack can deliver the published range at that mass.
    frozen = deepcopy(model)
    frozen.calculate_ttw_energy()
    np.testing.assert_allclose(frozen["TtW energy"], model["TtW energy"], rtol=1e-5)
    expected_range = (
        model["electric energy stored"]
        * model["battery DoD"]
        * 3600
        / frozen["TtW energy"]
    )
    np.testing.assert_allclose(model["range"], expected_range, rtol=1e-5)


@pytest.mark.parametrize("chemistry", CHEMISTRIES)
def test_target_range_converges_each_year_sample_and_inventory(chemistry):
    array = inputs(samples=True)
    original_array = array.copy(deep=True)
    keys = [("BEV", "Medium", year) for year in [2020, 2025]]
    storage = {"electric": dict.fromkeys(keys, chemistry)}
    target = dict.fromkeys(keys, 400)
    original_storage = deepcopy(storage)
    masses = []
    original_energy = EnergyConsumptionModel.motive_energy_per_km

    def capture(self, *args, **kwargs):
        masses.append(kwargs["driving_mass"].copy(deep=True))
        return original_energy(self, *args, **kwargs)

    with patch.object(EnergyConsumptionModel, "motive_energy_per_km", capture):
        model = run(array, energy_storage=storage, target_range=target)

    xr.testing.assert_identical(array, original_array)
    assert storage == original_storage
    assert target == dict.fromkeys(keys, 400)
    np.testing.assert_allclose(masses[-1], model["driving mass"], rtol=1e-5)
    np.testing.assert_allclose(model["range"], 400, rtol=1e-6)
    np.testing.assert_allclose(
        model["power"],
        model["curb mass"] * model["power to mass ratio"] / 1000,
        rtol=1e-5,
    )
    np.testing.assert_allclose(
        model["energy battery mass"],
        model["electric energy stored"]
        / model["battery cell energy density"]
        / model["battery cell mass share"],
        rtol=1e-6,
    )
    assert_energy_consistent(model)
    assert (
        model["TtW energy"].sel(value="loaded")
        > model["TtW energy"].sel(value="reference")
    ).all()
    assert np.isfinite(model["total cost per km"]).all()

    inventory = InventoryCar(model, scenario="static", functional_unit="vkm")
    impacts = inventory.calculate_impacts()
    assert np.isfinite(impacts).all()
    electricity_row = inventory.find_input_indices(
        ("electricity supply for electric vehicles",)
    )
    transport_col = inventory.find_input_indices(("transport, car,", "BEV", "Medium"))
    assert len(electricity_row) == len(transport_col) == 1
    expected_grid = (
        (
            model["TtW energy"]
            / 3600
            / model["battery charge efficiency"]
            / model["charger efficiency"]
        )
        .sel(size="Medium", powertrain="BEV")
        .transpose("value", "year")
    )
    np.testing.assert_allclose(
        -inventory.A[:, electricity_row[0], transport_col[0], :],
        expected_grid,
        rtol=1e-6,
    )
    battery_name = chemistry.replace("-", "")
    battery_row = inventory.find_input_indices(
        (f"market for battery, Li-ion, {battery_name}",)
    )
    car_col = [
        i
        for i, activity in inventory.rev_inputs.items()
        if activity[0].startswith("car, ")
        and "BEV" in activity[0]
        and "Medium" in activity[0]
    ]
    assert len(battery_row) == len(car_col) == 1
    expected_pack = (
        (model["energy battery mass"] * (1 + model["battery lifetime replacements"]))
        .sel(size="Medium", powertrain="BEV")
        .transpose("value", "year")
    )
    np.testing.assert_allclose(
        -inventory.A[:, battery_row[0], car_col[0], :], expected_pack, rtol=1e-6
    )


@pytest.mark.parametrize("chemistry", CHEMISTRIES)
def test_range_solution_matches_fresh_fixed_capacity_run(chemistry):
    array = inputs(years=(2025,))
    key = ("BEV", "Medium", 2025)
    storage = {"electric": {key: chemistry}}
    target_model = run(array, energy_storage=storage, target_range={key: 400})
    storage["capacity"] = {key: target_model["electric energy stored"].item()}
    capacity_model = run(array, energy_storage=storage)
    for parameter in ["driving mass", "power", "TtW energy", "range"]:
        np.testing.assert_allclose(
            capacity_model[parameter], target_model[parameter], rtol=1e-5
        )


@pytest.mark.parametrize("fixed", ["target_mass", "energy_consumption", "capacity"])
def test_target_range_preserves_other_override_contracts(fixed):
    array = inputs(years=(2025,))
    key = ("BEV", "Medium", 2025)
    models = []
    for chemistry in ["LFP", "NMC-811"]:
        storage = {"electric": {key: chemistry}}
        overrides = {}
        if fixed == "capacity":
            storage["capacity"] = {key: 50}
        else:
            overrides[fixed] = {key: 1900 if fixed == "target_mass" else 650}
        model = run(array, energy_storage=storage, target_range={key: 400}, **overrides)
        np.testing.assert_allclose(model["range"], 400, rtol=1e-6)
        assert_energy_consistent(model)
        if fixed == "target_mass":
            np.testing.assert_allclose(model["curb mass"], 1900)
        elif fixed == "energy_consumption":
            np.testing.assert_allclose(model["TtW energy"], 650, rtol=1e-6)
        else:
            reference = run(
                array,
                energy_storage={"electric": {key: chemistry}},
                target_range={key: 400},
            )
            np.testing.assert_allclose(
                model["electric energy stored"],
                reference["electric energy stored"],
                rtol=1e-5,
            )
        models.append(model)
    assert (
        models[0]["energy battery mass"].item()
        > models[1]["energy battery mass"].item()
    )
    if fixed == "capacity":
        # With free vehicle mass and modelled demand, chemistry affects both
        # consumption and the capacity needed for the same range.
        assert models[0]["TtW energy"].item() > models[1]["TtW energy"].item()
        assert (
            models[0]["electric energy stored"].item()
            > models[1]["electric energy stored"].item()
        )
    else:
        # Fixed total mass or fixed consumption can legitimately remove the
        # chemistry dependence of consumption and required nominal capacity.
        np.testing.assert_allclose(
            models[0]["TtW energy"], models[1]["TtW energy"], rtol=1e-6
        )


def test_range_override_does_not_change_other_vehicles_or_none_targets():
    array = inputs(powertrains=("BEV", "ICEV-p", "PHEV-p", "FCEV"))
    key = ("BEV", "Medium", 2025)
    baseline = run(array, energy_storage={"capacity": {("BEV", "Medium", 2020): 50}})
    model = run(
        array,
        energy_storage={"capacity": {("BEV", "Medium", 2020): 50}},
        target_range={key: 400},
    )
    for powertrain, year in [
        ("BEV", 2020),
        ("ICEV-p", 2025),
        ("PHEV-p", 2025),
        ("FCEV", 2025),
    ]:
        for parameter in [
            "TtW energy",
            "electric energy stored",
            "range",
            "driving mass",
        ]:
            selection = dict(powertrain=powertrain, year=year)
            np.testing.assert_allclose(
                model[parameter].sel(**selection),
                baseline[parameter].sel(**selection),
                rtol=1e-5,
            )
    none_model = run(
        array,
        energy_storage={"capacity": {("BEV", "Medium", 2020): 50}},
        target_range={key: None},
    )
    xr.testing.assert_identical(none_model.array, baseline.array)


def test_target_range_sizing_respects_iteration_limit():
    key = ("BEV", "Medium", 2025)
    with pytest.raises(ConvergenceError, match="iteration limit.*Medium"):
        run(inputs(years=(2025,)), target_range={key: 400}, max_iterations=1)
