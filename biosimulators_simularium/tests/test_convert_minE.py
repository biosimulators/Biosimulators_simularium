"""This is an example workflow using the v0.5.0 Simplified API."""


import os
from numpy.random import randint
from biosimulators_simularium.simulation_data import generate_agent_params_for_minE
from biosimulators_simularium.exec import generate_simularium_file
from biosimulators_simularium.config import Config


def test_convert_minE():
    # define the working dir
    working_dir = 'biosimulators_simularium/tests/fixtures/MinE'

    # define the simularium filepath (using the working dir as root in this case)
    simularium_fn = os.path.join(working_dir, 'simplified-api-output')

    model_fp = os.path.join(working_dir, 'model.txt')

    agent_params = generate_agent_params_for_minE(model_fp, 12100, 1.0)

    generate_simularium_file(
        working_dir=working_dir,
        simularium_filename=simularium_fn,
        agent_params=agent_params,
        model_fp=model_fp
    )
    try:
        assert os.path.exists(simularium_fn)
        print(f'{simularium_fn} has been successfully generated.')
    except:
        AssertionError('A simularium file could not be generated.')


def test_convert_minE_no_params():
    # define the working dir
    working_dir = 'biosimulators_simularium/tests/fixtures/MinE'

    # define the simularium filepath (using the working dir as root in this case)
    simularium_fn = os.path.join(working_dir, 'simulation')

    model_fp = os.path.join(working_dir, 'model.txt')

    generate_simularium_file(
        working_dir=working_dir,
        simularium_filename=simularium_fn
    )
    try:
        assert os.path.exists(simularium_fn)
        print(f'{simularium_fn} has been successfully generated.')
    except:
        AssertionError('A simularium file could not be generated.')
