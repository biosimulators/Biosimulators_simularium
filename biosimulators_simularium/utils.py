"""Some of the functions are from smoldyn.biosimulators.combine"""


import re
import os


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

