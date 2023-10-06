"""This file contains methods for getting file directory information, parsing platform, and coordinate interleaving.
"""


import os
from typing import Dict, List
from biosimulators_simularium.utils.coordinate_interleaver import CoordinateDeinterleaver, CoordinateInterleaver
from biosimulators_simularium.utils.platform_parser import SmoldynPlatformParser


__all__ = [
    'flatten_nested_list_of_strings',
    'are_lists_equal',
    'none_comparator',
    'none_sorted',
    'none_sort_key_gen',
    'get_filepaths',
    'make_files_dict',
    'remove_output_files',
    'remove_file',
    'coordinates_to_id',
    'id_to_coordinates',
    'parse_platform',
]


def flatten_nested_list_of_strings(nested_list, prefix='- ', indent=' ' * 2):
    """ Flatten a nested list of strings

    Args:
        nested_list (nested :obj:`list` of :obj:`str`): nested list of string
        prefix (:obj:`str`, optional): prefix
        indentation (:obj:`str`, optional): indentation

    Returns:
        :obj:`str`: flattened string
    """
    flattened = []
    for item in nested_list:
        flattened.append(prefix + item[0].replace('\n', '\n' + ' ' * len(prefix)))
        if len(item) > 1:
            flattened.append(
                indent
                + flatten_nested_list_of_strings(item[1], prefix=prefix, indent=indent).replace('\n', '\n' + indent)
            )

    return '\n'.join(flattened)


def none_comparator(x, y):
    if x == y:
        return 0

    if isinstance(x, tuple) and not isinstance(y, tuple):
        return 1
    if not isinstance(x, tuple) and isinstance(y, tuple):
        return -1
    if isinstance(x, tuple) and isinstance(y, tuple):
        if len(x) < len(y):
            return -1
        if len(x) > len(y):
            return 1

        for x1, y1 in zip(x, y):
            cmp = none_comparator(x1, y1)
            if cmp != 0:
                return cmp

        return 0  # pragma: no cover

    if x is None:
        return -1
    if y is None:
        return 1

    if x < y:
        return -1
    if x > y:
        return 1


def none_sort_key_gen(key=None):
    class NoneComparator(object):
        def __init__(self, obj):
            if key:
                self.obj = key(obj)
            else:
                self.obj = obj

        def __lt__(self, other):
            return none_comparator(self.obj, other.obj) < 0

        def __gt__(self, other):
            return none_comparator(self.obj, other.obj) > 0

        def __eq__(self, other):
            return none_comparator(self.obj, other.obj) == 0

        def __le__(self, other):
            return none_comparator(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return none_comparator(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return none_comparator(self.obj, other.obj) != 0
    return NoneComparator


def none_sorted(arr, key=None):
    """ Sort an error that contains :obj:`None`

    Args:
        arr (:obj:`list`): array

    Returns:
        :obj:`list`: sorted array
    """
    return sorted(arr, key=none_sort_key_gen(key))


def are_lists_equal(a, b):
    """ Determine if two lists are equal, optionally up to the order of the elements

    Args:
        a (:obj:`list`): first list
        b (:obj:`list`): second list

    Returns:
        :obj:`bool`: :obj:`True`, if lists are equal
    """
    if len(a) != len(b):
        return False

    a = none_sorted(a, key=lambda x: x.to_tuple())
    b = none_sorted(b, key=lambda x: x.to_tuple())

    for a_el, b_el in zip(a, b):
        if not a_el.is_equal(b_el):
            return False

    return True


def get_filepaths(dirpath: str) -> List[str]:
    paths = []
    for root, _, files in os.walk(dirpath):
        for f in files:
            fp = os.path.join(root, f)
            paths.append(fp)
    return paths


def make_files_dict(dirpath: str) -> Dict[str, str]:
    d = {}
    for c in os.path.split(dirpath):
        d[c[0]] = os.path.join(c[0], c[1])
    return d


def remove_output_files(fp='biosimulators_simularium/fixtures/archives/Andrews_ecoli_0523') -> None:
    files = get_filepaths(fp)
    for f in files:
        if f.endswith('.txt') and 'model' not in f:
            os.remove(f)


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
    deinterleaver = CoordinateDeinterleaver(id_value)
    print(deinterleaver.id_to_coordinates())  # Expected (12, 34, 56)


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
