from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='biosimulators-simularium',
    version='0.2.7',
    packages=find_packages(),
    url='https://github.com/biosimulators/Biosimulators_simularium',
    author='Alexander Patrie/BioSimulators Team',
    author_email='info@biosimulators.org',
    description='A Python tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'zarr',
        'simulariumio',
        'biosimulators-utils[smoldyn]'
    ],
    entry_points={
            'console_scripts': [
                'biosimulators-simularium = biosimulators_simularium.__main__:main',
            ],
    },
)
