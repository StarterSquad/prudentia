Prudentia |build-status| |pypi-downloads|
=========================================
Prudentia is a Continuous Deployment toolkit written in Python.

Mission
-------
Prudentia's mission is to help you to get production (or any other environment) ready in minutes instead of days, through 
streamlining all the actions needed to provision your architectural components.

Features
--------
Prudentia uses Ansible_ as main automation system, so it easily understand playbooks. 
A playbook is one of the information needed to define a Prudentia Box.

Prudentia currently offers:

* A CLI_ (supporting auto-completion) used to interactively define Boxes and run operation on them
* Here-Document_ format to script Prudentia environments
* Provision existing server that can be accessed trough SSH
* Manage the lifecycle of a Box that has been created through Prudentia
* Create Boxes using one of the available providers

  * Vagrant 
  * DigitalOcean
  * Local
  * Ssh

Currently, all features work with Python 2.6 and 2.7. Work is under way to support Python 3.3+ in the same codebase.

Installation
------------
To install prudentia:

.. code-block:: bash
    
    $ pip install prudentia


It may be necessary to have root privileges, in which case:

.. code-block:: bash
    
    $ sudo pip install prudentia


To uninstall:

.. code-block:: bash
    
    $ pip uninstall prudentia

Box operations
--------------
Simple providers (e.g. LocalProvider or SshProvider) have the following operation available:

* register 
* unregister
* reconfigure
* list
* set
* unset
* provision

Factory providers (e.g. VagrantProvider or DigitalOceanProvider) extend simple providers and adds those operations:

* create
* restart
* stop
* destroy
* phoenix (shortcut for stop -> destroy -> create -> start -> provision)

Usage
-----
We'll show a usage example of the SshProvider bundled with Prudentia.

**Make sure you have a server that you can ssh onto**.

.. code-block:: bash

    $ prudentia ssh

Check what the Ssh provider can do using tab completion::

    (Prudentia > Ssh)
    EOF          help         list         provision    reconfigure  register     set          unregister   unset

Let's start registering a new box::

    (Prudentia > Ssh) register
    Specify the playbook path:

Now Prudentia is asking for a playbook path, and this is actually an Ansible playbook.

You can use one of the samples that you can find in the `examples/boxes` directory.
For instance the `tasks.yml` that will run some Ansible tasks that we've defined (those tasks are not that meaningful but 
they are used as sanity check in our tests).
        
So let's continue using the `tasks.yml`::

    (Prudentia > Ssh) register
    Specify the playbook path: /path/to/prudentia/examples/boxes/tasks.yml
    Specify the box name [default: tasks-host]:
    Specify the address of the instance: ip.of.your.server
    Specify the remote user [default: _your_user_]: 
    Specify the password for the remote user [default: ssh key]:
    
    Box example -> (/path/to/prudentia/examples/boxes/tasks.yml, tasks-host, ip.of.your.server, _your_user_) added.

You will notice for some questions Prudentia gives us a suggested answer within `[ ]`. For instance the Box name is been 
suggested as `tasks-host`, if you like the suggestion just press enter to choose it.

So far we've registered a Prudentia Box that can be used to play around. If you want to check again the definition of it::

    (Prudentia > Ssh) list
    example -> (/path/to/prudentia/examples/boxes/tasks.yml, tasks-host, ip.of.your.server, _your_user_)
    
Now that we have double checked that our Box has been registered, we can provision it::

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

Now Prudentia has done the reasonable uninteresting uname, shuffling a list of ints and noop tasks for me on the remote machine.

The same sequence of operations can be executed using the `Here-Document`_ input:

.. code-block:: bash

    $ prudentia ssh <<EOF
    register
    /path/to/prudentia/examples/boxes/tasks.yml
    tasks-host
    ip.of.your.server
    _your_user_
    
    provision tasks-host
    EOF
    
More Info
---------
Here you can find a guide on how to use Prudentia to `provision a Digital Ocean droplet`_ with the StarterSquad website on it.

Another important source of information is `Iwein's post`_ that gives you an idea of what Continuous Delivery is and where 
Prudentia fits into the flow. 


Questions & Contributions
-------------------------
Questions, Contributions and Feedback are more than welcome.

You can e-mail me at: 

``tiziano@startersquad.com``


.. Links

.. _Ansible: https://github.com/ansible/ansible
.. _CLI: http://en.wikipedia.org/wiki/Command-line_interface
.. _Here-Document: http://en.wikipedia.org/wiki/Here_document#Unix_shells

.. _provision a Digital Ocean droplet: http://www.startersquad.com/blog/simple-deployments-with-prudentia/
.. _Iwein's post: http://www.startersquad.com/blog/getting-ready-for-continuous-delivery/

.. |build-status| image:: https://travis-ci.org/StarterSquad/prudentia.png?branch=master
   :target: https://travis-ci.org/StarterSquad/prudentia
   :alt: Travis CI: Build status
.. |pypi-downloads| image:: https://pypip.in/d/prudentia/badge.png
   :target: https://pypi.python.org/pypi/prudentia
   :alt: PyPI: Package status
