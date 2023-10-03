"""Utility functions related to `biosimulators_simularium.converters`."""


import os
import tempfile
from typing import Tuple, List, Set
import numpy as np
from smoldyn import Simulation as smoldynSim
from smoldyn.biosimulators.combine import (  # noqa: E402
    read_smoldyn_simulation_configuration,
    disable_smoldyn_graphics_in_simulation_configuration,
    write_smoldyn_simulation_configuration,
    init_smoldyn_simulation_from_configuration_file,
)
from biosimulators_simularium.archives.data_model import SpatialCombineArchive, ModelValidation, SmoldynCombineArchive


__all__ = [
    'validate_model',
    'generate_model_validation_object'
]


def validate_model(filename, name=None, config=None) -> Tuple[List[List[str]], List, Tuple[smoldynSim, List[str]]]:
    """ Check that a model is valid. This method and documentation for this method has been copied directly from
        `biosimulators_utils.model_lang.smoldyn.validation`.

    Args:
        filename (:obj:`str`): path to model
        name (:obj:`str`, optional): name of model for use in error messages
        config (:obj:`Config`, optional): whether to fail on missing includes

    Returns:
        :obj:`tuple`:

            * nested :obj:`list` of :obj:`str`: nested list of errors (e.g., required ids missing or ids not unique)
            * nested :obj:`list` of :obj:`str`: nested list of errors (e.g., required ids missing or ids not unique)
            * :obj:`tuple`:

                * :obj:`smoldyn.Simulation`: model configuration
                * :obj:`list` of :obj:`str`: model configuration
    """
    errors = []
    warnings = []
    model = None
    config = None

    if filename:
        if os.path.isfile(filename):
            config = read_smoldyn_simulation_configuration(filename)
            disable_smoldyn_graphics_in_simulation_configuration(config)
            fid, config_filename = tempfile.mkstemp(suffix='.txt', dir=os.path.dirname(filename))
            os.close(fid)
            write_smoldyn_simulation_configuration(config, config_filename)
            try:
                model = init_smoldyn_simulation_from_configuration_file(config_filename)
                valid = True
            except ValueError:
                valid = False
            if not valid:
                errors.append(['`{}` is not a valid Smoldyn configuration file.'.format(filename)])
            os.remove(config_filename)

        else:
            errors.append(['`{}` is not a file.'.format(filename or '')])

    else:
        errors.append(['`filename` must be a path to a file, not `{}`.'.format(filename or '')])

    return (errors, warnings, (model, config))


def generate_model_validation_object(archive: SpatialCombineArchive) -> ModelValidation:
    """ Generate an instance of `ModelValidation` based on the output of `archive.model_path`
            with above `validate_model` method.

    Args:
        archive: (:obj:`SpatialCombineArchive`): Instance of `SpatialCombineArchive` to generate model validation on.

    Returns:
        :obj:`ModelValidation`
    """
    validation_info = validate_model(archive.model_path)
    validation = ModelValidation(validation_info)
    return validation


def verify_simularium_in_archive(archive: SpatialCombineArchive) -> bool:
    return '.simularium' in list(archive.paths.keys())


def verify_simularium_in_smoldyn_archive(archive_rootpath: str) -> bool:
    """ Returns whether there exists the presence of a simularium file in a given smoldyn archive's rootpath.

        Args:
            archive_rootpath(:obj:`str`): path of the root relative to your COMBINE/OMEX archive.

        Returns:
            `bool`: The presence of a `.simularium` file in the archive's dir.
    """
    archive = SmoldynCombineArchive(rootpath=archive_rootpath)
    return verify_simularium_in_archive(archive)


def extract_simulation_from_validation(model_fp: str) -> smoldynSim:
    validation = validate_model(model_fp)
    return validation[2][0]


def extract_config_from_validation(model_fp: str) -> List[str]:
    validation = validate_model(model_fp)
    return validation[2][1]


def get_n_agents(model_fp: str):
    config = extract_config_from_validation(model_fp)
    numbers = []
    for line in config:
        if is_digit(line):
            numbers.append(line)
    return numbers


