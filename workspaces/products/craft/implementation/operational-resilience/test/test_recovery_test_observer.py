import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
OBSERVER = HERE.parent / 'src/recovery_test_observer.py'
DRIVER = HERE.parent / 'src/recovery_observed_case.py'
ROOT = HERE.parents[4]
R07 = ROOT / 'projects/domainspec-v2/development/completion-dag/v1/evidence/r07-recovery-v1'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / 'coordination.sqlite'
        with sqlite3.connect(self.db) as db:
            db.executescript('PRAGMA user_version=1; CREATE TABLE facts(id TEXT PRIMARY KEY, value INTEGER); INSERT INTO facts VALUES ("b",2),("a",1);')
        self.request = {'schema_version':'domainspec.orodi.recovery-observer/v1-candidate','scenario_id':'R01-F01','repetition':1,'test_id':'observer-test','subject_digest':'a'*64,'producer_pid':os.getpid(),'barrier_id':'before-test','sequence':1,'clock':{'kind':'injected','boot_id':'test-boot','monotonic_value':0},'fixture_root':str(self.root),'stores':[{'role':'coordination','path':str(self.db)}]}
    def invoke(self, request=None):
        result = subprocess.run([sys.executable,'-B',str(OBSERVER)],input=json.dumps(request or self.request),capture_output=True,text=True,timeout=5)
        return result.returncode, json.loads(result.stdout)
    def test_readonly_sorted_snapshot_and_closed_connection(self):
        before = {p.name:sha(p) for p in self.root.iterdir()}
        code, result = self.invoke()
        self.assertEqual(code,0)
        self.assertEqual(result['stores'][0]['state'],'observed',result)
        self.assertEqual(result['stores'][0]['tables']['facts']['rows'],[['a',1],['b',2]])
        self.assertEqual(before,{p.name:sha(p) for p in self.root.iterdir()})
        self.assertTrue(result['all_connections_closed'])
        self.assertNotEqual(result['observer_pid'],os.getpid())
        self.assertEqual(result['observer_digest'],sha(OBSERVER))
        # A writer can take EXCLUSIVE ownership after the observer returns.
        with sqlite3.connect(self.db,timeout=0) as db:
            db.execute('BEGIN EXCLUSIVE');db.execute('UPDATE facts SET value=3');db.commit()
    def test_missing_file_not_created(self):
        self.db.unlink()
        code,result=self.invoke();self.assertEqual(code,0)
        self.assertEqual(result['stores'][0]['state'],'unavailable');self.assertFalse(self.db.exists())
    def test_wal_rejected_without_new_files(self):
        db=sqlite3.connect(self.db)
        self.addCleanup(db.close)
        db.execute('PRAGMA journal_mode=WAL');db.execute('UPDATE facts SET value=4');db.commit()
        before={p.name:sha(p) for p in self.root.iterdir()}
        code,result=self.invoke();self.assertEqual(code,0)
        self.assertIn('WAL',result['stores'][0]['cause'])
        self.assertEqual(before,{p.name:sha(p) for p in self.root.iterdir()})
    def test_outside_root_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            target=Path(other)/'other.sqlite';target.write_bytes(self.db.read_bytes())
            link=self.root/'link.sqlite';link.symlink_to(target)
            self.request['stores'][0]['path']=str(link)
            code,result=self.invoke();self.assertEqual(code,2);self.assertIn('outside',result['cause'])
    def test_unknown_request_fields_and_parent_spoof_rejected(self):
        self.request['invoke']='forbidden';self.assertEqual(self.invoke()[0],2)
        del self.request['invoke'];self.request['producer_pid']+=100000;self.assertEqual(self.invoke()[0],2)
    def test_lock_failure_bounded_and_preserved(self):
        db=sqlite3.connect(self.db);self.addCleanup(db.close);db.execute('BEGIN EXCLUSIVE')
        code,result=self.invoke();self.assertEqual(code,0);self.assertEqual(result['stores'][0]['state'],'unavailable')
        self.assertIn('locked',result['stores'][0]['cause'])
    def test_query_authorizer_denies_writes(self):
        spec=importlib.util.spec_from_file_location('observer_test_module',OBSERVER)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with sqlite3.connect(self.db) as db:
            db.set_authorizer(module.authorizer)
            for sql in ['DELETE FROM facts','PRAGMA user_version=2','ATTACH DATABASE ":memory:" AS extra']:
                with self.assertRaises(sqlite3.DatabaseError):db.execute(sql)
    def test_two_stores_are_separate(self):
        other=self.root/'operation.sqlite';other.write_bytes(self.db.read_bytes())
        self.request['stores'].append({'role':'operation','path':str(other)})
        code,result=self.invoke();self.assertEqual(code,0);self.assertEqual(len(result['stores']),2);self.assertFalse(result['cross_store_atomic'])
    def test_bounded_row_count(self):
        with sqlite3.connect(self.db) as db:
            db.executemany('INSERT INTO facts VALUES (?,0)',[(str(i),) for i in range(10001)])
        code,result=self.invoke();self.assertEqual(code,0);self.assertIn('budget',result['stores'][0]['cause'])

class DriverTests(unittest.TestCase):
    def test_real_runtime_and_formation_smoke(self):
        manifest=sha(R07/'PRODUCT-TEST-MANIFEST.json')
        for scenario in ['R01-F01','R01-F26']:
            child=subprocess.run([sys.executable,'-B',str(DRIVER),'--scenario',scenario,'--repetition','1','--manifest-sha256',manifest,'--observer-sha256',sha(OBSERVER)],capture_output=True,text=True,timeout=40)
            self.assertEqual(child.returncode,0,child.stdout+child.stderr)
            result=json.loads(child.stdout);self.assertEqual(result['result'],'PASS')
            observations=result['observation']
            captures=[t[p] for t in observations['tests'] for p in ['before','after']]+observations['formation_observations']
            self.assertTrue(captures)
            for capture in captures:
                self.assertEqual(capture['producer_pid'],observations['pid'])
                self.assertNotEqual(capture['observer_pid'],observations['pid'])
                self.assertTrue(capture['all_connections_closed'])
                for store in capture['stores']:self.assertEqual(store['state'],'observed',store)
    def test_drift_stops_before_test(self):
        child=subprocess.run([sys.executable,'-B',str(DRIVER),'--scenario','R01-F01','--repetition','1','--manifest-sha256','0'*64,'--observer-sha256',sha(OBSERVER)],capture_output=True,text=True,timeout=5)
        self.assertEqual(child.returncode,2);self.assertIn('pinned',json.loads(child.stdout)['cause'])

if __name__=='__main__': unittest.main()
