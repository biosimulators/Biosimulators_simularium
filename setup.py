from setuptools import setup, find_packages
# noinspection PyProtectedMember

__version__ = '0.5.28'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='biosimulators-simularium',
    version=__version__,
    packages=find_packages(),
    url='https://github.com/biosimulators/Biosimulators_simularium',
    author='Alexander Patrie/BioSimulators Team',
    author_email='info@biosimulators.org',
    description='A Python tool for converting Biosimulators spatial simulation outputs into a Simularium-compliant format.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=["install.py"],
    entry_points={
            'console_scripts': [
                'biosimulators-simularium = biosimulators_simularium.__main__:main',
            ],
    },
)
