# Changelog

Notable user-facing changes to `carculator`. The entry below is prepared for release;
it has not yet been published. Older entries, where present, retain their original record.

## [1.9.6] - Unreleased

### Compatibility and installation

- Require Python 3.12 (`>=3.12,<3.13`); older Python environments must be recreated.
- Use NumPy `>=1.26.4,<2` through the shared runtime.
- Require the stable `carculator_utils>=1.3.6` release, including its export extras.
- Build wheels and source distributions from centralized `pyproject.toml` metadata.
- Keep core model/LCIA use independent of Brightway; install `excel` or `brightway` extras for export. The Brightway extra targets the legacy stack (`bw2io<0.9`, `bw2data<4`, `bw2calc<2`).
- Align documentation versions with the package version and provide complete documentation-build dependencies.

### Model and inventory changes

- Correct year/sample alignment in automatic component-cost projections. Multi-year sensitivity references now match static prices and costs; sampled factors remain attached to their samples across years. Preserve existing price curves, explicit battery prices and physical/inventory outputs.
- Preserve explicit generic and selected-chemistry battery prices through cost adjustment, including scoped zero and per-sample constructor inputs. Verify completed purchase and replacement costs and unchanged default pricing; see [usage](docs/usage.rst#battery-unit-costs).
- Converge BEV target range with battery mass, driving mass, motor power and energy demand, allowing chemistry to affect the required capacity and consumption.
- Verify capacity and pack-mass changes through completed models and inventories across four chemistries, two years and two load samples.
- Add native 2025 inputs and explicit component-efficiency priors, with temporal extensions that avoid artificial 2020/2025/2030 discontinuities.
- Expose opt-in petrol start-stop and fuel-cut energy controls; retain explicit energy and component-efficiency overrides.
- Apply corrected shared battery and hybrid energy accounting and consistently mask unavailable configurations across reported energy and supply outputs.
- Use bounded per-cell sizing, preserve custom inputs, and verify labelled samples, mass balance and annualized costs.
- Verify fuel blends, PHEV carbon accounting, hot pollutant translation and multi-year export through the updated shared dependency.

### Documentation and verification

- Add current installation and executable 2025 quick-start examples, migration notes and a release checklist.
- Record calibration scope, measurement boundaries and numerical consistency separately from empirical validation.
- Verify built wheels and sdist-built wheels, packaged resource hashes, installed tests with export extras and offline core-only model/LCIA smoke runs.

### Known limitations

- The 2025 inputs combine engineering priors and selected calibration evidence; they are not a measured validation of every vehicle configuration.
- ADAC cycle reconstruction is approximate. Remaining petrol-car residuals must be interpreted with road load, temperature and operating controls.
- Target range supersedes capacity, and capacity supersedes input pack mass. Fixed total mass or explicit consumption may suppress chemistry-dependent consumption changes.

See [validation](docs/validity.rst) and [release preparation](RELEASING.md) for scope and verification instructions.

## [1.9.5] - 2026-04-29

### Added

- Added `AGENTS.md` with repository-specific guidance for automated coding agents.
- Added this changelog.

### Changed

- Replaced the legacy `setup.py` packaging configuration with `pyproject.toml`.
- Declared supported Python versions and package data in `pyproject.toml`.
- Updated documentation release metadata to `1.9.5`.
- Made inventory tests use fresh model instances and temporary export directories.
- Converted the model reference-output test from a fixture-writing smoke test into assertions.

### Fixed

- Fixed `CarInputParameters` so caller-provided parameter dictionaries and file paths are honored.
- Fixed FCEV cost adjustment so fuel-cell stack costs update `fuel cell cost per kW` instead of overwriting hydrogen tank costs.
- Fixed vehicle purchase-cost amortisation to use lifetime in years, with zero-lifetime safeguards.
- Fixed component replacement discounting to use year-based lifetime discounting.
- Fixed CNG pump-to-tank methane leakage so direct methane emissions are added to the inventory.
- Fixed invalid impact indicator handling so typos raise `ValueError` before xarray result construction.
- Made export tests skip cleanly when the optional `bw2io` export stack is not importable in the active Python environment.
- Fixed the conda publication workflow to upload the package format produced by `conda-build`.
- Added `pip` and runtime `python` requirements to the conda recipe to support conda build publication.
- Aligned `carculator_utils>=1.3.5` across packaging metadata.
