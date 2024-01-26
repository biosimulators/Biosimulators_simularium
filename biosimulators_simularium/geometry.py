import os
from abc import abstractmethod, ABC
from typing import *
from vtk import (
    vtkCylinder,
    vtkSphere,
    vtkImplicitBoolean,
    vtkSampleFunction,
    vtkContourFilter,
    vtkPoints,
    vtkCellArray,
    vtkAppendPolyData,
    vtkPolyDataReader,
    vtkPolyDataWriter,
    vtkPolyData
)
from biosimulators_simularium.io import read_smoldyn_simulation_configuration
from biosimulators_simularium.simulation_data import get_simulation_boundaries


class Geometry(ABC):
    def __init__(self):
        super().__init__()

    @staticmethod
    def extract_surface(value, boundaries: List[float]):
        # Combine the shapes using vtkImplicitBoolean
        ib = vtkImplicitBoolean()
        ib.SetOperationTypeToUnion()
        ib.AddFunction(value)

        # Sample the sphere shape
        sample = vtkSampleFunction()
        sample.SetImplicitFunction(ib)
        sample.SetModelBounds(*boundaries)  # Bounds should encompass the sphere
        sample.SetSampleDimensions(40, 40, 40)

        # Extract the surface
        surface = vtkContourFilter()
        surface.SetInputConnection(sample.GetOutputPort())
        # surface.SetValue(0, 0.0)
        return surface


class Sphere(Geometry):
    def __init__(self, boundaries: List[float], x=None, y=None, z=None, radius=None):
        super().__init__()
        self.x = x or -1
        self.y = y or 0
        self.z = z or 0
        self.radius = radius or 0.5
        value = vtkSphere()
        value.SetCenter(self.x, self.y, self.z)
        value.SetRadius(self.radius)
        # self.value = self.extract_surface(value, boundaries)
        self.value = value



class CapsuleSurface:
    def __init__(self, boundaries: List[float], radius=None):
        """Create the geometry primitives and extract the surface."""
        # Create the geometry of the surface
        cyl = vtkCylinder()
        hemi1 = Sphere(-1, 0, 0, radius).value
        hemi2 = Sphere(1, 0, 0, radius).value
        # hemi1 = vtkSphere()
        # hemi2 = vtkSphere()
        # hemi1.SetCenter(-1, 0, 0)
        # hemi2.SetCenter(1, 0, 0)

        # Combine the shapes using vtkImplicitBoolean
        ib = vtkImplicitBoolean()
        ib.SetOperationTypeToUnion()
        ib.AddFunction(hemi1)
        ib.AddFunction(hemi2)
        ib.AddFunction(cyl)

        # Sample the combined shape
        sample = vtkSampleFunction()
        sample.SetImplicitFunction(ib)
        # sample.SetModelBounds(-2, 2, -0.5, 0.5, -0.5, 0.5)  # TODO: make this dynamically read-in.
        sample.SetModelBounds(*boundaries)
        sample.SetSampleDimensions(40, 40, 40)
        # sample.ComputeNormalsOff()

        # Extract the surface
        surface = vtkContourFilter()
        surface.SetInputData(sample.GetOutput())
        # surface.SetValue(0, 0.0)
        self.value = surface


class CapsulePoints:
    def __init__(self, coordinates):
        """Create polydata object from molecule coordinates via points and relative vertices."""
        # Create points and vertices for the molecule data
        points = vtkPoints()
        vertices = vtkCellArray()
        for coord in coordinates:
            point_id = points.InsertNextPoint(coord)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(point_id)

        # Create a polydata object and set the points and vertices
        polydata = vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetVerts(vertices)
        self.value = polydata


class Capsule:
    def __init__(self, surface: CapsuleSurface, points: CapsulePoints):
        """Interpolate points and surface of the primitives of a capsule."""
        # Combine surface and molecule data
        appendFilter = vtkAppendPolyData()
        appendFilter.AddInputData(surface.value.GetOutput())
        appendFilter.AddInputData(points.value)
        appendFilter.Update()
        self.value = appendFilter.GetOutput()


