Prudentia
=========
[![Build Status](https://travis-ci.org/StarterSquad/prudentia.png?branch=master)](https://travis-ci.org/StarterSquad/prudentia)

Prudentia is a Continuous Deployment toolkit that offers a command line interface to interact with.

It contains a collection of providers and tasks that allow you to deploy any application to most popular virtual
environments out of the box.

Of course you can extend the toolkit with providers and tasks of your own.

# Getting started

Getting started with Prudentia is super easy.

## Prerequisites

**Make sure you have python and virtualenv installed**:

    $ python --version
    Python 2.7.2

    $ virtualenv --version
    1.10

Later versions should work too. You know how that is.

Also **make sure you have a box that you can ssh onto**.

## Install

Check out Prudentia:

    $ git clone git@github.com:StarterSquad/prudentia.git
    $ cd prudentia

and run:

    $ ./prudentia.ssh setup

## Start the CLI and use the SSH provider

    $ prudentia ssh

This will pull in some python dependencies the first time. After that you can see what prudentia can do using tab completion:

    (Prudentia > Ssh)
    EOF          help         list         provision    reconfigure  register     set          unregister   unset
    (Prudentia > Ssh) register
    Specify the playbook path:

Now register is asking for a playbook path, and this is actually an [Ansible][1] playbook.

You can use one of the samples that you can find in the `examples/boxes` directory.
For instance the `uname.yml` that will print the operative system name of the target machine.
        
So let's continue using the `uname.yml`:

    $ prudentia ssh
    (Prudentia > Ssh) register
    Specify the playbook path: /path/to/prudentia/examples/boxes/uname.yml
    Specify the box name [default: example-host]: example
    Specify the address of the instance: localhost
    Specify the remote user [default: tiziano]:
    Specify the password for the remote user [default: ssh key]:

    Box example -> (/path/to/prudentia/examples/boxes/uname.yml, example-host, localhost, tiziano) added.

Good so now I have a box. In this case it's localhost, so that is not very interesting, but at least we can play around. Let's provision it:

    (Prudentia > Ssh) provision example

    PLAY [example-host] ***************************************************************
    
    GATHERING FACTS ***************************************************************
    ok: [localhost]
    
    TASK: [uname] *****************************************************************
    changed: [localhost] => {"changed": true, "cmd": ["uname", "-a"], "delta": "0:00:00.003120", "end": "2013-12-23 20:14:55.214061", "rc": 0, "start": "2013-12-23 20:14:55.210941", "stderr": "", "stdout": "Darwin lymnaea.fritz.box 12.5.0 Darwin Kernel Version 12.5.0: Sun Sep 29 13:33:47 PDT 2013; root:xnu-2050.48.12~1/RELEASE_X86_64 x86_64"}
    
    PLAY RECAP ********************************************************************
    localhost                  : ok=2    changed=1    unreachable=0    failed=0
    
    Play run took 0 minutes

Now Prudentia has done the reasonable uninteresting uname task for me on the 'remote' machine.

## What's next

This is the easiest example I could come up with to show you the use of the SSH providers bundled in Prudentia.

Right now there are other two providers way more powerful: `vagrant` and `digital-ocean`.
Those providers are more powerful because they don't only allow you to provision the target instance but they can change
its life cycle, so that you could restart it, destroy it or phoenix it.

Philosophy
==========

Prudentia (often associated with wisdom) is the ability to govern and discipline oneself by the use of reason.

Operationally talking when deploying and orchestrating systems, prudence is used in the sense of reluctance to take risks.

Our CLI learns (knowledge) and reasons (judge) about components or services within a specific architecture.

[1]: https://github.com/ansible/ansible "Ansible"
