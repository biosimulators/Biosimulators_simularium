#!/bin/bash 

use_poetry="$1"

test_file="$2"

if [ "${use_poetry}"=="0" ]; then
    conda activate biosimularium
    python3 biosimulators_simularium/tests/"${test_file}".py
else
    poetry run python3 biosimulators_simularium/tests/"${test_file}".py
fi
 
