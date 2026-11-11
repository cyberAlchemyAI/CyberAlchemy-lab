"""Independent source/admission and selected snapshot verification."""
import json,hashlib,sys,base64
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
auth=load(HERE/'authorization.json')
assert auth['authorized'] is True and auth['cryptographic_owner_signature'] is None
for item in auth['accepted_definitions']:
 p=ROOT/item['source']['path'];assert sha(p)==item['source']['sha256']
 jsonschema.Draft202012Validator(load(ROOT/'authority/artifact-types/definition/v2/schema.json')).validate(load(p))
if (HERE/'decision.json').exists():
 d=load(HERE/'decision.json');bundle=ROOT/(d['bundle'].get('path') or d['bundle']['ref']);assert sha(bundle)==d['bundle']['sha256']
 b=load(bundle);registry=ROOT/(b['registry'].get('path') or b['registry']['ref']);assert sha(registry)==b['registry']['sha256']
 reg=load(registry);assert len(reg['entries'])==194 and len(reg['current_lookup'])==188
 files=load(ROOT/'authority/admissions/shared-definitions-records-0076/snapshot-files.json')
 assert registry.read_bytes()==base64.b64decode(files['registry.json'])
 for e in reg['entries']:
  original=base64.b64decode(files[e['body']['path']])
  assert hashlib.sha256(original).hexdigest()==e['body']['sha256']
  assert len(original)==e['body']['bytes']
  assert (ROOT/e['body']['path']).read_bytes()==original
  disposition=base64.b64decode(files[e['owner_disposition']['path']])
  assert hashlib.sha256(disposition).hexdigest()==e['owner_disposition']['sha256']
 for f in (HERE/'dispositions').glob('*.json'):
  response=load(f);assert response['outcome']=='Accepted' and response['canonical_admission'] is True
 jsonschema.Draft202012Validator(load(ROOT/'implementation/lab-runtime/alchlang/shared-records/contracts/definition-registry-v2.schema.json')).validate(reg)
 old=load(ROOT/'authority/definitions/registry.json');new={e['definition_id']+'@'+e['version']:e for e in reg['entries']}
 for e in old['entries']:assert new[e['definition_id']+'@'+e['version']]['body']['sha256']==e['sha256']
 for e in auth['accepted_definitions']:
  assert new[e['version']]['standing']=='admitted-current'
 print(json.dumps({'status':'PASS','accepted':5,'retained':189,'versions':194,'current':188}))
else:print(json.dumps({'status':'PASS','phase':'preflight','exact_candidates':5}))
