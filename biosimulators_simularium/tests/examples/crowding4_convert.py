import os
from typing import *
import smoldyn
from biosimulators_utils.model_lang.smoldyn.validation import validate_model
from biosimulators_simularium.util.core import HEX_COLORS
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.old_api.converters.data_model import SmoldynDataConverter


crowding_archive_path = os.path.join('biosimulators_simularium', 'tests', 'fixtures', 'archives', 'crowding4')

archive = SmoldynCombineArchive(
    rootpath=crowding_archive_path,
    simularium_filename='crowding4_binary_save'
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
    ('red(up)', 0.2, HEX_COLORS.get('red')),
    ('green(up)', 0.5, HEX_COLORS.get('green')),
]

converter.generate_simularium_file(agents=agents, io_format='binary', box_size=20.0)
