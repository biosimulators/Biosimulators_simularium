import os
from biosimulators_simularium.convert import generate_output_data_object, translate_data_object
from biosimulators_simularium.io import write_simularium_file
from biosimulators_simularium.utils import get_model_fp, get_modelout_fp


def generate_simularium_file(working_dir: str, simularium_filename: str, model_fp: str = None, return_sim: bool = False):
    """If `model_fp` is `None` (by default), the working_dir passed into this function MUST be the parent(or contain)
        the Smoldyn model file to run.
    """
    if not model_fp:
        model_fp = get_model_fp(working_dir)

    #display_data = {}  # TODO: Iterate over the output of the simulation molecules and house them here of type species.

    # TODO: Port in function from process-bigraph that matches species types to individual molecule outputs
    data = generate_output_data_object(model=model_fp)
    translated_data = translate_data_object(data=data)
    write_simularium_file(data, simularium_filename=simularium_filename, save_format='JSON')
    return
