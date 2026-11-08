"""Real Rust / bubblewrap / Ansible host and non-effectful generation migration tests."""
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
import migration

HERE=Path(__file__).resolve().parent
CLI=HERE.parent.parent/'implementation/dist/cli.js'
NODE='/home/vrondelli/.nvm/versions/node/v26.8.1/bin/node'
CONTEXT={'actor':'OrderService','grants':['order-transaction-authority'],'transport_grants':['orders-local']}
POLICY={**CONTEXT,'operations':['place-order'],'isolation':'bubblewrap','consumer':{'actor':'OrderService','grants':['order-transaction-authority'],'operation':'record-order'}}
TOKEN='semantic_local_fixture_'*3

class SemanticHost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=Path(tempfile.mkdtemp(prefix='semantic-host-tests-'));cls.bundle=cls.temp/'bundle'
        cls.root=Path('/tmp/alch-provision-semantic-'+cls.temp.name);cls.proc=None;cls.addClassCleanup(cls.cleanup)
        def build(source,name):
            file=cls.temp/(name+'.alch');file.write_text(source);out=cls.temp/name
            p=subprocess.run([NODE,str(CLI),'build',str(file),'--out',str(out)],capture_output=True,text=True,timeout=180)
            assert p.returncode==0,(p.stdout,p.stderr)
            return out
        cls.bundle=build((HERE/'orders.alch').read_text(),'bundle')
        cls.next=build((HERE/'orders.alch').read_text().replace('  note: string required default ""','  note: string required default ""\n  revisionTag: string required default "v2"'),'next')
        cls.start()

    @classmethod
    def start(cls):
        cls.proc=subprocess.Popen([sys.executable,str(cls.bundle/'serve.py'),'--run-root',str(cls.root)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'ALCH_HOST_TOKEN':TOKEN,'ALCH_HOST_POLICY':json.dumps(POLICY),'PYTHONDONTWRITEBYTECODE':'1'})
        with selectors.DefaultSelector() as s:
            s.register(cls.proc.stdout,selectors.EVENT_READ)
            if not s.select(60):raise AssertionError('host startup timeout')
        line=json.loads(cls.proc.stdout.readline())
        assert line['status']=='listening',line
        cls.port=int(line['url'].rsplit(':',1)[1]);cls.db=cls.root/'target/state/runtime/function.sqlite'

    @classmethod
    def stop(cls):
        if cls.proc:
            cls.proc.terminate();cls.proc.wait(timeout=15);cls.proc.stdout.close();cls.proc.stderr.close();cls.proc=None

    @classmethod
    def cleanup(cls):
        cls.stop()
        artifacts=[{'name':name,'manifest':json.loads((cls.temp/name/'manifest.json').read_bytes())} for name in ('bundle','next') if (cls.temp/name/'manifest.json').exists()]
        (HERE/'host-artifacts.json').write_text(json.dumps({'status':'built-test-fixtures','artifacts':artifacts,'authority_effect':'none'},indent=2)+'\n')
        shutil.rmtree(cls.temp,ignore_errors=True);shutil.rmtree(cls.root,ignore_errors=True)

    @classmethod
    def http(cls,body,token=TOKEN):
        connection=http.client.HTTPConnection('127.0.0.1',cls.port,timeout=10)
        try:
            connection.request('POST','/functions/orders-local/place-order',json.dumps(body),{'Authorization':'Bearer '+token,'Content-Type':'application/json'})
            r=connection.getresponse();return r.status,json.loads(r.read())
        finally:connection.close()

    @classmethod
    def request(cls,body):
        until=time.monotonic()+10
        while time.monotonic()<until:
            result=cls.http(body)
            if result[0]!=503:return result
            time.sleep(.05)
        raise AssertionError('host stayed busy')

    @staticmethod
    def native(bundle,database,request):
        p=subprocess.run([str(bundle/'alch-event')],input=json.dumps({'request':request,'context':CONTEXT}),text=True,capture_output=True,env={**os.environ,'ALCH_EVENT_DATABASE':str(database)},timeout=10)
        return json.loads(p.stdout)

    def test_01_host_create_delivery_restart_and_replay(self):
        body={'facts':{'orderId':'host-1','payload':{'quantity':2}},'message_id':'host-m1','expected_version':0}
        self.assertEqual(self.http(body,'bad')[0],401)
        self.assertEqual(self.request(body)[1]['status'],'committed')
        until=time.monotonic()+10
        while time.monotonic()<until:
            data=migration.snapshot(self.db)
            if data['outbox'][0][4]=='published':break
            time.sleep(.1)
        self.assertEqual(data['outbox'][0][4],'published');self.assertEqual(len(data['state']),2);self.assertEqual(len(data['inbox']),1)
        self.stop();self.start()
        self.assertEqual(self.request(body)[1]['status'],'already-committed')
        self.assertEqual(self.request({**body,'facts':{**body['facts'],'status':'pending'}})[0],422)

    def test_02_migration_backfill_new_generation_and_replay(self):
        self.stop()
        ownership={'entity:Order':'entity:Order','projection:RecordedOrder':'projection:RecordedOrder'}
        fills={name:{'revisionTag':'v2'} for name in ownership}
        plan=migration.prepare(self.db,self.next,ownership,fills);self.assertEqual(migration.prepare(self.db,self.next,ownership),plan);out=self.temp/'migrated.sqlite'
        before=migration.snapshot(self.db);receipt=migration.apply(self.db,self.next,plan,out)
        self.assertEqual(receipt['status'],'prepared-generation');self.assertEqual(migration.snapshot(self.db),before)
        after=migration.snapshot(out)
        for row in after['state']:self.assertEqual(json.loads(row[2])['revisionTag'],'v2')
        self.assertEqual(after['outbox'],before['outbox']);self.assertEqual(after['inbox'],before['inbox'])
        # Existing producer fingerprint and versions survive a schema-only extension.
        request={'command':'invoke','operation':'place-order','facts':{'orderId':'host-1','payload':{'quantity':2}},'message_id':'host-m1','expected_version':0,'now':1788696000000,'at':'2026-09-06T12:00:00.000Z'}
        self.assertEqual(self.native(self.next,out,request)['status'],'already-committed')
        fresh={**request,'facts':{'orderId':'host-2','payload':{}},'message_id':'host-m2'}
        self.assertEqual(self.native(self.next,out,fresh)['status'],'committed')
        clock={'now':1788696000000,'at':'2026-09-06T12:00:00.000Z'}
        claim=self.native(self.next,out,{'command':'claim','worker':'migration-test',**clock})
        self.assertEqual(self.native(self.next,out,{'command':'invoke','operation':'record-order','message':claim['message'],**clock})['status'],'processed')
        self.assertEqual(self.native(self.next,out,{'command':'settle','worker':'migration-test','message_id':'host-m2','attempt':claim['attempt'],'outcome':'provider-accepted',**clock})['status'],'published')
        reverse={'entity:Order':'entity:Order','projection:RecordedOrder':'projection:RecordedOrder'}
        rollback=migration.prepare(out,self.bundle,reverse)
        with self.assertRaisesRegex(ValueError,'DESTRUCTIVE_CHANGE'):migration.apply(out,self.bundle,rollback,self.temp/'rollback.sqlite')
        self.start()

    def test_03_stale_plan_tamper_and_interruption(self):
        self.stop();ownership={'entity:Order':'entity:Order','projection:RecordedOrder':'projection:RecordedOrder'}
        fills={name:{'revisionTag':'v2'} for name in ownership};plan=migration.prepare(self.db,self.next,ownership,fills)
        tampered=copy.deepcopy(plan);tampered['backfills']['entity:Order']['revisionTag']='bad'
        with self.assertRaisesRegex(ValueError,'PLAN_DRIFT'):migration.apply(self.db,self.next,tampered,self.temp/'tamper.sqlite')
        with self.assertRaisesRegex(ValueError,'INJECTED_FAILURE'):migration.apply(self.db,self.next,plan,self.temp/'interrupted.sqlite','before-commit')
        self.assertFalse((self.temp/'interrupted.sqlite').exists())
        with sqlite3.connect(self.db) as db:db.execute('UPDATE state SET version=version+1')
        with self.assertRaisesRegex(ValueError,'STALE_PLAN'):migration.apply(self.db,self.next,plan,self.temp/'stale.sqlite')
        drift=self.temp/'drift';shutil.copytree(self.next,drift);(drift/'config.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'BUNDLE_DRIFT'):migration.prepare(self.db,drift,ownership,fills)
        self.start()

    def test_04_legacy_identity_requires_explicit_mapping_and_archives_old_fields(self):
        legacy=self.temp/'legacy.sqlite'
        with sqlite3.connect(legacy) as db:
            db.executescript('CREATE TABLE state(operation TEXT,key TEXT,state TEXT,version INTEGER,PRIMARY KEY(operation,key));CREATE TABLE outbox(id TEXT PRIMARY KEY,body TEXT,commit_json TEXT,attempts INTEGER,status TEXT,available INTEGER,lease_owner TEXT,lease_until INTEGER);CREATE TABLE inbox(operation TEXT,id TEXT,body TEXT,PRIMARY KEY(operation,id));')
            db.execute('INSERT INTO state VALUES(?,?,?,?)',('place-order','old1',json.dumps({'orderId':'old1','status':'committed','payload':{},'operationId':'preserve-in-archive'}),7))
        self.assertEqual(self.native(self.bundle,legacy,{'command':'inspect'})['error'],'LEGACY_MIGRATION_REQUIRED')
        with self.assertRaisesRegex(ValueError,'OWNERSHIP'):migration.prepare(legacy,self.bundle,{})
        plan=migration.prepare(legacy,self.bundle,{'place-order':'entity:Order'},{'entity:Order':{'note':''}})
        out=self.temp/'legacy-next.sqlite';migration.apply(legacy,self.bundle,plan,out)
        data=migration.snapshot(out);self.assertEqual(data['state'][0][0],'entity:Order');self.assertEqual(data['state'][0][3],7)
        self.assertEqual(json.loads(data['legacy_states'][0][2])['operationId'],'preserve-in-archive')
        self.assertEqual(self.native(self.bundle,out,{'command':'inspect'})['states'][0]['state']['note'],'')

if __name__=='__main__':unittest.main(verbosity=2)
