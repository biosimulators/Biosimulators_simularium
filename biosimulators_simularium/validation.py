from typing import *
from smoldyn.biosimulators.combine import validate_variables
from biosimulators_utils.sedml.data_model import Variable


def validate_spatial(variables: List[Variable]) -> Dict[Tuple, Tuple]:
    """Validate a list of `Variable` objects whose simulation's output data is spatial in nature, i.e: `listmols`.
        Wrapper of `smoldyn.biosimulators.combine.validate_variables()` which handles inevitable errors and
        continues.

        Args:
            variables:`List[Variable]`: A list of Variables derived from the Smoldyn simulation.

        Returns:
            :obj:`Dict[Tuple, Tuple]`: dictionary that maps variable targets and symbols to Smoldyn output commands
    """

