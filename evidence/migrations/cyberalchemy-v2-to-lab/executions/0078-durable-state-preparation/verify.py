"""Verify pinned preparation and preserve the unresolved owner boundary. See README.md."""
import hashlib,json,subprocess,os,tarfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/durable-state-package-0078';S=R/'.local/durable-state-successor-0078';P='cyberAlchemy-v2/durable-storage';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['0077-workspace-runtime-import','0038-durable-storage-context-import']:
 for b in r(H.parent/name/'verification.json')['bindings']:assert sha(R/b['path'])==b['sha256']
manifest=r(H/'package-inputs.json')
with tarfile.open(H/'package-snapshot.tar.gz') as a:
 assert set(a.getnames())=={x['path'] for x in manifest}
 for x in manifest:assert hashlib.sha256(a.extractfile(x['path']).read()).hexdigest()==sha(W/x['path'])==x['sha256']
assert {x['path'] for x in manifest if sha(S/x['path'])!=x['sha256']}=={P+'/sources.json'}
report=r(H/'repair-report.json');assert not report['imported'] and len(report['fingerprint_successors'])==4
original=r(W/P/'sources.json');successor=r(S/P/'sources.json')
for row in successor['sources']:
 old=next(x for x in original['sources'] if x['source_id']==row['source_id'])
 if row!=old:
  expected=dict(old);expected['sha256']=sha(S/row['path']);assert row==expected
for root,name in [(W,'source-validation'),(S,'successor-validation')]:
 c=subprocess.run(['python3',str(root/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});saved=r(H/(name+'.json'));assert c.returncode==saved['exit_code']==1 and json.loads(c.stdout)==json.loads(saved['stdout'])
assert len(json.loads(r(H/'source-validation.json')['stdout'])['errors'])==5
assert json.loads(r(H/'successor-validation.json')['stdout'])['errors']==[report['remaining_blocker']]
requirements=r(S/P/'storage-requirements.json');rows=next(v for v in requirements.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'subject_ref' in v[0]);external=next(x for x in rows if x['subject_ref']==report['missing_subject']);assert external['binding_state']==external['need_posture']=='external-owner' and external['artifact_kinds']==[] and external['durability_class_refs']==[]
assert report['nearby_reference']['capability_ref']!=report['missing_subject']
assert (R/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(H.parent/'0035-definition-card-import/imports.json').read_bytes()
result={'result':'PASS','imported':False,'authority_effect':'none','checks':['frozen preceding runtime and distinct encrypted-storage context verified','complete original source archive matches snapshot','only four source fingerprint fields change in successor','five original errors and one remaining successor error reproduce','external agent identity not replaced by private Define CLI','external-owner requirement retains no assigned storage or provider','all other model and evidence records preserved','capability inventory unchanged'],'bindings':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in sorted(H.rglob('*')) if p.is_file() and p.name!='verification.json']}
(H/'verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('PASS: eight preparation checks; one source blocker remains, no runtime import.')
