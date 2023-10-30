"""Data Model for the construction of actors who serve as parameters within a simulation. PLEASE NOTE: Currently,
    only Smoldyn is supported, but more will be added as they are onboarded to BioSimulators. In data_model, there are no
    declarations of logic, but rather the definition of objects and their parameters.


author: Alex Patrie <apatrie@uchc.edu>
date: 10/28/2023
licence: MIT
"""


from typing import *
from dataclasses import dataclass
from abc import ABC, abstractmethod
import numpy as np


class Variable(ABC):
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit


class Constant(ABC):
    def __init__(self, value: float, name: str = None):
        self.value = value
        if name is not None:
            self.name = name


@dataclass
class Environment:
    name: str
    conditions: List


@dataclass
class BoltzmannConstant:
    k: float = 1.380649 * 10 ** -23


@dataclass
class TemperatureValue:
    value: float


@dataclass
class TemperatureUnit:
    value: str


class Temperature:
    def __init__(self, value: float, unit: str):
        self.value = TemperatureValue(value)
        self.unit = TemperatureUnit(unit.upper())


@dataclass
class Density:  # aka: rho
    value: float
    unit: str


@dataclass
class Radius:
    value: float
    unit: str


@dataclass
class DiffusionCoefficient:
    def __init__(self, value: float):
        """Abstract base class for solving diffusion coefficients based on the given medium ('gas', 'liquid')

            Args:
                medium:`str`: medium for which a given particle's diffusion coefficient is being calculated.
        """
        self.value = value


@dataclass
class MeasurementUnit:
    value: str
    measurement_type: str

