"""Actual repeated snapshot protection assertion with immutable returned observation."""
import argparse,copy,hashlib,importlib.util,json,os,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--producer-sha256',required=True);a=p.parse_args();assert sha(HERE/'source-manifest.json')==a.producer_sha256
 for row in json.loads((HERE/'source-manifest.json').read_bytes())['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
 base=HERE.parent/'api-v14';name='_cal_api_v14';spec=importlib.util.spec_from_file_location(name,base/'__init__.py',submodule_search_locations=[str(base)])
 mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
 original=__import__(name+'.run_session_checks',fromlist=['Sessions']);original.PROFILE='a7e194f479942a86992627d1415ef2234587640ededa2cdc4eda473a83ba6cc3'
 class Snapshots(original.Sessions):
  def invoke(self,c,*,raw=None):
   result=super().invoke(c,raw=raw);self.events[-1]=copy.deepcopy(self.events[-1]);return result
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Snapshots('test_33_reply_profile_binding_does_not_mutate_host')]))
 out=HERE/'receipts/0001';out.mkdir(parents=True,exist_ok=False,mode=0o700)
 for name,value in [('tests.json',{'result':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'owned_fixture_root_removed':not Snapshots.root.exists(),'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}),('wire-observations.json',Snapshots.events)]:
  fd=os.open(out/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(original.source.encoded(value))
 return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