def read_geometry(fp: str, sim, coords):
    """Read a smoldyn configuration and return a vtk representation of the data therein."""
    geometry = get_config_geometry(fp)
    boundaries = get_simulation_boundaries(sim)
    print(geometry)
    if 'cylinder' and 'hemi' in geometry:
        cap_surface = CapsuleSurface(boundaries)
        cap_points = CapsulePoints(coords)
        print('generated capsule.')
        return Capsule(cap_surface, cap_points).value
    elif 'sphere' in geometry:
        print('generated sphere')
        sphere = Sphere(boundaries)
        return sphere.extract_surface(sphere.value, boundaries).GetOutput()
    else:
        points = vtkPoints()
        vertices = vtkCellArray()
        for coord in coords:
            point_id = points.InsertNextPoint(coord)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(point_id)

        # Create a polydata object and set the points and vertices
        polydata = vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetVerts(vertices)
        print('generated polydata')
        return polydata



def get_config_panels(fp: str):
    panels = []
    config = read_smoldyn_simulation_configuration(fp)
    for line in config:
        if line.startswith('panel'):
            panels.append(line)
    return panels


def get_panel_geometry(panels: List[str]):
    geometries = []
    for p in panels:
        panel = p.split()
        geometries.append(panel[1])
    return geometries


def get_config_geometry(fp: str) -> List[str]:
    """Return a list of primitive geometry types for all panels in a given smoldyn configuration file."""
    panels = get_config_panels(fp)
    return get_panel_geometry(panels)


def write_capsule_vtk_file(fp: str, data: Union[Capsule, vtkAppendPolyData]) -> int:
    """Write the append filter output to file.

        Returns:
            `int`: the resulting stdout code of this operation.
    """
    if isinstance(data, Capsule):
        data = data.value
    writer = vtkPolyDataWriter()
    writer.SetFileName(fp)
    writer.SetInputData(data.value.GetOutput())
    return writer.Write()


def read_vtk_file(fp: str) -> vtkPolyData:
    """Read vtk and return read-in polydata object"""
    reader = vtkPolyDataReader()
    reader.SetFileName(fp)
    reader.Update()
    return reader.GetOutput()


def generate_config_surface(fp: str):
    geos = get_config_geometry(fp)


def write_minE_capsule(coords, vtk_fp: str):
    """Create the geometry primitives and extract the surface."""
    # Create the geometry of the surface
    cyl = vtkCylinder()
    hemi1 = vtkSphere()
    hemi2 = vtkSphere()
    hemi1.SetCenter(-1, 0, 0)
    hemi2.SetCenter(1, 0, 0)

    # Combine the shapes using vtkImplicitBoolean
    ib = vtkImplicitBoolean()
    ib.SetOperationTypeToUnion()
    ib.AddFunction(hemi1)
    ib.AddFunction(hemi2)
    ib.AddFunction(cyl)

    # Sample the combined shape
    sample = vtkSampleFunction()
    sample.SetImplicitFunction(ib)
    sample.SetModelBounds(-2, 2, -0.5, 0.5, -0.5, 0.5)  # TODO: make this dynamically read-in.
    sample.SetSampleDimensions(40, 40, 40)
    # sample.ComputeNormalsOff()

    # Extract the surface
    surface = vtkContourFilter()
    surface.SetInputData(sample.GetOutput())
    # surface.SetValue(0, 0.0)

    """Create polydata object from molecule coordinates via points and relative vertices."""
    # Create points and vertices for the molecule data
    points = vtkPoints()
    vertices = vtkCellArray()

    for coord in coords:
        point_id = points.InsertNextPoint(coord)
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(point_id)

    # Create a polydata object and set the points and vertices
    polydata = vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetVerts(vertices)

    """Interpolate points and surface"""
    # Combine surface and molecule data
    appendFilter = vtkAppendPolyData()
    appendFilter.AddInputData(surface.GetOutput())
    appendFilter.AddInputData(polydata)
    appendFilter.Update()


    """Write the append filter output to file"""
    # Write the combined data to a file
    writer = vtkPolyDataWriter()
    writer.SetFileName(vtk_fp)
    writer.SetInputData(appendFilter.GetOutput())
    return writer.Write()
