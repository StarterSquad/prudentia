#!/bin/bash

python -c 'import sys; print sys.real_prefix' 2>/dev/null && INVENV=1 || INVENV=0

if [ ${INVENV} == 0 ]; then
  echo -e "No active Virtual Environment.\n"
  if [ ! -d "./p-env/" ]; then
    virtualenv p-env
  fi

  source ./p-env/bin/activate

  TMP_DEPS=/tmp/prudentia_test_temp_deps_${RANDOM}
  pip freeze -l > ${TMP_DEPS}
  if ! cmp ./requirements.txt ${TMP_DEPS} > /dev/null 2>&1
  then
    echo "Installing Python dependencies ..."
    diff ./requirements.txt ${TMP_DEPS}
    pip install -r ./requirements.txt
  fi
else
  echo -e "Virtual Env active.\n"
fi

export PRUDENTIA_USER_DIR=.
export PRUDENTIA_LOG=

rm -rf tests/envs tests/cover

nosetests -c nose.cfg $@
