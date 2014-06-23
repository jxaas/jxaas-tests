import logging
log = logging.getLogger(__name__)

import testbase
import utils

import psycopg2

class TestPostgresql(testbase.TestBase):
  def __init__(self):
    super(TestPostgresql, self).__init__()
    self.bundle_type = 'pg'
    self.proxy_charm = 'cs:~justin-fathomdb/trusty/postgresql-proxy'
    self.consumer_charm = 'cs:~justin-fathomdb/trusty/python-django'
    self.juju_interface = 'pgsql'

  def create_consumer_relation(self):
    utils.juju_ensure_relation('%s:db' % self.proxy_service_name, '%s' % self.consumer_service_name)

  def db_connect(self, relinfo):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (
                  relinfo.get('host'), relinfo.get('database'), relinfo.get('user'), relinfo.get('password'))
    log.info("Connecting to postgres %s", conn_string)

    connection = psycopg2.connect(conn_string)
    connection.autocommit = True
    return connection

  def execute_sql(self, db, sql, fetch=True):
    log.info("Running SQL: %s", sql)
    cur = db.cursor()
    cur.execute(sql)
    rows = None
    if fetch:
      rows = cur.fetchall()
    cur.close()
    return rows

  def check_service_state_consumer(self):
    relinfo = self.get_relation_properties()

    self.run_test_sql(relinfo)

  def run_test_sql(self, relinfo):
    db = self.db_connect(relinfo)
    self.execute_sql(db, 'CREATE TABLE IF NOT EXISTS test1 (id int)', fetch=False)

    self.execute_sql(db, 'DELETE FROM test1', fetch=False)
    for i in xrange(10):
      self.execute_sql(db, 'INSERT INTO test1 VALUES (1)', fetch=False)

    for i in xrange(12):
      self.execute_sql(db, 'INSERT INTO test1 SELECT * FROM test1', fetch=False)

    rows = self.execute_sql(db, 'SELECT * FROM test1')
    log.info("Rows %s", len(rows))
    assert len(rows) > 40000

t = TestPostgresql()
t.run_test()
