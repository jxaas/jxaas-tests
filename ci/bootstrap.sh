#!/bin/bash

set -ex

. common

get_keypair
get_instancetype


get_instance
wait_running ${INSTANCEID}

IP=$(get_publicip ${INSTANCEID})

wait_ssh ${SSH_USER} ${IP}
ssh ${SSH_USER}@${IP} sudo apt-get install --yes rsync

rsync -avz ${BASEDIR}/ ${SSH_USER}@${IP}:test

ssh ${SSH_USER}@${IP} sudo test/ci/install.sh
ssh ${SSH_USER}@${IP} test/ci/compile.sh



echo IP=${IP}
