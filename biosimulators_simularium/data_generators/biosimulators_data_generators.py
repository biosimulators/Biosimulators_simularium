from typing import Dict, List, Tuple, Optional
import importlib
import os
import numpy as np
import pandas as pd
import zarr
from simulariumio import (
    TrajectoryConverter,
    TrajectoryData,
    AgentData,
    UnitData,
    MetaData,
    ModelMetaData,
    CameraData,
    DisplayData,
    DISPLAY_TYPE,
)
from biosimulators_utils.config import Config, get_config
from biosimulators_utils.report.io import ReportFormat


def get_run_id(fp: str) -> str:
    i = 0
    files = os.listdir(fp)
    if str(i) in files:
        i = int(files[-1]) + 1
    return str(i)


class GenericBiosimulatorsDataGenerator:
    def __init__(self,
                 module: str,
                 archive_fp: str,
                 output_dir: str,
                 config: Optional[Config] = None,
                 save_conversion: Optional[bool] = True):
        """
        Run a biosimulators general simulation. Wraps `MODULE.biosimulators.combine.exec`\n

        Params
        ______
        `archive_fp: str`: path to OMEX/COMBINE archive file\n
        `output_dir: str`: path to house simulation outputs\n
        `config: Config`: biosimulators common configuration
        """
        self.simulator = importlib.import_module(module)
        self.archive_fp = archive_fp
        self.output_dir = output_dir
        self.save_conversion = save_conversion
        self.config = config or get_config()
        self.config.LOG_PATH = self.output_dir
        self.raw_data = self.get_result()
        self.df = self.get_result_dataframe()

    def get_result(self, archive_fp: str, output_dir: str, config: Config = None) -> Dict:
        config = config or get_config()
        config.REPORT_FORMATS = [ReportFormat.csv]
        config.LOG_PATH = output_dir
        results, log = self.simulator.exec_sedml_docs_in_combine_archive(
            archive_filename=archive_fp,
            out_dir=output_dir,
            config=config
        )
        return {'results': results, 'log': log}

    def to_zarr(self, chunks=(10, 10)) -> zarr.Array:
        data = self.raw_data.get('results')
        return zarr.array(data, chunks=chunks)

    def extract_result_dataframe(self) -> pd.DataFrame:
        csv_dir = os.path.join(self.output_dir, "simulation.sedml")
        for f in os.listdir(csv_dir):
            if f.endswith('.csv'):
                raw_df = pd.read_csv(os.path.join(csv_dir, f), header=None)
                cols = raw_df.pop(0).values.tolist()
                transposed_dataframe = raw_df.T
                return pd.DataFrame(data=transposed_dataframe.values, columns=cols)

    def generate_trajectory_object(self, title: str, df: Optional[pd.DataFrame] = None) -> TrajectoryData:
        df = df or self.df
        timestamps = df.pop('Time').values
        agents = df.values
        box_size = 100
        n_seconds = 100
        # total_steps = 5001
        total_steps = 100
        timestep = n_seconds / total_steps
        n_agents = 12
        type_names = []
        for t in range(total_steps):
            type_names.append(list(set([df.columns.tolist()[i] for i in range(n_agents)])))
        min_radius = 5
        max_radius = 10
        sim_display_data = self.generate_display_data(type_names=type_names)

        return TrajectoryData(
            meta_data=MetaData(
                box_size=np.array([box_size, box_size, box_size]),
                camera_defaults=CameraData(
                    position=np.array([10.0, 0.0, 200.0]),
                    look_at_position=np.array([10.0, 0.0, 0.0]),
                    fov_degrees=60.0,
                ),
                trajectory_title=title,
                model_meta_data=ModelMetaData(
                    title="Spatiotemporal oscillations in the E. coli Min system",
                    version="1.0",
                    authors="Steve Andrews et al.",
                    description=(
                        """
                            A Biosimulators/Smoldyn example model of the E. coli Min system, 
                            which is used to find the cell center during cell division.
                        """
                    ),
                    doi="10.1016/j.bpj.2016.02.002",
                    source_code_url="https://github.com/simularium/simulariumio",
                    source_code_license_url="https://github.com/simularium/simulariumio/blob/main/LICENSE",
                    input_data_url="https://allencell.org/path/to/native/engine/input/files",
                    raw_output_data_url="https://allencell.org/path/to/native/engine/output/files",
                ),
            ),
            agent_data=AgentData(
                times=timestep * np.array(list(range(total_steps))),
                n_agents=np.array(total_steps * [n_agents]),
                viz_types=np.array(total_steps * [n_agents * [1000.0]]),  # default viz type = 1000
                unique_ids=np.array(total_steps * [list(range(n_agents))]),
                types=type_names,
                positions=np.random.uniform(size=(total_steps, n_agents, 3)) * box_size - box_size * 0.5,
                radii=(max_radius - min_radius) * np.random.uniform(size=(total_steps, n_agents)) + min_radius,
                display_data=sim_display_data
            )
        )

    @staticmethod
    def generate_display_data(type_names: List[List[str]]) -> Dict[str, DisplayData]:
        display_data = {}
        for i in range(len(type_names[0])):
            name = type_names[0][i]
            if "in" not in name:
                display_data[name] = DisplayData(
                    name=name,
                    display_type=DISPLAY_TYPE.PDB,
                )
                print(f'NAME: {name}')
        return display_data

    def convert(self, traj_data: TrajectoryData, fname: str) -> None:
        """
        :param traj_data:`TrajectoryData` object instance.
        :param fname:`str`: new simularium filename.
        :return:`None`
        """
        traj = TrajectoryConverter(traj_data)
        if self.save_conversion and not os.path.exists(fname):
            traj.save(fname)

    @staticmethod
    def prepare_simularium_fp(simularium_dirpath: str, simularium_fname: str) -> str:
        if not os.path.exists(simularium_dirpath):
            os.mkdir(simularium_dirpath)
        return os.path.join(simularium_dirpath, simularium_fname)

    @staticmethod
    def get_run_id(fp: str) -> str:
        i = 0
        files = os.listdir(fp)
        if str(i) in files:
            i = int(files[-1]) + 1
        return str(i)


'''
class __BiosimulatorsDataGenerator:
    def __init__(self, module: str, archive_fp: str, output_dir: str, config: Config):
        self.simulator = importlib.import_module(module)

    def get_result(self, archive_fp: str, output_dir: str, config: Config = None) -> Tuple:
        config = config or get_config()
        config.REPORT_FORMATS = [ReportFormat.csv]
        config.LOG_PATH = output_dir
        return self.simulator.exec_sedml_docs_in_combine_archive(
            archive_filename=archive_fp,
            out_dir=output_dir,
            config=config
        )

    @staticmethod
    def extract_result_data(csv_dir: str) -> pd.DataFrame:
        for f in os.listdir(csv_dir):
            if f.endswith('.csv'):
                raw_df = pd.read_csv(os.path.join(csv_dir, f), header=None)
                cols = raw_df.pop(0).values.tolist()
                transposed_dataframe = raw_df.T
                return pd.DataFrame(data=transposed_dataframe.values, columns=cols)

    def to_zarr(self) -> zarr.Array:
        raise NotImplementedError
'''