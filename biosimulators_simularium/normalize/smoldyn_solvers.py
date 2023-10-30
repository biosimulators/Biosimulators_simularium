"""Objects and methods for calculating and solving for various particle values required for the `simulariumio` interface
    that are not explicitly exposed by Smoldyn. For example, particle radius will not be directly derived from a
    Smoldyn model file, but implicitly through the user-defined diffusion coefficient. The nomenclature used for objects
    will be relative the to universe according to Smoldyn. For clarity, the terms "molecule" and "agent" will
    be used interchangeably. Agent is because we have this term used in both smoldyn and simularium.

author: Alex Patrie <apatrie@uchc.edu>
date: 10/30/2023
license: MIT
"""


import numpy as np


class ParticleDiffusionCoefficient:
    """Object which calculates a molecule's diffusion coefficient given the required parameters of the
        Stokes-Einstein equation.
    """
    pass


class ParticleRadius:
    """Object which calculates a molecule's radius to serve as input for `simulariumio.DisplayData` relative to
        a given smoldyn simulation agent. The calculation for this value is based on the parameters which represent the
        molecular mass and density of the given agent. Can be used as an input parameter of the Stokes-Einstein
        equation.

        Methods:
            `radius_from_composition`: calculates the radius of the particle based on mol.mass and density.
            `radius_from_D`: calculates the radius of the particle by reverse-engineering the provided diffusion
                coefficient. Here, `T` is the absolute temp of the liquid during the simulation. Here, it is assumed that
                the radius was originally derived via the `radius_from_composition` by the Smoldyn modeler when
                creating the model itself.
    """
    pass


