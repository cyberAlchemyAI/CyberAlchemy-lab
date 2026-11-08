"""Queued builds, tenant isolation, schema-derived migration and uncertain route selection."""
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

class Controller(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(tempfile.mkdtemp(prefix='semantic-controller-test-'));cls.proc=None;cls.addClassCleanup(cls.cleanup)
        cls.config=json.loads((c.base.HERE/'operator.example.json').read_bytes())
        for user in cls.config['users']:
            user['token_sha256']=c.sha(((user['id']+'_fixture_')*5).encode());user['policy']['transport_grants']=['orders-local']
        cls.config_path=cls.root/'operator.json';cls.config_path.write_text(json.dumps(cls.config))
        cls.start()
        for user in ('alice','bob'):assert cls.request(user,'POST','/v1/projects/shop',{})[0]==200
        source=(c.HERE/'orders.alch').read_text();cls.old=cls.build(source)
        cls.new=cls.build(source.replace('  note: string required default ""','  note: string required default ""\n  revisionTag: string required default "v2"'))
        assert cls.prepare(cls.old)[0]==200
        status,value=cls.activate(cls.old);assert status==200,(status,value)
        cls.key=value['state_key'];cls.old_key=cls.key
        cls.body={'facts':{'orderId':'controller-o1','payload':{'quantity':2}},'message_id':'controller-m1','expected_version':0}
        assert cls.invoke(cls.body)[1]['status']=='committed';cls.wait_published(1)

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
        if cls.proc:
            cls.proc.terminate();cls.proc.wait(timeout=45);cls.proc.stdout.close();cls.proc.stderr.close();cls.proc=None

    @classmethod
    def cleanup(cls):
        cls.stop();keys=set()
        if (cls.root/'registry.sqlite').exists():
            with sqlite3.connect(cls.root/'registry.sqlite') as db:
                for table,column in [('function_states','state_key'),('migrations','old_key'),('migrations','new_key')]:
                    if db.execute('SELECT 1 FROM sqlite_master WHERE name=?',(table,)).fetchone():keys.update(r[0] for r in db.execute(f'SELECT {column} FROM {table}'))
        for key in keys:shutil.rmtree('/tmp/alch-provision-semantic-controller-'+key,ignore_errors=True)
        artifacts=[{'revision':p.parent.parent.name,'manifest':json.loads(p.read_bytes())} for p in (cls.root/'revisions').glob('*/bundle/manifest.json')]
        (c.HERE/'controller-artifacts.json').write_text(json.dumps({'status':'built-test-fixtures','artifacts':artifacts,'authority_effect':'none'},indent=2)+'\n')
        shutil.rmtree(cls.root,ignore_errors=True)

    @classmethod
    def request(cls,user,method,path,body=None):
        conn=http.client.HTTPConnection('127.0.0.1',cls.port,timeout=100)
        try:
            conn.request(method,path,None if body is None else json.dumps(body),{'Authorization':'Bearer '+(user+'_fixture_')*5,'Content-Type':'application/json'})
            r=conn.getresponse();return r.status,json.loads(r.read())
        finally:conn.close()

    @classmethod
    def build(cls,source):
        status,value=cls.request('alice','POST','/v1/projects/shop/revisions',{'source':source});assert status==202,(status,value)
        revision=value['revision'];until=time.monotonic()+230
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
    def invoke(cls,body):
        for _ in range(100):
            result=cls.request('alice','POST','/v1/projects/shop/functions/orders-local/invoke',body)
            if result[0]!=503:return result
            time.sleep(.05)
        raise AssertionError('busy')
    @classmethod
    def database(cls):return Path('/tmp/alch-provision-semantic-controller-'+cls.key)/'target/state/runtime/function.sqlite'
    @classmethod
    def wait_published(cls,count):
        until=time.monotonic()+15
        while time.monotonic()<until:
            with sqlite3.connect(cls.database()) as db:
                if db.execute("SELECT COUNT(*) FROM outbox WHERE status='published'").fetchone()[0]==count:return
            time.sleep(.1)
        raise AssertionError('delivery timeout')

    def test_01_tenant_and_input_boundaries(self):
        self.assertEqual(self.request('bob','GET',f'/v1/projects/shop/revisions/{self.old}')[0],404)
        self.assertEqual(self.invoke({**self.body,'facts':{**self.body['facts'],'status':'pending'}})[0],400)
        self.assertEqual(self.activate(self.new)[1]['error'],'PREPARATION_REQUIRED')
        status,plan=self.prepare(self.new);self.assertEqual(status,200,plan);self.assertEqual(plan['kind'],'additive')
        self.assertEqual(plan['migration']['additions']['Order'],['revisionTag'])

    def test_02_failed_selection_restores_old_host(self):
        self.stop();plane=c.Plane(self.root,self.config);user=next(u for u in plane.users.values() if u['id']=='alice')
        try:
            plane.restore_selected()
            with patch.object(plane,'select',side_effect=ValueError('injected-before-selection')):
                with self.assertRaises(c.Rejected):plane.activate(user,'shop',self.new)
            self.assertEqual(plane.state('alice','shop','orders-local')['state_key'],self.old_key)
            self.assertEqual(plane.invoke(user,'shop','orders-local',self.body)[1]['status'],'already-committed')
        finally:plane.close();self.start()

    def test_03_uncertain_commit_restores_durable_new_selection(self):
        self.stop();plane=c.Plane(self.root,self.config);user=next(u for u in plane.users.values() if u['id']=='alice');select=plane.select
        def uncertain(*args,**kwargs):select(*args,**kwargs);raise ValueError('injected-after-selection')
        try:
            plane.restore_selected()
            with patch.object(plane,'select',side_effect=uncertain):
                with self.assertRaises(c.Rejected):plane.activate(user,'shop',self.new)
            type(self).key=plane.state('alice','shop','orders-local')['state_key'];self.assertNotEqual(self.key,self.old_key)
            self.assertEqual(plane.invoke(user,'shop','orders-local',self.body)[1]['status'],'already-committed')
        finally:plane.close();self.start()
        self.assertEqual(self.invoke(self.body)[1]['status'],'already-committed')
        with sqlite3.connect(self.database()) as db:
            for row in db.execute('SELECT state FROM state'):self.assertEqual(json.loads(row[0])['revisionTag'],'v2')
        fresh={**self.body,'facts':{'orderId':'controller-o2','payload':{}},'message_id':'controller-m2'}
        self.assertEqual(self.invoke(fresh)[1]['status'],'committed');self.wait_published(2)

    def test_04_preparation_digest_and_stale_baseline(self):
        self.assertEqual(self.activate(self.old)[1]['error'],'BASELINE_CHANGED')
        self.stop();plane=c.Plane(self.root,self.config);user=next(u for u in plane.users.values() if u['id']=='alice')
        try:
            plane.restore_selected();saved=plane.db.execute('SELECT plan FROM prepared WHERE revision=?',(self.old,)).fetchone()[0]
            bad=json.loads(saved);bad['digest']='0'*64
            with plane.db:plane.db.execute('UPDATE prepared SET plan=? WHERE revision=?',(json.dumps(bad),self.old))
            with self.assertRaisesRegex(c.Rejected,'PLAN_DRIFT'):plane.activate(user,'shop',self.old)
            with plane.db:plane.db.execute('UPDATE prepared SET plan=? WHERE revision=?',(saved,self.old))
        finally:plane.close();self.start()

if __name__=='__main__':unittest.main(verbosity=2)
