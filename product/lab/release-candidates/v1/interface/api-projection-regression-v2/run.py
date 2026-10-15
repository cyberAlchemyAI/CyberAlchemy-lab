"""Full original Session suite in five bounded isolated groups with durable streams."""
import argparse,copy,hashlib,importlib.util,json,os,subprocess,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];GROUPS={'A':range(0,4),'B':range(4,9),'C':range(9,13),'D':range(13,23),'E':range(23,34)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write((json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode())
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);p.add_argument('--profile-sha256',required=True);p.add_argument('--producer-sha256',required=True);p.add_argument('--shard',choices=list(GROUPS));a=p.parse_args()
 assert sha(HERE/'source-manifest.json')==a.producer_sha256
 for row in json.loads((HERE/'source-manifest.json').read_bytes())['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
 base=HERE.parent/'api-v16';assert sha(base/'source-manifest.json')==a.source_sha256
 for row in json.loads((base/'source-manifest.json').read_bytes())['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
 if not a.shard:
  output=HERE/'receipts/0001';output.mkdir(parents=True,exist_ok=False,mode=0o700);children=[]
  for group in GROUPS:
   directory=output/group;directory.mkdir(mode=0o700);stdout=open(directory/'producer.stdout','xb');stderr=open(directory/'producer.stderr','xb')
   os.chmod(directory/'producer.stdout',0o600);os.chmod(directory/'producer.stderr',0o600)
   command=[sys.executable,str(Path(__file__).resolve()),'--source-sha256',a.source_sha256,'--profile-sha256',a.profile_sha256,'--producer-sha256',a.producer_sha256,'--shard',group]
   child=subprocess.Popen(command,stdout=stdout,stderr=stderr,cwd=ROOT);children.append((group,child,stdout,stderr))
  write(output/'started.json',{'children':[{'group':g,'pid':c.pid} for g,c,_,_ in children],'source_sha256':a.source_sha256,'profile_sha256':a.profile_sha256,'authority_effect':'none'})
  observed=[]
  for group,child,stdout,stderr in children:
   code=child.wait();stdout.close();stderr.close();observed.append({'group':group,'pid':child.pid,'exit_code':code,'terminal_observed':True})
  reports=[json.loads((output/group/'tests.json').read_bytes()) for group in GROUPS];events=[]
  for group in GROUPS:events += json.loads((output/group/'wire-observations.json').read_bytes())
  methods=[name for report in reports for name in report['methods']];success=all(report['result']=='PASS' and report['owned_fixture_root_removed'] for report in reports) and all(row['exit_code']==0 for row in observed) and len(methods)==len(set(methods))==34
  write(output/'tests.json',{'result':'PASS' if success else 'FAIL','tests_run':sum(report['tests_run'] for report in reports),'errors':sum(report['errors'] for report in reports),'failures':sum(report['failures'] for report in reports),'methods':methods,'children':observed,'source_sha256':a.source_sha256,'profile_sha256':a.profile_sha256,'owned_fixture_root_removed':all(report['owned_fixture_root_removed'] for report in reports),'actual_original_assertions_retained':True,'fixture_dependency_correction':'Explicit selected privacy import and copied caller messages; all 34 original tests executed exactly once across five isolated current grants','authority_effect':'none','actual_owner_outcome':None,'task_complete':False})
  write(output/'wire-observations.json',events);print(json.dumps({'result':'PASS' if success else 'FAIL','tests':len(methods),'processes':len(observed)}),flush=True);return 0 if success else 1
 name='_cal_api_v16';spec=importlib.util.spec_from_file_location(name,base/'__init__.py',submodule_search_locations=[str(base)])
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 original=__import__(name+'.run_session_checks',fromlist=['Sessions']);workspace=__import__(name+'.workspace',fromlist=['privacy']);original.PROFILE=a.profile_sha256
 class CorrectedSessions(original.Sessions):
  def opening(self,*,key=None):return copy.deepcopy(super().opening(key=key))
  def test_28_no_short_memory_in_any_recorded_reply(self):
   for row in self.events:workspace.privacy(row['reply']);original.D.EL.no_private_memory(row['reply'])
 names=unittest.defaultTestLoader.getTestCaseNames(CorrectedSessions);assert len(names)==34
 selected=[n for n in names if int(n.split('_')[1]) in GROUPS[a.shard]]
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(CorrectedSessions(n) for n in selected));output=HERE/'receipts/0001'/a.shard
 events=getattr(CorrectedSessions,'events',[])
 for row in events:workspace.privacy(row['reply']);original.D.EL.no_private_memory(row['reply'])
 write(output/'tests.json',{'result':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'methods':selected,'owned_fixture_root_removed':not getattr(CorrectedSessions,'root',HERE).exists(),'authority_effect':'none','actual_owner_outcome':None,'task_complete':False})
 write(output/'wire-observations.json',events);return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
