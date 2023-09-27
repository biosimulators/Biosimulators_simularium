from os import path as p
import warnings
from biosimulators_simularium.converters.data_model import (
    SmoldynCombineArchive,
    SmoldynDataConverter
)


TEST_ARCHIVE_ROOTPATH = p.join(
    p.abspath(p.dirname(__file__)),
    'fixtures',
    'archives',
    'minE_Andrews_052023',
)
TEST_SIMULARIUM_FILENAME = p.join(TEST_ARCHIVE_ROOTPATH, 'generated_from_test')
GENERATE_MODEL_OUTPUT = True


def test_generate_simularium_file_from_object():
    try:
        assert p.exists(TEST_ARCHIVE_ROOTPATH)
    except AssertionError('That file does not exist') as e:
        print(e)
        return

    # construct an archive instance to base operations on
    archive = SmoldynCombineArchive(
        rootpath=TEST_ARCHIVE_ROOTPATH,
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
    converter.generate_simularium_file()


def test_generate_simularium_file_from_function():
    pass


TESTS = {
    'test_generate_simularium_file_from_object': test_generate_simularium_file_from_object,
    'test_generate_simularium_file_from_function': test_generate_simularium_file_from_function,
}


if __name__ == '__main__':
    for k in TESTS.keys():
        TESTS[k]()
