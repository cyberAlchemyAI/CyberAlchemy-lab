"""Author the bounded successor without importing or operating its runtime."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
OLD=ROOT/'implementation/lab-runtime/v2';NEW=HERE/'runtime'
def put(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def edit(p,old,new):
 text=p.read_text();assert old in text,(p,old);p.write_text(text.replace(old,new))
assert not NEW.exists()
NEW.mkdir();shutil.copytree(OLD/'lab_runtime',NEW/'lab_runtime',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(OLD/'schemas',NEW/'schemas')
for name in ['profile.json','requirements.txt','lab.py']:shutil.copyfile(OLD/name,NEW/name)
shutil.copyfile(ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/artifact-content-entry.schema.json',NEW/'schemas/artifact-content-entry.schema.json')
edit(NEW/'lab_runtime/cli.py','DEFAULT_REPO = PACKAGE.parents[2]','DEFAULT_REPO = PACKAGE.parents[6]')
edit(NEW/'lab_runtime/cli.py','repo / ".local/lab-runtime/v2/store"','repo / ".local/lab-runtime/byte-custody-v1/store"')
p=NEW/'lab_runtime/operations.py'
edit(p,'from .sources import make_record, resolve, validate_histories, validate_schema','from .sources import make_record, resolve, validate_histories, validate_schema\nfrom .custody import CONTENT_SCHEMA, validate_proposal_content')
edit(p,'def protocol_check(value, schema):','LEGACY_PROPOSAL_SCHEMA = copy.deepcopy(PROPOSAL_SCHEMA)\nCONTENT_PROPOSAL_SCHEMA = copy.deepcopy(PROPOSAL_SCHEMA)\nCONTENT_PROPOSAL_SCHEMA["properties"]["schema_version"] = {"const": "lab-runtime-proposal/v2-candidate"}\nCONTENT_PROPOSAL_SCHEMA["required"].append("schema_contents")\nCONTENT_PROPOSAL_SCHEMA["properties"]["schema_contents"] = {"type": "object", "additionalProperties": CONTENT_SCHEMA}\n_CONTENT_TARGET = CONTENT_PROPOSAL_SCHEMA["properties"]["targets"]["items"]\n_CONTENT_TARGET["required"].append("content")\n_CONTENT_TARGET["properties"]["content"] = {"anyOf": [CONTENT_SCHEMA, {"type": "null"}]}\nPROPOSAL_SCHEMA = {"oneOf": [LEGACY_PROPOSAL_SCHEMA, CONTENT_PROPOSAL_SCHEMA]}\n\n\ndef protocol_check(value, schema):')
edit(p,'protocol_check(proposal, PROPOSAL_SCHEMA)\n    if verify_base:','protocol_check(proposal, PROPOSAL_SCHEMA)\n    validate_proposal_content(proposal)\n    if verify_base:')
edit(p,'entry.update(identity=ident, kind=kind)','if proposal["schema_version"] == "lab-runtime-proposal/v2-candidate":\n            entry["source"].update(sha256=target["content"]["byte_sha256"], encoding="base64-original-json/v1-candidate", content_ref=target["content"]["content_ref"])\n        entry.update(identity=ident, kind=kind)')
edit(p,'projection["subjects"][target["version_ref"]]["source"].update(path=tx_path, selector=f"/proposal/targets/{i}/record", store_id=store_id)','binding = projection["subjects"][target["version_ref"]]["source"]\n            binding.update(path=tx_path, selector=f"/proposal/targets/{i}/record", store_id=store_id)\n            if proposal["schema_version"] == "lab-runtime-proposal/v2-candidate":\n                binding.update(selector=f"/proposal/targets/{i}/content/data", record_selector=f"/proposal/targets/{i}/record")')
p=NEW/'lab_runtime/protocols.py'
edit(p,'from .operations import CATEGORIES, OPERATIONS, PROPOSAL_SCHEMA','from .operations import CATEGORIES, OPERATIONS, PROPOSAL_SCHEMA, LEGACY_PROPOSAL_SCHEMA, CONTENT_PROPOSAL_SCHEMA')
edit(p,'"proposal": PROPOSAL_SCHEMA, "approval": APPROVAL_SCHEMA,','"proposal": LEGACY_PROPOSAL_SCHEMA, "approval": APPROVAL_SCHEMA,')
edit(p,'SCHEMAS = {','LEGACY_TRANSACTION_SCHEMA = TRANSACTION_SCHEMA\nTRANSACTION_SCHEMA = {"oneOf": [LEGACY_TRANSACTION_SCHEMA,\n    closed({**TRANSACTION_COMMON, "schema_version": {"const": "lab-runtime-transaction/v2-candidate"},\n        "kind": {"const": "admission"}, "proposal": CONTENT_PROPOSAL_SCHEMA, "approval": APPROVAL_SCHEMA,\n        "decision_cores": {"type": "array", "minItems": 1}, "consequences": {"type": "object"}})]}\n\nSCHEMAS = {')
p=NEW/'lab_runtime/store.py'
edit(p,'tx["schema_version"] == "lab-runtime-transaction/v1"','tx["schema_version"] in ("lab-runtime-transaction/v1", "lab-runtime-transaction/v2-candidate")')
edit(p,'proposal = tx["proposal"]\n                require','proposal = tx["proposal"]\n                require((tx["schema_version"] == "lab-runtime-transaction/v2-candidate") == (proposal["schema_version"] == "lab-runtime-proposal/v2-candidate"), "transaction/proposal encoding mismatch")\n                require')
edit(p,'tx = sealed({"schema_version": "lab-runtime-transaction/v1", "kind": "admission", "sequence": sequence,','tx = sealed({"schema_version": ("lab-runtime-transaction/v2-candidate" if proposal["schema_version"] == "lab-runtime-proposal/v2-candidate" else "lab-runtime-transaction/v1"), "kind": "admission", "sequence": sequence,')
# Derived schemas use exactly the same explicit construction as code, without runtime imports.
legacy=json.loads((OLD/'schemas/proposal.schema.json').read_bytes());content=json.loads(json.dumps(legacy));entry=json.loads((NEW/'schemas/artifact-content-entry.schema.json').read_bytes())
content['properties']['schema_version']={'const':'lab-runtime-proposal/v2-candidate'}
content['required'].append('schema_contents');content['properties']['schema_contents']={'type':'object','additionalProperties':entry}
target=content['properties']['targets']['items'];target['required'].append('content');target['properties']['content']={'anyOf':[entry,{'type':'null'}]}
put(NEW/'schemas/proposal.schema.json',{'oneOf':[legacy,content]})
tx=json.loads((OLD/'schemas/transaction.schema.json').read_bytes());tx2=json.loads(json.dumps(tx['oneOf'][1]));tx2['properties']['schema_version']={'const':'lab-runtime-transaction/v2-candidate'};tx2['properties']['proposal']=content
put(NEW/'schemas/transaction.schema.json',{'oneOf':[tx,tx2]})
profile=json.loads((NEW/'profile.json').read_bytes());prefix=NEW.relative_to(ROOT).as_posix()
profile['runtime_materials']=[p.replace('implementation/lab-runtime/v2',prefix) for p in profile['runtime_materials']]+[prefix+'/lab_runtime/custody.py',prefix+'/schemas/artifact-content-entry.schema.json']
profile['content_custody_protocol_ref']='lab-runtime-original-json-custody/v1-candidate'
put(NEW/'profile.json',profile)
# Preserve every regression assertion, changing only the physical package/repo locators.
tests=(OLD/'tests/test_runtime.py').read_text().replace('REPO = PACKAGE.parents[2]','REPO = PACKAGE.parents[6]').replace('PACKAGE.parent / "v1"','REPO / "implementation/lab-runtime/v1"').replace('PACKAGE.parent / "v1/profile.json"','REPO / "implementation/lab-runtime/v1/profile.json"')
(NEW/'tests').mkdir();(NEW/'tests/test_runtime.py').write_text(tests)
put(HERE/'derivation.json',{'authority_effect':'none','actual_owner_outcome':None,'predecessor_files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(OLD.rglob('*')) if p.is_file() and '__pycache__' not in p.parts],'change_description':'Explicit content proposal/transaction successor, signed embedded originals, existing schema unchanged, candidate CLI locator, regression locator adaptation only.'})
print(json.dumps({'authored':prefix,'authority_effect':'none'}))
