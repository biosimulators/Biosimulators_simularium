from setuptools import setup, find_packages


setup(
    name='biosimulators-simularium',
    version='0.2.4',
    packages=find_packages(),
    url='https://github.com/biosimulators/Biosimulators_simularium',
    author='Alexander Patrie/BioSimulators Team',
    author_email='info@biosimulators.org',
    description='A Python tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format.',
    long_description=open('README.md').read(),
    install_requires=[
        'zarr',
        'simulariumio[tutorial]',
        'smoldyn',
        'biosimulators-utils'
    ],
    entry_points={
            'console_scripts': [
                'biosimulators-simularium = biosimulators_simularium.__main__:main',
            ],
    },
)
