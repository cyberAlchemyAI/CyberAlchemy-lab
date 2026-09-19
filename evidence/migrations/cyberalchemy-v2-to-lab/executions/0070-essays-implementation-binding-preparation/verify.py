"""Verify preparation and real validator rejection cases. Open questions: README.md."""
import hashlib,json,os,subprocess,tarfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/essays-binding-package-0070';S=R/'.local/essays-binding-successor-0070';BASE='cyberAlchemy-v2/essays/development/agent-runtime/';P=BASE+'conformance/implementation-binding';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for folder in ['0068-essays-system-context-import','0069-essays-conformance-bridge-import']:
 for b in r(H.parent/folder/'verification.json')['bindings']:assert sha(R/b['path'])==b['sha256']
manifest=r(H/'package-inputs.json')
with tarfile.open(H/'package-snapshot.tar.gz') as a:
 assert set(a.getnames())=={x['path'] for x in manifest}
 for x in manifest:assert hashlib.sha256(a.extractfile(x['path']).read()).hexdigest()==x['sha256']==sha(W/x['path'])
for x in manifest:
 if x['path'].startswith(BASE+'implementation/'):assert sha(S/x['path'])==x['sha256']
def validate(root):
 c=subprocess.run(['python3',str(root/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});return {'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr}
assert validate(W)==r(H/'source-validation.json');assert validate(S)==r(H/'successor-validation.json')
for name in ['BINDING.json','TRACEABILITY.json','IMPLEMENTATION-MANIFEST.json']:assert (S/P/name).read_bytes()==(H/'successor'/name).read_bytes()
trace=r(S/P/'TRACEABILITY.json');assert len(trace['entries'])==20 and all(x['posture']=='partial' for x in trace['entries'])
b=r(S/P/'BINDING.json');report=r(H/'repair-report.json');assert len(report['unassigned_files'])==16 and len(report['unmapped_system_nodes'])==7 and not report['imported']
placeholders={x['surface_id']:x for x in b['implementation_surfaces']};assert placeholders['unassigned-current-source-files']['system_nodes']==[];assert placeholders['unmapped-current-model-nodes']['files']==[]
assert (W/P/'RESIDUE.json').read_bytes()==(S/P/'RESIDUE.json').read_bytes()
cases=['dependency-fingerprint','authority-escalation','missing-manifest-entry']
for case in cases:
 path=S/P/('IMPLEMENTATION-MANIFEST.json' if case=='missing-manifest-entry' else 'BINDING.json');original=path.read_bytes();d=r(path)
 if case=='dependency-fingerprint':d['dependency_digests']['compiled_graph_sha256']='0'*64
 elif case=='authority-escalation':d['authority_effect']='admitted'
 else:d['files'].pop()
 try:
  path.write_text(json.dumps(d));result=validate(S);assert result['exit_code']==1 and json.loads(result['stdout'])['overall']=='BLOCK'
 finally:path.write_bytes(original)
assert r(H/'runtime-check.json')['exit_code']!=0 and 'missing manifest' in r(H/'runtime-check.json')['stderr']
assert (R/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(H.parent/'0035-definition-card-import/imports.json').read_bytes()
result={'result':'PASS','authority_effect':'none','imported':False,'checks':['frozen predecessor evidence unchanged','archive exactly matches original snapshot','original validator reproduces ninety errors','successor validator reproduces 319 checks and zero errors','all three successor files reproduce','implementation bytes unchanged','twenty proof states remain partial','unmapped nodes and unassigned files remain separate','fourteen original residue statements preserved','three validator mutation cases rejected','runtime setup failure recorded without test pass','capability inventory unchanged'],'negative_cases':cases,'bindings':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in sorted(H.rglob('*')) if p.is_file() and p.name!='verification.json']}
(H/'verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('PASS: twelve preparation checks; three validator rejection cases. Runtime verification blocked; no import.')
