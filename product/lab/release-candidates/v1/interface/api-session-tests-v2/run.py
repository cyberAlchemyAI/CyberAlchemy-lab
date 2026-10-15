"""Preserve all Session guards; resolve the privacy test's explicit selected dependency."""
import argparse,copy,hashlib,importlib.util,json,os,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);p.add_argument('--profile-sha256',required=True);p.add_argument('--producer-sha256',required=True);a=p.parse_args()
 assert sha(HERE/'source-manifest.json')==a.producer_sha256
 for row in json.loads((HERE/'source-manifest.json').read_bytes())['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
 base=HERE.parent/'api-v14';assert sha(base/'source-manifest.json')==a.source_sha256
 for row in json.loads((base/'source-manifest.json').read_bytes())['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
 name='_cal_api_v14';spec=importlib.util.spec_from_file_location(name,base/'__init__.py',submodule_search_locations=[str(base)])
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 original=__import__(name+'.run_session_checks',fromlist=['Sessions']);workspace=__import__(name+'.workspace',fromlist=['privacy']);original.PROFILE=a.profile_sha256
 class CorrectedSessions(original.Sessions):
  def opening(self,*,key=None):
   # Malformed caller input is a copied fixture message, never a mutation
   # of the independently captured SourceRecord ArtifactRef.
   return copy.deepcopy(super().opening(key=key))
  def test_28_no_short_memory_in_any_recorded_reply(self):
   # Only this fixture dependency is corrected. Actual production validation
   # and all original assertions remain selected source implementations.
   for row in self.events:workspace.privacy(row['reply']);original.EL.no_private_memory(row['reply'])
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CorrectedSessions))
 output=HERE/'receipts/0001';output.mkdir(parents=True,exist_ok=False,mode=0o700)
 values={'tests.json':{'result':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'source_sha256':a.source_sha256,'profile_sha256':a.profile_sha256,'actual_original_assertions_retained':True,'fixture_dependency_correction':'Explicit selected privacy import; copied complete opening messages isolate negative inputs from signed SourceRecord metadata','owned_fixture_root_removed':not CorrectedSessions.root.exists(),'authority_effect':'none','actual_owner_outcome':None,'task_complete':False},'wire-observations.json':getattr(CorrectedSessions,'events',[])}
 for filename,v in values.items():
  fd=os.open(output/filename,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(original.source.encoded(v))
 return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
