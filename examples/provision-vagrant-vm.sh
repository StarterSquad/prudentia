#!/bin/bash

prudentia vagrant <<-EOF
  register
  ${PWD}/boxes/tasks.yml
  mybox
  10.0.0.17
  1

  provision mybox
EOF
