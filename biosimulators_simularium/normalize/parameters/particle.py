"""Data Model for the construction of actors who serve as parameters within a simulation. PLEASE NOTE: Currently,
    only Smoldyn is supported, but more will be added as they are onboarded to BioSimulators.


author: Alex Patrie <apatrie@uchc.edu>
date: 10/28/2023
licence: MIT
"""


from typing import *
from dataclasses import dataclass
from abc import ABC, abstractmethod
from biosimulators_simularium.normalize.parameters.universe import AbsoluteTemperature




class Particle:
    density: Density
    r: Radius
    T: AbsoluteTemperature

