import logging
log = logging.getLogger(__name__)

import testbase
import utils

class TestElasticsearch(testbase.TestBase):
  def __init__(self):
    super(TestElasticsearch, self).__init__()
    self.bundle_type = 'es'
    self.proxy_charm = 'cs:~justin-fathomdb/trusty/elasticsearch-proxy'
    self.consumer_charm = 'cs:~justin-fathomdb/trusty/kibana'
    self.juju_interface = 'rest'

  def create_consumer_relation(self):
    utils.juju_ensure_relation('%s:rest' % self.service_name, '%s:rest' % self.consumer_service_name)


t = TestElasticsearch()
t.run_test()