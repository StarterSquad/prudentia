#!/bin/bash

if [ -z "$( which python )" ]
then
    echo "Please, install Python (>=2.7)."
    exit 1
fi

if [ -z "$( which virtualenv )" ]
then
    echo "Please, install Virtualenv."
    exit 1
fi

if [ ! -d "./p-env/" ]
then
    virtualenv p-env
fi

source ./p-env/bin/activate

echo "Checking dependencies ..."
pip install -r ./requirements.txt > /dev/null
./bin/install_vagrant.sh > /dev/null

./p-env/bin/python prudentia.py
