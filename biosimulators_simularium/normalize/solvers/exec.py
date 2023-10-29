from typing import *
from biosimulators_simularium.normalize.parameters.data_model import BoltzmannConstant, DiffusionCoefficient


class DiffusionCoefficientSolver(ABC):
    def __init__(self, medium: str):
        """Abstract base class for solving diffusion coefficients based on the given medium ('gas', 'liquid')

            Args:
                medium:`str`: medium for which a given particle's diffusion coefficient is being calculated.
        """
        self.medium = medium

    @abstractmethod
    def _solver(self) -> function:
        """Abstract private method for generating the diffusion coefficient equation given the medium you are passing in
            the child instance of this class. Here you must define the function itself and return the value. This
            should probably be simply a wrapper which returns an inner function from here.

            Returns:
                `function`: the function for the diffusion relative to the given implementation of solving for the
                    diffusion coefficient based on the medium.
        """
        pass

    def solve(self, **diffusion_parameters):
        """Public method used as the primary form of execution for the given medium's
            diffusion coefficient solver.
        """
        solver = self._solver()
        return solver(**diffusion_parameters)


class LiquidDiffusionCoefficient(DiffusionCoefficientSolver):
    def __init__(self):
        super().__init__('liquid')

    @staticmethod
    def _solver(**parameters) -> function:
        def solver(k, T, eta, r):
            return (k * T) / (6 * np.pi * eta * r)

        return solver(**parameters)

    def solve(self, **diffusion_parameters) -> float:
        diffusion_coeff = self._solver(**diffusion_parameters)
        return DiffusionCoefficient(diffusion_coeff)



