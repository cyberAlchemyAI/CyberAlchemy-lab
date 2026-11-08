import os,sys,types,json,hashlib,tempfile
from pathlib import Path
from unittest import mock
from contextlib import ExitStack
R=Path('/home/vlad_/projects/CyberAlchemy-lab');C=R/'implementation/lab-runtime/local-host/mapper-successor-stage-0002';h=lambda b:hashlib.sha256(b).hexdigest()
f=(C/'freeze.json').read_bytes()
if h(f)!='c214e06c122186124a11f16e456257a1f800cfea8b05361da9d18247ece60311':raise RuntimeError('FREEZE')
pins={}
for r in json.loads(f)['file_bindings']:
 p=R/r['path'];b=p.read_bytes()
 if len(b)!=r['size'] or h(b)!=r['sha256']:raise RuntimeError('PIN')
 pins[str(p)]=h(b)
for name in ('anchored_copy','held_stage','stage'):
 m=types.ModuleType(name);m.__file__=str(C/(name+'.py'));sys.modules[name]=m;exec(compile(Path(m.__file__).read_bytes(),m.__file__,'exec'),m.__dict__)
S=sys.modules['stage'];H=sys.modules['held_stage'];results=[]
for case in ('final-close','consumed-write-close'):
 with tempfile.TemporaryDirectory(prefix='mapper-stage-finalization-') as d:
  home=Path(d);attempt=home/'attempt';native=home/'native';native.write_bytes(b'inert ELF stand-in');native.chmod(0o755)
  plan={'files':[],'reader_effect_review_sha256':'inert'}
  cp={'attempt':str(attempt),'destination_root':str(attempt/'root'),'target_directory_names':[],'native_copy_target':str(attempt/'input/lab-context-native-reader')}
  baseclose=H.HeldAttempt.close;basewrite=H.HeldAttempt.write;copied=[];basecopy=H.HeldAttempt.copy
  def failingclose(c,primary=None):
   baseclose(c,primary)
   raise OSError('inert after final owned closes')
  def failingwrite(c,relative,raw,**kw):
   r=basewrite(c,relative,raw,**kw)
   if relative=='consumed.json':raise OSError('inert marker close uncertainty')
   return r
  def countedcopy(c,*a,**kw):copied.append(a[1]);return basecopy(c,*a,**kw)
  with ExitStack() as x:
   for name,value in [('STAGE_EFFECT_ENABLED',True),('NATIVE',native),('NATIVE_SHA',h(native.read_bytes()))]:x.enter_context(mock.patch.object(S,name,value))
   for name,value in [('preflight',{}),('selected',(plan,cp,{})),('source_inventory',{}),('verify_stage',None)]:x.enter_context(mock.patch.object(S,name,return_value=value))
   x.enter_context(mock.patch.object(H.HeldAttempt,'copy',countedcopy))
   x.enter_context(mock.patch.object(H.HeldAttempt,'close' if case=='final-close' else 'write',failingclose if case=='final-close' else failingwrite))
   try:S.execute()
   except OSError:pass
   else:raise RuntimeError('UNCERTAIN_EXECUTE_RETURNED')
  if case=='final-close':
   term=json.loads((attempt/'evidence/stage-terminal.json').read_bytes())
   if term['overall']!='OBSERVED_STAGE_ONLY' or term['requires_external_exit_zero_and_independent_stage_review'] is not True:raise RuntimeError('AUTHORITATIVE_PREMATURE_TERMINAL')
   results.append({'case':case,'returned_success':False,'local_terminal':'OBSERVED_STAGE_ONLY; requires external exit zero and independent review','local_unknown_present':(attempt/'stage-unknown.json').exists()})
  else:
   if copied or json.loads((attempt/'stage-unknown.json').read_bytes())['overall']!='UNKNOWN':raise RuntimeError('DISCLOSURE_AFTER_UNCERTAIN_MARKER')
   results.append({'case':case,'returned_success':False,'copy_calls':0,'unknown_on_owned_attempt':True})
for p,digest in pins.items():
 if h(Path(p).read_bytes())!=digest:raise RuntimeError('DRIFT')
print(json.dumps({'results':results,'effect':'owned synthetic files only','private_archive':'never selected'},sort_keys=True,indent=2))
