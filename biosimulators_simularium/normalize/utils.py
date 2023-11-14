"""Utilities for preparing agent radii based on the the model file
    within `biosimulators_simularium.archives.data_model.SmoldynCombineArchive.

    PLEASE NOTE: These methods are currently specific to Smoldyn itself. Soon, the methods will be more
    generalized/reorganized to reflect the methodologies of other simulator tools.

author: Alex Patrie <apatrie@uchc.edu>
date: 11/01/2023
license: MIT
"""


import os
from typing import *
from dataclasses import dataclass
import numpy as np
from biosimulators_simularium.converters.utils import validate_model
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.converters.data_model import SmoldynDataConverter


@dataclass
class EnvironmentAttribute:
    value: Union[float, int]
    units: str
    name: Optional[str] = None


class Environment:
    def __init__(self, T: EnvironmentAttribute, eta: EnvironmentAttribute):
        self.T = T
        self.eta = eta


class Agent:
    def __init__(self, name: str, radius: float, color: str):
        self.name = name
        self.radius = radius
        self.color = color


def build_environment(T: EnvironmentAttribute, eta: EnvironmentAttribute):
    return Environment(T, eta)


def calculate_radius(
        T_env: float,
        eta_env: float,
        D_agent: float,
        ) -> float:
    """Assumes K for T_env, cP for eta_env, um^2/s for D_agent, and nm for output radius.

    Args:
        T_env:`float`:
        eta_env:
        D_agent:
    Returns:
        `float`: agent radius nm.
    """
    k = 1.380649 * 10 ** -23
    return (k * T_env) / (6 * np.pi * (eta_env * 0.001) * D_agent) * 10**9


def agent_radius_from_D(
        T_env: float,
        eta_env: float,
        D_agent: float,
        radius_units='nm',
        env_units: Dict[str, str] = None
        ) -> float:
    """

    Args:
        T_env:`float`:
        eta_env:
        D_agent:
        radius_units: units by which to standardize/measure the output radius. Defaults to `'nm'` as per simularium.
        env_units:`Dict[str, str]`: units by which env parameters are measured. Defaults to
            `{'T': 'K', 'eta': 'cP'}`
    Returns:
        `float`: agent radius in `radius_units` units.
    """
    if not env_units:
        env_units = {
            'T': 'K',
            'eta': 'cP'
        }
    k = 1.380649 * 10 ** -23
    if 'cP' in env_units.get('eta'):
        eta_env *= 0.001
    r = (k * T_env) / (6 * np.pi * eta_env * D_agent)
    if radius_units == 'nm':
        return r * 10**18
    else:
        return r


def agent_radius_from_physicality(m: float, rho: float, scaling_factor: float = 10**(-2)) -> float:
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


def generate_agent_radii_from_physicality(agent_masses: Dict[str, int], protein_density: int = 1350) -> Dict[str, float]:
    """Generate a dict of agent radii, indexed by agent name.

        Args:
            agent_masses:`Dict[str, int]`: a dict describing {agent name: agent mass}. Expects Daltons.
            protein_density:`Optional[int]`: Average density of proteins in the given agent. Defaults to `1350` g/m^2.

        Returns:
            `Dict[str, float]`: Dictionary of agent name: radii.
    """
    agent_radii = {}
    for k in agent_masses.keys():
        r = agent_radius_from_physicality(agent_masses[k], protein_density)
        agent_radii[k] = r
    return agent_radii


def generate_min_agent_radii(
        agent_masses: Dict[str, Union[float, int]],
        protein_density, agents: List[Tuple]
        ) -> Dict[str, float]:
    """Generate a dictionary of {agent name: agent radius} based on input parameters.

        Args:
            agent_masses:`Dict`: dictionary of {agent name: masses}.
            protein_density:`int`: density of proteins in agent. Defaults to average min protein density.
            agents:`List[Tuple]`: a list of (agent name, agent color)

        Returns:
            `Dict[str, float]`: A dict of agent names: agent radii.
    """
    agent_radii = generate_agent_radii_from_physicality(agent_masses, protein_density)
    agent_objects = []
    radii = {}
    for agent in agents:
        agent_type = agent[0]
        agent_color = agent[1]
        if 'MinD' and not 'MinE' in agent_type:
            sim_agent = Agent(agent_type, agent_radii.get('MinD'), agent_color)
            agent_objects.append(sim_agent)
        elif 'MinE' and not 'MinD' in agent_type:
            sim_agent = Agent(agent_type, agent_radii.get('MinE'), agent_color)
            agent_objects.append(sim_agent)
        elif 'MinE' and 'MinD' in agent_type:
            sim_agent = Agent(agent_type, agent_radii.get('MinDMinE'), agent_color)
            agent_objects.append(sim_agent)
    for obj in agent_objects:
        radii[obj.name] = obj.radius
    return radii


def generate_agent(name, radius, color):
    return (name, radius, color)


def generate_agents(agent_masses, protein_density, agents):
    all_agents = []
    agent_radii = generate_min_agent_radii(agent_masses, protein_density, agents)
    for agent in agents:
        a = generate_agent(agent[0], agent_radii[agent[0]], agent[1])
        all_agents.append(a)
    return all_agents


def get_model_diffusion_coefficients(model_fp: str) -> Dict[str, str]:
    """Read in a model file and return a dictionary of {agent name: agent difc value}.
        Please note that difcs can be defined in Smoldyn as an alias which serves as a reference to another
        data definition.

        Args:
            model_fp:`str`: path to the model file of which you want to extract the agent diffusion coefficient
                values from.
        Returns:
            `Dict[str, str]`: a dictionary of {model agent name: model agent value}
    """
    difcs = {}
    difc_defs = read_value_from_model(model_fp, 'difc')
    for difc in difc_defs:
        single_agent_difc = difc.split(' ')
        agent_name = single_agent_difc[1]
        difc_value = single_agent_difc[2]
        difcs[agent_name] = difc_value
    return difcs


def get_model(model_fp: str) -> List[str]:
    validation = validate_model(model_fp)
    for item in validation:
        if isinstance(item, tuple):
            for datum in item:
                if isinstance(datum, list):
                    return datum


def read_value_from_model(model_fp: str, term: str) -> List[str]:
    model = get_model(model_fp)
    values = []
    for line in model:
        if line.startswith(term):
            values.append(line)
    return values
