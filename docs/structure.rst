.. _structure:

Model structure
===============

The public workflow is ``CarInputParameters`` -> parameter array -> ``CarModel``
-> ``InventoryCar`` -> impacts or exported inventories. Vehicle-specific defaults
and mass/cost calculations live in ``carculator``; common physics and inventory
machinery live in ``carculator_utils``. See :doc:`usage` for a runnable example.

Inputs and sizing
-----------------

``CarInputParameters`` loads static or sampled assumptions. The array builder
selects size, powertrain and year while preserving labelled samples. ``CarModel``
combines vehicle masses, power and battery properties in a bounded sizing loop.
For BEV target-range runs, battery mass and energy use converge together before
costs, direct emissions and inventories are calculated.

Energy and emissions
--------------------

The shared driving-cycle loader supplies speed and gradient. Road load, shaft
power, auxiliary demand and conversion losses determine fuel or electricity
requirements. Stored battery energy, terminal DC energy and grid electricity
have separate accounting boundaries. Shared modules calculate fuel-related CO2,
hot exhaust pollutants, non-exhaust particles and noise. See :doc:`modeling`
and :doc:`validity` for equations, sources and validation limits.

Life cycle inventories and results
----------------------------------

``InventoryCar`` links the completed vehicle to manufacturing, maintenance,
energy supply and direct emissions. Background fuel blends, electricity mixes
and scenario-specific characterized factors support impact calculations.
Functional-unit normalization and inventory export are separate operations;
exports use copies so repeated calls preserve calculated results and all years.
