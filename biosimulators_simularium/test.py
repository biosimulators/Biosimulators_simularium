from biosimulators_simularium.converters.data_model import SmoldynDataConverter, SmoldynCombineArchive
import os

archive_root = 'biosimulators_simularium/tests/fixtures/archives/__minE_Andrews_052023'
simularium_fp = os.path.join(archive_root, 'test_simularium_output')

minE_archive = SmoldynCombineArchive(rootpath=archive_root, simularium_filename=simularium_fp)

converter = SmoldynDataConverter(archive=minE_archive)

converter.generate_simularium_file()

manifest_fp = minE_archive.get_manifest_filepath()
minE_archive.add_simularium_file_to_manifest()

print(simularium_fp)



