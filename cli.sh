#!/bin/bash

PRJ_DIR="$(dirname "$(dirname "${BASH_SOURCE[0]}")")"
cd ${PRJ_DIR}/env/test
#echo 'Project directory: ' ${PRJ_DIR}

python ../../src/cli.py "$@" 2>&1