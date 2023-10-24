"""
:Author: Alexander Patrie <apatrie@uchc.edu>
:Date: 2023-09-16
:Copyright: 2023, UConn Health
:License: MIT


Utilities for reading/writing/adjusting Combine Archive contents, including the construction of a manifest
"""


import os


def create_archive_dir(archive_path: str):
    # first, we have to create the combine archive
    if not os.path.exists(archive_path):
        return os.mkdir(archive_path)


def compile_archive_contents():
    pass
