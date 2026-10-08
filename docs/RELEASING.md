# Publishing releases

Publishing a GitHub release for a tag such as `v.1.9.6` triggers
`.github/workflows/main.yml`. Tags `v1.9.6` are also supported. The tag version
must match both `carculator/_version.py` and `conda/meta.yaml`.

The workflow verifies installed wheels and source distributions on Linux,
macOS, and Windows with Python 3.12 before publishing. PyPI receives the exact
carculator wheel and source distribution verified on Linux. A separate job
builds and tests the noarch conda package, then uploads it to the `romainsacchi`
Anaconda channel. Publishing uses the existing repository secrets `PYPI_TOKEN`
and `ANACONDA_CLOUD`. Ordinary pushes and pull requests only verify artifacts.

Publish the required `carculator_utils` version to the target registries first.
Verification installs the sibling checkout, so passing verification does not
establish that the dependency is available to registry users. Carculator 1.9.6
requires `carculator_utils>=1.3.6`.

For an existing release, after this workflow is on the default branch, open
**Actions → Installed artifacts and release publishing → Run workflow** on that
branch and set `release_tag` to `v.1.9.6`. This checks out the existing tag,
verifies it again, and publishes it without moving or recreating the tag.
Leaving `release_tag` empty only runs verification. Both uploads skip existing
files, allowing a rerun after one registry succeeded and the other failed.

Creating a tag alone does not publish; publish its GitHub release to trigger
automatic publication. Publication runs are not cancelled by later CI pushes.
