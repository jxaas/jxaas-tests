#!/bin/bash

set -e
set -x


function wait_juju() {
  local i=0

  while [[ $i -lt 20 ]]; do
    if [[ $i != 0 ]]; then
      sleep 5
    fi
    failed=0
    status=$(juju status | grep started) || failed=1

    if [[ "${failed}" == "0" ]]; then
      echo "Juju is started"
      return 0
    fi

    echo "Juju not yet available.  Waiting..."
    let i=i+1
  done

  echo "Timed out waiting for Juju to start"
  return 1
}


pkill -KILL jxaasd || true

if [[ -f ~/.juju/environments.yaml ]]; then
  sudo juju destroy-environment --yes --force local
  rm -rf ~/.juju
fi

juju generate-config
juju switch local
juju bootstrap
juju status

wait_juju

juju set-env apt-http-proxy=http://10.0.3.1:8000

if screen -list | awk '{print $1}' | grep -q "juju$"; then
  echo "screen juju already exists" 
else
  screen -d -m -S juju
  sleep 2 # We have to wait for screen?
fi

LOGDIR=~/logs/

mkdir -p ${LOGDIR}

screen -S juju -X screen /bin/bash -c "cd ~/jxaas/.build; bin/jxaasd > ${LOGDIR}/jxaasd.log 2>&1"
