# Releasing carculator 1.9.6

Status: prepared, not published. Use Python 3.12 and review the matching family set:

| Package | Prepared version |
| --- | --- |
| `carculator_utils` | 1.3.6 |
| `carculator` | 1.9.6 |
| `carculator_truck` | 0.5.1 |
| `carculator_bus` | 0.1.1 |
| `carculator_two_wheeler` | 0.1.1 |


1. Review `CHANGELOG.md`, known limitations in `docs/validity.rst`, and the worktree.
   Preserve local notebooks and inventories; commit only the intended release files.
2. Check `carculator/_version.py`, `conda/meta.yaml` and dependency metadata together.
   Sphinx reads the package version automatically. All vehicle packages require
   `carculator_utils>=1.3.6`, including the optional export extras.
3. Build and verify actual artifacts from this checkout (use a new output directory):

```bash
python ../carculator_utils/scripts/verify_installation.py --repositories ../carculator_utils . --output /tmp/carculator-release-check --run-tests
```

For the complete family, run from `carculator_utils`:

```bash
python scripts/verify_installation.py \
  --repositories . ../carculator ../carculator_truck ../carculator_bus ../carculator_two_wheeler \
  --output /tmp/carculator-family-release-check --run-tests
```

The verifier builds wheels and sdists, rebuilds wheels from sdists, compares
packaged resource hashes, runs installed tests with export extras and checks
offline core-only model/LCIA runs. Keep `report.json`, test XML, dependency freezes
and artifact hashes with the release record. A local pass does not establish
that Linux, Windows or hosted CI passed. Confirm the release commit's CI separately.

4. Install `.[docs]`, build with `python -m sphinx -b html docs docs/_build/html`,
   and run the README example. Check wheel/sdist metadata before publication:

```bash
python -m pip install twine
python -m twine check --strict /tmp/carculator-family-release-check/wheels/carculator-1.9.6-py3-none-any.whl /tmp/carculator-family-release-check/wheels/carculator-1.9.6.tar.gz
```

5. Publish `carculator_utils` **first** and confirm that 1.3.6 is available before
   publishing the four vehicle packages. The same ordering applies to conda.
   Replace `Unreleased` with the actual publication date in the changelog, commit
   the final release metadata, and verify the final artifacts. Create an annotated
   `v.1.9.6` tag on that reviewed commit, following existing tag conventions.
   Do not reuse an existing tag or upload a different build under the same version.
6. Upload the exact verified wheel and sdist through the maintainer's configured
   PyPI credentials/trusted publishing process, create the GitHub release from the
   changelog entry, and attach the verification record. These are publication
   steps, not actions performed by the verification command.
7. Build the matching conda recipe with the required dependencies available and
   test it separately. Wheel verification does not certify a conda build.

The prepared metadata and README examples target this release; older published
packages may not provide the documented APIs or 2025 defaults.
