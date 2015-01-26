#!/bin/bash

set -e
set -x

if [[ -d ~/jxaas/jxaas ]]; then
  cd ~/jxaas/jxaas
  git pull
else
  cd ~
  git clone https://github.com/jxaas/jxaas.git ~/jxaas
  cd ~/jxaas/jxaas
fi
./build.sh

sudo pip install git+https://github.com/jxaas/python-client.git
sudo pip install git+https://github.com/jxaas/cli.git

