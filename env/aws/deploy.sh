#!/bin/bash

function timer() {
    if [[ $# -eq 0 ]]; then
        echo $(date '+%s')
    else
        local stime=$1
        etime=$(date '+%s')

        if [[ -z "$stime" ]]; then stime=$etime; fi

        dt=$((etime - stime))
        ds=$((dt % 60))
        dm=$(((dt / 60) % 60))
        dh=$((dt / 3600))
        printf '%d:%02d:%02d' $dh $dm $ds
    fi
}


AWS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "Current dir: ${AWS_DIR} \n"

if [ -z "$AWS_ACCESS_KEY" ] && [ -z "$AWS_SECRET_KEY" ]
then
    echo "Loading AWS profile ..."
    if [ -e ${AWS_DIR}/aws_profile.sh ]
    then
        source ${AWS_DIR}/aws_profile.sh
    else
        echo "AWS profile not found!"
        exit 1
    fi
fi

if [ -z $1 ]; then
    read -p "Enter an instance-id if you have it already (leave it blank otherwise): " -e INSTANCE_ID
else
    INSTANCE_ID=$1
fi

# http://cloud-images.ubuntu.com/locator/ec2/
# Ubuntu precise 12.04 LTS eu-west-1 amd64 released 2013-04-11.1
INSTANCE_STORE_AMI="ami-fc7a6e88"
EBS_AMI="ami-ce7b6fba"

# default on EBS
USE_INSTANCE_STORE="N"

if [ -z "${INSTANCE_ID}" ]; then
    read -p "Which instance type you want? " -e INSTANCE_TYPE
    read -p "Choose one of those keypairs [$( ec2-describe-keypairs | cut -f 2 | sed ':a;N;$!ba;s/\n/  /g' )] : " -e KEY_PAIR
    read -p "Choose one of those security groups [$( ec2-describe-group | grep GROUP | cut -f 4 | sed ':a;N;$!ba;s/\n/  /g' )] : " -e SECURITY_GROUP
    read -p "Do you want to use and instance store? [y/N] " -e USE_INSTANCE_STORE

    if [ "${USE_INSTANCE_STORE}" = "y" ]; then
        AMI=${INSTANCE_STORE_AMI}
    else
        AMI=${EBS_AMI}
    fi

    INSTANCE_ID=$(ec2-run-instances ${AMI} -n 1 -t ${INSTANCE_TYPE} -k ${KEY_PAIR} -g ${SECURITY_GROUP} | awk '/INSTANCE/{print $2}')
    echo "Created instance: ${INSTANCE_ID}"

    read -p "Please enter a tag name to associate to the instance: " -e TAG_NAME
    if [ -n "${TAG_NAME}" ]; then
        ec2-create-tags ${INSTANCE_ID} -t Name=${TAG_NAME}
    fi
else
    USE_INSTANCE_STORE_TEXT=$(ec2-describe-instances ${INSTANCE_ID} | grep 'INSTANCE' | cut  -f 21)
    if [ "${USE_INSTANCE_STORE_TEXT}" = "instance-store" ]; then
        echo "Uses instance store"
        USE_INSTANCE_STORE="y"
    fi

    TAG_NAME=$(ec2-describe-tags | grep ${INSTANCE_ID} | cut -f 5)
    echo "Tag name: ${TAG_NAME}"
fi

PUBLIC_IP=$(ec2-describe-instances ${INSTANCE_ID} | grep 'INSTANCE' | cut  -f 17)
echo "Public IP: ${PUBLIC_IP}"

echo ""

ANSIBLE_CMD=""
OS=$(uname -s)
if [[ "${OS}" == *Linux* ]]
then
    export ANSIBLE_CMD=/usr/bin/ansible-playbook
elif [[ "${OS}" == *Darwin* ]]
then
    export ANSIBLE_CMD=/usr/local/bin/ansible-playbook
fi

read -p "Enter the playbook that you want to run (leave it blank otherwise): " -e PLAYBOOK
if [ -n "${PLAYBOOK}" ]; then
    PLAYBOOK_FILE=${PLAYBOOK}
    if [ ! -e ${PLAYBOOK_FILE} ]; then
        echo "Playbook not found!"
        exit 1
    fi

    # TODO state running doesn't mean you can connect, should keep connecting with a timeout
    # wait till the instance is in state running
    IS_RUNNING=$(ec2-describe-instances ${INSTANCE_ID} |grep running|awk '{print $6}')
    while [ "${IS_RUNNING}" != "running" ]
    do
        echo "Waiting ${INSTANCE_ID} to be in state 'running' ..."
        IS_RUNNING=$(ec2-describe-instances ${INSTANCE_ID} |grep running|awk '{print $6}')
        sleep 20
    done

    # grab host name from ansible playbook file
    HOST=$(grep hosts ${PLAYBOOK_FILE} | cut -d':' -f 2 | tr -d ' ')

    # create a inventory file for ansible in /tmp
    INVENTORY=/tmp/host_${PUBLIC_IP}
    echo -e "[${HOST}]\n${PUBLIC_IP}\n" > ${INVENTORY}

    tmr=$(timer)

    echo -e "\nPlaying ${PLAYBOOK} on ${PUBLIC_IP} ..."
    ${ANSIBLE_CMD} -i ${INVENTORY} ${PLAYBOOK_FILE} -u ubuntu --extra-vars="user=ubuntu prudentia_dir=/Users/tiziano/Development/Work-My/prudentia" -vv &
    #  --extra-vars="user=ubuntu tags=conf" --tags='conf' -vv &
    wait ${!}

    printf 'Playing time: %s\n' $(timer ${tmr})
fi

echo ""

read -p "Do you want to snapshot the instance? [y/N] " -e SNAPSHOT_IT
if [ "${SNAPSHOT_IT}" = "y" ]; then
    read -p "Please give it a name: " -e NAME
    TODAY=$(date +"%d%m%Y-%H%M")
    IMAGE_NAME=${NAME}_${TODAY}

    if [ "${USE_INSTANCE_STORE}" = "y" ]; then
        # create a inventory file for ansible in /tmp
        AWS_INVENTORY=/tmp/host_${PUBLIC_IP}_aws
        echo -e "[target_snapshot]\n${PUBLIC_IP}\n" > ${AWS_INVENTORY}

        /usr/bin/ansible-playbook -i ${AWS_INVENTORY} ./tasks/snapshot-on-s3.yml -u ubuntu --extra-vars="bucket=${TAG_NAME} image_name=${IMAGE_NAME}" -vv &
        wait ${!}
    else
        ec2-stop-instances ${INSTANCE_ID}

        # wait till the instance is in state stopped
        STOPPED_INSTANCE=$(ec2-describe-instances ${INSTANCE_ID} |grep stopped|awk '{print $4}')
        while [ "${STOPPED_INSTANCE}" != "stopped" ]
        do
            echo "Waiting ${INSTANCE_ID} to be in state 'stopped' ..."
            STOPPED_INSTANCE=$(ec2-describe-instances ${INSTANCE_ID} |grep stopped|awk '{print $4}')
            sleep 20
        done

        ec2-create-image -n "${IMAGE_NAME}" ${INSTANCE_ID}
    fi

    # TODO wait till the snapshot/image is ready
fi

echo ""

read -p "Do you want to terminate the instance? [y/N] " -e CLEAN_IT
if [ "${CLEAN_IT}" = "y" ]; then
    ec2-terminate-instances ${INSTANCE_ID}
fi