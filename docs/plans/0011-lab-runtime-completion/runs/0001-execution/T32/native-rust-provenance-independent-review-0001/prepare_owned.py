"""UNRUN Root setup recipe only: exact locked cache into a new owned root.

No Cargo/compiler/native/Source guard. Stop and retain every partial on failure.
Root independently selects this script SHA before future execution.
"""
import argparse,hashlib,json,os,stat,sys,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
P=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-rust-provenance-preparation-0001'
CONTROL=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-performance-preparation-0001/control.py'
CONTROL_PIN='a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd'
PINS={'input-selection.json':'e22e042a6a9f9c3174b85c6b173a711ff9d9e0961c940ba4d946ff9f61b4644d','offline-cache-selection.json':'4a193850e99f38143637f4e4e5d7b0d55a4e801840647f24eb5bc12cf28908e2','ROOT-COMMAND-PROPOSAL.json':'ab91688ab8ad0c581447b310a7bbc9ab6e7609a5508938398eb11301fe7e0e67'}
OWNED=Path('/tmp/cal-T32-rust-provenance-root-0001')
def need(v,why):
 if not v:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def path_for(row):
 p=Path(row['path']);return p if p.is_absolute()else ROOT/p

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--setup-sha256',required=True);args=parser.parse_args()
 install=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
 need(Path(sys.executable)==install/'bin/python'and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'selected0004 isolated -B -S setup required')
 # Bootstrap consumes exact selected helper bytes, then anchored recaptures the
 # helper itself before any owned write. installed()/other guards are not called.
 raw=CONTROL.read_bytes();need(sha(raw)==CONTROL_PIN,'reviewed capture helper differs')
 m=types.ModuleType('_T32_rust_setup_selected_control');m.__file__=str(CONTROL)
 exec(compile(raw,str(CONTROL),'exec'),m.__dict__);need(m.capture(CONTROL,CONTROL_PIN)==raw,'helper attachment changed')
 m.capture(Path(__file__).absolute(),args.setup_sha256,limit=1024*1024)
 selected={name:json.loads(m.capture(P/name,pin))for name,pin in PINS.items()}
 inputs=selected['input-selection.json'];cache=selected['offline-cache-selection.json'];proposal=selected['ROOT-COMMAND-PROPOSAL.json']
 need(len(inputs['files'])==110 and cache['package_count']==len(cache['packages'])==32,'exact reviewed110/32 required')
 def guard_inputs():
  for row in inputs['files']:m.capture(path_for(row),row['sha256'],limit=64*1024*1024,size=row['size_bytes'])
 guard_inputs()
 need(proposal['owned_root']['path']==str(OWNED)and cache['fresh_CARGO_HOME']==str(OWNED/'cargo-home'),'exact reviewed new root required')
 # Explicitly account for all Cargo config ancestor candidates. For this recipe
 # any present config requires a separately selected successor; none is guessed.
 for parent in (ROOT,*ROOT.parents):
  for leaf in ('config','config.toml'):
   need(not os.path.lexists(parent/'.cargo'/leaf),'unselected Cargo configuration present')
 copies=[]
 for row in cache['packages']:
  copies += [(row['archive_destination'],row['archive_binding']),(row['index_destination'],row['index_binding'])]
 copies.append((cache['index_config']['destination'],cache['index_config']['source_binding']))
 need(len(copies)==65 and len({name for name,_ in copies})==65,'exact cache65 required')
 handles=[];links=[];rootfd=None
 identity=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode)
 def attachments():
  for parent,name,child,witness in links:
   need(identity(os.stat(name,dir_fd=parent,follow_symlinks=False))==identity(os.fstat(child))==witness,'owned setup ancestor detached')
 try:
  parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(parent)
  for name in OWNED.parts[1:-1]:
   child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child)
   links.append((parent,name,child,identity(os.fstat(child))));parent=child
  attachments();os.mkdir(OWNED.name,0o700,dir_fd=parent);os.fsync(parent)
  rootfd=os.open(OWNED.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(rootfd)
  links.append((parent,OWNED.name,rootfd,identity(os.fstat(rootfd))));attachments()
  s=os.fstat(rootfd);need(s.st_uid==os.getuid()and stat.S_IMODE(s.st_mode)==0o700,'fresh owned0700 root required')
  dirs={():rootfd}
  def directory(parts):
   if parts in dirs:return dirs[parts]
   parent=directory(parts[:-1]);attachments();os.mkdir(parts[-1],0o700,dir_fd=parent);os.fsync(parent)
   fd=os.open(parts[-1],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(fd)
   links.append((parent,parts[-1],fd,identity(os.fstat(fd))));dirs[parts]=fd;attachments();return fd
  def write(name,body):
   p=Path(name);need(not p.is_absolute()and p.as_posix()==name and '..'not in p.parts and p.parts,'closed output locator required')
   fd=directory(p.parts[:-1]);attachments();leaf=os.open(p.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=fd)
   try:
    offset=0
    while offset<len(body):
     count=os.write(leaf,body[offset:]);need(count>0,'short owned setup write');offset+=count
    os.fsync(leaf)
   finally:os.close(leaf)
   os.fsync(fd);attachments()
  for name in ('cargo-home','tmp','observations'):directory((name,))
  for name,binding in copies:
   raw=m.capture(path_for(binding),binding['sha256'],limit=64*1024*1024,size=binding['size_bytes'])
   write('cargo-home/'+name,raw)
   m.capture(OWNED/'cargo-home'/name,binding['sha256'],limit=64*1024*1024,size=binding['size_bytes'],owner=os.getuid(),mode=0o600)
  guard_inputs();attachments()
  for name in proposal['new_targets']:need(not os.path.lexists(name),'new Cargo targets must remain absent')
  write('commands.json',canonical(proposal['commands']))
  write('SETUP.json',canonical({'schema_version':'lab-T32-owned-rust-setup/v1-candidate','authority_effect':'none','setup_sha256':args.setup_sha256,'root':{'path':str(OWNED),'identity':[s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]},'inputs110_entry_exit':'PASS','locked_cache_files':65,'all_copied_sha_size_mode':'PASS','Cargo_compiler_native_or_Source_guards_executed':False,'all5_commands_unexecuted':True,'current_host_not_hermetic_build_provenance':True}))
  print(json.dumps({'result':'PREPARED-only','root':str(OWNED),'commands':str(OWNED/'commands.json'),'actual_commands_executed':0},sort_keys=True));return 0
 finally:
  # Only descriptors opened here are closed. No deletion or automatic rollback.
  for fd in reversed(handles):os.close(fd)
if __name__=='__main__':raise SystemExit(main())
