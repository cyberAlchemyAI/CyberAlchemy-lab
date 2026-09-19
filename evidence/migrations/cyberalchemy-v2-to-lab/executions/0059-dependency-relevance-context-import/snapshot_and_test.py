from pathlib import Path
import json,hashlib,shutil,tarfile,subprocess,os
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0059-dependency-relevance-context-import';W=R/'.local/dependency-package-0059';S=R.parent/'cyberAlchemy-v2';prefix='cyberAlchemy-v2/ontology/governance/dependency-kernel/';P=W/prefix
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
W.mkdir(parents=True,exist_ok=True)
with tarfile.open(H.parent/'0058-continuous-construction-context-import/package-snapshot.tar.gz') as a:a.extractall(W,filter='data')
shutil.copytree(S/'ontology/governance/dependency-kernel',P,ignore=shutil.ignore_patterns('target','node_modules','__pycache__'),dirs_exist_ok=True)
b=json.loads((P/'business-ontology.json').read_text())
for sel in b['source_bindings']:
 src=R.parent/sel['path'];dst=W/sel['path']
 if not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
files=sorted(p for p in P.rglob('*') if p.is_file());dump(H/'original-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
with tarfile.open(H/'original-package.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)))
trans=[]
for args in [['cargo','test','--locked'],['cargo','build','--locked']]:
 cmd=[str(S/'tools/toolchain/run')]+args
 c=subprocess.run(cmd,cwd=P/'runtime',env={**os.environ,'CARGO_NET_OFFLINE':'true'},capture_output=True,text=True);trans.append({'command':cmd,'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});dump(H/'runtime-validation.json',trans);assert c.returncode==0,c.stderr
binary=P/'runtime/target/debug/governance-dependency-kernel'
for op in ['validate-program','evaluate']:
 cmd=[str(binary),op,'--program',str(P/'programs/dependency-kernel-construction.program.json'),'--repository-root',str(W)]
 if op=='evaluate':cmd+=['--request',str(P/'requests/dependency-kernel-construction.request.json')]
 c=subprocess.run(cmd,capture_output=True,text=True);dump(H/('original-'+op+'.json'),{'exit_code':c.returncode,'output':json.loads(c.stdout)});print(op,c.returncode,c.stdout[:600])
