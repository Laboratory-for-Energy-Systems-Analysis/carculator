.. _intro:

Passenger-car life cycle assessment
===================================

``carculator`` estimates the energy use, emissions, costs and life cycle
impacts of passenger cars. You choose the vehicle type, size, year, load and
operating conditions. The model calculates the vehicle's mass and energy demand,
then combines them with production, energy-supply and end-of-life inventories.

The results describe a vehicle under the assumptions you supply. A size class
represents a generic vehicle; it is not a digital copy of a particular make or
model. Future inputs and energy scenarios are assumptions about possible futures,
not predictions guaranteed to occur.

Start here
----------

1. :doc:`installation` explains the Python environment and package versions.
2. :doc:`usage` walks through a complete calculation with 2025 inputs.
3. :doc:`interpretation` explains units, abbreviations and how to read results.
4. :doc:`validation_examples` shows comparisons with evidence and explains what
   each comparison can establish.

For equations and sources, see :doc:`modeling`. For the detailed checks and
remaining limitations, see :doc:`validity`. Older figures and parameter tables
in the methodology chapter describe their original studies; they are labelled
as historical where they do not describe current defaults.

Shared physics, electricity and fuel assumptions, impact coefficients and export
writers come from ``carculator_utils``. Core calculations use bundled data and
do not need an installed ecoinvent database or Brightway project. Exporting to
another LCA tool requires compatible background data there; see
:doc:`inventory_export`.

User's Guide
------------

.. toctree::
   :maxdepth: 2

   installation
   usage
   interpretation
   validation_examples
   inventory_export
   modeling
   structure
   validity

API Reference
-------------

.. toctree::
   :maxdepth: 2

   api

Project information
-------------------

.. toctree::
   :maxdepth: 1

   release

.. toctree::
   :maxdepth: 2
   :hidden:

   references/references
