#!/bin/bash

AWS_PROFILE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR=/opt/aws

OS=$(uname -s)
if [[ "${OS}" == *Linux* ]]
then
    export JAVA_HOME=/usr/lib/jvm/java-7-oracle/
elif [[ "${OS}" == *Darwin* ]]
then
    export JAVA_HOME=/System/Library/Frameworks/JavaVM.framework/Home/
fi

export AWS_CREDENTIAL_FILE=${AWS_PROFILE_DIR}/auth/credential
export AWS_AUTO_SCALING_HOME=$BASE_DIR/`basename ${BASE_DIR}/AutoScaling*`
export AWS_CLOUDWATCH_HOME=$BASE_DIR/`basename ${BASE_DIR}/CloudWatch*`
export AWS_RDS_HOME=$BASE_DIR/`basename ${BASE_DIR}/RDSCli*`
export AWS_IAM_HOME=$BASE_DIR/`basename ${BASE_DIR}/IAMCli*`
export EC2_REGION=eu-west-1

AWS_ACCESS_KEY=`grep AWSAccessKeyId ${AWS_CREDENTIAL_FILE} | cut -d '=' -f2`
AWS_SECRET_KEY=`grep AWSSecretKey ${AWS_CREDENTIAL_FILE} | cut -d '=' -f2`
export AWS_ACCESS_KEY
export AWS_SECRET_KEY
export EC2_AMITOOL_HOME=$BASE_DIR/`basename ${BASE_DIR}/ec2-ami-tools*`
export EC2_HOME=$BASE_DIR/`basename ${BASE_DIR}/ec2-api-tools*`
export EC2_URL=ec2.eu-west-1.amazonaws.com
export S3_CMD=$BASE_DIR/`basename ${BASE_DIR}/s3cmd*`

export PATH=$PATH:${AWS_AUTO_SCALING_HOME}/bin:${AWS_CLOUDWATCH_HOME}/bin:${AWS_RDS_HOME}/bin:${EC2_HOME}/bin:${AWS_IAM_HOME}/bin:${EC2_AMITOOL_HOME}/bin:${S3_CMD}
