"""Compose immutable correction and custody sources without operating a store."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
PARENT=HERE.parent/'corrections-v1';OLD=PARENT/'engine-next';BYTE=HERE.parent/'runtime-byte-custody-v3/runtime';NEW=HERE/'runtime'
def put(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def edit(p,a,b):
 s=p.read_text();assert a in s,(p,a);p.write_text(s.replace(a,b))
assert not NEW.exists();shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(BYTE/'lab_runtime/custody.py',NEW/'lab_runtime/custody.py');shutil.copyfile(BYTE/'schemas/artifact-content-entry.schema.json',NEW/'schemas/artifact-content-entry.schema.json')
p=NEW/'lab_runtime/custody.py'
edit(p,"PROPOSAL_VERSION = 'lab-runtime-original-json-proposal/v1-candidate'","PROPOSAL_VERSION = 'lab-runtime-original-json-proposal/v1-candidate'\nREVIEWED_PROPOSAL_VERSION = 'lab-runtime-reviewed-original-json-proposal/v1-candidate'\nORIGINAL_PROPOSAL_VERSIONS = (PROPOSAL_VERSION, REVIEWED_PROPOSAL_VERSION)")
edit(p,"if proposal['schema_version'] != PROPOSAL_VERSION:","if proposal['schema_version'] not in ORIGINAL_PROPOSAL_VERSIONS:")
edit(p,"require(proposal['schema_version'] == 'lab-runtime-proposal/v1', 'explicit v1 proposal input required')","require(proposal['schema_version'] in ('lab-runtime-proposal/v1', 'lab-runtime-proposal/v2-candidate'), 'explicit legacy or reference-correction proposal input required')")
edit(p,"result['schema_version'] = PROPOSAL_VERSION","result['schema_version'] = PROPOSAL_VERSION if proposal['schema_version'] == 'lab-runtime-proposal/v1' else REVIEWED_PROPOSAL_VERSION")
edit(p,"custody = proposal['schema_version'] == PROPOSAL_VERSION","custody = proposal['schema_version'] in ORIGINAL_PROPOSAL_VERSIONS")
p=NEW/'lab_runtime/operations.py'
edit(p,'from .sources import make_record, resolve, validate_histories, validate_schema','from .sources import make_record, resolve, validate_histories, validate_schema\nfrom .custody import CONTENT_SCHEMA, ORIGINAL_PROPOSAL_VERSIONS, validate_proposal_content')
edit(p,"PROPOSAL_SCHEMA={'oneOf':[LEGACY_PROPOSAL_SCHEMA,CORRECTION_PROPOSAL_SCHEMA]}","""PRE_CUSTODY_PROPOSAL_SCHEMA={'oneOf':[LEGACY_PROPOSAL_SCHEMA,CORRECTION_PROPOSAL_SCHEMA]}
def with_content_schema(base, version):
    schema=copy.deepcopy(base)
    schema['properties']['schema_version']={'const':version}
    schema['required'].append('schema_contents')
    schema['properties']['schema_contents']={'type':'object','additionalProperties':CONTENT_SCHEMA}
    target=schema['properties']['targets']['items']
    target['required'].append('content')
    target['properties']['content']={'anyOf':[CONTENT_SCHEMA,{'type':'null'}]}
    return schema
