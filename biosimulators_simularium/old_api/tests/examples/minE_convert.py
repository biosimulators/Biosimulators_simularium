from biosimulators_simularium.old_api.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.util.core import HEX_COLORS
from biosimulators_simularium.normalize.utils import generate_min_agent_radii, generate_agents


test_archive_root = 'biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023'
test_simularium_filename = 'minE_corrected_units_10'


archive = SmoldynCombineArchive(rootpath=test_archive_root, simularium_filename=test_simularium_filename)
converter = SmoldynDataConverter(archive=archive)

# env parameters
T = 310.0
eta = 8.1


agents = [
    ('MinD_ATP(front)', HEX_COLORS.get('blue')), # 0.01
    ('MinE(solution)', HEX_COLORS.get('orange')), # 2.5
    ('MinD_ADP(solution)', HEX_COLORS.get('green')), # 2.5
    ('MinDMinE(front)', HEX_COLORS.get('purple')), # 0.01
    ('MinD_ATP(solution)', HEX_COLORS.get('yellow')) # 2.5
] # normally 0.01 radius

agent_masses = {
    'MinD': 29700,
    'MinE': 9680,
    'MinDMinE': 29700 + 9680
}
protein_density = 1350
agent_radii = generate_min_agent_radii(agent_masses, protein_density, agents)
all_agents = generate_agents(agent_masses, protein_density, agents)
print(all_agents)

converter.generate_simularium_file(io_format='binary', agents=all_agents, box_size=10.0, spatial_units="cm")
