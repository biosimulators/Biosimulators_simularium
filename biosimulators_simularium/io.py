import os
import zipfile
from typing import Union, List
from simulariumio import TrajectoryData, BinaryWriter, JsonWriter
from simulariumio.smoldyn.smoldyn_data import SmoldynData


def get_archive_files(archive_rootpath: str) -> List[str]:
    """Return a list of absolute paths for all files whose parent is `archive_rootpath`."""
    return [os.path.join(archive_rootpath, f) for f in os.listdir(archive_rootpath)]


def get_smoldyn_model_filepath(archive_rootpath: str) -> str:
    files = get_archive_files(archive_rootpath)
    for f in files:
        if 'model.txt' in f:
            return f


def zip_archive(archive_rootpath: str, archive_filename: str) -> None:
    """Pack/Bundle a list of files derived from `rootpath` into a zip archive saved at `archive_filepath`.
    """
    archive_files = get_archive_files(archive_rootpath)
    with zipfile.ZipFile(archive_filename, mode='w') as zip_file:
        for file in archive_files:
            zip_file.write(file, arcname=archive_rootpath)


def unzip_and_read_archive(archive_filepath: str, out_dir: str) -> List[str]:
    """ Read the archive FILE found at `archive_filepath` and unpack into `out_dir`.

    Args:
        archive_filepath (:obj:`str`): path to zip file you want to unpack.
        out_dir (:obj:`str`, optional): path to unpack files.

    Returns:
        `List[str]`: a list of the absolute paths for each file in the archive.
    """
    with zipfile.ZipFile(archive_filepath, mode='r') as zip_file:
        zip_file.extractall(out_dir)
        archive_files = get_archive_files(out_dir)
    return archive_files


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


