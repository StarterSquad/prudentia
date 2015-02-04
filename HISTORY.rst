Release History
---------------

0.7 (2015-02-03)
++++++++++++++++

**Bugfixes**

- Fixes stop recreation DigitalOcean droplet when user reconfigures box without destroying it.

**Improvements**

- Makes provision accept multiple tags.
- Suggests tags during auto-completion filtering out the ones that have already been selected.
- Enables symlinks feature in VirtualBox.
- Registers an existing DigitalOcean droplet using the id.

**Misc**

- Adds History and Authors.

0.6 (2015-01-07)
++++++++++++++++

**Bugfixes**

- Fix creation user dir.

**Documentation**

- Described properly box operations.

0.5 (2015-01-07)
++++++++++++++++

**Bugfixes**

- Fixes error when running an action against a non existing box.

**Improvements**

- Drops execution of the script to install Vagrant.
- Publishes Prudentia on PyPI.
- Adds Python 2.6 to Travis build options.
- Refactor nodejs bundled task to use nvm (#11).
- Hides password when user enters it during box definition (#10).
- Executes extra checks when user inputs file paths (#8).
- Updates Readme doc.
- Updates and cleans up examples.
- Creates Local Provider.
- Adds bundled tasks: fontforge, opencv, noop, postgres, sbt, ssl-self-certificate, timezone.

**Behavioral Changes**

- Restructures python packages.
- Moves Prudentia environments directory under user home.
- Avoids check and install Vagrant package when using Vagrant Provider.

**Misc**

- Adds license.

0.4 (2014-02-09)
++++++++++++++++

**Bugfixes**

- Fixes several issue with Vagrantfile.
- Fixes provisioning non existing box.

**Improvements**

- Adds set/unset action used to set an environment variable.
- Sets default for yes/no question if no answer was given.
- Integrates Travis CI.
- Suggest box name based on playbook hosts name.
- Exit with error code 1 if one off cmd provisioning fails.
- Add example box.

0.3 (2014-01-16)
++++++++++++++++

**Improvements**

- Creates DigitalOcean Provider and Ssh Provider.
- Introduces Environment and Box entities.
- Adds bundled tasks: chrome, protractor, mongodb, python.
- Introduces bash utility.

0.2 (2013-10-15)
++++++++++++++++

**Bugfixes**

- Fixes provision without tags.

**Improvements**

- Loads box playbook tags and use in action argument suggestion.

0.1 (2013-09-17)
++++++++++++++++

**Beginning**

- Adds script to install Vagrant and Ansible.
- Creates Vagrant Provider with basic commands: add, remove, provision, phoenix, restart, destroy.
- Adds bundled tasks: common-setup, git, github, java7, jenkins, mercurial, mysql, nginx, nodejs, redis, ruby, sbt, ssh-key, tor.
- Provides tags support for provision action.
- Adds shared folder to Vagrant box definition.
