#!/usr/bin/env python

import logging
log = logging.getLogger(__name__)

import os
import testbase
import time
import utils

import pymongo

class TestMongodb(testbase.TestBase):
  def __init__(self, protocol=None):
    super(TestMongodb, self).__init__()
    self.bundle_type = 'mongodb'
    self.proxy_charm = 'cs:~justin-fathomdb/trusty/mongodb-proxy'
    self.consumer_charm = 'cs:~justin-fathomdb/trusty/node-app'
    self.juju_interface = 'mongodb'
    if protocol:
      self.proxy_properties['protocol'] = protocol

  def create_consumer_relation(self):
    utils.juju_ensure_relation('%s:database' % self.proxy_service_name, '%s' % self.consumer_service_name)

  def _db_connect(self, relinfo):
    log.info("Connecting to mongo %s", relinfo)
    host = relinfo.get('hostname')
    port = int(relinfo.get('port'))
    dbname = 'testdb'
    connection = pymongo.MongoClient(host, port)
    db = connection[dbname]
    return db

  def check_service_state_consumer(self):
    relinfo = self.get_relation_properties()
    self._run_test_mongodb(relinfo)

  def check_service_state_proxy(self):
    relinfo = self.get_relation_properties()
    db = self._db_connect(relinfo)
    collection  = db['testcollection']
    collection.insert({ "hello": "world" })

  def _run_test_mongodb(self, relinfo):
    db = self._db_connect(relinfo)
    collection = db['testcollection']

    # Delete everything
    collection.remove(None)

    for i in xrange(10):
      collection.insert({ "n": i })

    for i in xrange(12):
      items = collection.find()
      for item in items:
        item.pop('_id', None)
        collection.insert(item)

    items = collection.find()
    log.info("items %s", items.count())
    assert items.count() > 40000

  # TODO
  def change_properties(self):
    pass

  def inject_fault(self):
    utils.juju_ssh(self.backend_main_service_name, '0', ['sudo', 'service', 'mongodb', 'stop'])
    time.sleep(5)

t = TestMongodb(protocol=os.environ.get('TEST_PROTOCOL'))
t.run_test()
