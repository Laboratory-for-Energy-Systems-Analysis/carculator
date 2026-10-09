import numpy as np
import pytest
from carculator import (
    CarInputParameters,
    CarModel,
    InventoryCar,
    fill_xarray_from_input_parameters,
)

DEFAULT_SCOPE = {"powertrain": ["ICEV-d", "ICEV-p", "BEV"], "size": ["Medium"]}


def build_vehicle_array(scope=None):
    cip = CarInputParameters()
    cip.static()
    _, array = fill_xarray_from_input_parameters(cip, scope=scope or DEFAULT_SCOPE)
    return array


def build_car_model(scope=None, **kwargs):
    cm = CarModel(build_vehicle_array(scope), cycle="WLTC", **kwargs)
    cm.set_all()
    return cm


@pytest.fixture
def car_model():
    return build_car_model()


def require_export_inventory():
    try:
        from carculator_utils.export import ExportInventory  # noqa: F401
    except (ImportError, TypeError) as exc:
        pytest.skip(f"carculator_utils export stack is not importable: {exc}")


def bw2io_is_usable():
    try:
        import bw2io  # noqa: F401
    except (ImportError, TypeError):
        return False
    return True


def test_scope():
    """Test if scope works as expected"""

    cm = build_car_model()

    ic = InventoryCar(
        cm,
        method="recipe",
        indicator="midpoint",
    )
    results = ic.calculate_impacts()

    assert "Large" not in results.coords["size"].values
    assert "FCEV" not in results.coords["powertrain"].values


def test_plausibility_of_GWP(car_model):
    """Test if GWP scores make sense"""

    for method in ["recipe", "ef"]:
        ic = InventoryCar(car_model, method=method, indicator="midpoint")
        results = ic.calculate_impacts()

        m = "climate change"

        gwp_icev = results.sel(
            impact_category=m,
            powertrain=["ICEV-d", "ICEV-p"],
            value=0,
            year=2020,
            size="Medium",
        )

        # Broad plausibility bounds, not a frozen database-output snapshot.
        # The 3.12/Premise 2.5.4 rebuild gives 0.273/0.361 kg CO2-eq./vkm
        # for 2020 Medium diesel/petrol (previous bundle: 0.266/0.354).

        if method == "recipe":
            assert (gwp_icev.sum(dim="impact") > 0.24).all() and (
                gwp_icev.sum(dim="impact") < 0.40
            ).all(), gwp_icev.sum(dim="impact")

            # Check exhaust carbon against energy demand and fuel chemistry.
            # The former fixed exhaust interval was an output snapshot, not a
            # measured reference, and hid changes in the energy model.
            year_index = list(car_model.array.year.values).index(2020)
            inventory_year = list(ic.scope["year"]).index(2020)
            for powertrain, fuel in [("ICEV-d", "diesel"), ("ICEV-p", "petrol")]:
                selection = dict(
                    size="Medium", powertrain=powertrain, year=2020, value=0
                )
                fuel_kg_km = float(car_model["TtW energy"].sel(**selection)) / (
                    1000 * float(car_model["LHV fuel MJ per kg"].sel(**selection))
                )
                fossil_co2_per_kg = sum(
                    component["share"][year_index]
                    * component["CO2"]
                    * (1 - component["biogenic share"])
                    for component in car_model.fuel_blend[fuel].values()
                )
                expected = fuel_kg_km * fossil_co2_per_kg
                row = ic.inputs[("Carbon dioxide, fossil", ("air",), "kilogram")]
                columns = ic.find_input_indices(
                    ("transport, car, ", powertrain, "Medium")
                )
                assert len(columns) == 1
                np.testing.assert_allclose(
                    -ic.A[0, row, columns[0], inventory_year], expected, rtol=1e-6
                )
                exhaust = float(
                    gwp_icev.sel(powertrain=powertrain, impact="direct - exhaust")
                )
                assert exhaust >= expected * (1 - 1e-6)
                assert exhaust < float(
                    gwp_icev.sel(powertrain=powertrain).sum(dim="impact")
                )

        # Battery contribution: broad 20-50 g CO2-eq./vkm plausibility range.
        # The verified 3.12 background gives 41.0 g for this 2020 case.
        gwp_bev = results.sel(
            impact_category=m, powertrain="BEV", value=0, year=2020, size="Medium"
        )

        assert (gwp_bev.sel(impact="energy storage") > 0.02).all() and (
            gwp_bev.sel(impact="energy storage") < 0.05
        ).all()

        assert gwp_bev.sel(impact="direct - exhaust") == 0


