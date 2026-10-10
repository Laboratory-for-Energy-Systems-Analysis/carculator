Inventory export with Brightpath
================================

``InventoryCar`` inherits ``export_lci()`` from ``carculator_utils``, which uses
Brightpath to write Brightway Excel, SimaPro CSV and openLCA JSON-LD files.
The shared runtime installs ``brightpath>=1.0.0a6,<1.1`` and its writers;
see :doc:`installation`. This uses Brightpath's v1 API, currently an alpha.
Core model and LCIA calculations use bundled resources without importing
Brightpath or Brightway or opening a Brightway project.

Write inventory files
---------------------

Continue with the completed ``inventory`` from :doc:`usage`:

.. code-block:: python

   workbook = inventory.export_lci(
       ecoinvent_version="3.12",
       software="brightway2", format="file", directory="exports",
   )
   simapro_csv = inventory.export_lci(
       ecoinvent_version="3.12",
       software="simapro", format="file", directory="exports",
   )
   foreground_zip = inventory.export_lci(
       ecoinvent_version="3.12",
       software="openlca", format="file", directory="exports",
   )

The default target is **ecoinvent 3.12 cutoff**, matching the rebuilt LCA
background. Logical supplier labels and disaggregations resolve to their 3.12
identities. Legacy ``"3.9"``/``"3.10"`` exports reject newly introduced suppliers
without verified older counterparts; complete backward compatibility is not
claimed. Match external suppliers and elementary flows to the corresponding
background in the destination tool before calculation.

Exports operate on copies: the original inventory, calculated impacts and
selected functional unit (``vkm``, ``pkm`` or ``tkm``) are preserved.

Formats and return values
-------------------------

.. list-table:: Outputs for one model year
   :header-rows: 1

   * - ``software``
     - ``format="file"``
     - ``format="string"``
     - ``format="bw2io"``
   * - ``brightway2``
     - Excel ``.xlsx`` path
     - List of Excel bytes, even for one year
     - Unlinked ``LCIImporter``
   * - ``simapro``
     - CSV path
     - Decoded Latin-1 CSV text
     - Unsupported
   * - ``openlca``
     - JSON-LD ``.zip`` path
     - ZIP bytes
     - Unsupported

Multiple years return a list in model-year order, with one artifact per year.
Filenames include the year. ``format="string"`` uses temporary files and does
not create the supplied destination directory.

The default remains ``software="brightway2", format="bw2io"``. Explicitly use
``format="file"`` or ``format="string"`` with SimaPro and openLCA. Calling
``inventory.export_lci()`` returns an importer (or a list for multiple years);
it does not automatically register, link or write a Brightway database.

Select one sample
-----------------

Export requires exactly one retained ``value`` sample. The static quick start
already meets this requirement. For sampled inputs, select a draw from the raw
input array before constructing a fresh model and inventory. Using the imports
and ``array`` from :doc:`usage`:

.. code-block:: python

   selected = array.isel(value=[0])  # Change the position to choose another draw.
   model = CarModel(selected, cycle="WLTC")
   model.set_all()
   inventory = InventoryCar(model, functional_unit="vkm")
   importer = inventory.export_lci(format="bw2io")

Brackets preserve the ``value`` dimension. Numeric labels other than zero and
named samples such as ``reference`` are supported; use
``array.sel(value=["reference"])`` when that sensitivity sample is present.
Multiple selected samples raise an error. Export does not average draws or
create uncertainty distributions or presamples arrays.

SimaPro migration
-----------------

CSV output now follows Brightpath's layout: semicolon delimiters, standard CSV
quoting and Latin-1 encoding. Save returned strings with ``encoding="latin-1"``.
Embedded line breaks use SimaPro's DEL character (``\x7f``), and characters
outside Latin-1 are transliterated. Product identifiers include reference
product, geography and activity name. Update consumers that depend on the
previous CSV layout or identifiers.

Activity-specific comments and sources take precedence over catalog metadata;
sources appear as ``Source: ...``. SimaPro cannot represent the 24 custom
octave/time/location noise flow identities in its standard flow sections.
These were also omitted by the previous exporter; omission now emits a warning.
Other exchanges reported as unrepresented by Brightpath fail export.
Brightway and openLCA retain the custom noise names, amounts and compartments;
this does not establish characterization in the destination database.

openLCA scope and linking
-------------------------

The JSON-LD ZIP contains **foreground processes only**, with their connected
product flows, elementary flows, units and locations. It contains neither the
ecoinvent background nor LCIA methods. Brightpath has no packaged openLCA
identifier catalog for these ecoinvent targets: generated external references
must be mapped to background providers and characterized elementary flows in
the destination database before calculation. Each openLCA export warns about
this requirement.

Carculator builds activities and exchanges, normalizes functional units and
supplies vehicle, fuel and electricity provenance. Brightpath handles format
normalization, structural validation and serialization. Structural validation
does not verify external links against a licensed background database, and an
importable file does not establish equivalent LCIA results in another tool.
The automated checks do not establish successful GUI imports or numerical
equivalence inside SimaPro or openLCA.

See the `shared exporter guide
<https://github.com/Laboratory-for-Energy-Systems-Analysis/carculator_utils/blob/master/docs/inventory_export.rst>`_
for the implementation responsibilities and verification scope.
