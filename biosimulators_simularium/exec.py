import os
from typing import Dict
from simulariumio import TrajectoryData
from simulariumio.smoldyn.smoldyn_data import SmoldynData
import pyvista as pv
from biosimulators_simularium.convert import (
    generate_output_trajectory,
    translate_data_object
)
from biosimulators_simularium.io import write_simularium_file, write_vtp_file, write_vtk_file


__all__ = [
    'execute',
    'generate_simularium_file'
]


def execute(
        working_dir: str,
        output_dir: str = None,
        agent_params: Dict[str, Dict[str, float]] = None,
        translate: bool = True,
        use_json: bool = False,
        box_size: float = 10.0,
        **setup_config
) -> None:
    # define vtp filenames
    vtp_filename = setup_config.get('vtp_filename', 'simulation-')
    vtp_filepath: str = os.path.join(output_dir, vtp_filename)

    vtk_filename = setup_config.get('vtk_filename', 'simulation.vtk')
    vtk_filepath: str = os.path.join(output_dir, vtk_filename)

    # generate a trajectory from the smoldyn file within a given working_dir
    trajectory, mesh = generate_output_trajectory(
        root_fp=working_dir,
        agent_params=agent_params,
        spatial_units=setup_config.get('spatial_units', 'mm'),
        temporal_units=setup_config.get('temporal_units', 'ms')
    )

    # reconstruct the surface from the mesh points
    # surface: pv.PolyData = mesh.reconstruct_surface()

    # generate vtp files for both polydata instances
    # generate_vtp_file(mesh, filename=vtp_filepath + 'points.vtp')
    generate_vtk_file(fp=vtk_filepath, data=mesh)

    # generate a simularium file
    return generate_simularium_file(
        trajectory,
        working_dir,
        output_dir,
        agent_params,
        translate,
        use_json,
        box_size,
        **setup_config
    )


def generate_vtk_file(fp, data):
    print('Writing trajectory to VTK -------------')
    try:
        write_vtk_file(fp, data)
        print(f"Successfully wrote VTK file to {fp}.")
        return
    except IOError as e:
        print(e)
        raise e


def generate_vtp_file(mesh: pv.PolyData, **kwargs):
    """write a vtp file to `save_path` based on the `mesh`. Kwargs according to `pv.PolyData().save()` args.

        Keyword Args:
            filename:`str`: path in which to save the vtp file.
            binary: bool = True,
            texture: Any = None,
            recompute_normals: Any
    """
    print('Writing trajectory to VTP -------------')
    try:
        write_vtp_file(mesh, **kwargs)
        print(f"Successfully wrote VTP file to {kwargs['filename']}.")
        return
    except IOError as e:
        print(e)
        raise e


def generate_simularium_file(
        trajectory: SmoldynData,
        working_dir: str,
        output_dir: str = None,
        agent_params: Dict[str, Dict[str, float]] = None,
        translate: bool = True,
        use_json: bool = False,
        box_size: float = 10.0,
        **setup_config
) -> None:
    """Generate a simularium file from a Smoldyn configuration (model) file which resides inside an unzipped
        archive directory found at `working_dir`. This is a high-level function that automatically generates
        simulation/agent parameters from the specified `working_dir/model.txt` path.

        Args:
            trajectory:`SmoldynData`.
            working_dir:`str`: root directory in which to save the simularium file. If no `model_fp` is passed,
                this working dir path is assumed to contain the Smoldyn model file.
            output_dir:`optional, str`: path to the root of the directory in which you wish to save
                the outputs (simularium file, vtp). If `None` is passed, then this value will be set to
                `working_dir`. Defaults to `None`.
            agent_params:`optional, Dict`: a dictionary of agent parameters in which the outermost keys are species name (agent),
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
            translate:`Optional[bool]`: translate negative values of trajectory and generate a new instance
                of `TrajectoryData` from the `SmoldynData` object. Defaults to `True`.
            use_json:`Optional[bool]`: if `True` then write the simularium file out as json, otherwise
                write out binary by default. Defaults to `False`.
            box_size:`float`: size by which to scale the universe/box. Defaults to `10.0`.
                # TODO: Make box_size less arbitrary and move it.
            **setup_config:`kwargs`: simularium_filename, vtp_filename, spatial_units(str), temporal_units(str)
    """
    # handle output allocation
    if output_dir:
        working_dir = output_dir
    simularium_filename = setup_config.get('simularium_filename', 'simulation')
    simularium_filepath: str = os.path.join(working_dir, simularium_filename)

    if translate:
        # In most cases you must translate the data such that negative values are accounted for as shown here
        trajectory: TrajectoryData = translate_data_object(data=trajectory, box_size=box_size)

    return write_simularium_file(trajectory, simularium_filename=simularium_filepath, json=use_json)


def execute_generate(write_simularium, write_vtp, **kwargs):
    # TODO: implement callbacks
    pass

