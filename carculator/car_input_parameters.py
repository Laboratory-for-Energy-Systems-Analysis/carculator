"""
car_input_parameters.py contains the VehicleInputParameters class, which, after instantiated, contains
all definitions (metadata) of input and calculated parameters, along with their values.
Also, it inherits methods from `klausen`, which exposes the methods .static() and .stochastic(),
which generate single or random values for input parameters.
"""

from pathlib import Path
from typing import Union

from carculator_utils.vehicle_input_parameters import VehicleInputParameters


class CarInputParameters(VehicleInputParameters):
    """ """

    DEFAULT = Path(__file__, "..").resolve() / "data" / "default_parameters.json"
    EXTRA = Path(__file__, "..").resolve() / "data" / "extra_parameters.json"

    def __init__(
        self,
        parameters: Union[str, Path, list] = None,
        extra: Union[str, Path, list] = None,
    ) -> None:
        """Create a `klausen <https://github.com/cmutel/klausen>`__ model with the car input parameters."""
        super().__init__(parameters, extra)
