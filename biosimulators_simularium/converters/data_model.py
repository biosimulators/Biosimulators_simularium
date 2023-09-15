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
from smoldyn import Simulation
import smoldyn
import numpy as np
import pandas as pd
import zarr
from smoldyn.biosimulators.combine import validate_variables
from smoldyn import biosimulators as bioSim
from smoldyn.biosimulators.data_model import SmoldynOutputFile
from simulariumio.smoldyn.smoldyn_data import InputFileData, SmoldynData
from simulariumio.smoldyn import SmoldynConverter, SmoldynData
from simulariumio.filters import TranslateFilter
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
from biosimulators_utils.sedml.data_model import Task, Model, ModelLanguage
from biosimulators_utils.config import Config, get_config
from biosimulators_utils.report.data_model import ReportFormat
from biosimulators_utils.sedml.data_model import UniformTimeCourseSimulation, Variable, Task
from biosimulators_utils.model_lang.smoldyn.utils import get_parameters_variables_outputs_for_simulation


@dataclass
class Archive:
    rootpath: str
    output_dirpath: str
    model_path: Optional[str] = None
    name: Optional[str] = None


@dataclass
class SimulariumFilePath:
    path: str


class DataConverter(ABC):
    def __init__(self,
                 archive: Archive,
                 simularium_fp: SimulariumFilePath):
        self.archive = archive
        self.simularium_fp = simularium_fp
        self.archive.model_path = self._set_model_filepath()

    @abstractmethod
    def _set_model_filepath(self) -> Union[str, None]:
        """Find the model file in a given OMEX archive.
        """
        pass

    @abstractmethod
    def generate_data_object_for_output(
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
    def translate_data_object(self, data_object, box_size, n_dim):
        """Create a mirrored negative image of a distribution and apply it to 3dimensions if
            AND ONLY IF it contains all non-negative values.
        """
        pass

    @abstractmethod
    def generate_simularium_file(
            self,
            file_data_path: str,
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
    def prepare_input_file_data(output_filepath: str) -> InputFileData:
        return InputFileData(output_filepath)

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

    def save_simularium_file(self, data, simularium_filename: Optional[str] = None) -> None:
        output_path = simularium_filename or self.simularium_fp.path
        fp = os.path.join(output_path, simularium_filename)
        BinaryWriter.save(
            data,
            fp,
            validate_ids=False
        )


class SimulationSetupParams(str, Enum):
    project_root = 'biosimulators_simularium'
    model_fp = 'biosimulators_simularium/files/models/ecoli_model.txt'
    ecoli_archive_dirpath = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523'
    sed_doc = os.path.join(ecoli_archive_dirpath, 'simulation.sedml')
    outputs_dirpath = 'biosimulators_simularium/outputs'
