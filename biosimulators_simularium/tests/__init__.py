import os


def make_test_dir(output_dir):
    if not os.path.exists(output_dir):
            os.mkdir(output_dir)
