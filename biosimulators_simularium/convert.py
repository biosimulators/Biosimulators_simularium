import os.path
from typing import *
from smoldyn import Simulation
from simulariumio import (
    InputFileData,
    DisplayData,
    UnitData,
    MetaData,
    TrajectoryData,
    BinaryWriter,
    JsonWriter
)
from simulariumio.smoldyn.smoldyn_data import SmoldynData
from biosimulators_simularium.utils import (
    read_smoldyn_simulation_configuration,
    disable_smoldyn_graphics_in_simulation_configuration,
    write_smoldyn_simulation_configuration
)
from biosimulators_simularium.simulation_data import generate_molecules


def run_simulation(model_fp: str):
    return Simulation.fromFile(model_fp).runSim()


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


def generate_output_data_object(**config) -> SmoldynData:
    """Run a Smoldyn simulation from a given `model` filepath if a `modelout.txt` is not in the same working
        directory as the model file, and generate a configured instance of `simulariumio.smoldyn.smoldyn_data.SmoldynData`.

        Args:
              config:`kwargs`: The keyword arguments are as follows:
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

    if not os.path.exists(modelout_fp) and model_fp is not None:
        run_simulation(model_fp)
    return output_data_object(**config)


def write_simularium_file(
    data: Union[SmoldynData, TrajectoryData],
    simularium_filename: str,
    save_format: str,
    validation=True
) -> None:
    """Takes in either a `SmoldynData` or `TrajectoryData` instance and saves a simularium file based on it
        with the name of `simularium_filename`. If none is passed, the file will be saved in `self.archive.rootpath`
        Args:
            data(:obj:`Union[SmoldynData, TrajectoryData]`): data object to save.
            simularium_filename(:obj:`str`): `Optional`: name by which to save the new simularium file. If None is
                passed, will default to `self.archive.rootpath/self.archive.simularium_filename`.
            save_format(:obj:`str`): format which to write the `data`. Options include `json, binary`.
            validation(:obj:`bool`): whether to call the wrapped method using `validate_ids=True`. Defaults
                to `True`.
    """
    save_format = save_format.lower()
    if not os.path.exists(simularium_filename):
        if 'binary' in save_format:
            writer = BinaryWriter()
        elif 'json' in save_format:
            writer = JsonWriter()
        else:
            raise TypeError('You must provide a valid writer object.')
        return writer.save(trajectory_data=data, output_path=simularium_filename, validate_ids=validation)



