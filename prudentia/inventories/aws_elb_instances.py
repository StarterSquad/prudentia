#!/usr/bin/env python

####################################################################################
###
### Get EC2 instances inventory under ELB
### =====================================
###
### Generates inventory that Ansible can understand by making API request to
### AWS EC2 using the Boto library.
###
####################################################################################

import sys
import os
from boto import boto
from optparse import OptionParser
try:
    import json
except:
    import simplejson as json


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
ELB_NAME = os.getenv('ELB_NAME', '')
HOSTS_NAME = os.getenv('HOSTS_NAME', '')


# Log an error to stderr and quit
def error(err_msg, err_operation=None):
    if err_operation:
        err_msg = 'Error {err_operation}: "{err_msg}"\n'.format(err_msg=err_msg, err_operation=err_operation)
    else:
        err_msg = 'Error: {err_msg}\n'.format(err_msg=err_msg)
    sys.stderr.write(err_msg)
    sys.exit(1)

# Get instance info
def get_instance_info(instances):
    # Init ELB instance list
    info = []
    # Walk through the instance list
    for instance in instances:
        # Get instance info
        try:
            ec2_instance = ec2_conn.get_only_instances(instance.id)
            for i in ec2_instance:
                # Append instance info to the list
                info.append(i.ip_address)
        # Walk through instance info
        except boto.exception.BotoServerError as e:
            error("%s (%s)" % (e.message, e.error_code) , "fetching ELB instance properties")
    # Return info
    return info

# Get full instance list under each ELB
def get_elb_list():
    # Init function return dictionary
    elb_result = {}
    # Walk through the ELB list
    try:
        for elb in elb_conn.get_all_load_balancers():
            # Add list as a value to ELB name
            elb_result[elb.name] = get_instance_info(elb.instances)
    except boto.exception.BotoServerError as e:
        error("%s (%s)" % (e.message, e.error_code) , "fetching ELB list")
    # Return here
    return elb_result

# Get full instance list under particular ELB
def get_elb_info(elb_name):
    # Init function return dictionary
    elb_result = []
    # Get ELB info
    try:
        elb = elb_conn.get_all_load_balancers(elb_name)
        for i in elb:
            # Add list as a value to ELB name
            elb_result = get_instance_info(i.instances)
    except boto.exception.BotoServerError as e:
        error("%s (%s)" % (e.message, e.error_code) , "fetching instances under ELB")

    return elb_result

### Start the ball
# Parse the options
parser = OptionParser(usage="%prog [options] --list | --host <AWS ELB>")
parser.add_option('--list', default=False, dest="list", action="store_true", help="Produce a JSON consumable grouping of instances under ELB")
parser.add_option('--host', default=None, dest="elb", help="Generate additional host specific details for given host for Ansible")
(options, args) = parser.parse_args()

# Check if we have options and print help
if not options.list and not options.elb:
    parser.print_help()
    sys.exit(0)


# Try to connect to AWS
try:
    elb_conn = boto.connect_elb()
except boto.exception.BotoServerError as e:
    error("%s (%s)" % (e.message, e.error_code) , "connecting to ELB")

try:
    ec2_conn = boto.connect_ec2()
except boto.exception.BotoServerError as e:
    error("%s (%s)" % (e.message, e.error_code) , "connecting to EC2")

# Get instance details under all ELB
if ELB_NAME == '':
    if options.list:
        elb_list = get_elb_list()
        print json.dumps(elb_list)
        sys.exit(0)

    # Get instance details under particular ELB
    elif options.elb:
        elb_info = get_elb_info(options.elb)
        print json.dumps(elb_info)
        sys.exit(0)
else:
    elb_info = get_elb_info(ELB_NAME)
    elb_hosts = elb_info
    host_group = {HOSTS_NAME: {}}
    host_group[HOSTS_NAME]['hosts'] = elb_hosts
    print json.dumps(host_group)
    sys.exit(0)
