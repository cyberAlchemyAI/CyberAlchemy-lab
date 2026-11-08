import sys,pathlib,hashlib,json,unittest,tempfile,os
from contextlib import contextmanager
from unittest.mock import patch
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab');C=R/'implementation/lab-runtime/local-host/reader-only-entrypoint-0003'
def sha(b):return hashlib.sha256(b).hexdigest()
fraw=(C/'freeze.json').read_bytes();f=json.loads(fraw)
def verify():
 for row in f['file_bindings']:
  raw=(C/row['path']).read_bytes()
  if sha(raw)!=row['sha256'] or len(raw)!=row['size']:raise RuntimeError('freeze drift')
verify()
def guard(event,args):
 if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)) and os.fsdecode(args[0]).endswith('branch.snapshot'):raise RuntimeError('archive open prohibited')
 if event in ('subprocess.Popen','os.system','os.fork','os.posix_spawn'):raise RuntimeError('process launch prohibited')
sys.addaudithook(guard);sys.path.insert(0,str(C));import reader_once as r,test_reader_once as t
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(t));obs=[]
with tempfile.TemporaryDirectory(prefix='entrypoint-review-') as temp:
 p=pathlib.Path(temp);realopen=os.open;realclose=os.close;opened=[];closed=[]
 def op(*a,**kw):
  fd=realopen(*a,**kw);opened.append(fd);return fd
 def cl(fd):
  closed.append(fd);realclose(fd)
  if len(closed)==1:raise KeyboardInterrupt('owned synthetic interrupt')
 try:
  with patch.object(r.os,'open',op),patch.object(r.os,'close',cl):
   with r.held_directory(p):pass
 except KeyboardInterrupt:pass
 remain=[]
 for fd in opened:
  try:os.fstat(fd)
  except OSError:continue
  remain.append(fd);realclose(fd)
 obs.append({'case':'held_chain_interrupt','opened':len(opened),'close_attempts':len(closed),'left_open':len(remain),'reviewer_closed_remaining':True})
 snapshot=p/'snapshot';snapshot.mkdir();(snapshot/'victim').write_bytes(b'owned old bytes');identity=(snapshot.stat().st_dev,snapshot.stat().st_ino);old=p/'retained-old';original_hold=r.held_directory;swapped=[]
 @contextmanager
 def swap_before_open(path):
  if path==snapshot and not swapped:
   snapshot.rename(old);snapshot.mkdir();(snapshot/'victim').write_bytes(b'foreign synthetic data');swapped.append(True)
  with original_hold(path) as chain:yield chain
 raised=None
 with patch.object(r,'held_directory',swap_before_open):
  try:r.cleanup_snapshot(snapshot,identity)
  except BaseException as err:raised=err
 obs.append({'case':'cleanup_root_replaced_after_initial_check','refused_eventually':isinstance(raised,ValueError),'foreign_fixture_deleted':not(snapshot/'victim').exists(),'original_retained':(old/'victim').read_bytes()==b'owned old bytes','only_owned_temp_fixtures':True})
# Exercise run's actual ROOT rewiring with public synthetic code/data, while
# substituting only the cold-open endpoint; no selected original role is imported.
fixture=t.SyntheticStage(methodName='runTest');fixture.setUp()
try:
 fixture.make_stage();host=fixture.root/'synthetic/public/filler-0000';original=host.read_bytes();seen=[]
 def fake_cold(*args):
  seen.append(str(r.ROOT));host.write_bytes(b'host mutation')
  try:
   data=r.regular(r.ROOT/'synthetic/public/filler-0000');assert data==original
   return {'result':'SYNTHETIC_ENDPOINT_ONLY','host_mutation_not_consumed':True}
  finally:host.write_bytes(original)
 with patch.object(r,'_run_sealed',side_effect=fake_cold):outcome=r.run()
 obs.append({'case':'run_snapshot_root_rewiring','stubbed_endpoint':True,'source_mutation_isolated':outcome['host_mutation_not_consumed'],'root_restored':r.ROOT==fixture.root,'snapshot_removed':not(fixture.snapshot_parent/r.SNAPSHOT_NAME).exists(),'cold_original_executed':False})
finally:fixture.doCleanups()
verify();print(json.dumps({'tests':result.testsRun,'passed':result.wasSuccessful(),'freeze_sha256':sha(fraw),'members':len(f['file_bindings']),'observations':obs,'actual_archive_opened':False,'effect':'NOT_RUN','post_verified':True},sort_keys=True));sys.exit(0 if result.wasSuccessful() else 1)
