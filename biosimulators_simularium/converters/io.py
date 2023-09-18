from typing import Optional
from biosimulators_simularium.converters.data_model import CombineArchive, SmoldynDataConverter


__all__ = [
    'generate_new_simularium_file',
]


def generate_new_simularium_file(archive_rootpath: str, simularium_filename: Optional[str] = None) -> None:
    minE_archive = CombineArchive(rootpath=archive_rootpath, simularium_filename=simularium_filename)
    converter = SmoldynDataConverter(archive=minE_archive)
    return converter.generate_simularium_file(simularium_filename=simularium_filename)


