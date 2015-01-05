#!/bin/bash

set -e
set -x

if [[ ! -d apps/spring-music ]]; then
  mkdir -p apps
  pushd apps
  git clone https://github.com/cloudfoundry-samples/spring-music.git
  popd
fi

pushd apps/spring-music
./gradlew assemble
cf push spring-music -n spring-music
popd

cf service-brokers
cf create-service-broker jxaas admin admin http://10.0.3.1:8080/cf

cf service-access
# Should include mysql

cf enable-service-access mysql
cf service-access

# Should include Nirvana:
curl http://spring-music.10.244.0.34.xip.io/albums

# Should include 'in-memory', not 'mysql'
curl http://spring-music.10.244.0.34.xip.io/info

cf create-service mysql nano mysql1
cf services
cf bind-service spring-music mysql1

cf restage spring-music

# Should include Nirvana:
curl http://spring-music.10.244.0.34.xip.io/albums

# Should include 'mysql', not 'in-memory':
curl http://spring-music.10.244.0.34.xip.io/info

cf unbind-service spring-music mysql1
cf restage spring-music

# Should include Nirvana:
curl http://spring-music.10.244.0.34.xip.io/albums

# Should include 'in-memory', not 'mysql'
curl http://spring-music.10.244.0.34.xip.io/info

cf delete-service -f mysql1



