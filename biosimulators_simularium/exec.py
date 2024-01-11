import os
from typing import Tuple, Dict
from biosimulators_simularium.convert import generate_output_data_object, translate_data_object
from biosimulators_simularium.io import write_simularium_file
from biosimulators_simularium.utils import get_model_fp, get_modelout_fp
from smoldyn.biosimulators.combine import exec_sed_doc
from biosimulators_simularium.config import Config


def generate_simularium_file(
        working_dir: str,
        simularium_filename: str,
        agent_params: Dict[str, Dict[str, float]],
        model_fp: str = None
) -> None:
    """If `model_fp` is `None` (by default), the working_dir passed into this function MUST be the parent(or contain)
        the Smoldyn model file to run.

        Args:
            working_dir:`str`: root directory in which to save the simularium file. If no `model_fp` is passed,
                this working dir path is assumed to contain the Smoldyn model file.
            simularium_filename:`str`: filename by which to serialize the simularium data object(s).
            agent_params:`Dict`: a dictionary of agent parameters in which the outermost keys are species name (agent),
                and the value is another dictionary with the keys 'density' and 'molecular_mass'.

                    For example, in the MinE model:

                            agent_params = {
                                'MinD_ATP': {
                                    'density': 1.0,
                                    'molecular_mass': randomize_mass(minE_molecular_mass),
                                },
                                'MinD_ADP': {
                                    'density': 1.0,
                                    'molecular_mass': randomize_mass(minE_molecular_mass),
                                },
                                'MinE': {
                                    'density': 1.0,
                                    'molecular_mass': minE_molecular_mass,
                                },
                                'MinDMinE': {
                                    'density': 1.0,
                                    'molecular_mass': randomize_mass(minE_molecular_mass),
                                },
                            }

                The `biosimulators_simularium.simulation_data.generate_agent_params()` function is available
                    to populate this field based on a given model file and starting parameters.
            model_fp:`str`: path to the model file containing the simulation details. If not specified, the Smoldyn model
                file is assumed to be a child of the `working_dir`. Defaults to `None`.
    """
    if not model_fp:
        model_fp = get_model_fp(working_dir)

    # TODO: Port in function from process-bigraph that matches species types to individual molecule outputs
    data = generate_output_data_object(agent_params=agent_params, model=model_fp)
    translated_data = translate_data_object(data=data, box_size=10.0)
    return write_simularium_file(translated_data, simularium_filename=simularium_filename, json=False)


def exec_combine_archive_and_simularium(
        sed_doc: str,
        working_dir: str,
        output_dir: str,
        simularium_filename: str,
        model_fp: str = None,
        return_sim: bool = False,
        **config_params
) -> Tuple:
    """Pass in a `working_dir` filepath and execute/retrieve the outputs of two fundamentally different
        simulations: A. The output of a SED-ML simulation which returns 2d data (not molecule location based),
        and B. The output of a Smoldyn simulation run from a given Smoldyn model filepath.

        PLEASE NOTE: the simularium_filename is NOT path, but rather the name of the file itself, without .simularium.

        PLEASE NOTE: This function assumes that the model file is passed in with the working dir if model_fp is None.

        # TODO: Add the simularium filepath to this dir upon write, effectively adding the simularium file
            to the omex.
    """

    sedml_config = Config(**config_params)
    results, log, simularium_fp = exec_sed_doc(sed_doc, working_dir=working_dir, base_out_path=output_dir, config=sedml_config)

    # add the output simularium filepath to the Biosimulators output bundle
    simularium_fp = os.path.join(output_dir, simularium_filename)
    generate_simularium_file(working_dir, simularium_fp, model_fp)
    if not os.path.exists(simularium_fp):
        simularium_fp = None
    return results, log, simularium_fp

    # TODO: Open and write new omex file here.

