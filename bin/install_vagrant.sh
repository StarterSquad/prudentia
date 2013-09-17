#!/bin/bash

OS=$(uname -s)
VAGRANT_HASH="b12c7e8814171c1295ef82416ffe51e8a168a244"
VAGRANT_VERSION="1.3.1"

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

echo -e "Virtualbox is present"

function install_vagrant {
   if [[ "${OS}" == *Linux* ]]
    then
        wget http://files.vagrantup.com/packages/${VAGRANT_HASH}/vagrant_${VAGRANT_VERSION}_x86_64.deb -O vagrant.deb
        sudo dpkg -i vagrant.deb
        rm vagrant.deb
    elif [[ "${OS}" == *Darwin* ]]
    then
        curl http://files.vagrantup.com/packages/${VAGRANT_HASH}/Vagrant-${VAGRANT_VERSION}.dmg -o Vagrant.dmg
        hdiutil attach Vagrant.dmg
        sudo /Volumes/Vagrant/uninstall.tool
        sudo installer -pkg /Volumes/Vagrant/Vagrant.pkg -target /
        hdiutil detach /Volumes/Vagrant
        rm Vagrant.dmg
    fi
}

if [ -z "$( which vagrant )" ]
then
    install_vagrant
else
    CURRENT_VERSION=$(vagrant -v)
    if [ "${CURRENT_VERSION}" == "Vagrant ${VAGRANT_VERSION}" ]
    then
        echo ${CURRENT_VERSION}
    else
        echo -e "Vagrant exists but we'll update it ... (and answer Yes to the next question)\n"
        install_vagrant
    fi
fi

DEFAULT_BOX_NAME="precise_base"
if [ -z "$( vagrant box list | grep ${DEFAULT_BOX_NAME} )" ]; then
    read -p "You don't have the base Ubuntu Precise (64 bit) box, do you want to add it? [y/N] " -e answer

    if [ "${answer}" = "y" ]; then
        # http://www.vagrantbox.es/
        vagrant box add ${DEFAULT_BOX_NAME} http://files.vagrantup.com/precise64.box
    fi
fi