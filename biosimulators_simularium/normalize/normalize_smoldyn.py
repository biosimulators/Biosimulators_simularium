"""Objects and methods for calculating and solving for various particle values required for the `simulariumio` interface
    that are not explicitly exposed by Smoldyn. For example, particle radius will not be directly derived from a
    Smoldyn model file, but implicitly through the user-defined diffusion coefficient. The nomenclature used for objects
    will be relative the to universe according to Smoldyn. For clarity, the terms "molecule" and "agent" will
    be used interchangeably. Agent is because we have this term used in both smoldyn and simularium.

author: Alex Patrie <apatrie@uchc.edu>
date: 10/30/2023
license: MIT
"""


from typing import *
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive, validate_model
from biosimulators_simularium.normalize.data_model import AgentEnvironment


"""
1. get 'difc' from model file lines (isinstance)
2. get 'define' lines.split(' ')
3. match #1[split(' ')[-1]] to #2.split(' ')[-1]
4. Given an agent, assign the name from #2[1] to the radius.
"""


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


def read_model_definitions(model_fp: str):
    return read_value_from_model(model_fp, 'define')


def parse_difcs_from_model_definitions(model_fp: str):
    definitions = read_model_definitions(model_fp)
    parsed_difcs = get_model_diffusion_coefficients(model_fp)
    difcs = list(parsed_difcs.values())
    for definition in definitions:
        definition = definition.split(' ')


def generate_environment(**environment_parameters):
    """Generate a new instance of `AgentEnvironment` given environment parameters. The output of this function
        should be used on the global scale in relation to the highest level/view of the simulation. All agents
        (currently) communicate with this Singleton.

        Keyword Args:
            state:`str`: state in which the environment exists. Choices are `liquid` or `gas`. This effects how
                the calculation of agent radii in the stokes-einstein equation occurs. Defaults to `liquid`.
            viscosity:`float`: viscosity of the simulation environment.
            temperature`float`: temperature of the simulation temperature (absolute temperature).
            viscosity_units:`Optional[str]`: units by which the viscosity is measured. Defaults to 'cP' (centipoise)

        Returns:
            `AgentEnvironment`: instance of an object which represents the simulation environment.
    """
    return AgentEnvironment(**environment_parameters)


def calculate_agent_radius(D: float, environment: AgentEnvironment) -> float:
    T = environment.temperature.get('value')
    eta = environment.viscosity.get('value')
    if 'liquid' in environment.state:
        return (environment.k * T) / (6 * np.pi * eta * D)



archive = SmoldynCombineArchive(rootpath='biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023')

# 1. get difcs
difcs_from_model = get_model_diffusion_coefficients(archive.model_path)
# 2. get definitions
definitions = read_model_definitions(archive.model_path)
# match #1[split(' ')[-1]] to #2.split(' ')[-1]
parsed_difcs = get_model_diffusion_coefficients(archive.model_path)
# create agent difcs
agent_difcs = parse_difcs_from_model_definitions(archive.model_path)


USE validatemodel TO PARSE AGENT NAMES FOR BIOSIMULARIUM!
