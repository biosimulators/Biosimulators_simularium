"""
:Author: Alexander Patrie <apatrie@uchc.edu>
:Date: 2023-10-24
:Copyright: 2023, UConn Health
:License: MIT


Utilities for reading/writing/adjusting Combine Archive contents, including the construction of a manifest
"""


import os
from typing import List, Tuple
from biosimulators_simularium.archives.data_model import CombineArchiveContent, CombineArchiveWriter


def build_archive(archive_path: str, content: List[Tuple[str, str, bool]]) -> None:
    """Build and write an archive specified at the `archive_path`.

        Args:
            archive_path:`str`: path at which you will save the newly generated combine archive.
            content:`List[Tuple[str, str, bool]]`: a list of content by which to create new instances of
                `CombineArchiveContent`. The expected data in the tuple are: (location, format, master). See
                `biosimulators_simularium.archives.data_model.CombineArchiveContent`.
    """
    create_archive_dir(archive_path)
    archive_contents = []
    for i, c in enumerate(content):
        add_content(archive_contents, c)
        print(f'Step number: {i}: archive_contents')
    CombineArchiveWriter().write_manifest(archive_contents, archive_path)


def create_archive_dir(archive_path: str):
    # first, we have to create the combine archive
    if not os.path.exists(archive_path):
        return os.mkdir(archive_path)


def add_content(all_contents: List, content: Tuple) -> None:
    new_content = CombineArchiveContent(*content)
    return all_contents.append(new_content)
