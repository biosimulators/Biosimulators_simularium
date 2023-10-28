"""Data Model for the construction of actors who serve as parameters within a simulation. PLEASE NOTE: Currently,
    only Smoldyn is supported, but more will be added as they are onboarded to BioSimulators.

    Here is housed all params not related to particles, but rather env (cytoplasmic env)

author: Alex Patrie <apatrie@uchc.edu>
date: 10/28/2023
licence: MIT
"""


from typing import *
from dataclasses import dataclass
from abc import ABC, abstractmethod
from biosimulators_simularium.normalize.parameters.data_model import Variable, Constant, Temperature, Environment



class Viscosity:
    pass


class AbsoluteTemperature(Temperature):
    def __init__(self, value: float, unit: str, environment: Environment):
        super().__init__(value, unit)
        self.environment = environment