def test_fuel_blend():
    """Test if fuel blends defined by the user are considered"""
    year_count = build_vehicle_array().sizes["year"]

    bc = {
        "petrol": {
            "primary": {
                "type": "petrol",
                "share": np.full(year_count, 0.9),
            },
        },
        "diesel": {
            "primary": {
                "type": "diesel",
                "share": np.full(year_count, 0.93),
            },
        },
        "hydrogen": {
            "primary": {
                "type": "hydrogen - electrolysis - PEM",
                "share": np.full(year_count, 0.9),
            },
        },
        "methane": {
            "primary": {
                "type": "methane - biomethane - sewage sludge",
                "share": np.full(year_count, 1),
            }
        },
    }

    cm = build_car_model(fuel_blend=bc)

    assert np.array_equal(
        cm.fuel_blend["petrol"]["primary"]["share"],
        np.array(np.full(year_count, 0.9)),
    )

    assert np.array_equal(
        cm.fuel_blend["diesel"]["primary"]["share"],
        np.array(np.full(year_count, 0.93)),
    )
    assert np.array_equal(
        cm.fuel_blend["methane"]["primary"]["share"], np.array(np.full(year_count, 1))
    )
    assert np.allclose(
        cm.fuel_blend["methane"]["secondary"]["share"], np.zeros(year_count)
    )

    for fuels in [
        ("petrol", "diesel", "hydrogen - electrolysis - PEM", "methane"),
        (
            "petrol - bioethanol - wheat straw",
            "diesel - biodiesel - palm oil",
            "hydrogen - smr - natural gas",
            "methane - biomethane - sewage sludge",
        ),
        (
            "petrol - bioethanol - forest residues",
            "diesel - biodiesel - rapeseed oil",
            "hydrogen - smr - natural gas with CCS",
            "methane - synthetic - coal",
        ),
        (
            "petrol - bioethanol - maize starch",
            "diesel - biodiesel - cooking oil",
            "hydrogen - wood gasification",
            "methane - synthetic - biological",
        ),
        (
            "petrol - synthetic - methanol - cement - energy allocation",
            "diesel - synthetic - FT - coal - economic allocation",
            "hydrogen - atr - biogas",
            "methane - synthetic - biological",
        ),
        (
            "petrol - synthetic - methanol - cement - energy allocation",
            "diesel - synthetic - methanol - cement - economic allocation",
            "hydrogen - wood gasification with CCS",
            "methane - synthetic - electrochemical",
        ),
    ]:
        bc["petrol"]["primary"]["type"] = fuels[0]
        bc["diesel"]["primary"]["type"] = fuels[1]
        bc["hydrogen"]["primary"]["type"] = fuels[2]
        bc["methane"]["primary"]["type"] = fuels[3]

        if fuels[3] == "methane - synthetic - electrochemical":
            # Unsupported routes must fail before completing the vehicle model.
            with pytest.raises(ValueError, match="methane.*unavailable"):
                build_car_model(fuel_blend=bc)
        else:
            cm = build_car_model(fuel_blend=bc)
            ic = InventoryCar(cm)
            ic.calculate_impacts()

    bc["petrol"]["primary"][
        "type"
    ] = "petrol - synthetic - methanol - electrolysis - energy allocation"
    with pytest.raises(ValueError, match="petrol.*Ambiguous carbon-source alias"):
        build_car_model(fuel_blend=bc)


