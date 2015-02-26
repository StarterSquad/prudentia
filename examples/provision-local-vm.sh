#!/bin/bash

PLAYBOOK=${PWD}/boxes/tasks.yml
LOCAL_IP=10.0.0.17

read -p "
This is an example Prudentia script that will create and boot a local virtual machine using the Vagrant provider.

Those steps will be executed:
 - a new Prudentia box will be registered based on the '${PLAYBOOK}' playbook
 - the box will be provisioned
 - and eventually the box will be destroyed and unregistered

Press enter to continue.
"

prudentia vagrant <<-EOF
  register
  ${PLAYBOOK}
  mybox
  ${LOCAL_IP}
  1

  provision mybox

  unregister mybox
  y
EOF
