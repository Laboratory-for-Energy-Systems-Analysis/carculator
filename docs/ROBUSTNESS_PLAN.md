# Carculator family robustness and installation plan

Prepared 2026-10-06 from the [repository audit](REVIVAL_AUDIT.md).
Status: first hardening batch implemented; see [HARDENING_PROGRESS.md](HARDENING_PROGRESS.md)
for completed changes, executed evidence, numerical changes, and outstanding work.
Scope: carculator_utils, carculator, carculator_bus, carculator_truck,
carculator_two_wheeler, flaskCarculator, and carculator_online.

## 1. Intended outcome and boundaries

Deliver a coordinated, documented package family in which supported inputs give
validated, reproducible results; invalid inputs fail with useful diagnostics;
calculations cannot silently corrupt subsequent calculations; and released
artifacts install and execute in clean supported environments.

“Install-proof” means a tested support matrix and actionable failure messages.
It cannot mean compatibility with every Python version or arbitrary combinations
of third-party packages. Installation claims must be backed by tests of the actual
release artifacts, outside a source checkout.

Keep existing public imports, vehicle labels, result dimensions, and scientific
assumptions stable where possible. Explicit bug fixes may change results: record
and explain those changes. Numerical cleanup, scientific data updates, dependency
upgrades, and mechanical refactoring should have separate changesets and evidence.

Keep the seven repositories for now. A monorepo migration, new LCA formulation,
and wholesale class rewrite are unnecessary prerequisites. Maintain a shared
compatibility manifest and common test cases without merging the projects.

The current baseline is 92 passing tests and one bus failure, with substantial
coverage gaps. It establishes where to start, not scientific correctness.

## 2. Proposed support and compatibility policy

| Area | Initial stabilization target | Later expansion |
| --- | --- | --- |
| Python | 3.11 and 3.12 after clean-install qualification; advertise only passing combinations | Qualify 3.13/3.14 after scientific dependency migration; probe newer Python separately |
| Platforms | Linux x86_64, macOS arm64, Windows x86_64 | Add architectures only with executed installation/model tests |
| NumPy | Preserve the current <2 contract while correcting calculations | Separate NumPy 2 migration with old/new numerical comparison |
| Brightway | Preserve existing legacy export behavior during stabilization | Independently qualify newer bw2io/Brightway stacks and export versions |
| Package installation | PyPI wheels and sdists, editable development install | Conda packages qualify through their own installation tests |
| Reproducibility | Exact application/test environment constraints and a package-family compatibility manifest | Supported dependency-range expansion through scheduled compatibility tests |

