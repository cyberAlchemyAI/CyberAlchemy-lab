import sys,pathlib,hashlib,json,unittest,tempfile,os,datetime as dt
from unittest.mock import patch
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab');C=R/'implementation/lab-runtime/local-host/fresh-reader-docker-0007'
def sha(b):return hashlib.sha256(b).hexdigest()
fraw=(C/'freeze.json').read_bytes();freeze=json.loads(fraw)
def verify():
 for r in freeze['file_bindings']:
  b=(R/r['path']).read_bytes()
  if len(b)!=r['size'] or sha(b)!=r['sha256']:raise RuntimeError('freeze drift')
verify()
def guard(event,args):
 if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
  n=os.fsdecode(args[0])
  if n.endswith('branch.snapshot') and (n.startswith('/tmp/cal-') or n.startswith(str(R))):raise RuntimeError('real archive open prohibited')
 if event in ('subprocess.Popen','os.system','os.fork','os.posix_spawn'):raise RuntimeError('process effect prohibited')
sys.addaudithook(guard);sys.path.insert(0,str(C))
import test_inert,test_stage_only,stage_only as S
real_copy=S.copy_exact
def safe_copy(source,*args,**kwargs):
 if str(source).startswith('/tmp/cal-source-only-') and str(source).endswith('branch.snapshot'):raise RuntimeError('actual archive copy prohibited')
 return real_copy(source,*args,**kwargs)
S.copy_exact=safe_copy
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(m) for m in (test_inert,test_stage_only)])
result=unittest.TextTestRunner(verbosity=2).run(suite)
obs=[]
with tempfile.TemporaryDirectory(prefix='review-reader-stage-') as temp:
 base=pathlib.Path(temp);source,plan,archive=test_stage_only.StageOnlyTests.fixture(base);attempt=base/'attempt'
 clock=[dt.datetime(2026,10,21,8,19,59,tzinfo=dt.timezone.utc)];end=dt.datetime(2026,10,21,8,20,tzinfo=dt.timezone.utc)
 real_period=S.period_current;real_write=S.write_exact
 def selected_period(value):real_period(value,now=clock[0])
 def late_write(path,raw):
  if pathlib.Path(path).name=='stage-terminal.json':clock[0]=end
  return real_write(path,raw)
 with patch.object(S,'STAGE_RELEASE_ENABLED',True),patch.object(S,'ATTEMPT',attempt),patch.object(S,'SOURCE_ROOT',source),patch.object(S,'preflight',return_value={}),patch.object(S,'selected_plan',return_value=(plan,archive)),patch.object(S,'audit',return_value={'result':'PASS_INERT'}),patch.object(S,'period_current',side_effect=selected_period),patch.object(S,'write_exact',side_effect=late_write):
  refused=False
  try:S.execute(attempt=attempt)
  except ValueError:refused=True
 terminal=json.loads((attempt/'evidence/stage-terminal.json').read_bytes())
 obs.append({'case':'expiry_during_terminal_persistence','refused':refused,'retained_terminal':terminal['overall'],'clock_at_return':clock[0].isoformat(),'expiry':end.isoformat(),'observation_only':terminal['observation_only'],'reader_input_released':terminal['reader_input_released'],'unknown_precedence':terminal['unknown_receipt_takes_precedence'],'unknown_present':(attempt/'stage-unknown.json').exists(),'fixture_only':True})
with tempfile.TemporaryDirectory(prefix='review-reader-stage-') as temp:
 base=pathlib.Path(temp);source,plan,archive=test_stage_only.StageOnlyTests.fixture(base);attempt=base/'attempt';p=plan[archive];plan[archive]=(p[0],'0'*64,p[2],p[3]);failed=False
 with patch.object(S,'STAGE_RELEASE_ENABLED',True),patch.object(S,'ATTEMPT',attempt),patch.object(S,'SOURCE_ROOT',source),patch.object(S,'preflight',return_value={}),patch.object(S,'selected_plan',return_value=(plan,archive)):
  try:S.execute(attempt=attempt)
  except ValueError:failed=True
 obs.append({'case':'current_synthetic_archive_digest_mismatch','refused':failed,'marker_retained':(attempt/'consumed.json').exists(),'unknown':json.loads((attempt/'stage-unknown.json').read_bytes())['overall'],'pass_absent':not(attempt/'evidence/stage-terminal.json').exists(),'original_bytes_unchanged':(source/archive).read_bytes()==b'synthetic private archive, no historical bytes'})
with tempfile.TemporaryDirectory(prefix='review-reader-stage-') as temp:
 base=pathlib.Path(temp);source,plan,archive=test_stage_only.StageOnlyTests.fixture(base);attempt=base/'attempt'
 role=next(n for n in plan if n.endswith('base.py'));real_write=S.write_exact;raised=None
 def mutate_after_neutral(path,raw):
  if pathlib.Path(path).name=='stage-unknown.json':raise OSError('synthetic unknown receipt failure')
  answer=real_write(path,raw)
  if pathlib.Path(path).name=='stage-terminal.json':
   dest=attempt/'root'/role;dest.chmod(0o644);dest.write_bytes(b'changed synthetic role');dest.chmod(0o444)
  return answer
 with patch.object(S,'STAGE_RELEASE_ENABLED',True),patch.object(S,'ATTEMPT',attempt),patch.object(S,'SOURCE_ROOT',source),patch.object(S,'preflight',return_value={}),patch.object(S,'selected_plan',return_value=(plan,archive)),patch.object(S,'audit',return_value={'result':'PASS_INERT'}),patch.object(S,'write_exact',side_effect=mutate_after_neutral):
  try:S.execute(attempt=attempt)
  except BaseException as err:raised=err
 neutral=json.loads((attempt/'evidence/stage-terminal.json').read_bytes())
 obs.append({'case':'post_receipt_mutation_and_unknown_write_failure','refused':isinstance(raised,ValueError),'neutral':neutral['overall'],'reader_input_released':neutral['reader_input_released'],'external_exit_required':neutral['requires_external_exit_zero_and_fresh_reader_attachment_check'],'unknown_absent':not(attempt/'stage-unknown.json').exists(),'marker_retained':(attempt/'consumed.json').exists(),'secondary_failure_noted':any('UNKNOWN receipt write failed' in n for n in raised.__notes__)})
verify();print(json.dumps({'freeze_sha256':sha(fraw),'frozen_members':len(freeze['file_bindings']),'tests':result.testsRun,'passed':result.wasSuccessful(),'observations':obs,'actual_archive_body_opened':False,'effect':'NOT_RUN','post_verified':True},sort_keys=True));sys.exit(0 if result.wasSuccessful() else 1)
