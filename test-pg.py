import logging
log = logging.getLogger(__name__)

import testbase
import utils

class TestPostgresql(testbase.TestBase):
  def __init__(self):
    super(TestPostgresql, self).__init__()
    self.bundle_type = 'pg'
    self.proxy_charm = 'cs:~justin-fathomdb/trusty/postgresql-proxy'
    self.consumer_charm = 'cs:~justin-fathomdb/trusty/python-django'
    self.juju_interface = 'pgsql'

  def create_consumer_relation(self):
    utils.juju_ensure_relation('%s:db' % self.service_name, '%s' % self.consumer_service_name)

t = TestPostgresql()
t.run_test()