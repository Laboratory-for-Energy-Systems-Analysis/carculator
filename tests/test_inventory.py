import numpy as np
import pytest

from carculator import (
    CarInputParameters,
    CarModel,
    Inventory,
    fill_xarray_from_input_parameters,
)

# generate vehicle parameters
cip = CarInputParameters()
cip.static()

# fill in array with vehicle parameters
_, array = fill_xarray_from_input_parameters(cip)

# build CarModel object
cm = CarModel(array, cycle="WLTC")
# build vehicles
cm.set_all()


def test_scope():
    """Test if scope works as expected"""
    ic = Inventory(
        cm,
        method="recipe",
        indicator="midpoint",
        scope={"powertrain": ["ICEV-d", "ICEV-p"], "size": ["Lower medium"]},
    )
    results = ic.calculate_impacts()

    assert "Large" not in results.coords["size"].values
    assert "BEV" not in results.coords["powertrain"].values


def test_plausibility_of_GWP():
    """Test if GWP scores make sense"""

    for method in ["recipe", "ilcd"]:
        ic = Inventory(
            cm,
            method=method,
            indicator="midpoint",
            scope={"powertrain": ["ICEV-d", "ICEV-p", "BEV"], "size": ["Medium"]},
        )
        results = ic.calculate_impacts()

        if method == "recipe":
            m = "climate change"
        else:
            m = "climate change - climate change total"

        gwp_icev = results.sel(
            impact_category=m,
            powertrain=["ICEV-d", "ICEV-p"],
            value=0,
            year=2020,
            size="Medium",
        )

        # Are the medium ICEVs between 0.28 and 0.35 kg CO2-eq./vkm?

        if method == "recipe":
            assert (gwp_icev.sum(dim="impact") > 0.28).all() and (
                gwp_icev.sum(dim="impact") < 0.32
            ).all()

            # Are the medium ICEVs direct emissions between 0.13 and  0.18 kg CO2-eq./vkm?
            assert (gwp_icev.sel(impact="direct - exhaust") > 0.13).all() and (
                gwp_icev.sel(impact="direct - exhaust") < 0.19
            ).all()

        # Are the ICEVs glider emissions between 0.04 and 0.05 kg CO2-eq./vkm?
        assert (gwp_icev.sel(impact="glider") > 0.04).all() and (
            gwp_icev.sel(impact="glider") < 0.05
        ).all()

        # Is the GWP score for batteries of Medium BEVs between 0.025 and 0.035 kg Co2-eq./vkm?
        gwp_bev = results.sel(
            impact_category=m, powertrain="BEV", value=0, year=2020, size="Medium"
        )

        assert (gwp_bev.sel(impact="energy storage") > 0.025).all() and (
            gwp_bev.sel(impact="energy storage") < 0.038
        ).all()


