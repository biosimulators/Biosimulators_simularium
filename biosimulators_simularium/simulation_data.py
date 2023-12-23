from smoldyn import Simulation
import numpy as np
from biosimulators_simularium.validation import validate_model


def generate_molecules(model_fp: str, duration: int):
    simulation = Simulation.fromFile(model_fp)
    simulation.addOutputData('molecules')
    simulation.addCommand(cmd='listmols molecules', cmd_type='E')
    simulation.run(duration, simulation.dt)
    return simulation.getOutputData('molecules')


def generate_molecule_coordinates(model_fp: str, duration: int):
    data = generate_molecules(model_fp, duration)
    mol_coords = []
    for mol in data:
        mol_coords.append(mol[2:5])
    return np.array(mol_coords)


def get_axis(agent_coordinates: list[list[float]], axis: int) -> np.ndarray:
    """Return a 1d list of scalar `axis` values from the given `agent_coordinates`.

        Args:
            agent_coordinates:`str`: A list of lists where each inner list consists of [x, y, z].
            axis:`int`: the index of the desired axis given the syntax x, y, z. Pass `0` for x,
            `1` for y, and `2` for z.

        Returns:
            A 1d list of axis scalars
    """
    return np.array([agent_coord[axis] for agent_coord in agent_coordinates])


def run_model_file_simulation(model_fp: str) -> None:
    return validate_model(model_fp)[2][0].runSim()
