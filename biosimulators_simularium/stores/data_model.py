"""
:Author: Alexander Patrie <apatrie@uchc.edu>
:Date: 2023-09-16
:Copyright: 2023, UConn Health
:License: MIT
"""


from typing import List, Dict, Tuple, Optional
from abc import ABC, abstractmethod
import sqlite3
import zarr


class DataStore(ABC):
    def __init__(self, store_id):
        self.store_id = store_id

    @abstractmethod
    def read(self, source):
        pass

    @abstractmethod
    def write(self, **params):
        pass

    @abstractmethod
    def analyze(self):
        pass


class ZarrDataStore(DataStore):
    def __init__(self, store_id: str):
        super().__init__(store_id)

    @abstractmethod
    def read(self, source):
        pass

    @abstractmethod
    def create_dataset(self, dataset_name, data_shape, chunk_shape):
        """Construct and return a dataset derived from an empty store root via `self.create_in_memory_root`.

                   Args:
                       dataset_name(:obj:`str`): Name by which to store the dataset in memory. Used for later io ops.
                       data_shape(:obj:`Tuple[int, int]`): Expected shape of the stored data. This is found typically in the form of
                           `(time_steps, data_dimensions)` for our use case.
                       chunk_shape(:obj:`Tuple[int, int]`): Shape by which to chunk the data for storage. This is found typically
                           in the form of `(chunk_size, data_dimensions)` for our use case.

                   Returns:
                       `obj`: a new instance of `root.zeros`
        """
        pass

    @abstractmethod
    def analyze(self):
        pass

    @staticmethod
    def create_in_memory_root() -> zarr.Group:
        """Create an in-memory data store root and return it.

            Returns:
                :obj:`zarr.Group` : an empty in-memory store root.
        """
        return zarr.group()

    @staticmethod
    def write(**params):
        """Write data to zarr dataset. Kwarg params as follows:

            Kwargs:
                dataset(:obj:`obj`): dataset in which to write data.
                index(:obj:`int`): index which describes the point of insertion.
                val(:obj:`Any`): value to write to the zarr dataset.


        """
        dataset = params.get('dataset')
        index = params.get('index')
        value = params.get('value')
        dataset[index] = value
        return dataset

    def write_to_disk(self, root: zarr.Group, store_name: Optional[str] = None) -> None:
        """Save the entire zarr group (`root`) to disk by the name of `store_name`.

            Args:
                root(:obj:`zarr.Group`): root which you are saving.
                store_name(:obj:`str`): Name by which to save the zarr group. Defaults to `self.store_id`.
        """
        store_name = store_name or self.store_id
        return zarr.save(store_name, root)


class ZarrSpatialDataStore(ZarrDataStore):
    def __init__(self, store_id: str):
        super().__init__(store_id)

    def read(self, source):
        pass

    def create_dataset(self,
                       dataset_name: str,
                       time_steps: int,
                       chunk_size: int,
                       data_dimensions):
        """Construct and return a dataset derived from an empty store root via `self.create_in_memory_root`.

            Args:
                dataset_name(:obj:`str`): Name by which to store the dataset in memory. Used for later io ops.
                time_steps(:obj:`int`): Number of timesteps which exist in the simulation.
                chunk_size(:obj:`int`): Shape for a particular data dimension.
                data_dimensions: Shape of another dimension (could be tuple?)

            Returns:
                `obj`: a new instance of `root.zeros`
        """
        root = self.create_in_memory_root()
        data_shape = (time_steps, data_dimensions)
        chunk_shape = (chunk_size, data_dimensions)
        return root.zeros(dataset_name, shape=data_shape, chunks=chunk_shape)

    def analyze(self):
        """Perform some sort of analytical operation on the zarr dataset. Currently not implemented."""
        raise NotImplementedError


class Database(DataStore):
    def __init__(self, db_name):
        super().__init__(db_name)

    @abstractmethod
    def read(self, source):
        pass

    @abstractmethod
    def write(self, val):
        pass

    @abstractmethod
    def analyze(self):
        pass


class RelationalDatabase(Database):
    def __init__(self, db_name, tables: List[str]):
        super().__init__(db_name)
        self.tables = tables

    @abstractmethod
    def read(self, tablename: str):
        pass

    @abstractmethod
    def write(self, data):
        pass

    @abstractmethod
    def analyze(self):
        pass


class DocumentDatabase(Database):
    def __init__(self, db_name, config: Dict):
        super().__init__(db_name)
        self.config = config

    @abstractmethod
    def read(self, **params):
        pass

    @abstractmethod
    def write(self, data, **params):
        pass

    def analyze(self):
        return self.config


class SqliteDatabase(RelationalDatabase):
    def __init__(self, db_name, tables):
        super().__init__(db_name, tables)
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

    def read(self, tablename):
        pass

    def write(self, data):
        pass

    def analyze(self):
        pass
