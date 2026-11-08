from pathlib import Path
import os,sys,stat,json,hashlib,types,datetime
L=Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host');E=Path(__file__).parent
F=Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001');A=F/'context-attempt';R=A/'root';O=Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/context-successor-public-stage-release-0001')
sha=lambda b:hashlib.sha256(b).hexdigest()
def audit(event,args):
 if event=='open' and isinstance(args[0],str) and args[0].endswith('branch.snapshot'):raise RuntimeError('PRIVATE_ARCHIVE_READ_FORBIDDEN')
 if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.fork','os.exec'):raise RuntimeError('EFFECT_FORBIDDEN')
sys.addaudithook(audit);sys.path.append('/usr/lib/python3/dist-packages')
def ident(st):return dict(dev=st.st_dev,ino=st.st_ino,mode=stat.S_IMODE(st.st_mode),uid=st.st_uid,gid=st.st_gid,nlink=st.st_nlink,size=st.st_size,mtime_ns=st.st_mtime_ns,ctime_ns=st.st_ctime_ns)
DF=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
LF=os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC
pins={}
def verify_freeze(path,digest):
 raw=path.read_bytes();assert sha(raw)==digest; pins[str(path)]=digest
 f=json.loads(raw)
 for n,h in f['members'].items():assert sha((path.parent/n).read_bytes())==h; pins[str(path.parent/n)]=h
 return f
release=verify_freeze(L/'context-successor-public-stage-release-0001/freeze.json','f44f312c674dc34cb8b4a430937bfeb0d11e4844dfc3dcb600258aac71d68a34')
verify_freeze(L/'context-successor-public-stage-writer-0002/freeze.json',release['stage_freeze_sha256'])
review=L/'context-successor-public-stage-release-independent-static-review-0001/review.json';assert sha(review.read_bytes())=='d694dd275d000231ebf92390d312f7d6d965d4f9ae343c3b30acd9b121de86f8';pins[str(review)]=sha(review.read_bytes())
p=L/'context-successor-public-stage-writer-0002/stage_writer.py';raw=p.read_bytes();assert sha(raw)==release['stage_code_sha256'];W=types.ModuleType('checked_writer');W.__file__=str(p);exec(compile(raw,str(p),'exec'),W.__dict__)
assert W.EFFECT_ENABLED is False
S,selected=W.selected();rows=W.source_rows(S,selected);dirs=W.directory_modes(rows);assert len(rows)==1570 and len(dirs)==1021
plan=sha(W.wire(selected['bound_rows']))
intent=json.loads((O/'intent.json').read_bytes());external=json.loads((O/'result.json').read_bytes());out=(O/'stdout.bin').read_bytes();err=(O/'stderr.bin').read_bytes();summary=json.loads(out)
assert type(external['os_exit_code']) is int and external['os_exit_code']==0 and external['process_error'] is None and err==b''
assert external['stdout_size']==len(out) and external['stdout_sha256']==sha(out) and external['stderr_size']==0 and external['stderr_sha256']==sha(err)
assert intent['release_freeze_sha256']==pins[str(L/'context-successor-public-stage-release-0001/freeze.json')] and intent['independent_review_json_sha256']==pins[str(review)]
assert intent['argv']==['/usr/bin/python3','-I','-S',str(L/'context-successor-public-stage-release-0001/release.py'),'--execute-reviewed-one-shot']
consumed=json.loads((A/'consumed.json').read_bytes());prov=json.loads((A/'stage.provisional.json').read_bytes())
assert consumed=={'attempt':str(A),'plan_sha256':plan,'retry_allowed':False,'schema':'context-successor-stage-consumed/v1','status':'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_REVIEW'}
assert prov=={'attempt':str(A),'auth':'UNMINTED_UNSELECTED','directories':1021,'files':1570,'plan_sha256':plan,'retry_allowed':False,'schema':'context-successor-stage-provisional/v1','status':'OBSERVED_STAGE_ONLY_PENDING_EXTERNAL_OS_REVIEW'}
assert summary=={'attempt':str(A),'directories':1021,'files':1570,'retry_allowed':False,'status':'PROVISIONAL_STAGE_ONLY_EXTERNAL_OS_REVIEW_REQUIRED'}
assert set(os.listdir(A))=={'root','consumed.json','stage.provisional.json'}
assert set(os.listdir(O))=={'intent.json','result.json','stdout.bin','stderr.bin'}
roots={}
for path in (F,A,R,O):
 with W.held_dir(path) as (fd,ids):
  st=os.fstat(fd);assert stat.S_IMODE(st.st_mode)==0o700 and st.st_uid==os.getuid() and st.st_gid==os.getgid();W.reattach(path,ids);roots[str(path)]=ident(st)
