import os
from biosimulators_simularium.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.utils.core import HEX_COLORS


def main():
    archive_root = os.path.join(
        'biosimulators_simularium',
        'tests',
        'fixtures',
        'archives',
        'polymer_mid'
    )

    simularium_fname = 'polymer_mid_binary_save'

    archive = SmoldynCombineArchive(rootpath=archive_root, simularium_filename=simularium_fname)
    agents = [
        ('A', 2.0, HEX_COLORS.get('red'))
    ]

    converter = SmoldynDataConverter(archive)
    converter.generate_simularium_file(agents, scale=10.0, box_size=10.0, io_format='binary')


if __name__ == '__main__':
    main()

