from biosimulators_simularium.normalize.normalize_smoldyn import ModelDepiction
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.normalize.utils import calculate_radius


archive_root = 'biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023'
archive = SmoldynCombineArchive(rootpath=archive_root)

depiction = ModelDepiction(model_fp=archive.model_path)

environment = depiction.generate_environment(state='liquid', temperature=310.0, viscosity=8.1)

print(depiction.agents)
