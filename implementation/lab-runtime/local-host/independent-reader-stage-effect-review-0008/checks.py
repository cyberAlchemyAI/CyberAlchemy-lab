import os,stat,pathlib,json,hashlib,datetime
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab'); L=R/'implementation/lab-runtime/local-host'; C=L/'fresh-reader-docker-0008'; E=L/'independent-reader-stage-effect-review-0008'; A=pathlib.Path('/tmp/cal-reader-stage-20261020-0001-0008'); S=pathlib.Path('/tmp/cal-source-only-dev-20261020-0001-exact1')
def require(v,s):
 if not v:raise RuntimeError(s)
def ident(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def digest(p):
 p=pathlib.Path(p);fds=[]
 try:
  fds.append(os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW))
  for part in p.parts[1:-1]:fds.append(os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fds[-1]))
  before=os.stat(p.name,dir_fd=fds[-1],follow_symlinks=False);require(stat.S_ISREG(before.st_mode),'nonregular '+str(p))
  fd=os.open(p.name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fds[-1]);fds.append(fd);require(ident(os.fstat(fd))==ident(before),'attachment')
  h=hashlib.sha256();size=0
  while True:
   chunk=os.read(fd,1024*1024)
   if not chunk:break
   h.update(chunk);size+=len(chunk)
  require(ident(os.fstat(fd))==ident(before) and ident(os.stat(p.name,dir_fd=fds[-2],follow_symlinks=False))==ident(before),'drift')
  return {'path':str(p),'sha256':h.hexdigest(),'size':size,'uid':before.st_uid,'mode':format(stat.S_IMODE(before.st_mode),'04o'),'nlink':before.st_nlink,'device':before.st_dev,'inode':before.st_ino}
 finally:
  for fd in reversed(fds):os.close(fd)
def data(p):
 require(pathlib.Path(p).name!='branch.snapshot','archive parse refused');return json.loads(pathlib.Path(p).read_bytes())
def frozen(p,pin):
 b=digest(p);require(b['sha256']==pin,'freeze pin');f=data(p);out=[b]
 for row in f['file_bindings']:
  q=R/row['path'];v=digest(q);require(v['sha256']==row['sha256'] and v['size']==row['size'],'frozen drift '+str(q));out.append(v)
 return f,out
f,bindings=frozen(C/'freeze.json','7baa002724d031a1225e73518dee282caf3f9d26a914bdc306788c3873917606')
for ver,pin in [('0005','28d97810e1c3ac77aceee504a49a4e3e0c57fe08c520053b1c46b62c61e326a1'),('0007','3391cd37a4457472534768b9483cab97dbfb375536687684ca44d88d8724f41f')]:
 _,b=frozen(L/('fresh-reader-docker-'+ver)/'freeze.json',pin);bindings+=b
plan=data(C/'stage-plan.json');pb=digest(C/'stage-plan.json');require(pb['sha256']==f['stage_plan_sha256'],'plan pin'); rows=plan['files'];require(len(rows)==986 and len({x['path'] for x in rows})==986,'inventory count')
expected=set(x['path'] for x in rows);expected_dirs=set()
for name in expected:
 p=pathlib.PurePosixPath(name);require(not p.is_absolute() and '..' not in p.parts,'unsafe name')
 expected_dirs.update(str(v) for v in p.parents if str(v)!='.')
files=set();dirs=set();prod='product/lab/release-candidates/v1/interface/docker-source-20261020-0001'
for base,dd,ff in os.walk(A/'root',followlinks=False):
 for n in dd+ff:
  p=pathlib.Path(base)/n;st=p.lstat();rel=str(p.relative_to(A/'root'));require(st.st_uid==1000,'owner')
  if stat.S_ISDIR(st.st_mode):
   dirs.add(rel);mode=0o700 if rel==prod+'/receipts' or rel.startswith(prod+'/packages') else 0o755;require(stat.S_IMODE(st.st_mode)==mode,'directory mode')
  else:require(stat.S_ISREG(st.st_mode),'nonregular');files.add(rel)
require(files==expected and dirs==expected_dirs,'tree inventory')
for p,mode in [(A,0o700),(A/'root',0o755),(A/'evidence',0o700),(A/'reader-output',0o700)]:
 st=p.lstat();require(stat.S_ISDIR(st.st_mode) and st.st_uid==1000 and stat.S_IMODE(st.st_mode)==mode,'root mode')
