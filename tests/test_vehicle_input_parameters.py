import json
from pathlib import Path

import carculator.car_input_parameters as vip

DEFAULT = Path(__file__).parent / "fixtures" / "default_test.json"
EXTRA = Path(__file__).parent / "fixtures" / "extra_test.json"


def assert_custom_parameter_schema(inputs, records, extra):
    provided = {record["name"] for record in records.values()}
    expected = {
        record["name"]
        for record in json.loads(vip.CarInputParameters.DEFAULT.read_text()).values()
    }
    assert len(inputs.powertrains) == 5
    assert set(inputs.input_parameters) == provided
    # Missing native inputs remain visible for the pre-sizing coverage check;
    # loading a small custom fixture must not silently erase those requirements.
    assert set(inputs.parameters) == provided | expected | set(extra)


def test_can_pass_directly():
    records = json.loads(DEFAULT.read_text())
    extra = set(json.loads(EXTRA.read_text())) - {"foobazzle"}
    assert_custom_parameter_schema(
        vip.CarInputParameters(records, extra), records, extra
    )


def test_alternate_filepath():
    assert_custom_parameter_schema(
        vip.CarInputParameters(DEFAULT, EXTRA),
        json.loads(DEFAULT.read_text()),
        json.loads(EXTRA.read_text()),
    )
