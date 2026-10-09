# carculator

Prospective environmental and economic life cycle assessment of passenger cars and light-duty vehicles.

[![Installed artifacts](https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator/actions/workflows/main.yml)
[![PyPI](https://img.shields.io/pypi/v/carculator)](https://pypi.org/project/carculator/)

Developed at the [Paul Scherrer Institute](https://www.psi.ch/en).
This checkout prepares **1.9.6**; see [CHANGELOG.md](https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator/blob/master/CHANGELOG.md) for release status and changes.

## Installation

Use **Python 3.12** (`>=3.12,<3.13`) and a fresh environment. The shared runtime
requires NumPy `>=1.26.4,<2`.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

On Windows, activate with `.venv\Scripts\activate`. After publication, install
this release from PyPI:

```bash
python -m pip install "carculator==1.9.6"
```

Before publication, use the matching source checkouts as described under development.
Core calculations use bundled resources and need no Brightway project, ecoinvent
installation or network access. The matching `carculator_utils` runtime installs
`brightpath>=1.0.0a6,<1.1` for Brightway Excel, SimaPro CSV and openLCA JSON-LD
exports. It uses Brightpath's v1 API, currently an alpha; model and LCIA
calculations do not import Brightpath or Brightway.

The `excel` extra remains a compatibility alias. To select the tested legacy
Brightway stack (`bw2io<0.9`, `bw2data<4`, `bw2calc<2`), use:

```bash
python -m pip install "carculator[brightway]==1.9.6"
```

Brightpath also installs `bw2io` without that extra. Export targets ecoinvent
3.9 and 3.10, cut-off; external suppliers must be matched to the corresponding
background in the destination tool. See [inventory export](docs/inventory_export.rst).

## Quick start

```python
from carculator import (
    CarInputParameters,
    CarModel,
    InventoryCar,
    fill_xarray_from_input_parameters,
)

inputs = CarInputParameters()
inputs.static()
_, array = fill_xarray_from_input_parameters(
    inputs,
    scope={"size": ["Medium"], "powertrain": ["ICEV-p", "BEV"], "year": [2025]},
)
model = CarModel(array, cycle="WLTC")
model.set_all()
print(model["TtW energy"])  # kJ per vehicle-kilometre

inventory = InventoryCar(model, functional_unit="vkm")
impacts = inventory.calculate_impacts()
print(impacts.sel(impact_category="climate change").sum("impact"))
```

The example reports impacts per vehicle-kilometre.

## Inventory export

With the completed `inventory` from the quick start:

```python
workbook = inventory.export_lci(software="brightway2", format="file", directory="exports")
simapro_csv = inventory.export_lci(software="simapro", format="file", directory="exports")
foreground_zip = inventory.export_lci(software="openlca", format="file", directory="exports")
```

Retain exactly one sample before constructing the model and inventory. Each year
gets its own export; multiple years return a list. Exports preserve the original
inventory and calculated impacts. The default `export_lci()` returns an unlinked
Brightway importer.

The openLCA ZIP contains foreground processes, without an ecoinvent background or
LCIA methods; map external providers and elementary flows before calculation.
SimaPro CSV uses Latin-1 and warns when omitting custom noise flows. See the
[export guide](docs/inventory_export.rst) for return types, sample selection and
format-specific limitations.

## Battery sizing

Set nominal capacity with `energy_storage={"capacity": {("BEV", "Medium", 2025): 60}}`.
Set pack mass through the input array parameter `energy battery mass` (kg).
Set a desired range with `target_range={("BEV", "Medium", 2025): 400}`.
Range targets supersede capacity overrides; capacity overrides supersede pack-mass inputs.
The range solver converges battery mass and energy demand together. See the
[battery-sizing documentation](https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator/blob/master/docs/modeling.rst) for complete examples.

## Modelling and validation

Battery unit prices supplied by users now survive chemistry selection and cost
adjustment. Use `battery_costs` for explicit prices scoped by vehicle, year and
sample; see [battery-cost inputs](docs/usage.rst#battery-unit-costs).

The vehicle models include native **2025** parameters and documented temporal
extensions. These combine engineering priors and selected calibration evidence;
they are not independent measurements for every vehicle configuration.

`TtW energy` is in kJ/km. For BEVs it is net stored-energy depletion;
`model.battery_terminal_energy` reports terminal DC separately, while
`electricity consumption` is grid electricity in kWh/km. Identify the measurement
boundary before comparing energy outputs. Availability-masked zeroes do not
represent physically zero consumption.

Supported background scenarios are `SSP2-NPi`, `SSP2-PkBudg1000`,
`SSP2-PkBudg650`, and `static`. ReCiPe supports midpoint/endpoint and EF midpoint.
Use fresh model instances for independent cases. `inputs.stochastic(n, seed=...)`
seeds parameter sampling, not every downstream cost adjustment.

See [validation and limitations](https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator/blob/master/docs/validity.rst), [migration notes](https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator/blob/master/docs/release.rst)
and the [documentation](https://carculator.readthedocs.io/en/latest/).

## Development and release

Use matching sibling checkouts, especially `carculator_utils` **1.3.6 or newer**:

```bash
python -m pip install -e "../carculator_utils[test,excel,brightway]" -e ".[test,docs,excel,brightway]"
python -m pip check
python -m pytest
python -m sphinx -b html docs docs/_build/html
```

The `docs` extra includes the extensions used by this repository.
See [RELEASING.md](https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator/blob/master/RELEASING.md) for artifact verification, release order and publication.

## Support and license

Contact [carculator@psi.ch](mailto:carculator@psi.ch) or open an [issue](https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator/issues).
Maintained by [Romain Sacchi](https://github.com/romainsacchi), with contributions
from the carculator development team. See [contributing](https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator/blob/master/CONTRIBUTING.md).
Licensed under [BSD-3-Clause](https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator/blob/master/LICENSE).

Scientific background: [Cox et al. (2018)](https://doi.org/10.1021/acs.est.8b00261).
