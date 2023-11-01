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


def get_value_from_model(model_fp: str, term: str) -> List[str]:
    model = get_model(model_fp)
    values = []
    for line in model:
        if line.startswith(term):
            values.append(line)
    return values


def read_model_diffusion_coefficients(model_fp: str):
    return get_value_from_model(model_fp, 'difc')


def read_model_definitions(model_fp: str):
    return get_value_from_model(model_fp, 'define')


def calculate_agent_radius(D: float, environment: AgentEnvironment) -> float:
    T = environment.temperature.get('value')
    eta = environment.viscosity.get('value')
    if 'liquid' in environment.state:
        return (environment.k * T) / (6 * np.pi * eta * D)



archive = SmoldynCombineArchive(rootpath='biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023')

# 1. get difcs
difcs_from_model = read_model_diffusion_coefficients(archive.model_path)
# 2. get definitions
defines = read_model_definitions(archive.model_path)
# match #1[split(' ')[-1]] to #2.split(' ')[-1]

D = 2.5
environment = AgentEnvironment(viscosity=8.1, temperature=310.0)
D_D_radius = calculate_agent_radius(D, environment)
print(D_D_radius)