require({x.name for x in A.iterdir()}=={'consumed.json','root','evidence','reader-output'},'attempt extras')
require({x.name for x in (A/'evidence').iterdir()}=={'stage-terminal.json'},'evidence extras/UNKNOWN');require(not list((A/'reader-output').iterdir()),'Reader output present')
observed=[];total=0
for row in rows:
 staged=digest(A/'root'/row['path']);source=digest(row['source_path'])
 for b,mode in [(staged,row['target_mode']),(source,row['source_mode'])]:require(b['sha256']==row['sha256'] and b['uid']==1000 and b['mode']==mode and b['nlink']==1,'member bytes/mode/link')
 require(staged['size']==source['size'],'size parity');total+=staged['size'];observed.append({'path':row['path'],'stage':staged,'source':source})
require(total==33411923,'selected size')
terminal=data(A/'evidence/stage-terminal.json');marker=data(A/'consumed.json')
require(terminal['overall']=='OBSERVED_STAGE_ONLY' and terminal['reader_input_released'] is False and terminal['reader_effect']=='NOT_RUN' and terminal['no_retry'] is True,'neutral semantics')
for key in ['attempt','selection_sha256','stage_plan_sha256','predecessor_freeze_sha256','release_base_freeze_sha256','source_terminal_sha256']:require(terminal[key]==marker[key],'marker join '+key)
require(terminal['attempt']==str(A) and terminal['input_files']==986 and terminal['stage_plan_sha256']==pb['sha256'],'attempt selection')
source_terminal=digest(S/'evidence/source-once.terminal.json');require(source_terminal['sha256']==terminal['source_terminal_sha256'],'source terminal changed')
for field,path in [('source_manifest_sha256',prod+'/source-manifest.json'),('source_package_sha256',prod+'/packages/0001/manifest.json'),('reader_manifest_sha256','product/lab/release-candidates/v1/interface/docker-reader-20261020-0001/source-manifest.json')]:require(digest(A/'root'/path)['sha256']==terminal[field],'manifest join')
package=data(A/'root'/prod/'packages/0001/manifest.json');source=data(A/'root'/prod/'source-manifest.json')
original={r['path']:r['sha256'] for r in source['files']+package['files']};original[prod+'/source-manifest.json']=terminal['source_manifest_sha256'];original[prod+'/packages/0001/manifest.json']=terminal['source_package_sha256'];require(len(original)==978,'Source closure')
require(all(original[x['path']]==x['sha256'] for x in rows if x['path'] in original),'Source closure pins');require(len([x for x in rows if x['path'] in original])==978,'Source inclusion')
archive=next(x for x in observed if x['path']==plan['archive_path']);require(archive['stage']['sha256']==terminal['archive_sha256']==package['archive_binding']['sha256'],'archive binding')
for p in [A/'consumed.json',A/'evidence/stage-terminal.json']:
 b=digest(p);require(b['mode']=='0600' and b['uid']==1000 and b['nlink']==1,'receipt mode');bindings.append(b)
bindings += [source_terminal,pb,digest(E/'checks.py')]
# Recheck current freeze and selected plan after all streaming reads.
_,post=frozen(C/'freeze.json',f['file_bindings'] and bindings[0]['sha256']);require(digest(C/'stage-plan.json')['sha256']==pb['sha256'],'post plan')
(E/'inventory.json').write_text(json.dumps(observed,indent=2)+'\n');(E/'bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
result={'status':'PASS_CURRENT_RETAINED_STAGE_CHECKS','observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':len(files),'directories':len(dirs),'bytes':total,'current_freeze_members':len(f['file_bindings']),'no_unknown_receipt':True,'empty_reader_output':True,'archive_hash_only':archive,'source_originals':978,'reader_generated_originals':8,'source_and_stage_bytes_match':True,'external_exit':'not independently file-bound; coordinator reports exit_code=0, chunk_id=865246, wall_time=1.294298305s','effect_performed_by_review':'NONE','no_retry_performed':True}
(E/'observations.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='archive_hash_only'},sort_keys=True))
