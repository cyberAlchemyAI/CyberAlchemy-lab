"""Reproduce the import and reject corrupted bindings. Open questions: README.md."""
import importlib.util,json,subprocess,os
from pathlib import Path
H=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('impl_import',H/'import.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);b=m.build();p=m.PACKAGE/m.PREFIX
for ref in b['ontology']['concept_refs']:
 file,ptr=ref.split('#');obj=m.r(m.STORE/file)
 for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
 assert isinstance(obj,dict)
checks={f.stem:m.r(f) for f in (H/'checks').glob('*.json')}
for name in ['rust-version','fmt','clippy','test','browser-syntax']:assert checks[name]['exit_code']==0,(name,checks[name]['stderr'][-300:])
assert '1.94.0' in checks['rust-version']['stdout'];assert 'test result: ok. 11 passed; 0 failed' in checks['test']['stdout'];assert 'test result: ok. 3 passed; 0 failed' in checks['test']['stdout']
# Bind test receipts to the entire unchanged implementation snapshot.
for e in m.r(H/'package-inputs.json'):
 assert m.tool.sha(m.PACKAGE/e['path'])==e['sha256']
 if e['path'].startswith(m.IMPL+'/'):assert m.tool.sha(m.ROOT/'.local/essays-implementation-package-0071'/e['path'])==e['sha256']
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
cases=['wrong-file-digest','unknown-system-node','duplicate-trace-obligation','authority-escalation']
for case in cases:
 name='IMPLEMENTATION-MANIFEST.json' if case=='wrong-file-digest' else ('TRACEABILITY.json' if case=='duplicate-trace-obligation' else 'BINDING.json');path=p/name;original=path.read_bytes();d=m.r(path)
 if case=='wrong-file-digest':d['files'][0]['sha256']='0'*64
 elif case=='unknown-system-node':d['implementation_surfaces'][0]['system_nodes'].append('system:missing')
 elif case=='duplicate-trace-obligation':d['entries'].append(d['entries'][0])
 else:d['authority_effect']='admitted'
 try:
  path.write_text(json.dumps(d));c=subprocess.run(['python3',str(p/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});assert c.returncode==1 and json.loads(c.stdout)['overall']=='BLOCK'
 finally:path.write_bytes(original)
assert m.r(m.STORE/'bundle.json')==b
m.dump(H/'verification.json',{'result':'PASS','authority_effect':'none','checks':['frozen predecessors and admitted migration headers validate','all 40 exact implementation files preserved','seven source-inspected model mappings resolve to matching file fingerprints and selectors','sixteen files classified and no inventory placeholders remain','source validator reproduces 340 checks with no errors','all twenty obligation trace rows remain partial','candidate source record pointers resolve without invented graph relations','Rust version formatting lint runtime tests and browser syntax receipts pass','test receipt inputs match the entire pinned implementation','desktop result and remaining conformance gaps explicitly retained','four malformed bindings rejected by unchanged validator','capability inventory and imported bundle unchanged'],'negative_cases':cases,'bindings':[m.bind(p) for p in sorted(H.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: twelve import checks and four binding rejection cases.')
