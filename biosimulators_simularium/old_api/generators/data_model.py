from typing import List
from dataclasses import dataclass
from abc import abstractmethod, ABC


class BiosimulatorDataGenerator(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def generate(self):
        pass


@dataclass
class GeneratedData:
    meta_id: str
    metadata: List
    length: int
    size: int
    header: str
    tag: bytearray

