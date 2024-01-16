import os
from warnings import warn
from typing import Tuple, Dict
from biosimulators_simularium.convert import generate_output_data_object, translate_data_object
from biosimulators_simularium.io import write_simularium_file
from biosimulators_simularium.utils import get_model_fp, get_modelout_fp
from smoldyn.biosimulators.combine import exec_sed_doc
from biosimulators_simularium.config import Config
from biosimulators_simularium.io import get_archive_files
from biosimulators_utils.combine.io import CombineArchiveWriter, CombineArchiveReader
from biosimulators_utils.combine.data_model import CombineArchive, CombineArchiveContent


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
        working_dir: str,
        sed_doc_path: str,
        output_dir: str,
        simularium_filename: str,
        save_path: str,
        model_fp: str = None,
        **config_params
) -> None:
    """Pass in a `working_dir` filepath and execute/retrieve the outputs of two fundamentally different
        simulations: A. The output of a SED-ML simulation which returns 2d data (not molecule location based),
        and B. The output of a Smoldyn simulation run from a given Smoldyn model filepath. The output gets saved
        at `output_dir` and a simularium file and smoldyn output file gets generated into the `output_dir`.
        The contents of this output_dir then gets converted into an `.omex` file (COMBINE archive) at `savepath`.

        Args:
            working_dir:`str`: path to the root of the directory in which a smoldyn model, sedml,
                and manifest are stored.
            sed_doc_path:`str`: path to the SEDML document of which you wish to execute and get the output. Ideally,
                the penultimate leaf of this path is `working_dir/`.
            output_dir:`str`: path to the location you wish to store the output of the SEDML simulation, the
                Smoldyn model output, AND the simularium file.
            simularium_filename:`str`: name of the simularium file to be stored at
                `output_dir/simularium_filename.simularium`.
            save_path:`str`: path by which to save and write out what is effectively the output of this function
                in the form of an OMEX file: a directory containing SEDML simulation outputs, a Smoldyn Model file,
                a SEDML file, a manifest file, a Smoldyn model output file, and a Simularium file.
            model_fp:`Optional[str]`: Smoldyn model file that the simulation(s) are based on. If `None`, then the
                model file is assumed to have `working_dir` as its parent. Defaults to `None`.
            **config_params:`kwargs`: either `agent_params` or `config` with the values being dictionaries according
                to the relative fields required for each.

        Keyword Args:
            agent_params: dictionary of agent parameters for simulation configuration. Possibly the output of
                `biosimulators_simularium.simulation_data.get_agent_params_from_model_file()`.
            config: dictionary of parameter fields and respective values according to the singleton interface
                of `biosimulators_simularium.config.Config()`. For example: `config={'PLOTS_PATH': 'outs.zip'}`.

        PLEASE NOTE: the simularium_filename is NOT path, but rather the name of the file itself, without .simularium.
        PLEASE NOTE: This function assumes that the model file is passed in with the working dir if model_fp is None.
        PLEASE NOTE: Ideally, you will be able to derive the logs from the bundled output.
    """

    # TODO: Remove the commented-out content below if bundling works

    sedml_config = Config(**config_params.get('config', {}))

    # TODO: Make sed_doc_path optional and extract from working_dir
    _, _ = exec_sed_doc(
        sed_doc_path,
        working_dir=working_dir,
        # base_out_path=output_dir,
        base_out_path=working_dir,
        # config=sedml_config
    )

    # add the output simularium filepath to the Biosimulators output bundle
    # TODO: Refactor much of this logic into an exception clause

    # simularium_fp = os.path.join(output_dir, simularium_filename)
    simularium_fp = os.path.join(working_dir, simularium_filename)
    generate_simularium_file(
        working_dir=working_dir,
        simularium_filename=simularium_fp,
        model_fp=model_fp,
        agent_params=config_params['agent_params']
    )

    if os.path.exists(simularium_fp + '.simularium'):
        # archive_files = get_archive_files(output_dir)
        # archive_files = get_archive_files(working_dir)
        archive_files = os.listdir(working_dir)
        archive_content = []
        for file in archive_files:
            content = CombineArchiveContent(location=file)
            if 'sedml' in file:
                content.master = True
                content.format = "http://identifiers.org/combine.specifications/sed-ml"
            elif 'simularium' in file or 'manifest' in file:
                content.format = "application/octet-stream"
            elif 'model' and not 'out' in file:
                content.format = "http://purl.org/NET/mediatypes/text/smoldyn+plain"
            elif 'out' in file:
                content.format = "text/plain"
            elif 'h5' in file:
                content.format = "application/x-hdf5"
            archive_content.append(content)
        archive = CombineArchive(archive_content)
        writer = CombineArchiveWriter()
        # writer.write_manifest(filename=os.path.join(output_dir, 'manifest.xml'), contents=archive_content)
        writer.write_manifest(filename=os.path.join(working_dir, 'manifest.xml'), contents=archive_content)
        # writer.run(archive=archive, in_dir=output_dir, out_file=save_path)
        writer.run(archive=archive, in_dir=working_dir, out_file=save_path)
        print(f'File saved at: {save_path}')
    else:
        raise ValueError(
            f'There is no simularium file found at the path for working_dir/simularium_filename that you have defined as {simularium_fp}.'
        )



