import functools
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
tenant = 'a4792a88fb9d4ec2898c596c4c428ad1'
bundle_type = 'mysql'

proxy_charm = 'cs:~justin-fathomdb/trusty/mysql-proxy'
consumer_charm = 'cs:~justin-fathomdb/trusty/mediawiki'

relation = 'db'

jxaas = jujuxaas.client.Client(url='http://127.0.0.1:8080/xaas', username='', password='')

status = juju_status()
print status['services'].keys()

if not get_service_state(service_name):
  juju_deploy_service(proxy_charm, service_name, repository)

# time.sleep(120)

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

relinfo = jxaas.get_relation_properties(tenant, bundle_type, service_name, relation)
relinfo = relinfo['Properties']
log.info("JXaaS relation properties: %s", relinfo)

consumer_service_state = wait_service_started(consumer_service_name)
log.info("Consumer charm, all units started: %s", consumer_service_state)


import MySQLdb


def mysql_connect(relinfo):
  db = MySQLdb.connect(host=relinfo.get('host'),
                       user=relinfo.get('user'),
                       passwd=relinfo.get('password'),
                       db=relinfo.get('database'))
  return db

def execute_sql(db, sql):
  cur = db.cursor()
  cur.execute(sql)
  rows = cur.fetchall()
  cur.close()
  return rows


def check_for_wiki_tables(relinfo):
  db = mysql_connect(relinfo)
  rows = execute_sql(db, 'SHOW TABLES')
  tables = [row[0] for row in rows]

  if 'interwiki' in tables:
    return tables

  return None

# Wait for consumer charm to finish configuration
wait_for(functools.partial(check_for_wiki_tables, relinfo))

logs = jxaas.get_log(tenant, bundle_type, service_name)
assert len(logs) > 0

# TODO: Verify a line from the log
# TODO: Verify that there are no lines from other services in the log

metrics = jxaas.get_metrics(tenant, bundle_type, service_name)
assert len(metrics) > 0

# TODO: Verify some metrics from the log
# TODO: Verify there are no other metrics in the log

properties = juju_get_properties(main_service_name)
if str(properties['slow-query-time']['value']) != '0.01':
  log.info("Setting slow-query-time property on proxy charm; should be forwarded to main charm")
  juju_set_property(service_name, 'slow-query-time', '0.01')

  time.sleep(10)

  properties = juju_get_properties(main_service_name)
  log.info("Properties = %s", properties)
  log.info("slow-query-time = %s", properties['slow-query-time'])
  assert '0.01' == str(properties['slow-query-time']['value'])

# TODO: Scaling doesn't make sense with the current MySQL charm
# TODO: Should we use MySQL-Proxy as a charm on the server side?
# jxaas.ensure_instance(tenant, bundle_type, service_name, units=2)




jxaas.destroy_instance(tenant, bundle_type, service_name)

# TODO: Wait for service to disappear

# TODO: Really, destroying the service should do this...
juju_destroy_service(service_name)

juju_destroy_service(consumer_service_name)
