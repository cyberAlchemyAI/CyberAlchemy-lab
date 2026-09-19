"""Pin coverage records and all referenced bytes. Open questions: README.md."""
import hashlib,json,shutil,subprocess,os,tarfile
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0069-essays-conformance-bridge-import';W=R/'.local/essays-bridge-package-0069';BASE='cyberAlchemy-v2/essays/development/agent-runtime/';PREFIX=BASE+'conformance/bridge-ontology';IMPL=BASE+'implementation';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(R.parent/PREFIX,W/PREFIX,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
paths={'cyberAlchemy-v2/essays/capabilities/agent-runtime/obligations/agent-runtime.obligations.json','cyberAlchemy-v2/essays/capabilities/essays-agent-runtime.product-capability.json',IMPL+'/tests/TEST-CAMPAIGN.md'}
for row in r(W/PREFIX/'COVERAGE.json')['coverage']:
 for ref in row['implementation']+row['evidence']:paths.add(str((R.parent/IMPL/ref.split('#')[0]).resolve().relative_to(R.parent)))
for name in sorted(paths):
 dst=W/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R.parent/name,dst)
files=sorted(p for p in W.rglob('*') if p.is_file());dump(H/'package-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
c=subprocess.run(['python3',str(W/PREFIX/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/'source-validation.json',{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});assert c.returncode==0;print(c.stdout)
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
