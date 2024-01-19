import os.path
from typing import Dict, Union, Optional, List
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
    generate_agent_params
)
from biosimulators_simularium.io import (
    get_model_fp,
    normalize_modelout_path_in_root,
    read_smoldyn_simulation_configuration,
    disable_smoldyn_graphics_in_simulation_configuration,
    write_smoldyn_simulation_configuration
)


__all__ = [
    'new_output_data_object',
    'generate_output_data_object',
    'display_data_dict_from_archive_model',
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
def generate_output_data_object(
        root_fp: str,
        agent_params: Optional[Dict] = None,
        **config
) -> SmoldynData:
    """Run a Smoldyn simulation from a given `model` filepath if a `modelout.txt` is not in the same working
        directory as the model file, and generate a configured instance of `simulariumio.smoldyn.smoldyn_data.SmoldynData`.

            Args:

                root_fp:`str`: path to the working directory which houses smoldyn model.
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
                display_data:`Optional[Dict[str, DisplayData]]`--> defaults to `None`
                meta_data:`Optional[MetaData]`
                spatial_units:`str`: defaults to nm
                temporal_units:`str`: defaults to ns

    """
    # extract the archive files from the rootpath defined in the kwargs
    model_fp = get_model_fp(root_fp)

    sim_config = read_smoldyn_simulation_configuration(model_fp)
    disable_smoldyn_graphics_in_simulation_configuration(sim_config)
    write_smoldyn_simulation_configuration(sim_config, model_fp)
    mol_outputs = run_model_file_simulation(model_fp)
    # standardize the output name
    normalize_modelout_path_in_root(root_fp)

    # set the modelout file as input for simulariumio
    config['file_data'] = InputFileData(model_fp.replace('model.txt', 'modelout.txt'))

    # set the display data dict from the model file inside the archive
    if not config.get('display_data'):
        display_data_dict = display_data_dict_from_archive_model(rootpath=root_fp, agent_params=agent_params)
        config['display_data'] = display_data_dict

    print(f'final traj config: {config}')
    # return a configured instance
    return new_output_data_object(**config)


def display_data_dict_from_archive_model(
        rootpath: str = None,
        mol_outputs: List[List[float]] = None,
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
            mol_outputs:`str`: results of a smoldyn simulation with the listmols command. Defaults to None.
            mol_major:`bool`: if `True`, bases the display data objects on each individual molecule in the output.
            agent_params:`Dict`: Defaults to `None`.
    """
    # get the model fp
    model_fp = get_model_fp(rootpath)

    # get spec names from model fp
    species_names = get_species_names_from_model_file(model_fp)

    # TODO: set the m and rho vals more dynamically.
    # generate agent params if necessary from model_fp
    if not agent_params:
        agent_params = generate_agent_params(species_names, global_density=1.0, basis_m=1000)

    # return mol-based display data dict if mol_major; agent-based if not
    return display_data_dict_mol_major(mol_outputs, species_names, agent_params) \
        if mol_major else display_data_dict_agent_major(species_names, agent_params)


def display_data_dict_mol_major(
        mol_outputs: List[List[float]],
        species_names: List[str],
        agent_params: Dict[str, Dict[str, Union[int, float]]]
) -> Dict[str, DisplayData]:
    """Generate a dictionary in which the keys are `uuid4()`-assigned molecule names and the
        values are configured DisplayData instances based on the given molecule given
        physical parameters like mol mass and density.

        Args:
            mol_outputs:`List[List[float]]`: A list of molecule output data: the exact result of
                the Smoldyn `listmols` command.
            species_names:`List[str]`: List of species names corresponding to the species of a
                smoldyn simulation.
            agent_params:`Dict`: agent params encoded in a dictionary. See
                `biosimulators_simularium.convert.display_data_dict_agent_major()`.
    """
    display_data = {}
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

    return display_data


def display_data_dict_agent_major(
        species_names: List[str],
        agent_params: Dict[str, Dict[str, Union[int, float]]]
) -> Dict[str, DisplayData]:
    """Generate a dictionary in which the keys are agent(in this case, species) names, and
        the values are configured DisplayData instances corresponding to the agent name.
        This is generally what `simulariumio` expects when instantiating a Trajectory.

        Args:
            species_names:`List[str]`: List of species names which correspond to the species of
                a Smoldyn simulation configuration.
            agent_params:`Dict`: dictionary of agent parameters according to the species names/smoldyn
                configuration. For example, with a MinE simulation:

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
    """
    display_data = {}
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
