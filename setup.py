from setuptools import setup, find_packages


setup(
    name='biosimulators-simularium',
    version='0.2.0',
    packages=find_packages(),
    url='https://github.com/biosimulators/Biosimulators_simularium',
    author='Alexander Patrie/BioSimulators Team',
    author_email='apatrie@uchc.edu/info@biosimulators.org',
    install_requires=[
        'zarr',
        'simulariumio',
        'smoldyn',
    ],
    entry_points={
            'console_scripts': [
                'biosimulators-simularium = biosimulators_simularium.__main__:main',
            ],
    },
)
