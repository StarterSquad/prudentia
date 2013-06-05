This directory contains the configuration file for Vagrant in order to test playbooks and tasks.

NOTE: Vagrant MUST to be invoked from this directory.
NOTE: The playbook and other ansible options are specified in the Vagrantfile.

## Configure test environment

Copy Vagrantfile example and configure it accordingly:

    $ cp Vagrantfile.example Vagrantfile

## Use test environment

To check which box are provided:

    $ vagrant status

To initialize a new box and re-provision it:

    $ vagrant up|reload <name>

If the box already exists:

    $ vagrant provision <name>

To get rid of the box:

    $ vagrant destroy -f <name>


In case of error or you want to debug vagrant put 'VAGRANT_LOG=<level>' before the command, e.g.:

    $ VAGRANT_LOG=INFO vagrant up <name>