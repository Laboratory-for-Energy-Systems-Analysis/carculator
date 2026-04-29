import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from carculator import *
from carculator.model import CarModel


class TestCarModel(unittest.TestCase):

    DATA = Path(__file__, "..").resolve() / "fixtures" / "cars_values.xlsx"
    ref = pd.read_excel(DATA, index_col=0)

    def setUp(self):
        cip = CarInputParameters()
        cip.static()
        dcts, arr = fill_xarray_from_input_parameters(cip)
        self.cm = CarModel(arr, cycle="WLTC")
        self.cm.set_all()

    def test_model_results(self):
        list_powertrains = [
            "ICEV-p",
            "ICEV-d",
            "PHEV-p",
            "PHEV-d",
            "BEV",
            "ICEV-g",
            "HEV-d",
            "HEV-p",
        ]
        list_sizes = [
            "Medium",
        ]
        list_years = [
            2020,
        ]

        for pwt in list_powertrains:
            for size in list_sizes:
                for year in list_years:
                    for param in ["curb mass", "driving mass", "total cost per km"]:
                        val = float(
                            self.cm.array.sel(
                                powertrain=pwt,
                                size=size,
                                year=year,
                                parameter=param,
                                value=0,
                            ).values
                        )
                        ref = self.ref.loc[
                            (self.ref["powertrain"] == pwt)
                            & (self.ref["size"] == size)
                            & (self.ref["parameter"] == param),
                            year,
                        ]

                        assert not ref.empty, (pwt, size, year, param)
                        assert np.isfinite(val), (pwt, size, year, param)
                        assert np.isclose(
                            val, ref.values.astype(float).item(0), rtol=0.1, atol=1e-6
                        ), (pwt, size, year, param, val, ref.values.item(0))

    def test_setting_batt_cap(self):
        cip = CarInputParameters()
        cip.static()
        dcts, arr = fill_xarray_from_input_parameters(
            cip,
            scope={"size": ["Medium"], "powertrain": ["BEV"], "year": [2020]},
        )

        batt_cap = {
            "capacity": {
                ("BEV", "Medium", 2020): 50,
            }
        }

        cm = CarModel(arr, cycle="WLTC", energy_storage=batt_cap)
        cm.set_all()

        assert np.isclose(
            cm.array.sel(
                powertrain="BEV",
                size="Medium",
                year=2020,
                parameter="electric energy stored",
                value=0,
            ).values,
            50,
            rtol=0.01,
        )

    def test_setting_battery_chemistry(self):
        cip = CarInputParameters()
        cip.static()
        dcts, arr = fill_xarray_from_input_parameters(
            cip,
            scope={"size": ["Medium"], "powertrain": ["BEV"], "year": [2020]},
        )

        batt_chem = {
            "electric": {
                ("BEV", "Medium", 2020): "LFP",
            }
        }

        cm = CarModel(arr, cycle="WLTC", energy_storage=batt_chem)
        cm.set_all()

        assert np.isclose(
            cm.array.sel(
                powertrain="BEV",
                size="Medium",
                year=2020,
                parameter="battery cell energy density",
                value=0,
            ).values,
            0.16,
            rtol=0.01,
        )

    def test_setting_range(self):
        cip = CarInputParameters()
        cip.static()
        dcts, arr = fill_xarray_from_input_parameters(
            cip,
            scope={"size": ["Medium"], "powertrain": ["BEV"], "year": [2020]},
        )

        range = {
            ("BEV", "Medium", 2020): 100,
        }

        cm = CarModel(arr, cycle="WLTC", target_range=range)
        cm.set_all()

        assert (
            cm.array.sel(
                powertrain="BEV",
                size="Medium",
                year=2020,
                parameter="electric energy stored",
                value=0,
            ).values
            <= 25
        )

        assert np.isclose(
            cm.array.sel(
                powertrain="BEV",
                size="Medium",
                year=2020,
                parameter="range",
                value=0,
            ).values,
            np.array(100, dtype=np.float32),
            rtol=0.01,
        )

    def test_setting_mass(self):
        cip = CarInputParameters()
        cip.static()
        dcts, arr = fill_xarray_from_input_parameters(
            cip,
            scope={"size": ["Medium"], "powertrain": ["BEV"], "year": [2020]},
        )

        mass = {
            ("BEV", "Medium", 2020): 2000,
        }

        cm = CarModel(arr, cycle="WLTC", target_mass=mass)
        cm.set_all()

        assert (
            cm.array.sel(
                powertrain="BEV",
                size="Medium",
                year=2020,
                parameter="curb mass",
                value=0,
            ).values
            == 2000
        )

    def test_setting_ttw_energy(self):
        cip = CarInputParameters()
        cip.static()
        dcts, arr = fill_xarray_from_input_parameters(
            cip,
            scope={"size": ["Medium"], "powertrain": ["BEV", "ICEV-p"], "year": [2020]},
        )

        ttw_energy = {
            ("BEV", "Medium", 2020): 1000,
            ("ICEV-p", "Medium", 2020): 2500,
        }

        cm = CarModel(arr, cycle="WLTC", energy_consumption=ttw_energy)
        cm.set_all()

        assert (
            cm.array.sel(
                powertrain="BEV",
                size="Medium",
                year=2020,
                parameter="TtW energy",
                value=0,
            ).values
            == 1000
        )

        assert np.isclose(
            cm.array.sel(
                powertrain="BEV",
                size="Medium",
                year=2020,
                parameter="electricity consumption",
                value=0,
            ).values,
            (1000 / 3600) * 1.17,
            rtol=0.01,
        )

        assert (
            cm.array.sel(
                powertrain="ICEV-p",
                size="Medium",
                year=2020,
                parameter="TtW energy",
                value=0,
            ).values
            == 2500
        )

        _ = lambda x: np.where(x == 0, 1, x)
        assert np.array_equal(
            cm["fuel consumption"],
            (cm["fuel mass"] / (cm["range"]) / _(cm["fuel density per kg"])),
        )

    def test_stochastic_calculations(self):
        cip = CarInputParameters()
        cip.stochastic(50)
        dcts, arr = fill_xarray_from_input_parameters(
            cip,
            scope={"size": ["Medium"], "powertrain": ["BEV", "ICEV-p"], "year": [2020]},
        )
        cm = CarModel(arr, cycle="WLTC")
        cm.set_all()

    def test_setting_power(self):
        cip = CarInputParameters()
        cip.static()
        dcts, arr = fill_xarray_from_input_parameters(
            cip,
            scope={"size": ["Medium"], "powertrain": ["BEV", "ICEV-p"], "year": [2020]},
        )

        power = {
            ("BEV", "Medium", 2020): 100,
            ("ICEV-p", "Medium", 2020): 200,
        }

        cm = CarModel(arr, cycle="WLTC", power=power)
        cm.set_all()

        assert (
            cm.array.sel(
                powertrain="BEV",
                size="Medium",
                year=2020,
                parameter="electric power",
                value=0,
            ).values
            == 100
        )

        assert (
            cm.array.sel(
                powertrain="ICEV-p",
                size="Medium",
                year=2020,
                parameter="combustion power",
                value=0,
            ).values
            == 200
        )

        assert (
            cm.array.sel(
                powertrain="ICEV-p",
                size="Medium",
                year=2020,
                parameter="power",
                value=0,
            ).values
            == 200
        )

        assert np.array_equal(
            cm["combustion engine mass"],
            (
                cm["combustion power"] * cm["combustion mass per power"]
                + cm["combustion fixed mass"]
            ),
        )

    def test_setting_battery_origin(self):
        cip = CarInputParameters()
        cip.static()
        dcts, arr = fill_xarray_from_input_parameters(
            cip,
            scope={"size": ["Medium"], "powertrain": ["BEV"], "year": [2020]},
        )

        battery_origin = {"origin": "FR"}

        cm = CarModel(arr, cycle="WLTC", energy_storage=battery_origin)
        cm.set_all()

        assert cm.energy_storage["origin"] == "FR"

    def test_adjust_cost_updates_fcev_cost_parameters(self):
        cip = CarInputParameters()
        cip.static()
        _, arr = fill_xarray_from_input_parameters(
            cip,
            scope={"size": ["Medium"], "powertrain": ["FCEV"], "year": [2020, 2030]},
        )

        cm = CarModel(arr, cycle="WLTC")
        cm.adjust_cost()

        years = cm.array.year.values
        np.testing.assert_allclose(
            cm.array.sel(
                powertrain="FCEV",
                size="Medium",
                parameter="fuel tank cost per kg",
                value=0,
            ).values,
            1.078e58 * np.exp(-6.32e-2 * years) + 3.43e2,
            rtol=1e-6,
        )
        np.testing.assert_allclose(
            cm.array.sel(
                powertrain="FCEV",
                size="Medium",
                parameter="fuel cell cost per kW",
                value=0,
            ).values,
            3.15e66 * np.exp(-7.35e-2 * years) + 2.39e1,
            rtol=1e-6,
        )

    def test_purchase_cost_uses_lifetime_years_for_amortisation(self):
        lifetime = self.cm["lifetime kilometers"] / self.cm["kilometers per year"]
        interest_rate = self.cm["interest rate"]
        valid_lifetime = lifetime > 0
        safe_lifetime = lifetime.where(valid_lifetime, 1)
        safe_kilometers_per_year = self.cm["kilometers per year"].where(
            self.cm["kilometers per year"] > 0, 1
        )
        safe_interest_rate = interest_rate.where(interest_rate != 0, 1)
        amortisation_factor = np.where(
            interest_rate == 0,
            np.array(1) / safe_lifetime,
            safe_interest_rate
            + (
                safe_interest_rate
                / ((np.array(1) + safe_interest_rate) ** safe_lifetime - np.array(1))
            ),
        )
        amortisation_factor = np.where(valid_lifetime, amortisation_factor, 0)
        expected = np.where(
            valid_lifetime,
            self.cm["purchase cost"] * amortisation_factor / safe_kilometers_per_year,
            0,
        )

        np.testing.assert_allclose(
            self.cm["amortised purchase cost"].values,
            expected,
            rtol=1e-6,
            equal_nan=True,
        )

    # New tests start here

    def test_set_all(self):
        # Test that set_all completes without errors
        self.assertTrue(hasattr(self.cm, "ecm"))
        self.assertGreater(len(self.cm.array), 0)

    def test_set_battery_chemistry(self):
        self.cm.set_battery_chemistry()
        # Check if the energy_storage dictionary has been populated with expected values
        self.assertIn("electric", self.cm.energy_storage)
        self.assertEqual(self.cm.energy_storage["origin"], "CN")

    def test_adjust_cost(self):
        self.cm.adjust_cost()
        # Check if the costs have been adjusted as expected
        assert self.cm["total cost per km"].sum() > 0

    def test_set_vehicle_mass(self):
        # Mock necessary attributes for testing
        self.cm.array.loc[
            dict(
                powertrain=["ICEV-p", "ICEV-d", "ICEV-g"],
                parameter="glider base mass",
                size="Medium",
                year=2020,
                value=0,
            )
        ] = np.array([800, 900, 1000]).T
        self.cm.array.loc[
            dict(
                powertrain=["ICEV-p", "ICEV-d", "ICEV-g"],
                parameter="lightweighting",
                size="Medium",
                year=2020,
                value=0,
            )
        ] = np.array([0.1, 0.1, 0.1])
        self.cm.array.loc[
            dict(
                powertrain=["ICEV-p", "ICEV-d", "ICEV-g"],
                parameter="fuel mass",
                size="Medium",
                year=2020,
                value=0,
            )
        ] = np.array([50, 60, 70])
        self.cm.array.loc[
            dict(
                powertrain=["ICEV-p", "ICEV-d", "ICEV-g"],
                parameter="average passengers",
                size="Medium",
                year=2020,
                value=0,
            )
        ] = np.array([2, 2, 2])
        self.cm.array.loc[
            dict(
                powertrain=["ICEV-p", "ICEV-d", "ICEV-g"],
                parameter="average passenger mass",
                size="Medium",
                year=2020,
                value=0,
            )
        ] = np.array([70, 70, 70])
        self.cm.array.loc[
            dict(
                powertrain=["ICEV-p", "ICEV-d", "ICEV-g"],
                parameter="cargo mass",
                size="Medium",
                year=2020,
                value=0,
            )
        ] = np.array([100, 120, 140])

        # Perform the mass calculation
        self.cm.set_vehicle_masses()

        # Verify the mass has been set correctly
        self.assertIn("driving mass", self.cm.array.coords["parameter"].values)
        self.assertGreater(self.cm["driving mass"].sum(), 0)

    def test_set_electric_utility_factor(self):

        # Check if the electric utility factor is set within expected limits
        self.assertGreaterEqual(self.cm["electric utility factor"].min(), 0)
        self.assertLessEqual(self.cm["electric utility factor"].max(), 0.75)

    def test_remove_energy_consumption_from_unavailable_vehicles(self):

        self.cm.remove_energy_consumption_from_unavailable_vehicles()

        # Check that energy consumption is set to 0 for vehicles that should be unavailable
        self.assertEqual(
            self.cm["TtW energy"].sel(year=2010, powertrain="BEV").sum(), 0
        )


TestCarModel()
