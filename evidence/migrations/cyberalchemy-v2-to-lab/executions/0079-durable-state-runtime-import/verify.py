"""Verify the authorized scope removal, source checks, and existing-runtime import."""
import hashlib,json,subprocess,os,tarfile,tempfile,shutil
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/durable-state-package-0079';OLD=R/'.local/durable-state-successor-0078';P='cyberAlchemy-v2/durable-storage';STORE=R/'.local/durable-state-runtime-0079';BIN=R/'.local/people-teams-runtime-package-0074/runtime/target/debug/cal-ontology-source-runtime'
r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def hashes(root):return {str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}
def run(*args):return subprocess.run([str(BIN),*map(str,args)],capture_output=True,text=True,timeout=30)
def ok(*args):
 c=run(*args);assert c.returncode==0,c.stderr;return json.loads(c.stdout)
for folder in ['0078-durable-state-preparation','0074-people-teams-runtime-import']:
 for b in r(H.parent/folder/'verification.json')['bindings']:assert sha(R/b['path'])==b['sha256']
assert sha(BIN)==r(H.parent/'0074-people-teams-runtime-import/verification.json')['binary']['sha256']
inputs=r(H/'package-inputs.json');before=hashes(W);assert before=={x['path']:x['sha256'] for x in inputs}
with tarfile.open(H/'package-snapshot.tar.gz') as a:
 assert set(a.getnames())==set(before)
 for name,digest in before.items():assert hashlib.sha256(a.extractfile(name).read()).hexdigest()==digest
old=r(OLD/P/'storage-requirements.json');new=r(W/P/'storage-requirements.json');expected=json.loads(json.dumps(old));expected['requirements'].remove(r(H/'scope-change.json')['removed_requirement']);expected['coverage_basis']['external_agent_capability_reference_count']=0;expected['requirements'][0]['claim_limit']='Does not adopt Define or implement saved sessions.';assert expected==new and len(new['requirements'])==12
assert all(x['subject_kind']=='product-capability' for x in new['requirements'])
for file in ['nodes.json','relations.json','storage-classes.json','product-capability.json','sources.json']:assert (W/P/file).read_bytes()==(OLD/P/file).read_bytes()
for p in (OLD/P/'receipts').glob('*.json'):assert p.read_bytes()==(W/'historical/durable-storage-receipts'/p.name).read_bytes()
c=subprocess.run(['python3',str(W/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});assert c.returncode==0 and c.stdout==r(H/'source-validation.json')['stdout'];assert r(H/'negative-tests.json')['exit_code']==0
manifest=r(H/'runtime-manifest.json');pkg=manifest['packages'][0];dump(H/'plan.json',ok('plan',H/'runtime-manifest.json'))
if STORE.exists():assert hashes(STORE)==r(H/'store-bindings.json')
else:dump(H/'import-receipt.json',ok('import',H/'runtime-manifest.json',STORE))
state=hashes(STORE);summary=ok('summary',STORE);export=ok('export',STORE);assert export==ok('export',STORE);n=len(inputs);assert [summary[k] for k in ['nodes','relations','documents','semantic_events','governance_events']]==[25,22,n,47+n,47+n]
assert len(export['records'])==47+n
for rec in export['records']:
 b=rec['source_binding'];p=W/b['path'];assert sha(p)==b['sha256']
 if b['selector']=='/document':assert rec['source_record']['content'].encode()==p.read_bytes()
 else:
  obj=r(p)
  for k in b['selector'].strip('/').split('/'):obj=obj[int(k)] if isinstance(obj,list) else obj[k]
  assert obj==rec['source_record']
with tempfile.TemporaryDirectory(prefix='durable79-') as tmp:
 t=Path(tmp);fresh=t/'fresh';ok('import',H/'runtime-manifest.json',fresh);assert hashes(fresh)==state and ok('export',fresh)==export
 assert run('import',H/'runtime-manifest.json',fresh).returncode!=0 and hashes(fresh)==state
 assert run('export',fresh,'missing').returncode!=0
 bad=t/'bad';shutil.copytree(fresh,bad);p=bad/'transaction-00000001.json';d=r(p);d['digest']='0'*64;dump(p,d);assert run('export',bad).returncode!=0
assert hashes(W)==before and hashes(STORE)==state
assert (R/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(H.parent/'0035-definition-card-import/imports.json').read_bytes()
for name,obj in [('summary.json',summary),('export.json',export),('store-bindings.json',state),('observation.json',ok('observe',STORE,pkg['package_key']))]:dump(H/name,obj)
if not (H/'runtime-store.tar.gz').exists():
 with tarfile.open(H/'runtime-store.tar.gz','w:gz') as a:
  for p in sorted(STORE.iterdir()):a.add(p,arcname=p.name,recursive=False)
with tarfile.open(H/'runtime-store.tar.gz') as a:
 assert set(a.getnames())==set(state)
 for name,digest in state.items():assert hashlib.sha256(a.extractfile(name).read()).hexdigest()==digest
dump(H/'verification.json',{'result':'PASS','authority_effect':'none','counts':summary,'checks':['frozen predecessors and tested runtime binary verified','package archive and source bindings exact','only obsolete external requirement removed; twelve product subjects retained','business graph and storage classes unchanged','historical receipts preserved outside active receipt directory','revised native validator PASS and twelve source tests PASS','all runtime records export exact source content','fresh import and repeated export deterministic','overwrite unknown package and corruption rejected','source and store unchanged by reads','capability inventory unchanged','runtime archive exact'],'bindings':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in sorted(H.rglob('*')) if p.is_file() and p.name!='verification.json']});print('PASS',summary)
