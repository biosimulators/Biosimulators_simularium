import os
import re
import zipfile
from typing import Union, List
import pyvista as pv
from vtk import vtkPolyDataWriter, vtkPolyDataReader, vtkPolyData
from simulariumio import TrajectoryData, BinaryWriter, JsonWriter
from simulariumio.smoldyn.smoldyn_data import SmoldynData


__all__ = [
    'get_modelout_fp',
    'get_model_fp',
    'write_simularium_file',
    'normalize_modelout_path_in_root'
]




def get_fp(working_dir: str, identifier: str) -> Union[str, List[str]]:
    """Search a working_dir for a file of a specified identifier."""
    id_files = []
    for f in os.listdir(working_dir):
        fp = os.path.join(working_dir, f)
        if identifier in fp:
            id_files.append(fp)
    if len(id_files) > 1:
        return id_files
    else:
        return id_files[0]


def get_model_fp(working_dir: str):
    return os.path.join(working_dir, 'model.txt')


def get_modelout_fp(working_dir: str):
    return os.path.join(working_dir, 'modelout.txt')


def model_fp(working_dir: str) -> str:
    return get_fp(working_dir=working_dir, identifier='model.txt')


def modelout_fp(working_dir: str) -> str:
    return get_fp(working_dir=working_dir, identifier='modelout.txt')


def get_archive_files(archive_rootpath: str) -> List[str]:
    """Return a list of absolute paths for all files whose parent is `archive_rootpath`."""
    return [os.path.join(archive_rootpath, f) for f in os.listdir(archive_rootpath)]


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
            simularium_filename(:obj:`str`): name by which to save the new simularium file.
            json(:obj:`bool`): exports simularium file in JSON format if true; exports in binary if false. Defaults
                to `False` for optimization's sake.
            validate(:obj:`bool`): whether to call the wrapped method using `validate_ids=True`. Defaults
                to `True`.
    """
    if json:
        writer = JsonWriter()
    else:
        writer = BinaryWriter()
    return writer.save(trajectory_data=data, output_path=simularium_filename, validate_ids=validate)


def write_vtk_file(fp: str, data):
    """Write the append filter output to file"""
    # Write the combined data to a file
    writer = vtkPolyDataWriter()
    writer.SetFileName(fp)
    writer.SetInputData(data)
    return writer.Write()


def read_vtk_file(fp: str) -> vtkPolyData:
    """Read vtk and return read-in polydata object"""
    reader = vtkPolyDataReader()
    reader.SetFileName(fp)
    reader.Update()
    return reader.GetOutput()


def write_vtp_file(mesh: pv.PolyData, **kwargs):
    """write a vtp file to `save_path` based on the `mesh`. Kwargs according to `pv.PolyData().save()` args.

        Keyword Args:
            filename:`str`: path in which to save the vtp file.
            binary: bool = True,
            texture: Any = None,
            recompute_normals: Any
    """
    return mesh.save(kwargs['filename'])


def read_vtp_file(fp: str):
    """Return an object instance from Pyvista configured by the `fp` in vtp format."""
    return pv.get_reader(fp).read()


def read_smoldyn_simulation_configuration(filename: str) -> List[str]:
    ''' Read a configuration for a Smoldyn simulation

    Args:
        filename (:obj:`str`): path to model file

    Returns:
        :obj:`list` of :obj:`str`: simulation configuration
    '''
    with open(filename, 'r') as file:
        return [line.strip('\n') for line in file]


def write_smoldyn_simulation_configuration(configuration: List[str], filename: str):
    ''' Write a configuration for Smoldyn simulation to a file

    Args:
        configuration
        filename (:obj:`str`): path to save configuration
    '''
    with open(filename, 'w') as file:
        for line in configuration:
            file.write(line)
            file.write('\n')


def disable_smoldyn_graphics_in_simulation_configuration(configuration: List[str]):
    ''' Turn off graphics in the configuration of a Smoldyn simulation

    Args:
        configuration (:obj:`list` of :obj:`str`): simulation configuration
    '''
    for i_line, line in enumerate(configuration):
        if line.startswith('graphics '):
            configuration[i_line] = re.sub(r'^graphics +[a-z_]+', 'graphics none', line)


def standardize_model_output_fn(working_dirpath: str):
    """Read in the root of a directory for a file containing the word 'out' and rename
        it to reflect a standard name.

        working_dirpath(`str`): path of the directory root relative to where the output file is.
    """
    for root, _, files in os.walk(working_dirpath):
        for f in files:
            if 'out' in f[-7:]:
                extension = f[-4:]
                new_prefix = 'modelout'
                fp = os.path.join(root, new_prefix + extension)
                os.rename(os.path.join(root, f), fp)


def normalize_modelout_path_in_root(root_fp):
    for root, dirs, files in os.walk(root_fp):
        for filename in files:
            print(filename)
            if filename.endswith('out.txt'):
                original_path = os.path.join(root, filename)
                new_path = os.path.join(root, 'modelout.txt')
                os.rename(original_path, new_path)
