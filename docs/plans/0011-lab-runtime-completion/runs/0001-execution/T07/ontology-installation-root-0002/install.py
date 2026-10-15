"""Root-only fresh827 installation; all prior installations and failures retained."""
import argparse,hashlib,importlib.util,json,os,stat,sys,tempfile,traceback,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
BASE=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
P=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/ontology-native-execution-preparation-0002'
PROPOSAL_PIN='b506322170257a5b44388ac0fa77bbed9302bc05f7e08f14a1f003ec8fe237b5'
MF_PIN='cec90b3efee6a949706bef250447db110da5d07a0bcfe88eae082be061eb7548'
CONTROL=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-performance-preparation-0001/control.py'
CONTROL_PIN='a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd'
SOURCE='ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1'
PROFILE='9c8c3018226abb9077c6a99ee3cbc9dd0174c148b332b9488fd4a3a9cd30418b'
DEP=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
MODULES={'checked_io':(DEP/'checked_io.py','cf9871b52b91842efed22f10484a2d9084ca7aeee59f91d2e9b6277f2f35fd12'),
 'stage_io':(DEP/'stage_io.py','d16ec83b02a052b975dfba3d96cf848d32f0f9f2d706fe83fab375cdfda112ec'),
 'closure':(DEP/'closure.py','cae6610064a8f105e6e7ee9bbd5a5a0e07af239b6b43221d7e8b011f0e261a0a'),
 'dependencies':(DEP/'closure_hardened_0003.py','00d785f95d675a9acdf644324e21653e09e8b889226d4092576fef937d600715'),
 'executor':(P/'native_executor.py','6dc340b7b533ef138963383340f6874d84950daab992126b04bd16ad17a58c9e'),
 'api_guard':(API/'guard.py','65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3')}
def need(value,why):
 if not value:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def emit(name,raw):
 fd=os.open(HERE/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  os.fchmod(fd,0o600);offset=0
  while offset<len(raw):
   count=os.write(fd,raw[offset:]);need(count>0,'short owned output write');offset+=count
  os.fsync(fd)
 finally:os.close(fd)
 parent=os.open(HERE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(parent)
 finally:os.close(parent)
def anchor(path):
 need(not any(p.is_symlink()for p in(path,*path.parents)),'owned path alias')
 s=path.lstat();need(stat.S_ISDIR(s.st_mode)and s.st_uid==os.getuid()and stat.S_IMODE(s.st_mode)==0o700,'owned0700 root required')
 return {'path':str(path),'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'mode':stat.S_IMODE(s.st_mode)}
def diagnostic():
 kind,error,tb=sys.exc_info();return {'exception_class':kind.__name__,'message':str(error),'frames':[{'path':f.filename,'line':f.lineno,'function':f.name}for f in traceback.extract_tb(tb)]}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--driver-sha256',required=True);args=parser.parse_args()
 need(Path(sys.executable)==BASE/'bin/python'and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'selected0004 isolated -B -S required')
 raw=CONTROL.read_bytes();need(sha(raw)==CONTROL_PIN,'exact reviewed capture helper required')
 control=types.ModuleType('_Root827_control');control.__file__=str(CONTROL);exec(compile(raw,str(CONTROL),'exec'),control.__dict__)
 need(control.capture(CONTROL,CONTROL_PIN)==raw,'bootstrap origin changed');control.capture(Path(__file__).absolute(),args.driver_sha256)
 proposal=json.loads(control.capture(P/'ROOT-PREPARE-PROVISION-PROPOSAL.json',PROPOSAL_PIN))
 rows=json.loads(control.capture(P/'source-manifest.json',MF_PIN))['files'];need(len(rows)==176,'whole176 proposal closure required')
 def inputs():
  for row in rows:
   path=Path(row['path']);path=path if path.is_absolute()else ROOT/path
   body=control.capture(path,row['sha256']);need(len(body)==row['size_bytes'],'selected176 size changed')
  control.capture(Path(__file__).absolute(),args.driver_sha256);control.capture(P/'source-manifest.json',MF_PIN);control.capture(P/'ROOT-PREPARE-PROVISION-PROPOSAL.json',PROPOSAL_PIN)
 def load(key):
  path,pin=MODULES[key];name=key if key in('checked_io','stage_io','closure')else '_Root827_'+key
  need(name not in sys.modules,'fresh true-origin module required');body=control.capture(path,pin)
  spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;exec(compile(body,str(path),'exec'),m.__dict__);return m
 sys.path.insert(0,str(BASE/'deps'))
 loaded={key:load(key)for key in('checked_io','stage_io','closure','dependencies','executor','api_guard')}
 deps=loaded['dependencies'];executor_module=loaded['executor'];guard=loaded['api_guard'];base=None;new=None;executor=None;result=None;failure=None;errors=[]
 fd0=len(os.listdir('/proc/self/fd'))
 try:
  inputs();guard.verify(SOURCE);control.capture(API/'contract-profile.json',PROFILE)
  base=anchor(BASE);need(base==proposal['base_anchor'],'original0004 anchor changed')
  selection_base,_=deps.load_selection(ROOT/proposal['base_dependency_selection_binding']['path'],proposal['base_dependency_selection_binding']['sha256'])
  deps.preflight(ROOT/proposal['base_dependency_selection_binding']['path'],proposal['base_dependency_selection_binding']['sha256']);deps.verify_installed(BASE,selection_base)
  newroot=Path(tempfile.mkdtemp(prefix='ontology-0002-',dir=BASE.parent));new=anchor(newroot);need(os.listdir(newroot)==[],'fresh empty root required')
  emit('started.json',encoded({'authority_effect':'none','base':base,'new_installation':new,'native_cases_run':False}))
  raw=executor_module.prepare_selection(proposal['added_sources'],base,new,proposal['module_bindings'],deps,control)
  emit('execution-selection.json',raw);pin=sha(raw)
  executor=executor_module.SelectedOntologyExecutor(raw,pin,deps,control)
  need(len(executor.expected)==1011 and len(executor.value['added_inputs'])==1,'whole1010 plus only827 required')
  result=executor_module.provision(executor);executor.guard()
  result.update({'selection_binding':{'path':str((HERE/'execution-selection.json').relative_to(ROOT)),'sha256':pin},'installation_receipt_binding':executor.value['installation_receipt_binding'],'installed_payloads':1011})
 except BaseException:failure=diagnostic()
 finally:
  def original_base():
   need(base is not None and anchor(BASE)==base,'original0004 anchor unproved');deps.preflight(ROOT/proposal['base_dependency_selection_binding']['path'],proposal['base_dependency_selection_binding']['sha256']);deps.verify_installed(BASE,selection_base)
  for label,fn in [('currentSource',lambda:guard.verify(SOURCE)),('profile',lambda:control.capture(API/'contract-profile.json',PROFILE)),('whole176',inputs),('strictOriginal720_77ELF_1010',original_base)]:
   try:fn()
   except BaseException:errors.append({'phase':label,**diagnostic()})
  if executor is not None:
   try:executor.guard()
   except BaseException:errors.append({'phase':'completeNew1011AndReceipt',**diagnostic()})
  delta=len(os.listdir('/proc/self/fd'))-fd0
  emit('result.json',encoded({'authority_effect':'none','result':result,'failure':failure,'exit_errors':errors,'FD_delta':delta,'new_installation':new,'partials_preserved':True,'native_cases_run':False,'whole_task_complete':False}))
 return 0 if failure is None and not errors and delta==0 else 1
if __name__=='__main__':raise SystemExit(main())
