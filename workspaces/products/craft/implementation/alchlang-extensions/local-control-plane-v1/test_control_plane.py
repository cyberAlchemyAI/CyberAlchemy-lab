"""Real HTTP, compiler sandbox, RWO/Ansible and Rust tests; local fixtures only."""
import copy
import http.client
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import control_plane as c


class ControlPlaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(tempfile.mkdtemp(prefix='alch-control-test-'))
        cls.config=json.loads((c.HERE/'operator.example.json').read_text())
        cls.tokens={'alice':'alice_fixture_'*4,'bob':'bob_fixture_'*4,'limited':'limited_fixture_'*4}
        for u in cls.config['users']: u['token_sha256']=c.sha(cls.tokens[u['id']].encode())
        limited=copy.deepcopy(cls.config['users'][0])
        limited.update(id='limited',token_sha256=c.sha(cls.tokens['limited'].encode()),scopes=['invoke'],projects=['allowed'])
        cls.config['users'].append(limited)
        cls.config_path=cls.root/'operator.json'; cls.config_path.write_text(json.dumps(cls.config))
        cls.addClassCleanup(cls.cleanup)
        cls.start()
        cls.source=(c.HERE/'orders.alch').read_text()
        cls.body=json.loads((c.HERE.parent/'event-execution-v1/place-order.request.json').read_text())['request']
        cls.body={k:cls.body[k] for k in ('facts','expected_version')}
        cls.revisions={}
        for name in ('alice','bob'):
            status,_=cls.request(name,'POST','/v1/projects/shop',{})
            assert status==200
            status,value=cls.request(name,'POST','/v1/projects/shop/revisions',{'source':cls.source})
            if status!=201:
                logs='\n'.join(p.read_text() for p in (cls.root/'revisions').glob('*/build.log'))
                raise AssertionError((status,value,logs))
            cls.revisions[name]=value['revision']
            status,value=cls.request(name,'POST',f"/v1/projects/shop/revisions/{cls.revisions[name]}/activate",{})
            assert status==200,(status,value)

    @classmethod
    def start(cls):
        cls.proc=subprocess.Popen([sys.executable,str(c.HERE/'control_plane.py'),'--root',str(cls.root),'--config',str(cls.config_path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        with selectors.DefaultSelector() as selector:
            selector.register(cls.proc.stdout,selectors.EVENT_READ)
            assert selector.select(30),'startup timeout'
            line=cls.proc.stdout.readline()
        if not line: raise AssertionError(cls.proc.stderr.read().decode())
        cls.port=int(json.loads(line)['url'].rsplit(':',1)[1])

    @classmethod
    def stop(cls):
        if getattr(cls,'proc',None) and cls.proc.poll() is None:
            cls.proc.terminate()
            try: cls.proc.wait(timeout=30)
            except subprocess.TimeoutExpired: cls.proc.kill();cls.proc.wait();raise
        if getattr(cls,'proc',None):
            cls.proc.stdout.close();cls.proc.stderr.close()

    @classmethod
    def cleanup(cls):
        cls.stop()
        prefix='alch-provision-cp-'+c.sha(str(cls.root).encode())[:16]+'-'
        for p in Path('/tmp').glob(prefix+'*'): shutil.rmtree(p)
        shutil.rmtree(cls.root)

    @classmethod
    def request(cls,user,method,path,body=None,headers=None):
        connection=http.client.HTTPConnection('127.0.0.1',cls.port,timeout=240)
        try:
            connection.request(method,path,None if body is None else json.dumps(body),headers or {'Authorization':'Bearer '+cls.tokens.get(user,user),'Content-Type':'application/json'})
            response=connection.getresponse()
            return response.status,json.loads(response.read())
        finally: connection.close()

    @classmethod
    def invoke(cls,user,body=None):
        for _ in range(60):
            status,value=cls.request(user,'POST','/v1/projects/shop/functions/orders-local/invoke',body or cls.body)
            if status!=503:return status,value
            time.sleep(.05)
        raise AssertionError('persistent busy')

    @classmethod
    def snapshot(cls,user):
        root='/tmp/alch-provision-cp-'+c.sha(str(cls.root).encode())[:16]+'-'+cls.revisions[user]
        with sqlite3.connect(Path(root)/'target/state/runtime/function.sqlite') as db:
            return {'outbox':db.execute('SELECT status FROM outbox').fetchall(),'inbox':db.execute('SELECT operation,id FROM inbox').fetchall(),'state':db.execute('SELECT operation,version FROM state').fetchall()}

    def test_01_two_tenants_invoke_and_deliver_same_message_identity(self):
        for user in ('alice','bob'):
            status,value=self.invoke(user)
            self.assertEqual(status,200,value)
        for user in ('alice','bob'):
            for _ in range(300):
                state=self.snapshot(user)
                if state['outbox']==[('published',)]:break
                time.sleep(.1)
            self.assertEqual(state['outbox'],[('published',)])
            self.assertEqual(state['inbox'],[('record-order','m1')])
            self.assertEqual(sorted(state['state']),[('place-order',1),('record-order',1)])

    def test_02_cross_tenant_inspection_and_activation_denied(self):
        status,value=self.request('bob','GET','/v1/projects/shop')
        self.assertEqual(status,200)
        self.assertNotIn(self.revisions['alice'],json.dumps(value))
        status,value=self.request('bob','POST',f"/v1/projects/shop/revisions/{self.revisions['alice']}/activate",{})
        self.assertEqual(status,404)
        self.assertEqual(self.request('alice','POST','/v1/projects/private',{})[0],200)
        self.assertEqual(self.request('bob','GET','/v1/projects/private')[0],404)
        self.assertEqual(self.request('bob','POST','/v1/projects/private/functions/orders-local/invoke',self.body)[0],404)

    def test_03_scope_auth_and_request_boundaries(self):
        self.assertEqual(self.request('invalid','GET','/v1/projects/shop')[0],401)
        self.assertEqual(self.request('limited','GET','/v1/projects/shop')[0],403)
        self.assertEqual(self.request('limited','POST','/v1/projects/allowed',{})[0],403)
        self.assertEqual(self.request('limited','POST','/v1/projects/shop/functions/orders-local/invoke',self.body)[0],403)
        self.assertEqual(self.request('alice','POST','/v1/projects/shop/functions/orders-local/invoke',{**self.body,'context':{'actor':'admin'}})[0],400)
        self.assertEqual(self.request('alice','GET','/v1/projects/../shop')[0],404)
        self.assertEqual(self.request('alice','POST','/v1/projects/shop/revisions',{'source':'x'*262145})[0],413)
        self.assertEqual(self.request('alice','GET','/v1/projects/shop',headers={'Authorization':'Bearer '+self.tokens['alice'],'Origin':'http://example.invalid'})[0],401)

    def test_04_failed_build_is_recorded_and_keeps_route(self):
        status,value=self.request('alice','POST','/v1/projects/shop/revisions',{'source':'profile unsupported\n'})
        self.assertEqual(status,422,value)
        status,value=self.request('alice','GET','/v1/projects/shop')
        self.assertEqual(value['routes'],[{'function':'orders-local','revision':self.revisions['alice']}])
        failed=[r for r in value['revisions'] if r['status']=='failed']
        self.assertTrue(failed)
        self.assertEqual(self.request('alice','POST',f"/v1/projects/shop/revisions/{failed[0]['id']}/activate",{})[0],409)

    def test_05_artifact_tamper_stops_invocation(self):
        target=self.root/'revisions'/self.revisions['alice']/'bundle/host.json'
        before=target.read_bytes()
        try:
            target.write_bytes(before+b' ')
            self.assertEqual(self.invoke('alice')[0],409)
        finally:target.write_bytes(before)

    def test_06_build_sandbox_hides_tenants_and_environment(self):
        with tempfile.TemporaryDirectory(prefix='alch-build-probe-') as work:
            command=c.build_command(Path(work)); separator=command.index('--')
            script="import os,socket,json; s=socket.socket(); s.settimeout(.2); print(json.dumps({'tenant':os.path.exists("+repr(str(self.root))+"),'secret':os.getenv('CONTROL_SECRET'),'network':s.connect_ex(('198.51.100.1',80)),'job':os.access('/job',os.W_OK)}))"
            result=subprocess.run(command[:separator+1]+['/usr/bin/python3','-c',script],env={'CONTROL_SECRET':'hidden'},capture_output=True,text=True,check=True)
            value=json.loads(result.stdout)
            self.assertFalse(value['tenant']);self.assertIsNone(value['secret']);self.assertNotEqual(value['network'],0);self.assertTrue(value['job'])

    def test_07_single_owner_lock(self):
        with self.assertRaises(c.Rejected) as caught:c.Plane(str(self.root),self.config)
        self.assertEqual(caught.exception.code,'CONTROL_PLANE_BUSY')

    def test_08_policy_cannot_be_granted_by_source(self):
        cfg=json.loads((self.root/'revisions'/self.revisions['alice']/'bundle/host.json').read_bytes())
        bad=copy.deepcopy(self.config['users'][0]['policy']);bad['grants']=[]
        with self.assertRaises(c.Rejected):c.policy_check(cfg,bad)
        bad=copy.deepcopy(cfg);bad['isolation']='trusted-process'
        with self.assertRaises(c.Rejected):c.policy_check(bad,self.config['users'][0]['policy'])

    def test_09_restart_preserves_routes_and_deduplication(self):
        self.stop();self.start()
        for user in ('alice','bob'):
            status,value=self.invoke(user)
            self.assertEqual(status,200,value)
            self.assertEqual(self.snapshot(user)['inbox'],[('record-order','m1')])
            self.assertEqual(sorted(self.snapshot(user)['state']),[('place-order',1),('record-order',1)])

    def test_10_interrupted_build_reconciles_without_route(self):
        self.stop()
        with sqlite3.connect(self.root/'registry.sqlite') as db:
            db.execute('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?)',('alice','shop','f'*32,'0'*64,'building',None,None,None))
        self.start()
        _,value=self.request('alice','GET','/v1/projects/shop')
        failed=next(r for r in value['revisions'] if r['id']=='f'*32)
        self.assertEqual(failed['status'],'failed');self.assertEqual(failed['error'],'BUILD_INTERRUPTED')
        self.assertEqual(value['routes'],[{'function':'orders-local','revision':self.revisions['alice']}])

    def test_11_revision_switch_and_rollback_preserve_separate_state(self):
        old=self.revisions['alice']
        status,value=self.request('alice','POST','/v1/projects/shop/revisions',{'source':self.source+'\n# revision two\n'})
        self.assertEqual(status,201,value)
        new=value['revision'];self.assertNotEqual(old,new)
        self.assertEqual(self.request('alice','POST',f'/v1/projects/shop/revisions/{new}/activate',{})[0],200)
        status,value=self.invoke('alice');self.assertEqual(status,200,value)
        self.assertEqual(self.request('alice','POST',f'/v1/projects/shop/revisions/{old}/activate',{})[0],200)
        status,value=self.invoke('alice');self.assertEqual(status,200,value)
        self.assertEqual(sorted(self.snapshot('alice')['state']),[('place-order',1),('record-order',1)])
        _,other=self.request('bob','GET','/v1/projects/shop')
        self.assertNotIn(new,json.dumps(other))

    def test_12_failed_readiness_does_not_change_route(self):
        self.stop()
        plane=c.Plane(str(self.root),self.config)
        try:
            user=self.config['users'][0]
            before=plane.inspect(user,'shop')['routes']
            with patch.object(plane,'host',side_effect=c.Rejected('HOST_START_FAILED',503)):
                with self.assertRaises(c.Rejected):plane.activate(user,'shop',self.revisions['alice'])
            self.assertEqual(plane.inspect(user,'shop')['routes'],before)
        finally:plane.close();self.start()

    def test_13_compiler_drift_and_unavailable_build_sandbox_fail_closed(self):
        self.stop()
        plane=c.Plane(str(self.root),self.config)
        try:
            user=self.config['users'][0]
            before=plane.inspect(user,'shop')['routes']
            with patch.object(c,'compiler_binding',return_value={}):
                with self.assertRaises(c.Rejected) as caught:plane.build(user,'shop',self.source)
                self.assertEqual(caught.exception.code,'COMPILER_DRIFT')
            with patch.object(c,'build_command',return_value=['/nonexistent-alch-sandbox']):
                with self.assertRaises(c.Rejected) as caught:plane.build(user,'shop',self.source)
                self.assertEqual(caught.exception.code,'BUILD_FAILED')
            self.assertEqual(plane.inspect(user,'shop')['routes'],before)
        finally:plane.close();self.start()


if __name__=='__main__':unittest.main(verbosity=2)