files={};directory_records={};excluded=[]
with W.held_dir(R) as (root,chain):
 def walk(fd,prefix=''):
  for name in sorted(os.listdir(fd)):
   rel=f'{prefix}/{name}' if prefix else name;st=os.stat(name,dir_fd=fd,follow_symlinks=False)
   assert st.st_uid==os.getuid() and st.st_gid==os.getgid()
   if stat.S_ISDIR(st.st_mode):
    assert rel in dirs and stat.S_IMODE(st.st_mode)==dirs[rel];directory_records[rel]=ident(st)
    child=os.open(name,DF,dir_fd=fd)
    try:assert ident(os.fstat(child))==ident(st);walk(child,rel)
    finally:os.close(child)
   else:
    assert stat.S_ISREG(st.st_mode) and st.st_nlink==1;files[rel]=ident(st)
 walk(root)
 assert set(files)=={r['path'] for r in rows} and set(directory_records)==set(dirs)
 for row in rows:
  rel=row['path'];meta=files[rel];assert meta['mode']==int(row['mode'],8)
  source=row.get('source_path')
  if source is not None:
   with W.held_dir(source.parent) as (parent,ids):
    st=os.stat(source.name,dir_fd=parent,follow_symlinks=False)
    assert stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==row['source_mode'] and st.st_size==meta['size']
    W.reattach(source.parent,ids)
  if rel.endswith('/branch.snapshot'):
   excluded.append(dict(path=rel,expected_sha256=row['sha256'],stage_metadata=meta,source_metadata=ident(st),verification='METADATA_ONLY_PRIVATE_BODY_NOT_OPENED'));continue
  parts=rel.split('/');parent=os.dup(root)
  try:
   for part in parts[:-1]:
    child=os.open(part,DF,dir_fd=parent);os.close(parent);parent=child
   fd=os.open(parts[-1],LF,dir_fd=parent)
   try:
    before=os.fstat(fd);assert ident(before)==meta;h=hashlib.sha256()
    while True:
     b=os.read(fd,1048576)
     if not b:break
     h.update(b)
    assert ident(os.fstat(fd))==meta and h.hexdigest()==row['sha256'];meta['sha256']=h.hexdigest()
   finally:os.close(fd)
  finally:os.close(parent)
  if source is not None:assert sha(W.pinned(source,row['sha256'],W.MAX_FILE))==row['sha256']
  else:assert sha(row['raw'])==row['sha256']
 W.reattach(R,chain)
assert len(excluded)==1
assert not os.path.lexists(R/selected['auth_placeholder']['path'])
for n in ('consumed.json','stage.provisional.json'):
 st=(A/n).lstat();assert stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1;pins[str(A/n)]=sha((A/n).read_bytes())
for n in ('intent.json','result.json','stdout.bin','stderr.bin'):
 st=(O/n).lstat();assert stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1;pins[str(O/n)]=sha((O/n).read_bytes())
assert S.select_after_mapper()['bound_rows']==selected['bound_rows']
result=dict(schema='context-stage-independent-effect-audit/v1',observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),pins=pins,plan_sha256=plan,files=len(files),directories=len(directory_records),independently_hashed_stage_files=len(files)-len(excluded),private_archive_excluded=excluded,roots=roots,inventory=files,directory_inventory=directory_records,external_os_exit=0,auth_absent=True,unknown_absent=True,selected_source_period_sha256=selected['source_period_sha256'],start_time=datetime.datetime.fromtimestamp(intent['created_at_ns']/1e9,datetime.timezone.utc).isoformat(),finish_time=datetime.datetime.fromtimestamp(external['finished_at_ns']/1e9,datetime.timezone.utc).isoformat())
(E/'audit.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('files','directories','independently_hashed_stage_files','auth_absent','unknown_absent','start_time','finish_time')}))
