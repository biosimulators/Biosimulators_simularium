import os
from typing import *
from matplotlib.colors import cnames
from biosimulators_simularium.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive


def main():
    archive_root = os.path.join(
        'biosimulators_simularium',
        'tests',
        'fixtures',
        'archives',
        'polymer_mid'
    )

    simularium_fname = 'polymer_mid'

    archive = SmoldynCombineArchive(rootpath=archive_root, simularium_filename=simularium_fname)
    agents = [
        ('A', 2.0, cnames.get('red'))
    ]

    converter = SmoldynDataConverter(archive)
    converter.generate_simularium_file(agents, scale=10.0, box_size=10.0)


if __name__ == '__main__':
    main()

