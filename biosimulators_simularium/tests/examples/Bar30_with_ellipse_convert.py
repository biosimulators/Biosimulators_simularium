"""Testing `model.txt` to simularium ONLY"""


from biosimulators_simularium.old_api.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.util.core import HEX_COLORS


test_archive_root = 'biosimulators_simularium/tests/fixtures/archives/Bar30_with_ellipse'
test_model_filename = 'Bar30'


archive = SmoldynCombineArchive(
    rootpath=test_archive_root,
    model_filename=test_model_filename,
    simularium_filename=test_model_filename
)

converter = SmoldynDataConverter(archive=archive)


agents = [
    ('alpha(fsoln)', 0.05, HEX_COLORS.get('gray')),
    ('alpha(up)', 0.0, HEX_COLORS.get('orange')),
    ('Bar1(all)', 0.05, HEX_COLORS.get('green')),
    ('GPCR(up)', 0.08, HEX_COLORS.get('blue')),
    ('GPCRalpha(up)', 0.08, HEX_COLORS.get('red'))
]


converter.generate_simularium_file(io_format='binary', agents=agents, box_size=10.0)


