import os
from typing import Dict
import platform
import subprocess as subproc
from biosimulators_utils.model_lang.smoldyn.utils import get_parameters_variables_outputs_for_simulation
from biosimulators_utils.config import Config
from biosimulators_utils.report.data_model import ReportFormat
from biosimulators_utils.sedml.data_model import UniformTimeCourseSimulation, Variable, Task
from biosimulators_simularium.converters.data_model import CombineArchive, SmoldynDataConverter
# from biosimulators_simularium.converters.io import generate_new_simularium_file
from biosimulators_simularium.utils.io import remove_file, remove_output_files, parse_platform


def run(
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

    converter.generate_model_output()


archive_root = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523'


run(archive_rootpath=archive_root, install_smoldyn=False)

