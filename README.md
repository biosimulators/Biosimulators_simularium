# Biosimulators_simularium
Converting Biosimulators spatial simulation outputs into a Simularium-compliant format. This tooling acts as a 
superset of `Biosimulators_utils`.


*PLEASE NOTE:*
If you are using Apple silicon or Windows, you MUST use the Building from Source installation. Currently, smoldyn is only
available on PyPI cleanly on Linux.


## Installation with Python(PyPI) (_**Recommended**_)

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


## Installation (Building from Source)
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


### Getting-Started Example:
```python
import os
from biosimulators_simularium.archives.data_model import SmoldynCombineArchive
from biosimulators_simularium.converters.data_model import SmoldynDataConverter


# define the combine archive rootpath
crowding_archive_path = os.path.join('biosimulators_simularium', 'tests', 'fixtures', 'archives', 'crowding4')

# construct an archive instance based on the rootpath
archive = SmoldynCombineArchive(
    rootpath=crowding_archive_path,
    simularium_filename='crowding4'
)

# construct a data converter
converter = SmoldynDataConverter(archive)

# define the agents from the simulation that you are going to visualize. 
# The shape of the data is expected to be as follows:
    # (agent name, agent radius, agent hex color)
agents = [
    ('red(up)', 0.2, '#eb1414'),
    ('green(up)', 0.5, '#5dcf30'),
]

# pass the agents to the converter method
converter.generate_simularium_file(agents=agents, io_format='JSON', box_size=20.0)
```

You may then navigate to https://simularium.allencell.org/viewer and drag/drop the newly generated simularium
file into the GUI window.


### We welcome any and all collaborations and/or raising of issues:

   To report an issue, please visit [our Github issues page](https://github.com/biosimulators/Biosimulators_simularium/issues).

   To contact us, please send an email to apatrie@uchc.edu or info@biosimulators.org


