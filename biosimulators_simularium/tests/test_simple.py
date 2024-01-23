import os
import tempfile
from simulariumio.smoldyn.smoldyn_data import SmoldynData
from biosimulators_simularium.io import get_model_fp, get_archive_files
from biosimulators_simularium.tests import make_test_dir
from biosimulators_simularium.simulation_data import generate_agent_params
from biosimulators_simularium.exec import execute
from biosimulators_simularium.convert import (
    generate_output_trajectory,
    get_species_names_from_model_file,
    display_data_dict_from_archive_model
)


def assert_clause(clause: bool) -> int:
    try:
        assert clause
        return 0
    except:
        return 1


OUTPUT_DIR = 'Biosimulators_simularium/OUTPUT'
MIN_E_DIR = 'biosimulators_simularium/tests/fixtures/MinE'
CROWDING_DIR = 'biosimulators_simularium/tests/fixtures/crowding'
DOC_TEST_NAME = 'simularium'
USE_JSON = True


def test_simple_execute(archive_root=MIN_E_DIR, test_name=DOC_TEST_NAME, is_json=USE_JSON):
    archive_root = MIN_E_DIR
    make_test_dir(OUTPUT_DIR)
    execute(working_dir=archive_root, use_json=is_json, output_dir=OUTPUT_DIR)
    print(f'out files: {get_archive_files(OUTPUT_DIR)}')
    assert_clause(os.path.exists(os.path.join(archive_root, test_name + '.simularium')))


def test_simple_convert_minE():
    archive_root = 'biosimulators_simularium/tests/fixtures/MinE'
    simularium_name = 'simulation'
    is_json = True
    execute(working_dir=archive_root, use_json=is_json, output_dir=OUTPUT_DIR)
    assert_clause(os.path.exists(os.path.join(archive_root, DOC_TEST_NAME + '.simularium')))


def test_simple_convert_crowding():
    archive_root = 'biosimulators_simularium/tests/fixtures/crowding'
    simularium_name = 'simulation'
    is_json = True
    execute(working_dir=archive_root, use_json=is_json, output_dir=OUTPUT_DIR)
    assert_clause(os.path.exists(os.path.join(archive_root, DOC_TEST_NAME + '.simularium')))


def test_tempdir_convert():
    archive_root = 'biosimulators_simularium/tests/fixtures/MinE'
    simularium_name = 'simulation'
    is_json = True
    out_dir = tempfile.mkdtemp()
    execute(working_dir=archive_root, use_json=is_json, output_dir=out_dir)
    print(f'Output dir: {get_archive_files(out_dir)}')
    assert_clause(os.path.exists(os.path.join(out_dir, DOC_TEST_NAME + '.simularium')))


def test_trajectory_object():
    archive_root = 'biosimulators_simularium/tests/fixtures/MinE'
    simularium_name = 'simulation'
    model = get_model_fp(archive_root)
    specs = get_species_names_from_model_file(model)
    params = generate_agent_params(species_names=specs, global_density=10.0, basis_m=3343)
    display_dict = display_data_dict_from_archive_model(rootpath=archive_root, agent_params=params, mol_major=False)
    trajectory = generate_output_trajectory(root_fp=archive_root)
    assert_clause(isinstance(trajectory, SmoldynData))





