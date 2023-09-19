"""This file contains methods for getting file directory information, parsing platform, and coordinate interleaving.
"""


import os
from typing import Dict, List
from biosimulators_simularium.utils.coordinate_interleaver import CoordinateDeinterleaver, CoordinateInterleaver
from biosimulators_simularium.utils.platform_parser import SmoldynPlatformParser


__all__ = [
    'make_files_dict',
    'remove_output_files',
    'remove_file',
    'coordinates_to_id',
    'id_to_coordinates',
]


def make_files_dict(fp) -> Dict[str, str]:
    d = {}
    if os.path.exists(fp):
        for root, _, files in os.walk(fp):
            for i, f in enumerate(files):
                fp = os.path.join(root, f)
                d[fp + str(i)] = fp
    return d


def remove_output_files(fp='biosimulators_simularium/test_files/archives/Andrews_ecoli_0523') -> None:
    if os.path.exists(fp):
        for root, _, files in os.walk(fp):
            for f in files:
                fp = os.path.join(root, f)
                if fp.endswith('.txt') and 'model' not in fp:
                    os.remove(fp)


def remove_file(fp) -> None:
    return os.remove(fp) if os.path.exists(fp) else None


def coordinates_to_id(x, y, z) -> int:
    interleaver = CoordinateInterleaver(x, y, z)
    return interleaver.coordinates_to_id()


def id_to_coordinates(id_value: int):
    deinterleaver = CoordinateDeinterleaver(id_value)
    return deinterleaver.id_to_coordinates()


def test_interleaver():
    x, y, z = 1200, 3400, 5600
    interleaver = CoordinateInterleaver(x, y, z)
    id_value = interleaver.coordinates_to_id()
    print(id_value)
    print(interleaver.id_to_coordinates(id_value))  # Expected (12, 34, 56)


def parse_platform():
    return SmoldynPlatformParser()


def extract_path_sections(fp: str) -> List[str]:
    parts = []
    while fp:
        path, tail = os.path.split(fp)
        if tail:
            parts.insert(0, tail)
        else:
            if path:
                parts.insert(0, path)
            break
    return parts
