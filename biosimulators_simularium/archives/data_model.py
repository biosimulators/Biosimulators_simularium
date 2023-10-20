"""Objects for the storage, retrieval, and calculation of data pertaining to OMEX/Combine archives whose contents
    are directly related to purely spatial simulations. Several objects are copied directly from biosimulators-utils
    for ease of development, as they exist within the same organization.

:Author: Alexander Patrie <apatrie@uchc.edu> / Jonathan Karr
:Date: 2023-09-16
:Copyright: 2023, UConn Health
:License: MIT
"""


import os
import re
import zipfile
from zipfile import ZipFile as Zip
import enum
from warnings import warn
from typing import Optional, Tuple, Dict, List, Union
from abc import ABC, abstractmethod
import libcombine
from biosimulators_simularium.converters.utils import validate_model, ModelValidation
from biosimulators_simularium.utils.core import (
    are_lists_equal,
    none_sorted,
    flatten_nested_list_of_strings
)
from biosimulators_simularium.config import Config, get_config
from biosimulators_simularium.biosimulators_warning import warn, BioSimulatorsWarning


__all__ = [
    'Archive',
    'ArchiveFile',
    'ArchiveReader',
    'ArchiveWriter',
    'SpatialCombineArchive',
    'SmoldynCombineArchive'
]


class Archive(object):
    """ An archive (e.g., zip file)

    Attributes:
        files (:obj:`list` of :obj:`ArchiveFile`): files
    """

    def __init__(self, files=None):
        """
        Args:
            files (:obj:`list` of :obj:`ArchiveFile`, optional): files
        """
        self.files = files or []

    def to_tuple(self):
        """ Tuple representation of an archive

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation of an archive
        """
        return (
            tuple(none_sorted(file.to_tuple() for file in self.files)),
        )

    def is_equal(self, other):
        """ Determine if two archives are equal

        Args:
            other (:obj:`ArchiveFile`): another archive

        Returns:
            :obj:`bool`: :obj:`True`, if two archives are equal
        """
        return self.__class__ == other.__class__ \
            and are_lists_equal(self.files, other.files)


class ArchiveFile(object):
    """ A file in a archive (e.g., zip file)

    Attributes:
        local_path (:obj:`str`): path within local filesytem
        archive_path (:obj:`str`): archive_path
    """

    def __init__(self, local_path=None, archive_path=None):
        """
        Args:
            local_path (:obj:`str`, optional): path within local filesytem
            archive_path (:obj:`str`, optional): archive_path
        """
        self.local_path = local_path
        self.archive_path = archive_path

    def to_tuple(self):
        """ Tuple representation of a file

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation of a file
        """
        return (self.local_path, self.archive_path)

    def is_equal(self, other):
        """ Determine if two files are equal

        Args:
            other (:obj:`ArchiveFile`): another file

        Returns:
            :obj:`bool`: :obj:`True`, if two files are equal
        """
        return self.__class__ == other.__class__ \
            and self.local_path == other.local_path \
            and self.archive_path == other.archive_path


class ArchiveWriter(object):
    """ Class for writing zip archives """

    def run(self, archive, archive_filename):
        """ Bundle a list of files into a zip archive

        Args:
            archive (:obj:`Archive`): files to bundle into a zip archive
            archive_filename (:obj:`str`): path to save zip file
        """
        with zipfile.ZipFile(archive_filename, mode='w', compression=zipfile.ZIP_LZMA) as zip_file:
            for file in archive.files:
                zip_file.write(file.local_path, arcname=file.archive_path)


class ArchiveReader(object):
    """ Class for reading zip archives """

    def run(self, archive_filename, out_dir=None):
        """ Unpack the files in a zip archive

        Args:
            archive_filename (:obj:`str`): path to zip file
            out_dir (:obj:`str`, optional): path to unpack files

        Returns:
            archive (:obj:`Archive`): files unbundled from zip archive
        """
        archive = Archive()
        with zipfile.ZipFile(archive_filename, mode='r') as zip_file:
            for member in zip_file.namelist():
                archive.files.append(ArchiveFile(
                    archive_path=member,
                    local_path=os.path.join(out_dir, member) if out_dir else None,
                ))
            if out_dir:
                zip_file.extractall(out_dir)
        return archive


class CombineArchiveBase(ABC):
    """ A COMBINE/OMEX archive """
    pass


class CombineArchive(CombineArchiveBase):
    """ A COMBINE/OMEX archive

    Attributes:
        contents (:obj:`list` of :obj:`CombineArchiveContent`): contents of the archive
    """

    def __init__(self, contents=None):
        """
        Args:
            contents (:obj:`list` of :obj:`CombineArchiveContent`, optional): contents of the archive
        """
        self.contents = contents or []

    def get_master_content(self):
        """ Get the master content of an archive

        Returns:
            :obj:`list` of :obj:`CombineArchiveContent`: master content
        """
        master_content = []
        for content in self.contents:
            if content.master:
                master_content.append(content)
        return master_content

    def to_tuple(self):
        """ Tuple representation of a COMBINE/OMEX archive

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation of a COMBINE/OMEX archive
        """
        contents = tuple(none_sorted(content.to_tuple() for content in self.contents))
        return (contents)

    def is_equal(self, other):
        """ Determine if two content items are equal

        Args:
            other (:obj:`CombineArchiveContent`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two archives are equal
        """
        return self.__class__ == other.__class__ \
            and are_lists_equal(self.contents, other.contents)


