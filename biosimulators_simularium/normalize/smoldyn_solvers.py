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


class AgentAttribute(ABC):
    k: float

    def __init__(self):
        self.k = 1.380649 * 10**-23

    @abstractmethod
    def _calculate(self, **parameters) -> float:
        """Abstract method for calculating the values for the relative child class. I.E: if class is radius,
            this method would take in D, T, eta, etc and reverse-engineer the radius.
        """
        pass


class AgentRadius(AgentAttribute):
    def __init__(self, D: float, ):
        super().__init__()


class AgentDiffusionCoefficient(AgentAttribute):
    """Object which calculates a molecule's diffusion coefficient given the required parameters of the
            Stokes-Einstein equation.
    """
    def __init__(self):
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


class Agent:
    def __init__(self,
                 name: str,
                 environment: AgentEnvironment,
                 r: Optional[float] = None,
                 density: Optional[float] = None,
                 D: Optional[float] = None):
        """

        Args:
            environment:`MoleculeEnvironment`: this provides the T and eta required to solve for radius
            r:
            density:
            D:
        """
        self.name = name
        self.environment = environment
        self.D = D
        self.r = self._set_radius(r)
        self.density = density

    def _set_radius(self, r: Optional[float] = None) -> float:
        try:
            self.D
        except:
            raise ValueError('A diffusion coefficient value must be passed to compute radius.')
        else:
            if not r:
                T = self.environment.temperature
                eta = self.environment.viscosity
                if self.environment.state == 'liquid':
                    r = (self.k * T) / (6 * np.pi * eta * self.D)
                    return r
            else:
                return r

