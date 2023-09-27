from os import path as p
from biosimulators_simularium.converters.utils import (
    generate_model_validation_object,
)
from biosimulators_simularium.converters.data_model import (
    ModelValidation,
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


def test_generate_simularium_file_from_object():
    try:
        assert p.exists(TEST_ARCHIVE_ROOTPATH)
    except AssertionError('That file does not exist') as e:
        print(e)
        return

    archive = SmoldynCombineArchive(
        rootpath=TEST_ARCHIVE_ROOTPATH,
        simularium_filename=TEST_SIMULARIUM_FILENAME
    )

    # generate a modelout file if one does not exist
    '''if not p.exists(archive.model_output_filename):
        validation = generate_model_validation_object(archive)
        validation.simulation.runSim()'''

    converter = SmoldynDataConverter(archive)

    '''standardize_model_output_filename(archive)'''
    # create SmoldynDataConverter object and convert modelout to simularium via interface

    '''converter.generate_simularium_file()'''


def test_generate_simularium_file_from_function():
    pass


TESTS = {
    'test_generate_simularium_file_from_object': test_generate_simularium_file_from_object,
    'test_generate_simularium_file_from_function': test_generate_simularium_file_from_function,
}


if __name__ == '__main__':
    for k in TESTS.keys():
        TESTS[k]()
