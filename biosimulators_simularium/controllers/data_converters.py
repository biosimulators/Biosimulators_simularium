"""Using the Biosimulators side of Smoldyn to generate a modelout.txt Smoldyn file for a specified OMEX/COMBINE archive which then
    is used to generate a .simularium file for the given simulation. That .simularium file is then stored along with the log.yml and
    report.{FORMAT} relative to the simulation. Remember: each simulation, while not inherently published, has the potential for publication
    based purely on the simulation's ability to provide a valid OMEX/COMBINE archive. There exists (or should exist) an additional layer
    of abstraction to then validate and verify the contents therein.
"""


import os
from enum import Enum
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


class DataConverter(ABC):
    def __init__(self,
                 archive_rootpath: str,
                 output_dirpath: Optional[str] = None):
        self.archive_rootpath = archive_rootpath
        self.output_dirpath = output_dirpath

    @abstractmethod
    def _get_model_filepath(self) -> Union[str, None]:
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
    def prepare_simularium_fp(simularium_dirpath: str, simularium_fname: str) -> str:
        if not os.path.exists(simularium_dirpath):
            os.mkdir(simularium_dirpath)
        return os.path.join(simularium_dirpath, simularium_fname)

    @staticmethod
    def prepare_input_file_data(output_filepath: str) -> InputFileData:
        return InputFileData(output_filepath)

    @staticmethod
    def prepare_agent_data():
        pass

    @staticmethod
    def generate_display_data_object(
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

    def generate_display_data_object_dict(
            self,
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
            data[name[0]] = self.generate_display_data_object(
                name=name[0],
                radius=name[2],
                obj_color=name[3]
            )
        return data

    def save_simularium_file(self, data, simularium_filename: str) -> None:
        fp = os.path.join(self.output_dirpath, simularium_filename)
        BinaryWriter.save(
            data,
            fp,
            validate_ids=False
        )


class SmoldynDataConverter(DataConverter):
    def __init__(self,
                 archive_rootpath: str,
                 output_dirpath: Optional[str] = None):
        super().__init__(archive_rootpath, output_dirpath)
        self.model_filepath = self._get_model_filepath()

    def _get_model_filepath(self) -> Union[str, None]:
        if os.path.exists(self.archive_rootpath):
            for root, _, files in os.walk(self.archive_rootpath):
                for f in files:
                    fp = os.path.join(root, f)
                    return fp if fp.endswith('.txt') else None

    @staticmethod
    def validate_variables_from_archive_model(variables: List[Variable]) -> Dict:
        return validate_variables(variables)

    @staticmethod
    def get_params_from_model_file(
            model_fp: str,
            sim_language: str,
            sim_type=UniformTimeCourseSimulation
            ) -> Dict[str, List]:
        """Get the model changes, simulator, and variables from the model file without running the simulation

            Args:
                model_fp (:obj:`str`): path to model file
                sim_language (:obj:`str`): urn format of model language ie: "uri:sedml:language:smoldyn"
                sim_type (:obj:`Type`): object representing the subtype of simulation.

            Returns:
                :obj:`Dict` of `List` of model changes, simulation object, variables
        """
        res = get_parameters_variables_outputs_for_simulation(
            model_filename=model_fp,
            model_language=sim_language,
            simulation_type=sim_type
        )
        return {
            'model_changes': res[0],
            'simulation': res[1],
            'variables': res[2]

        }

    def generate_data_object_for_output(
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

    def translate_data_object(self, data_object: SmoldynData, box_size: float, n_dim=3):
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
            file_data_path: str,
            simularium_filename: str,
            box_size: float,
            spatial_units="nm",
            temporal_units="ns",
            n_dim=3,
            display_data: Optional[Dict[str, DisplayData]] = None
            ) -> None:
        input_file = self.prepare_input_file_data(file_data_path)
        data = self.generate_data_object_for_output(
            file_data=input_file,
            display_data=display_data,
            spatial_units=spatial_units,
            temporal_units=temporal_units
        )
        translated = self.translate_data_object(data, box_size, n_dim)
        self.save_simularium_file(translated, simularium_filename)
        print('New Simularium file generated!!')


class SimulationSetupParams(str, Enum):
    project_root = 'biosimulators_simularium'
    model_fp = 'biosimulators_simularium/files/models/ecoli_model.txt'
    ecoli_archive_dirpath = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523'
    sed_doc = os.path.join(ecoli_archive_dirpath, 'simulation.sedml')
    outputs_dirpath = 'biosimulators_simularium/outputs'
