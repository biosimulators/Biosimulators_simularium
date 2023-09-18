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
"""from biosimulators_simularium.converters.data_model import Archive, SimulariumFilePath, SmoldynDataConverter


def generate_new_simularium_file(archive: Archive, simularium_fp: SimulariumFilePath) -> None:
    converter = SmoldynDataConverter(
        archive=archive,
        simularium_fp=simularium_fp,
    )


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
    
"""