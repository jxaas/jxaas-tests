jxaas-tests
===========

This is the integration test-suite for JXaaS.

The main documentation can be found [here](https://github.com/jxaas/jxaas)

# How to run tests

Check out tests:
```
cd ~/jxaas
git clone http://github.com/jxaas/jxaas-tests.git

cd ~/jxaas/jxaas-tests
ci/compile.sh
```


Run postgres tests:
```
cd ~/jxaas/jxaas-tests
bin/run_all_scenarios test-pg
```


Run all tests (except CloudFoundry tests):
```
cd ~/jxaas/jxaas-tests
bin/run_all
```


To run the CloudFoundry tests, install CloudFoundry (we have some (instructions)[https://github.com/jxaas/jxaas/blob/master/docs/tutorial/cf.md]),
and then
```
cd ~/jxaas/jxaas-tests
bin/run_all_scenarios test-cf-mysql
```