class CombineArchiveContent(CombineArchiveBase):
    """ A content item (e.g., file) in a COMBINE/OMEX archive

    Attributes:
        location (:obj:`str`): path to the content
        format (:obj:`str`): URL for the specification of the format of the content
        master (:obj:`bool`): :obj:`True`, if the content is the "primary" content of the parent archive
    """

    def __init__(self, location=None, format=None, master=False):
        """
        Args:
            location (:obj:`str`, optional): path to the content
            format (:obj:`str`, optional): URL for the specification of the format of the content
            master (:obj:`bool`, optional): :obj:`True`, if the content is the "primary" content of the parent archive
        """
        self.location = location
        self.format = format
        self.master = master

    def to_tuple(self):
        """ Tuple representation of a content item of a COMBINE/OMEX archive

        Returns:
            :obj:`tuple` of :obj:`str`: tuple representation of a content item of a COMBINE/OMEX archive
        """
        return (self.location, self.format, self.master)

    def is_equal(self, other):
        """ Determine if two content items are equal

        Args:
            other (:obj:`CombineArchiveContent`): another content item

        Returns:
            :obj:`bool`: :obj:`True`, if two content items are equal
        """
        return self.__class__ == other.__class__ \
            and self.location == other.location \
            and self.format == other.format \
            and self.master == other.master


