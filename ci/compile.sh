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

if [[ -d ~/jxaas/etcd ]]; then
  cd ~/jxaas
  curl -L  https://github.com/coreos/etcd/releases/download/v2.0.0-rc.1/etcd-v2.0.0-rc.1-linux-amd64.tar.gz | tar xzvf -
  mv etcd-v2.0.0-rc.1-linux-amd64 etcd
fi

