"""Real queued builds and isolated Rust hosts, including durable lifecycle recovery."""
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import time
import unittest
import test_controller as prior
from client import Client

class Lifecycle(prior.Controller):
    @classmethod
    def sdk(cls,user='alice'):
        return Client('http://127.0.0.1:'+str(cls.port),(user+'_fixture_')*5)
    @classmethod
    def status(cls):
        from jsonschema import Draft202012Validator
        schema=json.loads((prior.c.HERE/'contracts.json').read_text())
        value=cls.sdk().status('shop','orders-local')
        Draft202012Validator({'$ref':'#/$defs/status','$defs':schema['$defs']}).validate(value)
        return value
    @classmethod
    def control(cls,action,request_id):
        client=cls.sdk();s=cls.status()
        receipt=client.control('shop','orders-local',action,s['expected'],request_id)
        value=client.wait_control('shop','orders-local',request_id)
        assert value['status']=='succeeded',value
        return value
    @classmethod
    def start_with_crash(cls,stage):
        # Failure injection exists only in this test process launcher.
        program="import sys,os;sys.path.insert(0,sys.argv.pop(1));import control_plane as c;stage=sys.argv.pop(1);c.Plane.failpoint=lambda self,s:os._exit(77) if s==stage else None;c.main()"
        cls.proc=subprocess.Popen([sys.executable,'-c',program,str(prior.c.HERE),stage,'--root',str(cls.root),'--config',str(cls.config_path)],
                                  stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        import selectors
        with selectors.DefaultSelector() as watcher:
            watcher.register(cls.proc.stdout,selectors.EVENT_READ);assert watcher.select(70),'startup timed out'
        line=cls.proc.stdout.readline();assert line,cls.proc.stderr.read().decode()
        cls.port=int(json.loads(line)['url'].rsplit(':',1)[1])

    def test_05_status_drain_resume_restart(self):
        before=self.status();self.assertEqual(before['health'],'ready')
        self.assertEqual(before['delivery']['published'],2)
        registry=self.root/'registry.sqlite'
        with sqlite3.connect(registry) as db:rows=db.execute('SELECT * FROM lifecycle_modes').fetchall()
        for _ in range(3):self.status()
        with sqlite3.connect(registry) as db:self.assertEqual(rows,db.execute('SELECT * FROM lifecycle_modes').fetchall())
        self.control('drain','drain-one');self.assertEqual(self.status()['health'],'drained')
        result=self.request('alice','POST','/v1/projects/shop/functions/orders-local/invoke',self.body)
        self.assertEqual(result[1]['error'],'FUNCTION_DRAINING')
        self.assertEqual(self.activate(self.new)[1]['error'],'FUNCTION_DRAINING')
        generation=self.status()['generation'];self.stop();self.start()
        self.assertEqual(self.status()['health'],'drained');self.assertNotEqual(self.status()['generation'],generation)
        self.control('restart','restart-drained');self.assertEqual(self.status()['health'],'drained')
        self.control('resume','resume-one');self.assertEqual(self.status()['health'],'ready')
        self.assertEqual(self.invoke(self.body)[1]['status'],'already-committed')
    def test_06_sdk_fencing_and_tenant(self):
        s=self.status();c=self.sdk();body={'expected':s['expected'],'request_id':'stable-id'}
        path='/v1/projects/shop/functions/orders-local/drain'
        first=self.request('alice','POST',path,body);self.assertEqual(first[0],202)
        duplicate=self.request('alice','POST',path,body);self.assertEqual(duplicate[1]['request_id'],'stable-id')
        c.wait_control('shop','orders-local','stable-id')
        self.assertEqual(self.request('alice','POST',path,{**body,'request_id':'stale'})[1]['error'],'STALE_FENCE')
        self.assertEqual(self.request('alice','POST',path,{**body,'expected':'0'*64})[1]['error'],'REQUEST_ID_CONFLICT')
        self.assertEqual(self.request('bob','GET','/v1/projects/shop/functions/orders-local/status')[0],404)
        self.assertEqual(self.request('bob','GET','/v1/projects/shop/functions/orders-local/requests/stable-id')[0],404)
        self.control('resume','resume-two')
    def test_07_dead_host_status_does_not_launch(self):
        # Direct process access is a test fixture capability, never returned by the API.
        children=set()
        for task in Path(f'/proc/{self.proc.pid}/task').iterdir():
            try:children.update((task/'children').read_text().split())
            except FileNotFoundError:pass
        hosts=[int(pid) for pid in children if b'function_host.py' in Path('/proc/'+pid+'/cmdline').read_bytes()]
        self.assertEqual(len(hosts),1)
        before=self.status();os.kill(hosts[0],signal.SIGKILL)
        until=time.monotonic()+5
        while self.status()['health'] not in ('failed','stopped') and time.monotonic()<until:time.sleep(.05)
        for _ in range(3):self.assertIn(self.status()['health'],('failed','stopped'))
        self.assertEqual(self.status()['generation'],before['generation'])
        self.control('restart','recover-dead');self.assertEqual(self.status()['health'],'ready')
        self.assertNotEqual(self.status()['generation'],before['generation'])
        self.assertEqual(self.invoke(self.body)[1]['status'],'already-committed')
    def test_08_dead_letters_block_drain_and_keep_status_responsive(self):
        # Add one terminal message in the owned test database, never in user state.
        with sqlite3.connect(self.database()) as db:
            db.execute("INSERT INTO outbox VALUES('fixture-dead','{}','{}',1,'dead',0,NULL,NULL)")
            db.execute("INSERT INTO dead_letters VALUES('orders-dead-letter','fixture-dead','{}','fixture')")
        try:
            c=self.sdk();s=self.status();self.assertEqual(s['delivery']['dead'],1)
            c.control('shop','orders-local','drain',s['expected'],'blocked-drain')
            before=time.monotonic();self.status();self.assertLess(time.monotonic()-before,2)
            result=c.wait_control('shop','orders-local','blocked-drain')
            self.assertEqual(result['status'],'blocked');self.assertEqual(result['reason'],'DRAIN_BLOCKED')
            self.assertEqual(self.status()['desired_mode'],'draining')
        finally:
            with sqlite3.connect(self.database()) as db:
                db.execute("DELETE FROM dead_letters WHERE id='fixture-dead'");db.execute("DELETE FROM outbox WHERE id='fixture-dead'")
        self.control('resume','after-block')
    def test_09_controller_crash_preserves_closed_gate(self):
        self.control('drain','before-crash');generation=self.status()['generation']
        self.proc.kill();self.proc.wait(timeout=10);self.proc.stdout.close();self.proc.stderr.close();type(self).proc=None
        # Parent-death signaling terminates the private host; let its owner lock settle.
        time.sleep(1);self.start()
        self.assertEqual(self.status()['desired_mode'],'draining')
        self.assertEqual(self.status()['health'],'drained');self.assertNotEqual(self.status()['generation'],generation)
        self.control('resume','after-crash');self.assertEqual(self.invoke(self.body)[1]['status'],'already-committed')
    def test_10_cli_status(self):
        result=subprocess.run([sys.executable,str(prior.c.HERE/'client.py'),'--url','http://127.0.0.1:'+str(self.port),'status','shop','orders-local'],
                              env={**os.environ,'ALCH_SERVICE_TOKEN':('alice_fixture_')*5},capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['health'],'ready')

    def test_11_drain_timeout_keeps_status_responsive_and_gate_closed(self):
        with sqlite3.connect(self.database()) as db:
            db.execute("INSERT INTO outbox VALUES('fixture-wait','{}','{}',1,'leased',0,'fixture',?)",(int(time.time()*1000)+120000,))
        try:
            c=self.sdk();s=self.status()
            c.control('shop','orders-local','drain',s['expected'],'timeout-drain')
            time.sleep(.2)
            before=time.monotonic();current=self.status();self.assertLess(time.monotonic()-before,2)
            self.assertEqual(current['delivery']['pending'],1)
            self.assertEqual(self.activate(self.new)[1]['error'],'FUNCTION_CONTROL_BUSY')
            result=c.wait_control('shop','orders-local','timeout-drain',50)
            self.assertEqual(result['status'],'blocked');self.assertEqual(result['reason'],'DRAIN_TIMEOUT')
            self.assertEqual(self.status()['desired_mode'],'draining')
        finally:
            with sqlite3.connect(self.database()) as db:db.execute("DELETE FROM outbox WHERE id='fixture-wait'")
        self.control('resume','after-timeout')

    def test_12_real_controller_crashes_at_each_control_stage(self):
        for index,stage in enumerate(['controlling','quiescent','stopped','launched','controlled','completed']):
            with self.subTest(stage=stage):
                self.stop();self.start_with_crash(stage)
                c=self.sdk();s=self.status();request_id='crash-stage-'+str(index)
                c.control('shop','orders-local','restart',s['expected'],request_id)
                self.proc.wait(timeout=60);self.assertEqual(self.proc.returncode,77)
                self.proc.stdout.close();self.proc.stderr.close();type(self).proc=None
                time.sleep(1);self.start()
                result=self.sdk().wait_control('shop','orders-local',request_id,90)
                self.assertEqual(result['status'],'succeeded',result)
                self.assertEqual(self.status()['desired_mode'],'accepting')
                self.assertEqual(self.invoke(self.body)[1]['status'],'already-committed')
                with sqlite3.connect(self.root/'registry.sqlite') as db:
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM lifecycle_requests WHERE id=?',(request_id,)).fetchone()[0],1)

    def test_13_inflight_invocation_finishes_before_drain(self):
        import socket,http.client
        self.stop();plane=prior.c.Plane(self.root,self.config)
        sock=None
        try:
            plane.restore_selected();user=next(u for u in plane.users.values() if u['id']=='alice')
            state=plane.state('alice','shop','orders-local');key=state['state_key']
            _,port,token=plane.children[key]
            body={**self.body,'facts':{'orderId':'inflight-order','payload':{}},'message_id':'inflight-message'}
            raw=json.dumps(body).encode();sock=socket.create_connection(('127.0.0.1',port),timeout=10)
            headers=('POST /functions/orders-local/place-order HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer '+token+'\r\nContent-Type: application/json\r\nContent-Length: '+str(len(raw))+'\r\n\r\n').encode()
            sock.sendall(headers+raw[:-1])
            deadline=time.monotonic()+2
            while not plane.probe(key).get('active') and time.monotonic()<deadline:time.sleep(.01)
            self.assertTrue(plane.probe(key).get('active'))
            status=plane.function_status(user,'shop','orders-local')
            plane.submit_control(user,'shop','orders-local','drain',{'expected':status['expected'],'request_id':'inflight-drain'})
            plane.start_lifecycle_worker()
            deadline=time.monotonic()+2
            while plane.probe(key).get('gate')!='draining' and time.monotonic()<deadline:time.sleep(.01)
            self.assertEqual(plane.probe(key).get('gate'),'draining')
            sock.sendall(raw[-1:]);response=http.client.HTTPResponse(sock);response.begin()
            self.assertEqual(response.status,200);self.assertEqual(json.loads(response.read())['status'],'committed')
            deadline=time.monotonic()+15
            while plane.request_status(user,'shop','orders-local','inflight-drain')['status'] in ('queued','running') and time.monotonic()<deadline:time.sleep(.05)
            self.assertEqual(plane.request_status(user,'shop','orders-local','inflight-drain')['status'],'succeeded')
            self.assertEqual(plane.function_status(user,'shop','orders-local')['health'],'drained')
        finally:
            if sock:sock.close()
            plane.close();self.start()
        self.control('resume','after-inflight')

    def test_14_crash_after_consume_preserves_dedup_and_lease(self):
        from unittest.mock import patch
        self.stop();plane=prior.c.Plane(self.root,self.config)
        try:
            user=next(u for u in plane.users.values() if u['id']=='alice')
            real_popen=subprocess.Popen
            def launch(args,*a,**kw):
                if '--host-launch' in args:args=[*args,'--test-crash-after-consume']
                return real_popen(args,*a,**kw)
            with patch.object(subprocess,'Popen',side_effect=launch):plane.restore_selected()
            body={**self.body,'facts':{'orderId':'delivery-crash','payload':{}},'message_id':'delivery-crash'}
            # Delivery may occupy the single invocation slot briefly.
            for _ in range(100):
                response=plane.invoke(user,'shop','orders-local',body)
                if response[0]!=503:break
                time.sleep(.05)
            self.assertEqual(response[1]['status'],'committed')
            key=plane.state('alice','shop','orders-local')['state_key'];proc=plane.children[key][0]
            proc.wait(timeout=15);self.assertEqual(proc.returncode,75)
            with sqlite3.connect(plane.database(key)) as db:
                self.assertEqual(db.execute("SELECT status FROM outbox WHERE id='delivery-crash'").fetchone()[0],'leased')
                before=db.execute("SELECT COUNT(*) FROM inbox WHERE id='delivery-crash'").fetchone()[0];self.assertEqual(before,1)
            status=plane.function_status(user,'shop','orders-local')
            plane.submit_control(user,'shop','orders-local','restart',{'expected':status['expected'],'request_id':'delivery-recovery'})
            plane.start_lifecycle_worker();deadline=time.monotonic()+50
            while time.monotonic()<deadline:
                with sqlite3.connect(plane.database(key)) as db:
                    if db.execute("SELECT status FROM outbox WHERE id='delivery-crash'").fetchone()[0]=='published':break
                time.sleep(.1)
            with sqlite3.connect(plane.database(key)) as db:
                self.assertEqual(db.execute("SELECT status FROM outbox WHERE id='delivery-crash'").fetchone()[0],'published')
                self.assertEqual(db.execute("SELECT COUNT(*) FROM inbox WHERE id='delivery-crash'").fetchone()[0],before)
            self.assertEqual(plane.request_status(user,'shop','orders-local','delivery-recovery')['status'],'succeeded')
        finally:plane.close();self.start()

if __name__=='__main__':unittest.main(verbosity=2)