class CombineArchiveContentFormat(str, enum.Enum):
    """ Format for the content of COMBINE/OMEX archives """
    ACTIONSCRIPT = 'http://purl.org/NET/mediatypes/text/x-actionscript'
    ADOBE_FLASH = 'http://purl.org/NET/mediatypes/application/x-shockwave-flash'
    AI = 'http://purl.org/NET/mediatypes/application/pdf'
    BioPAX = 'http://identifiers.org/combine.specifications/biopax'
    BMP = 'http://purl.org/NET/mediatypes/image/bmp'
    BNGL = 'http://purl.org/NET/mediatypes/text/bngl+plain'
    BOURNE_SHELL = 'http://purl.org/NET/mediatypes/text/x-sh'
    C = 'http://purl.org/NET/mediatypes/text/x-c'
    CellML = 'http://identifiers.org/combine.specifications/cellml'
    CopasiML = 'http://purl.org/NET/mediatypes/application/x-copasi'
    CPP_HEADER = 'http://purl.org/NET/mediatypes/text/x-c++hdr'
    CPP_SOURCE = 'http://purl.org/NET/mediatypes/text/x-c++src'
    CSS = 'http://purl.org/NET/mediatypes/text/css'
    CSV = 'http://purl.org/NET/mediatypes/text/csv'
    DLL = 'http://purl.org/NET/mediatypes/application/vnd.microsoft.portable-executable'
    DOC = 'http://purl.org/NET/mediatypes/application/msword'
    DOCX = 'http://purl.org/NET/mediatypes/application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    EPS = 'http://purl.org/NET/mediatypes/application/postscript'
    Escher = 'http://purl.org/NET/mediatypes/application/escher+json'
    GENESIS = 'http://purl.org/NET/mediatypes/text/x-genesis'
    GIF = 'http://purl.org/NET/mediatypes/image/gif'
    GINML = 'http://purl.org/NET/mediatypes/application/ginml+xml'
    GMSH_MESH = 'http://purl.org/NET/mediatypes/model/mesh'
    GRAPHML = 'http://purl.org/NET/mediatypes/application/graphml+xml'
    HDF5 = 'http://purl.org/NET/mediatypes/application/x-hdf'
    HOC = 'http://purl.org/NET/mediatypes/text/x-hoc'
    HTML = 'http://purl.org/NET/mediatypes/text/html'
    ICO = 'http://purl.org/NET/mediatypes/image/x-icon'
    INI = 'http://purl.org/NET/mediatypes/text/x-ini'
    IPython_Notebook = 'http://purl.org/NET/mediatypes/application/x-ipynb+json'
    JAVA_ARCHIVE = 'http://purl.org/NET/mediatypes/application/java-archive'
    JAVA_CLASS = 'http://purl.org/NET/mediatypes/application/java-vm'
    JAVA_SOURCE = 'http://purl.org/NET/mediatypes/text/x-java'
    JAVASCRIPT = 'http://purl.org/NET/mediatypes/text/javascript'
    JPEG = 'http://purl.org/NET/mediatypes/image/jpeg'
    JSON = 'http://purl.org/NET/mediatypes/application/json'
    Kappa = 'http://purl.org/NET/mediatypes/text/x-kappa'
    LEMS = 'http://purl.org/NET/mediatypes/application/lems+xml'
    MAPLE_WORKSHEET = 'http://purl.org/NET/mediatypes/application/x-maple'
    MARKDOWN = 'http://purl.org/NET/mediatypes/text/markdown'
    MASS = 'http://purl.org/NET/mediatypes/application/mass+json'
    MATHEMATICA_NOTEBOOK = 'http://purl.org/NET/mediatypes/application/vnd.wolfram.mathematica'
    MATLAB = 'http://purl.org/NET/mediatypes/text/x-matlab'
    MATLAB_DATA = 'http://purl.org/NET/mediatypes/application/x-matlab-data'
    MATLAB_FIGURE = 'http://purl.org/NET/mediatypes/application/matlab-fig'
    MorpheusML = 'http://purl.org/NET/mediatypes/application/morpheusml+xml'
    NCS = 'http://purl.org/NET/mediatypes/text/x-ncs'
    NeuroML = 'http://identifiers.org/combine.specifications/neuroml'
    NEURON_SESSION = 'http://purl.org/NET/mediatypes/text/x-nrn-ses'
    NMODL = 'http://purl.org/NET/mediatypes/text/x-nmodl'
    NuML = 'http://purl.org/NET/mediatypes/application/numl+xml'
    ODE = 'http://purl.org/NET/mediatypes/text/x-ode'
    ODT = 'http://purl.org/NET/mediatypes/application/vnd.oasis.opendocument.text'
    OMEX = 'http://identifiers.org/combine.specifications/omex'
    OMEX_MANIFEST = 'http://identifiers.org/combine.specifications/omex-manifest'
    OMEX_METADATA = 'http://identifiers.org/combine.specifications/omex-metadata'
    OWL = 'http://purl.org/NET/mediatypes/application/rdf+xml'
    PDF = 'http://purl.org/NET/mediatypes/application/PDF'
    PERL = 'http://purl.org/NET/mediatypes/text/x-perl'
    pharmML = 'http://purl.org/NET/mediatypes/application/pharmml+xml'
    PHP = 'http://purl.org/NET/mediatypes/application/x-httpd-php'
    PNG = 'http://purl.org/NET/mediatypes/image/png'
    POSTSCRIPT = 'http://purl.org/NET/mediatypes/application/postscript'
    PPT = 'http://purl.org/NET/mediatypes/application/vnd.ms-powerpoint'
    PPTX = 'http://purl.org/NET/mediatypes/application/vnd.openxmlformats-officedocument.presentationml.presentation'
    PSD = 'http://purl.org/NET/mediatypes/image/vnd.adobe.photoshop'
    Python = 'http://purl.org/NET/mediatypes/application/x-python-code'
    QUICKTIME = 'http://purl.org/NET/mediatypes/video/quicktime'
    R = 'http://purl.org/NET/mediatypes/text/x-r'
    R_Project = 'http://purl.org/NET/mediatypes/application/x-r-project'
    RBA = 'http://purl.org/NET/mediatypes/application/rba+zip'
    RDF_XML = 'http://purl.org/NET/mediatypes/application/rdf+xml'
    RST = 'http://purl.org/NET/mediatypes/text/x-rst'
    RUBY = 'http://purl.org/NET/mediatypes/text/x-ruby'
    SBGN = 'http://identifiers.org/combine.specifications/sbgn'
    SBML = 'http://identifiers.org/combine.specifications/sbml'
    SBOL = 'http://identifiers.org/combine.specifications/sbol'
    SBOL_VISUAL = 'http://identifiers.org/combine.specifications/sbol-visual'
    Scilab = 'http://purl.org/NET/mediatypes/application/x-scilab'
    SED_ML = 'http://identifiers.org/combine.specifications/sed-ml'
    SHOCKWAVE_FLASH = 'http://purl.org/NET/mediatypes/application/x-shockwave-flash'
    SimBiology_Project = 'http://purl.org/NET/mediatypes/application/x-sbproj'
    SLI = 'http://purl.org/NET/mediatypes/text/x-sli'
    Smoldyn = 'http://purl.org/NET/mediatypes/text/smoldyn+plain'
    SO = 'http://purl.org/NET/mediatypes/application/x-sharedlib'
    SQL = 'http://purl.org/NET/mediatypes/application/sql'
    SVG = 'http://purl.org/NET/mediatypes/image/svg+xml'
    SVGZ = 'http://purl.org/NET/mediatypes/image/svg+xml-compressed'
    TEXT = 'http://purl.org/NET/mediatypes/text/plain'
    TIFF = 'http://purl.org/NET/mediatypes/image/tiff'
    TSV = 'http://purl.org/NET/mediatypes/text/tab-separated-values'
    VCML = 'http://purl.org/NET/mediatypes/application/vcml+xml'
    Vega = 'http://purl.org/NET/mediatypes/application/vnd.vega.v5+json'
    Vega_Lite = 'http://purl.org/NET/mediatypes/application/vnd.vegalite.v3+json'
    WEBP = 'http://purl.org/NET/mediatypes/image/webp'
    XML = 'http://purl.org/NET/mediatypes/application/xml'
    XPP = 'http://purl.org/NET/mediatypes/text/x-ode'
    XPP_AUTO = 'http://purl.org/NET/mediatypes/text/x-ode-auto'
    XPP_SET = 'http://purl.org/NET/mediatypes/text/x-ode-set'
    XLS = 'http://purl.org/NET/mediatypes/application/vnd.ms-excel'
    XLSX = 'http://purl.org/NET/mediatypes/application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    XSL = 'http://purl.org/NET/mediatypes/application/xslfo+xml'
    XUL = 'http://purl.org/NET/mediatypes/text/xul'
    XYZ = 'http://purl.org/NET/mediatypes/chemical/x-xyz'
    YAML = 'http://purl.org/NET/mediatypes/application/x-yaml'
    ZGINML = 'http://purl.org/NET/mediatypes/application/zginml+zip'
    ZIP = 'http://purl.org/NET/mediatypes/application/zip'
    OTHER = 'http://purl.org/NET/mediatypes/application/octet-stream'


