"""This is an example workflow using the v0.5.0 Simplified API."""


import os
from biosimulators_simularium.exec import generate_simularium_file


def test_convert_minE():
    working_dir = 'biosimulators_simularium/tests/fixtures/models'
    simularium_fn = os.path.join(working_dir, 'simplified-api-output')
    generate_simularium_file(working_dir, simularium_fn)
    try:
        assert os.path.exists(simularium_fn)
        print(f'{simularium_fn} has been successfully generated.')
    except:
        AssertionError('A simularium file could not be generated.')


def test_convert_minE_archive():
    omex_fp = 'biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023.omex'
    w



if __name__ == '__main__':
    test_convert_minE()
