import os
from typing import List, Optional, Tuple, Union
from abc import ABC, abstractmethod
import zarr


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
    def read(self, fp: str):
        pass

    @abstractmethod
    def write(self, fp: str, data):
        pass


class BinaryFileWriter(FileWriter):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def _header(self, **header_items):
        pass

    def _padding(self, n_pad: int):
        pass

    def read(self, fp: str):
        with open(fp, 'wb') as f:
            for datum in self.data:
                f.write(datum.encode())

    def write(self, fp: str, data: List):
        with open(fp, 'rb') as f:
            content = f.read().decode()
            val = list(content)
            return val


class ZarrWriter(FileWriter):
    def __init__(self):
        super().__init__()

    def _header(self, **header_items):
        pass

    def _padding(self, n_pad: int):
        pass

    def read(self, fp: str):
        return zarr.open(fp, mode='r') if os.path.exists(fp) else None

    def write(
            self,
            fp: str,
            data,
            chunks: Tuple[int, int],
            shape: Union[Tuple[int, int], Tuple[int, int, int]],
            dtype: str,
            open_mode: str = 'w'):
        return zarr.open(fp, mode=open_mode, shape=shape, chunks=chunks, dtype=dtype)

    @staticmethod
    def get_slice(arr: zarr.Array, xA: int, xZ: int, yA: int, yZ: int):
        return arr[xA:xZ, yA:yZ]
