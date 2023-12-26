import os
from typing import Union
from simulariumio import TrajectoryData, BinaryWriter, JsonWriter
from simulariumio.smoldyn.smoldyn_data import SmoldynData


def write_simularium_file(
    data: Union[SmoldynData, TrajectoryData],
    simularium_filename: str,
    json: bool = False,
    validate: bool = True
) -> None:
    """Takes in either a `SmoldynData` or `TrajectoryData` instance and saves a simularium file based on it
        with the name of `simularium_filename`.

        Args:
            data(:obj:`Union[SmoldynData, TrajectoryData]`): data object to save.
            simularium_filename(:obj:`str`): `Optional`: name by which to save the new simularium file. If None is
                passed, will default to `self.archive.rootpath/self.archive.simularium_filename`.
            json(:obj:`bool`): exports simularium file in JSON format if true; exports in binary if false. Defaults
                to `False` for optimization's sake.
            validate(:obj:`bool`): whether to call the wrapped method using `validate_ids=True`. Defaults
                to `True`.
    """
    if not os.path.exists(simularium_filename):
        if json:
            writer = JsonWriter()
        else:
            writer = BinaryWriter()
        return writer.save(trajectory_data=data, output_path=simularium_filename, validate_ids=validate)
