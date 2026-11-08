import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch
from lifecycle import LifecycleMixin,LifecycleError,delivery_snapshot

class Core:
    def __init__(self,root,config):
        self.root=Path(root);self.stopping=threading.Event();self.children={}
        self.users={u['token_sha256']:u for u in config['users']}
        self.db=sqlite3.connect(self.root/'registry.sqlite');self.db.row_factory=sqlite3.Row
        self.db.executescript('CREATE TABLE routes(tenant,project,function,revision);CREATE TABLE journal(seq);')
        self.db.execute("INSERT INTO routes VALUES('alice','shop','orders-local','revision-a')");self.db.commit()
        self.epoch=1;self.effects=[];self.fail_control=None
    def scope(self,u,p,action):
        if action not in u['scopes'] or p not in u['projects']:raise LifecycleError('FORBIDDEN',403)
    def baseline(self,u,p,f):return {'revision':'revision-a','route_epoch':self.epoch,'state_key':'state'}
    def revision(self,u,p,r):return {'id':r}
    def host(self,row,user):self.effects.append('launch')
    def host_control(self,key,action):
        self.effects.append(action)
        if self.fail_control:raise LifecycleError(self.fail_control)
    def stop_host(self,key):self.effects.append('stop')
    def close(self):self.db.close()

class Plane(LifecycleMixin,Core):
    def probe(self,key):return {'state':'live','event_delivery':'idle'}

class Ledger(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.config={'schema':'alch.host-lifecycle/v1','users':[{'id':'alice','token_sha256':'a','projects':['shop'],'scopes':['read','lifecycle','invoke','activate']}]}
        self.p=Plane(self.temp.name,self.config);self.addCleanup(self.p.close);self.u=self.p.users['a']
    def token(self):return self.p.fence(self.p.baseline(self.u,'shop','orders-local'),self.p.mode('alice','shop','orders-local'))
    def submit(self,id='one',action='drain',token=None):return self.p.submit_control(self.u,'shop','orders-local',action,{'request_id':id,'expected':token or self.token()})
    def row(self):return self.p.db.execute('SELECT * FROM lifecycle_requests ORDER BY seq DESC LIMIT 1').fetchone()
    def test_duplicate_and_conflicting_id(self):
        token=self.token();first=self.submit(token=token)
        self.assertEqual(first,self.submit(token=token))
        with self.assertRaisesRegex(LifecycleError,'REQUEST_ID_CONFLICT'):self.submit(action='resume',token=token)
        self.assertEqual(self.p.db.execute('SELECT COUNT(*) FROM lifecycle_requests').fetchone()[0],1)
    def test_fences_and_active_request(self):
        with self.assertRaisesRegex(LifecycleError,'STALE_FENCE'):self.submit(token='0'*64)
        self.submit()
        with self.assertRaisesRegex(LifecycleError,'FUNCTION_CONTROL_BUSY'):self.submit(id='two')
    def test_route_aba_invalidates_token(self):
        old=self.token();self.p.epoch=3
        with self.assertRaisesRegex(LifecycleError,'STALE_FENCE'):self.submit(token=old)
    def test_explicit_permission_and_tenant(self):
        self.u['scopes'].remove('lifecycle')
        with self.assertRaisesRegex(LifecycleError,'FORBIDDEN'):self.submit()
        with self.assertRaisesRegex(LifecycleError,'NOT_FOUND'):self.p.request_status({**self.u,'id':'bob'},'shop','orders-local','one')
    def test_drain_and_resume_persist_intent(self):
        self.submit();self.assertEqual(self.p.mode('alice','shop','orders-local')['mode'],'draining')
        self.p.execute_control(self.row());self.assertEqual(self.row()['status'],'succeeded')
        self.submit('two','resume');self.p.execute_control(self.row())
        self.assertEqual(self.p.mode('alice','shop','orders-local')['mode'],'accepting')
    def test_failed_drain_stays_closed(self):
        self.submit();self.p.fail_control='DRAIN_BLOCKED';self.p.execute_control(self.row())
        self.assertEqual(self.row()['status'],'blocked')
        self.assertEqual(self.p.mode('alice','shop','orders-local')['mode'],'draining')
    def test_uncertain_effect_blocks_conflict(self):
        self.submit();self.p.fail_control='HOST_CONTROL_UNKNOWN';self.p.execute_control(self.row())
        self.assertEqual(self.row()['status'],'outcome_unknown')
        with self.assertRaisesRegex(LifecycleError,'FUNCTION_CONTROL_BUSY'):self.submit('two')
    def test_generation_fence(self):
        old=self.token()
        with self.p.db:self.p.db.execute("INSERT INTO lifecycle_modes VALUES('alice','shop','orders-local','accepting',0,'new')")
        with self.assertRaisesRegex(LifecycleError,'STALE_FENCE'):self.submit(token=old)
    def test_queue_capacity(self):
        self.submit()
        with self.p.db:
            self.p.db.execute("UPDATE lifecycle_requests SET function='another'")
            self.p.db.execute("INSERT INTO lifecycle_requests(tenant,project,function,id,status) VALUES('alice','shop','third','x','queued')")
        with self.assertRaisesRegex(LifecycleError,'LIFECYCLE_QUEUE_FULL'):self.submit('two')
    def test_crash_each_stage_reconciles_same_request(self):
        for index,stage in enumerate(['controlling','quiescent','stopped','launched','controlled','completed']):
            with self.subTest(stage=stage):
                self.submit(str(index),'restart')
                def crash(actual):
                    if actual==stage:raise SystemExit('simulated-process-exit')
                with patch.object(self.p,'failpoint',side_effect=crash):
                    with self.assertRaises(SystemExit):self.p.execute_control(self.row())
                # Startup reconciliation requeues unfinished requests; duplicates stay singular.
                self.p.restore_selected()
                row=self.row()
                if row['status']!='succeeded':self.p.execute_control(row)
                self.assertEqual(self.row()['status'],'succeeded')
                self.assertEqual(self.p.mode('alice','shop','orders-local')['mode'],'accepting')
    def test_changed_selection_rejects_queued_effect(self):
        self.submit();self.p.epoch=2;self.p.execute_control(self.row())
        self.assertEqual(self.row()['reason'],'STALE_FENCE');self.assertEqual(self.p.effects,[])
    def test_new_scope_is_not_implicit(self):
        bad={**self.config,'schema':'alch.local-control-plane/v1'}
        with self.assertRaisesRegex(LifecycleError,'LIFECYCLE_CONFIG_REQUIRED'):Plane(self.temp.name,bad)

class Summary(unittest.TestCase):
    def test_missing_is_unavailable_and_does_not_create(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'missing';s=delivery_snapshot(p)
            self.assertFalse(s['available']);self.assertIsNone(s['pending']);self.assertFalse(p.exists())
    def test_counts_and_unknown_status(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'db'
            with sqlite3.connect(p) as db:
                db.executescript("CREATE TABLE outbox(status);CREATE TABLE dead_letters(id);INSERT INTO outbox VALUES('pending'),('leased'),('published'),('dead');INSERT INTO dead_letters VALUES(1);")
            s=delivery_snapshot(p);self.assertEqual((s['pending'],s['leased'],s['published'],s['dead']),(2,1,1,1))
            with sqlite3.connect(p) as db:db.execute("INSERT INTO outbox VALUES('invented')")
            self.assertFalse(delivery_snapshot(p)['available'])
    def test_corrupt_storage(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'db';p.write_text('not sqlite')
            self.assertEqual(delivery_snapshot(p)['reason'],'STORAGE_UNAVAILABLE')

if __name__=='__main__':unittest.main(verbosity=2)
