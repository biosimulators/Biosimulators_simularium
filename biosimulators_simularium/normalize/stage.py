from abc import ABC, abstractmethod
from typing import *
from dataclasses import dataclass
import numpy as np


class AgentStage(ABC):
    """Abstract base class for preparing the output of specific simulators to be the input for the
        `simulariumio` API. The class handles the generation of agent radii based on the logic of the
        given simulator. For example, the `solve_radius` method should be specific to the logic and universe
        of the given simulator: ReDDY can solve agent radius based on diffusion coefficient, Smoldyn cannot and
        must solve given molecular mass and density.

        Attributes:
            simulator:`str`: name of the simulator tool given.
    """
    simulator: str

    def __init__(self):
        pass

    @abstractmethod
    def stage_agents(self, **agent_params) -> List[Tuple[str, float, str]]:
        """Abstract method for staging agents in to become input for
            `biosimulators_simularium.converters.data_model.SmoldynDataConverter.generate_simularium_file()`.

            Returns:
                `List[Tuple[str, float, str]]`: Tuple representation of Agents in the form of a list. The expected
                    shape of the agent tuple is: `(agent name, agent radius, agent color)`.
        """
        pass

    @abstractmethod
    def solve_agent_radius(self, **agent_params) -> float:
        """Abstract method for solving for the radius of a given agent based on the simulator tool. For example,
            if this were `SmoldynAgentStage`, this method would solve for agent radius based on its molecular
            mass and density. PLEASE NOTE: the user should be aware of the desired output spatial units and account
            for the conversion of units in the output of this method, if applicable.

            Returns:
                `float`: radius of the given agent, scaled to the correct units.
        """
        pass


class AgentAttribute(ABC):
    def __init__(self, value: Any, units: str, name: Optional[str] = None):
        self.units = units
        self.value = value
        self.name = name

    @abstractmethod
    def convert_units(self, desired_units: str) -> Tuple[float, str]:
        """Abstract method for converting `self.units` to another `desired_unit`. For example,
            convert Daltons to Kg in the `MolecularMassAttribute` implementation class.

            Returns:
                `Tuple[float, str]`: A tuple representation of (converted value, desired_units).
        """
        pass


class MolecularMassAttribute(AgentAttribute):
    def __init__(self, value: float, units: str):
        self.value = value
        self.units = units
        self.name = 'molecular_mass'

    def convert_units(self, desired_units: str) -> Tuple[float, str]:
        if 'daltons' in self.units.lower():
            pass


class SmoldynAgentStage(AgentStage):
    """Smoldyn-specific implementation of an `AgentStage` instance."""
    def __init__(self):
        super().__init__()
        self.simulator = 'smoldyn'

    def stage_agents(self, **agent_params) -> List[Tuple[str, float, str]]:
        pass

    def solve_agent_radius(self, scaling_factor: Optional[float] = 10**(-2), **agent_params) -> float:
        """Implementation of the parent abstract radius solver.

            Keyword Args:
                molecular_mass:`float`: molecular mass of the given agent in Daltons. Gets converted to Kg.
                density:`float`: density of the given in agent in kg/m^3.

            Args:
                scaling_factor:`float`: tiny number by which to scale the output measurement. Defaults to
                    `10**(-2)`, which (for Smoldyn), effectively converts from nm to cm.

            Returns:
                `float`: radius of the given agent derived from the provided `**agent_params` kwargs and scaling.
        """
        dalton_to_kg = 1.66053906660e-27  # Conversion factor from Daltons to kilograms
        try:
            m = agent_params.get('molecular_mass')
            rho = agent_params.get('density')
        except KeyError:
            raise "You must input valid keyword arguments (molecular_mass, density, and scaling_factor)."

        m_kg = m * dalton_to_kg  # Convert mass to kilograms
        radius_m = ((3 * m_kg) / (4 * np.pi * rho)) ** (1 / 3)  # Calculate radius in meters
        radius_nm = radius_m * 1e9  # Convert radius to nanometers
        return radius_nm * scaling_factor

