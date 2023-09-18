import os
from typing import Dict
import platform
import subprocess as subproc
from biosimulators_utils.model_lang.smoldyn.utils import get_parameters_variables_outputs_for_simulation
from biosimulators_utils.config import Config
from biosimulators_utils.report.data_model import ReportFormat
from biosimulators_utils.sedml.data_model import UniformTimeCourseSimulation, Variable, Task
from biosimulators_simularium.converters.data_model import CombineArchive, SmoldynDataConverter
from biosimulators_simularium.converters.io import generate_new_simularium_file
from biosimulators_simularium.utils.io import remove_file, remove_output_files, parse_platform


def convert(
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


def test_convert(archive_rootpath=archive_root):
    minE_archive = CombineArchive(rootpath=archive_rootpath, simularium_filename='MY_TEST_SIMULARIUM_OUTPUT')
    converter = SmoldynDataConverter(archive=minE_archive)
    converter.generate_simularium_file()


if __name__ == '__main__':
    # convert(archive_rootpath=archive_root, install_smoldyn=False)
    # generate_new_simularium_file(archive_rootpath=archive_root)
    test_convert(archive_root)
