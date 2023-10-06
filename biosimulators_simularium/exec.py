import os
from biosimulators_simularium.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive


test_archive_root = 'biosimulators_simularium/tests/fixtures/archives/__minE_Andrews_052023'
test_simularium_fp = os.path.join(test_archive_root, 'newest_minE_simularium_test')

archive = SmoldynCombineArchive(rootpath=test_archive_root, simularium_filename=test_simularium_fp)

print(archive.model_output_filename)

