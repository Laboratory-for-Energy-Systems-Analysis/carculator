# Changelog

All notable changes to `carculator` are documented in this file.

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
- Added `pip` and runtime `python` requirements to the conda recipe to support conda build publication.
- Aligned `carculator_utils>=1.3.5` across packaging metadata.
