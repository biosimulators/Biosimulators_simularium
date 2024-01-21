import os
from biosimulators_simularium.simulation_data import generate_molecule_coordinates, generate_output
from biosimulators_simularium.convert import generate_interpolated_mesh  # , generate_output_trajectory


MIN_E_DIR = 'biosimulators_simularium/tests/fixtures/MinE'
CROWDING_DIR = 'biosimulators_simularium/tests/fixtures/crowding'
DOC_NAME = 'simulation'
USE_JSON = True

mol_output = generate_output(dir_fp=MIN_E_DIR)
mesh = generate_interpolated_mesh(mol_output=mol_output)
print(mesh.point_normals)
