import os
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


class CapsuleSurface:
    def __init__(self):
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
        self.value = appendFilter


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