class CombineArchiveContentFormatPattern(str, enum.Enum):
    """ Format for the content of COMBINE/OMEX archives """
    ACTIONSCRIPT = r'^https?://purl\.org/NET/mediatypes/text/x-actionscript$'
    ADOBE_FLASH = r'^https?://purl\.org/NET/mediatypes/(application/x-shockwave-flash|application/vnd\.adobe\.flash-movie)$'
    AI = r'^https?://purl\.org/NET/mediatypes/(application/pdf|application/postscript)$'
    BioPAX = r'^https?://identifiers\.org/combine\.specifications/biopax($|\.)'
    BMP = r'^https?://purl\.org/NET/mediatypes/image/bmp$'
    BNGL = r'^https?://purl\.org/NET/mediatypes/text/bngl\+plain($|\.)'
    BOURNE_SHELL = r'^https?://purl\.org/NET/mediatypes/(text/x-sh|application/x-sh)$'
    C = r'^https?://purl\.org/NET/mediatypes/text/x-c$'
    CellML = r'^https?://identifiers\.org/combine\.specifications/cellml($|\.)'
    CPP_HEADER = r'^https?://purl\.org/NET/mediatypes/text/x-c\+\+hdr$'
    CPP_SOURCE = r'^https?://purl\.org/NET/mediatypes/text/x-c\+\+src$'
    CopasiML = r'^https?://purl\.org/NET/mediatypes/application/x-copasi$'
    CSS = r'^https?://purl\.org/NET/mediatypes/text/css$'
    CSV = r'^https?://purl\.org/NET/mediatypes/text/csv$'
    DLL = r'^https?://purl\.org/NET/mediatypes/application/vnd\.microsoft\.portable-executable$'
    DOC = r'^https?://purl\.org/NET/mediatypes/application/msword$'
    DOCX = r'^https?://purl\.org/NET/mediatypes/application/vnd\.openxmlformats-officedocument\.wordprocessingml\.document$'
    EPS = r'^https?://purl\.org/NET/mediatypes/(application/postscript|application/eps|application/x-eps|image/eps|image/x-eps)$'
    Escher = r'^https?://purl\.org/NET/mediatypes/application/escher\+json$'
    GENESIS = r'^https?://purl\.org/NET/mediatypes/text/x-genesis$'
    GIF = r'^https?://purl\.org/NET/mediatypes/image/gif$'
    GINML = r'^https?://purl\.org/NET/mediatypes/application/ginml\+xml$'
    GMSH_MESH = r'^https?://purl\.org/NET/mediatypes/model/mesh$'
    GRAPHML = r'^https?://purl\.org/NET/mediatypes/(application/graphml\+xml|application/x-graphml\+xml)$'
    HDF5 = r'^https?://purl\.org/NET/mediatypes/application/x-hdf5?$'
    HOC = r'^https?://purl\.org/NET/mediatypes/text/x-hoc$'
    HTML = r'^https?://purl\.org/NET/mediatypes/(text/html|application/xhtml\+xml)$'
    ICO = r'^https?://purl\.org/NET/mediatypes/(image/x-icon|image/vnd\.microsoft\.icon)$'
    INI = r'^https?://purl\.org/NET/mediatypes/text/x-ini$'
    IPython_Notebook = r'^https?://purl\.org/NET/mediatypes/application/x-ipynb\+json$'
    JAVA_ARCHIVE = (
        r'^https?://purl\.org/NET/mediatypes/('
        r'application/java-archive'
        r'|application/x-java-archive'
        r'|application/jar'
        r'|application/x-jar'
        r')$'
    )
    JAVA_CLASS = r'^https?://purl\.org/NET/mediatypes/(application/java-vm|application/x-java-vm|application/java|application/x-java)$'
    JAVA_SOURCE = r'^https?://purl\.org/NET/mediatypes/(text/x-java|text/x-java-source)$'
    JAVASCRIPT = r'^https?://purl\.org/NET/mediatypes/(text/javascript|text/x-javascript|application/javascript|application/x-javascript)$'
    JPEG = r'^https?://purl\.org/NET/mediatypes/image/jpeg$'
    JSON = r'^https?://purl\.org/NET/mediatypes/application/json$'
    Kappa = r'^https?://purl\.org/NET/mediatypes/text/x-kappa$'
    LEMS = r'^https?://purl\.org/NET/mediatypes/application/lems\+xml$'
    MAPLE_WORKSHEET = r'^https?://purl\.org/NET/mediatypes/application/x-maple$'
    MARKDOWN = r'^https?://purl\.org/NET/mediatypes/text/markdown$'
    MASS = r'^https?://purl\.org/NET/mediatypes/application/mass\+json$'
    MATHEMATICA_NOTEBOOK = r'^https?://purl\.org/NET/mediatypes/application/vnd\.wolfram\.mathematica$'
    MATLAB = r'^https?://purl\.org/NET/mediatypes/text/x-matlab$'
    MATLAB_DATA = r'^https?://purl\.org/NET/mediatypes/application/x-matlab-data$'
    MATLAB_FIGURE = r'^https?://purl\.org/NET/mediatypes/application/matlab-fig$'
    MorpheusML = r'^https?://purl\.org/NET/mediatypes/application/morpheusml\+xml$'
    NCS = r'^https?://purl\.org/NET/mediatypes/text/x-ncs$'
    NeuroML = r'^https?://identifiers\.org/combine\.specifications/neuroml($|\.)'
    NEURON_SESSION = r'^https?://purl\.org/NET/mediatypes/text/x-nrn-ses$'
    NMODL = r'^https?://purl\.org/NET/mediatypes/text/x-nmodl$'
    NuML = r'^https?://purl\.org/NET/mediatypes/application/numl\+xml$'
    ODE = r'^https?://purl\.org/NET/mediatypes/text/x-(ode|xpp)$'
    ODT = r'^https?://purl\.org/NET/mediatypes/application/vnd\.oasis\.opendocument\.text$'
    OMEX = r'^https?://identifiers\.org/combine\.specifications/omex($|\.)'
    OMEX_MANIFEST = r'^https?://identifiers\.org/combine\.specifications/omex-manifest($|\.)'
    OMEX_METADATA = r'^https?://identifiers\.org/combine\.specifications/omex-metadata($|\.)'
    OWL = r'^https?://purl\.org/NET/mediatypes/application/rdf\+xml$'
    PDF = r'^https?://purl\.org/NET/mediatypes/application/pdf$'
    PERL = r'^https?://purl\.org/NET/mediatypes/(text/x-perl|application/x-perl)$'
    pharmML = r'^https?://purl\.org/NET/mediatypes/application/pharmml\+xml$'
    PHP = r'^https?://purl\.org/NET/mediatypes/(application/x-httpd-php|application/x-httpd-php-source|application/x-php|text/x-php)$'
    PNG = r'^https?://purl\.org/NET/mediatypes/image/png$'
    POSTSCRIPT = r'^https?://purl\.org/NET/mediatypes/application/postscript$'
    PPT = r'^https?://purl\.org/NET/mediatypes/application/vnd\.ms-powerpoint$'
    PPTX = r'^https?://purl\.org/NET/mediatypes/application/vnd\.openxmlformats-officedocument\.presentationml\.presentation$'
    PSD = (
        r'^https?://purl\.org/NET/mediatypes/('
        r'image/vnd\.adobe\.photoshop'
        r'|image/psd'
        r'|image/x-psd'
        r'|application/photoshop'
        r'|application/x-photoshop'
        r'|application/psd'
        r'|application/x-psd'
        r')$'
    )
    Python = r'^https?://purl\.org/NET/mediatypes/application/x-python-code$'
    QUICKTIME = r'^https?://purl\.org/NET/mediatypes/(video/quicktime|image/mov)$'
    R = r'^https?://purl\.org/NET/mediatypes/text/x-r$'
    R_Project = r'^https?://purl\.org/NET/mediatypes/application/x-r-project$'
    RBA = r'^https?://purl\.org/NET/mediatypes/application/rba\+zip$'
    RDF_XML = r'^https?://purl\.org/NET/mediatypes/application/rdf\+xml$'
    RST = r'^https?://purl\.org/NET/mediatypes/text/x-rst$'
    RUBY = r'^https?://purl\.org/NET/mediatypes/text/x-ruby$'
    SBGN = r'^https?://identifiers\.org/combine\.specifications/sbgn($|\.)'
    SBML = r'^https?://identifiers\.org/combine\.specifications/sbml($|\.)'
    SBOL = r'^https?://identifiers\.org/combine\.specifications/sbol($|\.)'
    SBOL_VISUAL = r'^https?://identifiers\.org/combine\.specifications/sbol-visual($|\.)'
    Scilab = r'^https?://purl\.org/NET/mediatypes/application/x-scilab$'
    SED_ML = r'^https?://identifiers\.org/combine\.specifications/sed\-?ml($|\.)'
    SHOCKWAVE_FLASH = r'^https?://purl\.org/NET/mediatypes/(application/x-shockwave-flash|application/vnd\.adobe\.flash-movie)$'
    SimBiology_Project = r'^https?://purl\.org/NET/mediatypes/application/x-sbproj$'
    SLI = r'^https?://purl\.org/NET/mediatypes/text/x-sli$'
    Smoldyn = r'^https?://purl\.org/NET/mediatypes/text/smoldyn\+plain$'
    SO = r'^https?://purl\.org/NET/mediatypes/application/x-sharedlib$'
    SQL = r'^https?://purl\.org/NET/mediatypes/application/sql$'
    SVG = r'^https?://purl\.org/NET/mediatypes/image/svg\+xml$'
    SVGZ = r'^https?://purl\.org/NET/mediatypes/image/svg\+xml-compressed$'
    TEXT = r'^https?://purl\.org/NET/mediatypes/text/plain$'
    TIFF = r'^https?://purl\.org/NET/mediatypes/image/tiff$'
    TSV = r'^https?://purl\.org/NET/mediatypes/text/tab-separated-values$'
    Vega = r'^https?://purl\.org/NET/mediatypes/application/vnd\.vega\.v5\+json$'
    Vega_Lite = r'^https?://purl\.org/NET/mediatypes/application/vnd\.vegalite\.v3\+json$'
    VCML = r'^https?://purl\.org/NET/mediatypes/application/vcml\+xml$'
    WEBP = r'^https?://purl\.org/NET/mediatypes/image/webp$'
    XLS = r'^https?://purl\.org/NET/mediatypes/application/vnd\.ms-excel$'
    XLSX = r'^https?://purl\.org/NET/mediatypes/application/vnd\.openxmlformats-officedocument\.spreadsheetml\.sheet$'
    XML = r'^https?://purl\.org/NET/mediatypes/application/xml$'
    XPP = r'^https?://purl\.org/NET/mediatypes/text/x-(ode|xpp)$'
    XPP_AUTO = r'^https?://purl\.org/NET/mediatypes/text/x-(ode|xpp)-auto$'
    XPP_SET = r'^https?://purl\.org/NET/mediatypes/text/x-(ode|xpp)-set$'
    XSL = r'^https?://purl\.org/NET/mediatypes/(application/xslfo\+xml|text/xsl)$'
    XUL = r'^https?://purl\.org/NET/mediatypes/text/xul$'
    XYZ = r'^https?://purl\.org/NET/mediatypes/chemical/x-xyz$'
    YAML = r'^https?://purl\.org/NET/mediatypes/application/x-yaml$'
    ZGINML = r'^https?://purl\.org/NET/mediatypes/application/zginml\+zip$'
    ZIP = r'^https?://purl\.org/NET/mediatypes/application/zip$'
    OTHER = r'^https?://purl\.org/NET/mediatypes/application/octet-stream$'


