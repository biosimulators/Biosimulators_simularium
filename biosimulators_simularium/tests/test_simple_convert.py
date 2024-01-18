import os
from biosimulators_simularium import generate_simularium_file


def test_convert():
    archive_root = 'biosimulators_simularium/tests/fixtures/archives/MinE'
    simularium_fn = 'simulation'
    is_json = True

    generate_simularium_file(
        working_dir=archive_root,
        simularium_filename=simularium_fn,
        use_json=is_json
    )
    assert os.path.exists(os.path.join(archive_root, simularium_fn))


