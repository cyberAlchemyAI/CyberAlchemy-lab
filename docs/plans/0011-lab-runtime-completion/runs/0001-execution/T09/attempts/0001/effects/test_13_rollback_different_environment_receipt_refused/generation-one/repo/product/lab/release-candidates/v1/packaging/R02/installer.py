"""Explicit owned candidate installation, recovery and exact scoped public export."""
import base64, fcntl, os, stat, zipfile
from dataclasses import dataclass
from pathlib import Path
from common import *
@dataclass(frozen=True)
class OwnedScope:
 root: str
 def destination(self,p):
  root=Path(self.root);dest=Path(p)
  need(root.is_absolute() and str(root.resolve())==self.root and root.is_dir(),'owned scope root required')
  info=root.stat();need(info.st_uid==os.geteuid() and stat.S_IMODE(info.st_mode)&0o077==0,'candidate parent must be privately owned')
  need(dest.is_absolute() and dest.parent==root and dest.name not in ('','..','.'),'destination outside owned candidate scope')
  need(not any(x.is_symlink() for x in [root,*root.parents,dest]),'destination symlink');return dest

def package_bytes(package,pin):
 package=Path(package);raw=read(package/'selection.json');need(sha(raw)==pin,'independent package pin mismatch');v=parse(raw)
 need(set(v)=={'schema_version','authority_effect','actual_owner_outcome','environment','snapshot_sha256','wheels','versions','limitations'},'closed package selection')
 need(v['schema_version']=='lab-R02-installation-package/v1-candidate' and v['authority_effect']=='none' and v['actual_owner_outcome'] is None,'candidate package required')
 environment_guard(v['environment']);need(v['versions']==VERSIONS,'unselected dependency versions')
 raw=read(package/'payload.snapshot');need(sha(raw)==v['snapshot_sha256'],'package source bytes changed');files={'repo/'+n:b for n,b in payload(raw).items()}
 for row in v['wheels']:
  need(set(row)=={'filename','sha256','distribution','version'},'closed wheel binding');relative(row['filename']);need('/' not in row['filename'],'wheel filename required')
  wheel=package/'wheels'/row['filename'];need(sha(read(wheel))==row['sha256'],'wheel digest differs')
  with zipfile.ZipFile(wheel) as z:
   need(len(set(z.namelist()))==len(z.namelist()),'duplicate wheel path')
   for info in z.infolist():
    if info.is_dir():continue
    n=relative(info.filename);need('.data/' not in n and not n.endswith('.pth'),'unselected wheel installer hook')
    need(stat.S_IFMT(info.external_attr>>16)!=stat.S_IFLNK,'wheel symlink')
    n='deps/'+n;need(n not in files,'dependency file collision');files[n]=z.read(info)
 need({r['distribution']:r['version'] for r in v['wheels']}==VERSIONS and len(v['wheels'])==len(VERSIONS),'exact dependency closure required')
 need(set(p.name for p in (package/'wheels').iterdir())=={r['filename'] for r in v['wheels']},'unselected wheel')
 files['selection.json']=encoded(v);return v,files

def tree(path):
 result={}
 for p in Path(path).rglob('*'):
  need(not p.is_symlink(),'installed symlink')
  if p.is_file():result[p.relative_to(path).as_posix()]=read(p)
 return result

def verify_install(path,package,pin):
 _,expected=package_bytes(package,pin);actual=tree(path);need(actual==expected,'installed original-byte/file closure differs');return {'package_sha256':pin,'files':len(actual),'bytes':sum(map(len,actual.values()))}

def write_files(path,files):
 path.mkdir(mode=0o700)
 for n,b in sorted(files.items()):
  relative(n);p=path/n;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
  with p.open('xb') as f:os.chmod(p,0o600);f.write(b);f.flush();os.fsync(f.fileno())
 for p in [path]+[q for q in path.rglob('*') if q.is_dir()]:
  fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:os.fsync(fd)
  finally:os.close(fd)

