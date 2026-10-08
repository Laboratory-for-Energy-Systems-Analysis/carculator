"""Explicit battery prices must reach completed vehicle costs."""

import numpy as np
import xarray as xr

from carculator import CarInputParameters, CarModel, fill_xarray_from_input_parameters


def test_explicit_battery_price_survives_cost_adjustment():
    inputs = CarInputParameters()
    inputs.static()
    _, array = fill_xarray_from_input_parameters(
        inputs,
        scope={"size": ["Medium"], "powertrain": ["BEV"], "year": [2025]},
    )
    models = []
    for price in (0, 500):
        model = CarModel(
            array,
            battery_costs={
                "energy battery cost per kWh": {("BEV", "Medium", 2025): price}
            },
        )
        model.set_all()
        np.testing.assert_allclose(model["energy battery cost per kWh"], price)
        models.append(model)
    low, high = models
    delta = low["electric energy stored"] * 500 * low["markup factor"]
    np.testing.assert_allclose(
        high["purchase cost"] - low["purchase cost"], delta, rtol=2e-6, atol=0.01
    )
    np.testing.assert_allclose(
        high["component replacement cost"] - low["component replacement cost"],
        delta * low["battery lifetime replacements"],
        rtol=2e-6,
        atol=0.01,
    )
    np.testing.assert_array_equal(high["TtW energy"], low["TtW energy"])


def test_multiyear_sensitivity_reference_matches_static_costs():
    inputs = CarInputParameters()
    inputs.static()
    scope = {
        "size": ["Medium"],
        "powertrain": ["BEV", "HEV-p", "FCEV", "ICEV-g"],
        "year": [2020, 2025, 2030],
    }
    _, array = fill_xarray_from_input_parameters(inputs, scope=scope)
    _, samples = fill_xarray_from_input_parameters(
        inputs, scope=scope, sensitivity=True
    )
    samples = samples.sel(value=["reference", "energy battery cost per kWh"])
    static = CarModel(array)
    static.set_all()
    sensitivity = CarModel(samples)
    sensitivity.set_all()
    # Every reference cost, physical result and emission must retain its year.
    np.testing.assert_allclose(
        sensitivity.array.sel(value="reference").values,
        static.array.squeeze("value").values,
        rtol=1e-6,
        atol=1e-5,
    )
    expected = [186.489944, 134.640593, 102.573113]
    np.testing.assert_allclose(
        sensitivity["energy battery cost per kWh"]
        .sel(powertrain="BEV", value="reference")
        .values.ravel(),
        expected,
        rtol=1e-6,
    )
    np.testing.assert_allclose(
        sensitivity["energy battery cost per kWh"]
        .sel(powertrain="BEV", value="energy battery cost per kWh")
        .values.ravel(),
        np.array(expected) * 1.1,
        rtol=1e-6,
    )


def test_seeded_complete_runs_repeat_costs_and_preserve_selected_draws():
    saved_state = np.random.get_state()
    arrays, models = [], []
    try:
        for _ in range(2):
            # Unrelated random draws must not alter the seed's model results.
            np.random.random(19)
            state = np.random.get_state()
            inputs = CarInputParameters()
            inputs.stochastic(3, seed=42)
            _, array = fill_xarray_from_input_parameters(
                inputs,
                scope={
                    "size": ["Medium"],
                    "powertrain": ["BEV", "FCEV", "ICEV-g"],
                    "year": [2025, 2030],
                },
            )
            original = array.copy(deep=True)
            model = CarModel(array)
            model.set_all()
            xr.testing.assert_identical(array, original)
            current = np.random.get_state()
            assert current[0] == state[0]
            np.testing.assert_array_equal(current[1], state[1])
            assert current[2:] == state[2:]
            arrays.append(array)
            models.append(model)
        xr.testing.assert_identical(arrays[0], arrays[1])
        xr.testing.assert_identical(models[0].array, models[1].array)
        xr.testing.assert_identical(models[0].energy, models[1].energy)
        assert np.isfinite(models[0]["purchase cost"]).all()
        assert (models[0]["purchase cost"] > 0).all()

        # One retained stochastic sample must not revert to static pricing.
        selection = {"year": [2030, 2025], "value": [2]}
        selected = CarModel(arrays[0].sel(selection))
        selected.set_all()
        for name in [
            "energy battery cost per kWh",
            "power battery cost per kW",
            "fuel tank cost per kg",
            "fuel cell cost per kW",
        ]:
            xr.testing.assert_identical(selected[name], models[0][name].sel(selection))

        # An absolute battery-price override remains independent of cost draws.
        explicit = CarModel(
            arrays[0].sel(year=[2025], powertrain=["BEV"]),
            battery_costs={
                "energy battery cost per kWh": {("BEV", "Medium", 2025): [0, 100, 500]}
            },
        )
        explicit.set_all()
        np.testing.assert_array_equal(
            explicit["energy battery cost per kWh"].values.ravel(), [0, 100, 500]
        )
    finally:
        np.random.set_state(saved_state)
