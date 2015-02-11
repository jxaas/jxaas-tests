#!/usr/bin/env python

import logging
log = logging.getLogger(__name__)

import os
import testbase
import time
import utils
import elasticsearch

class TestElasticsearch(testbase.TestBase):
  def __init__(self, protocol=None):
    super(TestElasticsearch, self).__init__()
    self.bundle_type = 'es'
    self.proxy_charm = 'cs:~justin-fathomdb/trusty/elasticsearch-proxy'
    self.consumer_charm = 'cs:~justin-fathomdb/trusty/kibana'
    self.juju_interface = 'elasticsearch'
    if protocol:
      self.proxy_properties['protocol'] = protocol

  def create_consumer_relation(self):
    utils.juju_ensure_relation('%s:rest' % self.proxy_service_name, '%s:rest' % self.consumer_service_name)

  def _db_connect(self, relinfo):
    log.info("Connecting to elasticsearch %s", relinfo)

    host = {}
    host['host'] = relinfo.get('host')
    if relinfo.get('port'):
      host['port'] = int(relinfo.get('port'))

    connection = elasticsearch.Elasticsearch([host])
    return connection

  def check_service_state_consumer(self):
    relinfo = self.get_relation_properties()
    self._run_test_elasticsearch(relinfo)

  def check_service_state_proxy(self):
    relinfo = self.get_relation_properties()
    db = self._db_connect(relinfo)
    db.index(index="test-index1", doc_type="test-doctype1", id=1, body={ "hello": "world" })

  def _run_test_elasticsearch(self, relinfo):
    db = self._db_connect(relinfo)

    for i in xrange(10):
      db.index(index="test-index2", doc_type="test-doctype2", id=i, body={ "n": i })

    for i in xrange(10):
      o = db.get(index="test-index2", doc_type="test-doctype2", id=i)
      log.info("Got object %s", o)
      assert o['_source']['n'] == i

  # TODO
  def change_properties(self):
    pass

  def inject_fault(self):
    utils.juju_ssh(self.backend_main_service_name, '0', ['sudo', 'service', 'elasticsearch', 'stop'])
    time.sleep(5)

t = TestElasticsearch(protocol=os.environ.get('TEST_PROTOCOL'))
t.run_test()
