import json,hashlib,shutil,subprocess,os,tarfile
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0065-essays-agent-business-context-import';W=R/'.local/essays-business-package-0065';PREFIX='cyberAlchemy-v2/essays/capabilities/agent-runtime/ontology/';P=W/PREFIX;r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(R.parent/PREFIX,P,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
recovery=[]
for row in r(P/'SOURCES.json')['sources']:
 src=R.parent/row['path'];assert sha(src)==row['sha256'] and src.stat().st_size==row['size_bytes'];data=src.read_bytes();assert all(s in data.decode() for s in row['selectors'])
 dst=W/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);recovery.append({'source_id':row['source_id'],'path':row['path'],'sha256':sha(dst),'size_bytes':dst.stat().st_size})
dump(H/'source-bindings.json',recovery)
files=sorted(p for p in W.rglob('*') if p.is_file());manifest=[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files];dump(H/'package-inputs.json',manifest)
x=subprocess.run(['python3',str(P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/'source-validation.json',{'exit_code':x.returncode,'stdout':x.stdout,'stderr':x.stderr});print(json.loads(x.stdout)['summary']);assert x.returncode==0
for b in manifest:assert sha(W/b['path'])==b['sha256']
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
paths=['cyberAlchemy-v2/essays/development/agent-runtime/domainspec/generated/system-ontology.json','cyberAlchemy-v2/essays/development/agent-runtime/conformance/implementation-binding/PROFILE.json','cyberAlchemy-v2/essays/development/agent-runtime/conformance/bridge-ontology/PROFILE.json']
dump(H/'successor-observation.json',{'authority_effect':'none','source_validator_flag':'d65-successors','interpretation':'Hardcoded historical warning, not a current inventory assessment. Successor packages exist but are outside this business-only validation.','observed_successor_files':[{'path':path,'sha256':sha(R.parent/path)} for path in paths if (R.parent/path).is_file()],'source_validator_unchanged':True})
