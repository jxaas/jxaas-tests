#!/bin/bash

set -e
set -x

pkill -KILL jxaasd || true

if [[ -f ~/.juju/environments.yaml ]]; then
  sudo juju destroy-environment --yes --force local
  rm -rf ~/.juju
fi

juju generate-config
juju switch local
juju bootstrap
juju status

juju set-env apt-http-proxy=http://10.0.3.1:8000

if screen -list | awk '{print $1}' | grep -q "juju$"; then
  echo "screen juju already exists" 
else
  screen -d -m -S juju
  sleep 2 # We have to wait for screen?
fi
screen -S juju -X screen /bin/bash -c "cd ~/jxaas/.build; bin/jxaasd"
