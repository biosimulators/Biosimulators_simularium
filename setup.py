from setuptools import setup, find_packages


setup(
    packages=find_packages(),
    entry_points={
            'console_scripts': [
                'biosimulators-simularium = biosimulators_simularium.main:main',
            ],
    },
)