ORIGINAL_PROPOSAL_SCHEMA=with_content_schema(LEGACY_PROPOSAL_SCHEMA, ORIGINAL_PROPOSAL_VERSIONS[0])
REVIEWED_ORIGINAL_PROPOSAL_SCHEMA=with_content_schema(CORRECTION_PROPOSAL_SCHEMA, ORIGINAL_PROPOSAL_VERSIONS[1])
PROPOSAL_SCHEMA={'oneOf':[LEGACY_PROPOSAL_SCHEMA,CORRECTION_PROPOSAL_SCHEMA,ORIGINAL_PROPOSAL_SCHEMA,REVIEWED_ORIGINAL_PROPOSAL_SCHEMA]}""")
edit(p,'protocol_check(proposal, PROPOSAL_SCHEMA)\n    if verify_base:','protocol_check(proposal, PROPOSAL_SCHEMA)\n    validate_proposal_content(proposal)\n    if verify_base:')
edit(p,"if proposal['schema_version']=='lab-runtime-proposal/v2-candidate':","if proposal['schema_version'] in ('lab-runtime-proposal/v2-candidate', ORIGINAL_PROPOSAL_VERSIONS[1]):")
edit(p,'entry.update(identity=ident, kind=kind)','if proposal["schema_version"] in ORIGINAL_PROPOSAL_VERSIONS:\n            entry["source"].update(sha256=target["content"]["byte_sha256"], encoding="base64-original-json/v1-candidate", content_ref=target["content"]["content_ref"])\n        entry.update(identity=ident, kind=kind)')
edit(p,'projection["subjects"][target["version_ref"]]["source"].update(path=tx_path, selector=f"/proposal/targets/{i}/record", store_id=store_id)','binding = projection["subjects"][target["version_ref"]]["source"]\n            binding.update(path=tx_path, selector=f"/proposal/targets/{i}/record", store_id=store_id)\n            if proposal["schema_version"] in ORIGINAL_PROPOSAL_VERSIONS:\n                binding.update(selector=f"/proposal/targets/{i}/content/data", record_selector=f"/proposal/targets/{i}/record")')
p=NEW/'lab_runtime/corrections.py'
edit(p,"require(proposal['schema_version']=='lab-runtime-proposal/v2-candidate'","require(proposal['schema_version'] in ('lab-runtime-proposal/v2-candidate','lab-runtime-reviewed-original-json-proposal/v1-candidate')")
p=NEW/'lab_runtime/protocols.py'
edit(p,'from .operations import CATEGORIES, OPERATIONS, PROPOSAL_SCHEMA','from .operations import CATEGORIES, OPERATIONS, PROPOSAL_SCHEMA, PRE_CUSTODY_PROPOSAL_SCHEMA, ORIGINAL_PROPOSAL_SCHEMA, REVIEWED_ORIGINAL_PROPOSAL_SCHEMA')
edit(p,'"proposal": PROPOSAL_SCHEMA, "approval": APPROVAL_SCHEMA,','"proposal": PRE_CUSTODY_PROPOSAL_SCHEMA, "approval": APPROVAL_SCHEMA,')
edit(p,'SCHEMAS = {',"""PRE_CUSTODY_TRANSACTION_SCHEMA=TRANSACTION_SCHEMA
TRANSACTION_SCHEMA={'oneOf':[PRE_CUSTODY_TRANSACTION_SCHEMA,
    closed({**TRANSACTION_COMMON,'schema_version':{'const':'lab-runtime-original-json-transaction/v1-candidate'},
        'kind':{'const':'admission'},'proposal':ORIGINAL_PROPOSAL_SCHEMA,'approval':APPROVAL_SCHEMA,
        'decision_cores':{'type':'array','minItems':1},'consequences':{'type':'object'}}),
    closed({**TRANSACTION_COMMON,'schema_version':{'const':'lab-runtime-reviewed-original-json-transaction/v1-candidate'},
        'kind':{'const':'admission'},'proposal':REVIEWED_ORIGINAL_PROPOSAL_SCHEMA,'approval':APPROVAL_SCHEMA,
        'decision_cores':{'type':'array','minItems':1},'consequences':{'type':'object'}})]}

