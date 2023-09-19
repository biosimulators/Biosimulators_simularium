from biosimulators_simularium.converters.data_model import SmoldynDataGenerator, SmoldynDataConverter
from smoldyn import Simulation
from simulariumio import InputFileData, DisplayData
import os
from typing import Dict
from simulariumio.smoldyn import SmoldynData

MODEL_FP = 'biosimulators_simularium/test_files/models/ecoli_model.txt'
MODEL_OUTPUT_FP = 'biosimulators_simularium/test_files/models/ecoli_modelout.txt'
ECOLI_ARCHIVE_DIRPATH = 'biosimulators_simularium/test_files/archives/Andrews_ecoli_0523'
SED_DOC_PATH = os.path.join(ECOLI_ARCHIVE_DIRPATH, 'simulation.sedml')
SIMULARIUM_DIRPATH = 'biosimulators_simularium/generated_simularium_files'
SIMULARIUM_FILENAME = 'ecoli_spatial_7'

BOX_SIZE = 1.
N_DIM = 3
AGENTS = [
    ('MinD_ATP(front)', 'D_d', 2.0, "#FFFF00"),
    ('MinE(solution)', 'D_E', 1.0, "#800080"),
    ('MinD_ATP(solution)', 'SIGMA_D', 1.0, "#FF0000"),
    ('MinD_ADP(solution)', 'D_D', 1.0, "#008000"),
    ('MinDMinE(front)', 'D_de', 1.0, "#FFA500"),
]


def main():
    generator = SmoldynDataGenerator()
    converter = SmoldynDataConverter()

    sim = generate_simulation(generator)
    run_simulation(sim)

    simularium_fp = prepare_simularium_dir(converter)
    input_file_data = generate_input_file_data(converter)
    display_obj_dict = generate_display_obj_dict(converter)
    smoldyn_data = generate_smoldyn_data_object(
        converter,
        input_file_data,
        display_obj_dict
    )

    translated_data = translate_data(converter, smoldyn_data)
    write_simularium_file(converter, translated_data)


def generate_simulation(g: SmoldynDataGenerator) -> Simulation:
    return g.generate_simulation_object_from_configuration_file(MODEL_FP)


def run_simulation(s: Simulation) -> None:
    return s.runSim()


def prepare_simularium_dir(c: SmoldynDataConverter) -> str:
    return c.prepare_simularium_fp(SIMULARIUM_DIRPATH, SIMULARIUM_FILENAME)


def generate_input_file_data(c: SmoldynDataConverter) -> InputFileData:
    return c.prepare_input_file_data(MODEL_OUTPUT_FP)


def generate_display_obj_dict(c: SmoldynDataConverter) -> Dict:
    return c.generate_display_data_object_dict(AGENTS)


def generate_smoldyn_data_object(
        c: SmoldynDataConverter,
        fd: InputFileData,
        dd: Dict[str, DisplayData]
        ) -> SmoldynData:
    return c.prepare_smoldyn_data_for_conversion(
        file_data=fd,
        display_data=dd
    )


def translate_data(c: SmoldynDataConverter, data: SmoldynData):
    return c.translate_data(data, BOX_SIZE, N_DIM)


def write_simularium_file(c: SmoldynDataConverter, data) -> None:
    return c.convert_to_simularium(data, SIMULARIUM_FILENAME)


if __name__ == '__main__':
    main()


'''TODO:

1. RUN A SIMULATION FROM A SED DOC, AND OPEN THE VANILLA CSV DF WITH PANDAS AND TRY TO GET THE 3D DisplayData
2. CHANGE THE REGULAR SMOLDYN SIMULATION DISPLAY DATA OBJECT PARAMS TO BE SPHERE GROUP WITH SPHERES!'''