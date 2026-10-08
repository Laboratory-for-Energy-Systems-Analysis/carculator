"""Explicit battery prices must reach completed vehicle costs."""

import numpy as np
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
