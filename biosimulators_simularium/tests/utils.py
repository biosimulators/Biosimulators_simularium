from typing import *
from biosimulators_simularium.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.archives.utils import build_archive as build


class ConversionTester:
    def __init__(self, archive_root: str, archive_content: List[Tuple[str, str, bool]]):
        self._build_archive(archive_root, archive_content)
        archive = SmoldynCombineArchive(rootpath=archive_root)
        converter = SmoldynDataConverter(archive)
        self._generate_simularium(converter)

    @staticmethod
    def _build_archive(archive_rootpath: str, content: List[Tuple[str, str, bool]]):
        """
            Args:
                archive_path – str: path at which you will save the newly generated combine archive.
                content – List[Tuple[str, str, bool]]: a list of content by which to create new instances of
                    CombineArchiveContent. The expected data in the tuple are: (location, format, master).
                    See biosimulators_simularium.archives.data_model.CombineArchiveContent.
        """
        try:
            return build(archive_rootpath, content)
        except Exception:
            raise Exception('Could not build a new archive')

    @staticmethod
    def _generate_simularium(converter: SmoldynDataConverter, agents: List[Tuple[str, float, str]]):
        """

        Args:
            converter: `SmoldynDataConverter`
            agents: List of tuples in the shape of (agent name, agent radius, agent hexcolor)

        """
        try:
            return converter.generate_simularium_file(agents)
        except Exception:
            raise Exception('Could not generate simularium file.')
