import numpy as np
import pytest
from carculator import (
    CarInputParameters,
    CarModel,
    InventoryCar,
    fill_xarray_from_input_parameters,
)


@pytest.fixture(scope="module")
def model():
    ip = CarInputParameters()
    ip.static()
    _, array = fill_xarray_from_input_parameters(
        ip, scope={"size": ["Medium"], "powertrain": ["BEV"], "year": [2020, 2030]}
    )
    model = CarModel(array)
    model.set_all()
    return model


@pytest.mark.parametrize(
    "unit,simapro_unit", [("vkm", "km"), ("pkm", "personkm"), ("tkm", "tkm")]
)
def test_exports_preserve_units_years_and_lcia(model, tmp_path, unit, simapro_unit):
    inventory = InventoryCar(model, functional_unit=unit)
    before = inventory.calculate_impacts().values.copy()
    matrix = inventory.A.copy()
    for _ in range(2):
        strings = inventory.export_lci(
            software="simapro", format="string", directory=tmp_path
        )
        assert len(strings) == 2
        for year, text in zip([2020, 2030], strings):
            assert str(year) in text
            assert simapro_unit in text
        workbooks = inventory.export_lci(
            software="brightway2", format="string", directory=tmp_path
        )
        assert len(workbooks) == 2
        assert all(value.startswith(b"PK") for value in workbooks)
    np.testing.assert_array_equal(inventory.A, matrix)
    np.testing.assert_allclose(inventory.calculate_impacts().values, before)
