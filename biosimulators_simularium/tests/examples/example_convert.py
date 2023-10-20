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
    'MinD_ATP(front)',
    'MinE(solution)',
    'MinD_ADP(solution)',
    'MinDMinE(front)',
    'MinD_ATP(solution)'
]

box_size = 100.0
display_dict = converter.generate_display_data_dict(agents)
metadata_object = converter.generate_metadata_object(box_size=box_size)
converter.generate_simularium_file(io_format='JSON', metadata_object=metadata_object, display_data=display_dict)

print(metadata_object.scale_factor)
