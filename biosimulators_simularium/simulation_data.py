from typing import Tuple
from smoldyn import Simulation
import numpy as np
from biosimulators_simularium.validation import validate_model


def generate_molecules(model_fp: str, duration: int) -> np.ndarray:
    """Run the simulation model found at `model_fp` and return a numpy array of the `listmols` command output.

        Args:
            model_fp:`str`
            duration:`int`: duration by which to run the simulation.

    """
    simulation = Simulation.fromFile(model_fp)
    simulation.addOutputData('molecules')
    simulation.addCommand(cmd='listmols molecules', cmd_type='E')
    simulation.run(duration, simulation.dt)
    return np.array(simulation.getOutputData('molecules'))


def generate_molecule_coordinates(model_fp: str, duration: int) -> np.ndarray:
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
            A 1d scalar array of the chosen axis.
    """
    return np.array([agent_coord[axis] for agent_coord in agent_coordinates])


def validated_model(model_fp: str) -> Simulation:
    try:
        return validate_model(model_fp)[2][0]
    except:
        raise ValueError(f"The filepath: {model_fp} is not a valid Smoldyn model file.")


def run_model_file_simulation(model_fp: str) -> Tuple[Simulation, np.ndarray]:
    """Run a Smoldyn simulation from a given `model_fp` and return a Tuple consisting of
        (The simulation generated from the passed model fp, Molecule Outputs).

        Please Note: This function will run the model file IN ADDITION to the `listmols` command.
            All commands (if present) will be run in the Smoldyn model file.

    """
    simulation = validated_model(model_fp)
    simulation.addOutputData('molecules')
    simulation.addCommand(cmd='listmols molecules', cmd_type='E')
    simulation.runSim()
    molecules = np.array(simulation.getOutputData('molecules'))
    return simulation, molecules
