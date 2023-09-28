"""Using the Biosimulators side of Smoldyn to generate a modelout.txt Smoldyn file for a specified OMEX/COMBINE archive which then
    is used to generate a .simularium file for the given simulation. That .simularium file is then stored along with the log.yml and
    report.{FORMAT} relative to the simulation. Remember: each simulation, while not inherently published, has the potential for publication
    based purely on the simulation's ability to provide a valid OMEX/COMBINE archive. There exists (or should exist) an additional layer
    of abstraction to then validate and verify the contents therein.
"""


# pragma: no cover


import os
import zipfile
from warnings import warn
from typing import Optional, Tuple, Dict, List, Union
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from smoldyn import Simulation as smoldynSim
from simulariumio import (
    CameraData,
    UnitData,
    MetaData,
    DisplayData,
    DISPLAY_TYPE,
    BinaryWriter,
)
from simulariumio.smoldyn.smoldyn_data import InputFileData
from simulariumio.smoldyn import SmoldynConverter, SmoldynData
from simulariumio.filters import TranslateFilter
from simulariumio.data_objects.trajectory_data import TrajectoryData, AgentData
from biosimulators_utils.combine.io import CombineArchiveReader
from biosimulators_utils.archive.io import ArchiveReader, ArchiveWriter
from biosimulators_utils.model_lang.smoldyn.validation import validate_model


__all__ = [
    'SmoldynCombineArchive',
    'BiosimulatorsDataConverter',
    'SmoldynDataConverter',
]


def extract_omex(zipped_path, output=None):
    reader = ArchiveReader()
    if output is None:
        output = zipped_path.replace('.omex', '')
    reader.run(zipped_path, output)


def __extract_omex(omex_filename, output_folder):
    with zipfile.ZipFile(omex_filename, 'r') as zip_ref:
        zip_ref.extractall(output_folder)


class ModelValidation:
    def __init__(self, validation: Tuple[List[List[str]], List, Tuple[smoldynSim, List[str]]]):
        self.errors = validation[0]
        self.warnings = validation[1]
        self.simulation = validation[2][0]
        self.config = validation[2][1]


class AgentDisplayData:
    def __init__(self,
                 name: Optional[str] = None,
                 radius: Optional[float] = None,
                 display_type=None,
                 url: Optional[str] = None,
                 color: Optional[str] = None):
        """A class whose purpose is storing the configuration of a `simulariumio.DisplayData` object.

            Args:
                name(:obj:`str`): `Optional`: Defaults to None.
                radius(:obj:`float`): `Optional`: Radius of the particular agent display. Defaults to None.
                display_type(:obj:`Enum[str]`): `Optional`: One of the `simulariumio.DISPLAY_TYPE` types of geometry
                    used for the agent display. Defaults to None.
                url(:obj:`str`): `Optional`: Url from which the agent display is derived. Defaults to None.
                color(:obj:`str`): `Optional`: Color of the agent display in hex form ie: `#NNNNNN`. Defaults to None.
        """
        self.name = name
        self.radius = radius
        self.display_type = display_type
        self.url = url
        self.color = color


