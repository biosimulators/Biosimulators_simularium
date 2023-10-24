import os
import re
from typing import *
import smoldyn
from biosimulators_utils.model_lang.smoldyn.validation import validate_model
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.converters.data_model import SmoldynDataConverter


crowding_archive_path = os.path.join('biosimulators_simularium', 'tests', 'fixtures', 'archives', 'crowding4')

archive = SmoldynCombineArchive(
    rootpath=crowding_archive_path,
    simularium_filename='crowding4'
)

validation = validate_model(archive.model_path)


def parse_simulation(validation: Tuple):
    simulation = []
    for item in validation:
        if len(item):
            for thing in item:
                if isinstance(thing, smoldyn.Simulation):
                    return thing.runSim()


converter = SmoldynDataConverter(archive)

agents = [
    ('red(up)', 0.2, '#eb1414'),
    ('green(up)', 0.5, '#5dcf30'),
]

# converter.generate_simularium_file(agents=agents, io_format='JSON', box_size=20.0)


def parse_agent_names_from_model_file(model_fp):
    # Function to check if a substring is a number (integer or decimal)
    def is_number(substring):
        try:
            float(substring)  # for handling numbers with decimals
            return True
        except ValueError:
            return False

    def get_names(model_fp):
        validation = validate_model(model_fp)
        sim_info = validation[2]
        agent_names = []
        for info in sim_info:
            if isinstance(info, list):
                for line in info:
                    if line.startswith('difc'):
                        agent_names.append(line)
        names = [item.replace('difc ', '') for item in agent_names]
        return names

    def standardize_names(names):
        agent_list = []
        # \b is a word boundary in regex, ensuring we're removing "words" that are entirely made up of digits (possibly with a decimal point)
        pattern = re.compile(
            r'\b\d+(\.\d+)?\b')

        for item in names:
            # Use regex sub() method to replace numbers with an empty string
            new_string = pattern.sub('', item)

            # Strip extra whitespace that may have been left behind after removing numbers
            new_string = new_string.strip()

            agent_list.append(new_string)
        return agent_list

    names = get_names(model_fp)
    return standardize_names(names)


names = parse_agent_names_from_model_file(archive.model_path)
print(names)
