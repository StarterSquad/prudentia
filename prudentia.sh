#!/bin/bash

#http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in
SOURCE="${BASH_SOURCE[0]}"
# resolve $SOURCE until the file is no longer a symlink
while [ -h "${SOURCE}" ]; do
  DIR="$( cd -P "$( dirname "${SOURCE}" )" && pwd )"
  SOURCE="$(readlink "${SOURCE}")"
  # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
  [[ ${SOURCE} != /* ]] && SOURCE="${DIR}/${SOURCE}"
done
DIR="$( cd -P "$( dirname "${SOURCE}" )" && pwd )"

# Change cwd in Prudentia dir
cd ${DIR}

SETUP=false
if [ "$1" == "setup" ]; then
  echo "Setting up Prudentia ..."
  SETUP=true
fi

GLOBAL_BIN="/usr/bin/prudentia"
if [[ ! -x ${GLOBAL_BIN} ]]; then
  LINK=false
  if ! ${SETUP} ; then
    read -p "Do you want to link Prudentia to ${GLOBAL_BIN}? [y/N] " -e answer
    if [ "${answer}" = "y" ]; then
      LINK=true
    fi
  else
    LINK=true
  fi
  if ${LINK} ; then
    sudo ln -s ${DIR}/$(basename $0) ${GLOBAL_BIN}
  fi
fi

if [ -z "$( which python )" ]; then
    echo "Please, install Python (>=2.7)."
    exit 1
elif [ -z "$( which virtualenv )" ]; then
    echo "Please, install Virtualenv."
    exit 1
fi

# If Prudentia runs from the develop branch pulls from origin if the local and remote commit aren't the same
if [ "$( /usr/bin/git rev-parse --abbrev-ref HEAD )" == "develop" ]; then
  if [ ! "$( /usr/bin/git log --pretty=%H ...refs/heads/develop^ )" == "$( /usr/bin/git ls-remote origin -h refs/heads/develop |cut -f1 )" ]; then
    /usr/bin/git pull
  fi
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

if ! ${SETUP} ; then
  python -u prudentia.py "$@" 2>&1
else
  exit 0
fi
