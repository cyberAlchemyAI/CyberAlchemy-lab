"""Explicit offline snapshot migration. Never rewrites the source database or selects a live route."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import jsonschema


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def snapshot(database):
    with sqlite3.connect(f'file:{Path(database).resolve()}?mode=ro',uri=True) as db:
        db.execute('BEGIN')
        tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        # Table identifiers come from SQLite, quote rather than concatenate untrusted SQL.
        return {name:db.execute('SELECT * FROM "'+name.replace('"','""')+'" ORDER BY rowid').fetchall() for name in tables}


def verify_bundle(bundle):
    bundle=Path(bundle).resolve()
    manifest=json.loads((bundle/'manifest.json').read_bytes())
    if (bundle/'host-manifest.json').read_bytes()!=(bundle/'manifest.json').read_bytes():raise ValueError('BUNDLE_MANIFEST_DRIFT')
    expected=set(manifest['files'])
    actual={str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file()}-{'manifest.json','host-manifest.json'}
    if expected!=actual:raise ValueError('BUNDLE_INVENTORY')
    for name,value in manifest['files'].items():
        p=bundle/name
        if p.is_symlink() or not p.resolve().is_relative_to(bundle) or hashlib.sha256(p.read_bytes()).hexdigest()!=value:raise ValueError('BUNDLE_DRIFT')
    return digest(manifest)


def prepare(database,bundle,ownership,backfills=None):
    """ownership explicitly maps every old operation key to one entity/projection storage identity."""
    target=verify_bundle(bundle);data=snapshot(database);cfg=json.loads((Path(bundle)/'config.json').read_bytes())
    valid={e['storage'] for e in cfg['executions']}
    if 'semantic_metadata' in data and data['semantic_metadata']!=[(2,)]:raise ValueError('SCHEMA_VERSION')
    old={row[0] for row in data.get('state',[])}|{row[0] for row in data.get('inbox',[])}
    if set(ownership)!=old or any(v not in valid for v in ownership.values()) or len(set(ownership.values()))!=len(ownership):raise ValueError('EXPLICIT_UNAMBIGUOUS_OWNERSHIP_REQUIRED')
    if any(row[4]!='published' for row in data.get('outbox',[])):raise ValueError('DRAIN_REQUIRED')
    if backfills is None:
        backfills={}
        for node in json.loads((Path(bundle)/'backfills.json').read_bytes()):
            rows=[json.loads(row[2]) for row in data.get('state',[]) if ownership[row[0]]==node['storage']]
            if any(node['field'] not in row for row in rows):
                contract=json.loads((Path(bundle)/'backfills'/(node['file']+'.contract.json')).read_bytes())
                literal=contract['nodes'][0]['fields'][node['field']]
                if literal['op']!='literal':raise ValueError('BACKFILL_CONTRACT')
                backfills.setdefault(node['storage'],{})[node['field']]=literal['value']
    plan={'version':2,'baseline':digest(data),'target':target,'ownership':ownership,'backfills':backfills or {},'authority_effect':'none'}
    plan['digest']=digest(plan)
    return plan


def apply(database,bundle,plan,output,failpoint=None):
    """Caller must stop the old host. Produces a fresh generation; selection is a separate operation."""
    unsigned={k:v for k,v in plan.items() if k!='digest'}
    if digest(unsigned)!=plan.get('digest'):raise ValueError('PLAN_DRIFT')
    if verify_bundle(bundle)!=plan['target']:raise ValueError('TARGET_DRIFT')
    before=snapshot(database)
    if digest(before)!=plan['baseline']:raise ValueError('STALE_PLAN')
    # Re-evaluate intent, rather than trusting a rehashed arbitrary plan.
    if prepare(database,bundle,plan['ownership'],plan['backfills'])!=plan:raise ValueError('PLAN_REEVALUATION')
    output=Path(output)
    if output.exists():raise ValueError('NEW_GENERATION_REQUIRED')
    ontology=json.loads((Path(bundle)/'typed-ontology.json').read_bytes())
    config=json.loads((Path(bundle)/'config.json').read_bytes())
    by_storage={e['storage']:ontology['records'][e['subject']] for e in config['executions']}
    generated={}
    declarations=json.loads((Path(bundle)/'backfills.json').read_bytes())
    for storage,fields in plan['backfills'].items():
        for field,value in fields.items():
            node=next((n for n in declarations if n['storage']==storage and n['field']==field),None)
            if node is None:raise ValueError('BACKFILL_MAPPER_REQUIRED')
            entry=Path(bundle)/'backfills'/node['file']
            result=subprocess.run(['/home/vrondelli/.nvm/versions/node/v26.8.1/bin/node','--max-old-space-size=64','--input-type=module','-e',"const {execute}=await import(process.argv[1]);process.stdout.write(JSON.stringify(execute({},{})));",entry.resolve().as_uri()],capture_output=True,text=True,timeout=5)
            if result.returncode or json.loads(result.stdout)!={field:value}:raise ValueError('BACKFILL_MAPPER_RESULT')
            generated[(storage,field)]=json.loads(result.stdout)[field]
    fd=os.open(output,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    os.close(fd)
    try:
        with sqlite3.connect(f'file:{Path(database).resolve()}?mode=ro',uri=True) as src,sqlite3.connect(output) as dst:
            src.backup(dst)
            if digest(snapshot(output))!=plan['baseline']:raise ValueError('SOURCE_CHANGED_DURING_COPY')
            dst.execute('BEGIN IMMEDIATE')
            dst.execute('CREATE TABLE IF NOT EXISTS semantic_metadata(version INTEGER PRIMARY KEY)')
            dst.execute('INSERT OR IGNORE INTO semantic_metadata VALUES(2)')
            dst.execute('CREATE TABLE IF NOT EXISTS legacy_states(operation TEXT,key TEXT,state TEXT,version INTEGER,PRIMARY KEY(operation,key))')
            dst.execute('CREATE TABLE IF NOT EXISTS delivery_history(id TEXT PRIMARY KEY,created INTEGER,receives INTEGER)')
            dst.execute('CREATE TABLE IF NOT EXISTS dead_letters(channel TEXT,id TEXT,body TEXT,reason TEXT,PRIMARY KEY(channel,id))')
            from datetime import datetime
            for row in dst.execute('SELECT id,body FROM outbox').fetchall():
                at=json.loads(row[1])['occurredAt'];created=int(datetime.fromisoformat(at.replace('Z','+00:00')).timestamp()*1000)
                dst.execute('INSERT OR IGNORE INTO delivery_history VALUES(?,?,0)',(row[0],created))
            rows=dst.execute('SELECT operation,key,state,version FROM state').fetchall()
            for old,key,raw,version in rows:
                target=plan['ownership'][old];record=by_storage[target];values=json.loads(raw)
                if old!=target:dst.execute('INSERT INTO legacy_states VALUES(?,?,?,?)',(old,key,raw,version))
                fields={p['id']:p for p in record['properties']}
                if old==target and set(values)-set(fields):raise ValueError('DESTRUCTIVE_CHANGE')
                for field,value in plan['backfills'].get(target,{}).items():
                    prop=fields.get(field)
                    origin=record
                    while origin.get('from'):origin=ontology['records'][origin['from']]
                    default=next((p for p in origin['properties'] if p['id']==field and 'default' in p),None)
                    if not prop or not default or default['default']!=value:raise ValueError('BACKFILL_CONTRACT')
                    if field not in values:values[field]=generated[(target,field)]
                result={k:v for k,v in values.items() if k in fields}
                for name,prop in fields.items():
                    if name not in result:
                        if prop['required']:raise ValueError('BACKFILL_REQUIRED')
                        continue
                    v=result[name];t=prop['type']
                    ok=(type(v) is int and abs(v)<=9007199254740991 if t=='integer' else type(v) is bool if t=='boolean' else type(v) is dict if t=='record' else type(v) is str and (t=='string' or bool(v)))
                    if not ok:raise ValueError('STATE_TYPE')
                execution=next(e for e in config['executions'] if e['storage']==target)
                schemas=json.loads((Path(bundle)/'schemas.json').read_bytes())
                jsonschema.Draft202012Validator(schemas[execution['subject']],format_checker=jsonschema.FormatChecker()).validate(result)
                if result[execution['key']]!=key:raise ValueError('IDENTITY_CHANGE')
                dst.execute('DELETE FROM state WHERE operation=? AND key=?',(old,key))
                dst.execute('INSERT INTO state VALUES(?,?,?,?)',(target,key,json.dumps(result,sort_keys=True,separators=(',',':')),version))
            for old,target in plan['ownership'].items():
                if old!=target:dst.execute('UPDATE inbox SET operation=? WHERE operation=?',(target,old))
            if failpoint=='before-commit':raise ValueError('INJECTED_FAILURE')
            dst.commit()
        after=snapshot(output)
        for table in before:
            if table not in ('state','inbox','semantic_metadata') and before[table]!=after.get(table):raise ValueError('RECEIPT_DRIFT')
        if digest(snapshot(database))!=plan['baseline']:raise ValueError('SOURCE_CHANGED')
        if verify_bundle(bundle)!=plan['target']:raise ValueError('TARGET_DRIFT')
        with output.open('rb') as f:os.fsync(f.fileno())
        fd=os.open(output.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
        return {'status':'prepared-generation','baseline':plan['baseline'],'target':plan['target'],'result':digest(after),'authority_effect':'none'}
    except Exception:
        # Only this function's new output is removed; never source or an existing generation.
        output.unlink(missing_ok=True)
        raise
