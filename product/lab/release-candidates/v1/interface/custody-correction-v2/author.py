"""Version exact schema-byte custody while retaining all prior replay families."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];OLD=HERE.parent/'custody-correction-v1';NEW=HERE/'runtime'
def edit(p,a,b):
 text=p.read_text();assert a in text,(p,a);p.write_text(text.replace(a,b))
def put(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
assert not NEW.exists();shutil.copytree(OLD/'runtime',NEW,ignore=shutil.ignore_patterns('__pycache__'))
for name in ['loader.py','episode.py','test_corrections.py','test_schema_cache.py','regression.py','coupling_regression.py','checks.py','journey.py','reader_adapter.py','CONTRACT.md']:shutil.copyfile(OLD/name,HERE/name)
p=NEW/'lab_runtime/custody.py'
edit(p,'ORIGINAL_PROPOSAL_VERSIONS = (PROPOSAL_VERSION, REVIEWED_PROPOSAL_VERSION)',"EXACT_SCHEMA_PROPOSAL_VERSION = 'lab-runtime-original-json-proposal/v2-candidate'\nEXACT_SCHEMA_REVIEWED_PROPOSAL_VERSION = 'lab-runtime-reviewed-original-json-proposal/v2-candidate'\nEXACT_SCHEMA_PROPOSAL_VERSIONS = (EXACT_SCHEMA_PROPOSAL_VERSION, EXACT_SCHEMA_REVIEWED_PROPOSAL_VERSION)\nORIGINAL_PROPOSAL_VERSIONS = (PROPOSAL_VERSION, REVIEWED_PROPOSAL_VERSION, *EXACT_SCHEMA_PROPOSAL_VERSIONS)")
edit(p,'def with_originals(proposal, target_bytes, schema_bytes):','def with_originals(proposal, target_bytes, schema_bytes, *, exact_schema_bytes=False):')
edit(p,"result['schema_version'] = PROPOSAL_VERSION if proposal['schema_version'] == 'lab-runtime-proposal/v1' else REVIEWED_PROPOSAL_VERSION","versions = EXACT_SCHEMA_PROPOSAL_VERSIONS if exact_schema_bytes else (PROPOSAL_VERSION, REVIEWED_PROPOSAL_VERSION)\n    result['schema_version'] = versions[0] if proposal['schema_version'] == 'lab-runtime-proposal/v1' else versions[1]")
p=NEW/'lab_runtime/operations.py'
edit(p,'from .custody import CONTENT_SCHEMA, ORIGINAL_PROPOSAL_VERSIONS, validate_proposal_content','from .custody import CONTENT_SCHEMA, ORIGINAL_PROPOSAL_VERSIONS, EXACT_SCHEMA_PROPOSAL_VERSIONS, validate_proposal_content')
edit(p,"PROPOSAL_SCHEMA={'oneOf':[LEGACY_PROPOSAL_SCHEMA,CORRECTION_PROPOSAL_SCHEMA,ORIGINAL_PROPOSAL_SCHEMA,REVIEWED_ORIGINAL_PROPOSAL_SCHEMA]}","EXACT_SCHEMA_ORIGINAL_PROPOSAL_SCHEMA=with_content_schema(LEGACY_PROPOSAL_SCHEMA, EXACT_SCHEMA_PROPOSAL_VERSIONS[0])\nEXACT_SCHEMA_REVIEWED_PROPOSAL_SCHEMA=with_content_schema(CORRECTION_PROPOSAL_SCHEMA, EXACT_SCHEMA_PROPOSAL_VERSIONS[1])\nPROPOSAL_SCHEMA={'oneOf':[LEGACY_PROPOSAL_SCHEMA,CORRECTION_PROPOSAL_SCHEMA,ORIGINAL_PROPOSAL_SCHEMA,REVIEWED_ORIGINAL_PROPOSAL_SCHEMA,EXACT_SCHEMA_ORIGINAL_PROPOSAL_SCHEMA,EXACT_SCHEMA_REVIEWED_PROPOSAL_SCHEMA]}")
edit(p,"('lab-runtime-proposal/v2-candidate', ORIGINAL_PROPOSAL_VERSIONS[1])","('lab-runtime-proposal/v2-candidate', ORIGINAL_PROPOSAL_VERSIONS[1], EXACT_SCHEMA_PROPOSAL_VERSIONS[1])")
edit(p,'post["documents"][path] = schema',"""post["documents"][path] = schema
        # A schema path is a byte identity as well as a parsed value identity.
        existing=post.get('schema_content_bindings',{}).get(path)
        if proposal['schema_version'] in EXACT_SCHEMA_PROPOSAL_VERSIONS:
            entry=proposal['schema_contents'][path]
            sha=entry['byte_sha256']
            if existing:
                require(existing['byte_sha256']==sha,'immutable schema original bytes conflict')
            elif path in projection['documents']:
                require(byte_digest(encoded(projection['documents'][path]))==sha,'legacy immutable schema encoding conflict')
            else:
                post.setdefault('schema_content_bindings',{})[path]={'byte_sha256':sha,'content_ref':entry['content_ref'],
                    'encoding':'base64-original-json/v1-candidate','proposal_id':proposal['proposal_id'],
                    'selector':'/proposal/schema_contents/'+path.replace('~','~0').replace('/','~1')+'/data'}
        elif existing:
            require(byte_digest(encoded(schema))==existing['byte_sha256'],'immutable schema original bytes conflict')""")
edit(p,'require(c["schema_sha256"] == byte_digest(encoded(post["documents"][c["schema_path"]])), "artifact schema digest mismatch")',"expected_schema_sha=post.get('schema_content_bindings',{}).get(c['schema_path'],{}).get('byte_sha256',byte_digest(encoded(post['documents'][c['schema_path']])))\n            require(c['schema_sha256']==expected_schema_sha,'artifact schema digest mismatch')")
# Bind known proposed schema metadata to the same already immutable transaction selector.
edit(p,'tx_ref = f"admission-transaction:{store_id}:{sequence}"',"for binding in projection.get('schema_content_bindings',{}).values():\n        if binding['proposal_id']==proposal['proposal_id']:\n            binding.update(path=tx_path,store_id=store_id)\n    tx_ref = f\"admission-transaction:{store_id}:{sequence}\"")
p=NEW/'lab_runtime/corrections.py';edit(p,"('lab-runtime-proposal/v2-candidate','lab-runtime-reviewed-original-json-proposal/v1-candidate')","('lab-runtime-proposal/v2-candidate','lab-runtime-reviewed-original-json-proposal/v1-candidate','lab-runtime-reviewed-original-json-proposal/v2-candidate')")
p=NEW/'lab_runtime/protocols.py';edit(p,'ORIGINAL_PROPOSAL_SCHEMA, REVIEWED_ORIGINAL_PROPOSAL_SCHEMA','ORIGINAL_PROPOSAL_SCHEMA, REVIEWED_ORIGINAL_PROPOSAL_SCHEMA, EXACT_SCHEMA_ORIGINAL_PROPOSAL_SCHEMA, EXACT_SCHEMA_REVIEWED_PROPOSAL_SCHEMA')
edit(p,'SCHEMAS = {',"TRANSACTION_SCHEMA['oneOf'] += [\n    closed({**TRANSACTION_COMMON,'schema_version':{'const':'lab-runtime-original-json-transaction/v2-candidate'},\n        'kind':{'const':'admission'},'proposal':EXACT_SCHEMA_ORIGINAL_PROPOSAL_SCHEMA,'approval':APPROVAL_SCHEMA,\n        'decision_cores':{'type':'array','minItems':1},'consequences':{'type':'object'}}),\n    closed({**TRANSACTION_COMMON,'schema_version':{'const':'lab-runtime-reviewed-original-json-transaction/v2-candidate'},\n        'kind':{'const':'admission'},'proposal':EXACT_SCHEMA_REVIEWED_PROPOSAL_SCHEMA,'approval':APPROVAL_SCHEMA,\n        'decision_cores':{'type':'array','minItems':1},'consequences':{'type':'object'}})]\n\nSCHEMAS = {")
p=NEW/'lab_runtime/store.py';edit(p,"return {'lab-runtime-original-json-proposal/v1-candidate'", "return {'lab-runtime-original-json-proposal/v2-candidate':'lab-runtime-original-json-transaction/v2-candidate',\n            'lab-runtime-reviewed-original-json-proposal/v2-candidate':'lab-runtime-reviewed-original-json-transaction/v2-candidate',\n            'lab-runtime-original-json-proposal/v1-candidate'")
edit(p,'"lab-runtime-reviewed-original-json-transaction/v1-candidate")','"lab-runtime-reviewed-original-json-transaction/v1-candidate","lab-runtime-original-json-transaction/v2-candidate","lab-runtime-reviewed-original-json-transaction/v2-candidate")')
p=NEW/'lab_runtime/cli.py';edit(p,'.local/lab-runtime/custody-correction-v1/store','.local/lab-runtime/custody-correction-v2/store')
proposal=json.loads((NEW/'schemas/proposal.schema.json').read_bytes());new=[]
for i in [2,3]:
 s=json.loads(json.dumps(proposal['oneOf'][i]));s['properties']['schema_version']['const']=s['properties']['schema_version']['const'].replace('/v1-candidate','/v2-candidate');new.append(s)
proposal['oneOf']+=new;put(NEW/'schemas/proposal.schema.json',proposal)
tx=json.loads((NEW/'schemas/transaction.schema.json').read_bytes())
for i,s in zip([1,2],new):
 t=json.loads(json.dumps(tx['oneOf'][i]));t['properties']['schema_version']['const']=t['properties']['schema_version']['const'].replace('/v1-candidate','/v2-candidate');t['properties']['proposal']=s;tx['oneOf'].append(t)
put(NEW/'schemas/transaction.schema.json',tx)
p=NEW/'profile.json';profile=json.loads(p.read_bytes());profile['runtime_materials']=[s.replace('custody-correction-v1/','custody-correction-v2/') for s in profile['runtime_materials']];profile['exact_schema_original_bytes_protocol_ref']='lab-runtime-reviewed-original-json-custody/v2-candidate';put(p,profile)
# The actual combined journey now exercises the exact-schema successor; all inherited tests are unchanged.
edit(HERE/'journey.py',"with_originals(plain,originals,{})","with_originals(plain,originals,{},exact_schema_bytes=True)")
for name in ['lab-runtime-reviewed-original-json-proposal','lab-runtime-reviewed-original-json-transaction']:
 edit(HERE/'journey.py',name+'/v1-candidate',name+'/v2-candidate')
p=HERE/'CONTRACT.md';p.write_text(p.read_text()+"\n## Exact schema-byte successor\n\nThe two additional original-json/v2 and reviewed-original-json/v2 families bind descriptor and contract schema_sha256 to actual original schema bytes. Explicit immutable schema-content metadata enters canonical replay and source selectors. Reusing an existing path with different bytes fails even for equal parsed values. Old raw/v1 and correction/legacy families keep their prior replay when no newer original binding exists. No schema digest is silently replaced or missing original fabricated.\n")
print(json.dumps({'authored':NEW.relative_to(ROOT).as_posix(),'proposal_families':6,'authority_effect':'none'}))
