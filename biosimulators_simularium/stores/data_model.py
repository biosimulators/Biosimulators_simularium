from typing import List, Dict
from abc import ABC, abstractmethod
import sqlite3


class Database(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def read(self, **params):
        pass

    @abstractmethod
    def write(self, **params):
        pass

    @abstractmethod
    def analyze(self):
        pass


class RelationalDatabase(Database):
    def __init__(self, name: str, tables: List[str]):
        super().__init__()
        pass

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
    def __init__(self, config: Dict):
        super().__init__()
        pass

    @abstractmethod
    def read(self, **params):
        pass

    @abstractmethod
    def write(self, data, **params):
        pass

    def analyze(self):
        return self.config


class SqliteDatabase(RelationalDatabase):
    def __init__(self, name, tables):
        super().__init__(name, tables)
        self.conn = sqlite3.connect(name)
        self.cur = self.conn.cursor()

    def read(self, tablename):
        pass

    def write(self, data):
        pass

    def analyze(self):
        pass
