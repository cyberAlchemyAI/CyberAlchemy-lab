import os,sys,stat,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from contextlib import contextmanager
R=Path('/home/vlad_/projects/CyberAlchemy-lab');L=R/'implementation/lab-runtime/local-host';D=Path(__file__).parent
A=Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/mapper-attempt');E=Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/mapper-successor-stage-release-0001')
SHA=lambda b:hashlib.sha256(b).hexdigest()
def need(v,c):
 if not v:raise RuntimeError(c)
def ident(s):return [s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def did(s):return [s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid]
DF=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC;FF=os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC
@contextmanager
def held(path):
 fds=[os.open('/',DF)]
 try:
  for p in path.parts[1:]:fds.append(os.open(p,DF,dir_fd=fds[-1]))
  before=[did(os.fstat(fd)) for fd in fds];yield fds[-1]
  need(before==[did(os.fstat(fd)) for fd in fds],'HELD_ROOT_DRIFT')
  other=[os.open('/',DF)]
  try:
   for p in path.parts[1:]:other.append(os.open(p,DF,dir_fd=other[-1]))
   need(before==[did(os.fstat(fd)) for fd in other],'NAMED_ROOT_DRIFT')
  finally:
   for fd in reversed(other):os.close(fd)
 finally:
  for fd in reversed(fds):os.close(fd)
def file(rootfd,rel,digest=None,mode=None,raw=False):
 ps=rel.split('/');need(all(x not in ('','..','.') for x in ps),'PATH');fds=[os.dup(rootfd)]
 try:
  for p in ps[:-1]:fds.append(os.open(p,DF,dir_fd=fds[-1]))
  before=os.stat(ps[-1],dir_fd=fds[-1],follow_symlinks=False)
  need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.getuid() and before.st_gid==os.getgid(),'FILE_CUSTODY')
  if mode is not None:need(stat.S_IMODE(before.st_mode)==mode,'FILE_MODE')
  fd=os.open(ps[-1],FF,dir_fd=fds[-1]);fds.append(fd);need(ident(os.fstat(fd))==ident(before),'FILE_OPEN')
  h=hashlib.sha256();size=0;chunks=[]
  while True:
   b=os.read(fd,1024*1024)
   if not b:break
   h.update(b);size+=len(b)
   if raw:chunks.append(b);need(size<=2*1024*1024,'RAW_LIMIT')
   need(size<=128*1024*1024,'FILE_LIMIT')
  need(size==before.st_size and ident(os.fstat(fd))==ident(before) and ident(os.stat(ps[-1],dir_fd=fds[-2],follow_symlinks=False))==ident(before),'FILE_POST')
  if digest:need(h.hexdigest()==digest,'FILE_HASH')
  rec={'path':rel,'sha256':h.hexdigest(),'size':size,'identity':ident(before)}
  return (rec,b''.join(chunks)) if raw else rec
 finally:
  for fd in reversed(fds):os.close(fd)
pins={}
def selected(path,digest):
 b=path.read_bytes();need(SHA(b)==digest,'SELECTED_PIN');pins[str(path)]={'sha256':SHA(b),'size':len(b)};return b
for name,digest in [('mapper-successor-stage-release-0001','543f3f21bc0542a73fbcbc5980c353c3a610ef806d4a7942b6839340fb912443'),('mapper-successor-stage-0002','c214e06c122186124a11f16e456257a1f800cfea8b05361da9d18247ece60311'),('mapper-successor-stage-adapter-0002','c4a15d25587623ec4b73408d2e3e51f767d0d33e4943262b491bae435eabef0e')]:
 f=json.loads(selected(L/name/'freeze.json',digest))
 for row in f['file_bindings']:need(len(selected(R/row['path'],row['sha256']))==row['size'],'SELECTED_SIZE')
for name,digest in [('MAPPER-SUCCESSOR-STAGE-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md','7cd5411e65b1b0e3d545a83b91120035f0979c3b9177ccdf5da87192be43a9e4'),('MAPPER-SUCCESSOR-STAGE-INDEPENDENT-STATIC-REVIEW-0002.md','fad287769926dafe0a662ce9007d28b4bd90ba4523364b51a3ecd6a30974633f'),('context-successor-reader-independent-effect-review-0001/review.json','c2f9d0307610d281784c4d3c86211dbc37bd6a5843130647ff1718561957f295')]:selected(L/name,digest)
plan=json.loads(selected(L/'mapper-successor-stage-0002/stage-plan.json','9041aeedc8b349f6d7315e7ac2544aabda85afdb748663010e00af25e0b9ca2e'));cp=json.loads(selected(L/'mapper-successor-stage-0002/copy-plan.json','76bfc24841d652cbae039d666bcde80d7899b3b978ebd0291443705543d3dd95'))
evidence={}
with held(E) as fd:
 for n in ('intent.json','result.json','stdout.bin','stderr.bin'):
  rec,b=file(fd,n,raw=True);evidence[n]=rec;evidence[n]['absolute_path']=str(E/n)
  if n.endswith('.json'):evidence[n]['value']=json.loads(b)
  if n=='stdout.bin':stdout=b
  if n=='stderr.bin':need(b==b'','STDERR')