def test_fuel_blend():
    """Test if fuel blends defined by the user are considered"""

    bc = {
        "fuel blend": {
            "petrol": {
                "primary fuel": {
                    "type": "petrol",
                    "share": [0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
                },
                "secondary fuel": {
                    "type": "bioethanol - wheat straw",
                    "share": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                },
            },
            "diesel": {
                "primary fuel": {
                    "type": "diesel",
                    "share": [0.93, 0.93, 0.93, 0.93, 0.93, 0.93],
                },
                "secondary fuel": {
                    "type": "biodiesel - cooking oil",
                    "share": [0.07, 0.07, 0.07, 0.07, 0.07, 0.07],
                },
            },
            "cng": {
                "primary fuel": {
                    "type": "biogas - sewage sludge",
                    "share": [
                        1,
                        1,
                        1,
                        1,
                        1,
                        1,
                    ],
                }
            },
        }
    }

    ic = Inventory(
        cm, method="recipe", indicator="midpoint", background_configuration=bc
    )

    assert ic.fuel_blends["petrol"]["primary"]["share"] == [
        0.9,
        0.9,
        0.9,
        0.9,
        0.9,
        0.9,
    ]
    assert ic.fuel_blends["petrol"]["secondary"]["share"] == [
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
    ]
    assert ic.fuel_blends["cng"]["primary"]["share"] == [1, 1, 1, 1, 1, 1]
    assert np.sum(ic.fuel_blends["cng"]["secondary"]["share"]) == 0

    ic.calculate_impacts()

    for fuels in [
        ("petrol", "diesel", "electrolysis", "cng"),
        (
            "bioethanol - wheat straw",
            "biodiesel - palm oil",
            "smr - natural gas",
            "biogas - sewage sludge",
        ),
        (
            "bioethanol - forest residues",
            "biodiesel - rapeseed oil",
            "smr - natural gas with CCS",
            "biogas - biowaste",
        ),
        (
            "bioethanol - maize starch",
            "biodiesel - cooking oil",
            "wood gasification with EF with CCS",
            "biogas - biowaste",
        ),
        (
            "bioethanol - sugarbeet",
            "biodiesel - algae",
            "atr - biogas",
            "biogas - biowaste",
        ),
        (
            "synthetic gasoline - energy allocation",
            "synthetic diesel - energy allocation",
            "wood gasification with EF with CCS",
            "syngas",
        ),
    ]:
        ic = Inventory(
            cm,
            method="recipe",
            indicator="midpoint",
            background_configuration={
                "fuel blend": {
                    "petrol": {
                        "primary fuel": {"type": fuels[0], "share": [1, 1, 1, 1, 1, 1]},
                    },
                    "diesel": {
                        "primary fuel": {"type": fuels[1], "share": [1, 1, 1, 1, 1, 1]},
                    },
                    "hydrogen": {
                        "primary fuel": {
                            "type": fuels[2],
                            "share": [1, 1, 1, 1, 1, 1],
                        }
                    },
                    "cng": {
                        "primary fuel": {
                            "type": fuels[3],
                            "share": [1, 1, 1, 1, 1, 1],
                        }
                    },
                }
            },
        )
        ic.calculate_impacts()


def test_countries():
    """Test that calculation works with all countries"""
    for c in [
        "AO",
        "AT",
        "AU",
        "BE",
    ]:
        ic = Inventory(
            cm,
            method="recipe",
            indicator="midpoint",
            background_configuration={
                "country": c,
                "energy storage": {"electric": {"type": "NMC-622"}, "origin": c},
            },
        )
        ic.calculate_impacts()


def test_IAM_regions():
    """Test that calculation works with all IAM regions"""
    for c in ["BRA", "CAN", "CEU", "CHN", "EAF"]:
        ic = Inventory(
            cm,
            method="recipe",
            indicator="midpoint",
            background_configuration={
                "country": c,
                "energy storage": {
                    "electric": {("BEV", "Large", 2000): "NMC-622"},
                    "origin": c,
                },
            },
        )
        ic.calculate_impacts()


def test_endpoint():
    """Test if the correct impact categories are considered"""
    ic = Inventory(cm, method="recipe", indicator="endpoint")
    results = ic.calculate_impacts()
    assert "human health" in [i.lower() for i in results.impact_category.values]
    assert len(results.impact_category.values) == 4
    #
    #     """Test if it errors properly if an incorrect method type is give"""
    with pytest.raises(TypeError) as wrapped_error:
        ic = Inventory(cm, method="recipe", indicator="endpint")
        ic.calculate_impacts()
    assert wrapped_error.type == TypeError


def test_sulfur_concentration():
    ic = Inventory(cm, method="recipe", indicator="endpoint")
    ic.get_sulfur_content("RER", "diesel", 2000)
    ic.get_sulfur_content("foo", "diesel", 2000)

    with pytest.raises(ValueError) as wrapped_error:
        ic.get_sulfur_content("FR", "diesel", "jku")
    assert wrapped_error.type == ValueError


def test_custom_electricity_mix():
    """Test if a wrong number of electricity mixes throws an error"""

    # Passing four mixes instead of 6
    mix_1 = np.zeros((5, 15))
    mix_1[:, 0] = 1

    mixes = [mix_1]

    for mix in mixes:
        with pytest.raises(ValueError) as wrapped_error:
            Inventory(
                cm,
                method="recipe",
                indicator="endpoint",
                background_configuration={"custom electricity mix": mix},
            )
        assert wrapped_error.type == ValueError


def test_export_to_bw():
    """Test that inventories export successfully"""
    ic = Inventory(cm, method="recipe", indicator="endpoint")
    #

    for b in ("3.5", "3.6", "3.7", "3.8", "uvek"):
        for c in (True, False):
            ic.export_lci(
                ecoinvent_version=b,
                create_vehicle_datasets=c,
            )


def test_export_to_excel():
    """Test that inventories export successfully to Excel/CSV"""
    ic = Inventory(cm, method="recipe", indicator="endpoint")

    for b in ("3.5", "3.6", "3.7", "3.7.1", "3.8", "uvek"):
        for c in (True, False):
            for d in ("file", "string"):
                #
                ic.export_lci_to_excel(
                    ecoinvent_version=b,
                    create_vehicle_datasets=c,
                    export_format=d,
                    directory="directory",
                )
