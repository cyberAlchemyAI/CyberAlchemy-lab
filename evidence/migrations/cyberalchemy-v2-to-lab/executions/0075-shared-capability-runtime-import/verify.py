"""Import into an isolated store and verify exact replay/export. Open questions: README.md."""
import hashlib,json,subprocess,shutil,tempfile,tarfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/shared-capability-package-0075';STORE=R/'.local/shared-capability-runtime-0075';BIN=R/'.local/people-teams-runtime-package-0074/runtime/target/debug/cal-ontology-source-runtime';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):
 text=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=text:raise ValueError('Existing evidence differs: '+str(p))
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def hashes(root):return {str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}
def run(*args):
 c=subprocess.run([str(BIN),*map(str,args)],capture_output=True,text=True,timeout=30);return {'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr}
def ok(*args):
 result=run(*args);assert result['exit_code']==0,result;return json.loads(result['stdout'])
def run_source_validation():
 c=subprocess.run(['python3',str(W/'cyberAlchemy-v2/capability/scripts/validate.py')],capture_output=True,text=True,env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1'});assert c.returncode==0;d=json.loads(c.stdout);d.pop('validated_at');return d
for name in ['0074-people-teams-runtime-import']:
 for b in read(H.parent/name/'verification.json')['bindings']:assert sha(R/b['path'])==b['sha256']
manifest=read(H/'package-inputs.json')
for e in manifest:assert sha(W/e['path'])==e['sha256']
assert sha(BIN)==read(H.parent/'0074-people-teams-runtime-import/verification.json')['binary']['sha256']
assert read(H/'source-negative-tests.json')['exit_code']==1
assert read(H/'corrected-negative-tests.json')['exit_code']==0
c=subprocess.run(['python3',str(H/'check_negative_tests.py')],capture_output=True,text=True,env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1'});assert c.returncode==0 and c.stdout==read(H/'corrected-negative-tests.json')['stdout']
assert json.loads(read(H/'source-negative-tests.json')['stdout'])['cases']==17
result=run_source_validation()
assert result=={k:v for k,v in json.loads(read(H/'source-validation.json')['stdout']).items() if k!='validated_at'}
plan=read(H/'runtime-manifest.json');package=plan['packages'][0];source=W;source_before=hashes(source);docs=len(package['documents']);total=44+docs
for s in [package['profile'],package['nodes']['source'],package['relations']['source'],*package['documents']]:assert sha(source/s['path'])==s['sha256']
# Existing targets are never silently initialized or replaced.
if STORE.exists():
 assert (H/'store-bindings.json').exists(),'Existing target lacks this execution receipt'
 assert hashes(STORE)==read(H/'store-bindings.json')
else:
 assert not (H/'store-bindings.json').exists(),'Recorded target is missing; restore explicitly'
 for p in STORE.parents:assert not p.is_symlink()
 receipt=ok('import',H/'runtime-manifest.json',STORE);dump(H/'import-receipt.json',receipt)
store_before=hashes(STORE)
summary=ok('summary',STORE);first=ok('export',STORE);second=ok('export',STORE);observe=ok('observe',STORE)
assert first==second and first==ok('export',STORE,package['package_key'])
assert summary['nodes']==25 and summary['relations']==19 and summary['documents']==docs
assert summary['semantic_events']==summary['governance_events']==summary['latest_snapshots']==total
assert observe['context_relations']==19 and observe['context_nodes']==25+docs
seen=set()
for record in first['records']:
 binding=record['source_binding'];value=record['source_record'];key=(binding['path'],binding['selector']);assert key not in seen;seen.add(key);p=source/binding['path'];assert sha(p)==binding['sha256']
 if binding['selector']=='/document':assert value['content'].encode()==p.read_bytes() and value['content_sha256']==sha(p)
 else:
  expected=read(p)
  for k in binding['selector'].strip('/').split('/'):expected=expected[int(k)] if isinstance(expected,list) else expected[k]
  assert value==expected
expected={(s['path'],'/document') for s in package['documents']}
for key in ['nodes','relations']:
 reg=package[key];rows=read(source/reg['source']['path'])[key];expected|={(reg['source']['path'],reg['selector']+'/'+str(i)) for i in range(len(rows))}
assert seen==expected and len(seen)==total
with tempfile.TemporaryDirectory(prefix='people-runtime-0074-') as tmp:
 root=Path(tmp);fresh=root/'fresh';ok('import',H/'runtime-manifest.json',fresh);assert hashes(fresh)==store_before;assert ok('export',fresh)==first
 assert run('import',H/'runtime-manifest.json',fresh)['exit_code']!=0;assert hashes(fresh)==store_before
 assert run('export',fresh,'missing-package')['exit_code']!=0
 for case in ['transaction-corruption','head-corruption']:
  bad=root/case;shutil.copytree(STORE,bad);file=bad/('HEAD.json' if case=='head-corruption' else 'transaction-00000001.json');d=read(file);d['digest']='0'*64;file.write_text(json.dumps(d));assert run('export',bad)['exit_code']!=0
assert hashes(STORE)==store_before and hashes(source)==source_before
for name,obj in [('summary.json',summary),('export.json',first),('observation.json',observe),('store-bindings.json',store_before)]:dump(H/name,obj)
if not (H/'runtime-store.tar.gz').exists():
 with tarfile.open(H/'runtime-store.tar.gz','w:gz') as a:
  for p in sorted(STORE.iterdir()):a.add(p,arcname=p.name,recursive=False)
with tarfile.open(H/'runtime-store.tar.gz') as a:
 assert set(a.getnames())==set(store_before)
 for name,digest in store_before.items():assert hashlib.sha256(a.extractfile(name).read()).hexdigest()==digest
dump(H/'verification.json',{'result':'PASS','authority_effect':'none','runtime_store':str(STORE.relative_to(R)),'binary':{'path':str(BIN.relative_to(R)),'sha256':sha(BIN)},'counts':{'nodes':25,'relations':19,'documents':docs,'event_pairs':total},'checks':['frozen predecessors and complete source snapshot match','same exact v4 binary with 23 passing tests from 0074 reused; source validation and seventeen hostile cases pass','manifest fingerprints match all source records and documents','isolated import yields exact semantic/governance event pairs','two process restarts export identical records','all 44 graph records and every supporting document match original values/bytes','context includes all relation endpoints','independent fresh import produces byte-identical stored files','existing target overwrite and unknown package rejected','corrupt transaction and corrupt head rejected','observation leaves stored history and source unchanged'],'negative_cases':['existing-target','unknown-package','transaction-corruption','head-corruption'],'bindings':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in sorted(H.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: eleven runtime import checks and four rejection cases; exact replay and export verified.')
