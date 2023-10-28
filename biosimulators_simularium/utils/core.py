"""This file contains methods for getting file directory information, parsing platform, and coordinate interleaving.
"""


import os
from typing import Union
from enum import Enum
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
    'ContentFormat',
    'HEX_COLORS'
]


class ContentFormat(Enum):
    SMOLDYN = "http://purl.org/NET/mediatypes/text/smoldyn+plain"


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


def num_steps(timeEnd, timeStart, timeStep) -> Union[int, float]:
    """Return the number of steps to record for the simulation given end, start, and step size."""
    return (timeEnd - timeStart) / timeStep


HEX_COLORS = {
    "aliceblue": "#F0F8FF",
    "antiquewhite": "#FAEBD7",
    "aqua": "#00FFFF",
    "aquamarine": "#7FFFD4",
    "azure": "#F0FFFF",
    "beige": "#F5F5DC",
    "bisque": "#FFE4C4",
    "black": "#000000",
    "blanchedalmond": "#FFEBCD",
    "blue": "#0000FF",
    "blueviolet": "#8A2BE2",
    "brown": "#A52A2A",
    "burlywood": "#DEB887",
    "cadetblue": "#5F9EA0",
    "chartreuse": "#7FFF00",
    "chocolate": "#D2691E",
    "coral": "#FF7F50",
    "cornflowerblue": "#6495ED",
    "cornsilk": "#FFF8DC",
    "crimson": "#DC143C",
    "cyan": "#00FFFF",
    "darkblue": "#00008B",
    "darkcyan": "#008B8B",
    "darkgoldenrod": "#B8860B",
    "darkgray": "#A9A9A9",
    "darkgreen": "#006400",
    "darkgrey": "#A9A9A9",
    "darkkhaki": "#BDB76B",
    "darkmagenta": "#8B008B",
    "darkolivegreen": "#556B2F",
    "darkorange": "#FF8C00",
    "darkorchid": "#9932CC",
    "darkred": "#8B0000",
    "darksalmon": "#E9967A",
    "darkseagreen": "#8FBC8F",
    "darkslateblue": "#483D8B",
    "darkslategray": "#2F4F4F",
    "darkslategrey": "#2F4F4F",
    "darkturquoise": "#00CED1",
    "darkviolet": "#9400D3",
    "deeppink": "#FF1493",
    "deepskyblue": "#00BFFF",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1E90FF",
    "firebrick": "#B22222",
    "floralwhite": "#FFFAF0",
    "forestgreen": "#228B22",
    "fuchsia": "#FF00FF",
    "gainsboro": "#DCDCDC",
    "ghostwhite": "#F8F8FF",
    "gold": "#FFD700",
    "goldenrod": "#DAA520",
    "gray": "#808080",
    "green": "#008000",
    "greenyellow": "#ADFF2F",
    "grey": "#808080",
    "honeydew": "#F0FFF0",
    "hotpink": "#FF69B4",
    "indianred": "#CD5C5C",
    "indigo": "#4B0082",
    "ivory": "#FFFFF0",
    "khaki": "#F0E68C",
    "lavender": "#E6E6FA",
    "lavenderblush": "#FFF0F5",
    "lawngreen": "#7CFC00",
    "lemonchiffon": "#FFFACD",
    "lightblue": "#ADD8E6",
    "lightcoral": "#F08080",
    "lightcyan": "#E0FFFF",
    "lightgoldenrodyellow": "#FAFAD2",
    "lightgray": "#D3D3D3",
    "lightgreen": "#90EE90",
    "lightgrey": "#D3D3D3",
    "lightpink": "#FFB6C1",
    "lightsalmon": "#FFA07A",
    "lightseagreen": "#20B2AA",
    "lightskyblue": "#87CEFA",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#B0C4DE",
    "lightyellow": "#FFFFE0",
    "lime": "#00FF00",
    "limegreen": "#32CD32",
    "linen": "#FAF0E6",
    "magenta": "#FF00FF",
    "maroon": "#800000",
    "mediumaquamarine": "#66CDAA",
    "mediumblue": "#0000CD",
    "mediumorchid": "#BA55D3",
    "mediumpurple": "#9370DB",
    "mediumseagreen": "#3CB371",
    "mediumslateblue": "#7B68EE",
    "mediumspringgreen": "#00FA9A",
    "mediumturquoise": "#48D1CC",
    "mediumvioletred": "#C71585",
    "midnightblue": "#191970",
    "mintcream": "#F5FFFA",
    "mistyrose": "#FFE4E1",
    "moccasin": "#FFE4B5",
    "navajowhite": "#FFDEAD",
    "navy": "#000080",
    "oldlace": "#FDF5E6",
    "olive": "#808000",
    "olivedrab": "#6B8E23",
    "orange": "#FFA500",
    "orangered": "#FF4500",
    "orchid": "#DA70D6",
    "palegoldenrod": "#EEE8AA",
    "palegreen": "#98FB98",
    "paleturquoise": "#AFEEEE",
    "palevioletred": "#DB7093",
    "papayawhip": "#FFEFD5",
    "peachpuff": "#FFDAB9",
    "peru": "#CD853F",
    "pink": "#FFC0CB",
    "plum": "#DDA0DD",
    "powderblue": "#B0E0E6",
    "purple": "#800080",
    "rebeccapurple": "#663399",
    "red": "#FF0000",
    "rosybrown": "#BC8F8F",
    "royalblue": "#4169E1",
    "saddlebrown": "#8B4513",
    "salmon": "#FA8072",
    "sandybrown": "#F4A460",
    "seagreen": "#2E8B57",
    "seashell": "#FFF5EE",
    "sienna": "#A0522D",
    "silver": "#C0C0C0",
    "skyblue": "#87CEEB",
    "slateblue": "#6A5ACD",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#FFFAFA",
    "springgreen": "#00FF7F",
    "steelblue": "#4682B4",
    "tan": "#D2B48C",
    "teal": "#008080",
    "thistle": "#D8BFD8",
    "tomato": "#FF6347",
    "turquoise": "#40E0D0",
    "violet": "#EE82EE",
    "wheat": "#F5DEB3",
    "white": "#FFFFFF",
    "whitesmoke": "#F5F5F5",
    "yellow": "#FFFF00",
    "yellowgreen": "#9ACD32"
}
