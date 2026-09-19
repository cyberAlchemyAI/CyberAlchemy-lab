"""Pin exact source selections; no source mutation. Open questions: README.md."""
import hashlib,json,shutil,subprocess,os,tarfile,importlib.util
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/people-teams-package-0072';PREFIX='cyberAlchemy-v2/people-and-teams';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(R.parent/PREFIX,W/PREFIX,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
selected={'cyberAlchemy-v2/authority/definitions/DEFINITIONS.md':R/'.local/ontology-context-import-0064/package/cyberAlchemy-v2/authority/definitions/DEFINITIONS.md','cyberAlchemy-v2/product/product-thesis.record.json':R.parent/'cya-orquestrator/cyberAlchemy-v2/product/product-thesis.record.json','cyberAlchemy-v2/capability/schemas/capability.schema.json':R/'.local/ontology-context-import-0061/package/cyberAlchemy-v2/capability/schemas/capability.schema.json','cyberAlchemy-v2/authority/definitions/DEFINITIONS-INDEX.md':R.parent/'cyberAlchemy-v2/authority/definitions/DEFINITIONS-INDEX.md'}
for name,src in selected.items():dst=W/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
s=importlib.util.spec_from_file_location('validator',W/PREFIX/'scripts/validate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
bindings=[]
for row in r(W/PREFIX/'sources.json')['sources']:
 data=m.selected_source_bytes(row);assert hashlib.sha256(data).hexdigest()==row['expected_digest']
 bindings.append({'source_id':row['source_id'],'path':row['path'],'selector':row['selector'],'selected_digest':row['expected_digest'],'full_file_digest':sha(W/row['path']),'recovered_from':str(selected[row['path']]),'authority_effect':'none'})
dump(H/'source-bindings.json',bindings)
for name,script in [('source-validation','scripts/validate.py'),('source-negative-tests','tests/test_negative_mutations.py')]:
 c=subprocess.run(['python3',str(W/PREFIX/script)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/(name+'.json'),{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});assert c.returncode==0;print(c.stdout)
files=sorted(p for p in W.rglob('*') if p.is_file());dump(H/'package-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
