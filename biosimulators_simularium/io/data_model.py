"""
:Author: Alexander Patrie <apatrie@uchc.edu>
:Date: 2023-09-16
:Copyright: 2023, UConn Health
:License: MIT
"""


import os
from typing import List, Optional, Tuple, Union
from abc import ABC, abstractmethod
import zarr
import numpy as np


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


# noinspection PyMethodOverriding
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

    @staticmethod
    def convert_text_file_to_zarr(dtype_list: List[Tuple[str, str]],
                                  text_filename: str,
                                  target_varname: str,
                                  zarr_filename_to_save: str) -> None:
        """Convert the contents of a text file to a zarr formatted file using the mapped types from
            `dtype_list`.

            Args:
                  dtype_list:`List[Tuple[str, str]]`: A list of string tuples whose length are two. The expected
                    format is `(colname, dtype)`. For example:
                      dType = [('molecule', 'U20'), ('x', 'f8'), ('y', 'f8'), ('z', 'f8'), ('time_step', 'i4')]
                  text_filename: fp of the text file you are converting.
                  target_varname: Variable name to target for example: `'MinD_ATP(front)'`.
                  zarr_filename_to_save: fp of the newly converted zarr file.
        """
        data_list = []
        with open(text_filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5 and parts[0] == target_varname:
                    data_list.append((parts[0], float(parts[1]), float(parts[2]), float(parts[3]), int(parts[4])))
        data_array = np.array(data_list, dtype=dtype_list)
        z = zarr.array(data_array, chunks=(1000,))
        zarr.save(zarr_filename_to_save, z)

