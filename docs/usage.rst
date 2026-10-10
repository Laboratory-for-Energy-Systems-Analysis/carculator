.. _usage:

Usage
=====

The example below loads default inputs, calculates the vehicle, and then
calculates its life cycle impacts. Start with one year and a few vehicles. Add
more years, vehicle types or uncertainty samples once that example works.

Quick start
-----------

.. code-block:: python

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


Inputs and scope
----------------

The input classes load the default parameter tables. ``static()`` uses one
set of central values. ``stochastic(n, seed=42)`` draws ``n`` sets from the
specified uncertainty distributions; using the same seed repeats those draws.

The array builder returns ``(mappings, array)``. The array has labelled axes for
``size``, ``powertrain``, ``parameter``, ``year`` and ``value``; ``value`` identifies
the sample. The ``scope`` dictionary selects vehicles and years, rather than
changing their assumptions. Use labels and years present in the parameter
tables, including 2025. For other years, interpolate the input array explicitly
before constructing the vehicle model.

Change input parameters before constructing a fresh vehicle model. Constructor
overrides such as battery chemistry, capacity, fuel blends and component
efficiencies are copied, preserving the caller's data. Most vehicle overrides
use ``(powertrain, size, year)`` keys; consult the model API for exceptions.
Calling ``set_all()`` again is supported: it starts from saved inputs,
including explicit edits, rather than using calculated outputs as new inputs.
Use a fresh model for a separate scenario, new coordinates, or changes to the
component assumptions of a plug-in hybrid.

Energy and results
------------------

See :doc:`interpretation` for units, powertrain abbreviations, and the difference
between energy use, direct emissions and life cycle impacts.

``model["TtW energy"]`` is kJ per vehicle-kilometre. For BEVs it is net
stored-energy depletion; ``model.battery_terminal_energy`` is a separate DC
boundary, and ``model["electricity consumption"]`` is grid electricity in
kWh/km. Multiply the latter by 100 for kWh/100 km.

Construct the inventory with the completed model, not its raw parameter array.
Use ``calculate_impacts()`` and labelled selection/reduction of the returned
xarray. Functional units are ``vkm``, ``pkm`` and ``tkm``. Passenger- and
cargo-normalized results require finite positive loads for active vehicles.
A zero reported for an unavailable or infeasible vehicle is a status marker,
not a prediction of zero energy use.

BEV range targets converge battery mass and energy demand together. Range
takes precedence over capacity; capacity takes precedence over input pack mass.
See :doc:`modeling` for capacity, chemistry and mass examples.


Inventory export
----------------

The shared runtime includes Brightpath and its export writers. Continue with
the completed inventory from the quick start:

.. code-block:: python

   workbook = inventory.export_lci(
       ecoinvent_version="3.12",
       software="brightway2", format="file", directory="exports",
   )
   simapro_csv = inventory.export_lci(
       software="simapro", format="file", directory="exports",
   )
   foreground_zip = inventory.export_lci(
       software="openlca", format="file", directory="exports",
   )

Export requires exactly one selected sample, selected before constructing the
model and inventory. The static quick start already has one sample. Every
selected year gets an export; multiple years return a list. The original
inventory, calculated impacts and functional unit remain unchanged.

The default ``export_lci()`` returns an unlinked Brightway ``LCIImporter``.
Exports default to **ecoinvent 3.12 cutoff**, matching the bundled background.
Older ``3.9`` and ``3.10`` targets raise an error when a required supplier has no
verified counterpart in that version. The
openLCA ZIP contains foreground processes without an ecoinvent background or
LCIA methods; map external providers and elementary flows before calculation.
SimaPro uses Latin-1 CSV and warns when custom noise flows are omitted.
See :doc:`inventory_export` for the full format/return-value table, sample
selection and linking requirements.

Reproducibility and interpretation
----------------------------------

Record package versions, input overrides, driving cycle, load, geography,
fuel blend, background scenario, functional unit and energy meter boundary.
``stochastic(n, seed=42)`` also seeds projected-cost factors. Keep the array's
auxiliary coordinates and build fresh models for independent runs. See the
`shared cost-uncertainty guide
<https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator_utils/blob/master/docs/cost_uncertainty.rst>`_
for sample selection, serialization and legacy-array behavior.
See :doc:`validity` for the scope of
calibration, measurement comparisons and known limitations.


