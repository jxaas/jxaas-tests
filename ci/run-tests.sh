#!/bin/bash

set -e
set -x

juju generate-config
juju switch local
juju bootstrap
juju status

