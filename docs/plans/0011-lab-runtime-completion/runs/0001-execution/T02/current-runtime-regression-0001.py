"""Whole original affected classes; exact current pins, one runtime worker.

No production callback/clock substitution. No private keys or RAM snapshots in
the result. Original fixture methods run unchanged apart from reviewed changes.
"""
import datetime
import fcntl
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
SOURCE='ded1d9dd32d0ebc562293fcc2c6e946f548a9c48911a48b95913f506ae1c0cd1'
PROFILE='195d6a2e1aa27367ba438569d359a1e606841579084138ca71069b412fda90b6'

class Observed(unittest.TestResult):
    def __init__(self):
        super().__init__();self.observations=[]
    def startTest(self,test):
        super().startTest(test);self.started=time.monotonic()
        print(json.dumps({'phase':'test-start','test':test.id()}),flush=True)
    def record(self,test,status,error=None):
        row={'test':test.id(),'status':status,'elapsed_seconds':time.monotonic()-self.started}
        if error:
            row['error_type']=error[0].__name__;tb=error[2];frames=[]
            while tb:
                frames.append({'file':tb.tb_frame.f_code.co_filename,'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno});tb=tb.tb_next
            row['frames']=frames
        self.observations.append(row)
        print(json.dumps({k:v for k,v in row.items() if k!='frames'}),flush=True)
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'PASS')
    def addFailure(self,test,error):self.failures.append((test,error[0].__name__));self.record(test,'FAIL',error)
    def addError(self,test,error):self.errors.append((test,error[0].__name__));self.record(test,'ERROR',error)
    def addSkip(self,test,reason):super().addSkip(test,'bounded skip');self.record(test,'SKIP')

def main():
    lock=(RUN/'lease-sensitive-runtime.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    name='_root_api17_current_whole_regression0001'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    guard=__import__(name+'.guard',fromlist=['verify'])
    guard.verify(SOURCE)
    classes=[]
    for leaf,class_name in [('test_custody_sessions','Sessions'),('run_session_checks','Sessions'),('test_termination_boundaries','TerminationBoundaries')]:
        module=__import__(name+'.'+leaf,fromlist=[class_name]);module.PROFILE=PROFILE
        classes.append(getattr(module,class_name))
    result=Observed();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c)for c in classes).run(result)
    guard.verify(SOURCE)
    record={'schema_version':'lab-current-whole-Session-regression/v1-candidate','started_at':started,
        'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':SOURCE,'profile_sha256':PROFILE,
        'observations':result.observations,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'skipped':len(result.skipped),'entry_exit_current_guard':'PASS','historical_physical_closure':'REFUSED',
        'task_complete':False,'authority_effect':'none','private_keys_or_RAM_snapshots_recorded':False,
        'result':'PASS' if result.wasSuccessful() and not result.skipped else 'FAIL'}
    with (RUN/'T02/current-runtime-regression-0001.json').open('x') as handle:json.dump(record,handle,indent=2);handle.write('\n')
    print(json.dumps({k:v for k,v in record.items() if k!='observations'}),flush=True)
    lock.close()
    return 0 if record['result']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
