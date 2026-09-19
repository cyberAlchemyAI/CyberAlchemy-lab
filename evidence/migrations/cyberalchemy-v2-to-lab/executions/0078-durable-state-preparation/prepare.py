"""Pin Durable Capability State, distinct from encrypted-object storage. See README.md."""
import json,hashlib,shutil,subprocess,os,tarfile,importlib.util
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/durable-state-package-0078';P='cyberAlchemy-v2/durable-storage';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(R.parent/P,W/P,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
s=importlib.util.spec_from_file_location('source_validator',W/P/'scripts/validate.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
rows=r(W/P/'sources.json')['sources'];report=[]
for rel in dict.fromkeys(x['path'] for x in rows):
 group=[x for x in rows if x['path']==rel];candidates=[R.parent/rel,R.parent/'cya-orquestrator'/rel,*sorted((R/'.local').glob('ontology-context-import-*/package/'+rel)),*sorted((R/'.local').glob('*/'+rel))];candidates=list(dict.fromkeys(p for p in candidates if p.is_file()))
 def matches(p):
  for row in group:
   raw=p.read_bytes() if row['selection_kind']=='whole-file' else (v.markdown_section(p.read_text(),row['selector']) or '').encode()
   if hashlib.sha256(raw).hexdigest()!=row['sha256']:return False
  return True
 selected=next((p for p in candidates if matches(p)),None);src=selected or (candidates[0] if candidates else None)
 if src:dst=W/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 report.append({'path':rel,'source_ids':[x['source_id'] for x in group],'recovered_from':str(src) if src else None,'sha256':sha(src) if src else None,'selections_match':selected is not None})
dump(H/'source-recovery.json',report)
c=subprocess.run(['python3',str(W/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/'source-validation.json',{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});print(c.stdout)
files=sorted(p for p in W.rglob('*') if p.is_file());dump(H/'package-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
print('Unrecovered:',[x['path'] for x in report if not x['selections_match']])