def install(package,pin,destination,scope,*,crash_at=None):
 need(crash_at in (None,'after-stage','after-publish'),'unknown installation hook');dest=scope.destination(destination)
 _,files=package_bytes(package,pin)
 fd=os.open(dest.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 lock=os.open(dest.parent/'.candidate-install.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
 try:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  need(os.path.realpath('/proc/self/fd/'+str(fd))==str(dest.parent),'destination parent moved')
  if os.path.lexists(dest):
   result=verify_install(dest,package,pin);return dict(result,idempotent=True,recovered=False)
  stage=dest.parent/('.'+dest.name+'.install-'+pin)
  recovered=os.path.lexists(stage)
  if recovered:verify_install(stage,package,pin)
  else:write_files(stage,files)
  if crash_at=='after-stage':os._exit(75)
  # Recheck every original input and staged output before atomic publication.
  verify_install(stage,package,pin);publish(fd,stage.name,dest.name)
  if crash_at=='after-publish':os._exit(76)
  return dict(verify_install(dest,package,pin),idempotent=False,recovered=recovered)
 finally:os.close(lock);os.close(fd)

def export_legacy(reader,destination,scope):
 from lab_runtime.transition import committed_files
 data=reader.verify_full();bindings=committed_files(reader,data)
 # The exact baseline is protected history, never public Session material.
 files={n:read(reader.path/n) for n in bindings if n!='baseline.json'}
 need(all(sha(b)==bindings[n] for n,b in files.items()),'committed branch changed')
 need(committed_files(reader,reader.verify_full())==bindings,'branch changed during export')
 return export_files(files,destination,scope)

def export_successor(path,pins,policy,destination,scope):
 from lab_runtime.transition import replay_successor
 verified=replay_successor(path,pins,policy);files={n:b for n,b in tree(path).items() if n!='baseline.json'}
 need(replay_successor(path,pins,policy)==verified,'successor changed during export')
 return export_files(files,destination,scope)

def _key_guard(raw):
 need(not re.search(rb'-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----\r?\n',raw),'private key archive')
 if raw.lstrip().startswith((b'{',b'[')):
  def walk(v,schema=False):
   if isinstance(v,dict):
    if not schema:need(not ({'private_key','private_key_bytes'} & set(v)),'private key archive')
    for k,x in v.items():
     if k in ('byte_contents','control_bytes','executable_byte_contents') and isinstance(x,dict):
      for n,b in x.items():
       if k!='control_bytes':relative(n)
       _key_guard(base64.b64decode(b,validate=True))
     else:walk(x,schema or k in ('properties','$defs','definitions'))
   elif isinstance(v,list):
    for x in v:walk(x,schema)
  walk(parse(raw))

def _archive_files(files,destination,scope):
 dest=scope.destination(destination);need(not os.path.lexists(dest),'protected archive exists')
 for n,b in files.items():
  relative(n)
  if n=='baseline.json':_key_guard(b)
  else:privacy(b)
 raw=encoded(snapshot(files));fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 return {'sha256':sha(raw),'files':len(files),'visibility':'local-protected-history','authority_effect':'none','active_session_restored':False}

def archive_legacy(reader,destination,scope):
 from lab_runtime.transition import committed_files
 data=reader.verify_full();bindings=committed_files(reader,data);files={n:read(reader.path/n) for n in bindings}
 need(all(sha(b)==bindings[n] for n,b in files.items()) and committed_files(reader,reader.verify_full())==bindings,'archive cut changed')
 return _archive_files(files,destination,scope)

def archive_successor(path,pins,policy,destination,scope):
 from lab_runtime.transition import replay_successor
 data=replay_successor(path,pins,policy);files=tree(path)
 need(replay_successor(path,pins,policy)==data,'archive cut changed');return _archive_files(files,destination,scope)

def export_files(files,destination,scope):
 dest=scope.destination(destination);need(not os.path.lexists(dest),'export destination exists')
 for n,b in files.items():relative(n);privacy(b)
 raw=encoded(snapshot(files));fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 return {'sha256':sha(raw),'files':len(files),'bytes':sum(map(len,files.values())),'authority_effect':'none','session_restored':False}

def restore(archive,pin,destination,scope,*,crash_at=None):
 dest=scope.destination(destination);raw=read(archive);need(sha(raw)==pin,'independent recovery archive pin mismatch');files=payload(raw)
 for n,b in files.items():privacy(b)
 stage=dest.parent/('.'+dest.name+'.recover-'+pin)
 if os.path.lexists(dest):need(tree(dest)==files,'recovery cannot overwrite existing history');return {'idempotent':True}
 if os.path.lexists(stage):need(tree(stage)==files,'incomplete recovery retained')
 else:write_files(stage,files)
 if crash_at=='after-stage':os._exit(75)
 need(crash_at in (None,'after-stage'),'unknown recovery hook');need(sha(read(archive))==pin and tree(stage)==files,'recovery source/output changed')
 fd=os.open(dest.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:publish(fd,stage.name,dest.name)
 finally:os.close(fd)
 return {'idempotent':False,'session_restored':False,'authority_effect':'none'}

def _restore_verified_history(archive,pin,destination,scope,validator,*,crash_at=None):
 dest=scope.destination(destination);raw=read(archive);need(sha(raw)==pin,'independent protected archive pin mismatch');files=payload(raw)
 for n,b in files.items():
  if n=='baseline.json':_key_guard(b)
  else:privacy(b)
 stage=dest.parent/('.'+dest.name+'.recover-'+pin)
 if os.path.lexists(dest):
  need(tree(dest)==files,'protected recovery cannot overwrite history');validator(dest);return {'idempotent':True,'active_session_restored':False}
 if os.path.lexists(stage):need(tree(stage)==files,'incomplete protected recovery retained')
 else:write_files(stage,files)
 validator(stage)
 need(crash_at in (None,'after-stage'),'unknown protected recovery hook')
 if crash_at=='after-stage':os._exit(75)
 need(sha(read(archive))==pin and tree(stage)==files,'protected archive changed during replay')
 fd=os.open(dest.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:publish(fd,stage.name,dest.name)
 finally:os.close(fd)
 return {'idempotent':False,'active_session_restored':False,'visibility':'local-protected-history','authority_effect':'none'}

def restore_legacy(archive,pin,destination,scope,repository,executable_repo,pins,*,crash_at=None):
 from lab_runtime.store import VerifiedLegacyReadStore
 from lab_runtime.transition import committed_files
 def validator(path):
  reader=VerifiedLegacyReadStore(path,repository,executable_repo,pins);data=reader.verify_full()
  need(set(tree(path))==set(committed_files(reader,data)),'unselected protected history file')
 return _restore_verified_history(archive,pin,destination,scope,validator,crash_at=crash_at)

def restore_successor(archive,pin,destination,scope,pins,policy):
 from lab_runtime.transition import replay_successor
 return _restore_verified_history(archive,pin,destination,scope,lambda path:replay_successor(path,pins,policy))
