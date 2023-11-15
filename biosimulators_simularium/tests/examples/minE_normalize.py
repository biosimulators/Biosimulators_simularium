from biosimulators_simularium.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.normalize.data_model import SmoldynAgentStage


test_archive_root = 'biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023'
test_simularium_filename = 'minE_corrected_units_10'


archive = SmoldynCombineArchive(rootpath=test_archive_root, simularium_filename=test_simularium_filename)
converter = SmoldynDataConverter(archive=archive)

agent_names = [
    'MinD_ATP(front)',
    'MinE(solution)',
    'MinD_ADP(solution)'
    'MinDMinE(front)',
    'MinD_ATP(solution)'
]

agent_masses = [
    29700,
    9680,
    29700,
    29700 + 9680,
    29700
]

protein_density = 1350
