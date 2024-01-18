import os
from biosimulators_simularium import generate_simularium_file
from biosimulators_simularium.io import get_model_fp
from biosimulators_simularium.convert import generate_output_data_object, display_data_dict_agent_major, get_species_names_from_model_file
from biosimulators_simularium.simulation_data import generate_agent_params


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
    print(model)
    specs = get_species_names_from_model_file(model)
    params = generate_agent_params(model, 1.0, 10000)
    print(params)



test_trajectory_object()
./
