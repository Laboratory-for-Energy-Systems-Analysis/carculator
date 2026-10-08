.. _usage:

Usage
=====

Use the vehicle package’s input, model and inventory classes. Start with a small
static scope before expanding years, sizes or uncertainty samples.

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

The vehicle input classes provide packaged defaults. Call ``static()`` for a
single deterministic sample, or ``stochastic(n, seed=42)`` for seeded parameter
draws. The array builder returns ``(mappings, array)`` and preserves labelled
``size``, ``powertrain``, ``parameter``, ``year`` and ``value`` dimensions.
Scope by actual labels and native input years; interpolate explicitly when a
year is not in the parameter table. The current defaults include 2025.

Change input parameters before constructing a fresh vehicle model. Constructor
overrides such as battery chemistry, capacity, fuel blends and component
efficiencies are copied, preserving the caller's data. Most vehicle overrides
use ``(powertrain, size, year)`` keys; consult the model API for exceptions.
Repeated ``set_all()`` calls on an already completed model are not the supported
way to compare independent scenarios.

Energy and results
------------------

``model["TtW energy"]`` is kJ per vehicle-kilometre. For BEVs it is net
stored-energy depletion; ``model.battery_terminal_energy`` is a separate DC
boundary, and ``model["electricity consumption"]`` is grid electricity in
kWh/km. Multiply the latter by 100 for kWh/100 km.

Construct the inventory with the completed model, not its raw parameter array.
Use ``calculate_impacts()`` and labelled selection/reduction of the returned
xarray. Functional units are ``vkm``, ``pkm`` and ``tkm``. Passenger- and
cargo-normalized results require finite positive loads for active vehicles.
Availability-masked zero consumption does not describe a zero-energy vehicle.

BEV range targets converge battery mass and energy demand together. Range
takes precedence over capacity; capacity takes precedence over input pack mass.
See :doc:`modeling` for capacity, chemistry and mass examples.


Inventory export
----------------

Install the optional export dependencies described in :doc:`installation`.
After a complete model and inventory calculation, the shared public API is:

.. code-block:: python

   paths = inventory.export_lci(
       ecoinvent_version="3.10",
       software="brightway2",
       format="file",
       directory="exports",
       filename="vehicle-comparison",
   )

``software`` accepts ``brightway2`` or ``simapro``. Brightway export supports
``file``, ``string`` and ``bw2io``; SimaPro supports ``file`` and ``string``.
The supported ecoinvent targets are 3.9 and 3.10. Multi-year runs preserve every
year in the returned exports, and exporting does not change the original
inventory or calculated impacts. A destination Brightway/ecoinvent setup is
needed to register and link exported inventories, not for the core calculation.

Reproducibility and interpretation
----------------------------------

Record package versions, input overrides, driving cycle, load, geography,
fuel blend, background scenario, functional unit and energy meter boundary.
Seeded parameter draws do not seed every downstream cost adjustment.
See :doc:`release` for migration notes and :doc:`validity` for the scope of
calibration, measurement comparisons and known limitations.
