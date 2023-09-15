from typing import Dict
import os


__all__ = [
    'make_files_dict',
    'remove_output_files',
    'remove_file',
]


def make_files_dict(fp) -> Dict[str, str]:
    d = {}
    if os.path.exists(fp):
        for root, _, files in os.walk(fp):
            for i, f in enumerate(files):
                fp = os.path.join(root, f)
                d[fp + str(i)] = fp
    return d


def remove_output_files(fp='biosimulators_simularium/files/archives/Andrews_ecoli_0523') -> None:
    if os.path.exists(fp):
        for root, _, files in os.walk(fp):
            for f in files:
                fp = os.path.join(root, f)
                if fp.endswith('.txt') and 'model' not in fp:
                    os.remove(fp)


def remove_file(fp) -> None:
    return os.remove(fp) if os.path.exists(fp) else None
