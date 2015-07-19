#!/bin/bash

PLAYBOOK=${PWD}/boxes/tasks.yml
BOX_NAME=mybox

function valid_ip()
{
    local ip=$1
    local stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

read -p "
This is an example Prudentia script that will create and boot a local virtual machine using the Vagrant provider.

Those steps will be executed:
 - prompt for an available internal IP
 - a new Prudentia box will be registered based on the '${PLAYBOOK}' playbook
 - the box will be provisioned
 - and eventually the box will be destroyed and unregistered

Press enter to continue.
"

read -p "Please provide an internal IP to assign to box: " -e LOCAL_IP

if ! valid_ip ${LOCAL_IP}; then
  echo -e "\nThis is not a valid IP: ${LOCAL_IP}"
  exit 1
fi

prudentia vagrant <<-EOF
  register
  ${PLAYBOOK}
  ${BOX_NAME}
  ${LOCAL_IP}
  1

  provision ${BOX_NAME}

  unregister ${BOX_NAME}
  y
EOF
