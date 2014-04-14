repository = '/home/justinsb/juju/charms'
# service_name = 'it%s' % (int(time.time()))
service_name = 'it1397486022'
tenant = '405ad90bb19248af844071269cb5899c'
service_type = 'mysql'

consumer_charm = 'mediawiki'

relation = 'db'

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

status = juju_status()
print status['services'].keys()

# juju_deploy_service('local:precise/mysql-proxy', service_name, repository)

consumer_service_name = 'it-consumer-' + service_name
#juju_deploy_service(consumer_charm, consumer_service_name, repository)

#juju_add_relation('%s:%s' % (service_name, relation), '%s:%s' % (consumer_service_name, relation))

service_state = wait_service_started(service_name)
log.info("Proxy charm, all units started: %s", service_state)

main_service_name = 'u%s-%s-%s-%s' % (tenant, service_type, service_name, service_type)

main_service_state = wait_service_started(main_service_name)
log.info("Main XaaS service started: %s", main_service_state)

jxaas = jujuxaas.client.Client(url='http://10.0.3.1:8080/xaas', username='', password='')
properties = jxaas.get_relation_properties(tenant, service_type, service_name, relation)
properties = properties['Properties']
log.info("JXaaS relation properties: %s", properties)

consumer_service_state = wait_service_started(consumer_service_name)
log.info("Consumer charm, all units started: %s", consumer_service_state)

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



logs = jxaas.get_log(tenant, service_type, service_name)
assert len(logs) > 0

# TODO: Verify a line from the log
# TODO: Verify that there are no lines from other services in the log

metrics = jxaas.get_metrics(tenant, service_type, service_name)
assert len(metrics) > 0

# TODO: Verify some metrics from the log
# TODO: Verify there are no other metrics in the log


log.info("Setting slow-query-time property on proxy charm; should be forwarded to main charm")
juju_set_property(service_name, 'slow-query-time', '0.1')

time.sleep(1)

properties = juju_get_properties(main_service_name)
log.info("Properties = %s", properties)
log.info("slow-query-time = %s", properties['slow-query-time'])
assert '0.1' == properties['slow-query-time']['value']
