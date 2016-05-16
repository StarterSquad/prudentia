Release History
---------------

2.1 (2016-05-16)
++++++++++++++++

**Improvements**

- Replace sudo with become in bundled tasks.
- Makes phoenix operation accept tags.
- Parametrise add-sudo-user bundled task to use ssh key of the specified user.
- Addresses deprecation warning for JRE bundled task.

**Bugfixes**

- Makes sure verbose operation correctly works.

2.0 (2016-04-03)
++++++++++++++++

**Improvements**

- Upgrades to support Ansible 2.
- Sets user real name when creating sudo user using bundled task.
- Adds optional parameter root_mail_address to postfix bundled task.

**Bugfixes**

- Fixes timezone bulded task to avoid ntpdate running every minute.

1.0 (2016-02-09)
++++++++++++++++

**Improvements**

- Allows specifying version for mongodb_3 bundled task.
- Avoids dependency from Ansible constants module.
- Changes default logging level.

**Bugfixes**

- Returns valid cli completions when multiple box names with same prefix are available.

0.17.1 (2016-01-04)
+++++++++++++++++++

**Improvements**

- Introduces parametrize ntp server address for timezone bundled task.
- Removes initial warning message when creating environment.
- Disables output variables sets according to verbosity.
- Adds six as dependency.
- Provides backwards compatibility to java7 bundled task.

**Bugfixes**

- Makes verbose command resilient.
- Catch errors when parsing playbook on env loading.

0.17 (2015-12-04)
+++++++++++++++++

**Improvements**

- Adds `facts` CLI action that can be used to show information gathered from a box.
- Allows jre bundled task to provision a different java version.
- Digital-Ocean provider: prints image distribution as well when listing images.
- Digital-Ocean provider: uses image slug for default image instead of id.

**Bugfixes**

- Avoids use of getpass when inputing sensible information through heredoc.
- Digital-Ocean provider: not suggests default ubuntu image if not available within the images list.

0.16.1 (2015-11-19)
+++++++++++++++++++

**Bugfixes**

- Update apt cache after adding ubuntu repositories.
- Installs correctly prudentia when using the homonym task.

0.16 (2015-11-19)
+++++++++++++++++

**Improvements**

- Removes update-cache from all apt tasks.
- Updates to SBT 0.13.9, nvm 0.29, node 0.12.
- Revisions task and file namings.
- Enhances project readme.
- Adds bundled tasks: jre, postfix.

**Bugfixes**

- Leverages Ansible play to get proper information that will be used by the box.
- Makes sure webdriver path is found, is dependant from node and adds start at the end of the installation.

0.15.1 (2015-10-02)
+++++++++++++++++++

**Bugfixes**

- Digital Ocean: better error handling in case the target instance cannot be contacted.
- Digital Ocean: avoids misleading keys definition when registering an existing box.
- Uses correctly hostname as pattern during provisioning to instruct Ansible which instance to target.
- Adds hvac missing dependency used by Vault module and plugin.

**Improvements**

- Updates dependencies to latest version for development.

0.15 (2015-09-29)
+++++++++++++++++

**Improvements**

- Adds script that can generate dynamically an Ansible inventory based on the instances connected to an AWS ELB.
- Adds HashiCorp Vault Ansible lookup plugin.
- Adds HashiCorp File Ansible module.
- Adds bundled task: mongodb_3.
- Updates Ngnix example and improves Monit task.
- Updates to Ansible 1.9.3.

**Bugfixes**

- Changed state for UFW from 'disabled' to 'reset' to avoid old and new rules to be merged.

0.14 (2015-09-04)
+++++++++++++++++

**Improvements**

- Accepts now external inventory file, directory and script as alternative for the box address.
- Adds `envset` CLI action that can be used to define system environment variables.
- Disables Ansible verbose output and introduces `verbose` CLI action to explicit increase verbosity.
- Loads automatically vars/global.yml avoiding the need from now on to specify it in every playbook.
- Adds bundled tasks: sysdig, haproxy.

**Bugfixes**

- Fixes Digital Ocean droplet creation.

0.13 (2015-08-18)
+++++++++++++++++

**Improvements**

- Enable support for multiple base images on the Vagrant provider.
- List available base images when registering Vagrant box.
- Adds bundled tasks: vsftpd, mailhog, monit.
- Upgrades vault bundled task to 0.2
- Introduces retries mechanism when asking the user to provide a valid path.

**Bugfixes**

- Makes sure that Jinja2 templates do not ignore undefined variables and raise an error instead.

0.12 (2015-07-24)
+++++++++++++++++

**Improvements**

- Makes Nginx bundled task disable the default site.
- Shows more information about the DigitalOcean image when registering/reconfiguring a droplet.
- Allows only the newly added sudo user to not be prompted for password.
- Upgrades to Ansible 1.9.2.
- Adds bundled tasks: vault (https://vaultproject.io), fail2ban, tomcat7.
- Adds an action for the simple provider to set the password used to decrypt Ansible vault files.
- Refactors main cli to properly parse input arguments.
- Accepts list of commands as arguments.
- Introduces -v (--version) argument to print current Prudentia version.
- Adds an action for the simple provider to loads extra vars from an external .yml or .json file.
- Checks if current version is the latest released one.
- Accepts input paths relative to the directory where Prudentia was started or relative to the user home directory.
- Upgrades dopy to 0.3.6 and switches to DigitalOcean API version 2 based on API token.

**Bugfixes**

- Makes Nginx bundled task properly idempotent and reload the service at the end of the task.
- Fixes ElasticSearch init script.
- Makes sure variables value are set even if they contain spaces.
- Waits for async bash thread to finish.
- Fixes InsecurePlatformWarning when https connections are initiated.

**Misc**

- Updates Client component example.
- Moves build to new Travis container based infrastructure.
- Enables properly coverage verification and improved the coverage itself.
- Verifies support for Python 3.2+.

**Documentation**

- Adds `decrypt` action doc.
- Adds `vars` action doc.
- Extends Usage section describing the new Commands list argument.

0.11 (2015-06-19)
+++++++++++++++++

**Improvements**

- Suggests automatically latest Ubuntu 14.04 LTS 64bit image when creating DigitalOcean droplet.
- Validates setting extra variables and show existing ones when running `unset` without arguments.
- Updates examples.
- Adds bundled tasks: osquery, ufw, add sudo user, zeromq, elastic search, collectd, mongodb 2.6.
- Generalize bundled java task.
- Upgrades to a newer version of nginx using proper apt repository.
- Upgrades to SBT 0.13.8.

**Bugfixes**

- Sets correctly the user that will run the webdriver manager.

0.10 (2015-05-12)
+++++++++++++++++

**Improvements**

- Updates examples.
- Upgrade to Ansible 1.9.1.

**Bugfixes**

- Fixes buffering issue.

0.9.1 (2015-03-18)
++++++++++++++++++

**Bugfixes**

- Fixes issue if cli history file doesn't exist.

0.9 (2015-03-18)
++++++++++++++++

**Improvements**

- Enables cli history cross sessions.
- Adds bundled task for adding ssh known host.
- Adds status action for factory providers.
- Upgrade to Ansible 1.8.4.
- Improves examples.
- Increases code quality.

0.8.1 (2015-02-15)
++++++++++++++++++

**Bugfixes**

- Fixes tor bundled task.

**Improvements**

- Makes postgresql and sbt parametrized tasks.
- Improves ssh key bundled task using file module.

0.8 (2015-02-05)
++++++++++++++++

**Bugfixes**

- Fixes shared folder definition for Vagrant box.
- Includes HISTORY in python setup manifest.

0.7 (2015-02-04)
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
