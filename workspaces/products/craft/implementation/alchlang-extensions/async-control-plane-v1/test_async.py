"""Queue invariants plus real asynchronous HTTP/compiler/host integration."""
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


def config():
    value=json.loads((c.PREDECESSOR/'operator.example.json').read_text())
    prototype=value['users'][0]
    value['users']=[]
    for name in ('alice','bob','carol','david','eve'):
        user=copy.deepcopy(prototype)
        user.update(id=name,token_sha256=c.sha((name+'_fixture_') .encode()*5))
        value['users'].append(user)
    return value


def wait_for(predicate,seconds=10):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        value=predicate()
        if value:return value
        time.sleep(.05)
    raise AssertionError('condition timed out')


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix='alch-async-unit-'))
        self.config=config();self.plane=c.Plane(str(self.root),self.config)
        for user in self.config['users']:self.plane.project(user,'shop')
    def tearDown(self):
        self.plane.close();shutil.rmtree(self.root)
    def submit(self,name='alice',source='profile unsupported\n'):
        user=next(u for u in self.config['users'] if u['id']==name)
        return self.plane.build(user,'shop',source)['revision']

    def test_queue_caps_cover_active_and_waiting_without_partial_insert(self):
        self.submit();self.submit()
        self.plane.claim()
        with self.assertRaises(c.Rejected) as caught:self.submit()
        self.assertEqual(caught.exception.code,'BUILD_QUEUE_FULL')
        for name in ('bob','carol','david'):
            self.submit(name);self.submit(name)
        with self.assertRaises(c.Rejected) as caught:self.submit('eve')
        self.assertEqual(caught.exception.status,429)
        self.assertEqual(self.plane.db.execute('SELECT COUNT(*) FROM revisions').fetchone()[0],8)
        self.assertEqual(len(list((self.root/'revisions').iterdir())),8)

    def test_least_recently_dispatched_tenant_and_fifo(self):
        a=[self.submit(),self.submit()]
        b=[self.submit('bob'),self.submit('bob')]
        d=self.submit('carol')
        selected=[self.plane.claim()['id'] for _ in range(5)]
        self.assertEqual(selected,[a[0],b[0],d,a[1],b[1]])
        self.assertIsNone(self.plane.claim())

    def test_restart_retains_queue_and_dispatch_order_but_fails_active(self):
        active=self.submit();waiting=self.submit();bob=self.submit('bob')
        self.plane.claim();self.plane.close()
        self.plane=c.Plane(str(self.root),self.config)
        row=self.plane.revision(self.config['users'][0],'shop',active)
        self.assertEqual(row['status'],'failed');self.assertEqual(row['error'],'BUILD_INTERRUPTED')
        self.assertEqual(self.plane.revision(self.config['users'][0],'shop',waiting)['status'],'queued')
        self.assertEqual(self.plane.claim()['id'],bob)

    def test_queued_source_tamper_fails_before_launch(self):
        revision=self.submit()
        (self.root/'revisions'/revision/'source.alch').write_text('tampered')
        self.plane.start_worker()
        user=self.config['users'][0]
        row=wait_for(lambda: (r if (r:=self.plane.revision(user,'shop',revision))['status']=='failed' else None))
        self.assertEqual(row['error'],'SOURCE_DRIFT')
        self.assertFalse((self.root/'revisions'/revision/'build.log').exists())

    def test_revoked_build_permission_fails_queued_work(self):
        revision=self.submit();self.plane.close()
        self.config['users'][0]['scopes']=['read','invoke']
        self.plane=c.Plane(str(self.root),self.config);self.plane.start_worker()
        row=wait_for(lambda: (r if (r:=self.plane.revision(self.config['users'][0],'shop',revision))['status']=='failed' else None))
        self.assertEqual(row['error'],'FORBIDDEN')

    def test_worker_failure_is_visible_and_new_admission_stops(self):
        with patch.object(self.plane,'claim',side_effect=sqlite3.OperationalError('fixture storage failure')):
            self.plane.start_worker()
            wait_for(lambda:self.plane.worker_failure)
        with self.assertRaises(c.Rejected) as caught:self.submit()
        self.assertEqual(caught.exception.status,503)

    def test_shutdown_terminates_active_launcher_and_retains_waiting_work(self):
        active=self.submit();queued=self.submit('bob')
        with patch.object(c.base,'build_command',return_value=['/usr/bin/sleep','120']):
            self.plane.start_worker()
            proc=wait_for(lambda:self.plane.active_build)
            self.plane.close()
        self.assertIsNotNone(proc.poll())
        self.plane=c.Plane(str(self.root),self.config)
        self.assertEqual(self.plane.revision(self.config['users'][0],'shop',active)['error'],'BUILD_INTERRUPTED')
        self.assertEqual(self.plane.revision(self.config['users'][1],'shop',queued)['status'],'queued')

    def test_status_and_activation_cannot_cross_tenants_or_select_queue(self):
        revision=self.submit()
        with self.assertRaises(c.Rejected) as caught:self.plane.status(self.config['users'][1],'shop',revision)
        self.assertEqual(caught.exception.status,404)
        with self.assertRaises(c.Rejected) as caught:self.plane.activate(self.config['users'][0],'shop',revision)
        self.assertEqual(caught.exception.code,'REVISION_NOT_READY')
        self.assertEqual(self.plane.inspect(self.config['users'][0],'shop')['routes'],[])

    def test_changed_support_code_blocks_queued_execution(self):
        revision=self.submit()
        with patch.object(self.plane,'support_binding',return_value={}):
            self.plane.start_worker()
            row=wait_for(lambda: (r if (r:=self.plane.revision(self.config['users'][0],'shop',revision))['status']=='failed' else None))
            self.assertEqual(row['error'],'SUPPORT_DRIFT')
        self.assertFalse((self.root/'revisions'/revision/'build.log').exists())

    def test_old_store_requires_explicit_migration(self):
        with tempfile.TemporaryDirectory(prefix='alch-async-old-') as work:
            old=c.base.Plane(work,self.config);old.close()
            with self.assertRaises(c.Rejected) as caught:c.Plane(work,self.config)
            self.assertEqual(caught.exception.code,'NEW_ASYNC_ROOT_REQUIRED')


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(tempfile.mkdtemp(prefix='alch-async-http-'));cls.config=config()
        cls.config_path=cls.root/'operator.json';cls.config_path.write_text(json.dumps(cls.config))
        cls.addClassCleanup(cls.cleanup)
        cls.start()
        cls.source=(c.PREDECESSOR/'orders.alch').read_text()
        request=json.loads((c.HERE.parent/'event-execution-v1/place-order.request.json').read_text())['request']
        cls.body={k:request[k] for k in ('facts','expected_version')}
        for user in ('alice','bob'):
            assert cls.request(user,'POST','/v1/projects/shop',{})[0]==200
        status,accepted=cls.request('alice','POST','/v1/projects/shop/revisions',{'source':cls.source})
        assert status==202,(status,accepted)
        cls.alice=accepted['revision'];cls.await_ready('alice',cls.alice)
        status,value=cls.request('alice','POST',f'/v1/projects/shop/revisions/{cls.alice}/activate',{})
        assert status==200,(status,value)

    @classmethod
    def start(cls):
        cls.proc=subprocess.Popen([sys.executable,str(c.HERE/'control_plane.py'),'--root',str(cls.root),'--config',str(cls.config_path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        with selectors.DefaultSelector() as selector:
            selector.register(cls.proc.stdout,selectors.EVENT_READ)
            assert selector.select(30),'startup timeout'
            line=cls.proc.stdout.readline()
        if not line:raise AssertionError(cls.proc.stderr.read().decode())
        cls.port=int(json.loads(line)['url'].rsplit(':',1)[1])

    @classmethod
    def stop(cls):
        if getattr(cls,'proc',None):
            if cls.proc.poll() is None:
                cls.proc.terminate();cls.proc.wait(timeout=30)
            cls.proc.stdout.close();cls.proc.stderr.close()

    @classmethod
    def cleanup(cls):
        cls.stop()
        prefix='alch-provision-cp-'+c.sha(str(cls.root).encode())[:16]+'-'
        for p in Path('/tmp').glob(prefix+'*'):shutil.rmtree(p)
        shutil.rmtree(cls.root)

    @classmethod
    def request(cls,user,method,path,body=None):
        conn=http.client.HTTPConnection('127.0.0.1',cls.port,timeout=35)
        try:
            conn.request(method,path,None if body is None else json.dumps(body),{'Authorization':'Bearer '+(user+'_fixture_')*5,'Content-Type':'application/json'})
            response=conn.getresponse();return response.status,json.loads(response.read())
        finally:conn.close()

    @classmethod
    def await_ready(cls,user,revision):
        end=time.monotonic()+200
        while time.monotonic()<end:
            status,value=cls.request(user,'GET',f'/v1/projects/shop/revisions/{revision}')
            assert status==200,(status,value)
            if value['status']=='ready':return value
            if value['status']=='failed':
                log=cls.root/'revisions'/revision/'build.log'
                raise AssertionError((value,log.read_text() if log.exists() else 'no build log'))
            time.sleep(.2)
        raise AssertionError('build deadline exceeded')

    @classmethod
    def invoke(cls,user):
        for _ in range(60):
            status,value=cls.request(user,'POST','/v1/projects/shop/functions/orders-local/invoke',cls.body)
            if status!=503:return status,value
            time.sleep(.05)
        raise AssertionError('persistent busy')

    def test_01_other_tenant_build_does_not_block_invocation_or_status(self):
        status,value=self.invoke('alice');self.assertEqual(status,200,value)
        start=time.monotonic()
        status,accepted=self.request('bob','POST','/v1/projects/shop/revisions',{'source':self.source})
        self.assertEqual(status,202,accepted);self.assertLess(time.monotonic()-start,5)
        revision=accepted['revision']
        wait_for(lambda:self.request('bob','GET',accepted['status_url'])[1]['status']=='building')
        self.assertEqual(self.request('alice','GET',accepted['status_url'])[0],404)
        self.assertEqual(self.request('bob','POST',f'/v1/projects/shop/revisions/{revision}/activate',{})[0],409)
        status,value=self.invoke('alice');self.assertEqual(status,200,value)
        self.assertEqual(self.request('bob','GET',accepted['status_url'])[1]['status'],'building')
        self.await_ready('bob',revision)
        self.assertEqual(self.request('bob','POST',f'/v1/projects/shop/revisions/{revision}/activate',{})[0],200)
        status,value=self.invoke('bob');self.assertEqual(status,200,value)

    def test_02_invalid_source_fails_asynchronously_and_route_survives(self):
        status,accepted=self.request('alice','POST','/v1/projects/shop/revisions',{'source':'profile unsupported\n'})
        self.assertEqual(status,202)
        result=wait_for(lambda:(v if (v:=self.request('alice','GET',accepted['status_url'])[1])['status']=='failed' else None))
        self.assertEqual(result['error'],'BUILD_FAILED')
        self.assertEqual(self.invoke('alice')[0],200)

    def test_03_restart_resumes_queue_and_does_not_retry_interrupted_build(self):
        self.stop()
        plane=c.Plane(str(self.root),self.config)
        try:
            first=plane.build(self.config['users'][0],'shop','profile unsupported\n')['revision']
            second=plane.build(self.config['users'][1],'shop','profile unsupported\n')['revision']
            claimed=plane.claim()['id']
            queued=second if claimed==first else first
        finally:plane.close()
        self.start()
        who='alice' if claimed==first else 'bob'
        status,value=self.request(who,'GET',f'/v1/projects/shop/revisions/{claimed}')
        self.assertEqual(value['error'],'BUILD_INTERRUPTED')
        who='bob' if queued==second else 'alice'
        row=wait_for(lambda:(v if (v:=self.request(who,'GET',f'/v1/projects/shop/revisions/{queued}')[1])['status']=='failed' else None))
        self.assertEqual(row['error'],'BUILD_FAILED')
        self.assertEqual(self.invoke('alice')[0],200)


if __name__=='__main__':unittest.main(verbosity=2)
