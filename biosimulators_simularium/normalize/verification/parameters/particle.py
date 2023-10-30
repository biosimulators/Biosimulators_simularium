"""Data Model for the construction of actors who serve as parameters within a simulation. PLEASE NOTE: Currently,
    only Smoldyn is supported, but more will be added as they are onboarded to BioSimulators.


author: Alex Patrie <apatrie@uchc.edu>
date: 10/28/2023
licence: MIT
"""

from biosimulators_simularium.normalize.verification.parameters.data_model import (
    Density,
    Radius,
    Temperature,
    DiffusionCoefficient
)


class Particle:
    rho: Density
    r: Radius
    T: Temperature
    D: DiffusionCoefficient

