from typing import Tuple, Dict, List, Optional
from smoldyn import Simulation
import numpy as np
from biosimulators_simularium.validation import validate_model
# from biosimulators_simularium.utils import get_modelout_fp, standardize_model_output_fn


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


def get_species_names_from_model_file(model_fp: str) -> List[str]:
    sim = Simulation.fromFile(model_fp)
    species_names = [sim.getSpeciesName(n) for n in range(sim.count()['species'])]
    if 'empty' in species_names:
        species_names.remove('empty')
    return species_names


def generate_agent_params_for_minE(
        model_fp: str,
        base_molecular_mass: int,
        density: float
) -> Dict:
    params = {}
    names = get_species_names_from_model_file(model_fp)
    for name in names:
        if 'MinE' and not 'MinD' in name:
            mass = base_molecular_mass
        else:
            mass = randomize_mass(base_molecular_mass)
        params[name] = {
            'density': density,
            'molecular_mass': mass
        }
    return params


def generate_agent_params_from_model_file(
        model_fp: str,
        global_density: Optional[float] = None,
        basis_m: Optional[int] = None,
        **config
) -> Dict:
    """Generate a dictionary of agent parameters for the purpose of simulation input configuration which define the
        molecular mass and density inherent to a given agent based on a Smoldyn model file.

        Args:
            model_fp:`str`: path to a Smoldyn model file.
            global_density:`Optional[float]`: Density by which all agent densities are set. NOTE: this value is
              required if not passing explicit agent configs (**config). Defaults to `None`.
            basis_m:`Optional[int]`: Upper bound value of the molecular mass by which to set the basis for the
              randomization of agent molecular masses in the `randomize_mass` function which takes in a basis
              integer and returns a random integer between 0 and that number. NOTE: this value is required
              if not passing explicit agent configs (**config). Defaults to `None`.
        Keyword Args:
            <AGENT_NAME>:`dict`: an agent name (which should match that which is returned by
                smoldyn.Simulation.getSpeciesName()) as the definition (for example: `MinE=`) and a dictionary with
                `'molecular_mass'` and `'density'` as the keys.

    """
    params = {}
    names = get_species_names_from_model_file(model_fp)
    for name in names:
        agent_config = config.get(f'{name}')
        if agent_config:
            mass = agent_config['molecular_mass']
            density = agent_config['density']
        else:
            try:
                mass = randomize_mass(basis_m)
                density = global_density
            except:
                raise ValueError('You must pass either a config for a given agent or a base mol mass and global density.')
        params[name] = {
            'density': density,
            'molecular_mass': mass
        }
    return params


def randomize_mass(origin: float) -> int:
    return np.random.randint(int(origin))


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
    simulation = validate_model(model_fp)[2][0]
    if isinstance(simulation, Simulation):
        return simulation
    else:
        raise ValueError(f'{model_fp} is not valid.')


def run_model_file_simulation(model_fp: str) -> List[float]:
    """Run a Smoldyn simulation from a given `model_fp` and return a 2d List of
        molecule outputs with a shape of (n, 6) where n

        Please Note: This function will run the model file IN ADDITION to the `listmols` command.
            All commands (if present) will be run in the Smoldyn model file.

    """
    simulation = validated_model(model_fp)
    simulation.addOutputData('molecules')
    simulation.addCommand(cmd='listmols molecules', cmd_type='E')
    simulation.runSim()
    molecule_output_data = simulation.getOutputData('molecules')
    return molecule_output_data


def calculate_agent_radius(m: float, rho: float, scaling_factor: float = 10**(-2)) -> float:
    """Calculate the radius of an agent given its molecular mass and density. Please note: the molecular mass
        of MinE is 11000 Da with a protein density of 1.35 g/cm^3 (1350 kg/m^3).

        Args:
            m:`float`: the molecular mass of the given agent/particle (Daltons).
            rho:`float`: the density of the given agent/particle (kg/m^3).
            scaling_factor:`float`: tiny number by which to scale the output measurement. Defaults to
                `10**(-2)`, which effectively converts from nm to cm.

        Returns:
            `float`: radius of the given agent.
    """
    dalton_to_kg = 1.66053906660e-27  # Conversion factor from Daltons to kilograms
    m_kg = m * dalton_to_kg  # Convert mass to kilograms
    radius_m = ((3 * m_kg) / (4 * np.pi * rho)) ** (1 / 3)  # Calculate radius in meters
    radius_nm = radius_m * 1e9  # Convert radius to nanometers
    return radius_nm * scaling_factor


def calculate_agent_molecular_mass(n_amino_acids: int, amino_acid_mass: int = 110) -> float:
    """Calculate the molecular mass for an agent, given the amount of amino acids in the particular agent.
        For example, MinD in E.coli typically consists of around 270 amino acids. `amino_acid_mass` is meant to be
        the approximation of the average molecular weight of amino acids.

        Args:
            n_amino_acids:`int`: number of amino acids within the given agent.
            amino_acid_mass:`Optional[int]`: average molecular weight of amino acids. Defaults to `110`.

        Returns:
            `float`: the molecular mass of the given agent.
    """
    return float(n_amino_acids * amino_acid_mass)


def generate_agent_radii(agent_masses: Dict[str, int], protein_density: int = 1350) -> Dict[str, float]:
    """Generate a dict of agent radii, indexed by agent name.

        Args:
            agent_masses:`Dict[str, int]`: a dict describing {agent name: agent mass}. Expects Daltons.
            protein_density:`Optional[int]`: Average density of proteins in the given agent. Defaults to `1350` g/m^2.

        Returns:
            `Dict[str, float]`: Dictionary of agent name: radii.
    """
    agent_radii = {}
    for k in agent_masses.keys():
        r = calculate_agent_radius(agent_masses[k], protein_density)
        agent_radii[k] = r
    return agent_radii
