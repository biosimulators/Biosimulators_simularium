#!/bin/zsh

# TODO: read this from pyproject.toml
echo "What python version would you like to use for this environment?: "
read -r python_version

poetry env use python"${python_version}"
poetry run pip install --upgrade pip
poetry lock --no-update

if poetry install -v; then
   if poetry run ./install-with-smoldyn-mac-silicon.sh; then
      echo "Poetry installed Smoldyn and Biosimulators_simularium. Done."
   else
      echo "Smoldyn could not be installed. Exiting."
      exit 1
   fi
else
  echo "Could not install the deps. Exiting."
  exit 1
fi
