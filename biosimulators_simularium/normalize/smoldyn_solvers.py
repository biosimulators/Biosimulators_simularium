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


class MoleculeAttribute:
    k: float

    def __init__(self):
        self.k = 1.380649 * 10**-23


class MoleculeDiffusionCoefficient(MoleculeAttribute):
    """Object which calculates a molecule's diffusion coefficient given the required parameters of the
        Stokes-Einstein equation.
    """
    def __init__(self):
        super().__init__()


class MoleculeRadius(MoleculeAttribute):
    """Object which calculates a molecule's radius to serve as input for `simulariumio.DisplayData` relative to
        a given smoldyn simulation agent. The calculation for this value is based on the parameters which represent the
        molecular mass and density of the given agent. Can be used as an input parameter of the Stokes-Einstein
        equation.

        Methods(children):
            `radius_from_composition`: calculates the radius of the particle based on mol.mass and density.
            `radius_from_D`: calculates the radius of the particle by reverse-engineering the provided diffusion
                coefficient. Here, `T` is the absolute temp of the liquid during the simulation. Here, it is assumed that
                the radius was originally derived via the `radius_from_composition` by the Smoldyn modeler when
                creating the model itself.
    """

    def __init__(self, D: float, T: float, eta: float):
        """Instance which takes in a given diffusion coefficient from the smoldyn model file through validation
            and reverse-engineers the radius.

            Args:
                D:`float`: The diffusion coefficient as described by the field `difc` in the Smoldyn model file.
            Params:
                value:`float`: The particle's radius to use as the `radius` field within `simulariumio.DisplayData`.
        """
        super().__init__()
        self.value = self._set_radius(D)

    def _set_radius(self, D, T, eta):
        return


class MoleculeEnvironment(MoleculeAttribute):
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


class Molecule:
    def __init__(self,
                 name: str,
                 environment: MoleculeEnvironment,
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