@pytest.mark.parametrize("bio_share", [0, 0.35, 1])
def test_cng_leakage_adds_direct_methane_emissions(bio_share):
    cip = CarInputParameters()
    cip.static()
    _, array = fill_xarray_from_input_parameters(
        cip, scope={"powertrain": ["ICEV-g"], "size": ["Medium"], "year": [2020]}
    )
    cm = CarModel(
        array,
        cycle="WLTC",
        fuel_blend={
            "methane": {
                "primary": {"type": "methane", "share": 1 - bio_share},
                "secondary": {
                    "type": "methane - biomethane - sewage sludge",
                    "share": bio_share,
                },
            }
        },
    )
    cm.set_all()
    ic = InventoryCar(cm)
    (market,) = ic.find_input_indices(("fuel supply for methane vehicles",))
    (transport,) = ic.find_input_indices(("transport, car, ICEV-g, Medium",))
    engine_fuel = (cm["fuel consumption"] * cm["fuel density per kg"]).item()
    lost = engine_fuel * cm["CNG pump-to-tank leakage"].item()
    assert -ic.A[0, market, transport, 0] == pytest.approx(engine_fuel + lost)
    for origin, share in (("fossil", 1 - bio_share), ("non-fossil", bio_share)):
        row = ic.inputs[(f"Methane, {origin}", ("air",), "kilogram")]
        assert -ic.A[0, row, transport, 0] == pytest.approx(lost * share)


def test_countries(car_model):
    """Test that calculation works with all countries"""
    for c in [
        "AO",
        "AT",
        "AU",
        "BE",
    ]:
        ic = InventoryCar(
            car_model,
            method="recipe",
            indicator="midpoint",
            background_configuration={
                "country": c,
                "energy storage": {"electric": {"type": "NMC-622"}, "origin": c},
            },
        )
        ic.calculate_impacts()


def test_endpoint(car_model):
    """Test if the correct impact categories are considered"""
    ic = InventoryCar(car_model, method="recipe", indicator="endpoint")
    results = ic.calculate_impacts()
    assert "human toxicity: carcinogenic" in [
        i.lower() for i in results.impact_category.values
    ]
    assert len(results.impact_category.values) == 26
    #
    #     """Test if it errors properly if an incorrect method type is give"""
    with pytest.raises(ValueError):
        InventoryCar(car_model, method="recipe", indicator="endpint")


def test_static_scenario(car_model):
    """Test if the static scenario works as expected"""
    ic = InventoryCar(
        car_model, method="recipe", indicator="midpoint", scenario="static"
    )
    ic.calculate_impacts()


def test_EF_indicators(car_model):
    ic = InventoryCar(
        car_model,
        method="ef",
        indicator="midpoint",
    )
    ic.calculate_impacts()


def test_sulfur_concentration(car_model):
    ic = InventoryCar(
        car_model,
    )
    ic.get_sulfur_content(location="FR", fuel="diesel")


def test_custom_electricity_mix(car_model):
    """Test if a wrong number of electricity mixes throws an error"""

    # Passing four mixes instead of 6
    mix_1 = np.zeros((5, 15))
    mix_1[:, 0] = 1

    mixes = [mix_1]

    for mix in mixes:
        with pytest.raises(ValueError) as wrapped_error:
            InventoryCar(
                car_model,
                background_configuration={"custom electricity mix": mix},
            )
        assert wrapped_error.type == ValueError


def test_export_to_bw():
    """Test that inventories export successfully"""
    require_export_inventory()
    if not bw2io_is_usable():
        pytest.skip("bw2io is not importable in this environment")

    cm = build_car_model()

    ic = InventoryCar(
        cm,
    )
    #

    for b in ("3.12",):
        ic.export_lci(
            ecoinvent_version=b,
        )


def test_export_to_excel(tmp_path):
    """Test that inventories export successfully to Excel/CSV"""
    require_export_inventory()
    cm = build_car_model()
    ic = InventoryCar(cm, method="recipe", indicator="endpoint")

    for s in ("brightway2", "simapro"):
        for d in (("file", "bw2io") if s == "brightway2" else ("file",)):
            if d == "bw2io" and not bw2io_is_usable():
                continue
            ic.export_lci(
                ecoinvent_version="3.12",
                format=d,
                software=s,
                directory=str(tmp_path),
            )
