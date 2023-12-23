from biosimulators_simularium.converters.utils import validate_model


def main():
    archive_root = 'biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023'
    D_D = get_D_from_model_file()


def get_D_from_model_file(model_fp: str):
    validation = validate_model(model_fp)
    model = validation[len(validation)][1]
    for line in model:
        if line.startswith('difc') and 'D_D' in line:
            print(line)
            return line
