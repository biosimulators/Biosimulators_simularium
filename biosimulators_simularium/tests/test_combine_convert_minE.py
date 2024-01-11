from os.path import join as pj
from os import getcwd
from biosimulators_simularium.exec import exec_combine_archive_and_simularium


def test_exec():
    working_dir = 'biosimulators_simularium/tests/fixtures/archives/MinE'
    model_fp = pj(working_dir, 'model.txt')
    sed_fp = pj(working_dir, 'simulation.sedml')
    simularium_fn = 'simulation.simularium'
    base = getcwd()
    output_fp = pj(base, 'OUTPUT')
    output_omex_fp = pj(base, 'OUTPUT.omex')
    exec_combine_archive_and_simularium(
        working_dir=working_dir,
        sed_doc_path=sed_fp,
        output_dir=output_fp,
        simularium_filename=simularium_fn,
        save_path=output_omex_fp
    )


if __name__ == '__main__':
    test_exec()
