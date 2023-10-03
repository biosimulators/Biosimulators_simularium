import os
import zipfile
from warnings import warn
from typing import Optional, Tuple, Dict, List, Union
from abc import ABC, abstractmethod
from biosimulators_utils.combine.data_model import CombineArchiveContent
from biosimulators_utils.combine.io import CombineArchiveReader, CombineArchiveWriter
from biosimulators_utils.archive.io import ArchiveReader
from biosimulators_utils.model_lang.smoldyn.validation import validate_model
from biosimulators_simularium.generators.data_model import ModelValidation


# use this to toggle quicktest
TEST = False


class SpatialCombineArchive(ABC):
    paths: Dict[str, str]

    def __init__(self,
                 rootpath: str,
                 simularium_filename: Optional[str] = None,
                 name='new_spatial_archive'):
        """ABC Object for storing and setting/getting files pertaining to simularium file conversion.

            Args:
                rootpath: root of the unzipped archive. Consider this your working dirpath.
                simularium_filename:`Optional`: path which to assign to the newly generated simularium file.
                    Defaults to `{name}_output_for_simularium`.
                name: Commonplace name for the archive to be used if no `simularium_filename` is passed. Defaults to
                    `new_spatial_archive`.
        """
        super().__init__()
        self.rootpath = rootpath
        self.__parse_rootpath()
        self.simularium_filename = simularium_filename or name + '_output_for_simularium'
        self.paths = self.get_all_archive_filepaths()

    def __parse_rootpath(self):
        """Private method for parsing whether `self.rootpath` is the path to a directory or single OMEX/COMBINE
            zipped file. If .omex, then decompress the input path into an unzipped directory for working.
        """
        if self.rootpath.endswith('.omex'):
            reader = ArchiveReader()
            output = self.rootpath.replace('.omex', '_UNZIPPED')  # TODO: make tempdir here instead
            try:
                reader.run(self.rootpath, output)
                print('Omex unzipped!...')
                self.rootpath = output
            except Exception as e:
                warn(f'Omex could not be unzipped because: {e}')

    def get_all_archive_filepaths(self) -> Dict[str, str]:
        """Recursively read the contents of the directory found at `self.rootpath` and set their full paths.

            Returns:
                `Dict[str, str]`: Dict of form {'path_root': full_path}
        """
        paths = {}
        if os.path.exists(self.rootpath):
            for root, _, files in os.walk(self.rootpath):
                paths['root'] = root
                for f in files:
                    fp = os.path.join(root, f)
                    paths[f] = fp
        return paths

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
        return list(set(manifest))[0]

    def read_manifest_contents(self):
        """Reads the contents of the manifest file within `self.rootpath`.
            Read the return value of `self.get_manifest_filepath()` as the input for `CombineArchiveReader.run().
        """
        manifest_fp = self.get_manifest_filepath()
        reader = CombineArchiveReader()
        return reader.read_manifest(filename=manifest_fp)

    @staticmethod
    def generate_new_archive_content(fp: str) -> CombineArchiveContent:
        """Factory for generating a new instance of `CombineArchiveContent` using just fp.

            Args:
                fp: filepath of the content you wish to add to the combine archive.

            Returns:
                `CombineArchiveContent` based on the passed `fp`.
        """
        return CombineArchiveContent(fp)

    def add_simularium_file_to_manifest(self, simularium_fp: Optional[str] = None) -> None:
        """Read the contents of the manifest file found at `self.rootpath`, create a new instance of
            `CombineArchiveContent` using a set simularium_fp, append the new content to the original,
            and re-write the archive to reflect the newly added content.

            Args:
                  simularium_fp:`Optional`: path to the newly generated simularium file. Defaults
                    to `self.simularium_filename`.
        """
        contents = self.read_manifest_contents()
        simularium_fp = simularium_fp or self.simularium_filename
        new_content = self.generate_new_archive_content(simularium_fp)
        contents.append(new_content)
        writer = CombineArchiveWriter()
        try:
            manifest_fp = self.get_manifest_filepath()
            writer.write_manifest(contents=contents, filename=manifest_fp)
            print('Simularium File added to archive manifest contents!')
        except Exception as e:
            print(e)
            warn(f'The simularium file found at {simularium_fp} could not be added to manifest.')
            return

    def verify_smoldyn_in_manifest(self) -> bool:
        """Pass the return value of `self.get_manifest_filepath()` into a new instance of `CombineArchiveReader`
            such that the string manifest object tuples are evaluated for the presence of `smoldyn`.

            Returns:
                `bool`: Whether there exists a smoldyn model in the archive based on the archive's manifest.
        """
        manifest_contents = [c.to_tuple() for c in self.read_manifest_contents()]
        model_info = manifest_contents[0][1]
        return 'smoldyn' in model_info

    @abstractmethod
    def set_model_filepath(self,
                           model_default: str,
                           model_filename: Optional[str] = None) -> Union[str, None]:
        """Recurse `self.rootpath` and search for your simulator's model file extension."""
        pass

    @abstractmethod
    def set_model_output_filepath(self) -> None:
        """Recursively read the directory at `self.rootpath` and standardize the model output filename to become
                    `self.model_output_filename`.
        """
        pass

    @abstractmethod
    def generate_model_validation_object(self) -> ModelValidation:
        """Generate an instance of `ModelValidation` based on the output of `self.model_path`
                    with your simulator's primary validation method.

                Returns:
                    :obj:`ModelValidation`
        """
        pass


