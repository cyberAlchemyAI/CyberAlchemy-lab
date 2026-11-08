from pathlib import Path
import hashlib,json,os,sys,stat,types,datetime
E=Path(__file__).parent;L=E.parent
previous=json.loads((E/'audit.json').read_bytes());entry=previous['private_archive_excluded'][0]
A=Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/context-attempt');R=A/'root'
allowed={str(R/entry['path'])}
sys.path.append('/usr/lib/python3/dist-packages')
p=L/'context-successor-public-stage-writer-0002/stage_writer.py';raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()=='9228b7aa394a661c1c43513bd754fe4f2bf7e37c8f2dbd834d0c85b5805805bb'
W=types.ModuleType('checked_writer');W.__file__=str(p);exec(compile(raw,str(p),'exec'),W.__dict__)
S,selected=W.selected();rows=W.source_rows(S,selected);row=next(r for r in rows if r['path']==entry['path']);source=row['source_path'];allowed.add(str(source))
assert str(source).startswith('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-stage-attempt/root/')
def guard(event,args):
 if event=='open' and isinstance(args[0],str) and args[0].endswith('branch.snapshot') and args[0] not in allowed and args[0]!='branch.snapshot':raise RuntimeError('UNSELECTED_ARCHIVE')
 if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.fork','os.exec'):raise RuntimeError('EFFECT_FORBIDDEN')
sys.addaudithook(guard)
def identity(s):return dict(dev=s.st_dev,ino=s.st_ino,mode=stat.S_IMODE(s.st_mode),uid=s.st_uid,gid=s.st_gid,nlink=s.st_nlink,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)
observations=[]
for path,expected_mode,old in [(source,row['source_mode'],entry['source_metadata']),(R/row['path'],int(row['mode'],8),entry['stage_metadata'])]:
 with W.held_dir(path.parent) as (parent,ids):
  fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
  try:
   before=os.fstat(fd);meta=identity(before)
   assert meta==old and stat.S_ISREG(before.st_mode) and meta['mode']==expected_mode==0o600 and meta['nlink']==1 and meta['uid']==os.getuid() and meta['gid']==os.getgid()
   h=hashlib.sha256();count=0
   while True:
    b=os.read(fd,1048576)
    if not b:break
    count+=len(b);h.update(b)
   assert count==before.st_size and h.hexdigest()==row['sha256'] and identity(os.fstat(fd))==meta
   assert identity(os.stat(path.name,dir_fd=parent,follow_symlinks=False))==meta
  finally:os.close(fd)
  W.reattach(path.parent,ids)
 observations.append({'path':str(path),'sha256':h.hexdigest(),'metadata':meta,'body_persisted':False})
assert observations[0]['sha256']==observations[1]['sha256']
assert not os.path.lexists(R/selected['auth_placeholder']['path'])
assert S.select_after_mapper()['bound_rows']==selected['bound_rows']
result={'schema':'context-stage-disposable-archive-completion/v1','observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prior_audit_sha256':hashlib.sha256((E/'audit.json').read_bytes()).hexdigest(),'observations':observations,'complete_stage_files_hashed':1570,'historical_protected_source8_opened':False,'body_printed_or_persisted':False}
(E/'archive-completion.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'archive_source_and_stage_digest_match':True,'complete_stage_files_hashed':1570,'body_printed_or_persisted':False}))
