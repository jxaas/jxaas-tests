import os
import json
import subprocess
import sys
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

def juju_deploy_service(charm, name, repository=None):
  log.info("Deploying service: %s %s", charm, name)
  args = ['juju', 'deploy']
  if repository:
    args = args + ['--repository=' + repository]
  args = args + [charm, name]
  
  return _run_command(args)

def juju_add_relation(l, r):
  log.info("Add relation: %s %s", l, r)
  args = ['juju', 'add-relation', l, r]
  
  return _run_command(args)

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

def wait_service_started(service_name):
  # TODO: Timeout
  while True:
    service_state = get_service_state(service_name)
    if service_state:
      log.debug("Service state for %s => %s", service_name, service_state)
      unit_states = get_unit_states(service_state)
      assert len(unit_states) != 0
      if all(v == 'started' for v in unit_states.itervalues()):
        return service_state
    time.sleep(5)
  
