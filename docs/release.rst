Release notes
=============

1.9.6
-----

When upgrading from an earlier version:

* Create a Python 3.12 environment and install the updated package as described
  in :doc:`installation`. This version requires ``carculator_utils>=1.3.6``.
* Recalculate saved scenarios: changes to energy accounting, battery sizing,
  costs and emissions can affect results.
* Select a supported background scenario: ``SSP2-NPi``,
  ``SSP2-PkBudg1000``, ``SSP2-PkBudg650`` or ``static``. Older ``1150`` and
  ``500`` pathway labels are no longer accepted.

Inventory export now uses Brightpath through ``carculator_utils``. Writers are
runtime dependencies; the ``brightway`` extra selects the tested legacy stack.
Retain one sample before constructing the model and inventory. Brightway
importers remain unlinked; SimaPro consumers must account for its new Latin-1
layout and identifiers. The new openLCA JSON-LD ZIP contains foreground processes
and requires provider and elementary-flow mapping before calculation. See
:doc:`inventory_export` for migration details and return values.

The :download:`changelog <../CHANGELOG.md>` lists the changes in each version.
See :doc:`validity` for calibration evidence and the scope of model validation.