class SmoldynCombineArchive:
    def __init__(self,
                 rootpath: str,
                 outputs_dirpath: Optional[str] = None,
                 model_output_filename: Optional[str] = None,
                 simularium_filename: Optional[str] = None,
                 name='my_combine_archive'):
        """Object for handling the output of Smoldyn simulation data. An implementation of the abstract class
            `SpatialCombineArchive`. """
        self.rootpath = rootpath
        self.__handle_rootpath()
        self.outputs_dirpath = outputs_dirpath
        self.simularium_filename = simularium_filename or f'{name}_output_for_simularium'
        self.paths = self.get_all_archive_filepaths()
        self.model_path = self.set_model_filepath()

        self.model_output_filename = model_output_filename \
            or self.model_path.replace('.txt', '') + 'out.txt'
        self.paths['model_output_file'] = self.model_output_filename

    def __handle_rootpath(self):
        if self.rootpath.endswith('.omex'):
            reader = ArchiveReader()
            output = self.rootpath.replace('.omex', '')
            reader.run(self.rootpath, output)
            self.rootpath = output

    def get_all_archive_filepaths(self) -> Dict[str, str]:
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

    def set_model_output_filepath(self):
        for root, _, files in os.walk(self.rootpath):
            for f in files:
                if f.endswith('.txt') and 'model' not in f and os.path.exists(f):
                    f = os.path.join(root, f)
                    os.rename(f, self.model_output_filename)

    def get_manifest_filepath(self) -> Union[List[str], str]:
        """Read SmoldynCombineArchive manifest files. Return all filepaths containing the word 'manifest'.

            Returns:
                :obj:`str`: path if there is just one manifest file, otherwise `List[str]` of manifest filepaths.
        """
        manifest = []
        for v in list(self.paths.values()):
            if 'manifest' in v:
                manifest.append(v)
                self.paths['manifest'] = v
        return manifest if len(manifest) > 1 else manifest[0]

    def verify_smoldyn_in_manifest(self) -> bool:
        """Pass the return value of `self.get_manifest_filepath()` into a new instance of `CombineArchiveReader`
            such that the string manifest object tuples are evaluated for the presence of `smoldyn`.

            Returns:
                `bool`: Whether there exists a smoldyn model in the archive based on the archive's manifest.
        """
        manifest = self.get_manifest_filepath()
        reader = CombineArchiveReader()
        manifest_contents = [c.to_tuple() for c in reader.read_manifest(manifest)]
        model_info = manifest_contents[0][1]
        return 'smoldyn' in model_info

    def generate_model_validation_object(self) -> ModelValidation:
        """Generate an instance of `ModelValidation` based on the output of `self.model_path`
            with `biosimulators-utils.model_lang.smoldyn.validate_model` method.

        Returns:
            :obj:`ModelValidation`
        """
        validation_info = validate_model(self.model_path)
        validation = ModelValidation(validation_info)
        return validation


