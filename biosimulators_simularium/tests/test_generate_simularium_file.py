from os import path as p
import os
import warnings
from simulariumio import DISPLAY_TYPE, AgentData
from biosimulators_simularium.converters.data_model import (
    SmoldynCombineArchive,
    SmoldynDataConverter,
    AgentDisplayData,
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


def test_generate_minE_simularium_file(archive_fp, translate=False, v=True, f='JSON'):
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

    # construct a list of AgentDisplayData objects from simulation agents
    agents = [
        AgentDisplayData(
            name='MinD_ATP(solution)',
            radius=2.0,
            display_type=DISPLAY_TYPE.SPHERE
        ),
        AgentDisplayData(
            name='MinD_ATP(front)',
            radius=4.0,
            display_type=DISPLAY_TYPE.SPHERE
        ),
        AgentDisplayData(
            name='MinD_ADP(solution)',
            radius=2.0,
            display_type=DISPLAY_TYPE.SPHERE
        ),
        AgentDisplayData(
            name='MinE(solution)',
            radius=2.0,
            display_type=DISPLAY_TYPE.SPHERE
        ),
        AgentDisplayData(
            name='MinDMinE(front)',
            radius=4.0,
            display_type=DISPLAY_TYPE.SPHERE
        ),
    ]

    # generate a display data object mapping
    display = converter.generate_display_data_object_dict(agents)

    # convert the file
    converter.generate_simularium_file(
        temporal_units='ns',
        display_data=display,
        translate=translate,
        validate_ids=v,
        io_format=f
    )


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


def main():
    """
    # test generate simularium file from object using unzipped archive (dirpath)
    # test_generate_simularium_file_from_object(archive_fp=TEST_ARCHIVE_ROOTPATH)

    # test generate simularium file from object using OMEX file (filepath)
    # test_generate_simularium_file_from_object(
    #     archive_fp=TEST_OMEX_FILEPATH,
    #     new_omex=NEW_TEST_OMEX_FILEPATH
    # )
    """

    # test generate simularium file from object with custom display data (dirpath). Write to Binary.
    test_generate_minE_simularium_file(
        archive_fp=TEST_ARCHIVE_ROOTPATH,
        v=False,
        translate=True,
    )


if __name__ == '__main__':
    main()

