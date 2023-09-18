import os
import argparse
from biosimulators_simularium.converters.data_model import CombineArchive, SmoldynDataConverter
from biosimulators_simularium.converters.io import generate_new_simularium_file
from biosimulators_simularium.utils.io import remove_file, remove_output_files, parse_platform


def run(archive_rootpath: str, simularium_file_name: str, install_smoldyn=False) -> None:
    if install_smoldyn:
        parse_platform()
    return generate_new_simularium_file(archive_rootpath=archive_rootpath, simularium_filename=simularium_file_name)


def main():
    parser = argparse.ArgumentParser(description="Convert a smoldyn output file to simularium format")
    parser.add_argument("-archive_rootpath", required=True, help="Path to the archive root")
    parser.add_argument("-simularium_filename", required=True, help="Name of the Simularium file")
    parser.add_argument("-install_smoldyn", action="store_true", help="Flag to install smoldyn")

    args = parser.parse_args()

    run(
        archive_rootpath=args.archive_rootpath,
        simularium_file_name=args.simularium_filename,
        install_smoldyn=args.install_smoldyn
    )


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


archive_root = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523'
simularium_fp = os.path.join(archive_root, 'MY_SIMULARIUM_TEST_OUTPUT')


if __name__ == '__main__':
    # convert(archive_rootpath=archive_root, install_smoldyn=False)
    # generate_new_simularium_file(archive_rootpath=archive_root, simularium_filename=simularium_fp)
    main()
