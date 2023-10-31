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
                 viscosity_units: str = 'g/cm',
                 temperature_units: str = 'K',
                 state: str = 'liquid'):
        super().__init__()
        self.state = state
        self.viscosity = {'value': viscosity, 'units': viscosity_units}
        self.temperature = {'value': temperature, 'units': temperature_units}

    def _calculate(self, **parameters):
        pass


class Agent:
    """PLEASE NOTE: At a minimum, at least D or r must be passed."""
    def __init__(self,
                 name: str,
                 environment: AgentEnvironment,
                 D: Optional[float] = None,
                 r: Optional[float] = None,
                 density: Optional[float] = None,
                 molecular_mass: Optional[float] = None):
        """

        Args:
            name:`str`: name of the molecule (for metadata)
            environment:`MoleculeEnvironment`: this provides the T and eta required to solve for radius
            r:`Optional[float]`: radius of the given particle as per simulariumio. If `None` is passed, the default
                value for this field is derived from the given diffusion coefficient (D).
            density:
            D:
        """
        self.name = name
        self.environment = environment
        self.D = D
        self.r = self._set_radius(r)
        self.density = density
        self.molecular_mass = molecular_mass

    def _set_radius(self, r: Optional[float] = None) -> float:
        try:
            assert self.D is not None
        except AssertionError:
            raise ValueError('A diffusion coefficient value must be passed to compute radius.')
        else:
            if not r:
                T = self.environment.temperature
                eta = self.environment.viscosity
                if self.environment.state == 'liquid':
                    r = (self.environment.k * T.get('value')) / (6 * np.pi * eta.get('value') * self.D)
                    return r
            else:
                return r

