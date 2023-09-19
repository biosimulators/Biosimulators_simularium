"""Using the Biosimulators side of Smoldyn to generate a modelout.txt Smoldyn file for a specified OMEX/COMBINE archive which then
    is used to generate a .simularium file for the given simulation. That .simularium file is then stored along with the log.yml and
    report.{FORMAT} relative to the simulation. Remember: each simulation, while not inherently published, has the potential for publication
    based purely on the simulation's ability to provide a valid OMEX/COMBINE archive. There exists (or should exist) an additional layer
    of abstraction to then validate and verify the contents therein.
"""


import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List, Union
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import zarr
from smoldyn import Simulation
from smoldyn.biosimulators.data_model import SmoldynOutputFile
from smoldyn.biosimulators.combine import (
    init_smoldyn_simulation_from_configuration_file,
    validate_variables,
    disable_smoldyn_graphics_in_simulation_configuration,
    read_smoldyn_simulation_configuration,
    write_smoldyn_simulation_configuration,
)
from simulariumio import (
    TrajectoryData,
    CameraData,
    TrajectoryConverter,
    AgentData,
    UnitData,
    MetaData,
    DisplayData,
    DISPLAY_TYPE,
    ModelMetaData,
    BinaryWriter,
    InputFileData,
)
from simulariumio.smoldyn.smoldyn_data import InputFileData, SmoldynData
from simulariumio.smoldyn import SmoldynConverter, SmoldynData
from simulariumio.filters import TranslateFilter
from simulariumio.data_objects.trajectory_data import TrajectoryData


ECOLI_ARCHIVE_ROOTPATH = 'biosimulators_simularium/test_files/archives/Andrews_ecoli_0523'


class CombineArchive:
    def __init__(self,
                 rootpath: str,
                 outputs_dirpath: Optional[str] = None,
                 model_output_filename: Optional[str] = None,
                 simularium_filename: Optional[str] = None,
                 name='my_combine_archive'):
        self.rootpath = rootpath
        self.outputs_dirpath = outputs_dirpath
        self.simularium_filename = simularium_filename or f'{name}_output_for_simularium'
        self.paths = self.__get_all_archive_filepaths()
        self.model_path = self.set_model_filepath()

        self.model_output_filename = model_output_filename \
            or self.model_path.replace('.txt', '') + 'out.txt'
        self.paths['model_output_file'] = self.model_output_filename

    def __get_all_archive_filepaths(self) -> Dict[str, str]:
        paths = {}
        if os.path.exists(self.rootpath):
            for root, _, files in os.walk(self.rootpath):
                paths['root'] = root
                for f in files:
                    fp = os.path.join(root, f)
                    paths[f] = fp
        return paths

    def set_model_filepath(self, model_filename: Optional[str] = None) -> Union[str, None]:
        model_filename = model_filename or 'model.txt'  # default Smoldyn model name
        for k in self.paths.keys():
            full_path = self.paths[k]
            if model_filename in full_path:
                return full_path


'''a = CombineArchive(rootpath=ECOLI_ARCHIVE_ROOTPATH)

print('it is: ' + a.model_path)
print(a.paths)'''


class OutputData(ABC):
    def __init__(self, value, n_dim: int):
        self.value = value
        self.n_dim = n_dim


class TranslatedData(ABC):
    def __init__(self, data: OutputData, box_size: float):
        self.data = data
        self.c = self._set_converter(self.data)
        self.box_size = box_size

    @abstractmethod
    def _set_converter(self, data):
        pass


class SmoldynOutputData(OutputData):
    def __init__(self, value: SmoldynData, n_dim=3):
        super().__init__(value, n_dim)


class TranslatedSmoldynData(TranslatedData):
    def __init__(self, data: SmoldynOutputData, box_size: float):
        super().__init__(data, box_size)
        self.c = self._set_converter(data)
        self.box_size = box_size
        translation_magnitude = -self.box_size / 2
        self.filtered_data = self.c.filter_data([
            TranslateFilter(
                translation_per_type={},
                default_translation=translation_magnitude * np.ones(data.n_dim)
            ),
        ])

    def _set_converter(self, data: SmoldynOutputData):
        return SmoldynConverter(data.value)


