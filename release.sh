#!/bin/zsh

# Create and publish a new version by creating and pushing a git tag for
# the version and publishing the version to PyPI. Also perform some
# basic checks to avoid mistakes in releases, for example tags not
# matching PyPI.


set +e 
use_poetry="$1"
version=$(grep "__version__" setup.py | awk -F\' '{print $2}')

# Check version is valid
if [ "$use_poetry" != 1 ]; then
  setup_py_version="$(python setup.py --version)"
else
  setup_py_version="$(poetry run python3 setup.py --version)"
fi
if [ "$setup_py_version" != "$version" ]; then
    echo "setup.py has version $setup_py_version, not $version."
    echo "Aborting."
    exit 1
fi

# Check working directory is clean
if [ ! -z "$(git status --untracked-files=no --porcelain)" ]; then
    echo "You have changes that have yet to be committed."
    echo "Aborting PyPI upload and attempting to commit your changes."
    ./commit.sh
fi

# Check that we are on main
branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "$branch" != "dev" ]; then
    echo "You are on $branch but should be on dev for releases."
    echo "Aborting."
    exit 1
fi

# Create and push git tag
git tag -m "Version v$version" "v$version"
git push --tags

# Create and publish package
if [ "$use_poetry" != 1 ]; then
  echo "Not using poetry."
  python setup.py sdist bdist_wheel
  twine check dist/*
  twine upload dist/*
  rm -r dist && rm -r biosimulators_simularium.egg-info && rm -r build
else
  echo "Using poetry"
  poetry run python3 setup.py sdist
  twine check dist/*
  twine upload dist/*
  rm -r dist && rm -r biosimulators_simularium.egg-info
fi

# twine upload --repository biosimulators-simularium

echo "Version v$version has been published on PyPI and has a git tag."
