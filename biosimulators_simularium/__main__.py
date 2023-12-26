"""
:Author: Alexander Patrie <apatrie@uchc.edu>
:Date: 2023-09-16
:Copyright: 2023, UConn Health
:License: MIT
"""


# TODO: Update this CLI functionality based on the new simplified API

'''
import os
import argparse
from biosimulators_simularium.converters.io import generate_new_simularium_file


def run(archive_rootpath: str, simularium_file_name: str, install_smoldyn=0) -> None:
    simularium_filepath = os.path.join(archive_rootpath, simularium_file_name)
    return generate_new_simularium_file(archive_rootpath=archive_rootpath, simularium_filename=simularium_filepath)


def main():
    parser = argparse.ArgumentParser(description="Convert a smoldyn output file to simularium format")
    parser.add_argument("-a", required=True, help="Path to the archive root")
    parser.add_argument("-s", required=True, help="Name of the Simularium file")
    parser.add_argument("-install_smoldyn", action="store_true", help="Install Smoldyn at runtime")

    args = parser.parse_args()

    run(
        archive_rootpath=args.a,
        simularium_file_name=args.s,
        install_smoldyn=args.install,
    )


# TODO: NOW ADD A METHOD THAT ADDS THE SIMULARIUM FILE TO THE XML MANIFEST!
'''


if __name__ == '__main__':
    # main()
    pass
