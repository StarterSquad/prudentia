=========
Prudentia
=========
|status| |health| |coverage| |version| |license|

Prudentia is a Continuous Deployment toolkit written in Python.

*******
Mission
*******
Prudentia's mission is to help you to get production (or any other environment) ready in minutes instead of days, by 
streamlining all the actions needed to provision your architectural components.

********
Features
********
Prudentia uses Ansible_ as its main automation system, so it easily understands Ansible playbooks.
A playbook is one of the components needed to define a Prudentia Box.

Prudentia currently offers:

* a CLI_ (supporting auto-completion) used to interactively define Boxes and run operations on them
* Here-Document_ format to script Prudentia environments
* provisioning of an existing server that can be accessed trough SSH
* management of the lifecycle of a Box that has been created through Prudentia
* creating Boxes using one of these providers:

  * Vagrant
  * DigitalOcean
  * local
  * ssh

Currently, all features work with Python 2.6+ and 3.2+.

*************
Prerequisites
*************
You need at minimum:

* Python 2.6 and pip

To install on a Linux distribution you need:

* libffi-dev
* libssl-dev
* python-dev

************
Installation
************
To install Prudentia:

.. code-block:: bash

    $ pip install prudentia


It may be necessary to have root privileges, in which case:

.. code-block:: bash

    $ sudo pip install prudentia


To uninstall:

.. code-block:: bash

    $ pip uninstall prudentia

**************
Box operations
**************
A Simple provider (e.g. Local provider or SSH provider) have the following operations available:

* *register*: adds a new box definition to the registry
* *unregister*: removes a box from the registry
* *reconfigure*: changes the definition of an existing box
* *list*: lists all boxes in the registry
* *set*: defines or override an Ansible extra variable
* *unset*: removes an Ansible extra variable
* *vars*: loads Ansible extra variables from an external .yml or .json file (overriding existing ones)
* *envset*: sets the value of an environment variable
* *provision*: runs tasks defined in the playbook associated with a box
* *decrypt*: sets the password used to decrypt Ansible vault files
* *verbose*: sets Ansible verbosity, using a value between 0 and 4
* *facts*: shows useful information about the box and accepts optional parameter to filter properties

A Factory provider (e.g. Vagrant provider or DigitalOcean provider) extend simple provider and adds the ability
to change the box life cycle:

* *create*: instantiate a new instance based of the box definition
* *restart*: reloads the instance
* *stop*: shuts down the instance
* *destroy*: kill the instance
* *phoenix*: shortcut for stop -> destroy -> create -> start -> provision (citing `phoenix server`_ Martin Fowler's article)
* *status*: returns the status of the instance

*****
Usage
*****

CLI
===
We'll show a usage example of the SSH provider bundled with Prudentia.

**Make sure you have a server that you can ssh into**.

.. code-block:: bash

    $ prudentia ssh

Check what the Ssh provider can do using tab completion::

    (Prudentia > Ssh)
    decrypt      EOF          help         list         provision    reconfigure  register     set          unregister   unset        vars

Let's start registering a new box::

    (Prudentia > Ssh) register
    Specify the playbook path:

Now Prudentia is asking for a playbook path, and this is actually an Ansible playbook.

You can use one of the samples that you can find in the `examples/boxes` directory.
For instance, the `tasks.yml` that will run some Ansible tasks that we've defined (those tasks are not that meaningful,
but they are used as a sanity check in our tests).

So let's continue using the `tasks.yml`::

    (Prudentia > Ssh) register
    Specify the playbook path: /path/to/prudentia/examples/boxes/tasks.yml
    Specify the box name [default: tasks-host]:
    Specify the instance address or inventory: ip.of.your.server
    Specify the remote user [default: _your_user_]: 
    Specify the password for the remote user [default: ssh key]:

    Box example -> (/path/to/prudentia/examples/boxes/tasks.yml, tasks-host, ip.of.your.server, _your_user_) added.

You will notice that, for some questions, Prudentia gives suggested answer within `[ ]`. For instance, the suggested
Box name is `tasks-host`. If you like the suggestion, just press enter to choose it.

So far we've registered a Prudentia Box that can be used to play around. If you want to check the definition again::

    (Prudentia > Ssh) list
    example -> (/path/to/prudentia/examples/boxes/tasks.yml, tasks-host, ip.of.your.server, _your_user_)
    
