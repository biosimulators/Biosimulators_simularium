"""This is an example workflow using the v0.5.0 Simplified API."""


import os
from biosimulators_simularium.convert import generate_output_data_object


def convert_minE(model_fp: str, display_data_dict):
    """TODO: Create display data dict for each mol in the simulation."""

    data_obj = generate_output_data_object(
        file_data=model_fp,

    )



