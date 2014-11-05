#!/bin/bash

set -e
set -x

sudo apt-get install --yes golang
# go get requires some version control clients:
sudo apt-get install --yes git bzr mercurial

if [[ -d ~/jxaas ]]; then
  cd ~/jxaas
  git pull
else
cd ~
  git clone https://github.com/jxaas/jxaas.git ~/jxaas
  cd ~/jxaas
fi
./build.sh

sudo apt-get install --yes python-pip
#pip install requests
#pip install git+https://github.com/jxaas/charm-toolkit.git
#sudo apt-get install --yes git
sudo pip install git+https://github.com/jxaas/python-client.git
sudo pip install git+https://github.com/jxaas/cli.git