class CombineArchiveWriter(object):
    """ Writer for COMBINE/OMEX archives

    Attributes:
        errors (nested :obj:`list` of :obj:`str`): errors
        warnings (nested :obj:`list` of :obj:`str`): warnings
    """

    def __init__(self):
        self.errors = []
        self.warnings = []

    def run(self, archive, in_dir, out_file):
        """ Write an archive to a file

        Args:
            archive (:obj:`CombineArchive`): description of archive
            in_dir (:obj:`str`): directory which contains the files in the archive
            out_file (:obj:`str`): path to save archive

        Raises:
            :obj:`AssertionError`: if files could not be added to the archive or the archive could not be
                saved
        """
        self.errors = []
        self.warnings = []

        # instantiate archive
        archive_comb = libcombine.CombineArchive()

        # add files to archive
        for i_content, content in enumerate(archive.contents):
            if not archive_comb.addFile(
                os.path.join(in_dir, content.location),
                content.location,
                content.format if content.format else '',
                content.master
            ):
                content_id = '`' + content.location + '`' if content.location else str(i_content + 1)
                msg = 'Content element {} could not be added to the archive.'.format(content_id)
                self.errors.append([msg])
                raise Exception(msg)

        # save archive to a file
        if not archive_comb.writeToFile(out_file):
            msg = 'Archive could not be saved.'
            self.errors.append([msg])
            raise Exception(msg)

        errors, warnings = get_combine_errors_warnings(archive_comb.getManifest())
        self.errors.extend(errors)
        self.warnings.extend(warnings)

        if self.warnings:
            warn('COMBINE/OMEX archive has warnings.\n  ' + flatten_nested_list_of_strings(self.warnings).replace('\n', '\n  '),
                 BioSimulatorsWarning)
        if self.errors:
            raise ValueError('COMBINE/OMEX archive is invalid.\n  ' + flatten_nested_list_of_strings(self.errors).replace('\n', '\n  '))

    def write_manifest(self, contents, filename):
        """ Write an OMEX manifest file

        Args:
            contents (:obj:`list` of :obj:`CombineArchiveContent`): contents of a COMBINE/OMEX archive
            filename (:obj:`str`): path to OMEX manifest file
        """
        manifest = libcombine.CaOmexManifest()
        for content in contents:
            content_comb = manifest.createContent()

            if content.location is not None:
                content_comb.setLocation(content.location)

            if content.format is not None:
                content_comb.setFormat(content.format)

            if content.master is not None:
                content_comb.setMaster(content.master)

        errors, warnings = get_combine_errors_warnings(manifest)
        if warnings:
            msg = 'COMBINE/OMEX archive has warnings.\n  ' + flatten_nested_list_of_strings(warnings).replace('\n', '\n  ')
            warn(msg, BioSimulatorsWarning)
        if errors:
            msg = 'COMBINE/OMEX archive is invalid.\n  ' + flatten_nested_list_of_strings(errors).replace('\n', '\n  ')
            raise ValueError(msg)

        libcombine.writeOMEXToFile(manifest, filename)


