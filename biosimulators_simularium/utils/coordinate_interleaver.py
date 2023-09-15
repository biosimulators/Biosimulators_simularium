"""An object for interpreting a tuple of (x, y, z) coordinates into an integer and back.
"""

from typing import Tuple
import numpy as np


class CoordinateInterleaver:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.coordinates = (self.x, self.y, self.z)

    @staticmethod
    def interleave_bits(*args):
        """Interleave bits of multiple integer arguments."""
        result = 0
        num_values = len(args)
        for i in np.arange(0, 32, 1):  # Using 32 bits for each coordinate (this is adjustable)
            for j, arg in enumerate(args):
                result |= ((arg >> i) & 1) << (i * num_values + j)
        return result

    @staticmethod
    def deinterleave_bits(value, num_values):
        """Deinterleave bits into multiple integer values."""
        results = [0] * num_values
        for i in np.arange(0, 32, 1):
            for j in range(num_values):
                results[j] |= ((value >> (i * num_values + j)) & 1) << i
        return results

    def coordinates_to_id(self, coordinates: Tuple = None):
        coor = coordinates or self.coordinates
        return self.interleave_bits(*coor)

    def id_to_coordinates(self, value):
        return self.deinterleave_bits(value, 3)


def test_interleaver():
    x, y, z = 1200, 3400, 5600
    interleaver = CoordinateInterleaver(x, y, z)
    id_value = interleaver.coordinates_to_id()
    print(id_value)
    print(interleaver.id_to_coordinates(id_value))  # Expected (12, 34, 56)


test_interleaver()