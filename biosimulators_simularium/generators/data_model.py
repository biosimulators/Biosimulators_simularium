from typing import List, Tuple
from dataclasses import dataclass
from smoldyn import Simulation as smoldynSim


@dataclass
class ModelValidation:
    errors: List[List[str]]
    warnings: List[str]
    simulation: smoldynSim
    config: List[str]

    def __init__(self, validation: Tuple[List[List[str]], List, Tuple[smoldynSim, List[str]]]):
        self.errors = validation[0]
        self.warnings = validation[1]
        self.simulation = validation[2][0]
        self.config = validation[2][1]


