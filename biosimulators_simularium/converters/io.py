from typing import Optional
from biosimulators_simularium.converters.data_model import CombineArchive, SmoldynDataConverter


__all__ = [
    'generate_new_simularium_file',
]


def generate_new_simularium_file(archive_rootpath: str, simularium_filename: Optional[str] = None) -> None:
    """Generate a new `.simularium` file for the Smoldyn `model.txt` in a given COMBINE/OMEX archive.

        Args:
            archive_rootpath(:obj:`str`): path of the root relative to your COMBINE/OMEX archive.
            simularium_filename(:obj:`str`): `Optional`: desired path by which to save the new .simularium file. If `None` is passed, file will be stored by a generic name in the archive root.

        Returns:
            `None`
    """
    minE_archive = CombineArchive(rootpath=archive_rootpath, simularium_filename=simularium_filename)
    converter = SmoldynDataConverter(archive=minE_archive)
    return converter.generate_simularium_file(simularium_filename=simularium_filename)


