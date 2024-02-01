import os.path
from typing import Dict, Union, Optional, List, Tuple
from functools import partial
from uuid import uuid4
import numpy as np
from smoldyn import Simulation
import pyvista as pv
from simulariumio import (
    InputFileData,
    DisplayData,
    UnitData,
    MetaData,
    TrajectoryData,
    DISPLAY_TYPE,
    ModelMetaData
)
from simulariumio.smoldyn.smoldyn_data import SmoldynData
from simulariumio.smoldyn.smoldyn_converter import SmoldynConverter
from simulariumio.filters.translate_filter import TranslateFilter
from biosimulators_simularium.geometry import get_config_geometry, read_geometry
from biosimulators_simularium.simulation_data import (
    generate_molecule_coordinates,
    generate_output,
    calculate_agent_radius,
    get_species_names_from_model_file,
    generate_agent_params,
    get_axis,
    compute_vectors
)
from biosimulators_simularium.io import (
    get_model_fp,
    normalize_modelout_path_in_root,
    read_smoldyn_simulation_configuration,
    disable_smoldyn_graphics_in_simulation_configuration,
    write_smoldyn_simulation_configuration,
)


__all__ = [
    'new_output_trajectory',
    'generate_output_trajectory',
    'display_data_dict_from_archive_model',
    'translate_data_object'
]


