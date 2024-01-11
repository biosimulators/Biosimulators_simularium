from os.path import join as pj
from os import getcwd
from biosimulators_simularium.exec import exec_combine_archive_and_simularium
from biosimulators_simularium.simulation_data import generate_agent_params_for_minE


def test_exec():
    # define parameter paths (TODO: derive these mostly from the working_dir)
    working_dir = 'biosimulators_simularium/tests/fixtures/archives/MinE'
    model_fp = pj(working_dir, 'model.txt')
    sed_fp = pj(working_dir, 'simulation.sedml')
    simularium_fn = 'simulation'
    base = getcwd()
    output_fp = pj(base, 'OUTPUT')
    output_omex_fp = pj(base, 'OUTPUT.omex')

    # define simulation agent parameters. Let's use the helper:
    m_MinE = 12100
    rho_global = 1.0
    agent_parameters = generate_agent_params_for_minE(model_fp, m_MinE, rho_global)

    exec_combine_archive_and_simularium(
        working_dir=working_dir,
        sed_doc_path=sed_fp,
        output_dir=output_fp,
        simularium_filename=simularium_fn,
        save_path=output_omex_fp,
        agent_params=agent_parameters
    )


if __name__ == '__main__':
    test_exec()