class BiosimulatorsDataConverter(ABC):
    def __init__(self, archive: CombineArchive):
        """This class serves as the abstract interface for a simulator-specific implementation
            of utilities through which the user may convert Biosimulators outputs to a valid simularium File.

                Args:
                    :param:`archive`:(`CombineArchive`): new instance of a `CombineArchive` object.
        """
        self.archive = archive

    @abstractmethod
    def generate_output_data_object(
            self,
            file_data: InputFileData,
            display_data: Optional[Dict[str, DisplayData]] = None,
            spatial_units="nm",
            temporal_units="ns",
            ):
        """Generate a data object to fit the simulariumio.TrajectoryData interface.
        """
        pass

    @abstractmethod
    def translate_data_object(self, data_object: OutputData, box_size, n_dim) -> TrajectoryData:
        """Create a mirrored negative image of a distribution and apply it to 3dimensions if
            AND ONLY IF it contains all non-negative values.
        """
        pass

    @abstractmethod
    def generate_simularium_file(
            self,
            simularium_filename: str,
            box_size: float,
            spatial_units="nm",
            temporal_units="ns",
            n_dim=3,
            display_data: Optional[Dict[str, DisplayData]] = None
            ) -> None:
        """Create a data_object, optionally translate it, convert to simularium, and save.
        """
        pass

    @staticmethod
    def prepare_simularium_fp(**simularium_config) -> str:
        """Generate a simularium dir and joined path if not using the init object.

            Kwargs:
                (obj):`**simularium_config`: keys are 'simularium_dirpath' and 'simularium_fname'

            Returns:
                (obj):`str`: complete simularium filepath
        """
        dirpath = simularium_config.get('simularium_dirpath')
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        return os.path.join(dirpath, simularium_config.get('simularium_fname'))

    @staticmethod
    def prepare_agent_data():
        pass

    @staticmethod
    def generate_metadata_object(box_size: np.ndarray[int], camera_data: CameraData) -> MetaData:
        return MetaData(box_size=box_size, camera_defaults=camera_data)

    @staticmethod
    def generate_camera_data_object(
            position: np.ndarray,
            look_position: np.ndarray,
            up_vector: np.ndarray
            ) -> CameraData:
        return CameraData(position=position, look_at_position=look_position, up_vector=up_vector)

    @classmethod
    def generate_display_data_object(
            cls,
            name: str,
            radius: float,
            display_type=DISPLAY_TYPE.SPHERE,
            obj_color: Optional[str] = None,
    ) -> DisplayData:
        return DisplayData(
            name=name,
            radius=radius,
            display_type=display_type,
            color=obj_color
        )

    @classmethod
    def generate_display_data_object_dict(
            cls,
            agent_names: List[Tuple[str, str, float, str]]) -> Dict[str, DisplayData]:
        """Generate a display object dict.

            Args:
                agent_names: `List[Tuple[str, str, float]]` -> a list of tuples defining the Display Data configuration parameters.\n
                The Tuple is expected to be as such: [(`agent_name: str`, `display_name: str`, `radius: float`, `color`: `str`)]

            Returns:
                `Dict[str, DisplayData]`
        """
        data = {}
        for name in agent_names:
            data[name[0]] = cls.generate_display_data_object(
                name=name[0],
                radius=name[2],
                obj_color=name[3]
            )
        return data

    @staticmethod
    def save_simularium_file(
            data: Union[SmoldynData, TrajectoryData],
            simularium_filename,
            ) -> None:
        """Takes in either a `SmoldynData` or `TrajectoryData` instance and saves a simularium file based on it
            with the name of `simularium_filename`. If none is passed, the file will be saved in `self.archive.rootpath`

            Args:
                  data(:obj:`Union[SmoldynData, TrajectoryData]`): data object to save.
                  simularium_filename(:obj:`str`): `Optional`: name by which to save the new simularium file. If None is
                    passed, will default to `self.archive.rootpath/self.archive.simularium_filename`
        """
        BinaryWriter.save(
            data,
            simularium_filename,
            validate_ids=True
        )

    def generate_input_file_data_object(self, model_output_file: Optional[str] = None) -> InputFileData:
        """Generates a new instance of `simulariumio.data_model.InputFileData` based on
            `self.archive.model_output_filename` (which itself is derived from the model file) if no `model_output_file`
            is passed.

            Args:
                  model_output_file(:obj:`str`): `Optional`: file on which to base the `InputFileData` instance.
            Returns:
                  (:obj:`InputFileData`): simulariumio input file data object based on `self.archive.model_output_filename`

        """
        model_output_file = model_output_file or self.archive.model_output_filename
        return InputFileData(model_output_file)


