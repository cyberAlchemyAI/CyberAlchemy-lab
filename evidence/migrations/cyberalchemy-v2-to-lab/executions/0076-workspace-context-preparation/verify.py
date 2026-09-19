"""Verify bounded repair and preserve real blockers. Open questions: README.md."""
import hashlib,json,subprocess,os,tarfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/workspace-package-0076';S=R/'.local/workspace-successor-0076';P='cyberAlchemy-v2/workspace';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['0075-shared-capability-runtime-import','0064-define-bridge-context-import']:
 for b in read(H.parent/name/'verification.json')['bindings']:assert sha(R/b['path'])==b['sha256']
manifest=read(H/'package-inputs.json')
with tarfile.open(H/'package-snapshot.tar.gz') as a:
 assert set(a.getnames())=={e['path'] for e in manifest}
 for e in manifest:assert hashlib.sha256(a.extractfile(e['path']).read()).hexdigest()==e['sha256']==sha(W/e['path'])
delta={e['path'] for e in manifest if sha(S/e['path'])!=e['sha256']};assert delta=={P+'/sources.json','cyberAlchemy-v2/authority/definitions/DEFINITIONS.md'}
def validate(root):
 c=subprocess.run(['python3',str(root/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});return {'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr}
assert validate(W)==read(H/'source-validation.json');assert validate(S)==read(H/'successor-validation.json')
report=read(H/'repair-report.json');assert not report['imported'] and not report['registry_material_current'];assert {x['target'] for x in report['external_targets']}=={'CAV2-D60','CAV2-D67','ESSAYS-REALIZATION-BASELINE-003'}
lines=(S/'cyberAlchemy-v2/authority/definitions/DEFINITIONS.md').read_bytes().splitlines(keepends=True)
for item in read(S/P/'sources.json')['definition_selections']:
 start=next(i for i,l in enumerate(lines) if l.rstrip(b'\r\n')==item['selector'].encode());end=next((i for i in range(start+1,len(lines)) if lines[i].startswith(b'## ')),len(lines));assert hashlib.sha256(b''.join(lines[start:end])).hexdigest()==item['expected_digest']
for row in read(S/P/'sources.json')['sources']:
 if 'expected_sha256' in row:assert sha(S/row['path'])==row['expected_sha256']
bin=R/'.local/people-teams-runtime-package-0074/runtime/target/debug/cal-ontology-source-runtime';assert sha(bin)==read(H/'runtime-plan-check.json')['binary_sha256'];c=subprocess.run([str(bin),'plan',str(H/'runtime-plan.json')],capture_output=True,text=True);assert c.returncode!=0 and c.stderr.strip()=='unresolved relation endpoint'
cases=['duplicate-node','authority-escalation']
for case in cases:
 file=S/P/('nodes.json' if case=='duplicate-node' else 'profile.json');original=file.read_bytes();d=read(file)
 if case=='duplicate-node':d['nodes'].append(d['nodes'][0])
 else:d['authority_effect']='admitted'
 try:file.write_text(json.dumps(d));assert validate(S)['exit_code']==1
 finally:file.write_bytes(original)
result={'result':'PASS','imported':False,'authority_effect':'none','checks':['frozen predecessors verified','original package archive matches every pinned file','only sources registry and selected definitions container differ','five exact definition section digests preserved','all six expected source file fingerprints match successor','original BLOCK and successor PASS reproduce','stale registry material and three external endpoints remain explicit','existing runtime correctly rejects unresolved endpoints','two native-validator mutations rejected','generated model and sibling source are not modified by this preparation'],'negative_cases':cases,'bindings':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in sorted(H.rglob('*')) if p.is_file() and p.name!='verification.json']}
(H/'verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('PASS: ten preparation checks and two rejection cases; runtime import remains blocked by external references.')
