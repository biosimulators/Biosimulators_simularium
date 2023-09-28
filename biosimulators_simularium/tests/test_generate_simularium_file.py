from os import path as p
import warnings
from biosimulators_simularium.converters.data_model import (
    SmoldynCombineArchive,
    SmoldynDataConverter
)


TEST_ARCHIVE_LOCATION = p.join(
    p.abspath(p.dirname(__file__)),
    'fixtures',
    'archives',
)
TEST_ARCHIVE_ROOTPATH = p.join(TEST_ARCHIVE_LOCATION, 'minE_Andrews_052023')
TEST_OMEX_FILEPATH = TEST_ARCHIVE_ROOTPATH + '.omex'
TEST_SIMULARIUM_FILENAME = p.join(TEST_ARCHIVE_ROOTPATH, 'generated_from_test')
GENERATE_MODEL_OUTPUT = True


def main():
    # test generate simularium file from object using unzipped archive (dirpath)
    test_generate_simularium_file_from_object(archive_fp=TEST_ARCHIVE_ROOTPATH)

    # test generate simularium file from object using OMEX file (filepath)
    # test_generate_simularium_file_from_object(archive_fp=TEST_OMEX_FILEPATH)


def test_generate_simularium_file_from_object(archive_fp):
    try:
        assert p.exists(archive_fp)
    except AssertionError('That file does not exist') as e:
        print(e)
        return

    # construct an archive instance to base operations on
    archive = SmoldynCombineArchive(
        rootpath=archive_fp,
        simularium_filename=TEST_SIMULARIUM_FILENAME
    )

    # generate a modelout file if one does not exist
    converter = SmoldynDataConverter(
        archive=archive,
        generate_model_output=GENERATE_MODEL_OUTPUT
    )

    try:
        df = converter.read_model_output_dataframe()
        print(f'A dataframe was able to be created from the valid model output:\n{df}\n')
    except Exception as e:
        warnings.warn(str(e))

    # create SmoldynDataConverter object and convert modelout to simularium via interface
    converter.generate_simularium_file(spatial_units='nm', temporal_units='s')


def test_generate_simularium_file_from_function():
    pass


if __name__ == '__main__':
    main()

