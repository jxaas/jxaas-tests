#!/bin/bash

set -e
set -x

sudo apt-get install --yes juju

juju generate-config
juju switch local
juju bootstrap
juju status

