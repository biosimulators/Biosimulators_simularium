import os
from typing import Dict
from platform import platform
import smoldyn
import subprocess as subproc
from biosimulators_utils.model_lang.smoldyn.utils import get_parameters_variables_outputs_for_simulation
from biosimulators_utils.config import Config
from biosimulators_utils.report.data_model import ReportFormat
from biosimulators_simularium.converters.data_model import Archive, SimulariumFilePath
from biosimulators_simularium.converters.io import SmoldynDataConverter, generate_new_simularium_file
from biosimulators_simularium.utils.io import remove_file, remove_output_files
from biosimulators_utils.sedml.data_model import UniformTimeCourseSimulation, Variable, Task


ECOLI_ARCHIVE_DIRPATH = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523'
ECOLI_OMEX_DIRPATH = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523.omex'
SED_DOC_PATH = os.path.join(ECOLI_ARCHIVE_DIRPATH, 'simulation.sedml')
SIMULARIUM_DIRPATH = 'biosimulators_simularium/generated_simularium_files'
SIMULARIUM_FILENAME = os.path.join(SIMULARIUM_DIRPATH, 'ecoli_spatial_from_sedml_0')
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
    '''if mac or mac.lower() in plat:
        subproc.run("cd biosimulators_simularium/smoldyn-2.72-mac")
        subproc.run("sudo -H ./install.sh")'''


def run(install_mac=1, rm_files=1):
    model_out = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523/modelout.txt'
    min_save = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523/MinSave.txt'

    '''if rm_files:
        remove_file(model_out)
        remove_file(min_save)
        remove_output_files()'''

    if install_mac:
        install_smoldyn_mac()
    return generate_new_simularium_file(ECOLI_ARCHIVE_DIRPATH, SIMULARIUM_FILENAME)


def test():
    archive = Archive(ECOLI_ARCHIVE_DIRPATH, OUTPUTS_DIRPATH)
    simularium_fp = SimulariumFilePath(SIMULARIUM_FILENAME)
    converter = SmoldynDataConverter(archive, simularium_fp)

    params = get_parameters_variables_outputs_for_simulation(
        model_filename=converter.archive.model_path,
        model_language="urn:sedml:language:smoldyn",
        simulation_type=UniformTimeCourseSimulation
    )

    simulator = params[1][0]

    simulator.runSim()

    sim = smoldyn.biosimulators.fromFile(+)

    file_data = converter.prepare_input_file_data(
        'biosimulators_simularium/files/archives/Andrews_ecoli_0523/modelout.txt'
    )
    data = converter.generate_data_object_for_output(file_data=file_data)
    trans = converter.translate_data_object(data_object=data, box_size=1.)
    converter.save_simularium_file(trans, simularium_filename='/Users/alex/desktop/ecoli_spatial_from_sedml_0')


# turn off!
'''if __name__ == '__main__':
    # run()
    test()'''

test()