#!/bin/bash

test_file="$1"

file=biosimulators_simularium/tests/"${test_file}".py

mypy "${file}" \
  && poetry run python3 "${file}"

 
