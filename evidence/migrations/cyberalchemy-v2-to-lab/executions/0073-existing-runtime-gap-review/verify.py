"""Verify pinned comparison and read-only plan smoke checks. Open questions: README.md."""
import copy,json,hashlib,subprocess,tempfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
prev=H.parent/'0072-people-teams-context-import'
for b in r(prev/'verification.json')['bindings']:assert sha(R/b['path'])==b['sha256']
for b in r(H/'source-bindings.json'):assert sha(H/b['snapshot_path'])==b['sha256']
coverage=r(H/'package-coverage.json');assert coverage['legacy_registration_count']==6 and coverage['v4_manifest_package_count']==21
assert {x['ontology_id'] for x in coverage['rows'] if x['status']=='absent-from-v4-manifest'}=={'cav2.capability','cav2.workspace.capability','cav2.durable-storage.business','cav2.people-and-teams.business'}
binary=R/'implementation/bindings/ontology-product-event-runtime/v4/target/release/cal-ontology-source-runtime';plan=r(H/'people-teams-plan.json');root=Path(plan['roots']['people72']);before={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}
def run(path):
 c=subprocess.run([str(binary),'plan',str(path)],capture_output=True,text=True,timeout=30);return {'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr}
result=run(H/'people-teams-plan.json');assert result['exit_code']==0;out=json.loads(result['stdout']);assert out=={'authority_effect':'none','event_subjects':65,'packages':1,'result':'PASS'}
assert run(H/'people-teams-plan.json')==result
dump(H/'plan-check.json',{'result':result,'binary':{'path':str(binary.relative_to(R)),'sha256':sha(binary)},'claim_ceiling':'Smoke check of this exact existing binary only; no source-to-binary rebuild attestation or persistent import.','authority_effect':'none'})
cases=['source-digest-drift','missing-node-selector','duplicate-package','authority-escalation']
with tempfile.TemporaryDirectory(prefix='runtime-gap-0073-') as tmp:
 for case in cases:
  d=copy.deepcopy(plan)
  if case=='source-digest-drift':d['packages'][0]['nodes']['source']['sha256']='0'*64
  elif case=='missing-node-selector':d['packages'][0]['nodes']['selector']='/missing'
  elif case=='duplicate-package':d['packages'].append(copy.deepcopy(d['packages'][0]))
  else:d['authority_effect']='admitted'
  p=Path(tmp)/'manifest.json';dump(p,d);assert run(p)['exit_code']!=0,case
assert before=={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}
assert '"FLAG"' not in (H/'source/legacy/runtime.py').read_text()
assert not (R/'.local/ontology-source-runtime-v4-prototype').exists()
dump(H/'verification.json',{'result':'PASS','authority_effect':'none','checks':['frozen People and Teams predecessor verified','comparison snapshots match their captured digests','six registrations compared with twenty-one manifest packages','four missing manifest identities verified without claiming version equality for matches','existing binary plans sixty-five source subjects deterministically','four invalid plans rejected','People and Teams snapshot unchanged','documented demo target absent; no persistent activation inferred'],'negative_cases':cases,'bindings':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in sorted(H.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: eight comparison checks and four plan rejection cases; no runtime imported or activated.')
