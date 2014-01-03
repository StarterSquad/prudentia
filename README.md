# Overview

Prudentia is a Continuous Deployment toolkit. It contains a collection of providers and tasks that allow you to deploy any application to most popular virtual environments out of the box. Of course you can extend the toolkit with providers and tasks of your own.

#Getting started
Getting started with Prudentia is super easy.

## Prerequisites

**Make sure you have python and virtualenv installed**:

    $ python --version
    Python 2.7.2

    $ virtualenv --version
    1.10

Later versions should work too. You know how that is.

Also **make sure you have a box that you can ssh onto**.

Check out Prudentia:

    $ git clone git@github.com:StarterSquad/prudentia.git
    $ cd prudentia

## Start the CLI

    $ ./prudentia.sh ssh

This will pull in some python dependencies the first time. After that you can see what prudentia can do using tab completion:

    (Prudentia > Ssh)
    EOF          help         list         provision    reconfigure  register     unregister
    (Prudentia > Ssh) register
    Specify the playbook path:

Now register is asking for a playbook. This is actually an [Ansible][1] playbook that could look like this:

    ---
    - hosts: example

      tasks:
      - name: uname
        command: uname -a
        
Save it under `/tmp/temp.yml`. Now let's continue:

    $ ./prudentia.sh ssh
    (Prudentia > Ssh) register
    Specify the playbook path: /tmp/temp.yml
    Specify the address of the instance: localhost
    Specify the remote user [default: iwein]:
    Specify the password for the remote user [default: ssh key]:

    Box example -> (/tmp/temp.yml, localhost, iwein) added.

Good so now I have a box. In this case it's localhost, so that is not very interesting, but at least we can play around. Let's provision it:

    (Prudentia > Ssh) provision example
    PLAY [example] ***************************************************************
    
    GATHERING FACTS ***************************************************************
    ok: [localhost]
    
    TASK: [uname] *****************************************************************
    changed: [localhost] => {"changed": true, "cmd": ["uname", "-a"], "delta": "0:00:00.003120", "end": "2013-12-23 20:14:55.214061", "rc": 0, "start": "2013-12-23 20:14:55.210941", "stderr": "", "stdout": "Darwin lymnaea.fritz.box 12.5.0 Darwin Kernel Version 12.5.0: Sun Sep 29 13:33:47 PDT 2013; root:xnu-2050.48.12~1/RELEASE_X86_64 x86_64"}
    
    PLAY RECAP ********************************************************************
    localhost                  : ok=2    changed=1    unreachable=0    failed=0
    
    Provisioning took 0 minutes

Now Prudentia has done the reasonable uninteresting uname task for me on the 'remote' system.

## A more advanced example
TODO

## Philosophy

Prudentia (often associated with wisdom) is the ability to govern and discipline oneself by the use of reason.

Operationally talking when deploying and orchestrating systems, prudence is used in the sense of reluctance to take risks.

Our CLI learns (knowledge) and reasons (judge) about components or services within a specific architecture.

[1]: https://github.com/ansible/ansible "Ansible"
