import os
import json
import subprocess
import sys
import tempfile
import time
import yaml

import logging
log = logging.getLogger(__name__)

def _run_command(args, stdin='', exit_codes=[0], **kwargs):
  print "Running command: " + ' '.join(args)

  proc = subprocess.Popen(args,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          **kwargs)

  out, err = proc.communicate(input=stdin)
  retcode = proc.returncode
  if not retcode in exit_codes:
    print "Calling return error: " + ' '.join(args)
    print "Output: " + out
    print "Error: " + err
    raise subprocess.CalledProcessError(retcode, args)
  return out, err

def juju_status():
  stdout, _ = _run_command(['juju', 'status'])
  return yaml.load(stdout)

def juju_deploy_service(charm, name, repository=None, config=None):
  log.info("Deploying service: %s %s", charm, name)
  config_file = None
  if config:
    fd, config_file = tempfile.mkstemp()
    mapped = {}
    mapped[name] = config
    y = yaml.dump(mapped)
    os.write(fd, y)
    os.close(fd)
  args = ['juju', 'deploy']
  if repository:
    args = args + ['--repository=' + repository]
  if config_file:
    args = args + ['--config', config_file]
  args = args + [charm, name]

  out, err = _run_command(args)

  if config_file:
    os.remove(config_file)

  return out, err

def juju_destroy_service(name):
  log.info("Destroying service: %s", name)
  args = ['juju', 'destroy-service', name]
  return _run_command(args)

def juju_set_property(service, name, value):
  log.info("Setting property on service %s: %s=%s", service, name, value)
  args = ['juju', 'set', service, '%s=%s' % (name, value)]
  return _run_command(args)

def juju_get_properties(service):
  args = ['juju', 'get', service]
  out, _ = _run_command(args)
  return yaml.load(out)['settings']

def juju_add_relation(l, r):
  log.info("Add relation: %s %s", l, r)
  args = ['juju', 'add-relation', l, r]

  return _run_command(args)

def juju_ensure_relation(l, r):
  log.info("Ensure relation: %s %s", l, r)
  args = ['juju', 'add-relation', l, r]
  _, stderr = _run_command(args, exit_codes=[0, 1])
  if stderr:
    if not 'relation already exists' in stderr:
      raise Exception("Error adding relation: %s" % stderr)

def get_service_state(service_name):
  status = juju_status()
  service_state = status['services'].get(service_name)
  return service_state

def get_unit_states(service_state):
  states = {}
  units = service_state.get('units')
  for key, unit in units.iteritems():
    agent_state = unit.get('agent-state')
    log.debug("Unit state: %s => %s", key, unit)
    states[key] = agent_state
  return states

def get_jxaas_unit_states(service_state):
  states = {}
  units = service_state.get('Units')
  for key, unit in units.iteritems():
    unit_state = unit.get('Status')
    log.debug("Unit state: %s => %s", key, unit)
    states[key] = unit_state
  return states


def wait_for(fn):
  # TODO: Timeout
  while True:
    done = fn()
    if done:
      return done
    time.sleep(5)

def wait_jxaas_started(client, bundle_type, service_name):
  def jxaas_started():
    service_state = client.get_instance_state(bundle_type, service_name)
    if service_state:
      log.debug("Service state for %s => %s", service_name, service_state)
      unit_states = get_jxaas_unit_states(service_state)
      assert len(unit_states) != 0
      if all(v == 'started' for v in unit_states.itervalues()):
        return service_state
    return None

  return wait_for(jxaas_started)

def wait_service_started(service_name):
  def service_started():
    service_state = get_service_state(service_name)
    if service_state:
      log.debug("Service state for %s => %s", service_name, service_state)
      unit_states = get_unit_states(service_state)
      assert len(unit_states) != 0
      if all(v == 'started' for v in unit_states.itervalues()):
        return service_state

    return None

  return wait_for(service_started)


