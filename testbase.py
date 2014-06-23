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


class TestBase(object):
  def __init__(self, prefix=None):
    if not prefix:
      if len(sys.argv) > 1:
        prefix = sys.argv[1]
      else:
        prefix = 'it%s' % (int(time.time()))
    self.repository = None
    # self.repository = '/home/justinsb/juju/charms'
    # proxy_service_name = 'it%s' % (int(time.time()))
    self.proxy_service_name = prefix + '-proxy'
    self.consumer_service_name = prefix + '-consumer'

    self.jxaas_url = 'http://10.0.3.1:8080/xaas'
    self.jxaas_tenant = 'tenant1'
    self.jxaas_username = 'user1'
    self.jxaas_password = 'secret1'

    self.jxaas = jujuxaas.client.Client(url=self.jxaas_url,
                                        tenant=self.jxaas_tenant,
                                        username=self.jxaas_username,
                                        password=self.jxaas_password)


  def init(self):
    backend_main_service_name = 'u%s-%s-%s-%s' % (self.jxaas_tenant, self.bundle_type, self.proxy_service_name, self.bundle_type)
    self.backend_main_service_name = backend_main_service_name

  def run_test(self):
    self.init()

    self.create_proxy_service()
    self.create_consumer_service()
    self.create_consumer_relation()
    self.wait_proxy_started()
    relinfo = self.get_relation_properties()
    self.wait_consumer_started()

    self.check_service_state_consumer()

    self.check_log()

    self.change_properties()
    self.test_scaling()

    self.check_metrics()

    self.cleanup()

    print "Test: SUCCESS"

  def wait_proxy_started(self):
    service_state = wait_service_started(self.proxy_service_name)
    log.info("Proxy charm, all units started: %s", service_state)

    # Proxy should only be started once the backend service is started
    # wait_jxaas_started(self.jxaas, self.bundle_type, self.proxy_service_name)
    #    main_service_state = wait_service_started(self.backend_main_service_name)
    #    log.info("Main XaaS service started: %s", main_service_state)

  def get_relation_properties(self):
    relinfo = self.jxaas.get_relation_properties(self.bundle_type, self.proxy_service_name, self.juju_interface)
    relinfo = relinfo['Properties']
    log.info("JXaaS relation properties: %s", relinfo)

    return relinfo

  def wait_consumer_started(self):
    consumer_service_state = wait_service_started(self.consumer_service_name)
    log.info("Consumer charm, all units started: %s", consumer_service_state)

  def create_proxy_service(self):
    # status = juju_status()
    # print status['services'].keys()

    if not get_service_state(self.proxy_service_name):
      config = {}
      config['jxaas-url'] = self.jxaas_url
      config['jxaas-tenant'] = self.jxaas_tenant
      config['jxaas-user'] = self.jxaas_username
      config['jxaas-secret'] = self.jxaas_password
      juju_deploy_service(self.proxy_charm, self.proxy_service_name, self.repository, config)

      # time.sleep(120)

  def create_consumer_service(self):
    if not get_service_state(self.consumer_service_name):
      juju_deploy_service(self.consumer_charm, self.consumer_service_name, self.repository)

  def create_consumer_relation(self):
    raise Exception("Must implement create_consumer_relation")

  def check_service_state_consumer(self):
    log.warn("check_service_state_consumer not implemented")

  def change_properties(self):
    log.warn("change_properties not implemented")

  def test_scaling(self):
    log.warn("test_scaling not implemented")

  def check_log(self):
    logs = self.jxaas.get_log(self.bundle_type, self.proxy_service_name)
    assert len(logs) > 0

    # TODO: Verify a line from the log
    # TODO: Verify that there are no lines from other services in the log

  def check_metrics(self):
    metrics = self.jxaas.get_metrics(self.bundle_type, self.proxy_service_name)
    metrics = metrics['Metric']
    print "Metrics length %s" % (len(metrics))
    assert len(metrics) > 0

    print metrics
    # TODO: Verify some metrics from the log
    # TODO: Verify there are no other metrics in the log

  def cleanup(self):
    self.jxaas.destroy_instance(self.bundle_type, self.proxy_service_name)

    # TODO: Wait for service to disappear

    # TODO: Really, destroying the service should do this...
    juju_destroy_service(self.proxy_service_name)

    juju_destroy_service(self.consumer_service_name)
