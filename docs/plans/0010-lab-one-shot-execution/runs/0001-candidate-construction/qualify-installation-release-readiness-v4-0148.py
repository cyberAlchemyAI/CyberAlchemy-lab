"""Exact externally pinned real API qualification; retain full frozen history guards."""
import argparse
import importlib.util
import hashlib
import json
import pathlib
import sys
import unittest
import time
from datetime import datetime,timezone
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab');N=R/'product/lab/release-candidates/v1/interface/api-installation-release-v4';RUN=pathlib.Path(__file__).parent
parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);parser.add_argument('--profile-sha256',required=True);parser.add_argument('--case');parser.add_argument('--run',required=True);args=parser.parse_args();assert args.run.replace('-','').isalnum()
name='_cal_installation_release_readiness_v4_0148';spec=importlib.util.spec_from_file_location(name,N/'__init__.py',submodule_search_locations=[str(N)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
t=__import__(name+'.test_installation_release',fromlist=['InstallationReleaseAPI']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();t.SOURCE=args.source_sha256;t.PROFILE=args.profile_sha256
assert sha(N/'source-manifest.json')==t.SOURCE and sha(N/'contract-profile.json')==t.PROFILE
suite=unittest.TestSuite([t.InstallationReleaseAPI(args.case)]) if args.case else unittest.defaultTestLoader.loadTestsFromTestCase(t.InstallationReleaseAPI)
expected=1 if args.case else 22;assert suite.countTestCases()==expected
cases=[]
class Result(unittest.TextTestResult):
 def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'});print(test.id()+' PASS',flush=True)
 def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)});print(cases[-1]['detail'],flush=True)
 def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)});print(cases[-1]['detail'],flush=True)
start=time.time();started=datetime.now(timezone.utc).isoformat();result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
observations=getattr(t.InstallationReleaseAPI,'observations',[]);passed=result.wasSuccessful() and result.testsRun==expected
report={'schema_version':'lab-public-installation-release-qualification/v1-candidate','result':'PASS' if passed else 'FAIL','tests_run':result.testsRun,'expected_tests':expected,'cases':cases,'actual_public_calls':len(observations),'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.time()-start,'source_sha256':t.SOURCE,'profile_sha256':t.PROFILE,'runner_sha256':sha(pathlib.Path(__file__)),'full_frozen_history_entry_exit_guards_completed':passed,'original_test_method_ASTs_retained':323,'original_selected_producer_permission_signature_callbacks_unchanged':True,'actual_source_and_custody_fresh_reads':True,'whole_API_qualified':False,'human_pilot_observed':False,'actual_owner_outcome':None,'canonical_admissions_applied':0,'runtime_activations':0,'external_effects':0,'authority_effect':'none','goal_complete':False,'claim_ceiling':'Bounded actual authenticated API installation/release readiness cases on explicitly owned scratch with real private grant windows. Complete API qualification, actual human Product pilot and final owner R08 remain outstanding.'}
for filename,value in [('installation-release-readiness-v4-0148-'+args.run+'.json',report),('installation-release-readiness-v4-0148-'+args.run+'-wire.json',observations)]:
 with (RUN/filename).open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps({k:report[k] for k in ['result','tests_run','actual_public_calls','source_sha256','profile_sha256']}));raise SystemExit(0 if passed else 1)
