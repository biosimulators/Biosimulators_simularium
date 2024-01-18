import os
from biosimulators_simularium import generate_simularium_file
from biosimulators_simularium.io import get_model_fp
from biosimulators_simularium.convert import generate_output_data_object, display_data_dict_agent_major, get_species_names_from_model_file, display_data_dict_from_archive_model
from biosimulators_simularium.simulation_data import generate_agent_params
from biosimulators_simularium.exec import generate_simularium_file


def test_convert():
    archive_root = 'biosimulators_simularium/tests/fixtures/archives/MinE'
    simularium_fn = 'simulation'
    is_json = True

    generate_simularium_file(
        working_dir=archive_root,
        simularium_filename=simularium_fn,
        use_json=is_json
    )
    assert os.path.exists(os.path.join(archive_root, simularium_fn))


def test_trajectory_object():
    archive_root = 'biosimulators_simularium/tests/fixtures/MinE'
    model = get_model_fp(archive_root)
    specs = get_species_names_from_model_file(model)
    params = generate_agent_params(species_names=specs, global_density=10.0, basis_m=3343)
    display_dict = display_data_dict_from_archive_model(rootpath=archive_root, agent_params=params, mol_major=False)
    trajectory = generate_output_data_object(root_fp=archive_root)




test_trajectory_object()

