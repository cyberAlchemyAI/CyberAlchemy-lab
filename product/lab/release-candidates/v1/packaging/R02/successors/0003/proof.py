"""Before/after source guards, real subprocesses, immutable candidate proof receipt."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"0001"))
from common import *
from installer import *
import subprocess
from tempfile import TemporaryDirectory
CONTROL=Path(__file__).resolve().parent;HERE=CONTROL.parents[1];ROOT=HERE.parents[5];OUT=HERE/'packages/0003'

def guard(pin):
 raw=read(CONTROL/'source-manifest.json');need(sha(raw)==pin,'independent source manifest pin mismatch');v=parse(raw)
 for b in v['files']:need(sha(read(ROOT/b['path']))==b['sha256'],'frozen source changed: '+b['path'])
 for control in [HERE,CONTROL.parent/'0001',CONTROL.parent/'0002',CONTROL]:
  names={b['path'] for b in v['files'] if Path(b['path']).parent==control.relative_to(ROOT) and Path(b['path']).name!='source-manifest.json'}
  actual={p.relative_to(ROOT).as_posix() for p in control.iterdir() if p.is_file() and p.name!='source-manifest.json'}
  need(names==actual,'selected control source closure differs')
 return v

def run(pin):
 need({n:importlib.metadata.version(n) for n in VERSIONS}==VERSIONS,'selected regression dependency environment required')
 manifest=guard(pin);package_pin=manifest['package_binding']['sha256'];observations=[];checks={};files=list(manifest['files'])+[{'path':str((CONTROL/'source-manifest.json').relative_to(ROOT)),'sha256':pin}]
 def observed(name,cmd,timeout=240):
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout);row={'name':name,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr};observations.append(row);emit(CONTROL/('attempts/0001/'+name+'.json'),row);return p
 with TemporaryDirectory(prefix='cal-R02-install-proof-') as temp:
  root=Path(temp);scope=OwnedScope(str(root));old=root/'old-code';new=root/'new-code'
  # Actual hard exits at durable stage and after publish, followed by retry.
  command='import sys;sys.path.insert(0,sys.argv[1]);from installer import *;install(sys.argv[2],sys.argv[3],sys.argv[4],OwnedScope(sys.argv[5]),crash_at=sys.argv[6])'
  args=[sys.executable,'-I','-S','-c',command,str(HERE),str(OUT),package_pin,str(old),str(root)]
  p=observed('install-after-stage',args+['after-stage']);need(p.returncode==75,'stage crash did not occur');checks['install_stage_interruption']=True
  stage=root/('.old-code.install-'+package_pin);need(stage.is_dir() and not old.exists(),'stage not retained');checks['durable_stage_retained']=True
  p=observed('install-after-publish',args+['after-publish']);need(p.returncode==76,'publish crash did not occur');checks['published_retry_interruption']=True
  result=install(OUT,package_pin,old,scope);need(result['idempotent'],'published retry not idempotent');checks['cold_idempotent_install_retry']=True
  result2=install(OUT,package_pin,new,scope);need(tree(old)==tree(new),'fresh installations differ');checks['two_byte_identical_fresh_installations']=True
  import tests
  negative_count=tests.run(OUT,package_pin);checks['all_26_packaging_guards']=negative_count==26
  launcher=new/'repo'/HERE.relative_to(ROOT)/'installed.py'
  p=observed('selected-environment-transition-regression',[sys.executable,'-I','-S',str(launcher),'test_transition.py',str(ROOT),'-v'],timeout=600);need(p.returncode==0,'installed transition regression failed')
  import re
  count=int(re.search(r'Ran (\d+) tests',p.stderr).group(1));checks['selected_environment_transition_regression']=True
  state=root/'state';state.mkdir(mode=0o700)
  p=observed('installed-upgrade-export-recovery-rollback',[sys.executable,'-I','-S',str(launcher),'scenario.py',str(state),str(OUT),package_pin,str(old),str(ROOT)],timeout=480);need(p.returncode==0,'installed lifecycle proof failed');scenario=parse(p.stdout);checks.update(scenario['checks'])
  # Persist only public terminal observations and scoped facts; remove all
  # fixture installations, private keys, branches and memory before receipt.
  scenario['owned_fixture_removed_after_terminal']=True
 need(not root.exists(),'owned fixture cleanup failed');checks['owned_keys_stores_sessions_removed']=True
 guard(pin)
 need(all(checks.values()),'false acceptance check')
 report={'schema_version':'lab-R02-terminal-observations/v1-candidate','result':'PASS','authority_effect':'none','actual_owner_outcome':None,'packaging_guards':negative_count,'transition_regression_checks':count,'checks':checks,'observations':observations,'scenario':scenario,'installation':result2,'owned_fixture_removed':True}
 report_path=CONTROL/'proof/0001/terminal-observations.json';emit(report_path,report);files.append({'path':str(report_path.relative_to(ROOT)),'sha256':sha(read(report_path))})
 receipt={'schema_version':'lab-R02-verification-receipt/v1-candidate','task':'R02','result':'PASS','task_complete':True,'authority_effect':'none','actual_owner_outcome':None,'actual_admitted_operation':False,'package_binding':manifest['package_binding'],'source_manifest_binding':{'path':str((CONTROL/'source-manifest.json').relative_to(ROOT)),'sha256':pin},'environment':manifest['environment'],'checks':checks,'counts':{'packaging_guards':negative_count,'transition_regressions':count,'integration_acceptance':len(checks),'actual_terminal_processes':len(observations)},'files':sorted(files,key=lambda b:b['path']),'final_assembly_obligations':['R03 complete product operation payload and all API conformance','S02 exact owner/registry/environment/profile/release postimages and independent effect scopes','R08 actual human owner resolution and AC12 pilot','A01-A04 admitted operation and release; no candidate promotion inferred'],'claim_ceiling':'Original R02 isolated candidate install/upgrade/export/recovery/rollback criteria only. No complete product API, owner admission, global activation, publication or stable release.'}
 emit(CONTROL/'receipts/0001.json',receipt);print(json.dumps({'result':'PASS','checks':receipt['counts'],'files':len(files),'receipt_sha256':sha(read(CONTROL/'receipts/0001.json'))}))
if __name__=='__main__':run(sys.argv[1])
