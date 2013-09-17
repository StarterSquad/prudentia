#!/bin/bash

OS=$(uname -s)
ANSIBLE_VERSION=1.1

if [ -z "$( which ansible )" ]
then
    if [[ "${OS}" == *Linux* ]]
    then
        echo "Operative system: Linux"

        sudo apt-get --yes install git-core python-jinja2 python-yaml python-paramiko python-software-properties python-pip

        if [ ! -f /etc/apt/sources.list.d/rquillo-ansible-*.list ]
        then
            sudo add-apt-repository ppa:rquillo/ansible
            sudo apt-get update
        else
            echo -e "\nRepository 'rquillo' already present.\n"
        fi

        sudo apt-get --yes install ansible

        sudo pip install boto
    elif [[ "${OS}" == *Darwin* ]]
    then
        echo "Operative system: MacOSX"

        if [ -z "$( which gcc )" ]
        then
            echo "You should make sure that gcc is installed"
            echo "Download Xcode from App Store, then once it’s installed go to Xcode > Preferences > Downloads and install the Command Line Tools"
        else
            # http://www.pyrosoft.co.uk/blog/2012/06/26/installing-ansible-on-osx-lion/

            echo ""
            sudo easy_install paramiko
            wait $!
            sudo easy_install PyYAML
            wait $!
            sudo easy_install jinja2
            wait $!
            echo ""

            if [ -d /tmp/ansible ]
            then
                echo "Found temporary ansible dir, removing ..."
                rm -rf /tmp/ansible
            fi

            echo "Installing Ansible ${ANSIBLE_VERSION} ..."
            cd /tmp
            git clone git://github.com/ansible/ansible.git -b release${ANSIBLE_VERSION}
            cd ansible

            sudo make install
        fi
    fi
else
    CURRENT_VERSION=$(ansible --version)
    echo ${CURRENT_VERSION}
fi