def calculate_n_steps(time_stop, time_start, time_step) -> int:
    return int((time_stop - time_start) / time_step)


def calculate_total_steps_from_model(model_fp: str):
    details = {}
    model_config = extract_config_from_validation(model_fp)
    for line in model_config:
        if 'TIME_STOP' in line:
            details['time_stop'] = line
    return


def calculate_times(timestep: int, total_steps: int) -> np.ndarray:
    return timestep * np.array(list(range(total_steps)))


def read_lines(modelout_fp: str):
    with open(modelout_fp, 'r') as fp:
        return fp.readlines()


def extract_unique_colnames_from_modelout(modelout_fp: str):
    type_names = []
    lines = read_lines(modelout_fp)
    for line in lines:
        parts = line.split()
        type_names.append(parts[0])
    return list(set(type_names))


def is_digit(item):
    return item.replace('.', '', 1).isdigit()


def extract_timestamps(modelout_fp: str):
    names = extract_unique_colnames_from_modelout(modelout_fp)
    return np.array(sorted([float(item) for item in names if is_digit(item)]))


def extract_agent_type_names(modelout_fp: str) -> List[str]:
    names = extract_unique_colnames_from_modelout(modelout_fp)
    return [item for item in names if not is_digit(item)]


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


def get_modelout_fp(working_dir):
    for f in os.listdir(working_dir):
        fp = os.path.join(working_dir, f)
        if 'out' in fp:
            return fp


def generate_formatted_typename_list(model_filepath: str, num_steps: int):
    formatted_types = []
    type_names = extract_agent_type_names(model_filepath)
    for t in range(num_steps):
        formatted_types.append(type_names)
    return formatted_types


def get_mol_data(modelout_fp: str):
    mol_data = []
    lines = read_lines(modelout_fp)
    for line in lines:
        line = line.split()
        if len(line) > 2:
            end = len(line) + 1
            start = 1
            mapped_floats = list(map(float, line[start:end]))
            mol_data.append(mapped_floats)
    return mol_data


def extract_coordinates(mol_data: List[float]) -> np.ndarray:
    coordinates = []
    for datum in mol_data:
        triple = np.array(datum[0:len(datum) - 1])
        coordinates.append(triple)
    return np.array(coordinates)


def __parse_modelout_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    all_data = []
    current_timestep_data = []
    for line in lines:
        parts = line.split()
        # If the line has 2 elements, it's a timestep indicator
        if len(parts) == 2:
            # If there's data in the current timestep, save it
            if current_timestep_data:
                all_data.append(current_timestep_data)
                print(f"Timestep data length: {len(current_timestep_data)}")  # Let's inspect the length
                current_timestep_data = []
        # Otherwise, it's molecular data
        elif len(parts) > 2:
            coordinates = list(map(float, parts[1:4]))  # Extract x, y, z coordinates
            current_timestep_data.append(coordinates)

    # Append any remaining timestep data
    if current_timestep_data:
        all_data.append(current_timestep_data)
        print(f"Last timestep data length: {len(current_timestep_data)}")  # Let's inspect the length
    # At this point, let's not convert to numpy array yet, first, let's identify the issue
    return all_data


def count_agents_per_timestep(modelout_fp: str):
    with open(modelout_fp, 'r') as f:
        lines = f.readlines()
    timestep_counts = {}
    current_timestep = None
    count = 0
    for line in lines:
        line = line.strip()

        # Assuming a timestep line is a single number, like "2" or "2 2"
        if line.isdigit() or all(x.isdigit() for x in line.split()):
            # If we already have a current timestep, record its count and reset
            if current_timestep is not None:
                timestep_counts[current_timestep] = count
                count = 0
            current_timestep = line
        else:
            # Increment the agent count for the current timestep
            count += 1

    # After the loop, we should add the count for the last timestep
    if current_timestep is not None:
        timestep_counts[current_timestep] = count
    return timestep_counts


def calculate_n_agents(modelout_fp: str) -> int:
    agent_counts = count_agents_per_timestep(modelout_fp)
    return sum(list(agent_counts.values()))
