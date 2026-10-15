"""Profile the unmodified real-deadline failure; collect function timings only."""
import cProfile
import hashlib
import importlib.util
import json
from pathlib import Path
import pstats
import sys
import unittest

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v96'
SOURCE='a5c61899e2ec5bd07d098475842848846bdd42d18b82e16d879f835361f44048'
PROFILE='451726c90fdeeff92c2b1f6351698f8bf9bfa4722c9fc395dd0ad36f70461e99'
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    out=RUN/'Session-opening-profile-0140.json';assert not out.exists()
    name='_cal_original_session_timing_0140'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    guard=__import__(name+'.guard',fromlist=['*']);guard.verify(SOURCE)
    tests=__import__(name+'.run_session_checks',fromlist=['*']);tests.SOURCE=SOURCE;tests.PROFILE=PROFILE
    suite=unittest.TestSuite([tests.Sessions('test_27_actual_expiry_timer_disposes')])
    profile=cProfile.Profile();result=profile.runcall(unittest.TextTestRunner(verbosity=2).run,suite)
    stats=pstats.Stats(profile);timings=[]
    for (file,line,function),(primitive,calls,total,cumulative,callers) in stats.stats.items():
        timings.append({'file':file,'line':line,'function':function,'primitive_calls':primitive,'calls':calls,
                        'total_seconds':total,'cumulative_seconds':cumulative})
    guard.verify(SOURCE)
    value={'schema_version':'lab-original-session-timing-diagnosis/v1-candidate','result':'PASS' if result.wasSuccessful() else 'FAIL',
           'actual_methods':result.testsRun,'failures':[detail for test,detail in result.failures],
           'errors':[detail for test,detail in result.errors],'function_timings':sorted(timings,key=lambda x:x['cumulative_seconds'],reverse=True),
           'original_clock_deadline_assertions_callbacks_unchanged':True,'source_guarded_exit_completed':True,
           'function_locals_private_keys_and_RAM_inspected':False,
           'files':[binding(p) for p in [API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve()]],
           'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'goal_complete':False,
           'claim_ceiling':'Function timing diagnosis of one unmodified original test. Profiling changes runtime cost; no performance qualification inferred.'}
    with out.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'report_binding':binding(out)}),flush=True)
if __name__=='__main__':main()
