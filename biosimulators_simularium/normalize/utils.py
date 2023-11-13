"""Utilities for preparing agent radii based on the the model file
    within `biosimulators_simularium.archives.data_model.SmoldynCombineArchive

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


def agent_radius_from_physicality(m: float, rho: float) -> float:
    """Calculate the radius of an agent given its molecular mass and density.

        Args:
            m:`float`: the molecular mass of the given agent/particle.
            rho:`float`: the density of the given agent/particle.

        Returns:
            `float`: radius of the given agent.
    """
    return ((3 * m) / (4 * np.pi * rho)) ** (1/3)


def calculate_minE_molecular_mass(amino_acid_mass_sequence: List[float], water_mol_mass: List[float], n_amino_acids: int = None) -> float:
    mass_total = 0.0
    for mass in amino_acid_mass_sequence:
        for m in water_mol_mass:
            mass_total += mass - m
    return mass_total


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


'''MODEL_DIFCS = {
    'D_D':  2.5,
    'D_E':  2.5,
    'D_d':  0.01,
    'D_de':  0.01,
}

# env parameters
T = 310.0
k = 1.380649 * 10**-23
eta = 8.1

difc_radii_values = {}
for difc in MODEL_DIFCS.keys():
    radius = calculate_agent_radius(k, T, eta, MODEL_DIFCS[difc])
    difc_radii_values[difc] = radius


archive = SmoldynCombineArchive(rootpath='biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023')
model_coeffs = get_model_diffusion_coefficients(archive.model_path)
print(model_coeffs)
print(difc_radii_values)

for key in model_coeffs:
    if model_coeffs[key] in difc_radii_values:
        model_coeffs[key] = difc_radii_values[model_coeffs[key]]

'''






