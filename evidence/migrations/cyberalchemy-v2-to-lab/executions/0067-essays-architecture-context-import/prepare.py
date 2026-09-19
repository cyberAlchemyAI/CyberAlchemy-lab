import json,hashlib,shutil,subprocess,os,tarfile
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0067-essays-architecture-context-import';W=R/'.local/essays-architecture-package-0067';PREFIX='cyberAlchemy-v2/essays/development/agent-runtime/architecture-properties/';P=W/PREFIX;r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(R.parent/PREFIX,P,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
selections=[]
for row in r(P/'SOURCES.json')['sources']:
 src=R.parent/row['path'];data=src.read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'] and len(data)==row['size_bytes'];assert all(s in data.decode() for s in row['selectors'])
 dst=W/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);selections.append({'source_id':row['source_id'],'path':row['path'],'sha256':sha(dst),'size_bytes':len(data)})
cap='cyberAlchemy-v2/essays/capabilities/essays-agent-runtime.product-capability.json';(W/cap).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R.parent/cap,W/cap)
dump(H/'source-bindings.json',selections)
files=sorted(p for p in W.rglob('*') if p.is_file());manifest=[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files];dump(H/'package-inputs.json',manifest)
c=subprocess.run(['python3',str(P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/'source-validation.json',{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});print(c.stdout);assert c.returncode==0
for b in manifest:assert sha(W/b['path'])==b['sha256']
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
