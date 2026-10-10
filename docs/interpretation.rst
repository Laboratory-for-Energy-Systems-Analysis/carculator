Understanding inputs and results
================================

A calculation has three stages: choose vehicle inputs, calculate its physical
performance, then calculate its life cycle inventory and impacts. The last stage
includes production and energy supply as well as emissions during driving.

The words used in the guides
----------------------------

* **Driving cycle:** speed at each time step, with a road-gradient profile.
  Two tests with different speed or gradient profiles need not give the same
  consumption, even for the same vehicle.
* **Curb mass:** vehicle mass including onboard fuel, excluding people and cargo
  in this model. **Driving mass** adds people and cargo.
* **Powertrain:** the engine, motor and associated components that propel the
  vehicle. ``ICEV-p``, ``ICEV-d`` and ``ICEV-g`` mean petrol, diesel and gas
  vehicles. ``BEV`` means battery electric; ``FCEV`` means hydrogen fuel-cell
  electric. ``HEV`` is a hybrid without plug-in charging; ``PHEV`` is a plug-in
  hybrid. Each package supports its own subset of these choices.
* **Auxiliaries:** equipment that uses energy without propelling the wheels,
  such as pumps, electronics and cabin heating or cooling. HVAC means heating,
  ventilation and air conditioning.
* **Sample:** one set of input values. A static calculation has one sample.
  Monte Carlo calculations draw several samples to explore specified uncertainty.
* **Inventory:** the quantities of materials, energy and emissions attributed
  to a vehicle or transport service. **Foreground** means the vehicle and supply
  processes assembled explicitly by the model. **Background** means the other
  supplying processes represented by database coefficients.
* **LCIA:** life cycle impact assessment, which converts inventory quantities
  into indicators such as climate change. An impact score is not a direct
  measurement of emissions from the vehicle.
* **Proxy:** a documented substitute used when a dataset for the exact vehicle,
  process or location is unavailable. Its suitability must be assessed for the
  study.
* **Provenance:** the record of data sources, assumptions, software versions and
  file checksums needed to trace a result.

Energy quantities are different measurements
--------------------------------------------

.. list-table:: Outputs and units
   :header-rows: 1
   :widths: 30 20 50

   * - Output
     - Unit
     - Meaning
   * - ``TtW energy``
     - kJ/vehicle-km
     - Fuel energy for combustion and fuel-cell vehicles; net stored-battery energy used by a
       BEV, including battery losses. TtW abbreviates tank-to-wheel.
   * - ``electricity consumption``
     - kWh/vehicle-km
     - Electricity purchased for charging, including battery-charge and charger
       losses. Multiply by 100 for kWh/100 km.
   * - ``battery_terminal_energy``
     - kJ/vehicle-km
     - Net direct-current (DC) energy at the battery terminals, recorded separately
       from stored-energy depletion. Divide by 36 for kWh/100 km.
   * - ``fuel consumption``
     - L/vehicle-km
     - Model fuel volume. Multiply by 100 for L/100 km. Compare gaseous-fuel
       measurements in kg using fuel mass or the blend density, not litres.
   * - ``electric energy stored``
     - kWh
     - Nominal battery capacity. Usable energy also depends on the depth-of-discharge
       assumption; this is a capacity, not energy used per kilometre.

For BEVs, charging electricity is usually measured on the alternating-current
(AC) side of the charger. A battery DC measurement excludes charger losses.
Do not compare the two directly or add charging losses to an output that already
includes them. For a plug-in hybrid, report both fuel and purchased electricity,
with the fraction of distance driven electrically. Its combined ``TtW energy``
is not a substitute for those two purchased-energy quantities.

Passenger cars and trucks use annual-average cabin heating and cooling inputs.
Two-wheelers do not model cabin HVAC. All three reject ambient-temperature
overrides. Buses support an outside
temperature or twelve monthly values; their cabin-temperature assumption is fixed
at 20 degrees Celsius. This restriction does not make bus heating and cooling
independent of outside temperature.

Choosing a unit for life cycle impacts
--------------------------------------

The ``functional_unit`` argument specifies the transport service being compared:

* ``vkm``: one vehicle travelling one kilometre.
* ``pkm``: one passenger transported one kilometre. The vehicle result is divided
  by the modelled number of passengers.
* ``tkm``: one tonne of cargo transported one kilometre. The vehicle result is
  divided by cargo mass in tonnes, not gross vehicle mass.

For example, 0.20 kg CO2-eq per vehicle-km with two passengers is 0.10 kg CO2-eq
per passenger-km. This is an arithmetic example, not a model result. Active
vehicles need a positive passenger or cargo load for these divisions.

Car, truck and two-wheeler cost outputs are per vehicle-kilometre. Bus cost
outputs are per passenger-kilometre. Costs are financial estimates; they are
not environmental impact indicators.

Reading a climate result
------------------------

``calculate_impacts()`` separates contributions along the ``impact`` axis.
Select an ``impact_category`` before adding these contributions. Do not sum
categories expressed in different units, or add results for different vehicles,
years or samples unless that aggregation answers your study question.

In the bundled ``method="recipe", indicator="midpoint"`` set, the category
``climate change`` uses **IPCC 2021, 100-year global warming potentials, excluding
biogenic CO2**. The selector names the collection of indicators; it does not
mean that this climate row uses ReCiPe's own climate factors. The separate
``climate change w bio`` category includes biogenic CO2.

A life cycle climate score includes manufacturing, energy supply, use and
end-of-life contributions. It differs from tailpipe CO2 and from fuel
consumption. Changing the background database can change the life cycle score
while leaving vehicle mass and consumption unchanged.

Assessing confidence in a result
--------------------------------

**Verification** checks that the program implements its equations and accounting
correctly. **Calibration** adjusts an assumption using observations.
**Independent validation** tests predictions against evidence not used to make
that adjustment. A **screening comparison** is an initial comparison for which
important conditions, such as route or test mass, do not fully match.

The difference reported in the comparison pages is
``100 * (model - reported) / reported``. Positive values mean the model is higher.
This difference is not a confidence interval or a general measure of model
accuracy. Several cycles or two meters on one vehicle do not constitute several
independent vehicles. See :doc:`validation_examples` for concrete cases and
:doc:`validity` for the detailed evidence.
