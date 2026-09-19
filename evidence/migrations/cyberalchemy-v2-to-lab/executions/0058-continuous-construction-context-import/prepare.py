import json,hashlib,tarfile,shutil,subprocess
from pathlib import Path
ROOT=Path.cwd(); H=ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0058-continuous-construction-context-import'; PREV=H.parent/'0056-continuous-task-loop-context-import'; W=ROOT/'.local/governance-package-0058'; PREFIX='cyberAlchemy-v2/ontology/governance/continuous-construction/'; P=W/PREFIX
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=lambda p:json.loads(p.read_text())
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
W.mkdir(parents=True,exist_ok=True)
with tarfile.open(PREV/'package-snapshot.tar.gz') as a:a.extractall(W,filter='data')
s=r(P/'business-ontology.json')['source_bindings'][2]; source=ROOT.parent/s['path']; target=W/s['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
ids=s['selector'].split('=')[1].split(',');nodes=sorted([n for n in r(target)['nodes'] if n['id'] in ids],key=lambda n:n['id']);assert len(nodes)==len(ids)
selected=(json.dumps(nodes,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode();assert hashlib.sha256(selected).hexdigest()==s['sha256']
dump(H/'selection-recovery.json',{'result':'PASS','selection':s,'canonicalization':'selected nodes sorted by id; JSON sorted keys, compact separators, UTF-8, final newline','source_file_sha256':sha(target),'selected_records':len(nodes),'authority_effect':'none'})
for f in ['construction-binding.json','evidence/conformance-candidate.json']:shutil.copyfile(P/f,H/('original-'+Path(f).name))
b=r(P/'construction-binding.json');e=r(P/'evidence/conformance-candidate.json');changes=[]
def update(d,key,value,ptr):
 if d[key]!=value:changes.append({'pointer':ptr+'/'+key,'before':d[key],'after':value});d[key]=value

def walk(v,ptr):
 if isinstance(v,dict):
  if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str):update(v,'sha256',sha(W/v['path']),ptr)
  for k,c in v.items():walk(c,ptr+'/'+k)
 elif isinstance(v,list):
  for i,c in enumerate(v):walk(c,ptr+'/'+str(i))
for key,file in [('graph','graph.json'),('system_ontology','system-ontology.json'),('build_receipt','build-receipt.json')]:update(e['domainspec_build'],key+'_sha256',sha(P/'domainspec/generated'/file),'evidence/conformance-candidate.json#/domainspec_build')
system=r(P/'domainspec/generated/system-ontology.json');update(e['domainspec_build'],'source_set_sha256',system['source_set_digest'],'evidence/conformance-candidate.json#/domainspec_build');update(b['stages'][4],'source_set_sha256',system['source_set_digest'],'construction-binding.json#/stages/4')
dump(P/'evidence/conformance-candidate.json',e);walk(b['stages'],'construction-binding.json#/stages');dump(P/'construction-binding.json',b)
dump(H/'successor-changes.json',{'authority_effect':'none','changes':changes,'reason':'Current development profile/project and reproducible generated artifacts supersede stale evidence fingerprints. Original runtime and historical test claims remain unchanged; 0056 and 0057 supply current fixture evidence.','historical_comparison_limit':'Original artifact versions were not recovered; these are explicit current successors, not assertions of historical semantic equivalence.'})
loader='/home/vrondelli/.cache/auth-completion/build-tools/node_modules/tsx/dist/loader.mjs'
cmd=['node','--import',loader,str(P/'scripts/validate.ts')];v=subprocess.run(cmd,capture_output=True,text=True);dump(H/'source-validation.json',{'command':cmd,'exit_code':v.returncode,'stdout':v.stdout,'stderr':v.stderr});print(v.stdout,v.stderr);assert v.returncode==0
files=sorted(p for p in W.rglob('*') if p.is_file());dump(H/'package-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
print('packaged',len(files),'files',len(changes),'changes')
