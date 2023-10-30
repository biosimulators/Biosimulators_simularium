"""Data Model for the construction of actors who serve as parameters within a simulation. PLEASE NOTE: Currently,
    only Smoldyn is supported, but more will be added as they are onboarded to BioSimulators.

    Here is housed all params not related to particles, but rather env (cytoplasmic env)

author: Alex Patrie <apatrie@uchc.edu>
date: 10/28/2023
licence: MIT
"""

from biosimulators_simularium.normalize.verification.parameters.data_model import Temperature


class Viscosity:
    pass


class AbsoluteTemperature(Temperature):
    def __init__(self, value: float, units: str):
        """The most commonly used units will be Kelvin (K) or Celsius (C)"""
        super().__init__(value, units)
        self.C = self._celsius()
        self.K = self._kelvin()

    def _celsius(self):
        units = self.unit.value
        if "C" in units:
            return self.value
        elif "K" in units:
            return self.value + 273.15

    def _kelvin(self):
        units = self.unit.value
        if "K" in units:
            return self.value
        elif "C" in units:
            return self.value - 273.15


class Gravity:
    value: float
    units: str
