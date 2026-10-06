"""Small formula tests: explicit inputs, no sizing loop or reference spreadsheet."""

from functools import lru_cache

import numpy as np
import pytest
import xarray as xr
from carculator import CarInputParameters, CarModel, fill_xarray_from_input_parameters
from hypothesis import given, settings
from hypothesis import strategies as st


@lru_cache(maxsize=1)
def parameter_template():
    ip = CarInputParameters()
    ip.static()
    _, array = fill_xarray_from_input_parameters(
        ip, scope={"size": ["Medium"], "powertrain": ["BEV"], "year": [2020]}
    )
    return xr.zeros_like(array, dtype=float)


def model_with(**parameters):
    model = CarModel(parameter_template().copy(deep=True))
    for name, value in parameters.items():
        model[name.replace("_", " ")] = value
    return model


@settings(max_examples=30, derandomize=True, deadline=None, database=None)
@given(
    base=st.floats(min_value=10, max_value=10000),
    reduction=st.floats(min_value=0, max_value=1),
    battery=st.floats(min_value=0, max_value=1000),
    passengers=st.integers(min_value=0, max_value=10),
    cargo=st.floats(min_value=0, max_value=1000),
)
def test_mass_balance(base, reduction, battery, passengers, cargo):
    model = model_with(
        glider_base_mass=base,
        lightweighting=reduction,
        battery_cell_mass=battery,
        average_passengers=passengers,
        average_passenger_mass=75,
        cargo_mass=cargo,
    )
    model.set_vehicle_masses()
    expected_curb = base * (1 - reduction) + battery
    expected_cargo = passengers * 75 + cargo
    assert model["curb mass"].item() == pytest.approx(expected_curb)
    assert model["total cargo mass"].item() == pytest.approx(expected_cargo)
    assert model["driving mass"].item() == pytest.approx(expected_curb + expected_cargo)


@pytest.mark.parametrize(
    "order",
    [
        ("value", "year", "parameter", "powertrain", "size"),
        ("parameter", "powertrain", "value", "size", "year"),
    ],
)
def test_labelled_axes_and_model_instances_are_independent(order):
    source = (
        parameter_template()
        .copy(deep=True)
        .isel(value=[0, 0])
        .assign_coords(value=["low", "high"])
    )
    source.loc[dict(parameter="glider base mass")] = xr.DataArray(
        [100.0, 200.0], dims="value", coords={"value": ["low", "high"]}
    )
    original = source.copy(deep=True)
    first = CarModel(source.transpose(*order))
    second = CarModel(source)
    first.set_vehicle_masses()
    np.testing.assert_allclose(first["curb mass"].values.ravel(), [100, 200])
    first["glider base mass"] = 999
    xr.testing.assert_identical(source, original)
    xr.testing.assert_identical(second.array, original)


@pytest.mark.parametrize("rate", [0.0, 0.05])
@pytest.mark.parametrize("annual_km", [1000.0, 2000.0])
@pytest.mark.parametrize("years", [5, 10])
def test_costs_follow_discounted_cash_flow(rate, annual_km, years):
    # Annual payments must repay the initial capital. Mid-life battery
    # replacement has a separately discounted present value.
    model = model_with(
        glider_base_mass=1000,
        markup_factor=1,
        interest_rate=rate,
        lifetime_kilometers=years * annual_km,
        kilometers_per_year=annual_km,
        average_passengers=2,
        battery_charge_efficiency=0.8,
        electric_energy_stored=10,
        battery_lifetime_replacements=1,
        glider_cost_slope=1,
        glider_cost_intercept=0,
    )
    model["energy battery cost per kWh"] = 100
    model["energy cost per kWh"] = 0.2
    model["TtW energy"] = 3600
    model.set_costs()
    repayment = 1 / sum((1 + rate) ** (-year) for year in range(1, years + 1))
    purchase = 2000
    divisor = annual_km * 1
    assert model["purchase cost"].item() == pytest.approx(purchase)
    assert model["amortised purchase cost"].item() == pytest.approx(
        purchase * repayment / divisor
    )
    assert model["amortised component replacement cost"].item() == pytest.approx(
        1000 / (1 + rate) ** (years / 2) * repayment / divisor
    )
    assert model["energy cost"].item() == pytest.approx(0.25 / 1)

    assert model["total cost per km"].item() == pytest.approx(
        0.25 / 1 + repayment / divisor * (purchase + 1000 / (1 + rate) ** (years / 2))
    )