Python 3.10 reached end of life on 2026-10-01; it should not be the new support
baseline. Python 3.11 is a transition floor rather than the long-term target.
Recheck lifecycle dates at release time. [Python version status](https://devguide.python.org/versions/).

Library metadata should express tested dependency ranges and directly imported
requirements. Exact locks belong to deployments and reproducibility environments.
Do not impose speculative upper bounds on every dependency; constrain known
incompatibilities and document why. Set an explicit tested compatibility policy
for the tightly coupled utils/vehicle interfaces.

Preserve the distinction between the API TCS branch and main. Stabilize TCS first;
qualify main's additional features separately. Neither the conflicting utils tag
nor the API's file-identical divergent history needs rewriting to implement this plan.

## 3. Delivery sequence and gates

| Stage | Main deliverables | Depends on | Completion gate |
| --- | --- | --- | --- |
| A: Test foundation | Reproducible environments, small fixtures, failure reproductions, artifact-install prototype | Audit | Tests run without user datasets, repository writes, or hidden local imports |
| B: Correctness repairs | Battery/input/sensitivity/export fixes; finite-result checks | A | Confirmed defects have regressions and all four modes pass representative scientific checks |
| C: Packaging | Unified metadata, explicit extras, complete resources, clean artifact installation | A; final numerical gate from B | Wheel and sdist install and run on the advertised matrix |
| D: Numerical/API contracts | Validation, array alignment, bounded convergence, immutable inputs, reproducible sampling | B | Invalid/edge cases fail deliberately; repeated and reordered runs are consistent |
| E: Maintainability | Smaller tested helpers, typed boundaries, uniform diagnostics, performance checks | D | Refactors preserve corrected baselines and improve reviewability |
| F: Consumers | API integration, local website/worker tests, versioned result mapping | B–D | Validated end-to-end use of the candidate package family |
| G: Coordinated release | Cross-repository CI, release candidates, user docs, version/provenance records | C–F | Exact tested artifacts and resolved environments satisfy the release checklist |

Packaging can progress alongside correctness work once the test foundation is
stable. Neither stream should block small defect reproductions. Modern NumPy and
Brightway migrations follow the stabilized baseline as separately gated work.

## 4. Stage A — build a reliable test foundation

### A1. Capture reproducible environments and results

- Record exact repository revisions, interpreter/platform, direct and transitive
  versions, seeds, input cases, and relevant runtime-data checksums.
- Commit compact baseline cases and machine-readable summaries in each repo.
  Keep detailed generated reports as CI artifacts, not tracked Excel workbooks.
- Preserve legacy outputs for diagnosis, but label known wrong outputs clearly.
  A bug fix must not turn a wrong baseline into a permanent expected value.
- Establish one integration manifest listing the tested five-package combination
  and API branch. Use candidate artifacts from exact commits, never an unrecorded
  mixture of branch tips and installed releases.

### A2. Make tests isolated and inexpensive

- Move model creation out of module-level test imports into fixtures.
- Use small scopes for unit/integration tests and fresh mutable models per test;
  share only immutable input resources or explicitly copied fixtures.
- Replace comparison-only spreadsheet tests with assertions and readable failure
  diagnostics. Use tmp_path for optional reports and all export outputs.
- Separate unit, contract, integration, numerical-regression, export, installation,
  and slow full-grid suites. Test collection should not run full calculations.
- Introduce a common downstream contract suite in utils/tests with optional
  downstream installs; each vehicle repo retains model-specific expectations.
- Add deterministic random seeds now; replace global RNG use in Stage D.
- Fail on unexpected numerical RuntimeWarnings in focused numerical tests.
  Temporarily allowlist specific external warnings with owner/reason/removal
  condition; do not globally suppress warnings or create broad permanent xfails.

### A3. Establish scientific reference cases

| Package | Minimum representative cases |
| --- | --- |
| Cars | Medium diesel/petrol/BEV; FCEV; petrol/diesel PHEV; a small and large size; 2020 and a future year |
| Buses | 13m-city diesel plus BEV-depot, BEV-opp and BEV-motion; FCEV; one articulated and one coach case |
| Trucks | 40t diesel/BEV long haul; 18t urban delivery; FCEV/PHEV; light and heavy payload boundaries |
| Two-wheelers | Human bicycle, electric bicycle, electric scooter, petrol motorcycle; supported/unsupported combinations |
| Backgrounds | Static and the three current IAM scenarios; CH plus a contrasting electricity mix |
| Sampling | Static, seeded stochastic with multiple samples, sensitivity reference plus named perturbations |
| Exports | Multi-year, every supported software/format/version combination and vkm/pkm/tkm where meaningful |

Use a small selected set on every PR and broader combinations nightly/release.
Do not expand this into an enormous Cartesian product on every commit.

Acceptance: clean test collection, no modified source/fixture files after tests,
repeatable small-case outputs, and explicit regression reproductions for Stage B.

## 5. Stage B — repair confirmed defects first

Each repair should contain a failing reproduction, the smallest coherent fix,
an explanation of result changes, and downstream tests.

| Priority / finding | Implementation | Required evidence |
| --- | --- | --- |
| B1: Battery preferences silently skipped | Separate required physical chemistry properties from cost preferences. Apply documented generic cost fallback when chemistry cost is absent; reject missing required physical properties with chemistry/vehicle context | Bus and two-wheeler positive density, capacity/cell-mass relation, mass-share balance; existing car/truck results preserved where inputs were already valid |
| B2: Inputs discarded | Forward parameters and extra in bus/truck/two-wheeler constructors; normalize dict/path input consistently | Custom values and extra labels actually reach arrays; empty vs None semantics; caller dictionaries unchanged |
| B3: Bus overrides overwritten | Merge chemistry/origin defaults underneath explicit caller overrides without replacing the entire energy_storage object | Requested CH origin survives; chemistry/capacity overrides survive; missing values receive defaults |
| B4: Sensitivity builder fails | Preserve named value coordinates and explicit reference/perturbation dimensions; avoid implicit string-to-float conversion or numeric relabeling | Each perturbation changes only the intended input by the declared factor; reference equals static case; end-to-end costs and impacts work |
| B5: Non-vkm export mutates A | Normalize a copy or produce an independent export representation; retain canonical internal inventory | Repeated exports equal; export before/after calculate_impacts does not alter results; correct pkm/tkm scaling |
| B6: API PHEV-p target range | Reproduce and correct the target_range/payload mix-up without changing unrelated override ordering | PHEV-p and PHEV-d tests with/without payload; preserved combustion/electric intermediate range overrides |
| B7: Noise overflow and non-finite propagation | Isolate triggering inputs; correct numerical formulation or invalid inputs at their source; stop masking invalid results as plausible numbers | Finite expected noise outputs, correct power-domain source addition, zero-distance behavior; failed valid-cell calculations remain visible |

Do not resolve B1 by inventing scientific cost values or relaxing battery tests.
Define fallback semantics using existing generic cost inputs and make them visible
in diagnostics. If no legitimate fallback exists, require the missing data.

Acceptance: original bus failure passes for the right reason, all defect
reproductions pass, and result-change reports identify affected combinations.

## 6. Stage C — make installation a tested product feature

### C1. Consistent, minimal packaging

- Migrate the four remaining core setup.py projects to pyproject.toml using the
  existing setuptools backend. Do this one repository at a time, without moving
  source files in the same change.
- Make pyproject metadata the authoritative direct dependency declaration;
  generate or check requirements/conda recipes against it rather than maintaining
  several inconsistent hand-edited lists.
- Use one authoritative version value. Preserve the public __version__ tuple
  compatibility used by consumers while exposing the standard distribution
  version string; verify equality between metadata, package and release tag.
- Align requires-python, classifiers, docs and CI. Audit direct imports so scipy,
  YAML, progress display and export engines are not available only by accident.
- Replace recursive “include everything” package discovery/data walks with
  explicit package/resource rules. Exclude notebooks, editor files and generated
  artifacts, while proving all nested scientific resources are retained.
- Keep build metadata evaluation independent of importing the scientific package.
  Building a wheel must not require importing xarray, running a model, or Git.

The proposed structure follows standard pyproject build-system, dependencies and
optional-dependencies metadata. [PyPA guidance](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).

### C2. Separate optional capabilities

Proposed utils installation surfaces:

| Installation | Capability and dependency policy |
| --- | --- |
| carculator-utils | Core parameter/model/LCIA work using bundled background data; no Brightway database required |
| carculator-utils[excel] | Excel export engine, explicitly declaring xlsxwriter; include readers only where runtime functionality uses them |
| carculator-utils[brightway] | bw2io and any genuinely required legacy export dependencies, with tested compatibility constraints |
| Development test/docs groups | pytest, coverage, fixture readers such as openpyxl, documentation tools; kept out of basic runtime installs |

Audit actual use before removing wurst/xlrd or moving any dependency. Lazy imports
already help, but mandatory dependency metadata still pulls the legacy stack in.
Moving defaults to extras changes installation expectations: provide a transition
release/migration note and an exact remedy when an optional capability is used.
Vehicle packages may forward convenience extras to utils so users do not have to
understand the dependency graph. Existing APIs should fail with a precise
capability-specific install instruction, never an unrelated import traceback.

Keep PyPI library requirements free of moving Git branch dependencies. Applications
can use exact candidate Git SHAs during integration, then locked released artifacts.

### C3. Installed package resources

- Centralize resource access using importlib.resources with explicit handling
  where a real path is required. Preserve public DATA_DIR compatibility during
  transition. Remove dependence on repository-relative working directories.
- Maintain a resource inventory: parameter JSON, cost/chemistry YAML, driving
  cycles, gradients, emission factors, activity indices, characterization matrices,
  export mappings, and API BAFU data.
- Validate resource existence, schema and index compatibility from an installed
  wheel and from a wheel rebuilt using only the unpacked sdist.
- Test a read-only package directory, arbitrary working directory, paths with
  spaces/non-ASCII characters, and explicit output locations.
- Core import and calculation must not need network access, a local ecoinvent
  installation, or a Brightway project. Optional exports have separate requirements.

### C4. Installation test protocol

For every supported platform/Python combination, using fresh environments:

1. Build sdist and wheel in build isolation from a clean checkout.
2. Unpack the sdist outside the checkout and rebuild its wheel independently.
3. Inspect metadata and required resources in both distributions.
4. Install the wheel normally with dependencies; never use --no-deps to hide
   resolver problems. Run pip check.
5. Clear PYTHONPATH, change to an unrelated directory, and assert module paths
   resolve inside the fresh environment. Run public quickstart and scoped LCIA.
6. Repeat with the sdist-built wheel, every optional capability, and all five
   vehicle-family packages installed together in one resolver transaction.
7. Test minimal supported dependency combinations, current compatible resolved
   versions, and a locked known-good environment. Make minimum constraints
   mutually installable rather than mechanically pinning inconsistent old versions.
8. Run one upgrade test from the previous supported family release and one
   repeated-install/uninstall scenario to catch stale/missing resources.
9. Install built conda artifacts into clean environments and run more than import
   tests: one model plus LCIA/resource check. Report conda separately from pip.

Installed-artifact tests must not silently import the checkout. pytest's import
mode/layout guidance supports this distinction. A later src-layout migration is
optional and should be isolated from packaging repairs. [pytest guidance](https://docs.pytest.org/en/stable/explanation/goodpractices.html).

Acceptance: documented install commands work on the advertised matrix without
manual dependency repair; wheel and sdist model results agree within declared
tolerances; the minimal installation does not accidentally contain export extras.

## 7. Stage D — make numerical and public contracts explicit

### D1. Validate boundaries

Create small typed configuration/validation components for model scope, overrides,
energy storage, fuel blends, background configuration and functional units. Prefer
simple data structures initially; introducing a large validation framework is not
a prerequisite.

- Validate labels, required dimensions, unique coordinates, coordinate coverage,
  finite values, and compatible shapes before expensive calculation.
- Check applicable units/ranges: positive density and lifetime, nonnegative masses,
  fractions in [0,1], normalized blends, valid year intervals, positive occupancy
  for pkm and positive payload for tkm.
- Distinguish omitted, None, zero, empty, unavailable and invalid. Replace `x or
  default` where it discards valid explicit zero/empty settings.
- Specify interpolation/extrapolation policy per input group. Warn or reject
  unsupported extrapolation deliberately instead of silently extrapolating all data.
- Replace assert-based user validation with explicit exceptions; Python -O must
  not disable validation. Replace bare except with narrow handling and context.
- Define errors such as InputValidationError, ConvergenceError, DataCompatibilityError
  and MissingOptionalDependencyError. Preserve ValueError compatibility where useful.

### D2. Array and state safety

- Use named selection/transposition at interfaces. Restrict .values to documented
  numerical kernels with explicit axis order and shape assertions.
- Audit np.resize and positional broadcasting, especially load factors and sample
  dimensions: resizing can repeat data rather than align coordinates.
- Define a canonical array order internally but accept supported reordered input
  dimensions through explicit normalization. Reject ambiguous mixed vehicle scopes.
- Copy caller-owned scope, overrides and input arrays by default, or offer an
  explicitly documented opt-in in-place mode where performance justifies it.
- Store raw inputs separately from calculated state. Target deterministic repeated
  set_all() from the same inputs; until implemented, explicitly reject unsupported
  reruns rather than silently applying markup or replacements twice.
- Make context-manager selections restore state even after exceptions; test nested
  scopes or reject them explicitly. Avoid a single overwritten shared cache.
- Represent vehicle availability/compliance explicitly and carry masks into results.
  Do not use zero TtW energy as the sole signal for every unsupported vehicle.
- Never blindly convert NaN/Inf in valid vehicles to zero or maximum floats.
  Apply scientifically justified masking only to known unavailable cells and
  report the reason. Negative credits/characterized impacts can be legitimate:
  validate parameter-specific rules rather than banning all negative outputs.

### D3. Convergence and numerical precision

- Introduce a shared iteration controller with max iterations, absolute plus
  relative tolerances, finite checks, and oscillation/non-convergence diagnostics.
- Measure convergence per active vehicle/sample, not only the sum across a grid:
  increases and decreases in different vehicles must not cancel.
- Cover zero denominators, decreasing mass, near-zero payload and infeasible ranges.
  Do not return partially converged values as a successful scientific result.
- Audit float32 versus float64 on representative mass/energy/LCIA kernels. Use
  float64 where error analysis supports it; benchmark memory before a blanket change.
- Check sparse solver warnings, finite solutions and residuals against small
  analytically solvable inventories. Preserve documented A sign conventions.
- Stabilize logarithm/exponential operations where necessary, including noise
  summation, without clipping away evidence of implausible inputs.

### D4. Sampling and reproducibility

- Accept an explicit seed or NumPy Generator and propagate it through parameter
  sampling and cost uncertainty; inspect klausen behavior and bridge it explicitly.
- Ensure scientific sampling does not modify global RNG state or depend on which
  unrelated model ran first. Preserve intended correlations between parameters.
- Sensitivity output must retain reference and named perturbation coordinates;
  stochastic output must retain sample identity through model, inventory and export.
- Record seed, sample count, method/scenario, package versions and data versions
  in result metadata. Promise numerical tolerance reproducibility across platforms,
  not universal bit-for-bit floating-point equality.

Acceptance: repeated runs, reordered coordinates, cross-model execution order and
functional-unit conversions obey documented invariants; invalid states are visible.

## 8. Stage E — simplify code without obscuring scientific behavior

- Retain thin vehicle subclasses for vehicle-specific equations and assumptions.
  Extract common tested helpers for amortization, replacements, battery selection,
  override application, convergence, and cost aggregation only after documenting
  real differences. Truck residual credit and bus charging schedules stay explicit.
- Split large orchestration methods into named stages with clear input/output
  contracts. Keep the public constructors and set_all() facade during migration.
- Introduce types at public boundaries and data loaders first; static checking
  cannot validate xarray coordinates, so retain runtime contract checks.
- Keep Black/isort initially and add focused lint rules for undefined names,
  accidental shadowing, unused imports and risky exception handling. Separate
  broad mechanical cleanup from any numerical change.
- Replace unconditional prints/PrettyTable side effects with logging and optional
  progress/report callbacks. Library calls should work quietly in notebooks,
  batch pipelines and APIs; preserve optional human-readable diagnostics.
- Audit import-time effects, warning filters, file handles and mutable caches.
  Use context managers and cache immutable resources with data-version-aware keys.
- Profile fixed representative workloads. Track runtime and peak memory before
  caching or vectorization changes; assert scientific outputs remain equivalent.
- Document all remaining intentional duplication before attempting a generic
  framework. Do not add abstraction just to make model files look alike.

Acceptance: unchanged corrected numerical baselines, clear public annotations,
no new lint/typing debt in touched boundaries, and no unexplained performance loss.

## 9. Scientific data and test strategy

### Data validation and provenance

Validate every shipped parameter/resource schema: units, uncertainty bounds,
unique parameter/size/powertrain/year assignments, required versus derived values,
chemistry availability, referenced labels and category mappings. Reject conflicting
records rather than silently keeping the first duplicate.

For matrices, validate activity/category indices, shapes, supported scenario/year
coverage and finite entries. Store source/database/method versions, transformation
script revision, checksums and known limitations. Do not ship licensed source data
merely to make tests work; synthetic fixtures cover solver mechanics, while
permitted packaged factors cover integration.

Keep scientific updates separate: old/new result tables, contributions explaining
the differences, and expert assessment where physical assumptions change.
A larger tolerance is not an acceptable substitute for an explained change.

### Required kinds of tests

| Layer | Examples | What a pass establishes |
| --- | --- | --- |
| Unit | Loader validation, amortization including zero interest, safe math, single override | Local equation/branch behavior |
| Contract | Array dimensions, nonmutation, inherited hooks, result schema | Repositories remain interoperable |
| Property/invariant | Battery mass balance, normalized blends, reversible unit conversions, reorder invariance | General relationships across generated valid inputs |
| Numerical regression | Energy, component mass, purchase/per-km costs, category and contribution totals | Corrected reference cases remain stable |
| Analytical inventory | Tiny A/B with known solution; sample-specific loads | Solver, signs, characterization and normalization are correct |
| Integration | Four vehicle types × chosen backgrounds; multi-year/multi-sample workflows | Real components work together |
| Export | Every promised format/version, all years, normalized quantities, repeated use | Export completeness and absence of state corruption |
| Consumer | API input/result mapping, worker lifecycle, localization | User-facing behavior remains correct |
| Installation | Actual wheels/sdists/extras/conda in clean environments | Release artifacts are complete and usable |

Test scaling only under controlled assumptions: for a fixed vehicle/inventory,
doubling the demand doubles results; doubling load halves per-load impacts when
vehicle operation is held fixed. It is not a universal claim after re-sizing.
Check that contribution sums reconstruct totals and that PHEV utility-factor
boundaries reproduce the correct component modes where the formulation applies.

Measure branch coverage first. Initial proposed targets: >=90% on newly extracted
validation/numerical helpers and >=80% changed-line coverage, with a ratchet on
whole-project coverage. These are review aids, not substitutes for physical tests.
Use targeted mutation checks on a few critical formulas to confirm tests catch
sign, factor-of-1000 and normalization errors before expanding this technique.

## 10. Stage F — make consumers resilient

### flaskCarculator

- Test all four vehicle types through the local Flask test client, not only
  validation failures. Cover plain nomenclature, TCS and applicable SwissCargo cases.
- Normalize external naming and units once, including two-wheeler identifiers,
  PHEV consumption/utility factors, and kg-to-g conversion.
- Treat each request/model independently; validate no mutable state leaks across
  vehicles, requests or exceptions. Apply explicit body, fleet-size, model-grid
  and computation limits appropriate to service capacity.
- Separate malformed input, unsupported combinations and computation failures
  into stable HTTP errors; emit finite JSON and useful request identifiers.
- Retain independent BAFU/ecoinvent results and provenance. Verify BAFU replacement
  cannot contaminate the original inventory or subsequent requests.
- Maintain explicit adapters for cost/result schemas while preserving older
  response shapes during a documented deprecation period.
- Lock application dependencies to a qualified release set and run comparison
  payloads before replacing the existing TCS commit pins.
- Qualify main's additional functionality separately with its external services
  stubbed in ordinary CI and explicitly configured for integration testing.

### carculator_online

- Introduce a configurable application factory and injectable calculation/service
  dependencies so importing calculation logic does not require production services.
- Create local Redis/database integration fixtures. Test queued/running/completed/
  failed/expired jobs, progress monotonicity, duplicate submissions and unavailable
  workers. Return useful errors when the 120-second result TTL expires.
- Avoid sharing mutable Calculation/model state across requests/jobs. Use one
  isolated calculation context per job.
- Snapshot representative translated payloads and result contracts for supported
  locales. Keep backend impact labels, JavaScript category mappings and exports aligned.
- Test selected browser flows against a local deployment: submit, poll, compare,
  download and recover from a failed/expired job. Do not use production endpoints
  or send support email during tests.
- Derive displayed versions from runtime metadata; remove stale hard-coded labels.
  Make DB migration and deployment separate explicit operations with integration tests.

Acceptance: local end-to-end smoke checks and numerical comparisons pass against
the same candidate package-family manifest; no production service is needed in CI.

## 11. Stage G — CI and release gates

### Required CI layers

| Trigger | Required jobs |
| --- | --- |
| Every PR | Formatting/lint, focused types, unit/contract tests, resource validation, small numerical cases, one installed-wheel smoke test |
| utils changes | Above plus all four downstream model contract suites using exact candidate artifacts |
| Dependency/packaging changes | Clean resolver matrix, wheel/sdist equivalence, extras combinations, all-family installation, pip check |
| Scheduled compatibility run | Broader Python/platform/dependency matrix, full grids, export integrations and upstream deprecations |
| Release candidate | Full supported matrix, application smoke tests, complete numerical diff/provenance report, conda qualification if advertised |

Start with an achievable PR runtime target of about ten minutes on a specified CI
runner, then measure and adjust. Keep full-grid/performance jobs separate; a timeout
must not turn a still-running test into an assumed pass.

Remove CI auto-format-and-push behavior. PR checks should report differences and
never publish packages. Build artifacts once, retain checksums, and publish those
same tested artifacts through release-only jobs. Prefer trusted publishing over
long-lived PyPI credentials; GitHub documents the OIDC workflow.
[GitHub PyPI publishing guidance](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-pypi).

For cross-repository changes, build all candidate wheels into one wheelhouse and
install the intended set together. Test utils against released downstream packages
and proposed downstream changes when a compatibility migration needs both.
Publish utils first, verify it from the package index, then dependent vehicle
releases, then application locks. Exact released versions must be mutually
resolvable; unbounded installed branch tips are not a release manifest.

### Release acceptance checklist

- All confirmed defects repaired with regression tests; no unexplained failure,
  skipped promised capability, or unexpected numerical warning in reference cases.
- All four vehicle families have meaningful physical/numerical assertions.
- Inputs remain unchanged; repeated model/export operations obey the chosen contract.
- Finite-result and convergence rules distinguish invalid from unavailable vehicles.
- Wheel, sdist-built wheel and advertised conda packages install in clean supported
  environments with their resources and declared dependencies.
- Optional-dependency absence is tested; requested optional features work when installed.
- Every supported Python/platform cell passes or is removed from advertised support.
- Versions, dependency bounds, data provenance, docs examples and result schemas agree.
- API and website smoke tests use the exact release candidate family.
- Release notes explain numerical changes and installation/API migrations.
- Previous application lockfiles and artifact identifiers are retained for rollback;
  revert a deployment through a known-good dependency set rather than overwriting tags.

## 12. Suggested implementation backlog

These are reviewable work packages; split further when a numerical change becomes
hard to assess. Each package must include relevant tests and documentation.

| Order | Work package | Primary repositories | Dependencies |
| --- | --- | --- | --- |
| 01 | Test isolation, reproducible baselines and compatibility manifest | All core repos | None |
| 02 | Battery-property/fallback contract and bus override preservation | utils, bus, two-wheeler | 01 |
| 03 | Custom parameter/extra forwarding and loader validation | bus, truck, two-wheeler, utils | 01 |
| 04 | Correct sensitivity coordinates and perturbation semantics | utils, all vehicles | 01 |
| 05 | Export nonmutation and functional-unit/sample scaling | utils | 01 |
| 06 | Noise overflow reproduction and finite-result policy | utils, all vehicles | 01–02 |
| 07 | Packaging metadata/version consistency and artifact CI | Core repos | 01; can proceed alongside 02–06 |
| 08 | Optional export dependencies and installed resource access | utils, vehicle packages, API | 07 |
| 09 | Explicit validation, named array alignment and override precedence | utils, all vehicles | 02–04 |
| 10 | Bounded per-vehicle convergence and safe model lifecycle | utils, all vehicles | 09 |
| 11 | Seeded sampling, analytical inventory tests and numerical provenance | utils, all vehicles | 04, 09–10 |
| 12 | Targeted helper extraction, logging, typing and performance baseline | Core repos | 09–11 |
| 13 | API target-range fix, all-mode requests and schema adapters | flaskCarculator | 01–05; small defect fix can ship earlier |
| 14 | Website factory, worker/error/localization/download tests | carculator_online | 07–11 |
| 15 | Cross-platform/extras/conda matrix and coordinated release automation | All | 07–14 |
| 16 | Candidate release, migration notes and verified application locks | All | 15 |
| Follow-up | NumPy 2, modern Brightway, newer Python qualification | utils then all consumers | Stabilized release |

Start with packages 01–03 and the packaging prototype in 07. They address the
highest-confidence failures while creating the evidence needed for the larger
numerical and installation changes. Reassess scope after the first clean artifact
matrix; dependency incompatibilities may change the modernization effort.
