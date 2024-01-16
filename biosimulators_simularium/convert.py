import os.path
from typing import Dict, Union, Optional
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
    get_species_names_from_model_file
)
from biosimulators_simularium.utils import (
    read_smoldyn_simulation_configuration,
    disable_smoldyn_graphics_in_simulation_configuration,
    write_smoldyn_simulation_configuration
)


def output_data_object(
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

    return SmoldynData(
        smoldyn_file=file_data,
        spatial_units=UnitData(spatial_units),
        time_units=UnitData(temporal_units),
        display_data=display_data,
        meta_data=meta_data,
        center=True
    )


def generate_output_data_object(agent_params: Dict, **config) -> SmoldynData:
    """Run a Smoldyn simulation from a given `model` filepath if a `modelout.txt` is not in the same working
        directory as the model file, and generate a configured instance of `simulariumio.smoldyn.smoldyn_data.SmoldynData`.

            Args:
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

                config:`kwargs`: output data configuration whose keyword arguments are as follows:
                    model:`str`: path to the model file
                    file_data:`Union[str, InputFileData]` path to the output file(pass if not model),
                    display_data:`Optional[Dict[str, DisplayData]]`--> defaults to `None`
                    meta_data:`Optional[MetaData]`
                    spatial_units:`str`: defaults to nm
                    temporal_units:`str`: defaults to ns
    """
    model_fp = config.pop('model')
    modelout_fp = model_fp.replace('model.txt', 'modelout.txt')
    config['file_data'] = modelout_fp

    sim_config = read_smoldyn_simulation_configuration(model_fp)
    if 'graphic' in sim_config:
        disable_smoldyn_graphics_in_simulation_configuration(sim_config)
        write_smoldyn_simulation_configuration(sim_config, model_fp)

    if model_fp is not None:
        mol_outputs = run_model_file_simulation(model_fp)

        if not config.get('display_data'):
            display_data = {}
            species_names = get_species_names_from_model_file(model_fp)

            if 'empty' in species_names:
                species_names.remove('empty')

            for agent in species_names:
                mol_params = agent_params[agent]
                agent_radius = calculate_agent_radius(m=mol_params['molecular_mass'], rho=mol_params['density'])
                display_data[agent] = DisplayData(
                    name=agent,
                    display_type=DISPLAY_TYPE.SPHERE,
                    radius=0.01,
                    url=f'{agent}.obj'
                )

            # extract data from the individual molecule array
            # for mol in mol_outputs:
            #     mol_species_id_index = int(mol[0]) - 1  # here we account for the removal of 'empty'
            #     mol_name = str(uuid4()).replace('-', '_')
            #     mol_species_name = species_names[mol_species_id_index]
            #     mol_params = agent_params[mol_species_name]
            #     mol_radius = calculate_agent_radius(m=mol_params['molecular_mass'], rho=mol_params['density'])
            #     display_data[mol_name] = DisplayData(
            #         name=mol_species_name,
            #         display_type=DISPLAY_TYPE.SPHERE,
            #         radius=mol_radius
            #     )
            config['display_data'] = display_data
    else:
        raise ValueError('You must pass a valid Smoldyn model file. Please pass the path to such a model file as "model" in the args of this function.`')
    return output_data_object(**config)


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
