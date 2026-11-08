"""Real compiler/host/state handoff tests; fault mutations affect owned fixtures only."""
import copy
import http.client
import importlib.util
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
from compatibility import fingerprint


class Upgrades(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(tempfile.mkdtemp(prefix='alch-upgrade-test-'))
        cls.config=json.loads((c.base.HERE/'operator.example.json').read_text())
        for u in cls.config['users']:u['token_sha256']=c.sha(((u['id']+'_fixture_')*5).encode())
        cls.config_path=cls.root/'operator.json';cls.config_path.write_text(json.dumps(cls.config))
        cls.addClassCleanup(cls.cleanup);cls.start()
        cls.sources=[(c.HERE/'orders-v1.alch').read_text(),(c.HERE/'orders-v2.alch').read_text()]
        cls.revisions=[]
        for user in ('alice','bob'):assert cls.request(user,'POST','/v1/projects/shop',{})[0]==200
        for source in cls.sources:
            status,value=cls.request('alice','POST','/v1/projects/shop/revisions',{'source':source})
            assert status==202,(status,value);cls.revisions.append(value['revision'])
        for revision in cls.revisions:cls.ready('alice',revision)
        status,value=cls.request('alice','POST','/v1/projects/shop/revisions',{'source':cls.sources[0].replace('field status default string "committed"','field status default string "complete"')})
        assert status==202;(cls.bad,)= (value['revision'],)
        status,value=cls.request('bob','POST','/v1/projects/shop/revisions',{'source':cls.sources[0]})
        assert status==202;cls.bob=value['revision']
        cls.ready('alice',cls.bad);cls.ready('bob',cls.bob)
        status,value=cls.activate(cls.revisions[0]);assert status==200,(status,value)
        cls.key=value['state_key'];cls.database=Path('/tmp/alch-provision-upgrade-'+cls.key)/'target/state/runtime/function.sqlite'
        status,value=cls.request('bob','POST',f'/v1/projects/shop/revisions/{cls.bob}/activate',{})
        assert status==200,(status,value);cls.bobkey=value['state_key']
        request=json.loads((c.HERE.parent/'event-execution-v1/place-order.request.json').read_text())['request']
        cls.body={k:request[k] for k in ('facts','expected_version')}

    @classmethod
    def start(cls):
        cls.proc=subprocess.Popen([sys.executable,str(c.HERE/'control_plane.py'),'--root',str(cls.root),'--config',str(cls.config_path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        with selectors.DefaultSelector() as s:
            s.register(cls.proc.stdout,selectors.EVENT_READ)
            assert s.select(70),'controller start timeout'
            line=cls.proc.stdout.readline()
        if not line:raise AssertionError(cls.proc.stderr.read().decode())
        cls.port=int(json.loads(line)['url'].rsplit(':',1)[1])
    @classmethod
    def stop(cls):
        if getattr(cls,'proc',None):
            if cls.proc.poll() is None:cls.proc.terminate();cls.proc.wait(timeout=40)
            cls.proc.stdout.close();cls.proc.stderr.close()
    @classmethod
    def cleanup(cls):
        cls.stop()
        db=cls.root/'registry.sqlite'
        keys=[]
        if db.exists():
            with sqlite3.connect(db) as connection:
                if connection.execute("SELECT 1 FROM sqlite_master WHERE name='function_states'").fetchone():
                    keys=[r[0] for r in connection.execute('SELECT state_key FROM function_states')]
        for key in keys:
            path=Path('/tmp/alch-provision-upgrade-'+key)
            if path.exists():shutil.rmtree(path)
        shutil.rmtree(cls.root)
    @classmethod
    def request(cls,user,method,path,body=None):
        conn=http.client.HTTPConnection('127.0.0.1',cls.port,timeout=80)
        try:
            conn.request(method,path,None if body is None else json.dumps(body),{'Authorization':'Bearer '+(user+'_fixture_')*5,'Content-Type':'application/json'})
            response=conn.getresponse();return response.status,json.loads(response.read())
        finally:conn.close()
    @classmethod
    def ready(cls,user,revision):
        until=time.monotonic()+210
        while time.monotonic()<until:
            status,value=cls.request(user,'GET',f'/v1/projects/shop/revisions/{revision}')
            assert status==200,(status,value)
            if value['status']=='ready':return
            if value['status']=='failed':raise AssertionError((value,(cls.root/'revisions'/revision/'build.log').read_text()))
            time.sleep(.2)
        raise AssertionError('build timeout')
    @classmethod
    def activate(cls,revision):return cls.request('alice','POST',f'/v1/projects/shop/revisions/{revision}/activate',{})
    @classmethod
    def body_for(cls,n):
        body=copy.deepcopy(cls.body);body['expected_version']=n-1
        body['facts']['outboxMessageId']='m'+str(n);body['facts']['operationId']='op'+str(n)
        return body
    @classmethod
    def invoke(cls,n):
        for _ in range(80):
            status,value=cls.request('alice','POST','/v1/projects/shop/functions/orders-local/invoke',cls.body_for(n))
            if status!=503:return status,value
            time.sleep(.05)
        raise AssertionError('persistent busy')
    @classmethod
    def snapshot(cls):
        with sqlite3.connect(cls.database) as db:
            return {'state':db.execute('SELECT operation,version FROM state ORDER BY operation').fetchall(),
                    'outbox':db.execute('SELECT id,status,attempts FROM outbox ORDER BY id').fetchall(),
                    'inbox':db.execute('SELECT id FROM inbox ORDER BY id').fetchall()}
    @classmethod
    def published(cls,n):
        until=time.monotonic()+45
        while time.monotonic()<until:
            result=cls.snapshot()
            if len(result['outbox'])==n and all(row[1]=='published' for row in result['outbox']):return result
            time.sleep(.1)
        raise AssertionError(result)
    @classmethod
    def native(cls,request,context=None):
        bundle=cls.root/'revisions'/cls.revisions[0]/'bundle'
        spec=importlib.util.spec_from_file_location('fixture_worker',bundle/'local_worker.py')
        worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
        cfg=json.loads((bundle/'host.json').read_bytes())
        return worker.invoke(bundle,cfg,cls.database,request,context or {'actor':'OrderService','grants':['order-transaction-authority'],'transport_grants':['order-transport']})

    def test_01_v1_v2_rollback_preserves_orders_and_both_dedup_tables(self):
        self.assertEqual(self.invoke(1)[0],200)
        status,value=self.activate(self.revisions[1]);self.assertEqual(status,200,value);self.assertEqual(value['state_key'],self.key)
        self.assertEqual(self.invoke(1)[1]['status'],'already-committed')
        self.assertEqual(self.invoke(2)[0],200)
        status,value=self.activate(self.revisions[0]);self.assertEqual(status,200,value);self.assertEqual(value['state_key'],self.key)
        self.assertEqual(self.invoke(2)[1]['status'],'already-committed')
        result=self.published(2)
        self.assertEqual(result['state'],[('place-order',2),('record-order',2)])
        self.assertEqual(result['inbox'],[('m1',),('m2',)])

    def test_02_incompatible_mapping_rejected_without_route_or_state_change(self):
        before=self.snapshot()
        status,value=self.activate(self.bad)
        self.assertEqual(status,409,value);self.assertEqual(value['error'],'INCOMPATIBLE_REVISION')
        self.assertEqual(self.snapshot(),before)
        self.assertEqual(self.request('alice','GET','/v1/projects/shop')[1]['routes'][0]['revision'],self.revisions[0])

    def test_03_tenant_storage_and_activation_are_separate(self):
        self.assertNotEqual(self.key,self.bobkey)
        with sqlite3.connect(Path('/tmp/alch-provision-upgrade-'+self.bobkey)/'target/state/runtime/function.sqlite') as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM state').fetchone()[0],0)
        self.assertEqual(self.request('bob','POST',f'/v1/projects/shop/revisions/{self.revisions[0]}/activate',{})[0],404)
        self.assertEqual(self.request('alice','POST','/_host/drain',{})[0],404)

    def test_04_restart_delivers_pending_event_without_invocation(self):
        self.stop()
        code,value=self.native({'command':'invoke','operation':'place-order',**self.body_for(3)})
        self.assertEqual(code,0,value);self.assertEqual(self.snapshot()['outbox'][-1][1],'pending')
        self.start()
        result=self.published(3)
        self.assertEqual(result['state'],[('place-order',3),('record-order',3)])

    def test_05_upgrade_waits_for_scheduled_pending_event(self):
        self.stop()
        self.assertEqual(self.native({'command':'invoke','operation':'place-order',**self.body_for(4)})[0],0)
        with sqlite3.connect(self.database) as db:
            db.execute("UPDATE outbox SET available=? WHERE id='m4'",(int(time.time()*1000)+15000,))
        self.start()
        self.assertEqual(self.snapshot()['outbox'][-1][1],'pending')
        status,value=self.activate(self.revisions[1]);self.assertEqual(status,200,value)
        result=self.snapshot();self.assertTrue(all(row[1]=='published' for row in result['outbox']))
        self.assertEqual(result['state'],[('place-order',4),('record-order',4)])

    def test_06_readiness_failure_restores_old_host_and_route(self):
        self.stop();plane=c.Plane(str(self.root),self.config)
        try:
            user=self.config['users'][0];original=plane.launch
            def fail_after_ready(row,*args):
                result=original(row,*args)
                if row['id']==self.revisions[0]:raise c.Rejected('FIXTURE_AFTER_READY',503)
                return result
            with patch.object(plane,'launch',side_effect=fail_after_ready):
                with self.assertRaises(c.Rejected):plane.activate(user,'shop',self.revisions[0])
            self.assertEqual(plane.inspect(user,'shop')['routes'][0]['revision'],self.revisions[1])
            self.assertEqual(plane.running_revisions[self.key],self.revisions[1])
            status,value=plane.invoke(user,'shop','orders-local',self.body_for(4));self.assertEqual(status,200,value)
        finally:plane.close();self.start()

    def test_07_consumer_commit_before_lost_settlement_recovers_once(self):
        self.stop()
        self.assertEqual(self.native({'command':'invoke','operation':'place-order',**self.body_for(5)})[0],0)
        code,claim=self.native({'command':'claim','worker':'lost-worker'})
        self.assertEqual(code,0,claim);self.assertEqual(claim['status'],'leased')
        code,value=self.native({'command':'invoke','operation':'record-order','message':claim['message']})
        self.assertEqual(code,0,value)
        with sqlite3.connect(self.database) as db:
            db.execute("UPDATE outbox SET lease_until=0 WHERE id='m5'")
        self.start()
        result=self.published(5)
        self.assertEqual(result['state'],[('place-order',5),('record-order',5)])
        self.assertEqual(result['outbox'][-1],('m5','published',2))
        self.assertEqual(result['inbox'].count(('m5',)),1)

    def test_08_dead_event_blocks_upgrade_and_resumes_old_producer(self):
        with sqlite3.connect(self.database) as db:db.execute("UPDATE outbox SET status='dead' WHERE id='m5'")
        try:
            status,value=self.activate(self.revisions[0]);self.assertEqual(status,409,value);self.assertEqual(value['error'],'DRAIN_BLOCKED')
            self.assertEqual(self.invoke(5)[1]['status'],'already-committed')
            self.assertEqual(self.request('alice','GET','/v1/projects/shop')[1]['routes'][0]['revision'],self.revisions[1])
        finally:
            with sqlite3.connect(self.database) as db:db.execute("UPDATE outbox SET status='published' WHERE id='m5'")

    def test_09_compatibility_binds_shape_rules_identity_and_runtime(self):
        original=self.root/'revisions'/self.revisions[0]/'bundle'
        same=self.root/'revisions'/self.revisions[1]/'bundle'
        self.assertEqual(fingerprint(original),fingerprint(same))
        self.assertNotEqual(fingerprint(original),fingerprint(self.root/'revisions'/self.bad/'bundle'))
        with tempfile.TemporaryDirectory(prefix='alch-contract-test-') as work:
            clone=Path(work)/'bundle';shutil.copytree(original,clone)
            f=clone/'config.json';data=json.loads(f.read_bytes())
            for key in ['model','executions','event','transport']:
                modified=copy.deepcopy(data);modified[key]={'incompatible':True};f.write_text(json.dumps(modified))
                self.assertNotEqual(fingerprint(original),fingerprint(clone))
            f.write_text(json.dumps(data));runtime=clone/'rust/src/lib.rs';runtime.write_bytes(runtime.read_bytes()+b'\n')
            self.assertNotEqual(fingerprint(original),fingerprint(clone))


if __name__=='__main__':unittest.main(verbosity=2)
