import json,hashlib,shutil,subprocess,os,tarfile
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0063-define-session-context-import';W=R/'.local/define-system-package-0063';P=W/'cyberAlchemy-v2/define/system-ontology';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(R.parent/'cyberAlchemy-v2/define/system-ontology',P,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
(W/'.git').write_text('Isolated migration root marker for read-only validator path discovery; not a Git repository.\n')
recovery=[]
for row in r(P/'SOURCES.json')['sources']:
 candidates=[R.parent/row['path'],R.parent/'domainspec-core'/row['path'],R.parent/'cya-orquestrator'/row['path'],Path('/tmp/define-system-recovery')/row['sha256']]
 selected=next((p for p in candidates if p.is_file() and sha(p)==row['sha256']),None);assert selected,row
 dst=W/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(selected,dst);recovery.append({'source_id':row['source_id'],'path':row['path'],'sha256':sha(dst),'selected_from':str(selected)})
cap='cyberAlchemy-v2/define/capabilities/define-shared-meaning.product-capability.json';(W/cap).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R.parent/cap,W/cap)
dump(H/'source-recovery.json',{'sources':recovery,'historical_recovery':r(Path('/tmp/define-system-recovery/recovery.json'))})
files=sorted(p for p in W.rglob('*') if p.is_file());manifest=[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files];dump(H/'package-inputs.json',manifest)
c=subprocess.run(['python3',str(P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
dump(H/'source-validation.json',{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});print(c.stdout[:2000],c.stderr)
for b in manifest:assert sha(W/b['path'])==b['sha256']
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