def new_output_trajectory(
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
def generate_output_trajectory(
        root_fp: str,
        agent_params: Optional[Dict] = None,
        **config
) -> Tuple[SmoldynData, pv.PolyData]:
    """Run a Smoldyn simulation from a given `model` filepath if a `modelout.txt` is not in the same working
        directory as the model file, and generate a two-tuple of configured instance of `simulariumio.smoldyn.smoldyn_data.SmoldynData`.
        as well as `pyvista.PolyData` with interpolated point values.

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

    # disable graphics if necessary
    sim_config = read_smoldyn_simulation_configuration(model_fp)
    disable_smoldyn_graphics_in_simulation_configuration(sim_config)
    write_smoldyn_simulation_configuration(sim_config, model_fp)

    # run the simulation and generate an output
    mol_outputs: Dict = generate_output(model_fp=model_fp)

    # generate vtk
    # mesh = generate_point_mesh(mol_output=mol_outputs)
    mesh = read_geometry(fp=model_fp, sim=mol_outputs['simulation'], coords=mol_outputs['coordinates'])

    # standardize the output name
    normalize_modelout_path_in_root(root_fp)

    # set the modelout file as input for simulariumio
    config['file_data'] = InputFileData(model_fp.replace('model.txt', 'modelout.txt'))

    # set the display data dict from the model file inside the archive
    if not config.get('display_data'):
        config['display_data'] = display_data_dict_from_archive_model(
            rootpath=root_fp,
            agent_params=agent_params
        )

    # handle metadata and generate if none is present  TODO: extract this from a Biosimulations abstract
    if not config.get('meta_data'):
        config['meta_data'] = generate_metadata_object()

    # return a configured instance
    trajectory = new_output_trajectory(**config)
    return trajectory, mesh


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
            radius=0.001,
            # url=f'{agent}.obj'
        )

    return display_data


def generate_metadata_object(
        box_size: float = 10.0,
        trajectory_title: str = "A spatial simulation trajectory",
        **model_metadata_params
) -> MetaData:
    """Generate a metadata object configured for the particular simulation. Also generates model metadata
        which you must define parameters of via this function's kwargs.

        Args:
            box_size:`float`: size by which we scale each dimension.
            trajectory_title:`str`: title of the trajectory/data_object.
            **model_metadata_params:`kwargs`: params required by the `simulariumio.ModelMetadata` constructor.
                The kwargs are as follows: title, version, authors, description, doi, source_code_url,
                    source_code_license_url, input_data_url, raw_output_data_url. Keep in mind that
                    these kwargs pertain to the model only.
    """
    return MetaData(
        box_size=np.array([box_size, box_size, box_size]),
        trajectory_title=trajectory_title,
        model_meta_data=ModelMetaData(**model_metadata_params)
    )


def generate_point_mesh(
        include_vectors: bool = False,
        **kwargs
) -> pv.PolyData:
    """Generate a mesh from the given simulation run's `smoldyn.Simulation.fromFile()`
        instance into which passed molecule coordinate points are represented. Currently, this
        function only returns the points as a mesh without an explicit surface: the user may easily
        reconstruct the surface from the output of this function with: `generate_interpolated_mesh().reconstruct_surface()`.
        You have to either pass a `mol_output` dict or a np.array of molecule coordinates ALONG with a cooresponding simulation
        instance.

        Args:
            include_vectors:`optional, bool`: Compute the point vectors and include them as an attribute to
                the points `pv.PolyData` instance. NOTE: This may be computationally expensive
                depending on the size of the molecule output. Defaults to `False`.

        Keyword Args:
            mol_output:`optional, Dict`: dictionary of molecule outputs that define 'data', 'simulation',
                'coordinates', and 'boundaries'. NOTE: This is the preferred input type for this function.
            coordinates:`optional, np.ndarray`: Nd array of shape (n, 3) representing each molecule's coordinates.
                If `None` is passed, you must pass the path to a smoldyn model file or simulation instance.
                Defaults to `None`.
            boundaries:`optional, Tuple[List[float], List[float]`: a two-tuple of lists of floats where
                the 0th entry are the lower bounds of x, y, z and the 1th entry being the same for higher bounds.
            simulation:`optional, smoldyn.Simulation`: simulation instance used to generate molecule coordinates used
                to define boundaries if boundaries are not passed.
            model_fp:`optional, str`: if no `mol_coords` are passed, the path to the smoldyn configuration by which you
                generate the coordinates for the mesh.

    """
    print('Generating point mesh -------------')

    # helper for standalone functionality
    mol_output = kwargs.get('mol_output')
    if isinstance(mol_output, dict):
        mol_coords = mol_output['coordinates']
    else:
        mol_coords = kwargs['coordinates']

    # define particle points as a mesh
    points = pv.PolyData(mol_coords)

    if include_vectors:
        # compute vectors
        point_vectors = compute_vectors(points)
        y = get_axis(mol_coords, axis=1)
        z = get_axis(mol_coords, axis=2)

        # add the vectors to the mesh and configure viz arrows
        points['vectors'] = point_vectors
        vector_arrows = points.glyph(
            orient='vectors',
            scale=False,
            factor=3.0
        )
    print('Point mesh Generated!')

    return points


def generate_interpolated_mesh(
        include_vectors: bool = False,
        points: pv.PolyData = None,
        **kwargs,
) -> pv.PolyData:
    """Generate an interpolated surface of reconstructed point surface and points.
        You have to either pass a `mol_output` dict or a np.array of molecule coordinates ALONG with a cooresponding simulation
        instance.

        Args:
            include_vectors:`optional, bool`: Compute the point vectors and include them as an attribute to
                the points `pv.PolyData` instance. NOTE: This may be computationally expensive
                depending on the size of the molecule output. Defaults to `False`.
            points:`optional, pv.PolyData`: polydata instance of mol points. Defaults to `None`.

        Keyword Args:
            mol_output:`optional, Dict`: dictionary of molecule outputs that define 'data', 'simulation',
                'coordinates', and 'boundaries'. NOTE: This is the preferred input type for this function.
            coordinates:`optional, np.ndarray`: Nd array of shape (n, 3) representing each molecule's coordinates.
                If `None` is passed, you must pass the path to a smoldyn model file or simulation instance.
                Defaults to `None`.
            boundaries:`optional, Tuple[List[float], List[float]`: a two-tuple of lists of floats where
                the 0th entry are the lower bounds of x, y, z and the 1th entry being the same for higher bounds.
            simulation:`optional, smoldyn.Simulation`: simulation instance used to generate molecule coordinates used
                to define boundaries if boundaries are not passed.
            model_fp:`optional, str`: if no `mol_coords` are passed, the path to the smoldyn configuration by which you
                generate the coordinates for the mesh.

    """
    print('Generating interpolated mesh -------------')
    if not points:
        points = generate_point_mesh(include_vectors, **kwargs)

    # reconstruct the surface from the points in the mesh
    surface = points.reconstruct_surface()

    # interpolate the points into the surface
    return surface.interpolate(points, radius=12.0)


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

