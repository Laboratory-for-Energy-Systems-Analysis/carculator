Calendar-year lifecycle impacts
===============================

``carculator`` can optionally assign the completed passenger-car inventory to
calendar years.  The ordinary ``calculate_impacts()`` result and all exports
remain lifetime aggregates; temporalization is an additional view of the same
foreground exchanges.

Quick start
-----------

Complete the model and inventory as usual, then request the schedule or the
characterized result::

   from carculator import CarInputParameters, CarModel, InventoryCar
   from carculator import fill_xarray_from_input_parameters

   inputs = CarInputParameters()
   inputs.static()
   _, array = fill_xarray_from_input_parameters(
       inputs,
       scope={
           "size": ["Medium"],
           "powertrain": ["BEV", "ICEV-p"],
           "year": [2025],
       },
   )
   model = CarModel(array)
   model.set_all()
   inventory = InventoryCar(model, scenario="SSP2-NPi")

   schedule = inventory.lifecycle_schedule()
   impacts = inventory.calculate_temporal_impacts()
   audit = inventory.temporal_coverage()

``year`` remains the vehicle cohort year and denotes its first operating year.
``calendar_year`` is the year in which an event is assigned. The impact result
also has a ``lifecycle_stage`` dimension with manufacturing, use, maintenance,
replacement and end-of-life stages. ``normalization="vehicle"`` is the default;
``normalization="functional_unit"`` divides by lifetime vehicle-kilometres.

Passenger-car maintenance frequency
-----------------------------------

The default is a temporal allocation convention, not maintenance advice for a
specific make, model, market or duty cycle.

.. list-table:: Default passenger-car maintenance timing
   :header-rows: 1
   :widths: 28 22 50

   * - Powertrain
     - Frequency
     - Distance threshold used for each vehicle cell
   * - ICEV-p, ICEV-d and ICEV-g
     - Every 1 year
     - ``1 * kilometers per year``
   * - HEV-p and HEV-d
     - Every 1 year
     - ``1 * kilometers per year``
   * - PHEV-p and PHEV-d
     - Every 1 year
     - ``1 * kilometers per year``
   * - FCEV
     - Every 1 year
     - ``1 * kilometers per year``
   * - BEV
     - Every 2 years
     - ``2 * kilometers per year``

Thus two BEVs with different assumed annual mileages receive maintenance in
the same operating years but have different kilometre thresholds.  A threshold
exactly reached at year end is assigned to that operating year: annual service
starts in the cohort year and a two-year interval first appears in the next
calendar year.  A fractional allocation in the final operating year conserves
the original distance-proportional maintenance inventory; it does not represent
a partial workshop visit.

The split reflects the broad official schedules reviewed for this assumption.
For example, Peugeot lists annual petrol/hybrid/PHEV service and a two-year
scheduled interval for electric passenger cars after their initial operation
check.  Manufacturer schedules differ, and the model deliberately uses a
family-level convention rather than claiming a universal OEM rule.  See the
`Peugeot service schedule <https://www.peugeot.co.uk/owners/peugeot-ownership-offers-peugeot-uk/service-care-plan.html>`_.

Timing by component and exchange type
-------------------------------------

.. list-table:: Passenger-car temporalization contract
   :header-rows: 1
   :widths: 24 19 37 20

   * - Component or burden
     - Lifecycle stage
     - Default timing
     - Recurrence basis
   * - Glider, lightweighting and assembly
     - Manufacturing
     - Year -1, before first use
     - Once per vehicle
   * - Combustion engine, motor, inverter, converter and power distribution
     - Manufacturing
     - Year -2, before final assembly
     - Once per vehicle
   * - On-board charger and fuel or hydrogen tanks
     - Manufacturing
     - Year -2, before final assembly
     - Once per vehicle
   * - Initial traction battery
     - Manufacturing
     - Year -2, before final assembly
     - Once per vehicle
   * - Traction-battery replacements
     - Replacement
     - Distance/calendar threshold used by the completed model; throughput is
       used when it is the available lifetime basis
     - Modelled replacement count, including fractional legacy counts
   * - Initial fuel-cell stack and balance of plant
     - Manufacturing
     - Year -2, before final assembly
     - Once per vehicle
   * - Fuel-cell replacements
     - Replacement
     - Stack operating-hour lifetime converted with cycle average speed
     - Modelled replacement count
   * - Scheduled maintenance and refrigerant replenishment supplier
     - Maintenance
     - Annual except BEVs every two years
     - Vehicle-specific annual mileage threshold
   * - Electricity, hydrogen and fuel supply
     - Use
     - Every operating year, including exact distance in the final partial year
     - Per vehicle-kilometre
   * - Exhaust, abrasion, noise and direct refrigerant emissions
     - Use
     - Every operating year
     - Per vehicle-kilometre
   * - Road construction and road maintenance
     - Use
     - Every operating year
     - Per vehicle-kilometre
   * - Used replacement battery
     - End of life
     - In each battery-replacement year
     - One disposal share per replacement
   * - Final battery, powertrain dismantling, fuel-tank treatment and other
       explicit vehicle end-of-life exchanges
     - End of life
     - One year after the final operating year
     - Once at final end of life

Year zero is the first operating year. The -1 and -2 buckets express ordering
at annual resolution, not exact factory lead times. Glider suppliers remain
with final assembly in year -1; separately exposed components are assigned to
year -2 by default.

Manufacturing can be moved or spread before the cohort year with component
profiles::

   from carculator_utils import TemporalPolicy

   policy = TemporalPolicy(
       manufacturing={
           "vehicle": {-2: 0.2, -1: 0.5, 0: 0.3},
           "battery": {-1: 0.4, 0: 0.6},
       },
       end_of_life_offset=1,
   )
   impacts = inventory.calculate_temporal_impacts(policy)

Maintenance overrides
---------------------

Use a scalar year interval for all selected cars, or match full vehicle labels,
powertrains and a fallback::

   all_annual = TemporalPolicy(maintenance_interval_years=1)
   selected = TemporalPolicy(
       maintenance_interval_years={"BEV": 3, "default": 1}
   )

An explicit kilometre interval is retained for compatibility and takes
precedence over the year frequency::

   distance_based = TemporalPolicy(
       service_intervals={"maintenance": 40_000}
   )

Backgrounds, electricity and boundaries
---------------------------------------

Characterization factors are interpolated for each event year.  The national
charging mix is also interpolated independently for each operating year; it is
not the lifetime-average electricity mix used by ordinary LCIA.  Values outside
the available horizon use the nearest endpoint by default. Set
``background_horizon="error"`` or the background configuration's
``"temporal electricity horizon"`` to ``"error"`` to reject extrapolation.

Only direct foreground exchanges exposed by the reduced inventory can be dated.
End-of-life operations already embedded in a glider, engine or other background
supplier stay with that supplier's event. Tyre and other wear-part replacements
are not separate component events; their existing production or maintenance
proxy remains in those exchanges. Temporalization is calendar assignment, not
impact discounting or dynamic atmospheric fate modelling.

Use ``inventory.temporal_coverage(policy)`` and
``inventory.lifecycle_events.to_dataset()`` to audit the resolved maintenance
frequency, event-year range and exchange classification.  The shared
``carculator_utils`` calendar-year guide is the normative API and boundary
reference for all vehicle families.
