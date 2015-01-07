#!/bin/bash

if [ -z "$( which python )" ]; then
    echo "Please, install Python (>=2.6)."
    exit 1
elif [ -z "$( which virtualenv )" ]; then
    echo "Please, install Virtualenv."
    exit 1
fi

if [ ! -d "./p-env/" ]; then
    virtualenv p-env
fi

source ./p-env/bin/activate

TMP_DEPS=/tmp/prudentia_temp_deps_${RANDOM}
pip freeze -l > ${TMP_DEPS}
if ! cmp ./requirements.txt ${TMP_DEPS} > /dev/null 2>&1
then
  echo "Installing Python dependencies ..."
  cat ${TMP_DEPS}
  pip install -r ./requirements.txt
fi

PYTHONPATH=. PYTHONUNBUFFERED=1 bin/prudentia "$@" 2>&1
