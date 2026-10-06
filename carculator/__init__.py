"""

Submodules
==========

.. autosummary::
    :toctree: _autosummary


"""

__all__ = (
    "CarInputParameters",
    "fill_xarray_from_input_parameters",
    "CarModel",
    "InventoryCar",
    "get_standard_driving_cycle_and_gradient",
)
from pathlib import Path

from ._version import __version__

DATA_DIR = Path(__file__).resolve().parent / "data"

from carculator_utils.array import fill_xarray_from_input_parameters
from carculator_utils.driving_cycles import get_standard_driving_cycle_and_gradient

from .car_input_parameters import CarInputParameters
from .inventory import InventoryCar
from .model import CarModel
