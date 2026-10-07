# Energy assumptions across model years

The 2025 energy inputs now have consistent temporal extensions at every native
anchor (2000, 2010, 2020, 2025, 2030, 2040, 2050). All 2025 nominal values and
uncertainty distributions are preserved. These are a mixture of baseline trends,
engineering priors and limited vehicle-specific calibration, not universal
measurement-based calibration of every vehicle.

- Battery and charger efficiencies preserve relative legacy **loss** trends,
  rebased on their 2025 component priors. When no usable loss trend exists, the
  2025 prior is held constant. This changes historical estimates as well as
  projections; it corrects component boundaries rather than implying new
  measurements for those years.
- Motor/inverter efficiency (0.90), electric transmission efficiency (0.97),
  and independent hybrid motor peak/system-power ratio (0.65 where applicable)
  are explicit across years. This prevents interpolation between missing zero
  inputs and a nonzero 2025-only override.
- The bus hybrid combustion peak/system-power prior (0.70) also applies across
  years. Only the bus package uses this architecture correction.
- In the bus package, 13 m city BEVs use 8.3 kW base auxiliaries from 2020 onward.
  Earlier anchors retain their legacy values. The triangular 6.225–10.375 kW
  bounds are engineering uncertainty, shared across modern years using the
  `uncertainty_group` metadata supported by matching `carculator_utils`.
  Other bus sizes and combustion buses retain their prior auxiliary values.

`data/temporal_energy_provenance.json` archives affected original records,
original ordering, added records, methods, 2025 anchor references and the original
file hash. The shared repository's `scripts/harmonize_energy_time_trends.py`
provides the staging and restoration routines; `scripts/audit_energy_time_trends.py`
compares annual full models from 2015 through 2040. The shared Sphinx page
`temporal_energy.rst` explains the formulas and validation results.

For annual inputs, build the native-year array first, then interpolate before
constructing the vehicle model:

```python
# inputs is the vehicle-specific InputParameters object after inputs.static().
_, native = fill_xarray_from_input_parameters(inputs, scope=scope)
annual = native.astype(float).interp(year=range(2020, 2031))
```

Include the native anchors that bracket all requested years in `scope`.
Technology availability and discrete chemistry policies still apply; continuity
of engineering inputs does not imply availability of every powertrain in every
year. Measured vehicle-specific overrides remain preferable to generic priors.
