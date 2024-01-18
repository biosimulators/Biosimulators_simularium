import platform
import sys
from subprocess import run, CalledProcessError


USER_PLATFORM = platform.system().lower()


def run_install():
    if 'darwin' in USER_PLATFORM:
        return install_macOS()
    elif 'linux' in USER_PLATFORM:
        return install_linux()
    else:
        raise RuntimeError('Unsupported Platform.')


def install_macOS():
    tarball_name = "smoldyn-2.72-mac.tgz"
    tar_dir = tarball_name.replace('.tgz', '')
    try:
        run("poetry env use python3.10".split(), check=True)
        run("poetry run pip install --upgrade pip".split(), check=True)
        run("poetry lock --no-update")
        run("poetry install -v".split(), check=True)
        run("poetry run pip uninstall smoldyn".split(), check=True)
        run("wget https://www.smoldyn.org/smoldyn-2.72-mac.tgz".split(), check=True)
        run(f"tar -xzvf {tarball_name}".split(), check=True)
        run(f"rm {tarball_name}".split(), check=True)
        run(f"cd {tar_dir}".split(), check=True)
        run(f"sudo -H ./install.sh".split(), check=True)
        run("cd ..".split(), check=True)
        run("poetry run pip install -e .".split(), check=True)
    except CalledProcessError as e:
        print(f'An error occured: {e}')
        print('Exiting')
        sys.exit(1)


def install_linux():
    try:
        run("echo 'smoldyn' >> requirements.txt".split(), check=True)
        run("pip install -r requirements.txt".split(), check=True)
    except CalledProcessError as e:
        print(f'An error occured: {e}. Exiting')
        sys.exit(1)


if __name__ == '__main__':
    run_install()
