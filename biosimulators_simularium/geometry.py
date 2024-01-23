import os
from dataclasses import dataclass
import pyvista as pv
from typing import *


@dataclass
class Capsule:
    cyl: pv.Cylinder
    spheres: List[pv.Sphere]


def construct_capsule(R: float = 0.5, L_PARAM: int = 2) -> pv.PolyData:
    """Construct a capsule shape out of a cylinder and two spheres.

    TODO: Encode json and derive the parameters automatically from the simulation instance.
    """
    # Create cylinder
    cylinder = pv.Cylinder(center=(0, 0, 0), radius=R, height=L_PARAM * 2)
    # Create hemispheres
    hemisphere1 = pv.Sphere(radius=R, center=(L_PARAM, 0, 0))
    hemisphere2 = pv.Sphere(radius=R, center=(-L_PARAM, 0, 0))
    return cylinder.merge(hemisphere1).merge(hemisphere2)