intent=evidence['intent.json']['value'];ext=evidence['result.json']['value']
need(evidence['result.json']['sha256']=='ddac0db744829ec1bd849e1111fe325fb3af9055939334d97373c68eff104e54','EXTERNAL_PIN')
need(ext['schema']=='mapper-successor-stage-external-observation/v1' and type(ext['os_exit_code']) is int and ext['os_exit_code']==0 and ext['process_error'] is None and ext['retry_allowed'] is False,'EXIT')
for obj in (intent,ext):need(obj['freeze_sha256']=='543f3f21bc0542a73fbcbc5980c353c3a610ef806d4a7942b6839340fb912443' and obj['review_sha256']=='7cd5411e65b1b0e3d545a83b91120035f0979c3b9177ccdf5da87192be43a9e4','EXTERNAL_SELECTION')
need(intent['schema']=='mapper-successor-stage-external-intent/v1' and intent['retry_allowed'] is False and intent['argv']==['/usr/bin/python3','-B',str(L/'mapper-successor-stage-release-0001/release.py'),'--execute-reviewed-one-shot'],'INTENT')
for k in ('stdout','stderr'):need(type(ext[k+'_size']) is int and ext[k+'_size']==evidence[k+'.bin']['size'] and ext[k+'_sha256']==evidence[k+'.bin']['sha256'],'STREAM')
need(type(intent['started_at_ns']) is int and type(ext['finished_at_ns']) is int and ext['finished_at_ns']>=intent['started_at_ns'],'TIMES')
source='product/lab/release-candidates/v1/interface/docker-source-20261020-0002';mapper='product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002'
def dir_mode(n):return 0o700 if n==source+'/receipts' or n.startswith(source+'/packages') or n==mapper+'/packages' else 0o755
def inventory(fd):
 files=set();dirs={}
 def scan(d,prefix):
  with os.scandir(d) as it:
   for ent in it:
    name=prefix+ent.name;st=os.stat(ent.name,dir_fd=d,follow_symlinks=False)
    need(st.st_uid==os.getuid() and st.st_gid==os.getgid(),'INV_OWNER')
    if stat.S_ISDIR(st.st_mode):
     dirs[name]=ident(st);child=os.open(ent.name,DF,dir_fd=d)
     try:need(did(os.fstat(child))==did(st),'DIR_OPEN');scan(child,name+'/')
     finally:os.close(child)
    else:need(stat.S_ISREG(st.st_mode) and st.st_nlink==1,'INV_TYPE');files.add(name)
    need(len(files)<=1200 and len(dirs)<=1100,'INV_BOUND')
 scan(fd,'');return files,dirs
snapshots={}
with held(A) as afd:
 need(stat.S_IMODE(os.fstat(afd).st_mode)==0o700,'ATTEMPT_MODE');attempt_id=ident(os.fstat(afd))
 need(set(os.listdir(afd))=={'root','input','evidence','consumed.json'},'ATTEMPT_INVENTORY')
 for d in ('input','evidence'):need(stat.S_IMODE(os.stat(d,dir_fd=afd,follow_symlinks=False).st_mode)==0o700,'CONTROL_DIR_MODE')
 for n in ('consumed.json','evidence/stage-terminal.json'):
  rec,b=file(afd,n,mode=0o600,raw=True);evidence[n]=rec;evidence[n]['value']=json.loads(b)
 marker=evidence['consumed.json']['value'];term=evidence['evidence/stage-terminal.json']['value']
 need(marker['schema']=='lab-mapper-successor-stage-consumed/v1' and marker['no_retry'] is True and marker['attempt']==str(A),'CONSUMED')
 need(term['schema']=='lab-mapper-successor-stage-terminal/v1' and term['overall']=='OBSERVED_STAGE_ONLY' and term['effect']=='PRIVATE_STAGE_COPY_ONLY' and term['mapper_effect']=='NOT_RUN' and term['no_retry'] is True and term['requires_external_exit_zero_and_independent_stage_review'] is True,'TERMINAL')
 for ob in (marker,term):need(ob['stage_plan_sha256']==cp['source_plan_sha256'] and ob['copy_plan_sha256']=='76bfc24841d652cbae039d666bcde80d7899b3b978ebd0291443705543d3dd95' and ob['attempt']==str(A),'PLAN_JOIN')
 need(json.loads(stdout)==term,'STDOUT_TERMINAL');need((term['input_files'],term['source_directories'],term['target_directories'],term['private_rows'])==(991,931,933,37),'COUNTS')
 need(term['reader_effect_review_sha256']==plan['reader_effect_review_sha256'] and term['native_sha256']==plan['native_sha256'],'LINEAGE')
 snapshots['native']=file(afd,'input/lab-context-native-reader',plan['native_sha256'],0o755)
