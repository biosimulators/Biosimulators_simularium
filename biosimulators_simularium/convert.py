import os.path
from typing import Dict, Union, Optional
from functools import partial
from uuid import uuid4
import numpy as np
from simulariumio import (
    InputFileData,
    DisplayData,
    UnitData,
    MetaData,
    TrajectoryData,
    DISPLAY_TYPE
)
from simulariumio.smoldyn.smoldyn_data import SmoldynData
from simulariumio.smoldyn.smoldyn_converter import SmoldynConverter
from simulariumio.filters.translate_filter import TranslateFilter
from biosimulators_simularium.simulation_data import (
    run_model_file_simulation,
    calculate_agent_radius,
    get_species_names_from_model_file,
    generate_agent_params_from_model_file
)
from biosimulators_simularium.io import (
    get_model_fp,
    get_modelout_fp,
    get_archive_files,
    read_smoldyn_simulation_configuration,
    disable_smoldyn_graphics_in_simulation_configuration,
    write_smoldyn_simulation_configuration
)


__all__ = [
    'new_output_data_object',
    'generate_output_data_object',
    'display_data_dict_from_archive_model_file',
    'translate_data_object'
]


def new_output_data_object(
    file_data: Union[InputFileData, str],
    display_data: Optional[Dict[str, DisplayData]] = None,
    meta_data: Optional[MetaData] = None,
    spatial_units="nm",
    temporal_units="ns",
) -> SmoldynData:
    """Generate a new instance of `SmoldynData`. If passing `meta_data`, please create a new `MetaData` instance
        using the `self.generate_metadata_object` interface of this same class.

    Args:
        file_data: (:obj:`InputFileData`, `str`): `simulariumio.InputFileData` instance based on model output or `str`
            path to the output.
        display_data: (:obj:`Dict[Dict[str, DisplayData]]`): `Optional`: if passing this parameter, please
            use the `self.generate_display_object_dict` interface of this same class.
        meta_data: (:obj:`Metadata`): new instance of `Metadata` object. If passing this parameter, please use the
            `self.generate_metadata_object` interface method of this same class.
        spatial_units: (:obj:`str`): spatial units by which to measure this simularium output. Defaults to `nm`.
        temporal_units: (:obj:`str`): time units to base this simularium instance on. Defaults to `ns`.

    Returns:
        :obj:`SmoldynData` configured
    """
    if isinstance(file_data, str):
        file_data = InputFileData(file_data)

    data = SmoldynData(
        smoldyn_file=file_data,
        spatial_units=UnitData(spatial_units),
        time_units=UnitData(temporal_units),
        # display_data=display_data,
        meta_data=meta_data,
        center=True
    )
    if isinstance(display_data, dict):
        data.display_data = display_data
    return data


# noinspection PyBroadException
def generate_output_data_object(agent_params: Optional[Dict] = None, **config) -> SmoldynData:
    """Run a Smoldyn simulation from a given `model` filepath if a `modelout.txt` is not in the same working
        directory as the model file, and generate a configured instance of `simulariumio.smoldyn.smoldyn_data.SmoldynData`.

            Args:
                agent_params:`optional, Dict`: a dictionary of agent parameters in which the outermost keys are species name (agent),
                    and the value is another dictionary with the keys 'density' and 'molecular_mass'.
                    If this value is passed as `None`, such a value is generated from the given `rootpath=...`
                    passed as a kwarg in this function.

                    For example, in the MinE model agent params would look something like:

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

            Keyword Args:
                rootpath:`str`: path to the working directory which houses smoldyn model.
                file_data:`Union[str, InputFileData]` path to the output file,
                display_data:`Optional[Dict[str, DisplayData]]`--> defaults to `None`
                meta_data:`Optional[MetaData]`
                spatial_units:`str`: defaults to nm
                temporal_units:`str`: defaults to ns
    """
    # extract the archive files from the rootpath defined in the kwargs
    root_fp = config.pop('rootpath')
    model_fp = get_model_fp(root_fp)
    try:
        modelout_fp = get_modelout_fp(root_fp)
    except:
        # turn off graphics if necessary
        sim_config = read_smoldyn_simulation_configuration(model_fp)
        if 'graphic' in sim_config:
            disable_smoldyn_graphics_in_simulation_configuration(sim_config)
            write_smoldyn_simulation_configuration(sim_config, model_fp)
        run_model_file_simulation(model_fp)
        modelout_fp = get_modelout_fp(root_fp)

    # set the modelout file as input for simulariumio
    config['file_data'] = InputFileData(modelout_fp)

    # set the display data dict from the model file inside the archive
    if not config.get('display_data'):
        display_data_dict = display_data_dict_from_archive_model_file(rootpath=root_fp)
        config['display_data'] = display_data_dict

    # return a configured instance
    return new_output_data_object(**config)


