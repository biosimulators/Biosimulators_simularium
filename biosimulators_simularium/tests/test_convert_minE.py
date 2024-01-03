"""This is an example workflow using the v0.5.0 Simplified API."""


import os
from numpy.random import randint
from biosimulators_simularium.exec import generate_simularium_file
from biosimulators_simularium.config import Config


def randomize_mass(origin: float) -> int:
    return randint(int(origin))


def test_convert_minE():
    # define the working dir
    working_dir = 'biosimulators_simularium/tests/fixtures/MinE'

    # define the simularium filepath (using the working dir as root in this case)
    simularium_fn = os.path.join(working_dir, 'simplified-api-output')

    model_fp = os.path.join(working_dir, 'model.txt')

    # define agent parameters (for now, we randomly select masses based on MinE primitive mass)
    minE_molecular_mass = 12100
    agent_params = {
        'MinD_ATP': {
            'density': 1.0,
            'molecular_mass': randomize_mass(minE_molecular_mass),
        },
        'MinD_ADP': {
            'density': 1.0,
            'molecular_mass': randomize_mass(minE_molecular_mass),
        },
        'MinE': {
            'density': 1.0,
            'molecular_mass': minE_molecular_mass,
        },
        'MinDMinE': {
            'density': 1.0,
            'molecular_mass': randomize_mass(minE_molecular_mass),
        },
    }

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


test_convert_minE()
