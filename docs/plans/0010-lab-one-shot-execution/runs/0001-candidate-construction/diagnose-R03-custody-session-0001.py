"""Actual unchanged rawSession04 and selected exceptionframes; no locals/memory."""
import argparse,hashlib,importlib.util,json,os,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-v18'
PIN='07a14881e21fe3c0db88ff55e0b3b982de05959cbd68a931efa89a2c3368e445';PROFILE='fba4e67cada59ce70277ba2cfb09ece691193989bc20821ca4457eebcf5656ca'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def guard(pin):
 p=HERE/'custody-session-diagnostic-source-0001.json';assert sha(p.read_bytes())==pin
 for row in json.loads(p.read_bytes())['files']:
  p=ROOT/row['path'];assert p.is_file() and not p.is_symlink() and sha(p.read_bytes())==row['sha256'],row['path']
def emit(p,v):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();guard(a.source_sha256)
 name='_cal_raw_session_causal_diagnostic';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 def imported(n):return __import__(name+'.'+n,fromlist=['*'])
 G=imported('guard');G.verify(PIN);T=imported('test_custody_sessions');T.PROFILE=PROFILE;F=imported('example_fixture');W=imported('workspace');traces=[];witnesses=[];roots=[]
 paths={str(API/'custody_context_sessions.py'),str(API/'service.py'),str(T.EL.__file__),str(API/'workspace.py')}
 def trace(frame,event,arg):
  if event=='exception' and frame.f_code.co_filename in paths:
   error_type,error,_=arg
   if isinstance(error,(ValueError,AssertionError,KeyError,RuntimeError)):
    entry={'path':str(Path(frame.f_code.co_filename).relative_to(ROOT)),'function':frame.f_code.co_name,'line':frame.f_lineno,'exception_type':error_type.__name__,'message':str(error)[:2000]};W.privacy(entry);traces.append(entry);print(json.dumps({'exception_frame':entry}),flush=True)
  return trace
 class Actual(T.Sessions):
  def setUp(self):
   super().setUp();roots.append(self.root);raw=F.proof(self.key,self.channel.challenge);witnesses.append({'public_policy':json.loads(self.policy.read_bytes()),'signed_nonce_proof':json.loads(raw),'challenge':self.channel.challenge,'authenticated':self.authenticated})
  def tearDown(self):
   self.diagnostic_journal=[]
   for p in self.root.joinpath('workspace/journal').glob('session-*.json'):self.diagnostic_journal.append(json.loads(p.read_bytes()))
   super().tearDown()
 Actual.setUpClass();case=Actual('test_04_no_instance_identity_reuse')
 try:
  sys.settrace(trace);result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([case]))
 finally:sys.settrace(None);Actual.stack.close()
 report={'schema_version':'lab-raw-session-causal-diagnostic/v1-candidate','result':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'diagnostic_only':True,'source_sha256':PIN,'profile_sha256':PROFILE,'original_test_method':'test_04_no_instance_identity_reuse','exception_frames':traces,'actual_wire_events':Actual.events,'public_witnesses':witnesses,'observed_session_journal':getattr(case,'diagnostic_journal',[]),'owned_hosts_removed':all(not p.exists() for p in roots),'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
 W.privacy(report);assert report['owned_hosts_removed'];G.verify(PIN);guard(a.source_sha256);emit(HERE/'custody-session-diagnostic-result-0001.json',report)
 print(json.dumps({'result':'OBSERVED','actual_test_result':report['result'],'tests_run':result.testsRun,'exception_frames':len(traces),'owned_hosts_removed':True}),flush=True)
if __name__=='__main__':main()
