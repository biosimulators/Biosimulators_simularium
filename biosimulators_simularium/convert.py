import os
from typing import Dict
import platform
import subprocess as subproc
from biosimulators_utils.model_lang.smoldyn.utils import get_parameters_variables_outputs_for_simulation
from biosimulators_utils.config import Config
from biosimulators_utils.report.data_model import ReportFormat
from biosimulators_utils.sedml.data_model import UniformTimeCourseSimulation, Variable, Task
from biosimulators_simularium.converters.data_model import Archive, SimulariumFilePath, SmoldynDataConverter
from biosimulators_simularium.converters.io import generate_new_simularium_file
from biosimulators_simularium.utils.io import remove_file, remove_output_files, parse_platform


def run(
        archive_rootpath: str,
        archive_output_dirpath: str,
        new_simularium_fp: str,
        install_smoldyn=False
        ):
    if install_smoldyn:
        parse_platform()

    archive = Archive(rootpath=archive_rootpath, output_dirpath=archive_output_dirpath)
    new_simularium_fp = SimulariumFilePath(path=new_simularium_fp)

    converter = SmoldynDataConverter(archive, new_simularium_fp)

    print(f'Model path: {converter.archive.model_path}')


archive_root = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523'
archive_output = 'biosimulators_simularium'
simularium_fp = os.path.join(archive_output, 'test_simularium_file_new')

run(archive_root, archive_output, simularium_fp, install_smoldyn=False)