def display_data_dict_from_archive_model_file(
        rootpath: str = None,
        mol_major: Optional[bool] = False,
        agent_params: Optional[Dict] = None
) -> Dict[str, DisplayData]:
    """Generate agent parameters from the archive rootpath if none are passed and
        iterate `simulariumio.DisplayData` instances in a dictionary over either agents or
        individual molecules. If `mol_major`, then generate the display data based on each molecule
        in the output which is generally more computationally expensive,
        otherwise base it on the agents (species id) in the simulation.


        Args:
            rootpath:`str`: path to the working directory in which resides the smoldyn model file.
            mol_major:`bool`: if `True`, bases the display data objects on each individual molecule in the output.
            agent_params:`Dict`: Defaults to `None`.
    """
    model_fp = get_model_fp(rootpath)
    species_names = get_species_names_from_model_file(model_fp)
    if 'empty' in species_names:
        species_names.remove('empty')

    # TODO: set the m and rho vals more dynamically.
    if not agent_params:
        agent_params = generate_agent_params_from_model_file(model_fp, global_density=1.0, basis_m=1000)

    display_data = {}
    # extract data from the individual molecule array if mol major
    if mol_major:
        mol_outputs = run_model_file_simulation(model_fp)
        for mol in mol_outputs:
            mol_species_id_index = int(mol[0]) - 1  # here we account for the removal of 'empty'
            mol_name = str(uuid4()).replace('-', '_')
            mol_species_name = species_names[mol_species_id_index]
            mol_params = agent_params[mol_species_name]
            mol_radius = calculate_agent_radius(m=mol_params['molecular_mass'], rho=mol_params['density'])
            display_data[mol_name] = DisplayData(
                name=mol_species_name,
                display_type=DISPLAY_TYPE.SPHERE,
                radius=mol_radius
            )
    # otherwise base it on the agents
    else:
        for agent in species_names:
            mol_params = agent_params[agent]
            agent_radius = calculate_agent_radius(m=mol_params['molecular_mass'], rho=mol_params['density'])
            display_data[agent] = DisplayData(
                name=agent,
                display_type=DISPLAY_TYPE.SPHERE,
                radius=0.01,
                url=f'{agent}.obj'
            )

    return display_data


def translate_data_object(
    data: SmoldynData,
    box_size: float,
    n_dim=3,
    translation_magnitude: Optional[Union[int, float]] = None
) -> TrajectoryData:
    """Translate the data object's data if the coordinates are all positive to center the data in the
           simularium viewer.

           Args:
               data:`SmoldynData`: configured simulation output data instance.
               box_size: size of the simularium viewer box.
               n_dim: n dimensions of the simulation output. Defaults to `3`.
               translation_magnitude: magnitude by which to translate and filter. Defaults to `-box_size / 2`.

           Returns:
               `TrajectoryData`: translated data object instance.
       """
    translation_magnitude = translation_magnitude or -box_size / 2
    return SmoldynConverter(data).filter_data(
        [TranslateFilter(translation_per_type={}, default_translation=translation_magnitude * np.ones(n_dim))]
    )
