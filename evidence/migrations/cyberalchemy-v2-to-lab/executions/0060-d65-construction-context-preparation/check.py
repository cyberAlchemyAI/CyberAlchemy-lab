import json,hashlib,shutil,tarfile,subprocess,os,importlib.util
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0060-d65-construction-context-preparation';W=R/'.local/d65-package-0060';S=R.parent/'cyberAlchemy-v2';G=W/'cyberAlchemy-v2/ontology/governance';PREV=H.parent/'0059-dependency-relevance-context-import'
r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
for b in r(PREV/'verification.json')['bindings']:assert sha(R/b['path'])==b['sha256']
W.mkdir(parents=True,exist_ok=True)
with tarfile.open(PREV/'package-snapshot.tar.gz') as a:a.extractall(W,filter='data')
for rel in ['ontology/governance','capability']:
 shutil.copytree(S/rel,W/'cyberAlchemy-v2'/rel,dirs_exist_ok=True,ignore=shutil.ignore_patterns('target','node_modules','__pycache__'))
shutil.copyfile(S/'authority/definitions/DEFINITIONS.md',W/'cyberAlchemy-v2/authority/definitions/DEFINITIONS.md')
registry=r(G/'construction-bindings.json')
for b in registry['bindings'][0]['file_bindings']:
 source=R.parent/b['path'];dst=W/b['path']
 if not dst.exists() and source.is_file():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dst)
files=sorted(p for p in W.rglob('*') if p.is_file());manifest=[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files];dump(H/'package-inputs.json',manifest)
sp=importlib.util.spec_from_file_location('legacy',G/'scripts/validate-construction.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
d=m.evaluate_registry(registry,verify_build=False,verify_dependency_checks=False);dump(H/'legacy-evaluation.json',d)
trans=[]
for rel in ['tests/test_d65_construction_mutations.py','tests/test_d65_prototype_construction.py','scripts/validate-prototype-construction.py']:
 args=['python3',str(G/rel)];c=subprocess.run(args,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True);entry={'command':args,'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr};trans.append(entry)
dump(H/'validation-transcripts.json',trans)
loader='/home/vrondelli/.cache/auth-completion/build-tools/node_modules/tsx/dist/loader.mjs';cmd=['node','--import',loader,str(G/'first-invariant/scripts/build.ts'),'--emit-json'];c=subprocess.run(cmd,capture_output=True,text=True)
build={'exit_code':c.returncode,'stderr':c.stderr}
if c.returncode==0:
 output=json.loads(c.stdout);build['output_sha256']=hashlib.sha256(c.stdout.encode()).hexdigest();build['changed_generated_artifacts']=[n for n,b in output.items() if (G/'first-invariant/domainspec/generated'/n).read_text()!=b]
else:build['stdout']=c.stdout
dump(H/'build-check.json',build)
for b in manifest:assert sha(W/b['path'])==b['sha256'],'check mutated '+b['path']
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
print('legacy',d['status'],len(d['errors']),d['blockers']);print('test exits',[t['exit_code'] for t in trans]);print('build',build)
