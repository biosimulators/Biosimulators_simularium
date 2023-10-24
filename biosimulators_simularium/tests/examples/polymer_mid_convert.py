import os
from typing import *
from biosimulators_simularium.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.utils.core import ContentFormat
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.archives.utils import build_archive as build


def main():
    archive_root = os.path.join(
        'biosimulators_simularium',
        'tests',
        'fixtures',
        'archives',
        'polymer_mid_convert'
    )
    make_model_master = True
    archive_content = [
        (os.path.join(archive_root, 'model.txt'), ContentFormat.SMOLDYN.value, make_model_master)
    ]

    if not os.path.exists(archive_root):
        build_archive(archive_root, archive_content)

    archive = SmoldynCombineArchive(rootpath=archive_root)
    converter = SmoldynDataConverter(archive)
    agents = NOW MAKE AGENTS IN THE FORM OF AGENT NAME, RADIUS, AND COLOR!
    generate_simularium(converter, agents)


def build_archive(archive_rootpath: str, content: List[Tuple[str, str, bool]]):
    """
        Args:
            archive_path – str: path at which you will save the newly generated combine archive.
            content – List[Tuple[str, str, bool]]: a list of content by which to create new instances of
                CombineArchiveContent. The expected data in the tuple are: (location, format, master).
                See biosimulators_simularium.archives.data_model.CombineArchiveContent.
    """
    return build(archive_rootpath, content)


def generate_simularium(converter: SmoldynDataConverter, agents: List[Tuple[str, float, str]]):
    """

    Args:
        converter: `SmoldynDataConverter`
        agents: List of tuples in the shape of (agent name, agent radius, agent hexcolor)

    """
    return converter.generate_simularium_file(agents)


if __name__ == '__main__':
    main()

