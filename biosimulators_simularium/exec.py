import os
from biosimulators_simularium.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive


test_archive_root = 'biosimulators_simularium/tests/fixtures/archives/__minE_Andrews_052023'
test_simularium_filename = 'newest_minE_simularium_test'

archive = SmoldynCombineArchive(rootpath=test_archive_root, simularium_filename=test_simularium_filename)

converter = SmoldynDataConverter(archive=archive)

# converter.generate_simularium_file(io_format='JSON')

print(converter.archive.simularium_filename)
