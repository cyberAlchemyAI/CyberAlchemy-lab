"""Real HTTP builds, isolated Rust hosts, SQLite migrations and injected switch failures."""
import copy
import http.client
import json
import os
from pathlib import Path
import selectors
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import control_plane as c
from planner import snapshot,transform,derive_change,previous
preserved=previous.preserved

class Migrations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(tempfile.mkdtemp(prefix='alch-migration-test-'))
        cls.config=json.loads((c.base.HERE/'operator.example.json').read_bytes())
        for u in cls.config['users']:u['token_sha256']=c.sha(((u['id']+'_fixture_')*5).encode())
        cls.config_path=cls.root/'operator.json';cls.config_path.write_text(json.dumps(cls.config))
        cls.addClassCleanup(cls.cleanup);cls.start()
        for user in ('alice','bob'):assert cls.request(user,'POST','/v1/projects/shop',{})[0]==200
        cls.old=cls.build((c.HERE/'orders-v1.alch').read_text())
        cls.old_bundle=cls.root/'revisions'/cls.old/'bundle'
        cls.contract=c.upgrade.fingerprint(cls.old_bundle)
        print('source_contract='+cls.contract,flush=True)
        cls.source=(c.HERE/'orders-v2.alch').read_text()
        cls.new=cls.build(cls.source);cls.bundle=cls.root/'revisions'/cls.new/'bundle'
        cls.compatible=cls.build((c.HERE/'orders-v1.alch').read_text()+'\n# Compatible revision for baseline fencing.\n')
        assert cls.prepare(cls.old)[0]==200
        status,value=cls.activate(cls.old);assert status==200,(status,value)
        cls.old_key=value['state_key'];cls.key=cls.old_key
        req=json.loads((c.HERE.parent/'event-execution-v1/place-order.request.json').read_bytes())['request']
        cls.body={k:req[k] for k in ('facts','expected_version')}
        assert cls.invoke(1)[0]==200;cls.wait_published(1)

    @classmethod
    def start(cls):
        cls.proc=subprocess.Popen([sys.executable,str(c.HERE/'control_plane.py'),'--root',str(cls.root),'--config',str(cls.config_path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        with selectors.DefaultSelector() as s:
            s.register(cls.proc.stdout,selectors.EVENT_READ);assert s.select(70),'controller start timeout';line=cls.proc.stdout.readline()
        if not line:raise AssertionError(cls.proc.stderr.read().decode())
        cls.port=int(json.loads(line)['url'].rsplit(':',1)[1])
    @classmethod
    def stop(cls):
        if getattr(cls,'proc',None):
            if cls.proc.poll() is None:cls.proc.terminate();cls.proc.wait(timeout=45)
            cls.proc.stdout.close();cls.proc.stderr.close();cls.proc=None
    @classmethod
    def cleanup(cls):
        cls.stop();keys=set()
        if (cls.root/'registry.sqlite').exists():
            with sqlite3.connect(cls.root/'registry.sqlite') as db:
                for table,column in [('function_states','state_key'),('migrations','new_key'),('migrations','old_key')]:
                    if db.execute('SELECT 1 FROM sqlite_master WHERE name=?',(table,)).fetchone():keys.update(r[0] for r in db.execute(f'SELECT {column} FROM {table}'))
        for key in keys:
            path=Path('/tmp/alch-provision-ontology-'+key)
            if path.exists():shutil.rmtree(path)
        shutil.rmtree(cls.root)
    @classmethod
    def request(cls,user,method,path,body=None):
        conn=http.client.HTTPConnection('127.0.0.1',cls.port,timeout=100)
        try:
            conn.request(method,path,None if body is None else json.dumps(body),{'Authorization':'Bearer '+(user+'_fixture_')*5,'Content-Type':'application/json'})
            response=conn.getresponse();return response.status,json.loads(response.read())
        finally:conn.close()
    @classmethod
    def build(cls,source):
        status,value=cls.request('alice','POST','/v1/projects/shop/revisions',{'source':source});assert status==202,(status,value)
        revision=value['revision'];until=time.monotonic()+210
        while time.monotonic()<until:
            status,value=cls.request('alice','GET',f'/v1/projects/shop/revisions/{revision}')
            if value['status']=='ready':return revision
            if value['status']=='failed':raise AssertionError((value,(cls.root/'revisions'/revision/'build.log').read_text()))
            time.sleep(.2)
        raise AssertionError('build timeout')
    @classmethod
    def prepare(cls,revision):return cls.request('alice','POST',f'/v1/projects/shop/revisions/{revision}/prepare',{})
    @classmethod
    def activate(cls,revision):return cls.request('alice','POST',f'/v1/projects/shop/revisions/{revision}/activate',{})
    @classmethod
    def database(cls,key=None):return Path('/tmp/alch-provision-ontology-'+(key or cls.key))/'target/state/runtime/function.sqlite'
    @classmethod
    def invoke(cls,n):
        body=copy.deepcopy(cls.body);body['expected_version']=n-1;body['facts']['outboxMessageId']='migration-m'+str(n);body['facts']['operationId']='op'+str(n)
        for _ in range(100):
            status,value=cls.request('alice','POST','/v1/projects/shop/functions/orders-local/invoke',body)
            if status!=503:return status,value
            time.sleep(.05)
        raise AssertionError('persistent busy')
    @classmethod
    def wait_published(cls,n):
        until=time.monotonic()+15
        while time.monotonic()<until:
            with sqlite3.connect(cls.database()) as db:
                if db.execute("SELECT COUNT(*) FROM outbox WHERE status='published'").fetchone()[0]==n:return
            time.sleep(.05)
        raise AssertionError('delivery incomplete')
    @classmethod
    def view(cls,key=None):
        with sqlite3.connect(cls.database(key)) as db:return db.execute('SELECT operation,key,state,version FROM state ORDER BY operation,key').fetchall(),preserved(db)

    def test_01_ontology_drives_schemas_and_prepared_mapper(self):
        status,value=self.activate(self.new);self.assertEqual(status,409);self.assertEqual(value['error'],'PREPARATION_REQUIRED')
        status,plan=self.prepare(self.new);self.assertEqual(status,200,plan)
        type(self).manifest=plan['migration']
        self.assertEqual(plan['baseline']['revision'],self.old)
        self.assertEqual(plan['migration']['field'],'schemaVersion')
        self.assertNotIn('from-contract',self.source);self.assertNotIn('migration ',self.source)
        self.assertEqual(self.prepare(self.new)[1]['digest'],plan['digest'])
        typed=json.loads((self.bundle/'typed-ontology.json').read_bytes());schemas=json.loads((self.bundle/'schemas.json').read_bytes())
        prop=next(p for p in typed['records']['OrderOperation']['properties'] if p['name']=='schemaVersion')
        self.assertEqual(prop['default'],'v2');self.assertFalse(prop['required'])
        self.assertEqual(schemas['facts']['OrderOperation']['properties']['schemaVersion']['default'],'v2')
        before=self.view()
        with tempfile.TemporaryDirectory(prefix='alch-ontology-rehearsal-') as tmp:
            target=Path(tmp)/'copy.sqlite';snapshot(self.database(),target)
            receipt=transform(target,self.bundle,self.manifest,c.base.NODE)
            self.assertEqual(receipt['rows'],2)
            with sqlite3.connect(target) as db:self.assertEqual(preserved(db),before[1])
        self.assertEqual(before,self.view())

    def test_02_stale_baseline_rejects_and_requires_new_candidate(self):
        self.assertEqual(self.request('bob','POST',f'/v1/projects/shop/revisions/{self.new}/prepare',{})[0],404)
        self.assertEqual(self.prepare(self.compatible)[0],200)
        self.assertEqual(self.activate(self.compatible)[0],200)
        status,value=self.activate(self.new);self.assertEqual(status,409);self.assertEqual(value['error'],'BASELINE_CHANGED')
        self.assertEqual(self.prepare(self.new)[0],409)
        cls=type(self);cls.old=cls.compatible;cls.old_bundle=cls.root/'revisions'/cls.old/'bundle'
        cls.new=cls.build(cls.source);cls.bundle=cls.root/'revisions'/cls.new/'bundle'
        status,plan=cls.prepare(cls.new);self.assertEqual(status,200,plan);cls.manifest=plan['migration']
        self.assertEqual(self.invoke(1)[0],200)

    def test_03_failed_rehearsal_keeps_old_host_usable(self):
        self.stop();plane=c.Plane(self.root,self.config);user=next(u for u in plane.users.values() if u['id']=='alice')
        try:
            plane.restore_selected();before=self.view()
            with patch.object(c,'transform',side_effect=ValueError('fixture-mapper-failure')):
                with self.assertRaises(c.Rejected):plane.activate(user,'shop',self.new)
            self.assertEqual(plane.state('alice','shop','orders-local')['state_key'],self.old_key)
            self.assertEqual(before,self.view())
        finally:plane.close();self.start()
        self.assertEqual(self.invoke(1)[0],200)

    def test_04_failure_after_candidate_readiness_restores_old(self):
        self.stop();plane=c.Plane(self.root,self.config);user=next(u for u in plane.users.values() if u['id']=='alice')
        try:
            plane.restore_selected();before=self.view()
            with patch.object(plane,'select',side_effect=RuntimeError('fixture-before-route-commit')):
                with self.assertRaises(c.Rejected):plane.activate(user,'shop',self.new)
            self.assertEqual(plane.state('alice','shop','orders-local')['state_key'],self.old_key)
            self.assertEqual(before,self.view())
        finally:plane.close();self.start()
        self.assertEqual(self.invoke(1)[0],200)

    def test_05_real_migration_preserves_replay_and_new_writes(self):
        before=self.view();status,value=self.activate(self.new);self.assertEqual(status,200,value)
        type(self).key=value['state_key'];self.assertNotEqual(self.key,self.old_key)
        after=self.view();self.assertEqual(before[1],after[1]);self.assertEqual(before,self.view(self.old_key))
        for old,new in zip(before[0],after[0]):
            self.assertEqual(old[:2],new[:2]);self.assertEqual(old[3],new[3]);expected=json.loads(old[2]);expected['schemaVersion']='v2';self.assertEqual(expected,json.loads(new[2]))
        status,value=self.invoke(1);self.assertEqual(status,200);self.assertEqual(value['status'],'already-committed')
        self.assertEqual(self.invoke(2)[0],200);self.wait_published(2)
        for row in self.view()[0]:self.assertEqual(json.loads(row[2])['schemaVersion'],'v2');self.assertEqual(row[3],2)

    def test_06_rollback_cannot_discard_post_migration_writes(self):
        before=self.view();status,value=self.activate(self.old)
        self.assertEqual(status,409);self.assertEqual(value['error'],'BASELINE_CHANGED')
        self.assertEqual(before,self.view());self.assertEqual(self.invoke(2)[0],200)

    def test_07_restart_uses_selected_generation(self):
        before=self.view();self.stop();self.start();self.assertEqual(before,self.view())
        self.assertEqual(self.invoke(2)[0],200)
        self.assertEqual(self.activate(self.new)[1]['state_key'],self.key)

    def test_08_mapper_failure_rolls_back_snapshot_transaction(self):
        with tempfile.TemporaryDirectory(prefix='alch-migration-conflict-') as tmp:
            target=Path(tmp)/'copy.sqlite';snapshot(self.database(),target)
            with sqlite3.connect(target) as db:before=(db.execute('SELECT * FROM state').fetchall(),preserved(db))
            with self.assertRaisesRegex(ValueError,'MAPPER_FAILED'):transform(target,self.bundle,self.manifest,c.base.NODE)
            with sqlite3.connect(target) as db:self.assertEqual(before,(db.execute('SELECT * FROM state').fetchall(),preserved(db)))

    def test_09_source_contract_binding_and_receipt(self):
        status,value=self.request('alice','GET',f'/v1/projects/shop/revisions/{self.old}')
        self.assertEqual(status,200);self.assertEqual(value['state_contract'],self.contract)
        self.assertEqual(self.manifest['from_contract'],self.contract)
        with sqlite3.connect(self.root/'registry.sqlite') as db:
            receipts=db.execute("SELECT receipt FROM migrations WHERE stage='selected'").fetchall()
        self.assertEqual(len(receipts),1);receipt=json.loads(receipts[0][0])
        self.assertEqual(receipt['source_contract'],self.contract);self.assertEqual(receipt['rows'],2)
        self.assertEqual(receipt['mapper_sha256'],self.manifest['mapper_sha256'])

    def test_10_generated_input_schema_rejects_invalid_facts(self):
        body=copy.deepcopy(self.body);body['facts']['schemaVersion']=42
        status,value=self.request('alice','POST','/v1/projects/shop/functions/orders-local/invoke',body)
        self.assertEqual(status,400);self.assertEqual(value['error'],'INPUT_SCHEMA_INVALID')
        body['facts'].pop('schemaVersion');body['facts']['undeclared']='x'
        self.assertEqual(self.request('alice','POST','/v1/projects/shop/functions/orders-local/invoke',body)[1]['error'],'INPUT_SCHEMA_INVALID')

    def test_11_ontology_diff_does_not_guess_business_changes(self):
        with tempfile.TemporaryDirectory(prefix='alch-ontology-diff-') as tmp:
            target=Path(tmp)/'bundle';shutil.copytree(self.bundle,target)
            typed=json.loads((target/'typed-ontology.json').read_bytes())
            field=next(p for p in typed['records']['OrderOperation']['properties'] if p['name']=='orderId')
            field['type']='integer'
            (target/'typed-ontology.json').write_text(json.dumps(typed))
            schemas=json.loads((target/'schemas.json').read_bytes());schemas['ontology_sha256']=c.sha(json.dumps(typed,separators=(',',':'),ensure_ascii=False).encode())
            (target/'schemas.json').write_text(json.dumps(schemas))
            with self.assertRaisesRegex(ValueError,'PROPERTY_CHANGE_REQUIRES_INTENT'):derive_change(self.old_bundle,target,self.contract)

if __name__=='__main__':unittest.main(verbosity=2)
