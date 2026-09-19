import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from check import assess, read_input
from support import ROOT, LAB, PACKAGE, load, dump, binding

class Pattern(unittest.TestCase):
    def setUp(self): self.record=load(PACKAGE/'fixtures/valid/architecture-pattern-record.json')
    def changed(self,edit):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'after.json'; data=load(LAB/self.record['witness']['after']['path']); edit(data); dump(path,data)
            self.record['witness']['after']=binding(path); return assess(self.record)
    def test_append(self):
        result=assess(self.record); self.assertTrue(result['conforms']); self.assertEqual(result['appended_events'],1)
        self.assertFalse(result['runtime_enforcement_proven']); self.assertFalse(result['promotion_authorized'])
    def test_noop(self):
        self.record['witness']['after']=self.record['witness']['before']; self.assertTrue(assess(self.record)['conforms'])
    def test_rewrite(self):
        result=self.changed(lambda x:x['events'][0]['payload'].update(action='erased')); self.assertIn('history-rewritten',result['snapshot_errors'])
    def test_truncate(self):
        result=self.changed(lambda x:x.update(events=[])); self.assertIn('history-truncated',result['snapshot_errors'])
    def test_duplicate(self):
        result=self.changed(lambda x:x['events'][1].update(event_id='event-1')); self.assertIn('after:duplicate-event',result['snapshot_errors'])
    def test_sequence(self):
        result=self.changed(lambda x:x['events'][1].update(sequence=4)); self.assertIn('after:sequence-gap-or-order',result['snapshot_errors'])
    def test_float_sequence(self):
        result=self.changed(lambda x:x['events'][1].update(sequence=2.0)); self.assertFalse(result['conforms'])
    def test_scope(self):
        result=self.changed(lambda x:x.update(scope_ref='other')); self.assertFalse(result['conforms'])
    def test_missing_context(self):
        self.record['witness']['context']={}; result=assess(self.record); self.assertEqual(result['applicability'],'indeterminate'); self.assertIsNone(result['conforms'])
    def test_context_conflict(self):
        self.record['witness']['context']['history_policy']='overwrite'; result=assess(self.record); self.assertEqual(result['applicability'],'not-applicable'); self.assertIsNone(result['conforms'])
    def test_unknown_force(self):
        self.record['consequences'][0]['force_refs']=['unknown']
        with self.assertRaisesRegex(ValueError,'Unknown force'): assess(self.record)
    def test_uncovered_force(self):
        self.record['forces'].append({'force_id':'other','description':'Unaddressed'})
        with self.assertRaisesRegex(ValueError,'lacks consequence'): assess(self.record)
    def test_digest_drift(self):
        self.record['witness']['before']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Bound bytes changed'): assess(self.record)
    def test_json_type_distinction(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            before=load(LAB/self.record['witness']['before']['path']); before['events'][0]['payload']={'value':True}
            after=copy.deepcopy(before); after['events'][0]['payload']['value']=1
            for name,data in [('before',before),('after',after)]:
                path=Path(d)/(name+'.json'); dump(path,data); self.record['witness'][name]=binding(path)
            self.assertFalse(assess(self.record)['conforms'])
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input.json'; path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): read_input(path)
    def test_cli_states(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'record.json'
            for expected in [0,1,2]:
                if expected==1: self.record['witness']['context']={}
                if expected==2: self.record['authority_effect']='promote'
                dump(path,self.record)
                result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