Battery unit costs
------------------

Explicit battery unit prices survive chemistry selection and automatic cost
adjustment. Using the input array from the quick start above:

.. code-block:: python

   model = CarModel(
       array,
       battery_costs={
           "energy battery cost per kWh": {("BEV", "Medium", 2025): 100},
       },
   )
   model.set_all()

The amount is EUR/kWh of nominal capacity before markup; use
``power battery cost per kW`` for power batteries (EUR/kW). Amounts must be finite
and nonnegative, either scalar or one per sample in the array's sample order.
Zero and prices equal to packaged inputs are supported.

Ordinary battery-cost array edits and changed dictionary/file definitions also
survive, provided the array retains the reference coordinates supplied by the
current array builder. Use the constructor for old or hand-built arrays, or for
an explicit price equal to the original input. An explicit generic price wins
over an explicit price for the selected chemistry; untouched inputs keep the
existing year trajectory. Prices affect purchase and replacement costs without
changing mass, energy use or environmental inventories.

See the shared `battery-cost guide
<https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator_utils/blob/master/docs/battery_costs.rst>`_
for chemistry selection, sensitivity, provenance and plug-in-hybrid component
inputs. This change preserves supplied prices; it does not recalibrate the
underlying default cost curve.


Multi-year cost calculations
----------------------------

Automatic component-cost projections now align year and sample labels explicitly.
This corrects a reshaping error that mixed prices between years and samples in
multi-year uncertainty and sensitivity runs. The sensitivity reference now agrees
with static costs in each year; the default BEV battery prices are EUR 186.49,
134.64 and 102.57/kWh in 2020, 2025 and 2030, respectively.

The equations, uncertainty distributions and explicit battery-price precedence
are unchanged. Static calculations retain their previous results. Regenerate
multi-year sensitivity costs calculated with the old projection, and stochastic
costs calculated before cost factors were tied to the input seed. Each sample's
factor applies across all years and survives reordering or selection, including
selection of just one sample. ``stochastic(1)`` now also draws a cost factor;
use ``static()`` for deterministic inputs and prices.

Completed regressions compare sensitivity references with static results across
battery-electric and combustion powertrains. Paired runs with the pre-fix cost
hooks also verify unchanged physical outputs, inventories and LCIA. These checks
validate the numerical assignment of costs, not the empirical price assumptions.


Repeated completion
-------------------

Repeated ``set_all()`` calls reuse retained inputs instead of previous results.
Existing coordinate selections and explicit input-cell edits are supported.
Modify PHEV component inputs in a fresh model rather than aggregated outputs.
See the `shared guide to repeated runs
<https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator_utils/blob/master/docs/repeated_runs.rst>`_.

Bundled parameter scopes
------------------------

Bundled records now have unique parameter/size/powertrain/year cells. The cleanup
preserves the formerly effective first record, including its distribution and
source, rather than choosing a new scientific value from a conflicting later
record. Original overlapping records and replacement scopes are archived in
``data/overlap_resolution_provenance.json``. Split scopes share an uncertainty
group. Regenerate saved stochastic arrays: removing redundant records can change
seeded draw sequences, while their distributions remain the same. Explicit
custom dictionaries retain first-entry precedence for compatibility; audit them
with ``validate_parameters(records, check_duplicates=True)``.

Additional gas leakage
----------------------

``CNG pump-to-tank leakage`` now defaults to zero at all tabulated years. This
excludes an unqualified overlay beyond the delivered-fuel supplier boundary; it
does not remove upstream emissions or exhaust methane, or assert that actual
vehicle leakage is zero. The former 0.004 prior combined potentially overlapping
delivery/storage/vehicle stages. Supply a documented residual loss (kg lost/kg
engine fuel) for the selected pathway when available. Original records and
source/boundary rationale are packaged in ``data/methane_leakage_provenance.json``.
