"""Explicit reviewed docs-only adoption. Root coordinates any actual application."""
import argparse,contextlib,fcntl,hashlib,json,os,re,stat
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[6]
WEBSITE=HERE.parent/'website-integration-preparation-0001'
SCOPE=['website/','tooling/docs/import_site_docs.py','docs/lab/']

def need(ok,message):
 if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):
 def pairs(items):
  out={}
  for k,v in items:need(k not in out,'duplicate JSON key');out[k]=v
  return out
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'nonfinite JSON'))
def canonical(value):
 need(type(value)is str and value and '\\' not in value,'canonical path string required')
 p=Path(value);need(not p.is_absolute() and p.as_posix()==value and '..' not in p.parts and '.' not in p.parts,'canonical relative path required')
 return p
def captured_locator(value):
 need(type(value)is str and value and '\\' not in value,'captured locator string required')
 p=Path(value);need(p.as_posix()==value and '..' not in p.parts and '.' not in p.parts,'canonical captured locator required')
 if p.is_absolute():
  try:return p.relative_to(ROOT).as_posix()
  except ValueError:return p.as_posix()
 return canonical(value).as_posix()

def target(value):
 p=canonical(value);need(any(value.startswith(x) if x.endswith('/') else value==x for x in SCOPE),'outside reviewed docs scope')
 need(p.name not in {'.','..'} and len(p.parts)>1,'file target required');return p

def identity(s):return(s.st_dev,s.st_ino,s.st_mode,s.st_uid)
def stamp(s):return identity(s)+(s.st_size,s.st_mtime_ns,s.st_ctime_ns)

@contextlib.contextmanager
def parent(rootfd,rel,create=False):
 parts=canonical(rel).parts;fds=[];links=[];fd=rootfd
 try:
  for name in parts[:-1]:
   if create:
    try:os.mkdir(name,0o755,dir_fd=fd)
    except FileExistsError:pass
   child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);fds.append(child)
   info=os.fstat(child);links.append((fd,name,child,identity(info)));fd=child
  def attached():
   for anchor,name,child,old in links:
    need(identity(os.fstat(child))==old==identity(os.stat(name,dir_fd=anchor,follow_symlinks=False)),'selected parent detached or mode/owner changed')
  attached();yield fd,parts[-1],attached;attached()
 finally:
  for fd in reversed(fds):os.close(fd)

@contextlib.contextmanager
def repo():
 fds=[os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)];links=[]
 try:
  for name in ROOT.parts[1:]:
   anchor=fds[-1];child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=anchor);fds.append(child);links.append((anchor,name,child,identity(os.fstat(child))))
  def attached():
   for anchor,name,child,old in links:need(identity(os.fstat(child))==old==identity(os.stat(name,dir_fd=anchor,follow_symlinks=False)),'repository origin detached')
  attached();yield fds[-1],attached;attached()
 finally:
  for fd in reversed(fds):os.close(fd)

def read_at(rootfd,rel,absent=False):
 try:
  with parent(rootfd,rel) as (p,name,attached):
   fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=p)
   try:
    before=os.fstat(fd);need(stat.S_ISREG(before.st_mode) and before.st_size<=32*1024*1024,'bounded regular input required')
    blocks=[];total=0
    while block:=os.read(fd,1024*1024):total+=len(block);need(total<=32*1024*1024,'input grew');blocks.append(block)
    raw=b''.join(blocks);need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(name,dir_fd=p,follow_symlinks=False)),'input attachment or bytes changed');attached();return raw,before
   finally:os.close(fd)
 except FileNotFoundError:
  if absent:return None,None
  raise

def binding(rootfd,row):
 need(type(row)is dict and set(row)=={'path','sha256'} and re.fullmatch('[a-f0-9]{64}',row['sha256'])is not None,'closed exact binding required')
 raw,_=read_at(rootfd,canonical(row['path']).as_posix());need(sha(raw)==row['sha256'],'independent input hash changed: '+row['path']);return raw

