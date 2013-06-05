#!/bin/bash

if [ "$(id -u)" != "0" ]
then
    echo "This script must be run as root" 1>&2
    exit 1
fi

OS=$(uname -s)

if [[ "${OS}" == *Linux* ]]
then
    echo "Operative system: Linux"

    apt-get --yes install git-core python-jinja2 python-yaml python-paramiko python-software-properties python-pip

    if [ ! -f /etc/apt/sources.list.d/rquillo-ansible-*.list ]
    then
        add-apt-repository ppa:rquillo/ansible
        apt-get update
    else
        echo -e "\nRepository 'rquillo' already present.\n"
    fi

    apt-get --yes install ansible

    pip install boto

    echo "Ansible installed correctly."
elif [[ "${OS}" == *Darwin* ]]
then
    echo "Operative system: MacOSX"

    if [ -z "$( which gcc )" ]
    then
        echo "You should make sure that gcc is installed"
	    echo "Download Xcode from App Store, then once it’s installed go to Xcode > Preferences > Downloads and install the Command Line Tools"
    else
        # http://www.pyrosoft.co.uk/blog/2012/06/26/installing-ansible-on-osx-lion/

        easy_install paramiko
        wait $!
        easy_install PyYAML
        wait $!
        easy_install jinja2
        wait $!

        if [ ! -d /tmp/ansible ]
        then
            cd /tmp
            git clone git://github.com/ansible/ansible.git -b release1.0
            cd ansible
        else
            cd /tmp/ansible
        fi

        make install

        echo "Ansible installed correctly."
    fi
fi