import logging
log = logging.getLogger(__name__)

import testbase
import utils

class TestMongodb(testbase.TestBase):
  def __init__(self):
    super(TestMongodb, self).__init__()
    self.bundle_type = 'mongodb'
    self.proxy_charm = 'cs:~justin-fathomdb/trusty/mongodb-proxy'
    self.consumer_charm = 'cs:~justin-fathomdb/trusty/node-app'
    self.juju_interface = 'mongodb'

  def create_consumer_relation(self):
    utils.juju_ensure_relation('%s:database' % self.proxy_service_name, '%s' % self.consumer_service_name)

t = TestMongodb()
t.run_test()