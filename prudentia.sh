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

# Change cwd in prudentia dir
cd ${DIR}

GLOBAL_BIN="/usr/bin/prudentia"
if [[ ! -x ${GLOBAL_BIN} ]]
then
  read -p "Do you want to link Prudentia to ${GLOBAL_BIN}? [y/N] " -e answer
  if [ "${answer}" = "y" ]
  then
      sudo ln -s ${DIR}/$(basename $0) ${GLOBAL_BIN}
  fi
fi

if [ -z "$( which python )" ]
then
    echo "Please, install Python (>=2.7)."
    exit 1
elif [ -z "$( which virtualenv )" ]
then
    echo "Please, install Virtualenv."
    exit 1
fi

if [ ! -d "./p-env/" ]
then
    virtualenv p-env
fi

source ./p-env/bin/activate

pip freeze > /tmp/prudentia_temp_deps
if ! cmp ./requirements.txt /tmp/prudentia_temp_deps > /dev/null 2>&1
then
  echo "Installing Python dependencies ..."
  pip install -r ./requirements.txt
fi

./p-env/bin/python prudentia.py "$@"
