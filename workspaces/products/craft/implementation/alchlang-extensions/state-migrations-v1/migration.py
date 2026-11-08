"""Bounded SQLite snapshots and isolated execution of DomainSpec-generated defaults."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import time

LIMIT=64*1024*1024
def require(value,code):
    if not value:raise ValueError(code)
def digest(value):return hashlib.sha256(value).hexdigest()
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

def semantic(value):
    if isinstance(value,dict):return {k:semantic(v) for k,v in value.items() if k not in ('source_refs','binding_digest')}
    if isinstance(value,list):return [semantic(v) for v in value]
    return value

def validate_change(old,new,contract):
    old,new=Path(old),Path(new)
    m=json.loads((new/'migration.json').read_bytes())
    require(m['profile']=='alch.state-migration/v1' and m['from_contract']==contract,'MIGRATION_SOURCE_MISMATCH')
    require(digest((new/'migration.mjs').read_bytes())==m['mapper_sha256'],'MAPPER_DRIFT')
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

def snapshot(source,destination):
    source,destination=Path(source),Path(destination)
    require(source.is_file() and not source.is_symlink() and not destination.exists(),'SNAPSHOT_PATH')
    require(source.stat().st_size<=LIMIT,'MIGRATION_STORAGE_LIMIT')
    deadline=time.monotonic()+10
    def progress(status,remaining,total):
        require(total*4096<=LIMIT and time.monotonic()<deadline,'SNAPSHOT_LIMIT')
    with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True,timeout=5) as src,sqlite3.connect(destination) as dst:
        require(src.execute('PRAGMA page_size').fetchone()[0]==4096,'SNAPSHOT_PAGE_SIZE')
        src.backup(dst,pages=128,progress=progress,sleep=.01)
    os.chmod(destination,0o600)

def preserved(db):
    tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name") if r[0]!='state']
    require(all(t.replace('_','').isalnum() for t in tables),'TABLE_NAME')
    return {t:sorted(db.execute('SELECT * FROM "'+t+'"').fetchall(),key=repr) for t in tables}

def logical_digest(db):
    return digest(encoded({'state':db.execute('SELECT operation,key,state,version FROM state ORDER BY operation,key').fetchall(),'other_tables':preserved(db)}))

def transform(database,bundle,manifest,node):
    """The mapper receives JSON through stdin; no database or tenant filesystem mount."""
    bundle=Path(bundle);database=Path(database)
    with sqlite3.connect(database) as db:
        require(db.execute('PRAGMA integrity_check').fetchall()==[('ok',)],'DATABASE_INTEGRITY')
        require(db.execute('SELECT COUNT(*) FROM state').fetchone()[0]<=10000,'MIGRATION_ROW_LIMIT')
        all_rows=db.execute('SELECT operation,key,state,version FROM state ORDER BY operation,key').fetchall()
        rows=[r for r in all_rows if r[0] in manifest['operations']]
        originals=[json.loads(r[2]) for r in rows];payload=encoded(originals)
        require(len(payload)<=16*1024*1024,'MIGRATION_INPUT_LIMIT')
        command=['/usr/bin/bwrap','--die-with-parent','--unshare-all','--new-session','--clearenv',
                 '--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64',
                 '--proc','/proc','--dev','/dev','--tmpfs','/tmp','--ro-bind',str(node),'/node',
                 '--ro-bind',str(bundle/'migration.mjs'),'/work/migration.mjs',
                 '--ro-bind',str(bundle/'migrate.mjs'),'/work/migrate.mjs',
                 '/node','--max-old-space-size=128','/work/migrate.mjs']
        result=subprocess.run(command,input=payload,capture_output=True,timeout=15)
        require(result.returncode==0,'MAPPER_FAILED')
        require(len(result.stdout)<=32*1024*1024,'MAPPER_OUTPUT_LIMIT')
        mapped=json.loads(result.stdout);require(isinstance(mapped,list) and len(mapped)==len(rows),'MAPPER_CARDINALITY')
        receipts=preserved(db);unchanged=[r for r in all_rows if r[0] not in manifest['operations']]
        for original,value,row in zip(originals,mapped,rows):
            field=manifest['field']
            require(isinstance(original,dict) and field not in original,'STATE_FIELD_CONFLICT')
            require(isinstance(value,dict) and set(value)==set(original)|{field},'MAPPER_FIELDS')
            require(encoded({k:v for k,v in value.items() if k!=field})==encoded(original),'MAPPER_PRESERVATION')
            require(encoded(value[field])==encoded(manifest['default']),'MAPPER_DEFAULT')
            db.execute('UPDATE state SET state=? WHERE operation=? AND key=?',(encoded(value).decode(),row[0],row[1]))
        require(receipts==preserved(db),'RECEIPT_CHANGED')
        current=db.execute('SELECT operation,key,state,version FROM state ORDER BY operation,key').fetchall()
        require([(r[0],r[1],r[3]) for r in all_rows]==[(r[0],r[1],r[3]) for r in current],'STATE_IDENTITY_CHANGED')
        require(unchanged==[r for r in current if r[0] not in manifest['operations']],'UNSELECTED_STATE_CHANGED')
        require(db.execute('PRAGMA integrity_check').fetchall()==[('ok',)],'DATABASE_INTEGRITY')
        logical=logical_digest(db)
    with sqlite3.connect(database) as db:db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    with database.open('rb') as stream:os.fsync(stream.fileno())
    return {'rows':len(rows),'mapper_sha256':manifest['mapper_sha256'],'receipts_sha256':digest(encoded(receipts)),
            'result_sha256':digest(database.read_bytes()),'logical_sha256':logical,'checks':['default','existing-fields','state-keys-and-versions','all-other-tables','integrity'],
            'authority_effect':'none'}