class CombineArchiveReader(object):
    """ Reader for COMBINE/OMEX archives

    Attributes:
        errors (nested :obj:`list` of :obj:`str`): errors
        warnings (nested :obj:`list` of :obj:`str`): warnings
    """

    NONE_DATETIME = '2000-01-01T00:00:00Z'

    def __init__(self):
        self.errors = []
        self.warnings = []

    def run(self, in_file: str, out_dir: str, include_omex_metadata_files: bool = True, config: Config = None) -> CombineArchive:
        """ Read an archive from a file

        Args:
            in_file (:obj:`str`): path to archive
            out_dir (:obj:`str`): directory where the contents of the archive should be unpacked
            include_omex_metadata_files (:obj:`bool`, optional): whether to include the OMEX metadata
                file as part of the contents of the archive
            config (:obj:`Config`, optional): configuration

        Returns:
            :obj:`CombineArchive`: description of archive

        Raises:
            :obj:`ValueError`: archive is invalid
        """
        if config is None:
            config = get_config()

        self.errors = []
        self.warnings = []

        if not os.path.isfile(in_file):
            msg = "`{}` is not a file.".format(in_file)
            self.errors.append([msg])
            raise ValueError(msg)

        archive_comb = libcombine.CombineArchive()
        archive_initialized = archive_comb.initializeFromArchive(in_file)
        if archive_initialized:
            errors, warnings = get_combine_errors_warnings(archive_comb.getManifest())
            if config.VALIDATE_OMEX_MANIFESTS:
                self.errors.extend(errors)
                self.warnings.extend(warnings)

        if not archive_initialized or errors:
            if not config.VALIDATE_OMEX_MANIFESTS:
                try:
                    archive = CombineArchiveZipReader().run(in_file, out_dir)
                    msg = '`{}` is a plain zip archive, not a COMBINE/OMEX archive.'.format(in_file)
                    self.warnings.append([msg])
                    warn(msg, BioSimulatorsWarning)
                    return archive
                except ValueError:
                    msg = "`{}` is not a valid COMBINE/OMEX archive.".format(in_file)
                    self.errors.append([msg])
                    raise ValueError(msg)
            elif not self.errors:
                msg = "`{}` is not a valid COMBINE/OMEX archive.".format(in_file)
                self.errors.append([msg])
                raise ValueError(msg)

        # instantiate archive
        archive = CombineArchive()

        # read files
        for location in archive_comb.getAllLocations():
            location = location.c_str()
            file_comb = archive_comb.getEntryByLocation(location)

            if file_comb.isSetFormat():
                format = file_comb.getFormat()
            else:
                format = None

            content = CombineArchiveContent(
                location=location,
                format=format,
                master=file_comb.isSetMaster() and file_comb.getMaster(),
            )
            archive.contents.append(content)

        # extract files

        with Zip(in_file, 'r') as zip_archive:
            zip_archive.extractall(path=out_dir)