class SmoldynCombineArchive(SpatialCombineArchive):
    def __init__(self,
                 rootpath: str,
                 model_output_filename: Optional[str] = None,
                 simularium_filename: Optional[str] = None,
                 name='smoldyn_combine_archive'):
        """Object for handling the output of Smoldyn simulation data. Implementation child of `SpatialCombineArchive`"""
        super().__init__(rootpath, simularium_filename, name)
        self.model_path = self.set_model_filepath()
        self.model_output_filename = model_output_filename \
            or self.model_path.replace('.txt', '') + 'out.txt'
        self.paths['model_output_file'] = self.model_output_filename

    def set_model_filepath(self, model_filename: Optional[str] = None, model_default='model.txt') -> Union[str, None]:
        """Recursively read the full paths of all files in `self.paths` and return the full path of the file
            containing the term 'model.txt', which is the naming convention.
            Implementation of ancestral abstract method.

            Args:
                model_filename: `Optional[str]`: index by which to label a file in directory as the model file.
                    Defaults to `model_default`.
                model_default: `str`: default model filename naming convention. Defaults to `'model.txt'`
        """
        model_filename = model_filename or model_default  # default Smoldyn model name
        for k in self.paths.keys():
            full_path = self.paths[k]
            if model_filename in full_path:
                return full_path
            else:
                return None

    def set_model_output_filepath(self) -> None:
        """Recursively search the directory at `self.rootpath` for a smoldyn
            modelout file (`.txt`) and standardize the model output filename to become
            `self.model_output_filename`. Implementation of ancestral abstract method.
        """
        for root, _, files in os.walk(self.rootpath):
            for f in files:
                if f.endswith('.txt') and 'model' not in f and os.path.exists(f):
                    f = os.path.join(root, f)
                    os.rename(f, self.model_output_filename)

    def generate_model_validation_object(self) -> ModelValidation:
        """Generate an instance of `ModelValidation` based on the output of `self.model_path`
            with `biosimulators-utils.model_lang.smoldyn.validate_model` method.
            Implementation of ancestral abstract method.

        Returns:
            :obj:`ModelValidation`
        """
        validation_info = validate_model(self.model_path)
        validation = ModelValidation(validation_info)
        return validation


def test_smoldyn_archive_with_omex(test: bool):
    """If `TEST`, test the `SmoldynCombineArchive` constructor by passing an `.omex` file as `rootpath`."""
    if test:
        omex_archive_rootpath = 'biosimulators_simularium/tests/fixtures/archives/minE_Andrews_052023'
        omex_archive_fp = omex_archive_rootpath + '.omex'
        simularium_fp = os.path.join(omex_archive_rootpath, 'test_smoldyn_from_omex')
        archive = SmoldynCombineArchive(rootpath=omex_archive_fp, simularium_filename=simularium_fp)
        print(archive.rootpath)
        print(archive.model_path)
        print(archive.model_output_filename)


if __name__ == '__main__':
    test_smoldyn_archive_with_omex(TEST)