SCHEMAS = {""")
# Correct only the export mapping; the old transaction branch keeps its closed predecessor proposal schema.
edit(p,'SCHEMAS = {"proposal": PRE_CUSTODY_PROPOSAL_SCHEMA,','SCHEMAS = {"proposal": PROPOSAL_SCHEMA,')
p=NEW/'lab_runtime/store.py'
edit(p,'from .sources import capture, freshness',"from .sources import capture, freshness\n\ndef transaction_version(proposal):\n    return {'lab-runtime-original-json-proposal/v1-candidate':'lab-runtime-original-json-transaction/v1-candidate',\n            'lab-runtime-reviewed-original-json-proposal/v1-candidate':'lab-runtime-reviewed-original-json-transaction/v1-candidate'}.get(proposal['schema_version'],'lab-runtime-transaction/v1')")
edit(p,'tx["schema_version"] == "lab-runtime-transaction/v1"','tx["schema_version"] in ("lab-runtime-transaction/v1","lab-runtime-original-json-transaction/v1-candidate","lab-runtime-reviewed-original-json-transaction/v1-candidate")')
edit(p,'proposal = tx["proposal"]\n                require','proposal = tx["proposal"]\n                require(tx["schema_version"] == transaction_version(proposal), "transaction/proposal encoding mismatch")\n                require')
edit(p,'tx = sealed({"schema_version": "lab-runtime-transaction/v1", "kind": "admission", "sequence": sequence,','tx = sealed({"schema_version": transaction_version(proposal), "kind": "admission", "sequence": sequence,')
p=NEW/'lab_runtime/cli.py';edit(p,'DEFAULT_REPO = PACKAGE.parents[2]','DEFAULT_REPO = PACKAGE.parents[6]');edit(p,'repo / ".local/lab-runtime/v2/store"','repo / ".local/lab-runtime/custody-correction-v1/store"')
# Generate schemas using explicit authoring construction rather than importing the candidate before freeze.
legacy=json.loads((OLD/'schemas/proposal.schema.json').read_bytes());content=json.loads((BYTE/'schemas/artifact-content-entry.schema.json').read_bytes())
def content_schema(base,name):
 s=json.loads(json.dumps(base));s['properties']['schema_version']={'const':name};s['required'].append('schema_contents');s['properties']['schema_contents']={'type':'object','additionalProperties':content};t=s['properties']['targets']['items'];t['required'].append('content');t['properties']['content']={'anyOf':[content,{'type':'null'}]};return s
r=content_schema(legacy['oneOf'][0],'lab-runtime-original-json-proposal/v1-candidate');c=content_schema(legacy['oneOf'][1],'lab-runtime-reviewed-original-json-proposal/v1-candidate');put(NEW/'schemas/proposal.schema.json',{'oneOf':legacy['oneOf']+[r,c]})
oldtx=json.loads((OLD/'schemas/transaction.schema.json').read_bytes());branches=[]
for schema,name in [(r,'lab-runtime-original-json-transaction/v1-candidate'),(c,'lab-runtime-reviewed-original-json-transaction/v1-candidate')]:
 t=json.loads(json.dumps(oldtx['oneOf'][1]));t['properties']['schema_version']={'const':name};t['properties']['proposal']=schema;branches.append(t)
put(NEW/'schemas/transaction.schema.json',{'oneOf':[oldtx]+branches})
profile=json.loads((NEW/'profile.json').read_bytes());prefix=NEW.relative_to(ROOT).as_posix();profile['runtime_materials']=[p.replace('implementation/lab-runtime/v2',prefix) for p in profile['runtime_materials']]
profile['runtime_materials'] += [prefix+'/lab_runtime/endpoint_mapping.py',prefix+'/lab_runtime/corrections.py',prefix+'/lab_runtime/custody.py',prefix+'/endpoint-mapping.json',prefix+'/write-profile.json',prefix+'/schemas/artifact-content-entry.schema.json']
profile['content_custody_protocol_ref']='lab-runtime-reviewed-original-json-custody/v1-candidate';put(NEW/'profile.json',profile)
for name in ['loader.py','episode.py','test_corrections.py','test_schema_cache.py','regression.py','coupling_regression.py']:
 shutil.copyfile(PARENT/name,HERE/name)
edit(HERE/'loader.py',"ENGINE = HERE / 'engine-next'","ENGINE = HERE / 'runtime'")
put(HERE/'derivation.json',{'authority_effect':'none','actual_owner_outcome':None,'parent_correction_files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(OLD.rglob('*')) if p.is_file() and '__pycache__' not in p.parts],'custody_source_binding':{'path':(BYTE.parent/'source-manifest.json').relative_to(ROOT).as_posix(),'sha256':hashlib.sha256((BYTE.parent/'source-manifest.json').read_bytes()).hexdigest()},'legacy_semantic_and_permission_code_preserved':'Scope/profile/reference/member/carrier/endpoint/domain/approval fields preserved. New family adds required original bytes and explicit transaction tag; it grants no extra domain or effect.'})
print(json.dumps({'authored':prefix,'protocol_families':4,'authority_effect':'none'}))
