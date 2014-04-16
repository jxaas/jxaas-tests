import os
import json
import subprocess
import sys
import time
import yaml
import jujuxaas.client

from utils import *

import logging
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)


if len(sys.argv) > 1:
  prefix = sys.argv[1]
else:
  prefix = 'it%s' % (int(time.time()))

repository = '/home/justinsb/juju/charms'
# service_name = 'it%s' % (int(time.time()))
service_name = prefix + '-proxy'
tenant = '2c1f1c9f92d7481a8015fd6b53fb2f26'
bundle_type = 'mysql'

consumer_charm = 'mediawiki'

relation = 'db'

jxaas = jujuxaas.client.Client(url='http://127.0.0.1:8080/xaas', username='', password='')

status = juju_status()
print status['services'].keys()

if not get_service_state(service_name):
  juju_deploy_service('local:precise/mysql-proxy', service_name, repository)

#time.sleep(120)

consumer_service_name = prefix + '-consumer'
if not get_service_state(consumer_service_name):
  juju_deploy_service(consumer_charm, consumer_service_name, repository)

juju_ensure_relation('%s:%s' % (service_name, relation), '%s:%s' % (consumer_service_name, relation))

service_state = wait_service_started(service_name)
log.info("Proxy charm, all units started: %s", service_state)

wait_jxaas_started(jxaas, tenant, bundle_type, service_name)

main_service_name = 'u%s-%s-%s-%s' % (tenant, bundle_type, service_name, bundle_type)

main_service_state = wait_service_started(main_service_name)
log.info("Main XaaS service started: %s", main_service_state)

properties = jxaas.get_relation_properties(tenant, bundle_type, service_name, relation)
properties = properties['Properties']
log.info("JXaaS relation properties: %s", properties)

consumer_service_state = wait_service_started(consumer_service_name)
log.info("Consumer charm, all units started: %s", consumer_service_state)

# TODO: Need sleep for consumer charm to finish configuration?

import MySQLdb

db = MySQLdb.connect(host=properties.get('host'),
                     user=properties.get('user'),
                     passwd=properties.get('password'),
                     db=properties.get('database'))

cur = db.cursor() 
cur.execute("SHOW TABLES")
tables = [row[0] for row in cur.fetchall()]
cur.close()

assert 'interwiki' in tables


logs = jxaas.get_log(tenant, bundle_type, service_name)
assert len(logs) > 0

# TODO: Verify a line from the log
# TODO: Verify that there are no lines from other services in the log

metrics = jxaas.get_metrics(tenant, bundle_type, service_name)
assert len(metrics) > 0

# TODO: Verify some metrics from the log
# TODO: Verify there are no other metrics in the log


log.info("Setting slow-query-time property on proxy charm; should be forwarded to main charm")
juju_set_property(service_name, 'slow-query-time', '0.1')

time.sleep(10)

properties = juju_get_properties(main_service_name)
log.info("Properties = %s", properties)
log.info("slow-query-time = %s", properties['slow-query-time'])
assert '0.1' == str(properties['slow-query-time']['value'])


jxaas.destroy_instance(tenant, bundle_type, service_name)

# TODO: Wait for service to disappear

# TODO: Really, destroying the service should do this...
juju_destroy_service(service_name)

juju_destroy_service(consumer_service_name)
