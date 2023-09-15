import os
from platform import platform
from biosimulators_simularium.converters.io import SmoldynDataConverter
from subprocess import run


def install_smoldyn_mac():
    plat = platform()
    mac = "Darwin"
    if mac or mac.lower() in plat:
        run("cd smoldyn-2.72-mac")
        run("sudo -H ./install.sh")


def generate_simularium_file():
    pass

