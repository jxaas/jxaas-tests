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

import testbase

import MySQLdb

class TestMysql(testbase.TestBase):
  def __init__(self):
    super(TestMysql, self).__init__()
    self.bundle_type = 'mysql'
    self.proxy_charm = 'cs:~justin-fathomdb/trusty/mysql-proxy'
    self.consumer_charm = 'cs:~justin-fathomdb/trusty/mediawiki'
    self.juju_interface = 'mysql'

  def mysql_connect(self, relinfo):
    db = MySQLdb.connect(host=relinfo.get('host'),
                         port=int(relinfo.get('port')),
                         user=relinfo.get('user'),
                         passwd=relinfo.get('password'),
                         db=relinfo.get('database'))
    return db

  def execute_sql(self, db, sql):
    log.info("Running SQL: %s", sql)
    cur = db.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    return rows

  def create_consumer_relation(self):
    juju_ensure_relation('%s:db' % self.proxy_service_name, '%s:db' % self.consumer_service_name)

  def check_service_state_proxy(self):
    relinfo = self.get_relation_properties()
    db = self.mysql_connect(relinfo)
    self.execute_sql(db, 'SHOW TABLES')

  def check_for_wiki_tables(self, relinfo):
    db = self.mysql_connect(relinfo)
    rows = self.execute_sql(db, 'SHOW TABLES')
    tables = [row[0] for row in rows]

    if 'interwiki' in tables:
      return tables

    return None

  def inject_fault(self):
    juju_ssh(self.backend_main_service_name, '0', ['sudo', 'service', 'mysql', 'stop'])
    time.sleep(5)

  def check_service_state_consumer(self):
    relinfo = self.get_relation_properties()
    # Wait for consumer charm to finish configuration
    wait_for(functools.partial(self.check_for_wiki_tables, relinfo))

    self.run_test1(relinfo)

  def change_properties(self):
    properties = juju_get_properties(self.backend_main_service_name)
    newv = 0.01
    if float(properties['slow-query-time']['value']) == newv:
      newv = 0.02

    log.info("Setting slow-query-time property on proxy charm; should be forwarded to main charm")
    juju_set_property(self.proxy_service_name, 'slow-query-time', str(newv))

    time.sleep(10)

    properties = juju_get_properties(self.backend_main_service_name)
    log.info("Properties = %s", properties)
    log.info("slow-query-time = %s", properties['slow-query-time'])
    assert newv == float(properties['slow-query-time']['value'])

    # Needed to avoid the MySQL restart
    time.sleep(10)

    relinfo = self.get_relation_properties()
    db = self.mysql_connect(relinfo)
    rows = self.execute_sql(db, "SHOW VARIABLES LIKE 'long_query_time'")
    assert len(rows) == 1
    assert float(rows[0][1]) == newv

# def test_scaling(self):
# TODO: Scaling doesn't make sense with the current MySQL charm
# TODO: Should we use MySQL-Proxy as a charm on the server side?
# jxaas.ensure_instance(tenant, bundle_type, service_name, units=2)

  def run_test1(self, relinfo):
    db = self.mysql_connect(relinfo)
    self.execute_sql(db, 'CREATE TABLE IF NOT EXISTS test1 (id int)')

    self.execute_sql(db, 'DELETE FROM test1')
    for i in xrange(10):
      self.execute_sql(db, 'INSERT INTO test1 VALUES (1)')

    for i in xrange(12):
      self.execute_sql(db, 'INSERT INTO test1 SELECT * FROM test1')

    rows = self.execute_sql(db, 'SELECT * FROM test1')
    log.info("Rows %s", len(rows))
    assert len(rows) > 40000


t = TestMysql()
t.run_test()
