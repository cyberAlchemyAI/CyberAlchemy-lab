"""Typed semantic-host schema comparison and snapshot transformation adapter."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import migration as semantic

PREVIOUS=Path(__file__).resolve().parent.parent/'state-migrations-v1'
spec=importlib.util.spec_from_file_location('alch_semantic_snapshot',PREVIOUS/'migration.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
snapshot,logical_digest=previous.snapshot,previous.logical_digest


def ontology(bundle):
    semantic.verify_bundle(bundle)
    value=json.loads((Path(bundle)/'typed-ontology.json').read_bytes())
    if value['schema_version']!='alch.semantic-ontology/v2':raise ValueError('SEMANTIC_ONTOLOGY_REQUIRED')
    import hashlib
    if value['source_sha256']!=hashlib.sha256((Path(bundle)/'source.alch').read_bytes()).hexdigest():raise ValueError('SOURCE_DRIFT')
    return value


def derive_change(old,new,contract):
    before,after=ontology(old),ontology(new)
    if before['domain']!=after['domain'] or set(before['records'])!=set(after['records']):raise ValueError('IDENTITY_CHANGE_REQUIRES_INTENT')
    additions={}
    for name,record in before['records'].items():
        target=after['records'][name]
        if record['kind']!=target['kind'] or record.get('from')!=target.get('from'):raise ValueError('ROLE_CHANGE_REQUIRES_INTENT')
        old_props={p['id']:p for p in record['properties']};new_props={p['id']:p for p in target['properties']}
        if not set(old_props)<=set(new_props) or any(new_props[k]!=v for k,v in old_props.items()):raise ValueError('DESTRUCTIVE_CHANGE')
        added=set(new_props)-set(old_props)
        if added:
            if target['kind'] not in ('entity','event','projection'):raise ValueError('INPUT_CHANGE_REQUIRES_INTENT')
            origin=target
            while origin.get('from'):origin=after['records'][origin['from']]
            defaults={p['id'] for p in origin['properties'] if 'default' in p}
            if not added<=defaults:raise ValueError('DEFAULT_REQUIRED')
            additions[name]=sorted(added)
    if not additions:raise ValueError('RUNTIME_CHANGE_REQUIRES_INTENT')
    old_config=json.loads((Path(old)/'config.json').read_bytes());new_config=json.loads((Path(new)/'config.json').read_bytes())
    new_config['model']['facts']=[f for f in new_config['model']['facts'] if f['id'] not in additions.get(f['subject_ref'],[])]
    for mapping in new_config['model']['mappings']:mapping['clauses']=[c for c in mapping['clauses'] if c['target_field'] not in additions.get(mapping['target_ref'],[])]
    old_config.pop('binding_digest');new_config.pop('binding_digest')
    if old_config!=new_config:raise ValueError('EXECUTION_CHANGE_REQUIRES_INTENT')
    for file in ('rust/src/lib.rs','rust/src/main.rs','rust/Cargo.toml','rust/Cargo.lock','local_worker.py','binding.json'):
        if (Path(old)/file).read_bytes()!=(Path(new)/file).read_bytes():raise ValueError('RUNTIME_CHANGE_REQUIRES_INTENT')
    return {'kind':'additive','source_contract':contract,'additions':additions,'authority_effect':'none'}


def transform(database,bundle,manifest,node):
    import sqlite3
    data=semantic.snapshot(database);ownership={row[0]:row[0] for row in data.get('state',[])}
    ownership.update({row[0]:row[0] for row in data.get('inbox',[])})
    plan=semantic.prepare(database,bundle,ownership)
    with tempfile.TemporaryDirectory(prefix='semantic-transform-',dir=Path(database).parent) as temp:
        target=Path(temp)/'generation.sqlite';receipt=semantic.apply(database,bundle,plan,target)
        # Only the controller's private rehearsal/candidate database is replaced here.
        with sqlite3.connect(target) as src,sqlite3.connect(database) as dst:src.backup(dst)
    with sqlite3.connect(database) as db:receipt['logical_sha256']=logical_digest(db)
    return receipt
