import os
from typing import Dict
from biosimulators_utils.config import Config
from biosimulators_utils.report.data_model import ReportFormat

ECOLI_ARCHIVE_DIRPATH = 'biosimulators_simularium/test_files/archives/Andrews_ecoli_0523'
ECOLI_OMEX_DIRPATH = 'biosimulators_simularium/test_files/archives/Andrews_ecoli_0523.omex'
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


def make_files_dict(fp) -> Dict[str, str]:
    d = {}
    if os.path.exists(fp):
        for root, _, files in os.walk(fp):
            for i, f in enumerate(files):
                fp = os.path.join(root, f)
                d[fp + str(i)] = fp
    return d


def remove_output_files(fp='biosimulators_simularium/test_files/archives/Andrews_ecoli_0523') -> None:
    if os.path.exists(fp):
        for root, _, files in os.walk(fp):
            for f in files:
                fp = os.path.join(root, f)
                if fp.endswith('.txt') and 'model' not in fp:
                    os.remove(fp)


def remove_file(fp) -> None:
    return os.remove(fp) if os.path.exists(fp) else None


def main(rm_files=1) -> None:
    model_out = 'biosimulators_simularium/test_files/archives/Andrews_ecoli_0523/modelout.txt'
    min_save = 'biosimulators_simularium/test_files/archives/Andrews_ecoli_0523/MinSave.txt'

    if rm_files:
        remove_file(model_out)
        remove_file(min_save)
        remove_output_files()

    config = Config(
        LOG_PATH=OUTPUTS_DIRPATH,
        COLLECT_COMBINE_ARCHIVE_RESULTS=True,
        COLLECT_SED_DOCUMENT_RESULTS=True,
        REPORT_FORMATS=[ReportFormat.h5]
    )
    generator = SmoldynDataGenerator(
        output_dirpath=OUTPUTS_DIRPATH,
        config=config
    )

    model = os.path.join(ECOLI_ARCHIVE_DIRPATH, 'model.txt')
    lang = 'urn:sedml:language:smoldyn'
    sim_params = generator.get_params_from_model_file(model, lang)
    variables_list = sim_params.get('variables')
    mapping = validate_variables(variables_list)

    print(variables_list)
    print()
    print(mapping)

    # NOW MAKE A TASK!

    '''_, _, configuration = validate_model(model)

    simulation = configuration[0]

    simulation.runSim()'''


    '''result, log = generator.run_simulation_from_archive(ECOLI_OMEX_DIRPATH)
    print(result)'''

    '''generator.run_simulation_from_smoldyn_file(
        os.path.join(ECOLI_ARCHIVE_DIRPATH, 'model.txt')
    )'''

    '''result, log = generator.run_simulation_from_archive(
        archive_fp='biosimulators_simularium/test_files/archives/custom.omex',
    )'''

    # converter = SmoldynDataConverter(OUTPUTS_DIRPATH)

    # r0, r1, r2 = validate_model('biosimulators_simularium/test_files/archives/Andrews_ecoli_0523/model.txt')
    # print(r2)

    # input_file_data = converter.prepare_input_file_data(model_out)
    # data_object = converter.prepare_smoldyn_data_for_conversion(file_data=input_file_data)

    # trans = converter.translate_data(data_object, 100.)
    # converter.convert_to_simularium(data_object, 'biosimulators_simularium/minE_Andrews_052023')


if __name__ == '__main__':
    main(0)

