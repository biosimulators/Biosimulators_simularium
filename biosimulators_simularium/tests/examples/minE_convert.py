from biosimulators_simularium.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.utils.core import HEX_COLORS


test_archive_root = 'biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023'
test_simularium_filename = 'minE_binary_save'


archive = SmoldynCombineArchive(rootpath=test_archive_root, simularium_filename=test_simularium_filename)
converter = SmoldynDataConverter(archive=archive)


agents = [
    ('MinD_ATP(front)', 0.01, HEX_COLORS.get('blue')),
    ('MinE(solution)', 0.01, HEX_COLORS.get('orange')),
    ('MinD_ADP(solution)', 0.01, HEX_COLORS.get('green')),
    ('MinDMinE(front)', 0.01, HEX_COLORS.get('purple')),
    ('MinD_ATP(solution)', 0.01, HEX_COLORS.get('yellow'))
]


converter.generate_simularium_file(io_format='binary', agents=agents, box_size=10.0)
