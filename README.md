# Biosimulators_simularium
Converting Biosimulators spatial simulation outputs into a Simularium-compliant format.


*PLEASE NOTE:*
If you are using Apple silicon or Windows, you MUST use the Building from Source installation. Currently, smoldyn is only
available on PyPI cleanly on Linux.


## Installation with Python(PyPI) (_**Recommended**_)

The easiest way to interact with `Biosimulators_simularium` is via the Python Package Index and a
[virtual environment](https://docs.python.org/3/tutorial/venv.html). 

   1. `poetry use python3.10`
2. 
We recommend [installing and using Conda](https://conda.io/projects/conda/en/latest/user-guide/concepts/environments.html):
   
   After you have created the environment...

   1. `conda create -n biosimularium python=3.10`
   2. `conda activate biosimularium`
   3. `pip install biosimulators-simularium`

   To verify successful platform installation...
   
   1. `python3`
   2. `import biosimulators_simularium as biosimularium`
   3. `biosimularium.__version__` should display the most recent version with no errors.

## Installation (Building from Source) (Preferred)
The preferred build-from-source method involves using Python Poetry. Please ensure that this
is globally installed on your machine. The preferred method of installation from source
is through the use of the `install-deps.sh` script that is included at the root of this
repo. Follow the instructions below to install the environment on your machine (mac):

1. `git clone https://github.com/biosimulators/biosimulators-simularium.git`
2. `cd Biosimulators_simularium`
3. `chmod +x ./install.sh`
4. `./install.sh`
5. OPTIONAL: `poetry shell`
6. `python3`
7. `import biosimulators_simularium`

If there are no errors, you are all set!


## Installation (Building from Source) (Alternative)
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

#### Generating a 3d stochastic particle diffusion simulation visualization is as easy as:

1. Defining the filepath to an unpacked directory/archive in which a Smoldyn model resides
   and defining the name of simularium file. We also want to save the simularium file in JSON format:
```python
from biosimulators_simularium import generate_simularium_file


archive_root = 'biosimulators_simularium/tests/fixtures/archives/MinE'
simularium_fn = 'simulation'
is_json = True
```
2. Generating a simularium file from the model file housed in the `archive_root`:
```python
generate_simularium_file(
   working_dir=archive_root,
   simularium_filename=simularium_fn,
   use_json=is_json
)

import os 

assert os.path.exists(os.path.join(archive_root, simularium_fn)))
```

#### Here is another, slightly more complex example in which agent parameters such as molecular mass and density are defined:
```python
"""Generating a simularium file for the MinE Smoldyn model."""

import os 
from biosimulators_simularium import generate_simularium_file

# define the working dir: here we use a dir from the tests library as an example.
working_dir = 'biosimulators_simularium/tests/fixtures/crowding'

# define the simularium filepath (using the working dir as root in this case)
simularium_fn = os.path.join(working_dir, 'simplified-api-output')

# define the path to the smoldyn model file which in this case is assumed to be in the working dir
model_fp = os.path.join(working_dir, 'model.txt')

# define agent parameters (for this example, we randomly select masses)
red_molecular_mass = 11004
green_molecular_mass = 12424

# create a parameter mapping that maps simulation species type names to respective density and molecular_mass
agent_params = {
    'red': {
        'density': 1.0,
        'molecular_mass': red_molecular_mass,
    },
    'green': {
        'density': 1.0,
        'molecular_mass': green_molecular_mass,
    }
}

# generate a simularium file from the given parameters
generate_simularium_file(
    working_dir=working_dir,
    simularium_filename=simularium_fn,
    agent_params=agent_params,
    model_fp=model_fp
)

# test the existence of a simularium file
try:
    assert os.path.exists(simularium_fn)
    print(f'{simularium_fn} has been successfully generated.')
except:
    AssertionError('A simularium file could not be generated.')
```

Consider also this MinE simulation where we use the params function to extract parameters of agents from the Smoldyn model file:

```python
import os 
from biosimulators_simularium.simulation_data import generate_agent_params_for_minE
from biosimulators_simularium.exec import generate_simularium_file
# define the working dir
working_dir = 'biosimulators_simularium/tests/fixtures/MinE'

# define the simularium filepath (using the working dir as root in this case)
simularium_fn = os.path.join(working_dir, 'simplified-api-output')

model_fp = os.path.join(working_dir, 'model.txt')

base_mass = 12100
density = 1.0
agent_params = generate_agent_params_for_minE(model_fp, base_mass, density)

generate_simularium_file(
    working_dir=working_dir,
    simularium_filename=simularium_fn,
    agent_params=agent_params,
    model_fp=model_fp
)

try:
    assert os.path.exists(simularium_fn)
    print(f'{simularium_fn} has been successfully generated.')
except:
    AssertionError('A simularium file could not be generated.')
```

You may then navigate to https://simularium.allencell.org/viewer and drag/drop the newly generated simularium
file into the GUI window.


### We welcome any and all collaborations and/or raising of issues:

   To report an issue, please visit [our Github issues page](https://github.com/biosimulators/Biosimulators_simularium/issues).

   To contact us, please send an email to apatrie@uchc.edu or info@biosimulators.org


