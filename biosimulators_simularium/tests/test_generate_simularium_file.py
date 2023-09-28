from os import path as p
import warnings
from simulariumio import DISPLAY_TYPE, DisplayData
from biosimulators_simularium.converters.data_model import (
    SmoldynCombineArchive,
    SmoldynDataConverter,
    AgentDisplayData
)


TEST_ARCHIVE_LOCATION = p.join(
    p.abspath(p.dirname(__file__)),
    'fixtures',
    'archives',
)
TEST_ARCHIVE_ROOTPATH = p.join(TEST_ARCHIVE_LOCATION, '__minE_Andrews_052023')
TEST_OMEX_FILEPATH = TEST_ARCHIVE_ROOTPATH.replace('__', '') + '.omex'
NEW_TEST_OMEX_FILEPATH = p.join(TEST_ARCHIVE_LOCATION, 'myNewlyGeneratedCOMBINE')
TEST_SIMULARIUM_FILENAME = p.join(TEST_ARCHIVE_ROOTPATH, 'generated_from_test')
GENERATE_MODEL_OUTPUT = True


def main():
    # test generate simularium file from object using unzipped archive (dirpath)
    test_generate_simularium_file_from_object(archive_fp=TEST_ARCHIVE_ROOTPATH)

    # test generate simularium file from object using OMEX file (filepath)
    test_generate_simularium_file_from_object(
        archive_fp=TEST_OMEX_FILEPATH,
        new_omex=NEW_TEST_OMEX_FILEPATH
    )

    # test generate simularium file from object with custom display data (dirpath)
    test_generate_simularium_file_from_object_with_custom_display(
        archive_fp=TEST_ARCHIVE_ROOTPATH,
        translate=True
    )


def test_generate_simularium_file_from_object_with_custom_display(archive_fp, translate=True):
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

    # construct an agent data dict from simulation agents
    agent_names = [
        'MinD_ATP(solution)',
        'MinD_ATP(front)',
        'MinD_ADP(solution)',
        'MinE(solution)',
        'MinDMinE(front)',
    ]
    display = {}
    for agent in agent_names:
        display[agent] = DisplayData(display_type=DISPLAY_TYPE.SPHERE, radius=0.45, name=agent)

    # convert the file
    converter.generate_simularium_file(temporal_units='s', display_data=display, translate=translate)


def test_generate_simularium_file_from_object(archive_fp, new_omex=None):
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
    converter.generate_simularium_file(
        spatial_units='nm',
        temporal_units='s',
        new_omex_filename=new_omex,
    )


def test_generate_simularium_file_from_function():
    pass


if __name__ == '__main__':
    main()

