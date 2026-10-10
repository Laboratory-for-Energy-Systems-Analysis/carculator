How the package fits together
=============================

The calculation follows the same sequence as the example in :doc:`usage`:

1. ``CarInputParameters`` loads parameter records, units and uncertainty distributions.
   Call ``static()`` for central values or ``stochastic(n, seed=...)`` for samples.
2. ``fill_xarray_from_input_parameters()`` builds a labelled array and its
   coordinate mappings. Select the sizes, powertrains and years needed for the study.
3. ``CarModel`` accepts this array and any constructor overrides. ``set_all()``
   calculates masses, component sizes, energy demand, direct emissions and costs.
4. ``InventoryCar`` combines the calculated vehicle with material and energy
   suppliers. ``calculate_impacts()`` returns results by impact category and
   contribution group.
5. Export methods write foreground inventories for use in another LCA tool.
   Linking them to that tool's background database is a separate step.

The vehicle packages contain their own defaults and sizing rules.
``carculator_utils`` supplies the common array handling, cycle physics, fuel and
electricity systems, emissions, matrix calculations and export interface. The
bare shared input class has no standalone vehicle defaults.

Key files for readers of the code
---------------------------------

* ``vehicle_input_parameters.py`` and ``array.py`` load and arrange inputs.
* ``model.py`` calculates vehicle properties; vehicle packages extend this class.
* ``energy_consumption.py`` calculates power over the driving cycle.
* ``background_systems.py`` selects fuel properties and electricity shares.
* ``inventory.py`` assembles inventories and calculates impact scores.
* ``export.py`` prepares inventories for the supported export writers.

The last four shared files live in ``carculator_utils``; a vehicle package may
also have its own ``model.py`` and ``inventory.py``. See :doc:`interpretation` for
units and :doc:`validity` for checks on these interfaces. Input samples, sizing
iterations and background scenarios are different concepts and should not be
used interchangeably when reporting a study.
