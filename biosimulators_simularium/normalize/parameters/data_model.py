"""Data Model for the construction of actors who serve as parameters within a simulation. PLEASE NOTE: Currently,
    only Smoldyn is supported, but more will be added as they are onboarded to BioSimulators.


author: Alex Patrie <apatrie@uchc.edu>
date: 10/28/2023
licence: MIT
"""


from typing import *
from dataclasses import dataclass
from abc import ABC, abstractmethod


class Variable(ABC):
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit


class Constant(ABC):
    def __init__(self, value: float):
        self.value = value


@dataclass
class Environment:
    name: str
    conditions: List


@dataclass
class TemperatureNumber:
    value: float


@dataclass
class TemperatureUnit:
    value: str


class Temperature(Variable):
    def __init__(self, value: float, unit: str):
        super().__init__(value, unit)
        self.number = TemperatureNumber(value)
        self.unit = TemperatureUnit(unit)


@dataclass
class Density:  # aka: rho
    value: float
    unit: str


@dataclass
class Radius:
    value: float
    unit: str
