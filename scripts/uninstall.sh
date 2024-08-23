#!/bin/bash
# !/bin/zsh

# echo "Enter the Python version of the poetry environment you wish to remove: "
# read -r version

version="$1"

if [ "$version" == "" ]; then
  echo "Please enter the version: "
  read -r version
else
  echo "Removing""${version}"
fi

if sudo poetry env remove python"${version}"; then
   echo "Python ${version} env successfully removed."
   ./clear-cache.sh
   echo "Poetry env and caches removed successfully removed. Done."
else
   echo "Something went wrong. Exiting."
   exit 1
fi
