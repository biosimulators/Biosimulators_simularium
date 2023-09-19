import os
import argparse
from biosimulators_simularium.converters.io import generate_new_simularium_file
from biosimulators_simularium.utils.io import remove_file, remove_output_files, parse_platform


def run(archive_rootpath: str, simularium_file_name: str, install_smoldyn=0) -> None:
    if install_smoldyn:
        parse_platform()
    simularium_filepath = os.path.join(archive_rootpath, simularium_file_name)
    return generate_new_simularium_file(archive_rootpath=archive_rootpath, simularium_filename=simularium_filepath)


def main():
    parser = argparse.ArgumentParser(description="Convert a smoldyn output file to simularium format")
    parser.add_argument("-archive_rootpath", required=True, help="Path to the archive root")
    parser.add_argument("-simularium_filename", required=True, help="Name of the Simularium file")
    parser.add_argument("-install_smoldyn", action="store_true", help="Install Smoldyn at runtime")

    args = parser.parse_args()

    run(
        archive_rootpath=args.archive_rootpath,
        simularium_file_name=args.simularium_filename,
        install_smoldyn=args.install_smoldyn
    )

# NOW ADD A METHOD THAT ADDS THE SIMULARIUM FILE TO THE XML MANIFEST!

if __name__ == '__main__':
    main()
