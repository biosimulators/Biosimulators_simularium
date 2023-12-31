from typing import *
# from biosimulators_utils.sedml.data_model import Variable
# from smoldyn.biosimulators.combine import validate_variables
import os
import tempfile
import re
from dataclasses import dataclass
from typing import Tuple, List
import numpy as np
from smoldyn import Simulation as smoldynSim


__all__ = [
    'ModelValidation',
    'validate_model',
    'generate_model_validation_object',
    'read_smoldyn_simulation_configuration',
    'disable_smoldyn_graphics_in_simulation_configuration',
    'write_smoldyn_simulation_configuration'
]


@dataclass
class ModelValidation:
    errors: List[List[str]]
    warnings: List[str]
    simulation: smoldynSim
    config: List[str]

    def __init__(self, validation: Tuple[List[List[str]], List, Tuple[smoldynSim, List[str]]]):
        self.errors = validation[0]
        self.warnings = validation[1]
        self.simulation = validation[2][0]
        self.config = validation[2][1]


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


def generate_model_validation_object(
        archive
) -> ModelValidation:
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


def read_smoldyn_simulation_configuration(filename):
    ''' Read a configuration for a Smoldyn simulation

    Args:
        filename (:obj:`str`): path to model file

    Returns:
        :obj:`list` of :obj:`str`: simulation configuration
    '''
    with open(filename, 'r') as file:
        return [line.strip('\n') for line in file]


def write_smoldyn_simulation_configuration(configuration, filename):
    ''' Write a configuration for Smoldyn simulation to a file

    Args:
        configuration
        filename (:obj:`str`): path to save configuration
    '''
    with open(filename, 'w') as file:
        for line in configuration:
            file.write(line)
            file.write('\n')


def disable_smoldyn_graphics_in_simulation_configuration(configuration):
    ''' Turn off graphics in the configuration of a Smoldyn simulation

    Args:
        configuration (:obj:`list` of :obj:`str`): simulation configuration
    '''
    for i_line, line in enumerate(configuration):
        if line.startswith('graphics '):
            configuration[i_line] = re.sub(r'^graphics +[a-z_]+', 'graphics none', line)


def init_smoldyn_simulation_from_configuration_file(filename):
    ''' Initialize a simulation for a Smoldyn model from a file

    Args:
        filename (:obj:`str`): path to model file

    Returns:
        :obj:`smoldyn.Simulation`: simulation
    '''
    if not os.path.isfile(filename):
        raise FileNotFoundError('Model source `{}` is not a file.'.format(filename))

    smoldyn_simulation = smoldynSim.fromFile(filename)
    if not smoldyn_simulation.getSimPtr():
        error_code, error_msg = smoldynSim.getError()
        msg = 'Model source `{}` is not a valid Smoldyn file.\n\n  {}: {}'.format(
            filename, error_code.name[0].upper() + error_code.name[1:], error_msg.replace('\n', '\n  '))
        raise ValueError(msg)

    return smoldyn_simulation


def verify_simularium_in_archive(archive) -> bool:
    return '.simularium' in list(archive.paths.keys())


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


'''def validate_spatial(model_fp: str) -> Dict[Tuple, Tuple]:
    """Validate a list of `Variable` objects whose simulation's output data is spatial in nature, i.e: `listmols`.
        Wrapper of `smoldyn.biosimulators.combine.validate_variables()` which handles inevitable errors and
        continues.

        Args:
            variables:`List[Variable]`: A list of Variables derived from the Smoldyn simulation.

        Returns:
            :obj:`Dict[Tuple, Tuple]`: dictionary that maps variable targets and symbols to Smoldyn output commands
    """
    sim_config = read_smoldyn_simulation_configuration(model_fp)
    for line in sim_config:
        if 'cmd' or 'output_files' in line:
            line[0] = '#'

    os.remove(model_fp)
    write_smoldyn_simulation_configuration(sim_config, model_fp)

    simulation = validate_model(model_fp)[2][0]
    #simulation.addOutputData('output_time')
    simulation.addOutputData('molecules')
    #simulation.addCommand(cmd='executiontime output_time', cmd_type='E')
    simulation.addCommand(cmd='listmols molecules', cmd_type='E')
    simulation.runSim()

    output_data = simulation.getOutputData('molecules')

    variables = []
    for mol in output_data:
        variable = Variable(
            id=str(mol[-1]),

        )
'''


