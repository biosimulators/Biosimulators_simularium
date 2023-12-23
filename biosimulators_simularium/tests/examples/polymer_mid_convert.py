import os
from biosimulators_simularium.old_api.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.util.core import HEX_COLORS


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
    '''if os.path.exists(archive.model_output_filename):
        os.remove(archive.model_output_filename)
    if os.path.exists(os.path.join(archive.rootpath, archive.simularium_filename)):
        os.remove(archive.simularium_filename)
'''
    agents = [
        ('A(solution)', 0.1, HEX_COLORS.get('red'))
    ]

    converter = SmoldynDataConverter(archive)
    converter.generate_simularium_file(scale=10.0, box_size=20.0, io_format='binary')


if __name__ == '__main__':
    main()

