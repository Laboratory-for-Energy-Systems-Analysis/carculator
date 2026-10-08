Release 1.9.6: migration and validation
=======================================

This checkout prepares ``carculator 1.9.6``; it has not yet been published.
The :download:`changelog <../CHANGELOG.md>` lists package-specific changes and
the :download:`release checklist <../RELEASING.md>` describes artifact verification
and publication order.

Environment and API migration
-----------------------------

Use Python **3.12** (``>=3.12,<3.13``) with NumPy ``>=1.26.4,<2``.
Vehicle packages require the stable ``carculator_utils>=1.3.6`` release.
Core model/LCIA runs need no Brightway project or ecoinvent installation;
``excel`` and ``brightway`` are optional export extras. The Brightway extra
targets ``bw2io<0.9``, ``bw2data<4`` and ``bw2calc<2``.

Use the public vehicle-specific input, model and inventory classes. The array
builder returns ``(mappings, array)``; call ``set_all()`` on a fresh model before
constructing its inventory. See :doc:`installation` and the repository README
for runnable examples using 2025 inputs. Invalid coordinates, fuel shares and
active functional-unit loads now fail explicitly; sizing has a bounded iteration
limit with per-cell diagnostics.

Numerical results and reproducibility
-------------------------------------

Re-run saved scenarios after upgrading. Corrected energy accounting, component
priors, cost annualization, fuel blends, direct CO2 and hot pollutant mapping can
change results from earlier releases. Retain package versions, input overrides,
cycle, load, fuel blend, functional unit and energy meter boundary with results.
Native 2025 parameters and smooth temporal extensions are not evidence that
every configuration has been empirically calibrated. See :doc:`validity`.

``TtW energy`` is kJ/km; for BEVs it is stored-energy depletion. Terminal DC
energy is separately available as ``model.battery_terminal_energy`` and grid
electricity as ``electricity consumption`` in kWh/km. Preserve these boundaries
when comparing measured data. Sampling with ``stochastic(n, seed=...)`` controls
input draws, not every downstream stochastic cost adjustment.

Background scenarios are ``SSP2-NPi``, ``SSP2-PkBudg1000``,
``SSP2-PkBudg650`` and ``static``. Older 1150/500 labels are rejected.
Exports target ecoinvent 3.9 and 3.10; the bundled characterized background
matrices and export target versions are separate choices.

Known limits
------------

* The 2025 inputs combine engineering priors and selected calibration evidence; they are not a measured validation of every vehicle configuration.
* ADAC cycle reconstruction is approximate. Remaining petrol-car residuals must be interpreted with road load, temperature and operating controls.
* Target range supersedes capacity, and capacity supersedes input pack mass. Fixed total mass or explicit consumption may suppress chemistry-dependent consumption changes.

Verification status
-------------------

On 2026-10-08, the five-package installed-artifact suites passed **497 tests**,
with one existing expected two-wheeler cost failure. Wheel and sdist-built
wheel resource checks, offline core-only model/LCIA runs, strict Twine metadata
checks, README execution and the documented inventory exports passed. All five
Sphinx sites built using the release wheels and their ``docs`` extras.

The :download:`release verification record <_static/release_verification.json>`
contains versions, artifact hashes, test counts and qualifications. Builds were
local on macOS with Python 3.12; hosted CI and conda builds need separate
qualification. Existing documentation warnings are recorded. These checks
exercise packaging and software consistency; they do not establish physical
plausibility or replace the measurement evidence and limitations in :doc:`validity`.
