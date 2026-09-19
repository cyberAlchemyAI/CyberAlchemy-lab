"""Recover exact dependency selections for Shared Capability. Open questions: README.md."""
import json,hashlib,shutil,importlib.util,subprocess,os,tarfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/shared-capability-package-0075';P='cyberAlchemy-v2/capability';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(R.parent/P,W/P,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
s=importlib.util.spec_from_file_location('capvalidator',W/P/'scripts/validate.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
doc=r(W/P/'sources.json');selections=doc['selections'];external={x['path']:x['sha256'] for x in r(W/P/'migration.json')['external_records']};report=[]
for row in doc['sources']:
 rel=row['path'];candidates=[R.parent/rel,R.parent/'cya-orquestrator'/rel,*sorted((R/'.local').glob('ontology-context-import-*/package/'+rel)),*sorted((R/'.local').glob('*/'+rel))]
 if rel.startswith('arcanum/'):
  candidates += [R.parent/'domainspec-core/.agents/skills/invoke'/rel.removeprefix('arcanum/')]
 candidates=list(dict.fromkeys(p for p in candidates if p.is_file()));sels=[x for x in selections if x['source_id']==row['source_id']]
 def matches(p):
  raw=p.read_bytes()
  if rel in external and sha(p)!=external[rel]:return False
  try:
   try:parsed=json.loads(raw)
   except Exception:parsed=None
   return all(hashlib.sha256(v.selected_bytes(x,raw,parsed)).hexdigest()==x['selection_sha256'] for x in sels)
  except Exception:return False
 exact=next((p for p in candidates if sha(p)==row['observed_file_sha256'] and matches(p)),None);selected=exact or next((p for p in candidates if matches(p)),None)
 fallback=selected or (candidates[0] if candidates else None)
 if fallback:
  dst=W/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(fallback,dst)
 report.append({'source_id':row['source_id'],'path':rel,'recovered_from':str(fallback) if fallback else None,'sha256':sha(fallback) if fallback else None,'selected_bytes_match':selected is not None,'containing_file_match':exact is not None,'selection_count':len(sels)})
dump(H/'source-recovery.json',report)
c=subprocess.run(['python3',str(W/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/'source-validation.json',{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});print(c.stdout)
files=sorted(p for p in W.rglob('*') if p.is_file());dump(H/'package-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
print('Unrecovered:',[x['source_id'] for x in report if not x['selected_bytes_match']])
