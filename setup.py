import os
from setuptools import setup, find_packages

# os.system('sudo -H smoldyn-2.72-mac/install.sh')

setup(
    packages=find_packages(),
    entry_points={
            'console_scripts': [
                'biosimulators-simularium = biosimulators_simularium.main:main',
            ],
    },
)
