import pathlib,os,sys,json,hashlib,unittest,tempfile
from unittest.mock import patch
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab');C=R/'implementation/lab-runtime/local-host/reader-only-unified-0002'
def sha(b):return hashlib.sha256(b).hexdigest()
fraw=(C/'freeze.json').read_bytes();f=json.loads(fraw)
def verify():
 for row in f['file_bindings']:
  raw=(R/row['path']).read_bytes()
  if sha(raw)!=row['sha256'] or len(raw)!=row['size']:raise RuntimeError('freeze drift')
verify();allowed={"import sys;sys.stdout.write('x'*100);sys.stderr.write('y'*100)","print('would-be-log')","import sys;sys.stdout.write('x'*100000)"};children=[]
def guard(event,args):
 if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)) and os.fsdecode(args[0]).endswith('branch.snapshot'):raise RuntimeError('archive open prohibited')
 if event in ('subprocess.Popen','os.posix_spawn'):
  argv=args[1]
  if len(argv)!=4 or argv[0]!=sys.executable or list(argv[1:3])!=['-B','-c'] or argv[3] not in allowed:raise RuntimeError('nonfixture process prohibited')
  children.append(event)
 if event in ('os.system','os.fork'):raise RuntimeError('launch prohibited')
sys.addaudithook(guard);sys.path.insert(0,str(C));import controller as c,test_controller as tc,test_reader_once as tr
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(tc),unittest.defaultTestLoader.loadTestsFromModule(tr)])
result=unittest.TextTestRunner(verbosity=2).run(suite)
obs=[]
def refusal(name,fn):
 try:fn()
 except (ValueError,OSError):obs.append({'case':name,'refused':True});return
 raise RuntimeError('unexpected acceptance '+name)
with tempfile.TemporaryDirectory(prefix='unified2-review-') as temp:
 root=pathlib.Path(temp);root.chmod(0o700);(root/'evidence').mkdir()
 (root/'evidence/stage-terminal.json').write_bytes((c.STAGE/'evidence/stage-terminal.json').read_bytes())
 (root/'consumed.json').write_bytes((c.STAGE/'consumed.json').read_bytes())
 with patch.object(c,'STAGE',root):
  c.stage_provenance();obs.append({'case':'exact_neutral_positive','accepted':True})
  for location,kind in [('stage-unknown.json','file'),('stage-unknown.json','dangling'),('evidence/stage-unknown.json','file')]:
   target=root/location
   if kind=='file':target.write_text('{"overall":"UNKNOWN"}')
   else:target.symlink_to('missing-target')
   refusal(location+'_'+kind,c.stage_provenance);target.unlink()
 stage=root/'stage';stage.mkdir(mode=0o755);stage.chmod(0o755)
 name=c.SOURCE+'/packages/0001/period.json';dirs=c.expected_directories({name})
 for directory in sorted(dirs,key=lambda x:(len(pathlib.Path(x).parts),x)):
  p=stage/directory;p.mkdir(exist_ok=True);p.chmod(0o700 if directory==c.SOURCE+'/receipts' or directory.startswith(c.SOURCE+'/packages') else 0o755)
 leaf=stage/name;leaf.write_bytes(b'owned synthetic period');leaf.chmod(0o600);plan={name:{'path':name,'sha256':c.sha(leaf.read_bytes()),'target_mode':'0600'}}
 def verify_stage():c.verify_stage_metadata(stage,plan,dirs)
 verify_stage();obs.append({'case':'metadata_positive','accepted':True})
 leaf.chmod(0o777);refusal('same_bytes_bad_mode',verify_stage);leaf.chmod(0o600)
 link=root/'link';link.hardlink_to(leaf);refusal('same_bytes_second_hardlink',verify_stage);link.unlink()
 parent=leaf.parent;parent.chmod(0o777);refusal('private_dir_bad_mode',verify_stage);parent.chmod(0o700)
 held=root/'moved';parent.rename(held);parent.symlink_to(held,target_is_directory=True);refusal('ancestor_symlink',verify_stage);parent.unlink();held.rename(parent)
 original_read=os.read;swapped=[]
 def read(fd,*args):
  if not swapped and os.fstat(fd).st_ino==leaf.stat().st_ino:
   parent.rename(held);parent.mkdir(mode=0o700);(parent/'period.json').write_bytes(b'owned synthetic period');(parent/'period.json').chmod(0o600);swapped.append(True)
  return original_read(fd,*args)
 with patch.object(c.os,'read',read):refusal('ancestor_replaced_while_leaf_held',verify_stage)
 (parent/'period.json').unlink();parent.rmdir();held.rename(parent);verify_stage()
verify();print(json.dumps({'freeze_sha256':sha(fraw),'tests':result.testsRun,'passed':result.wasSuccessful(),'post_verified':True,'observations':obs,'local_public_stream_process_events':len(children),'archive_opened':False,'Docker_Reader_effect':'NOT_RUN'},sort_keys=True));sys.exit(0 if result.wasSuccessful() else 1)