#        archive_comb.extractTo(out_dir) # libcombine incorrectly extracts files as directories.

        # read metadata files skipped by libCOMBINE
        content_locations = set(os.path.relpath(content.location, '.') for content in archive.contents)
        manifest_contents = self.read_manifest(os.path.join(out_dir, 'manifest.xml'), in_file, config=config)

        if include_omex_metadata_files:
            for manifest_content in manifest_contents:
                if (
                    manifest_content.format
                    and re.match(CombineArchiveContentFormatPattern.OMEX_METADATA.value, manifest_content.format)
                    and os.path.relpath(manifest_content.location, '.') not in content_locations
                ):
                    archive.contents.append(manifest_content)

        if config.VALIDATE_OMEX_MANIFESTS:
            manifest_includes_archive = False
            for manifest_content in manifest_contents:
                if os.path.relpath(manifest_content.location, '.') == '.':
                    if manifest_content.format:
                        if re.match(CombineArchiveContentFormatPattern.OMEX, manifest_content.format):
                            manifest_includes_archive = True
                        else:
                            msg = 'The format of the archive must be `{}`, not `{}`.'.format(
                                CombineArchiveContentFormat.OMEX, manifest_content.format)
                            self.errors.append([msg])

            if not manifest_includes_archive:
                msg = (
                    'The manifest does not include its parent COMBINE/OMEX archive. '
                    'Manifests should include their parent COMBINE/OMEX archives.'
                )
                self.warnings.append([msg])

        # raise warnings and errors
        if self.warnings:
            warn('COMBINE/OMEX archive has warnings.\n  ' + flatten_nested_list_of_strings(self.warnings).replace('\n', '\n  '),
                 BioSimulatorsWarning)
        if self.errors:
            raise ValueError('`{}` is not a valid COMBINE/OMEX archive.\n  {}'.format(
                in_file, flatten_nested_list_of_strings(self.errors).replace('\n', '\n  ')))

        # return information about archive
        return archive

    def read_manifest(self, filename, archive_filename=None, config=None):
        """ Read the contents of an OMEX manifest file

        Args:
            filename (:obj:`str`): path to OMEX manifest file
            archive_filename (:obj:`str`, option): path to COMBINE archive
            config (:obj:`Config`, optional): configuration

        Returns:
            :obj:`list` of :obj:`CombineArchiveContent`: contents of the OMEX manifest file
        """
        if config is None:
            config = get_config()

        manifest_comb = libcombine.readOMEXFromFile(filename)
        if not isinstance(manifest_comb, libcombine.CaOmexManifest):
            if config.VALIDATE_OMEX_MANIFESTS or archive_filename is None:
                self.errors(['`{}` could not be read as an OMEX manifest file.'].format(filename))
                return []
            else:
                try:
                    contents = CombineArchiveZipReader().run(archive_filename).contents
                    contents.append(CombineArchiveContent(location='.', format=CombineArchiveContentFormat.ZIP))
                    return contents
                except ValueError:
                    msg = "`{}` is not a valid zip file.".format(archive_filename)
                    self.errors.append([msg])
                    return []

        errors, warnings = get_combine_errors_warnings(manifest_comb)
        if config.VALIDATE_OMEX_MANIFESTS or archive_filename is None:
            self.errors.extend(errors)
            self.warnings.extend(warnings)
            if errors:
                return []
        else:
            if errors:
                try:
                    contents = CombineArchiveZipReader().run(archive_filename).contents
                    contents.append(CombineArchiveContent(location='.', format=CombineArchiveContentFormat.ZIP))
                    return contents
                except ValueError:
                    msg = "`{}` is not a valid zip file.".format(archive_filename)
                    self.errors.append([msg])
                    return []

        contents = []
        for content_comb in manifest_comb.getListOfContents():
            content = CombineArchiveContent()

            if content_comb.isSetLocation():
                content.location = content_comb.getLocation()

            if content_comb.isSetFormat():
                content.format = content_comb.getFormat()

            if content_comb.isSetMaster():
                content.master = content_comb.getMaster()

            contents.append(content)

        return contents


class CombineArchiveZipReader(object):
    """ Create a COMBINE/OMEX archive object from a plain zip archive. Set the format of files with
    the extension ``.sedml`` to :obj:`CombineArchiveContentFormat.SED_ML.value`.
    """
    @classmethod
    def run(cls, in_file, out_dir=None):
        """ Read an archive from a zip file

        Args:
            in_file (:obj:`str`): path to archive
            out_dir (:obj:`str`, optional): directory where the contents of the archive should be unpacked

        Returns:
            :obj:`CombineArchive`: description of the archive

        Raises:
            :obj:`ValueError`: archive is invalid
        """
        try:
            zip_archive = ArchiveReader().run(in_file, out_dir)
        except (FileNotFoundError, zipfile.BadZipFile):
            msg = '`{}` is not a valid zip archive.'.format(in_file)
            raise ValueError(msg)

        combine_archive = CombineArchive()
        for file in zip_archive.files:
            combine_archive.contents.append(
                CombineArchiveContent(
                    location=file.archive_path,
                    format=(CombineArchiveContentFormat.SED_ML.value
                            if os.path.splitext(file.archive_path)[1] == '.sedml' else None),
                ),
            )

        return combine_archive


def get_combine_errors_warnings(manifest):
    """ Get the errors and warnings of an OMEX manifest

    Args:
        manifest (:obj:`libcombine.CaOmexManifest`): manifest

    Returns:
        :obj:`tuple`:

            * nested :obj:`list` of :obj:`str`: errors
            * nested :obj:`list` of :obj:`str`: warnings
    """
    errors = []
    warnings = []

    log = manifest.getErrorLog()
    for i_error in range(log.getNumErrors()):
        error = log.getError(i_error)
        if error.isError() or error.isFatal():
            errors.append([error.getMessage()])
        else:
            warnings.append([error.getMessage()])

    return (errors, warnings)