class SmoldynDataConverter(BiosimulatorsDataConverter):
    def __init__(self, archive: CombineArchive):
        """General class for converting Smoldyn output (modelout.txt) to .simularium. Checks the passed archive object
            directory for a `modelout.txt` file (standard Smoldyn naming convention) and runs the simulation by default if
            not.

            Args:
                archive (:obj:`CombineArchive`): new instance of a `CombineArchive` object.
        """
        super().__init__(archive)
        self.__disable_graphics()
        if not os.path.exists(self.archive.model_output_filename):
            self.__generate_model_output_file()

    def __disable_graphics(self):
        """Helper method to wrap smoldyn functions. Read the passed `CombineArchive.model_path` as a list, turn off the
            graphics using Smoldyn, and rewrite the model file with turned off graphics. NOTE: This method
            is required for automation on the command-line.
        """
        smoldyn_config = read_smoldyn_simulation_configuration(self.archive.model_path)
        disable_smoldyn_graphics_in_simulation_configuration(smoldyn_config)
        write_smoldyn_simulation_configuration(smoldyn_config, self.archive.model_path)

    def __generate_model_output_file(self) -> None:
        """Method required for checking the existence of a `modelout.txt` file and running the simulation
            with graphics turned off if not.
        """
        simulation = init_smoldyn_simulation_from_configuration_file(self.archive.model_path)
        return simulation.runSim()

    def read_model_output_dataframe(self) -> pd.DataFrame:
        colnames = ['mol_name', 'x', 'y', 'z', 't']
        return pd.read_csv(self.archive.model_output_filename, sep=" ", header=None, skiprows=1, names=colnames)

    def generate_output_data_object(
            self,
            file_data: InputFileData,
            display_data: Optional[Dict[str, DisplayData]] = None,
            spatial_units="nm",
            temporal_units="ns",
            ) -> SmoldynData:
        return SmoldynData(
            smoldyn_file=file_data,
            spatial_units=UnitData(spatial_units),
            time_units=UnitData(temporal_units),
            display_data=display_data,
        )

    def translate_data_object(self, data_object: SmoldynData, box_size: float, n_dim=3) -> TrajectoryData:
        c = SmoldynConverter(data_object)
        translation_magnitude = -box_size / 2
        return c.filter_data([
            TranslateFilter(
                translation_per_type={},
                default_translation=translation_magnitude * np.ones(n_dim)
            ),
        ])

    def generate_simularium_file(
            self,
            box_size=1.,
            spatial_units="nm",
            temporal_units="ns",
            n_dim=3,
            simularium_filename: Optional[str] = None,
            display_data: Optional[Dict[str, DisplayData]] = None
            ) -> None:
        input_file = self.generate_input_file_data_object()
        data = self.generate_output_data_object(
            file_data=input_file,
            display_data=display_data,
            spatial_units=spatial_units,
            temporal_units=temporal_units
        )
        translated = self.translate_data_object(data, box_size, n_dim)
        simularium_filename = simularium_filename \
            or os.path.join(self.archive.rootpath, self.archive.simularium_filename)
        self.save_simularium_file(translated, simularium_filename)
        print('New Simularium file generated!!')


class SimulationSetupParams(str, Enum):
    project_root = 'biosimulators_simularium'
    model_fp = 'biosimulators_simularium/test_files/models/ecoli_model.txt'
    ecoli_archive_dirpath = 'biosimulators_simularium/test_files/archives/Andrews_ecoli_0523'
    sed_doc = os.path.join(ecoli_archive_dirpath, 'simulation.sedml')
    outputs_dirpath = 'biosimulators_simularium/outputs'
