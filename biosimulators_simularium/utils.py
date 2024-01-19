"""Some of the functions are from smoldyn.biosimulators.combine"""


from typing import Dict
from smoldyn import Simulation


def generate_agent_parameters(sim: Simulation) -> Dict[str, Dict]:
    species_names = sorted(list([sim.getSpeciesName(n) for n in range(sim.count()['species'])]))
    if 'empty' in species_names:
        species_names.remove('empty')

    agent_params = {
        spec_name: {}
        for spec_name in species_names
    }
    return agent_params
