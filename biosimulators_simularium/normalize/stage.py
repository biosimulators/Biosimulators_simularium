from abc import ABC, abstractmethod
from typing import *
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


class SmoldynAgentStage(AgentStage):
    """Smoldyn-specific implementation of an `AgentStage` instance."""
    def __init__(self):
        super().__init__()
        self.simulator = 'smoldyn'

