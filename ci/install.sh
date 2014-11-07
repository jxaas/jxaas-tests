#!/bin/bash

set -e
set -x

sudo apt-get update

sudo apt-get install --yes golang
# go get requires some version control clients:
sudo apt-get install --yes git bzr mercurial

sudo apt-get install --yes python-pip

# For tests
sudo apt-get install --yes python-mysqldb

#Install LXC
mkdir -p /mnt/var/lib/lxc
if [[ ! -h /var/lib/lxc ]]; then
  ln -s /mnt/var/lib/lxc /var/lib/
fi
chown root:root /mnt/var/lib/lxc
if [[ ! $(which juju) ]]; then
  sudo apt-get update
  sudo apt-get install --yes juju juju-local
fi


# To speed up lxc
mkdir -p /mnt/var/cache/squid-deb-proxy
if [[ ! -h /var/cache/squid-deb-proxy ]]; then
  ln -s /mnt/var/cache/squid-deb-proxy/ /var/cache/
fi
chown proxy:proxy /mnt/var/cache/squid-deb-proxy
if [[ ! -d /etc/squid-deb-proxy/ ]]; then
  sudo apt-get install --yes squid-deb-proxy
fi
cat > /etc/squid-deb-proxy/mirror-dstdomain.acl << EOF
.com
.net
.org
EOF

/etc/init.d/squid-deb-proxy reload
