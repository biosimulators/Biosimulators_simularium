"""Methods for writing and reading simularium files within COMBINE/OMEX archives."""


import os
from typing import Optional
from biosimulators_simularium.converters.data_model import SmoldynCombineArchive, SmoldynDataConverter
from biosimulators_simularium.converters.utils import generate_model_validation_object


__all__ = [
    'generate_new_simularium_file',
]


# pragma: no cover
def generate_new_simularium_file(archive_rootpath: str,
                                 simularium_filename: Optional[str] = None,
                                 save_output_df: bool = False) -> None:
    """Generate a new `.simularium` file based on the `model.txt` in the passed-archive rootpath using the above
        validation method. Raises an `Exception` if there are errors present.

    Args:
        archive_rootpath (:obj:`str`): Parent dirpath relative to the model.txt file.
        simularium_filename (:obj:`str`): `Optional`: Desired save name for the simularium file to be saved
            in the `archive_rootpath`. Defaults to `None`.
        save_output_df (:obj:`bool`): Whether to save the modelout.txt contents as a pandas df in csv form. Defaults
            to `False`.

    Returns:
        None
    """
    archive = SmoldynCombineArchive(rootpath=archive_rootpath, name=simularium_filename)
    model_validation = generate_model_validation_object(archive)
    if model_validation.errors:
        raise ValueError(f'There are errors involving your model file:\n{model_validation.errors}\nPlease adjust your model file.')
    simulation = model_validation.simulation
    if not os.path.exists(archive.model_output_filename):
        print('Running simulation...')
        simulation.runSim()
        print('Simulation Complete...')

    for root, _, files in os.walk(archive.rootpath):
        for f in files:
            if f.endswith('.txt') and 'model' not in f:
                f = os.path.join(root, f)
                os.rename(f, archive.model_output_filename)

    converter = SmoldynDataConverter(archive)

    if save_output_df:
        df = converter.read_model_output_dataframe()
        csv_fp = archive.model_output_filename.replace('txt', 'csv')
        df.to_csv(csv_fp)

    return converter.generate_simularium_file(simularium_filename=simularium_filename)


