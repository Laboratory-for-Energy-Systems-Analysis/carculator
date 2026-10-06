"""Run the family installation verifier from the sibling utils checkout."""

import runpy
from pathlib import Path

if __name__ == "__main__":
    harness = (
        Path(__file__).resolve().parents[2]
        / "carculator_utils"
        / "scripts"
        / "verify_installation.py"
    )
    if not harness.is_file():
        raise SystemExit(
            "Checkout the matching carculator_utils revision beside carculator first."
        )
    runpy.run_path(str(harness), run_name="__main__")