def overlap(rootfd,packet,targets):
 rows=[]
 need(set(packet['runtime_overlap_bindings'])=={'source','reader','mapped','context','original_api_source'},'all five captured tables required')
 for role,b in packet['runtime_overlap_bindings'].items():
  table=parse(binding(rootfd,b));need(type(table.get('files'))is list,'captured files table required');paths=[];external=0;absolute_inside=0
  for row in table['files']:
   need(type(row)is dict and type(row.get('path'))is str,'unsupported captured row');p=captured_locator(row['path']);paths.append(p)
   if Path(row['path']).is_absolute():
    if Path(p).is_absolute():external+=1
    else:absolute_inside+=1
  conflicts=[(t,p) for t in targets for p in paths if t==p or p.startswith(t+'/') or t.startswith(p+'/')]
  need(not conflicts,'captured runtime/API target overlap: '+str(conflicts[:3]));rows.append({'role':role,'binding':b,'captured_rows':len(paths),'absolute_inside_comparison_only':absolute_inside,'absolute_external_declared_origins':external,'external_origins_read_or_rebased':False,'overlaps':0})
 return rows

def preflight(rootfd,packet):
 fields={'schema_version','authority_effect','shared_applied','full_T21_complete','website_selection_binding','website_manifest_binding','website_handoff_binding','website_peer_binding','expected_counts','scope','runtime_overlap_bindings','runtime_overlap_scope','old_API_overlap_only','target_modes','application_order'}
 need(type(packet)is dict and set(packet)==fields and packet['schema_version']=='lab-T21-reviewed-shared-docs-adoption/v1-candidate' and packet['authority_effect']=='none' and packet['shared_applied']is False and packet['full_T21_complete']is False and packet['scope']==SCOPE and packet['old_API_overlap_only']is True,'closed reviewed application packet required')
 selected=parse(binding(rootfd,packet['website_selection_binding']));mf=parse(binding(rootfd,packet['website_manifest_binding']));handoff=parse(binding(rootfd,packet['website_handoff_binding']));peer=parse(binding(rootfd,packet['website_peer_binding']))
 need(peer['result']=='PASS-exact-owned-website-integration-candidate' and peer['findings']==[],'exact peer PASS required')
 for key,name in [('website_selection_binding','postimage-selection.json'),('website_manifest_binding','source-manifest.json'),('website_handoff_binding','HANDOFF.json')]:need(peer['bindings'][name]==packet[key]['sha256'],'peer binding mismatch')
 need(handoff['source_manifest_sha256']==packet['website_manifest_binding']['sha256'] and handoff['postimage_selection_sha256']==packet['website_selection_binding']['sha256'],'handoff closure mismatch')
 mfrows={r['path']:r for r in mf['files']};need(len(mfrows)==len(mf['files']),'duplicate frozen manifest row')
 for row in mfrows.values():binding(rootfd,{'path':row['path'],'sha256':row['sha256']})
 modes={r['target']:r for r in packet['target_modes']};need(len(modes)==len(packet['target_modes']),'duplicate selected modes')
 rows=[];targets=[]
 for row in selected['files']:
  need(type(row)is dict and set(row)=={'target','preimage','postimage','changed'},'closed postimage row required');t=target(row['target']).as_posix();need(t not in targets,'duplicate selected target');targets.append(t)
  expectedpost=(WEBSITE/'postimages'/t).relative_to(ROOT).as_posix();need(row['postimage']['path']==expectedpost and mfrows.get(expectedpost,{}).get('sha256')==row['postimage']['sha256'],'postimage true origin/manifest mismatch')
  new=binding(rootfd,row['postimage']);pre=row['preimage'];need(pre.get('path')==t,'preimage target origin mismatch')
  newleaf=pre.get('exists')is False
  need(set(pre)==({'path','sha256','exists'} if newleaf else {'path','sha256'}),'closed preimage required');need(not newleaf or pre['sha256']is None,'new target has invented original hash')
  old,info=read_at(rootfd,t,absent=newleaf);mode=modes.get(t);need(mode is not None and set(mode)=={'target','preimage_mode','postimage_mode'},'closed selected modes required')
  if newleaf:need(old is None and mode['preimage_mode']is None and mode['postimage_mode']==0o644,'new target occupied or invalid new mode')
  else:need(info.st_uid==os.getuid() and sha(old)==pre['sha256'] and stat.S_IMODE(info.st_mode)==mode['preimage_mode']==mode['postimage_mode'],'existing target bytes/mode/owner conflict: '+t)
  need(type(row['changed'])is bool and row['changed']==(newleaf or old!=new),'changed flag disagrees with exact bytes')
  rows.append({**row,**mode,'old_bytes':old,'new_bytes':new,'old_stamp':stamp(info) if info else None})
 need(set(modes)==set(targets),'mode target closure differs');need(all(not b.startswith(a+'/') for a in targets for b in targets if a!=b),'file/directory target collision')
 counts={'selected':len(rows),'changed':sum(r['changed'] for r in rows),'existing':sum(r['old_bytes']is not None for r in rows),'new':sum(r['old_bytes']is None for r in rows)}
 need(counts==packet['expected_counts']=={'selected':100,'changed':97,'existing':17,'new':83},'whole100 closure/count mismatch')
 tables=overlap(rootfd,packet,targets);return rows,counts,tables

