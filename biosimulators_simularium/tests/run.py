import os
from biosimulators_simularium.simulation_data import generate_molecule_coordinates, generate_output
from biosimulators_simularium.convert import generate_interpolated_mesh  # , generate_output_trajectory
from biosimulators_simularium.tests.test_simple import test_simple_execute


OUTPUT_DIR = 'Biosimulators_simularium/OUTPUT'
MIN_E_DIR = 'biosimulators_simularium/tests/fixtures/MinE'
CROWDING_DIR = 'biosimulators_simularium/tests/fixtures/crowding'
DOC_NAME = 'simulation'
USE_JSON = True


if __name__ == '__main__':
    #mol_output = generate_output(dir_fp=MIN_E_DIR)
    #mesh = generate_interpolated_mesh(mol_output=mol_output)
    test_simple_execute()
