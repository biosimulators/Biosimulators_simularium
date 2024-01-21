#!/bin/bash

test_file="$1"

file=biosimulators_simularium/tests/"${test_file}".py

set +e

if poetry run mypy "${file}" && poetry run python3 "${file}"; then
  echo "Success. Done."
else
  echo ":("
fi

 
