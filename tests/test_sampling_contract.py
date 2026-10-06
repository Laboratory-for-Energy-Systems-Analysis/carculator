import numpy as np
from carculator import (
    CarInputParameters,
    CarModel,
    InventoryCar,
    fill_xarray_from_input_parameters,
)


def test_sensitivity_runs_through_model_and_pkm_impacts():
    ip = CarInputParameters()
    ip.static()
    # Keep the integration case small; the shared unit test covers perturbation math.
    ip.input_parameters = ["glider base mass"]
    _, array = fill_xarray_from_input_parameters(
        ip,
        sensitivity=True,
        scope={"size": ["Medium"], "powertrain": ["BEV"], "year": [2020]},
    )
    model = CarModel(array)
    model.set_all()
    result = InventoryCar(model, functional_unit="pkm").calculate_impacts(
        sensitivity=True
    )
    assert result.value.values.tolist() == ["reference", "glider base mass"]
    climate = result.sel(impact_category="climate change")
    assert np.isfinite(climate).all()
    np.testing.assert_allclose(climate.sel(value="reference"), 1)
    assert (climate.sel(value="glider base mass") > 0).all()
