#!/bin/bash

test_file="$1"

file=biosimulators_simularium/tests/"${test_file}".py

poetry run mypy "${file}"
if poetry run python3 "${file}"; then
  echo "Success. Done."
else
  echo ":("
fi

 
