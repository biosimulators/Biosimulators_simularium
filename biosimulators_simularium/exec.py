import os
from biosimulators_simularium.convert import generate_output_data_object, translate_data_object
from biosimulators_simularium.io import write_simularium_file
from biosimulators_simularium.utils import get_model_fp, get_modelout_fp
from smoldyn.biosimulators.combine import exec_sed_doc
from biosimulators_simularium.config import Config


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


def exec_combine_archive(
        sed_doc: str,
        working_dir: str,
        output_dir: str,
        simularium_filename: str,
        model_fp: str = None,
        return_sim: bool = False,
        **config_params
):
    """Pass in a `working_dir` filepath and execute/retrieve the outputs of two fundamentally different
        simulations: A. The output of a SED-ML simulation which returns 2d data (not molecule location based),
        and B. The output of a Smoldyn simulation run from a given Smoldyn model filepath.

        PLEASE NOTE: the simularium_filename is NOT path, but rather the name of the file itself, without .simularium.

        PLEASE NOTE: This funciton assumes that the model file is passed in with the working dir if model_fp is None.

        # TODO: Add the simularium filepath to this dir upon write, effectively adding the simularium file
            to the omex.
    """

    sedml_config = Config(**config_params)
    results, log = exec_sed_doc(sed_doc, working_dir=working_dir, base_out_path=output_dir, config=sedml_config)

    # add the output simularium filepath to the Biosimulators output bundle
    simularium_fp = os.path.join(output_dir, simularium_filename)
    generate_simularium_file(working_dir, simularium_fp, model_fp, return_sim)

    # TODO: Open and write new omex file here.
