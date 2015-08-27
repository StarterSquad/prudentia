#!/usr/bin/env python

####################################################################################
###
### Get EC2 instances inventory under ELB
### =====================================
###
### Generates inventory that Ansible can understand by making API request to
### AWS EC2 using the Boto library.
###
### NOTE: This script assumes Ansible is being executed where the environment
### variables needed for Boto have already been set:
###     export AWS_ACCESS_KEY_ID='ABC123'
###     export AWS_SECRET_ACCESS_KEY='abc123'
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

### Functions
# Check env vars
def check_vars():
  if None in [os.environ.get('AWS_ACCESS_KEY_ID'), os.environ.get('AWS_SECRET_ACCESS_KEY')]:
    boto_path = ['/etc/boto.cfg', '~/.boto', '~/.aws/credentials']
    boto_config_found = list(p for p in boto_path if os.path.isfile(os.path.expanduser(p)))
    if len(boto_config_found) <= 0:
      error("Cannot find AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY variables or read credentials from %s" % boto_path, "checking the envronment")

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
    # Walk through instance info
    except boto.exception.BotoServerError as e:
      error("%s (%s)" % (e.message, e.error_code) , "fetching ELB instance properties")
    for i in ec2_instance:
      # Q: shall we check if ec2_instance and i.id match?
      # Append instance info to the list
      #info.append([i.id, i.ip_address, i.dns_name])
      info.append(i.ip_address)
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
  elb_result = {}
  # Get ELB info
  try:
    elb = elb_conn.get_all_load_balancers(elb_name)
    for i in elb:
      # Add list as a value to ELB name
      elb_result[i.name] = get_instance_info(i.instances)
  except boto.exception.BotoServerError as e:
    error("%s (%s)" % (e.message, e.error_code) , "fetching instances under ELB")
  # Return here
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

# Check if env vars are in place
check_vars()

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
if options.list:
  elb_list = get_elb_list()
  print json.dumps(elb_list, indent=4)
  sys.exit(0)

# Get instance details under particular ELB
elif options.elb:
  elb_info = get_elb_info(options.elb)
  print json.dumps(elb_info, indent=4)
  sys.exit(0)

### EOF
