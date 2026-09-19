"""Pin Workspace's declared semantic package only. Open questions: README.md."""
import ast,json,hashlib,shutil,subprocess,os,tarfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/workspace-package-0076';P='cyberAlchemy-v2/workspace';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
script=R.parent/P/'scripts/validate.py';tree=ast.parse(script.read_text());names=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MATERIAL_FILES' for t in n.targets))
for name in names:
 dst=W/P/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R.parent/P/name,dst)
report=[]
for row in r(W/P/'sources.json')['sources']:
 rel=row['path'];candidates=[R.parent/rel,R.parent/'cya-orquestrator'/rel,*sorted((R/'.local').glob('ontology-context-import-*/package/'+rel)),*sorted((R/'.local').glob('*/'+rel))];candidates=list(dict.fromkeys(p for p in candidates if p.is_file()));selected=next((p for p in candidates if sha(p)==row.get('expected_sha256')),None)
 if row['posture']=='self-registration-bound-runtime-source':selected=R.parent/rel
 src=selected or (candidates[0] if candidates else None)
 if src:dst=W/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 report.append({'source_id':row['source_id'],'path':rel,'recovered_from':str(src) if src else None,'sha256':sha(src) if src else None,'exact_expected_hash':bool(selected) if 'expected_sha256' in row else None,'posture':row['posture']})
dump(H/'source-recovery.json',report)
c=subprocess.run(['python3',str(W/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/'source-validation.json',{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});print(c.stdout)
files=sorted(p for p in W.rglob('*') if p.is_file());dump(H/'package-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
