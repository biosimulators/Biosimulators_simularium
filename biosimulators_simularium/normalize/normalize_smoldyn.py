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
from warnings import warn
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive, validate_model
from biosimulators_simularium.normalize.data_model import AgentEnvironment


"""
1. get 'difc' from model file lines (isinstance)
2. get 'define' lines.split(' ')
3. match #1[split(' ')[-1]] to #2.split(' ')[-1]
4. Given an agent, assign the name from #2[1] to the radius.
"""


@dataclass
class ModelAgent:
    """Because we assume the user of Smoldyn knows the diffusion coefficient of a given molecule/agent in the
        simulation, """
    name: str = None
    difc: Union[float, str] = None  # check if val passed is type(str)...if so require or get val.
    color: str = None


class ModelDepiction:
    def __init__(self, model_fp: str, agents: List[ModelAgent] = None, environment: AgentEnvironment = None):
        """Agents differ from molecules in the context of simulation: unlike molecules which are
            'living, breathing' entities that exist in the known physical world, Agents are ephemeral in relation
            to the duration of the simulation itself. Technically, the `environment` is not derived in the same
            scope, but rather integrating real-world theories and measurements into the simulation. Think of this
            as analogous to a written poem and a painting which depicts that poem. It is an interpretation of
            what the poem suggests. In this context, the poem is the suggestor (universe generator) and the
            painting is the interpreter. This is the case for the model(poem) and simulation(painting). Just
            as the painting is a depiction(implementation) of the poem in a particular medium, a simulation
            is a depiction of the model file. There exists an exception: consider the 1-1 relationship of
            poem--painting in this case. The ratio by which the relationship between model and simulation does not
            exist in that sense. You can experiment with the model (change the parameter values) and examine the model
            under various circumstances/with many other models. In this sense, the relationship is 1-n where n is the
            number of customizable parameters that exist in the model itself. Thus, this would be analogous to
            depicting a poem within another setting itself. I.e, say the poem was about a tall red tree. The painting is
            the tall red tree of a different shape etc.....in this case the tree has a length for example. Such is a
            model param. It is for these reasons that the name `ModelDepiction` was derived.


            Args:
                agents:`List[ModelAgent]`: list of model agents serving the depiction.
                environment:`AgentEnvironment`: instance of `AgentEnvironment` specific to this simulation.
        """
        self.model_fp = model_fp

        if not environment:
            warn('Warning: this Model Depiction was created without an environment and therefore must create one.')
        self.environment = environment
        self.agent_difcs = self._set_agent_difcs(model_fp)
        self.agents = self._set_agents(agents)

    def _set_agent_difcs(self, model_fp: str):
        agent_difcs = self.get_model_diffusion_coefficients(model_fp)
        for v in list(agent_difcs.values()):
            if not isinstance(v, float):
                warn(f'Warning: the value passed for the diffusion coefficient is an alias and must be defined/derived.')
        return agent_difcs

    def _set_agents(self, agents: List[ModelAgent] = None) -> Union[Dict[str, ModelAgent], List[ModelAgent]]:
        model_agents = {}
        if not agents:
            agents = list(self.agent_difcs.keys())
            for agent in agents:
                model_agent = ModelAgent(name=agent, difc=self.agent_difcs[agent])
                model_agents[model_agent.name] = model_agent
            return model_agents
        else:
            return agents

    @staticmethod
    def get_model(model_fp: str) -> List[str]:
        validation = validate_model(model_fp)
        for item in validation:
            if isinstance(item, tuple):
                for datum in item:
                    if isinstance(datum, list):
                        return datum

    def read_value_from_model(self, term: str, model_fp: str) -> List[str]:
        model = self.get_model(model_fp)
        values = []
        for line in model:
            if line.startswith(term):
                values.append(line)
        return values

    def get_model_diffusion_coefficients(self, model_fp: str) -> Dict[str, str]:
        """Read in a model file and return a dictionary of {agent name: agent difc value}.
            Please note that difcs can be defined in Smoldyn as an alias which serves as a reference to another
            data definition.

            Args:
                model_fp:`str`: path to the model file of which you want to extract the agent diffusion coefficient
                    values from.

            Returns:
                `Dict[str, str]`: a dictionary of {model agent name: model agent value}
        """
        difcs = {}
        difc_defs = self.read_value_from_model('difc', model_fp)
        for difc in difc_defs:
            single_agent_difc = difc.split(' ')
            agent_name = single_agent_difc[1]
            difc_value = single_agent_difc[2]
            difcs[agent_name] = difc_value
        return difcs

    def read_model_definitions(self, model_fp: Optional[str] = None):
        return self.read_value_from_model(model_fp or self.model_fp, 'define')

    def parse_difcs_from_model_definitions(self):
        model_fp = self.model_fp
        definitions = self.read_model_definitions(model_fp)
        parsed_difcs = self.get_model_diffusion_coefficients(model_fp)
        difcs = list(parsed_difcs.values())
        for definition in definitions:
            definition = definition.split(' ')

    def generate_environment(self, **environment_parameters):
        """Generate a new instance of `AgentEnvironment` given environment parameters. The output of this function
            should be used on the global scale in relation to the highest level/view of the simulation. All agents
            (currently) communicate with this Singleton. Sets the environment if not a value for this class.

            Keyword Args:
                state:`str`: state in which the environment exists. Choices are `liquid` or `gas`. This effects how
                    the calculation of agent radii in the stokes-einstein equation occurs. Defaults to `liquid`.
                viscosity:`float`: viscosity of the simulation environment.
                temperature`float`: temperature of the simulation temperature (absolute temperature).
                viscosity_units:`Optional[str]`: units by which the viscosity is measured. Defaults to 'cP' (centipoise)
                temperature_units:`Optional[str]`: units by which the temperature is measured. Defaults to 'K'.

            Returns:
                `AgentEnvironment`: instance of an object which represents the simulation environment.
        """
        env = AgentEnvironment(**environment_parameters)
        if self.environment is None:
            self.environment = env
        return env

    def calculate_agent_radius(
            self,
            D_agent: float,
            radius_units='nm',
            ) -> float:
        """

        Args:
            D_agent:
            radius_units: units by which to standardize/measure the output radius. Defaults to `'nm'` as per simularium.
        Returns:
            `float`: agent radius in `radius_units` units.
        """
        T_env = self.environment.temperature.get_temp()
        eta_env = self.environment.temperature.get_viscosity()
        k = 1.380649 * 10 ** -23
        if 'cP' in self.environment.viscosity.get('units'):
            eta_env *= 0.001
        r = (k * T_env) / (6 * np.pi * eta_env * D_agent)
        if radius_units == 'nm':
            return r * 10 ** 9
        else:
            return r

    @staticmethod
    def _check_units(*units):
        u = [*units]
        print(u)




def generate_depiction(model_fp: str):
    return ModelDepiction(model_fp=model_fp)


def generate_depiction_from_archive(archive: SmoldynCombineArchive):
    depiction = generate_depiction(archive.model_path)
    return depiction




# USE validatemodel TO PARSE AGENT NAMES FOR BIOSIMULARIUM!