class SpatialCombineArchive(ABC):
    # TODO: Add more robust rezipping
    paths: Dict[str, str]

    def __init__(self,
                 rootpath: str,
                 simularium_filename: Optional[str] = None):
        """ABC Object for storing and setting/getting files pertaining to simularium file conversion.

            Args:
                rootpath: root of the unzipped archive. Consider this your working dirpath.
                simularium_filename:`Optional`: full path which to assign to the newly generated simularium file.
                If using this value, it EXPECTS a full path. Defaults to `{name}_output_for_simularium`.
                name: Commonplace name for the archive to be used if no `simularium_filename` is passed. Defaults to
                    `new_spatial_archive`.
        """
        super().__init__()
        self.rootpath = rootpath
        self.__parse_rootpath()
        if simularium_filename is None:
            simularium_filename = 'spatial_combine_archive'
        self.simularium_filename = os.path.join(self.rootpath, simularium_filename)
        self.paths = self.get_all_archive_filepaths()

    def __parse_rootpath(self):
        """Private method for parsing whether `self.rootpath` is the path to a directory or single OMEX/COMBINE
            zipped file. If .omex, then decompress the input path into an unzipped directory for working.
        """
        if self.rootpath.endswith('.omex'):
            self.unzip()

    def unzip(self, unzipped_output_location: str = None):
        reader = ArchiveReader()
        try:
            if not unzipped_output_location:
                unzipped_output_location = self.rootpath.replace(
                    '.omex',
                    '_UNZIPPED'
                )  # TODO: make tempdir here instead
            reader.run(self.rootpath, unzipped_output_location)
            print('Omex successfully unzipped!...')
            self.rootpath = unzipped_output_location
        except Exception as e:
            warn(f'Omex could not be unzipped because: {e}')

    def rezip(self, paths_to_write: Optional[List[str]] = None, destination: Optional[str] = None):
        if '.omex' in self.rootpath:
            writer = ArchiveWriter()
            if not paths_to_write:
                paths_to_write = list(self.get_all_archive_filepaths().values())
                print(f'HERE THEY ARE: {paths_to_write}')
            if not destination:
                destination = self.rootpath
            writer.run(archive=paths_to_write, archive_filename=destination)
            print(f'Omex successfully bundled with the following paths: {paths_to_write}!')

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
        return reader.read_manifest(filename=manifest_fp, archive_filename=self.rootpath)

    @staticmethod
    def generate_new_archive_content(fp: str) -> CombineArchiveContent:
        """Factory for generating a new instance of `CombineArchiveContent` using just fp.

            Args:
                fp: filepath of the content you wish to add to the combine archive.

            Returns:
                `CombineArchiveContent` based on the passed `fp`.
        """
        return CombineArchiveContent(fp)

    def add_file_to_manifest(self, contents_fp: str) -> None:
        contents = self.read_manifest_contents()
        new_content = self.generate_new_archive_content(contents_fp)
        contents.append(new_content)
        writer = CombineArchiveWriter()
        try:
            manifest_fp = self.get_manifest_filepath()
            writer.write_manifest(contents=contents, filename=manifest_fp)
            print('File added to archive manifest contents!')
        except Exception as e:
            print(e)
            warn(f'The simularium file found at {contents_fp} could not be added to manifest.')
            return

    def add_modelout_file_to_manifest(self, model_fp) -> None:
        return self.add_file_to_manifest(model_fp)

    def add_simularium_file_to_manifest(self, simularium_fp: Optional[str] = None) -> None:
        """Read the contents of the manifest file found at `self.rootpath`, create a new instance of
            `CombineArchiveContent` using a set simularium_fp, append the new content to the original,
            and re-write the archive to reflect the newly added content.

            Args:
                  simularium_fp:`Optional`: path to the newly generated simularium file. Defaults
                    to `self.simularium_filename`.
        """
        try:
            if not simularium_fp:
                simularium_fp = self.simularium_filename
            self.add_file_to_manifest(simularium_fp)
            print('Simularium File added to archive manifest contents!')
        except Exception:
            raise IOError(f'The simularium file found at {simularium_fp} could not be added to manifest.')

    def verify_spatial_simulator_in_manifest(self, sim='smoldyn') -> bool:
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
                 model_output_filename='modelout.txt',
                 simularium_filename: Optional[str] = None):
        """Object for handling the output of Smoldyn simulation data. Implementation child of `SpatialCombineArchive`.

            Args:
                rootpath: fp to the root of the archive 'working dir'.
                model_output_filename: filename ONLY not filepath of the model file you are working with. Defaults to
                    `modelout.txt`.
                simularium_filename:
        """
        super().__init__(rootpath, simularium_filename)
        self.set_model_filepath()
        self.model_output_filename = os.path.join(self.rootpath, model_output_filename)
        self.paths['model_output_file'] = self.model_output_filename

    def set_model_filepath(self, model_filename: Optional[str] = None, model_default='model.txt'):
        """Recursively read the full paths of all files in `self.paths` and return the full path of the file
            containing the term 'model.txt', which is the naming convention.
            Implementation of ancestral abstract method.

            Args:
                model_filename: `Optional[str]`: index by which to label a file in directory as the model file.
                    Defaults to `model_default`.
                model_default: `str`: default model filename naming convention. Defaults to `'model.txt'`
        """
        if not model_filename:
            model_filename = os.path.join(self.rootpath, model_default)  # default Smoldyn model name
        for k in self.paths.keys():
            full_path = self.paths[k]
            if model_filename in full_path:
                self.model_path = model_filename

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

