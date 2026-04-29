# AGENTS.md

Guidance for automated agents working in this repository.

## Scope

These instructions apply to the whole repository.

## Project Overview

`carculator` is a Python package for prospective environmental and economic life
cycle assessment of passenger cars and light-duty vehicles. It provides the
car-specific implementation on top of shared parent classes and utilities from
`carculator_utils`.

Most model state is represented with `xarray.DataArray` objects. Core dimensions
are usually `size`, `powertrain`, `parameter`, `year`, and `value`.

Important paths:

- `carculator/`: package source.
- `carculator/data/`: bundled car model data, parameters, and cost assumptions.
- `tests/`: pytest tests and small fixture files.
- `docs/`: Sphinx documentation.
- `examples/`: example notebooks and usage material.
- `dev/`: development and exploratory files.
- `conda/`: conda build recipe.
- `.github/workflows/main.yml`: CI formatting, test, packaging, and publish workflow.

Main modules:

- `car_input_parameters.py`: loads car parameter dictionaries and subclasses
  `carculator_utils.vehicle_input_parameters.VehicleInputParameters`.
- `array.py`: converts input parameters into labeled `xarray` arrays.
- `model.py`: `CarModel`, the main car model subclass of
  `carculator_utils.model.VehicleModel`.
- `inventory.py`: `InventoryCar`, the car-specific life cycle inventory builder.
- `driving_cycles.py`: standard driving cycle and road gradient helpers.

## Environment

The package declares Python `>=3.9` in `setup.py`.

The local conda environment named `carculator` can be used to access all needed
dependencies:

```bash
conda activate carculator
```

Typical local setup:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pip install pytest pytest-cov
```

Documentation dependencies are separate:

```bash
python -m pip install -r docs/docs_requirements.txt
python -m pip install -e .
```

When dependencies or version metadata change, keep the relevant files aligned:

- `setup.py`
- `requirements.txt`
- `conda/meta.yaml`
- `carculator/__init__.py`
- documentation requirements, if the change affects docs builds

## Verification Commands

Run tests from the repository root:

```bash
python -m pytest
```

Run focused test files:

```bash
python -m pytest tests/test_model.py
python -m pytest tests/test_inventory.py
python -m pytest tests/test_vehicle_input_parameters.py
```

Run coverage similarly to CI:

```bash
python -m pytest --cov=carculator
```

Run formatting checks or fixes:

```bash
python -m black .
python -m isort --profile black .
```

Build documentation after installing docs dependencies:

```bash
make -C docs html
```

The test suite imports `carculator` and therefore also imports
`carculator_utils`; install project dependencies before interpreting import
failures as code regressions.

## Formatting and Style

- Follow Black formatting.
- Use isort with the Black profile: `isort --profile black .`
- Use Sphinx-style docstrings for public classes, functions, and modules.
- Prefer `pathlib.Path` and package-relative paths over hard-coded absolute paths.
- For package data access, prefer `carculator.DATA_DIR` or
  `Path(__file__).resolve().parent / "data"` patterns already used in the
  codebase.
- Keep imports explicit and avoid adding expensive import-time side effects.
- Prefer vectorized `numpy`, `pandas`, and `xarray` operations when working with
  model arrays.

## Model Contracts

This package depends heavily on parent classes from `carculator_utils`, while
downstream users often depend on `carculator` public behavior.

- Treat `CarInputParameters`, `CarModel`, and `InventoryCar` as public APIs.
- Preserve public exports from `carculator/__init__.py` unless the change is
  intentional and documented.
- Maintain the core `xarray.DataArray` contract: dimensions `size`,
  `powertrain`, `parameter`, `year`, and `value`.
- Keep schema-sensitive labels stable: parameter names, powertrain labels, size
  labels, chemistry labels, units, country codes, and years are part of the
  practical API.
- Be careful with the ordering in `CarModel.set_all()`. Mass, power, battery,
  energy consumption, costs, emissions, and PHEV utility-factor calculations are
  interdependent.
- Preserve override paths such as `energy_storage`, `target_mass`,
  `target_range`, `energy_consumption`, `fuel_blend`, and
  `electric_utility_factor` unless all effects are checked.
- Use inherited inventory and background-system helpers from
  `carculator_utils` where possible instead of duplicating logic locally.
- When parent behavior expects subclass-provided data files or attributes, fail
  with explicit errors and document the expected input.

## Data Handling

The repository ships package data used directly by model calculations. Be
conservative when editing files under `carculator/data/`.

- Preserve existing JSON and YAML schemas.
- Keep parameter names, powertrain labels, size labels, and units stable unless
  the migration is explicit and tested.
- Prefer text formats such as JSON, CSV, and YAML for new data when possible,
  matching the existing repository style.
- If adding a new data file type or directory, update `MANIFEST.in` and verify
  that `setup.py` package data includes it.
- Use small fixtures in `tests/fixtures/` for new tests instead of depending on
  large production data where possible.
- Some tests and development scripts may generate Excel or notebook artifacts;
  inspect `git status` carefully before staging.

## Testing Guidance

- Add or update tests for behavior changes, especially array dimensions,
  interpolation, vehicle construction, fuel blends, battery assumptions,
  background inventory, and impact results.
- For changes to data loaders, include at least a smoke test that the loader
  returns the expected type and core dimensions or keys.
- For model changes, test representative powertrains and at least one focused
  edge case rather than relying only on broad integration tests.
- Keep stochastic or sample-based tests deterministic.
- Check downstream compatibility mentally against `carculator_utils` contracts
  before broad refactors.

## Documentation Guidance

- Update `docs/` for user-facing API, scenario, parameter, or workflow changes.
- Keep README and docs examples aligned with the public API exported from
  `carculator/__init__.py`.
- Build docs locally with `make -C docs html` when changing doc configuration,
  API docs, or example snippets.
- Clear transient notebook execution output unless the repository intentionally
  tracks it.

## Packaging and Release Guidance

- Keep version metadata synchronized between `setup.py` and
  `carculator/__init__.py`.
- `conda/meta.yaml` uses the `VERSION` environment variable during publication;
  keep the conda recipe aligned with runtime dependencies.
- Keep `requirements.txt` aligned with the lower-level dependency expectations
  declared in `setup.py` and the conda recipe.
- When changing packaged data, verify source distributions and conda builds still
  include the required files.

## Git Hygiene

- Leave unrelated dirty worktree changes untouched.
- Do not commit local editor files, `.DS_Store`, virtual environments, build
  artifacts, coverage output, generated docs output, or scratch notebooks.
- Avoid broad refactors while making targeted scientific or data-model changes;
  this package has implicit compatibility expectations with `carculator_utils`
  and user workflows.

