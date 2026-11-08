import sys, os, json, hashlib, types, unittest, io
from pathlib import Path
from unittest import mock
R=Path('/home/vlad_/projects/CyberAlchemy-lab')
L=R/'implementation/lab-runtime/local-host'
C=L/'mapper-successor-stage-adapter-0002'
OUT=Path(__file__).parent
H=lambda b:hashlib.sha256(b).hexdigest()
fraw=(C/'freeze.json').read_bytes()
if H(fraw)!='c4a15d25587623ec4b73408d2e3e51f767d0d33e4943262b491bae435eabef0e':raise RuntimeError('FREEZE')
rows=json.loads(fraw)['file_bindings']; pins={}
for row in rows:
 p=R/row['path'];raw=p.read_bytes()
 if H(raw)!=row['sha256'] or len(raw)!=row['size']:raise RuntimeError('MEMBER')
 pins[str(p)]={'sha256':H(raw),'size':len(raw)}
pins[str(C/'freeze.json')]={'sha256':H(fraw),'size':len(fraw)}
reads=set()
def audit(event,args):
 if event=='open' and isinstance(args[0],(str,bytes)):
  p=os.fsdecode(args[0])
  if Path(p).name=='branch.snapshot':raise RuntimeError('PRIVATE_ARCHIVE_FORBIDDEN')
  if p.startswith(str(R)) or p.startswith('/home/vlad_/.local/state/'):
   reads.add(p)
 if event in ('subprocess.Popen','os.system','os.exec','os.fork'):raise RuntimeError('EFFECT_FORBIDDEN')
sys.addaudithook(audit)
A=types.ModuleType('adapter');A.__file__=str(C/'adapter.py');sys.modules['adapter']=A
exec(compile((C/'adapter.py').read_bytes(),A.__file__,'exec'),A.__dict__)
T=types.ModuleType('author_tests');T.__file__=str(C/'test_adapter.py')
exec(compile((C/'test_adapter.py').read_bytes(),T.__file__,'exec'),T.__dict__)
suite=unittest.defaultTestLoader.loadTestsFromModule(T)
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():raise RuntimeError('AUTHOR_TESTS')
raws=A._actual_effect_bytes();stage=A.stage_basis(); checks=[]
# Coherently repin the altered original to reach each strict numeric check.
fields=[('external','os_exit_code','ACTUAL_EXTERNAL_SHA'),('review','os_exit_code','ACTUAL_REVIEW_SHA'),('final','client_exit','ACTUAL_FINAL_SHA'),('final','daemon_exit','ACTUAL_FINAL_SHA'),('create_response','returncode','ACTUAL_CREATE_RESPONSE_SHA'),('pre_removal','daemon_wait_exit','ACTUAL_PRE_REMOVAL_SHA')]
for role,field,const in fields:
 for invalid in (False,0.0):
  changed=dict(raws);v=A.parse(changed[role]);v[field]=invalid;changed[role]=A.encoded(v)
  patches={const:H(changed[role])}
  review=A.parse(changed['review'])
  join={'external':'external_observation_sha256','final':'final_sha256','create_response':'create_response_sha256','pre_removal':'pre_removal_sha256'}.get(role)
  if join:review[join]=H(changed[role]);changed['review']=A.encoded(review);patches['ACTUAL_REVIEW_SHA']=H(changed['review'])
  if role=='final':
   changed['stdout']=A.encoded(v);patches['ACTUAL_STDOUT_SHA']=H(changed['stdout'])
   ext=A.parse(changed['external']);ext['stdout_sha256']=patches['ACTUAL_STDOUT_SHA'];ext['stdout_size']=len(changed['stdout']);changed['external']=A.encoded(ext);patches['ACTUAL_EXTERNAL_SHA']=H(changed['external'])
   review=A.parse(changed['review']);review['external_observation_sha256']=patches['ACTUAL_EXTERNAL_SHA'];changed['review']=A.encoded(review);patches['ACTUAL_REVIEW_SHA']=H(changed['review'])
  with mock.patch.multiple(A,**patches):
   try:A._validated_actual_reader(changed,stage)
   except A.Refused as e:checks.append({'case':role+'.'+field+':'+type(invalid).__name__,'refusal':str(e)})
   else:raise RuntimeError('SCALAR_ACCEPTED')
selected=A.select_actual(now=T.NOW)
for key,name in [('stage_plan','stage-plan.json'),('copy_plan','copy-plan.json'),('verifier_plan','verifier-plan.json')]:
 if A.encoded(selected[key])!=(C/name).read_bytes():raise RuntimeError('PLAN_REGEN')
# Inventory directory metadata only, never open file contents.
root=Path(selected['stage_plan']['reader_stage_root']);dirs=[];stack=[root]
while stack:
 base=stack.pop()
 with os.scandir(base) as it:
  for ent in it:
   if ent.is_symlink():raise RuntimeError('STAGE_SYMLINK')
   if ent.is_dir(follow_symlinks=False):
    dirs.append(str(Path(ent.path).relative_to(root)));stack.append(Path(ent.path))
   if len(dirs)>4096:raise RuntimeError('DIRECTORY_LIMIT')
cp=selected['copy_plan'];target=set(cp['target_directory_names']);generated=next(k for k in selected['generated_mapper_bytes'] if k.endswith('/source-manifest.json')).rsplit('/',1)[0]
if len(dirs)!=931 or target!=set(dirs)|{generated,generated+'/packages'}:raise RuntimeError('EMPTY_DIRECTORY_CLOSURE')
for p,row in pins.items():
 raw=Path(p).read_bytes()
 if H(raw)!=row['sha256'] or len(raw)!=row['size']:raise RuntimeError('POST_DRIFT')
# Read trace inventory captures public originals/aggregate evidence only; private archive denied above.
for p in sorted(reads):
 q=Path(p)
 if q.is_file() and q.name!='branch.snapshot' and q.suffix!='.pyc':
  raw=q.read_bytes();pins[p]={'sha256':H(raw),'size':len(raw)}
report={'author_tests':result.testsRun,'independent_scalar_cases':checks,'directory_metadata_count':len(dirs),'plan_regeneration':'exact three originals','archive_body_opened':False,'effects':'none','pins':pins}
print(json.dumps(report,sort_keys=True,indent=2))
