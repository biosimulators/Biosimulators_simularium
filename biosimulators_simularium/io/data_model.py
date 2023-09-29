from typing import List
from abc import ABC, abstractmethod


class FileWriter(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _header(self, **header_items):
        pass

    @abstractmethod
    def _padding(self, n_pad: int):
        pass

    @abstractmethod
    def read(self, fp: str, data):
        pass

    @abstractmethod
    def write(self, fp: str, data):
        pass


class BinaryFileWriter(FileWriter):
    def __init__(self):
        super().__init__()

    def _header(self, **header_items):
        pass

    def _padding(self, n_pad: int):
        pass

    def read(self, fp: str, data: List):
        with open(fp, 'wb') as f:
            for datum in data:
                f.write(datum.encode())

    def write(self, fp: str, data: List):
        with open(fp, 'rb') as f:
            content = f.read().decode()
            val = list(content)
            return val
