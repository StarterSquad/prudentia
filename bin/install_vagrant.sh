#!/bin/bash

if [ "$(id -u)" == "0" ]
then
    echo "This script must NOT be run as root" 1>&2
    exit 1
fi

OS=$(uname -s)

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
        curl http://download.virtualbox.org/virtualbox/4.1.24/VirtualBox-4.1.24-82872-OSX.dmg -o VirtualBox.dmg
        hdid VirtualBox.dmg
        sudo installer -pkg /Volumes/VirtualBox/VirtualBox.pkg -target /
        rm VirtualBox.dmg
    fi
fi

echo -e "\nVirtualbox installed correctly.\n"

VAGRANT_EXE=""

if [[ "${OS}" == *Linux* ]]
then
    if [ -z "$( which vagrant )" ]
    then
        wget http://files.vagrantup.com/packages/476b19a9e5f499b5d0b9d4aba5c0b16ebe434311/vagrant_x86_64.deb
        sudo dpkg -i vagrant_x86_64.deb
        rm vagrant_x86_64.deb

        sudo ln -s /opt/vagrant/bin/vagrant /usr/bin/vagrant
    fi
    VAGRANT_EXE="vagrant"
elif [[ "${OS}" == *Darwin* ]]
then
    if [ -z "$( which Vagrant )" ]
    then
        curl http://files.vagrantup.com/packages/476b19a9e5f499b5d0b9d4aba5c0b16ebe434311/Vagrant.dmg -o Vagrant.dmg
        hdid Vagrant.dmg
        sudo installer -pkg /Volumes/Vagrant/Vagrant.pkg -target /
        rm Vagrant.dmg
    fi
    VAGRANT_EXE="Vagrant"
fi

echo -e "\nVagrant installed correctly.\n"

if [ -z "$( ${VAGRANT_EXE} gem list | grep ansible )" ]; then
    ${VAGRANT_EXE} gem install vagrant-ansible
    wait $!

    # TODO issue with vagrant-ansible in multi-vm environment
    if [[ "${OS}" == *Linux* ]]
    then
        sed -i 's/#{forward}/#{ssh.port}/g' ~/.vagrant.d/gems/gems/vagrant-ansible-0.0.5/lib/vagrant-ansible/provisioner.rb
    elif [[ "${OS}" == *Darwin* ]]
    then
        sed -i '' 's/#{forward}/#{ssh.port}/g' ~/.vagrant.d/gems/gems/vagrant-ansible-0.0.5/lib/vagrant-ansible/provisioner.rb
    fi

    echo -e "\nVagrant-Ansible module installed correctly.\n"
fi

${VAGRANT_EXE} gem update

DEFAULT_BOX_NAME="precise_base"
if [ -z "$( vagrant box list | grep ${DEFAULT_BOX_NAME} )" ]; then
    read -p "You don't have the base Ubuntu Precise (64 bit) box, do you want to add it? [y/N] " -e answer

    if [ "${answer}" = "y" ]; then
        # http://www.vagrantbox.es/
        ${VAGRANT_EXE} box add ${DEFAULT_BOX_NAME} http://files.vagrantup.com/precise64.box
    fi
fi