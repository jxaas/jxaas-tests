#!/bin/bash

set -ex

. common

find_instance
if [[ ${INSTANCEID} != "" ]]; then
  terminate_instance ${INSTANCEID}
fi


