from biosimulators_simularium.old_api.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.normalize.data_model import SmoldynAgentStage
from biosimulators_simularium.util.core import HEX_COLORS


test_archive_root = 'biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023'
test_simularium_filename = 'minE_Andrews_normalized_1'

agent_names = [
    'MinD_ATP(front)',
    'MinE(solution)',
    'MinD_ADP(solution)',
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

agent_colors = [
    HEX_COLORS.get('blue'),  # 0.01
    HEX_COLORS.get('orange'),  # 2.5
    HEX_COLORS.get('green'),  # 2.5
    HEX_COLORS.get('purple'),  # 0.01
    HEX_COLORS.get('yellow')  # 2.5
]

protein_density = 1350

archive = SmoldynCombineArchive(rootpath=test_archive_root, simularium_filename=test_simularium_filename)
stage = SmoldynAgentStage(
    molecular_masses=agent_masses,
    density=protein_density,
    agent_names=agent_names,
    agent_colors=agent_colors
)
converter = SmoldynDataConverter(archive=archive, agent_stage=stage)

converter.generate_simularium_file(io_format='binary', spatial_units='cm')

print('The converter has the following stage whose agents have gone into simularium: ')
for agent in converter.stage.agents:
    print(agent.name, agent.radius, agent.color)