for label,root,rows,dirs in [('target',A/'root',plan['files'],set(cp['target_directory_names'])),('source',Path(cp['source_root']),[r for r in plan['files'] if r['source_kind']=='reviewed-reader-stage'],set(cp['target_directory_names'])-{mapper,mapper+'/packages'})]:
 with held(root) as fd:
  need(stat.S_IMODE(os.fstat(fd).st_mode)==0o755,'ROOT_MODE');found,di=inventory(fd)
  need(found=={r['path'] for r in rows} and set(di)==dirs,'EXACT_INVENTORY')
  for name,identity in di.items():need(stat.S_IMODE(identity[2])==dir_mode(name),'DIR_MODE')
  records=[file(fd,r['path'],r['sha256'],int(r['target_mode'],8)) for r in rows]
  need(inventory(fd)==(found,di),'POST_INVENTORY')
  snapshots[label]={'root':str(root),'root_identity':ident(os.fstat(fd)),'files':records,'directories':di}
need(len(snapshots['target']['files'])==991 and len(snapshots['source']['files'])==986,'FILE_COUNT')
need(sum(stat.S_IMODE(x['identity'][2])==0o600 for x in snapshots['target']['files'])==37,'PRIVATE_MODE')
with held(A/'root') as fd:
 rec,b=file(fd,source+'/packages/0001/period.json',raw=True);period=json.loads(b)
 period_start=datetime.fromisoformat(period['not_before']);period_end=datetime.fromisoformat(period['expires_at']);now=datetime.now(timezone.utc)
 need(period_start<=now<period_end,'CURRENT_PERIOD')
 for ns in (intent['started_at_ns'],ext['finished_at_ns']):need(period_start.timestamp()<=ns/1e9<period_end.timestamp(),'EFFECT_PERIOD')
need(not os.path.lexists(A/'root'/mapper/'packages/0001'),'MAPPER_OUTPUT_ABSENT')
for p,row in pins.items():need(SHA(Path(p).read_bytes())==row['sha256'],'POST_PIN')
# Exact no-extra-attempt inventory includes no UNKNOWN; directories are empty where selected.
need(not os.path.lexists(A/'stage-unknown.json'),'UNKNOWN_PRESENT')
need(list((A/'root'/source/'receipts').iterdir())==[] and list((A/'root'/mapper/'packages').iterdir())==[],'EMPTY_DIRS')
report={'schema':'mapper-stage-independent-observation/v1','checked_at':now.isoformat(),'attempt':str(A),'attempt_identity':attempt_id,'pins':pins,'evidence':evidence,'snapshots':snapshots,'period':{'not_before':period['not_before'],'expires_at':period['expires_at'],'valid_at_execution_and_review':True},'verdict':'PASS_BOUNDED_STAGE_ONLY_EFFECT','no_retry':True,'mapper_effect':'NOT_RUN','private_content_printed':False,'source_identity_limit':'current snapshot only; creation/pre-effect per-file inode identities were not externally retained','historical_terminal_claim':'source identity compared internally by selected stage; independently verified current bytes/modes match original selected closure'}
(D/'observation.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'verdict':report['verdict'],'observation_sha256':SHA((D/'observation.json').read_bytes()),'target_files':991,'target_dirs':933,'source_files':986,'source_dirs':931,'private_rows':37,'checked_at':now.isoformat(),'terminal_sha256':evidence['evidence/stage-terminal.json']['sha256'],'stdout_sha256':evidence['stdout.bin']['sha256'],'marker_sha256':evidence['consumed.json']['sha256']},sort_keys=True))
