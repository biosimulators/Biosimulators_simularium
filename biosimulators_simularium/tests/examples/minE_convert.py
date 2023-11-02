from biosimulators_simularium.converters.data_model import SmoldynDataConverter
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.utils.core import HEX_COLORS
from biosimulators_simularium.normalize.utils import calculate_agent_radius


test_archive_root = 'biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023'
test_simularium_filename = 'minE_um_scale2'


archive = SmoldynCombineArchive(rootpath=test_archive_root, simularium_filename=test_simularium_filename)
converter = SmoldynDataConverter(archive=archive)

# env parameters
T = 310.0
k = 1.380649 * 10**-23
eta = 8.1

agents = [
    ('MinD_ATP(front)', calculate_agent_radius(k, T, eta, 0.01), HEX_COLORS.get('blue')), # 0.01
    ('MinE(solution)', calculate_agent_radius(k, T, eta, 2.5), HEX_COLORS.get('orange')), # 2.5
    ('MinD_ADP(solution)', calculate_agent_radius(k, T, eta, 2.5), HEX_COLORS.get('green')), # 2.5
    ('MinDMinE(front)', calculate_agent_radius(k, T, eta, 0.01), HEX_COLORS.get('purple')), # 0.01
    ('MinD_ATP(solution)', calculate_agent_radius(k, T, eta, 2.5), HEX_COLORS.get('yellow')) # 2.5
] # normally 0.01 radius


for agent in agents:
    print(agent)
#converter.generate_simularium_file(io_format='binary', agents=agents, box_size=10.0, spatial_units="um", scale=2.0)
