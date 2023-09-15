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
from biosimulators_simularium.utils.io import remove_file, remove_output_files
from biosimulators_simularium.converters.data_model import Archive, SimulariumFilePath, DataConverter


class SmoldynDataConverter(DataConverter):
    def __init__(self,
                 archive_fp: str,
                 output_dirpath: str):
        self.archive = Archive(rootpath=archive_fp, output_dirpath=output_dirpath)
        self.simularium_fp = SimulariumFilePath(path=output_dirpath)
        super().__init__(self.archive, self.simularium_fp)
        # self.archive.model_path = self._set_model_filepath()
        self.model_params = self.get_params_from_model_file(
            model_fp=self.archive.model_filepath,
            sim_language="uri:sedml:language:smoldyn"
        )

    def _set_model_filepath(self) -> Union[str, None]:
        if os.path.exists(self.archive.rootpath):
            for root, _, files in os.walk(self.archive_rootpath):
                for f in files:
                    fp = os.path.join(root, f)
                    if fp.endswith('.txt'):
                        return fp

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


def generate_new_simularium_file(
        archive_dirpath: str,
        rm_files=1
        ) -> None:
    model_out = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523/modelout.txt'
    min_save = 'biosimulators_simularium/files/archives/Andrews_ecoli_0523/MinSave.txt'

    if rm_files:
        remove_file(model_out)
        remove_file(min_save)
        remove_output_files()

    converter = SmoldynDataConverter(archive_fp=archive_dirpath)

    config = Config(
        LOG_PATH=converter.output,
        COLLECT_COMBINE_ARCHIVE_RESULTS=True,
        COLLECT_SED_DOCUMENT_RESULTS=True,
        REPORT_FORMATS=[ReportFormat.h5]
    )


    # model = os.path.join(ECOLI_ARCHIVE_DIRPATH, 'model.txt')
    lang = 'urn:sedml:language:smoldyn'
    sim_params = converter.get_params_from_model_file(model, lang)
    variables_list = sim_params.get('variables')
    mapping = validate_variables(variables_list)

    print(variables_list)
    print()
    print(mapping)

    # NOW MAKE A TASK!

    '''_, _, configuration = validate_model(model)

    simulation = configuration[0]

    simulation.runSim()'''


    '''result, log = generator.run_simulation_from_archive(ECOLI_OMEX_DIRPATH)
    print(result)'''

    '''generator.run_simulation_from_smoldyn_file(
        os.path.join(ECOLI_ARCHIVE_DIRPATH, 'model.txt')
    )'''

    '''result, log = generator.run_simulation_from_archive(
        archive_fp='biosimulators_simularium/files/archives/custom.omex',
    )'''

    # converter = SmoldynDataConverter(OUTPUTS_DIRPATH)

    # r0, r1, r2 = validate_model('biosimulators_simularium/files/archives/Andrews_ecoli_0523/model.txt')
    # print(r2)

    # input_file_data = converter.prepare_input_file_data(model_out)
    # data_object = converter.prepare_smoldyn_data_for_conversion(file_data=input_file_data)

    # trans = converter.translate_data(data_object, 100.)
    # converter.convert_to_simularium(data_object, 'biosimulators_simularium/minE_Andrews')