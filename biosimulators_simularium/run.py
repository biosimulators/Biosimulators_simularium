import os
from typing import Dict
from platform import platform
import subprocess as subproc
from biosimulators_utils.config import Config
from biosimulators_utils.report.data_model import ReportFormat
from biosimulators_simularium.converters.io import SmoldynDataConverter, generate_new_simularium_file
from biosimulators_simularium.utils.io import remove_file, remove_output_files

__all__ = [
    'run',
]

ECOLI_ARCHIVE_DIRPATH = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523'
ECOLI_OMEX_DIRPATH = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523.omex'
SED_DOC_PATH = os.path.join(ECOLI_ARCHIVE_DIRPATH, 'simulation.sedml')
SIMULARIUM_DIRPATH = 'biosimulators_simularium/generated_simularium_files'
SIMULARIUM_FILENAME = 'ecoli_spatial_from_sedml_0'
OUTPUTS_DIRPATH = 'biosimulators_simularium/simulation_outputs'

BOX_SIZE = 1.
N_DIM = 3
AGENTS = [
    ('MinD_ATP(front)', 'D_d', 2.0, "#FFFF00"),
    ('MinE(solution)', 'D_E', 1.0, "#800080"),
    ('MinD_ATP(solution)', 'SIGMA_D', 1.0, "#FF0000"),
    ('MinD_ADP(solution)', 'D_D', 1.0, "#008000"),
    ('MinDMinE(front)', 'D_de', 1.0, "#FFA500"),
]


def install_smoldyn_mac():
    plat = platform()
    mac = "Darwin"
    if mac or mac.lower() in plat:
        subproc.run("cd smoldyn-2.72-mac")
        subproc.run("sudo -H ./install.sh")


def run(install_mac=1, rm_files=1):
    model_out = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523/modelout.txt'
    min_save = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523/MinSave.txt'

    if rm_files:
        remove_file(model_out)
        remove_file(min_save)
        remove_output_files()

    if install_mac:
        install_smoldyn_mac()
    return generate_new_simularium_file(ECOLI_ARCHIVE_DIRPATH)

