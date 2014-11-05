#!/bin/bash

set -e
set -x

if [[ ! $(which juju) ]]; then
  sudo apt-get update
  sudo apt-get install --yes juju juju-local
fi

pkill -KILL jxaasd || true

if [[ -d ~/.juju ]]; then
  sudo juju destroy-environment --yes --force local
  rm -rf ~/.juju
fi

juju generate-config
juju switch local
juju bootstrap
juju status

if [[ ! -d /etc/squid-deb-proxy/ ]]; then
  sudo apt-get install --yes squid-deb-proxy
fi
juju set-env apt-http-proxy=http://10.0.3.1:8000

if screen -list | awk '{print $1}' | grep -q "juju$"; then
  echo "screen juju already exists" 
else
  screen -d -m -S juju
fi
screen -S juju -X screen /bin/bash -c "cd ~/jxaas/.build; bin/jxaasd"