class BiosimulatorsDataConverter(ABC):
    def __init__(self, archive: SmoldynCombineArchive):
        """This class serves as the abstract interface for a simulator-specific implementation
            of utilities through which the user may convert Biosimulators outputs to a valid simularium File.

                Args:
                    :obj:`archive`:(`SmoldynCombineArchive`): instance of a `SmoldynCombineArchive` object.
        """
        self.archive = archive
        self.has_smoldyn = self.archive.verify_smoldyn_in_manifest()

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
    def translate_data_object(self, data_object, box_size, n_dim) -> TrajectoryData:
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

    def prepare_agent_data(self) -> AgentData:
        """Create a new instance of an `AgentData` object following the specifications of the simulation within the
            relative combine archive.
        """
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

    def generate_display_data_object_dict(self, agent_names: List[Tuple[str, str, float, str]]) -> Dict[str, DisplayData]:
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
        return BinaryWriter.save(data, simularium_filename, validate_ids=True) \
            if not os.path.exists(simularium_filename) else None

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
    def __init__(self, archive: SmoldynCombineArchive, generate_model_output: bool = True):
        """General class for converting Smoldyn output (modelout.txt) to .simularium. Checks the passed archive object
            directory for a `modelout.txt` file (standard Smoldyn naming convention) and runs the simulation by default if
            not. At the time of construction, checks for the existence of a simulation `out.txt` file and runs
            `self.generate_model_output_file()` if such a file does not exist, based on `self.archive`. To turn
            this off, pass `generate_data` as `False`.

            Args:
                archive (:obj:`SmoldynCombineArchive`): instance of a `SmoldynCombineArchive` object.
                generate_model_output(`bool`): Automatically generates and standardizes the name of a
                    smoldyn model output file based on the `self.archive` parameter if True. Defaults to `True`.
        """
        super().__init__(archive)
        if generate_model_output:
            self.generate_model_output_file()

    def generate_model_output_file(self,
                                   model_output_filename: Optional[str] = None,
                                   smoldyn_archive: Optional[SmoldynCombineArchive] = None) -> None:
        """Generate a modelout file if one does not exist using the `ModelValidation` interface via
            `.utils.generate_model_validation_object` method. If either parameter is not passed, the data will
            be derived from `self.archive(:obj:`SmoldynCombineArchive`)`.

            Args:
                model_output_filename(:obj:`str`): `Optional`: filename from which to run a smoldyn simulation
                    and generate an out.txt file. Defaults to `self.archive.model_output_filename`.
                smoldyn_archive(:obj:`SmoldynCombineArchive`): `Optional`: instance of `SmoldynCombineArchive` from
                    which to base the simulation/model.txt from. Defaults to `self.archive`.

            Returns:
                None
        """
        model_output_filename = model_output_filename or self.archive.model_output_filename
        archive = smoldyn_archive or self.archive
        if not os.path.exists(model_output_filename):
            validation = archive.generate_model_validation_object()
            validation.simulation.runSim()

        # standardize the modelout filename
        for root, _, files in os.walk(archive.rootpath):
            for f in files:
                if f.endswith('.txt') and 'model' not in f:
                    f = os.path.join(root, f)
                    os.rename(f, archive.model_output_filename)

    def read_model_output_dataframe(self) -> pd.DataFrame:
        colnames = ['mol_name', 'x', 'y', 'z', 't']
        return pd.read_csv(self.archive.model_output_filename, sep=" ", header=None, skiprows=1, names=colnames)

    def write_model_output_dataframe_to_csv(self, save_fp: str) -> None:
        df = self.read_model_output_dataframe()
        return df.to_csv(save_fp)

    def generate_output_data_object(
            self,
            file_data: InputFileData,
            display_data: Optional[Dict[str, DisplayData]] = None,
            meta_data: Optional[MetaData] = None,
            spatial_units="nm",
            temporal_units="ns",
            ) -> SmoldynData:
        """Generate a new instance of `SmoldynData`. If passing `meta_data`, please create a new `MetaData` instance
            using the `self.generate_metadata_object` interface of this same class.

        Args:
            file_data: (:obj:`InputFileData`): `simulariumio.InputFileData` instance based on model output.
            display_data: (:obj:`Dict[Dict[str, DisplayData]]`): `Optional`: if passing this parameter, please
                use the `self.generate_display_object_dict` interface of this same class.
            meta_data: (:obj:`Metadata`): new instance of `Metadata` object. If passing this parameter, please use the
                `self.generate_metadata_object` interface method of this same class.
            spatial_units: (:obj:`str`): spatial units by which to measure this simularium output. Defaults to `nm`.
            temporal_units: (:obj:`str`): time units to base this simularium instance on. Defaults to `ns`.

        Returns:
            :obj:`SmoldynData`
        """
        return SmoldynData(
            smoldyn_file=file_data,
            spatial_units=UnitData(spatial_units),
            time_units=UnitData(temporal_units),
            display_data=display_data,
            meta_data=meta_data
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
            temporal_units="s",
            n_dim=3,
            simularium_filename: Optional[str] = None,
            display_data: Optional[Dict[str, DisplayData]] = None,
            new_omex_filename: Optional[str] = None,
            translate=True,
            overwrite=True
            ) -> None:
        """Generate a new simularium file based on `self.archive.rootpath`. If `self.archive.rootpath` is an `.omex`
            file, the outputs will be re-bundled.

            Args:
                box_size(:obj:`float`): `Optional`: size by which to scale the simulation stage. Defaults to `1.`
                spatial_units(:obj:`str`): `Optional`: units by which to measure the spatial aspect
                    of the simulation. Defaults to `nm`.
                temporal_units(:obj:`str`): `Optional`: units by which to measure the temporal aspect
                    of the simulation. Defaults to `s`.
                n_dim(:obj:`int`): `Optional`: n dimensions of the simulation output. Defaults to `3`.
                simularium_filename(:obj:`str`): `Optional`: filename by which to save the simularium output. Defaults
                    to `archive.simularium_filename`.
                display_data(:obj:`Dict[str, DisplayData]`): `Optional`: Dictionary of DisplayData objects.
                new_omex_filename(:obj:`str`): `Optional`: Filename by which to save the newly generate .omex IF and
                    only IF `self.archive.rootpath` is an `.omex` file.
                translate(:obj:`bool`): Whether to translate the simulation mirror data. Defaults to `True`.
                overwrite(:obj:`bool`): Whether to overwrite a simularium file of the same name as `simularium_filename`
                    if one already exists in the COMBINE archive. Defaults to `True`.
        """
        if not simularium_filename:
            simularium_filename = os.path.join(self.archive.rootpath, self.archive.simularium_filename)

        if os.path.exists(simularium_filename):
            warn('That file already exists in this COMBINE archive.')
            if not overwrite:
                warn('Overwrite is turned off an thus a new file will not be generated.')
                return

        input_file = self.generate_input_file_data_object()
        data = self.generate_output_data_object(
            file_data=input_file,
            display_data=display_data,
            spatial_units=spatial_units,
            temporal_units=temporal_units
        )

        if translate:
            data = self.translate_data_object(data, box_size, n_dim)

        self.save_simularium_file(data, simularium_filename)
        print('New Simularium file generated!!')
        if '.omex' in self.archive.rootpath:
            writer = ArchiveWriter()
            paths = list(self.archive.get_all_archive_filepaths().values())
            writer.run(paths, self.archive.rootpath)
            print('Omex bundled!')