Now that we have double-checked that our Box has been registered, we can provision it::

    (Prudentia > Ssh) provision example
    
    PLAY [tasks-host] ***************************************************************
    
    GATHERING FACTS ***************************************************************
    ok: [tasks-host]
    
    TASK: [Uname] *****************************************************************
    changed: [tasks-host] => {"changed": true, "cmd": ["uname", "-a"], "delta": "0:00:00.005527", "end": "2015-01-01 19:13:58.633534", "rc": 0, "start": "2015-01-01 19:13:58.628007", "stderr": "", "stdout": "Darwin tiziano-air 12.5.0 Darwin Kernel Version 12.5.0: Sun Sep 29 13:33:47 PDT 2013; root:xnu-2050.48.12~1/RELEASE_X86_64 x86_64", "warnings": []}

    TASK: [Shuffle] *************************************************************** 
    ok: [tasks-host] => (item=2) => {
        "item": 2, 
        "msg": "2"
    }
    ok: [tasks-host] => (item=4) => {
        "item": 4, 
        "msg": "4"
    }
    ok: [tasks-host] => (item=1) => {
        "item": 1, 
        "msg": "1"
    }
    ok: [tasks-host] => (item=5) => {
        "item": 5, 
        "msg": "5"
    }
    ok: [tasks-host] => (item=3) => {
        "item": 3, 
        "msg": "3"
    }
    
    TASK: [No operation] ********************************************************** 
    ok: [tasks-host] => {
        "msg": "Task noop executed."
    }

    PLAY RECAP ********************************************************************
    tasks-host                  : ok=4    changed=1    unreachable=0    failed=0
    
    Play run took 0 minutes

Now Prudentia has done the reasonable uninteresting uname, shuffling a list of ints and noop tasks on the remote machine.

Here-Document
=============
The same sequence of operations can be executed using the `Here-Document`_ input:

.. code-block:: bash

    $ prudentia ssh <<EOF
    register
    /path/to/prudentia/examples/boxes/tasks.yml
    tasks-host
    ip.of.your.server
    _your_user_
    
    provision tasks-host

    unregister tasks-host
    EOF

Command arguments
=================
If you want to run few commands that don't require specific inputs then there is an option that is quicker than using
the CLI or the Here-Document.

Let's for example have a look at an example right away:

.. code-block:: bash

    $ prudentia ssh 'decrypt' 'vars ./encrypted-vars.yml' 'provision box-name'


After running this command we will be asked to input the Ansible vault password, after that an encrypted file containing
variables will be loaded (we assume that the provided password can correctly decrypt the file) and eventually provision
an existing registered ssh box.

***********
Development
***********

You can debug and extend Prudentia (or run the latest develop) simply by sym-linking a bash script that we provided:

.. code-block:: bash

    $ ln -s `pwd`/prudentia.sh /usr/local/bin/prudentia-dev
    $ prudentia-dev

In this way you can have both versions, stable and development, running on your system. The development version will
run in a python virtual environment without interfering with the dependencies of the stable version. The only
information that will be shared are the boxes definition.

****
More
****

Posts
=====
Here you can find a guide on how to use Prudentia to `provision a Digital Ocean droplet`_ with the StarterSquad website on it.

Another important source of information is `Iwein's post`_ that gives you an idea of what Continuous Delivery is, and
where Prudentia fits into the flow.

Questions & Contributions
=========================
Questions, Contributions and Feedback are more than welcome.

You can checkout planned new features on the `Trello Board`_. Feel free to create feature requests on github issues.

You can e-mail me at:

``tiziano@startersquad.com``


.. Links

.. _Ansible: https://github.com/ansible/ansible
.. _CLI: http://en.wikipedia.org/wiki/Command-line_interface
.. _Here-Document: http://en.wikipedia.org/wiki/Here_document#Unix_shells
.. _phoenix server: http://martinfowler.com/bliki/PhoenixServer.html
.. _provision a Digital Ocean droplet: http://www.startersquad.com/blog/simple-deployments-with-prudentia/
.. _Iwein's post: http://www.startersquad.com/blog/getting-ready-for-continuous-delivery/

.. _Trello board: https://trello.com/b/CyRrVZom

.. |status| image:: https://travis-ci.org/StarterSquad/prudentia.png?branch=develop
   :target: https://travis-ci.org/StarterSquad/prudentia
   :alt: Status
.. |health| image:: https://landscape.io/github/StarterSquad/prudentia/develop/landscape.svg?style=flat
   :target: https://landscape.io/github/StarterSquad/prudentia/develop
   :alt: Health
.. |coverage| image:: http://codecov.io/github/StarterSquad/prudentia/coverage.svg?branch=develop
   :target: http://codecov.io/github/StarterSquad/prudentia?branch=develop
   :alt: Coverage
.. |version| image:: https://badge.fury.io/py/prudentia.svg
   :target: http://badge.fury.io/py/prudentia
   :alt: Version
.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://pypi.python.org/pypi/prudentia
   :alt: License
