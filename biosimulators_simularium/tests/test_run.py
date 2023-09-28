import os
from biosimulators_simularium.converters.data_model import CombineArchive, SmoldynDataConverter
from biosimulators_simularium.converters.io import generate_new_simularium_file
from biosimulators_simularium.utils.io import parse_platform, get_filepaths
from biosimulators_simularium.__main__ import run


TEST_ARCHIVE_ROOTPATH = 'biosimulators_simularium/fixtures/archives/__minE_Andrews_052023'


def test_generate_new_simularium_file():
    generate_new_simularium_file(archive_rootpath=TEST_ARCHIVE_ROOTPATH)
    paths = get_filepaths(TEST_ARCHIVE_ROOTPATH)
    for path in paths:
        return f'A simularium file exists: {".simularium" in path}'


def test_run():
    pass


def test_convert(
        archive_rootpath: str,
        archive_output_dirpath: str = None,
        new_simularium_fp: str = None,
        install_smoldyn=False
        ):
    if install_smoldyn:
        parse_platform()

    archive = CombineArchive(rootpath=archive_rootpath)
    converter = SmoldynDataConverter(archive)
    print(f'Model path: {converter.archive.model_path}')
    print(converter.archive.model_output_filename)

    input_file_data = converter.generate_input_file_data_object()
    print(input_file_data)
    print(dir(input_file_data))


if __name__ == '__main__':
    test_generate_new_simularium_file()