def write_all(fd,raw):
 at=0
 while at<len(raw):n=os.write(fd,raw[at:]);need(n>0,'short write');at+=n

@contextlib.contextmanager
def effect_lock(rootfd):
 rel=(HERE/'effect.lock').relative_to(ROOT).as_posix()
 with parent(rootfd,rel) as (p,name,attached):
  fd=os.open(name,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600,dir_fd=p)
  try:
   info=os.fstat(fd);need(stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o600 and info.st_nlink==1,'owned effect lock required')
   fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);attached();yield;attached()
  finally:os.close(fd)

def exclusive_file(rootfd,rel,raw,mode):
 with parent(rootfd,rel,create=True) as (p,name,attached):
  attached();fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode,dir_fd=p)
  try:os.fchmod(fd,mode);write_all(fd,raw);os.fsync(fd)
  finally:os.close(fd)
  os.fsync(p);attached()

def recheck(rootfd,row):
 old,info=read_at(rootfd,row['target'],absent=row['old_bytes']is None)
 need(old==row['old_bytes'] and (stamp(info) if info else None)==row['old_stamp'],'current target changed since complete preflight: '+row['target'])

def install(rootfd,row,token):
 recheck(rootfd,row)
 with parent(rootfd,row['target'],create=True) as (p,name,attached):
  tmp='.'+name+'.t21-'+token+'.tmp';need('/'not in tmp,'temp leaf required');fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,row['postimage_mode'],dir_fd=p)
  published=False
  try:
   try:os.fchmod(fd,row['postimage_mode']);write_all(fd,row['new_bytes']);os.fsync(fd)
   finally:os.close(fd)
   recheck(rootfd,row);attached()
   if row['old_bytes']is None:os.link(tmp,name,src_dir_fd=p,dst_dir_fd=p,follow_symlinks=False)
   else:os.replace(tmp,name,src_dir_fd=p,dst_dir_fd=p)
   published=True;os.fsync(p);attached()
  finally:
   # Only our exclusively allocated temp leaf is ever removed.
   try:os.unlink(tmp,dir_fd=p);os.fsync(p)
   except FileNotFoundError:pass
  new,info=read_at(rootfd,row['target']);need(new==row['new_bytes'] and stat.S_IMODE(info.st_mode)==row['postimage_mode'],'published row verification failed')
 return published

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--packet',required=True);ap.add_argument('--packet-sha256',required=True);ap.add_argument('--apply',action='store_true');ap.add_argument('--application-id');ap.add_argument('--report',required=True);a=ap.parse_args()
 report=canonical(a.report);need((ROOT/report).is_relative_to(HERE),'owned report path required')
 with repo() as (rootfd,origin):
  prior_report,_=read_at(rootfd,report.as_posix(),absent=True);need(prior_report is None,'fresh owned report required before effects')
  packet=parse(binding(rootfd,{'path':a.packet,'sha256':a.packet_sha256}));rows,counts,tables=preflight(rootfd,packet)
  if not a.apply:
   value={'schema_version':'lab-T21-shared-adoption-preflight/v1','authority_effect':'none','result':'PASS-complete-reviewed100-preflight','counts':counts,'runtime_overlap_tables':tables,'shared_applied':False,'old_API_overlap_only':True,'whole_API_qualified':False}
   exclusive_file(rootfd,report.as_posix(),(json.dumps(value,sort_keys=True,indent=2)+'\n').encode(),0o600);print(json.dumps(value));return
  need(a.application_id is not None and re.fullmatch('[a-z0-9-]{1,48}',a.application_id)is not None,'explicit fresh application id required')
  with effect_lock(rootfd):
   app=HERE/'applications'/a.application_id;apprel=app.relative_to(ROOT).as_posix()
   need(report.as_posix()==apprel+'/application-receipt.json','actual apply receipt must be inside its fresh owned application')
   with parent(rootfd,apprel,create=True) as (p,name,_):os.mkdir(name,0o700,dir_fd=p);os.fsync(p)
   progressfd=None
   try:
    with parent(rootfd,apprel+'/progress.jsonl') as (p,name,_):progressfd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=p);fcntl.flock(progressfd,fcntl.LOCK_EX|fcntl.LOCK_NB)
    def progress(kind,**data):write_all(progressfd,(json.dumps({'event':kind,**data},sort_keys=True)+'\n').encode());os.fsync(progressfd)
    progress('preflight-complete',counts=counts,packet_sha256=a.packet_sha256,runtime_overlap_tables=tables)
    backups=[]
    for row in rows:
     if row['old_bytes']is not None:
      rel=apprel+'/preimages/'+row['target'];exclusive_file(rootfd,rel,row['old_bytes'],row['preimage_mode']);backups.append({'target':row['target'],'backup_path':rel,'sha256':sha(row['old_bytes']),'mode':row['preimage_mode']})
    exclusive_file(rootfd,apprel+'/backup-manifest.json',(json.dumps({'files':backups,'new_targets':[r['target'] for r in rows if r['old_bytes']is None]},sort_keys=True,indent=2)+'\n').encode(),0o600);progress('all-preimages-durable',existing_backups=len(backups))
    # Repeat all input/target/overlap checks after backups, before first shared change.
    fresh,_,tables=preflight(rootfd,packet);need([r['old_stamp'] for r in fresh]==[r['old_stamp'] for r in rows],'preflight changed while backing up');origin()
    changed=[];unchanged=[]
    for i,row in enumerate(rows):
     binding(rootfd,row['postimage']);overlap(rootfd,packet,[row['target']]);recheck(rootfd,row);origin()
     if not row['changed']:unchanged.append(row['target']);progress('unchanged-preserved',target=row['target']);continue
     progress('row-start',target=row['target'],index=i,postimage_sha256=row['postimage']['sha256']);install(rootfd,row,a.application_id+'-'+str(i));changed.append(row['target']);progress('row-complete',target=row['target'],index=i,postimage_sha256=row['postimage']['sha256'],mode=row['postimage_mode'])
    for row in rows:
     raw,info=read_at(rootfd,row['target']);need(raw==row['new_bytes'] and stat.S_IMODE(info.st_mode)==row['postimage_mode'],'final whole100 closure changed')
    overlap(rootfd,packet,[r['target']for r in rows]);origin();progress('complete',changed=len(changed),unchanged=len(unchanged))
    value={'schema_version':'lab-T21-shared-adoption-application/v1','authority_effect':'none','result':'APPLIED-exact-reviewed100-docs-only','counts':counts,'changed':changed,'unchanged':unchanged,'backup_manifest':apprel+'/backup-manifest.json','progress':apprel+'/progress.jsonl','runtime_overlap_tables':tables,'publication_or_runtime_or_private_change':False,'full_T21_complete':False}
    exclusive_file(rootfd,report.as_posix(),(json.dumps(value,sort_keys=True,indent=2)+'\n').encode(),0o600);print(json.dumps(value))
   except BaseException as error:
    if progressfd is not None:progress('failed-no-automatic-retry-or-rollback',error_type=type(error).__name__,message=str(error),manual_reconciliation_required=True)
    raise
   finally:
    if progressfd is not None:os.close(progressfd)
if __name__=='__main__':main()
