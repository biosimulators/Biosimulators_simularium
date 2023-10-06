import termcolor
from warnings import warn as _warn
from biosimulators_simularium.config import Colors


__all__ = ['BioSimulatorsWarning', 'warn']


class BioSimulatorsWarning(UserWarning):
    """ Base class for simulator warnings """
    pass  # pragma: no cover


def warn(message, category):
    """ Issue a warning in a color

    Args:
        message (:obj:`str`): message
        category (:obj:`type`): category
    """
    _warn(termcolor.colored(message, Colors.warning.value), category)
