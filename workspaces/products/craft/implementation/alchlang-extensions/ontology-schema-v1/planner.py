"""Ontology comparison and source-pinned migration planning; no schema inference from data."""
import importlib.util
import json
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker

PREVIOUS=Path(__file__).resolve().parent.parent/'state-migrations-v1'
spec=importlib.util.spec_from_file_location('alch_previous_migration',PREVIOUS/'migration.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
require,digest,encoded,semantic=previous.require,previous.digest,previous.encoded,previous.semantic
snapshot,logical_digest=previous.snapshot,previous.logical_digest


def ontology(bundle):
    bundle=Path(bundle)
    value=json.loads((bundle/'typed-ontology.json').read_bytes())
    schemas=json.loads((bundle/'schemas.json').read_bytes())
    require(value['schema_version']=='alch.typed-host-ontology/v1','TYPED_ONTOLOGY_REQUIRED')
    require(value['source_sha256']==digest((bundle/'authored.alch').read_bytes()),'ONTOLOGY_SOURCE_DRIFT')
    require(schemas['ontology_sha256']==digest(json.dumps(value,separators=(',',':'),ensure_ascii=False).encode()),'SCHEMA_ONTOLOGY_DRIFT')
    return value


def derive_change(old,new,contract):
    before,after=ontology(old),ontology(new)
    require(before['domain']==after['domain'] and set(before['records'])==set(after['records']),'RECORD_CHANGE_REQUIRES_INTENT')
    additions=[]
    for subject,record in before['records'].items():
        target=after['records'][subject];require(record['id']==target['id'],'RECORD_IDENTITY_CHANGED')
        old_fields={p['id']:p for p in record['properties']};new_fields={p['id']:p for p in target['properties']}
        require(len(old_fields)==len(record['properties']) and len(new_fields)==len(target['properties']),'PROPERTY_IDENTITY_AMBIGUOUS')
        require(set(old_fields)<=set(new_fields),'REMOVAL_OR_RENAME_REQUIRES_INTENT')
        require(all(old_fields[k]==new_fields[k] for k in old_fields),'PROPERTY_CHANGE_REQUIRES_INTENT')
        additions.extend((subject,p) for k,p in new_fields.items() if k not in old_fields)
    require(len(additions)==1,'ONE_ADDITIVE_FIELD_REQUIRED')
    subject,prop=additions[0]
    require(not prop['required'] and 'default' in prop,'EXPLICIT_OPTIONAL_DEFAULT_REQUIRED')
    index=json.loads((Path(new)/'default-mappers.json').read_bytes())
    matches=[r for r in index if r['property_id']==prop['id']]
    require(len(matches)==1,'DEFAULT_MAPPER_REQUIRED');directory=matches[0]['directory']
    require(__import__('re').fullmatch(r'defaults/[a-f0-9]{24}',directory),'MAPPER_PATH')
    manifest=json.loads((Path(new)/directory/'descriptor.json').read_bytes())
    require(manifest['property_id']==prop['id'] and manifest['subject']==subject and manifest['field']==prop['name'] and manifest['scalar']==prop['type'] and encoded(manifest['default'])==encoded(prop['default']),'ONTOLOGY_MAPPING_DRIFT')
    manifest={**manifest,'from_contract':contract,'mapper_directory':directory}
    validate_change(old,new,contract,manifest)
    return manifest

def validate_change(old,new,contract,m):
    old,new=Path(old),Path(new)
    require(m['profile']=='alch.state-migration/v1' and m['from_contract']==contract,'MIGRATION_SOURCE_MISMATCH')
    require(digest((new/m['mapper_directory']/'migration.mjs').read_bytes())==m['mapper_sha256'],'MAPPER_DRIFT')
    before=json.loads((old/'config.json').read_bytes());after=json.loads((new/'config.json').read_bytes())
    name,subject=m['field'],m['subject']
    require(not any(f['id']==name for f in before['model']['facts']),'STATE_FIELD_CONFLICT')
    fields=[f for f in after['model']['facts'] if f['id']==name]
    owner=next(f['owner'] for f in before['model']['facts'] if f['subject_ref']==subject)
    require(fields==[{'id':name,'subject_ref':subject,'type':m['scalar'],'required':False,'owner':owner}],'MIGRATION_FIELD_CONTRACT')
    expected=[e for e in before['executions'] if subject in next(a for a in before['model']['actions'] if a['id']==e['operation'])['subject_refs']]
    require(m['operations']==[e['operation'] for e in expected] and set(m['state_mappings'])=={e['state'] for e in expected},'MIGRATION_OPERATION_CONTRACT')
    after['model']['facts']=[f for f in after['model']['facts'] if f['id']!=name]
    for mapping in after['model']['mappings']:
        if mapping['id'] not in m['state_mappings']:continue
        additions=[c for c in mapping['clauses'] if c['target_field']==name]
        require(additions==[{'target_field':name,'source_field':None,'default_value':{'value_type':m['scalar'],'value':m['default']}}],'MIGRATION_MAPPING_CONTRACT')
        mapping['clauses']=[c for c in mapping['clauses'] if c['target_field']!=name]
    require(semantic(before)==semantic(after),'UNDECLARED_SEMANTIC_CHANGE')
    hosts=[json.loads((p/'host.json').read_bytes()) for p in (old,new)]
    for key in ('id','runtime','events','isolation','operation','actors','boundary','consumer','transport'):
        require(hosts[0][key]==hosts[1][key],'MIGRATION_HOST_CHANGE')
    for file in ('rust/src/lib.rs','rust/src/main.rs','rust/Cargo.toml','rust/Cargo.lock','local_worker.py'):
        require((old/file).read_bytes()==(new/file).read_bytes(),'MIGRATION_RUNTIME_CHANGE')
    return m


def transform(database,bundle,manifest,node):
    result=previous.transform(database,Path(bundle)/manifest['mapper_directory'],manifest,node)
    schemas=json.loads((Path(bundle)/'schemas.json').read_bytes())
    import sqlite3
    with sqlite3.connect(database) as db:
        for operation,text in db.execute('SELECT operation,state FROM state'):
            require(operation in schemas['states'],'STATE_SCHEMA_MISSING')
            validator=Draft202012Validator(schemas['states'][operation],format_checker=FormatChecker())
            require(validator.is_valid(json.loads(text)),'STATE_SCHEMA_INVALID')
    return {**result,'schema_sha256':digest((Path(bundle)/'schemas.json').read_bytes()),'ontology_sha256':digest((Path(bundle)/'typed-ontology.json').read_bytes())}
