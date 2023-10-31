"""Data model for Objects and methods for calculating and solving for various particle values required for the
    `simulariumio` interface that are not explicitly exposed by Smoldyn. For example, particle radius will not be
    directly derived from a Smoldyn model file, but implicitly through the user-defined diffusion coefficient.
    The nomenclature used for objects will be relative the to universe according to Smoldyn. For clarity, the terms
    "molecule" and "agent" will be used interchangeably. Agent is because we have this term used in both smoldyn and
    simularium.

author: Alex Patrie <apatrie@uchc.edu>
date: 10/31/2023
license: MIT
"""


from typing import *
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from biosimulators_simularium.converters.utils import validate_model


class AgentAttribute:
    k: float

    def __init__(self):
        self.k = 1.380649 * 10**-23


class AgentRadius(AgentAttribute):
    def __init__(self, D: float, T: float, eta: float):
        super().__init__()


class AgentDiffusionCoefficient(AgentAttribute):
    """Object which calculates a molecule's diffusion coefficient given the required parameters of the
            Stokes-Einstein equation.
    """
    def __init__(self, T: float, eta: float, r: float):
        super().__init__()


class AgentEnvironment(AgentAttribute):
    def __init__(self,
                 viscosity: float,
                 temperature: float,
                 viscosity_units: str = 'cP',
                 temperature_units: str = 'K',
                 state: str = 'liquid'):
        super().__init__()
        self.state = state
        self.viscosity = {'value': viscosity, 'units': viscosity_units}
        self.temperature = {'value': temperature, 'units': temperature_units}

    def _calculate(self, **parameters):
        pass


class SmoldynAgent:
    def __init__(self,
                 name: str,
                 model_fp: str,
                 diffc_name: str,
                 density: Optional[float] = None,
                 molecular_mass: Optional[float] = None,
                 **environment_parameters):
        """
        Args:
            name:`str`: name of the molecule (for metadata)
            model_fp:`str`: fp to the model from which this agent originates.
            environment:`MoleculeEnvironment`: this provides the T and eta required to solve for radius
            diffc_name:`str`: name of the diffusion coefficient for the agent's `name` from the model file. This will
                be used as input for reading the model file for a coeff name.
            density:`Optional[float]`: density of the molecule. Defaults to `None`.
            molecular_mass:`Optional[float]`: molecular mass of the particle. Defaults to `None`.
            **environment_parameters:`kwargs`: parameters required for the `AgentEnvironment` constructor. The
                params are: viscosity(`float`) and temperature(`float`). The optional parameters are:
                viscosity_units(`str`): defaults to `'g/cm'`, temperature_units(`str`): defaults to `'K'`, and
                state(`str`): defaults to `'liquid'`.
        """
        self.name = name
        self.model_fp = model_fp
        self.environment = AgentEnvironment(**environment_parameters)
        self.density = density
        self.molecular_mass = molecular_mass
        self.D = self.read_diffc(diffc_name, model_fp)

    def calculate_r(self, **params) -> float:
        """Solve for an agent's radius given a diffusion coefficient. Diffusion coefficients could be read from
            smoldyn model files.

            Kwargs:
                **params: params to calculate r. they are `k`, `T`, and `eta`. Defaults to self values if not.

            Returns:
                `float`: radius of the agent to be used as an input parameter of `simulariumio.DisplayData` for the
                    given agent.
        """
        k = params.get('k') or self.environment.k
        T = params.get('T') or self.environment.temperature
        eta = params.get('eta') or self.environment.viscosity
        if self.environment.state == 'liquid':
            r = (k * T.get('value')) / (6 * np.pi * eta.get('value') * self.D)
            return r

    def read_diffc(self, difc_name: str, model_fp: Optional[str] = None) ->float:
        """Read in the diffusion coefficient value of a certain name from a given model filepath. Please note that this
            method assumes you have prior knowledge of the given diffusion coefficient. TODO: make this more dynamic
            such that the user does not have to know the diffusion coefficient name.

            Args:
                model_fp:`str`: path to the model file whose diffusion coefficients you want to read. Defaults to
                    `self.model_fp`.
                difc_name:`str`: name of the diffusion coefficient you want to read. Most likely written in the
                    model file as `define` or `diffc`.

            Return:
                `float`: The value of the given diffusion coefficient from the given model.
        """
        if model_fp is None:
            model_fp = self.model_fp
        validation = validate_model(model_fp)
        for item in validation:
            if isinstance(item, tuple):
                for datum in item:
                    if isinstance(datum, list):
                        for i, line in enumerate(datum):
                            if line.startswith('define') and difc_name in line:
                                print(line)
                            #print(self.D)




agent = SmoldynAgent(
    name='MinD_ATP(solution)',
    diffc_name='D_D',
    model_fp='biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023/model.txt',
    viscosity=8.1,
    temperature=310.0
)





