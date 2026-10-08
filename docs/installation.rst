.. _install:

Installation
============

Use Python **3.12** (``>=3.12,<3.13``) in a fresh environment.
The shared runtime requires NumPy ``>=1.26.4,<2``.

Published release
-----------------

After ``1.9.6`` is published on PyPI::

   python3.12 -m venv .venv
   source .venv/bin/activate
   python -m pip install "carculator==1.9.6"

On Windows activate with ``.venv\Scripts\activate``. Alternatively, create a
conda environment with ``conda create -n carculator-release python=3.12 pip``,
activate it, and use the same pip command. Availability of a conda package is
separate from the PyPI release.

Core calculations use bundled resources without a Brightway project, an
ecoinvent installation or network access. For export support::

   python -m pip install "carculator[excel,brightway]==1.9.6"

The Brightway extra intentionally targets the legacy stack (``bw2io<0.9``,
``bw2data<4``, ``bw2calc<2``). Importing exported inventories requires a matching
background database in the destination LCA tool.

Source checkout and documentation
---------------------------------

Before publication, use the matching sibling checkouts and install from this
repository root::

   python -m pip install -e "../carculator_utils[test,excel,brightway]" -e ".[test,docs,excel,brightway]"
   python -m pip check
   python -m pytest
   python -m sphinx -b html docs docs/_build/html

The ``docs`` extra includes the Sphinx extensions used here. See :doc:`release`
for migration notes and the :download:`release checklist <../RELEASING.md>` for
wheel/source-distribution verification.
