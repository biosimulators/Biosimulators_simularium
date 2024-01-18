#!/bin/bash

test_file="$1"

poetry run python3 biosimulators_simularium/tests/"${test_file}".py

 
