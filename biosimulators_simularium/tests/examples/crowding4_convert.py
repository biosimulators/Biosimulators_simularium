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
    simularium_filename='crowding4_new'
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

converter.generate_simularium_file(agents=agents, io_format='JSON', box_size=20.0)
