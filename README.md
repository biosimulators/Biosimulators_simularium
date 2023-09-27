# Biosimulators_simularium
Converting Biosimulators spatial simulation outputs into a Simularium-compliant format. This tooling acts as a 
superset of `Biosimulators_utils`.

PLEASE NOTE: The command-line arguments for the standalone version of this program are as follows:

    -a (`str`): archive_rootpath => path to the root of your COMBINE/OMEX archive relative to where you currently are.
    -s (`str`): simularium_fp => desired path where to store the newly generated filepath. Will default to your OMEX archive.


## Getting Started with Python(PyPI) (_**Recommended**_)

The easiest way to interact with `Biosimulators_simularium` is via the Python Package Index and a
[virtual environment](https://docs.python.org/3/tutorial/venv.html). 
We recommend [installing and using Conda](https://conda.io/projects/conda/en/latest/user-guide/concepts/environments.html):
   
   After you have created the environment...

   1. `conda create -n biosimularium python=3.10`
   2. `conda activate biosimularium`
   3. `pip install biosimulators-simularium`

   To verify successfull platform and installation...
   
   1. `python3`
   2. `import biosimulators_simularium as biosimularium`
   3. `biosimularium.__version__` should display the most recent version with no errors.


## Getting Started with Docker (_*Experimental*_)

You may also interact with Biosimulators_simularium on a standalone-basis by using Docker. _Please note_: this feature
is experimental and may not be functional depending on the current development:


1. `cd {WHERE YOU ARE GOING TO WORK}`
2. `git clone https://github.com/biosimulators/biosimulators-simularium.git`
3. `cd Biosimulators_simularium`
4. Choose a tag-name for the image(we use a generic name here): `docker build -t biosimularium .`

Say we want to add a `.simularium` file to our COMBINE archive based on a Smoldyn model's output. We have this model file in an archive with the
rootpath of `./biosimulators_simularium/test_files/archives/minE_Andrews_052023` and save it to `./biosimulators_simularium/test_files/archives/minE_Andrews_052023`
(the same archive):

    docker run biosimularium \
      -a './biosimulators_simularium/test_files/archives/minE_Andrews_052023' \
      -s './biosimulators_simularium/test_files/archives/minE_Andrews_052023'


## Getting Started (Building from Source)


### BEFORE STARTING: This application uses Smoldyn to generate simulation data. Please install Smoldyn into your local environment. Instructions below use the Mac silicon install and Python 3.10. More information on installing Smoldyn can be found [here](https://www.smoldyn.org/download.html)

1. Set up a virtual environment. We recommend using Conda: `conda create -n biosimularium 
python=3.10`

2. `conda activate biosimularium`

3. `cd {REPO DESTINATION}`

4. `git clone https://github.com/biosimulators/biosimulators-simularium.git`

5. `cd Biosimulators_simularium`

6. `pip install -e .`

7. FOR MAC ONLY: Download Smoldyn for your Mac (Silicon or Intel): https://www.smoldyn.org/download.html
   - `cd /path/to/your/download/of/smoldyn-2.72-mac` 
   - `sudo -H ./install.sh`

8. OTHERWISE: `pip install smoldyn`


A Jupyter Notebook will soon be available which is based off of the simulariumio tutorial series. This will 
give users the ability to have a tool that quickly generates simularium files with the click of a button based 
on a valid COMBINE/OMEX archive.


### We welcome any and all collaborations and/or raising of issues:

   To report an issue, please visit [our Github issues page](https://github.com/biosimulators/Biosimulators_simularium/issues).

   To contact us, please send an email to apatrie@uchc.edu or info@biosimulators.org


