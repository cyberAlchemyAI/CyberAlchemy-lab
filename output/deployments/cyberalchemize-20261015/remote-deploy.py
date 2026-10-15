#!/usr/bin/env python3
"""Bounded, rollback-preserving release of the reviewed Lab website."""
import sys,json,hashlib,tarfile,subprocess,os,time,fcntl
from pathlib import Path
BASE=Path('/srv/co-op-engine');release=Path(sys.argv[1]);action=sys.argv[2]
assert release.parent==BASE/'deployments' and release.name.startswith('lab-20261015T')
envelope=json.loads((release/'envelope.json').read_text());assert release.name==envelope['release_id']
lock=(BASE/'.lab-static-deploy.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def run(args,**kwargs):return subprocess.run(args,check=True,capture_output=True,text=True,**kwargs).stdout.strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):(release/name).write_text(json.dumps(data,indent=2)+'\n')
def inventory(root):
 rows={}
 for p in sorted(root.rglob('*')):
  assert not p.is_symlink(),str(p)
  if p.is_file():rows[str(p.relative_to(root))]=sha(p)
 return rows
STATEFILES=['nginx.conf','docker-compose.yml','.env','.domainspec.htpasswd']
def configuration():return {n:sha(BASE/n) for n in STATEFILES}
def containers():
 ids=run(['docker','ps','-q']).splitlines();data=json.loads(run(['docker','inspect',*ids]));return {d['Name'].lstrip('/'):{'id':d['Id'],'started':d['State']['StartedAt'],'image':d['Image']} for d in data}
def unchanged_support(baseline):
 current=configuration()
 assert all(current[n]==baseline['config'][n] for n in STATEFILES if n!='nginx.conf'),'support configuration drift'
 now=containers()
 for name,row in baseline['containers'].items():
  if name!='coop-engine-site':assert now.get(name)==row,('unrelated container changed',name)
 assert now['coop-engine-site']['image']==baseline['image'],'static image changed'
 old=baseline['site'];current_site=inventory(BASE/'site')
 assert all(current_site.get(n)==v for n,v in old.items() if n!='index.html'),'existing sibling content changed'
def compose():return run(['docker','compose','--env-file','.env','-f','docker-compose.yml','up','-d','--no-deps','--pull','never','--force-recreate','site'],cwd=BASE)
def ready():
 for attempt in range(20):
  try:
   result=run(['docker','exec','coop-engine-site','wget','-qO-','http://127.0.0.1/healthz'])
   if result=='ok':return
  except subprocess.CalledProcessError:pass
  time.sleep(.5)
 raise RuntimeError('static health check failed')
def rollback():
 # Rename originals back; existing previous/next releases are never touched.
 oldsite=release/'live-before-site';oldconf=release/'live-before-nginx.conf'
 if oldsite.exists():
  if (BASE/'site').exists():(BASE/'site').rename(release/'failed-site')
  oldsite.rename(BASE/'site')
 if oldconf.exists():
  if (BASE/'nginx.conf').exists():(BASE/'nginx.conf').rename(release/'failed-nginx.conf')
  oldconf.rename(BASE/'nginx.conf')
 compose();ready();baseline=json.loads((release/'baseline.json').read_text())
 assert inventory(BASE/'site')==baseline['site'];assert configuration()==baseline['config'];unchanged_support(baseline)
 save('rollback.json',{'status':'restored','time':time.time()});print('ROLLBACK_RESTORED')
if action=='stage':
 assert (BASE/'.coop-engine-deployment').is_file()
 assert sha(BASE/'nginx.conf')==envelope['nginx_before_sha256']
 assert sha(BASE/'docker-compose.yml')==envelope['compose_sha256']
 assert sha(release/'nginx.conf.candidate')==envelope['nginx_candidate_sha256']
 assert sha(release/'reviewed-site.tar.gz')==envelope['upload_sha256']
 assert {p.name for p in (BASE/'site').iterdir()}=={'index.html','craft','bella','domainspec','agent-orchestration-guide'}
 oldsite=inventory(BASE/'site');assert len(oldsite)==9
 before=containers();image=before['coop-engine-site']['image']
 assert run(['docker','image','inspect','nginx:1.27-alpine','--format','{{.Id}}'])==image
 baseline={'site':oldsite,'config':configuration(),'containers':before,'image':image,'time':time.time()};save('baseline.json',baseline)
 backup=release/'rollback';backup.mkdir(mode=0o700)
 run(['cp','-a',str(BASE/'site'),str(backup/'site')])
 for name in STATEFILES:run(['cp','-a',str(BASE/name),str(backup/name)])
 assert inventory(backup/'site')==oldsite
 assert all(sha(backup/n)==baseline['config'][n] for n in STATEFILES)
 stage=release/'site';run(['cp','-a',str(BASE/'site'),str(stage)])
 allowed=set(envelope['allowed_new_paths']+envelope['allowed_replace'])
 with tarfile.open(release/'reviewed-site.tar.gz','r:gz') as archive:
  members=archive.getmembers();assert len(members)==envelope['files']
  for member in members:
   path=Path(member.name);assert member.isfile() and not path.is_absolute() and '..' not in path.parts and path.parts[0] in allowed
   dest=stage/path;dest.parent.mkdir(parents=True,exist_ok=True)
   with archive.extractfile(member) as source,dest.open('wb') as target:target.write(source.read())
   dest.chmod(0o644)
 for d in stage.rglob('*'):
  if d.is_dir():d.chmod(0o755)
 stage.chmod(0o755)
 manifest=json.loads((stage/'release-manifest.json').read_text());assert sha(stage/'release-manifest.json')==envelope['release_manifest_sha256']
 for row in manifest['files']:assert sha(stage/row['path'])==row['sha256'],row['path']
 staged=inventory(stage);assert len(staged)==len(oldsite)+envelope['files']-1
 assert all(staged[n]==v for n,v in oldsite.items() if n!='index.html')
 assert inventory(BASE/'site')==oldsite and configuration()==baseline['config']
 mounts=['-v',str(stage)+':/usr/share/nginx/html:ro','-v',str(release/'nginx.conf.candidate')+':/etc/nginx/conf.d/default.conf:ro','-v',str(BASE/'.domainspec.htpasswd')+':/etc/nginx/domainspec.htpasswd:ro']
 run(['docker','run','--rm','--network','none',*mounts,image,'nginx','-t'])
 run(['docker','run','--rm','--network','none','--user','101:101','--entrypoint','sh',*mounts,image,'-c','find /usr/share/nginx/html -type f -exec sh -c \'for f do test -r "$f" || exit 1; done\' sh {} + && test -r /etc/nginx/domainspec.htpasswd'])
 name='coop-lab-preflight-'+release.name.split('-')[-1]
 run(['docker','run','-d','--name',name,'--network','none',*mounts,image])
 try:
  for attempt in range(20):
   try:
    run(['docker','exec',name,'wget','-qO-','http://127.0.0.1/healthz']);break
   except subprocess.CalledProcessError:time.sleep(.5)
  samples=['/','/governance-lab-series/index.html','/governance-lab-series/start-here.html','/governance-lab-series/reference/def-cal-definition-actor.html','/craft-documentation-proposal/craft-model.html','/robot-learning-series/robot-learning-series.html','/governance-lab-series/assets/paper-crimson/appearance.css','/release-manifest.json','/craft','/bella','/agent-orchestration']
  for path in samples:run(['docker','exec',name,'wget','-qO-','http://127.0.0.1'+path])
  response=subprocess.run(['docker','exec',name,'wget','-S','-O','/dev/null','http://127.0.0.1/domainspec/'],capture_output=True,text=True)
  assert response.returncode and '401 Unauthorized' in response.stderr
 finally:run(['docker','rm','-f',name])
 unchanged_support(baseline)
 save('staged.json',{'status':'validated','files':len(staged),'new_files':envelope['files'],'preserved_old_files':len(oldsite)-1,'samples':samples,'nginx_valid':True,'all_files_worker_readable':True,'private_route_anonymous':401,'time':time.time()})
 print('STAGED_VALIDATED',len(staged),'files; current site unchanged; protected route401')
elif action=='cutover':
 assert json.loads((release/'staged.json').read_text())['status']=='validated';baseline=json.loads((release/'baseline.json').read_text())
 assert configuration()==baseline['config'] and inventory(BASE/'site')==baseline['site'],'live drift since staging'
 try:
  (BASE/'site').rename(release/'live-before-site');(release/'site').rename(BASE/'site')
  (BASE/'nginx.conf').rename(release/'live-before-nginx.conf');(release/'nginx.conf.candidate').rename(BASE/'nginx.conf')
  compose();ready();assert sha(BASE/'nginx.conf')==envelope['nginx_candidate_sha256'];unchanged_support(baseline)
  actual=run(['docker','exec','coop-engine-site','sha256sum','/usr/share/nginx/html/release-manifest.json']).split()[0]
  assert actual==envelope['release_manifest_sha256']
  save('cutover.json',{'status':'live','time':time.time(),'manifest_sha256':actual,'unrelated_containers_unchanged':True,'sibling_content_unchanged':True,'support_configuration_unchanged':True})
  print('CUTOVER_COMPLETE; same image; other containers and sibling files unchanged')
 except BaseException:
  rollback();raise
elif action=='check':
 baseline=json.loads((release/'baseline.json').read_text());unchanged_support(baseline);ready()
 assert sha(BASE/'nginx.conf')==envelope['nginx_candidate_sha256'];assert sha(BASE/'site/release-manifest.json')==envelope['release_manifest_sha256']
 manifest=json.loads((BASE/'site/release-manifest.json').read_text())
 for row in manifest['files']:assert sha(BASE/'site'/row['path'])==row['sha256'],row['path']
 print('FINAL_REMOTE_INTEGRITY_PASS; release exact; siblings, credentials, config and unrelated containers preserved')
elif action=='rollback':rollback()
else:raise ValueError(action)
