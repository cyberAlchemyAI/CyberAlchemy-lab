"""Verify explicit source projections and exact existing-runtime replay. See README.md."""
import hashlib,json,subprocess,os,shutil,tempfile,tarfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/workspace-runtime-package-0077';STORE=R/'.local/workspace-runtime-0077';P='cyberAlchemy-v2/workspace';BIN=R/'.local/people-teams-runtime-package-0074/runtime/target/debug/cal-ontology-source-runtime';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):
 text=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=text:raise ValueError('Existing evidence differs: '+str(p))
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def hashes(root):return {str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}
def run(*args):return subprocess.run([str(BIN),*map(str,args)],capture_output=True,text=True,timeout=30)
def ok(*args):
 c=run(*args);assert c.returncode==0,c.stderr;return json.loads(c.stdout)
for folder in ['0076-workspace-context-preparation','0074-people-teams-runtime-import']:
 for b in r(H.parent/folder/'verification.json')['bindings']:assert sha(R/b['path'])==b['sha256']
assert sha(BIN)==r(H.parent/'0074-people-teams-runtime-import/verification.json')['binary']['sha256']
for e in r(H/'package-inputs.json'):assert sha(W/e['path'])==e['sha256']
source_before=hashes(W);plan=r(H/'runtime-manifest.json');workspace,external=plan['packages'];assert len(workspace['documents'])==41
refs=r(W/'adapters/workspace-external-references.json')['nodes'];assert len(refs)==3
for ref in refs:
 p=W/ref['source_path']
 if ref['selector']=='/':assert ref['source_record']==r(p) and ref['selected_sha256']==sha(p)
 else:
  lines=p.read_bytes().splitlines(keepends=True);i=next(i for i,l in enumerate(lines) if l.rstrip(b'\r\n')==ref['selector'].encode());j=next((j for j in range(i+1,len(lines)) if lines[j].startswith(b'## ')),len(lines));raw=b''.join(lines[i:j]);assert ref['selected_text'].encode()==raw and hashlib.sha256(raw).hexdigest()==ref['selected_sha256']
original=r(W/P/'relations.json');projected=r(W/'adapters/workspace-relations.json');reverse={x['runtime_target']:x['source_target'] for x in r(H/'endpoint-mappings.json')};reversed_edges=json.loads(json.dumps(projected))
for e in reversed_edges['relations']:e['target']=reverse.get(e['target'],e['target'])
assert reversed_edges==original
registry=r(W/'cyberAlchemy-v2/implementation/ontology-runtime/registry.json');entry=next(e for e in registry['entries'] if e['ontology_id']=='cav2.workspace.capability');h=hashlib.sha256()
for name in sorted(entry['material_files']):h.update(name.encode()+b'\0'+(W/P/name).read_bytes()+b'\0')
assert entry['expected_material_digest']==h.hexdigest()==r(H/'registration-change.json')['after']
oldregistry=r(R/'.local/workspace-successor-0076/cyberAlchemy-v2/implementation/ontology-runtime/registry.json');restored=json.loads(json.dumps(registry));next(e for e in restored['entries'] if e['ontology_id']=='cav2.workspace.capability')['expected_material_digest']=r(H/'registration-change.json')['before'];assert restored==oldregistry
c=subprocess.run(['python3',str(W/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});assert c.returncode==0 and c.stdout==r(H/'source-validation.json')['stdout']
if STORE.exists():assert (H/'store-bindings.json').exists() and hashes(STORE)==r(H/'store-bindings.json')
else:
 assert not (H/'store-bindings.json').exists();dump(H/'import-receipt.json',ok('import',H/'runtime-manifest.json',STORE))
state=hashes(STORE);export=ok('export',STORE);assert export==ok('export',STORE);summary=ok('summary',STORE);observation=ok('observe',STORE,workspace['package_key'])
assert [summary[k] for k in ['nodes','relations','documents','semantic_events','governance_events','latest_snapshots']]==[15,14,41,70,70,70]
assert observation['context_nodes']==56 and observation['context_relations']==14
assert len(ok('export',STORE,workspace['package_key'])['records'])==67 and len(ok('export',STORE,external['package_key'])['records'])==3
seen=set()
for rec in export['records']:
 b=rec['source_binding'];key=(b['package_key'],b['path'],b['selector']);assert key not in seen;seen.add(key);p=W/b['path'];assert sha(p)==b['sha256'];value=rec['source_record']
 if b['selector']=='/document':assert value['content'].encode()==p.read_bytes() and value['content_sha256']==sha(p)
 else:
  obj=r(p)
  for k in b['selector'].strip('/').split('/'):obj=obj[int(k)] if isinstance(obj,list) else obj[k]
  assert obj==value
assert len(seen)==70
with tempfile.TemporaryDirectory(prefix='workspace-runtime-0077-') as tmp:
 t=Path(tmp);fresh=t/'fresh';ok('import',H/'runtime-manifest.json',fresh);assert hashes(fresh)==state and ok('export',fresh)==export
 assert run('import',H/'runtime-manifest.json',fresh).returncode!=0 and hashes(fresh)==state
 assert run('export',fresh,'missing').returncode!=0
 bad=t/'bad';shutil.copytree(fresh,bad);p=bad/'transaction-00000001.json';d=r(p);d['digest']='0'*64;p.write_text(json.dumps(d));assert run('export',bad).returncode!=0
 missing=json.loads(json.dumps(plan));missing['packages']=missing['packages'][:1];p=t/'missing-endpoints.json';p.write_text(json.dumps(missing));assert run('plan',p).returncode!=0
assert hashes(STORE)==state and hashes(W)==source_before
for name,obj in [('summary.json',summary),('export.json',export),('workspace-observation.json',observation),('store-bindings.json',state)]:dump(H/name,obj)
if not (H/'runtime-store.tar.gz').exists():
 with tarfile.open(H/'runtime-store.tar.gz','w:gz') as a:
  for p in sorted(STORE.iterdir()):a.add(p,arcname=p.name,recursive=False)
with tarfile.open(H/'runtime-store.tar.gz') as a:
 assert set(a.getnames())==set(state)
 for name,digest in state.items():assert hashlib.sha256(a.extractfile(name).read()).hexdigest()==digest
dump(H/'verification.json',{'result':'PASS','authority_effect':'none','runtime_store':str(STORE.relative_to(R)),'counts':{'workspace_nodes':12,'external_reference_nodes':3,'relations':14,'documents':41,'event_pairs':70},'checks':['frozen predecessors and exact tested runtime binary verified','all pinned source inputs unchanged','three explicit reference projections match exact selected source content','three qualified targets reverse to original relationship records','only Workspace registry material fingerprint changes and matches independently','native source validator reproduces PASS','all seventy runtime subjects export exactly','Workspace context includes all three external endpoints','two separate-process reads and independent fresh import match','overwrite unknown package corruption and missing dependency rejected','source and committed store unchanged by reads','runtime archive matches committed files'],'negative_cases':['existing-target','unknown-package','transaction-corruption','missing-reference-package'],'bindings':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in sorted(H.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: twelve import checks and four rejection cases; Workspace replay/export and external references verified.')
