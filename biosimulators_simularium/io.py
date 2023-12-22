import os
from typing import Union
from simulariumio import TrajectoryData, BinaryWriter, JsonWriter
from simulariumio.smoldyn.smoldyn_data import SmoldynData


def write_simularium_file(
    data: Union[SmoldynData, TrajectoryData],
    simularium_filename: str,
    save_format: str,
    validation=True
) -> None:
    """Takes in either a `SmoldynData` or `TrajectoryData` instance and saves a simularium file based on it
        with the name of `simularium_filename`. If none is passed, the file will be saved in `self.archive.rootpath`
        Args:
            data(:obj:`Union[SmoldynData, TrajectoryData]`): data object to save.
            simularium_filename(:obj:`str`): `Optional`: name by which to save the new simularium file. If None is
                passed, will default to `self.archive.rootpath/self.archive.simularium_filename`.
            save_format(:obj:`str`): format which to write the `data`. Options include `json, binary`.
            validation(:obj:`bool`): whether to call the wrapped method using `validate_ids=True`. Defaults
                to `True`.
    """
    save_format = save_format.lower()
    if not os.path.exists(simularium_filename):
        if 'binary' in save_format:
            writer = BinaryWriter()
        elif 'json' in save_format:
            writer = JsonWriter()
        else:
            raise TypeError('You must provide a valid writer object.')
        return writer.save(trajectory_data=data, output_path=simularium_filename, validate_ids=validation)
