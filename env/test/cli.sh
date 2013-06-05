#!/bin/bash

PRJ_DIR="$(dirname "$(dirname "${BASH_SOURCE[0]}")")"
cd ${PRJ_DIR}
#echo 'Project directory: ' ${PRJ_DIR}

python cli.py "$@" 2>&1