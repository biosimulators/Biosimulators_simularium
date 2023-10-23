import os
from typing import *
from simulariumio import DISPLAY_TYPE, DisplayData
from biosimulators_simularium.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive


test_archive_root = 'biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023'
test_simularium_filename = 'newest_minE_simularium_test'


archive = SmoldynCombineArchive(rootpath=test_archive_root, simularium_filename=test_simularium_filename)
converter = SmoldynDataConverter(archive=archive)


agents = [
    ('MinD_ATP(front)', 0.01),
    ('MinE(solution)', 0.01),
    ('MinD_ADP(solution)', 0.01),
    ('MinDMinE(front)', 0.01),
    ('MinD_ATP(solution)', 0.01)
]


converter.generate_simularium_file(io_format='JSON', agents=agents, box_size=10.0)
