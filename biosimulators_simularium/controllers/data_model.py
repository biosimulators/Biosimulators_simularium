from abc import ABC
from biosimulators_simularium.stores.data_model import Database, SqliteDatabase, DocumentDatabase


class DBController:
    def __init__(self, db_name: str, con):
        raise NotImplementedError
