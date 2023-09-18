from biosimulators_simularium.converters.data_model import CombineArchive, SmoldynDataConverter
from biosimulators_simularium.utils.io import parse_platform


def test_run(
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
