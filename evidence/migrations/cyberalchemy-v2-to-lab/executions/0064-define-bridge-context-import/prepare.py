import json,hashlib,shutil,tarfile,ast,subprocess,os
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0064-define-bridge-context-import';W=R/'.local/define-bridge-package-0064';P=W/'cyberAlchemy-v2/define';S=R.parent/'cyberAlchemy-v2/define';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
W.mkdir(parents=True,exist_ok=True)
for prev in ['0062-shared-meaning-context-import','0063-define-session-context-import']:
 folder=H.parent/prev
 for b in r(folder/'verification.json')['bindings']:assert sha(R/b['path'])==b['sha256']
 with tarfile.open(folder/'package-snapshot.tar.gz') as a:a.extractall(W,filter='data')
profile=r(S/'profile.json');materials=profile['material_files'];selected=[]
for f in materials:
 src=S/f;dst=P/f;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copyfile(src,dst)
 selected.append({'path':f,'checkout_sha256':sha(src),'selected_sha256':sha(dst),'historical_child_selection':sha(src)!=sha(dst)})
shutil.copytree(S/'receipts',P/'receipts',dirs_exist_ok=True)
excluded=[]
for f in S.rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(S)
 if str(rel) in materials or rel.parts[0] in ['business-ontology','system-ontology','capabilities','receipts']:continue
 excluded.append({'path':str(rel),'sha256':sha(f)})
dump(H/'parent-material-selection.json',{'selected_materials':selected,'outside_declared_material':excluded,'authority_effect':'none'})
sources=r(P/'sources.json');dump(H/'original-sources.json',sources);recovery=[]
for row in sources['sources']:
 paths=[W/row['path'],R.parent/row['path'],R.parent/'domainspec-core'/row['path'],R.parent/'cya-orquestrator'/row['path'],Path('/tmp/define-bridge-recovery')/row['sha256']]
 if row['path'].startswith('arcanum/spells/invoke/'):paths.append(R.parent/'domainspec-core/.agents/skills/invoke'/row['path'].removeprefix('arcanum/spells/invoke/'))
 chosen=next((f for f in paths if f.is_file() and sha(f)==row['sha256']),None);exact=chosen is not None
 if chosen is None:
  assert row['id']=='SRC-CAV2-PRODUCT-THESIS',row;chosen=W/row['path']
 data=chosen.read_bytes();assert all(s in data.decode() for s in row['selectors']),row['id']
 dst=W/row['path'];dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists() and dst.read_bytes()!=data:raise ValueError('Conflicting pinned dependency: '+str(dst))
 dst.write_bytes(data);recovery.append({'id':row['id'],'path':row['path'],'expected_sha256':row['sha256'],'observed_sha256':sha(dst),'exact':exact,'selected_from':str(chosen)})
 if not exact:row['sha256']=sha(dst);row['size']=len(data)
dump(H/'source-recovery.json',{'sources':recovery,'git_recoveries':r(Path('/tmp/define-bridge-recovery/recovery.json'))})
cmd=['python3',str(P/'scripts/validate.py')]
def run():
 t=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});return {'exit_code':t.returncode,'stdout':t.stdout,'stderr':t.stderr}
initial=run();dump(H/'original-validation.json',initial)
dump(P/'sources.json',sources)
final=run();dump(H/'source-validation.json',final);print(final['stdout'][-2800:],final['stderr']);assert final['exit_code']==0
for child in ['0062-shared-meaning-context-import','0063-define-session-context-import']:
 for b in r(H.parent/child/'package-inputs.json'):
  assert sha(W/b['path'])==b['sha256'],('child snapshot drift',b['path'])
files=sorted(p for p in W.rglob('*') if p.is_file());dump(H/'package-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
