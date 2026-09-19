"""Pin and diagnose the original binding. Open questions: README.md."""
import hashlib,json,shutil,subprocess,os,tarfile
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0070-essays-implementation-binding-preparation';W=R/'.local/essays-binding-package-0070';BASE='cyberAlchemy-v2/essays/development/agent-runtime/';P=BASE+'conformance/implementation-binding';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
for rel in [P,BASE+'implementation']:
 shutil.copytree(R.parent/rel,W/rel,dirs_exist_ok=True,ignore=shutil.ignore_patterns('target','node_modules','.git','__pycache__'))
for execution,rel in [('0068',BASE+'domainspec'),('0069',BASE+'conformance/bridge-ontology')]:
 shutil.copytree(R/'.local'/('ontology-context-import-'+execution)/'package'/rel,W/rel,dirs_exist_ok=True)
for rel in ['cyberAlchemy-v2/essays/capabilities/agent-runtime/obligations/agent-runtime.obligations.json','cyberAlchemy-v2/essays/capabilities/essays-agent-runtime.product-capability.json']:
 dst=W/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'.local/ontology-context-import-0069/package'/rel,dst)
for entry in r(R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0069-essays-conformance-bridge-import/package-inputs.json'):
 if entry['path'].startswith(BASE+'implementation/'):
  assert sha(W/entry['path'])==entry['sha256'],('Implementation changed since 0069',entry['path'])
files=sorted(p for p in W.rglob('*') if p.is_file());dump(H/'package-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
c=subprocess.run(['python3',str(W/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/'source-validation.json',{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});print(c.stdout)
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
