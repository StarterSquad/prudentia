#!/bin/bash

if [ "$(id -u)" == "0" ]
then
    echo "This script must NOT be run as root" 1>&2
    exit 1
fi

OS=$(uname -s)
VAGRANT_VERSION=1.2.2

if [[ "${OS}" == *Linux* ]]
then
    if [ -z "$( which virtualbox )" ]
    then
        if [ ! -f /etc/apt/sources.list.d/debfx-virtualbox-*.list ]; then
            sudo add-apt-repository ppa:debfx/virtualbox
            sudo apt-get update
        fi

        sudo apt-get --yes install virtualbox-ose virtualbox-guest-additions
    fi
elif [[ "${OS}" == *Darwin* ]]
then
    if [[ -z "$( which VirtualBox )" ]]
    then
        curl http://download.virtualbox.org/virtualbox/4.2.12/VirtualBox-4.2.12-84980-OSX.dmg -o VirtualBox.dmg
        hdiutil attach VirtualBox.dmg
        sudo installer -pkg /Volumes/VirtualBox/VirtualBox.pkg -target /
        hdiutil detach /Volumes/VirtualBox
        rm VirtualBox.dmg
    fi
fi

echo -e "\nVirtualbox installed correctly.\n"

VAGRANT_EXE=""

if [[ "${OS}" == *Linux* ]]
then
    if [ -z "$( which vagrant )" ]
    then
        wget http://files.vagrantup.com/packages/7e400d00a3c5a0fdf2809c8b5001a035415a607b/vagrant_${VAGRANT_VERSION}_x86_64.deb -O vagrant.deb
        sudo dpkg -i vagrant.deb
        rm vagrant.deb

        sudo ln -s /opt/vagrant/bin/vagrant /usr/bin/vagrant
    fi
    VAGRANT_EXE="vagrant"
elif [[ "${OS}" == *Darwin* ]]
then
    if [ -z "$( which Vagrant )" ]
    then
        curl http://files.vagrantup.com/packages/7e400d00a3c5a0fdf2809c8b5001a035415a607b/Vagrant-${VAGRANT_VERSION}.dmg -o Vagrant.dmg
        hdiutil attach Vagrant.dmg
        sudo /Volumes/Vagrant/uninstall.tool
        sudo installer -pkg /Volumes/Vagrant/Vagrant.pkg -target /
        hdiutil detach /Volumes/Vagrant
        rm Vagrant.dmg
    else
        vagrant -v
    fi
    VAGRANT_EXE="vagrant"
fi

echo -e "\nVagrant installed correctly.\n"

DEFAULT_BOX_NAME="precise_base"
if [ -z "$( vagrant box list | grep ${DEFAULT_BOX_NAME} )" ]; then
    read -p "You don't have the base Ubuntu Precise (64 bit) box, do you want to add it? [y/N] " -e answer

    if [ "${answer}" = "y" ]; then
        # http://www.vagrantbox.es/
        ${VAGRANT_EXE} box add ${DEFAULT_BOX_NAME} http://files.vagrantup.com/precise64.box
    fi
fi