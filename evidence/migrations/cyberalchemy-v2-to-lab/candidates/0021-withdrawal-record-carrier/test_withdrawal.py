import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from jsonschema import ValidationError
from check import assess
from support import ROOT, PACKAGE, load, dump, binding
class Withdrawal(unittest.TestCase):
    def setUp(self):
        self.path=PACKAGE/'fixtures/valid/withdrawal-record.json'; self.record=load(self.path); self.query=load(ROOT/'examples/clear.json')
    def result(self): return assess(self.path,self.query)
    def changed_record(self,edit,error):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'record.json'; edit(self.record); dump(path,self.record); self.query['withdrawal_record']=binding(path)
            with self.assertRaises((ValueError,ValidationError)) as caught: assess(path,self.query)
            self.assertIn(error,str(caught.exception))
    def test_clear(self):
        result=self.result(); self.assertEqual(result['reserved_count'],12); self.assertEqual(result['outcome'],'no-listed-collision')
        for key in ['allocation_authorized','new_withdrawal_performed','successor_authority_verified']: self.assertFalse(result[key])
    def test_retired(self):
        self.query['proposed_ids']=['CAV2-D70']; self.assertEqual(self.result()['collisions'],[{'retired_id':'CAV2-D70','successor_id':'KEP-D1'}])
    def test_all_retired(self):
        self.query['proposed_ids']=[x['retired_id'] for x in self.record['reservations']]; self.assertEqual(len(self.result()['collisions']),12)
    def test_successor_not_authorized(self):
        self.query['proposed_ids']=['KEP-D1']; self.assertFalse(self.result()['allocation_authorized'])
    def test_scope(self):
        self.query['scope_ref']='other'; self.assertEqual(self.result()['outcome'],'not-applicable')
    def test_missing_reservation(self): self.changed_record(lambda x:x['reservations'].pop(),'differ from accepted')
    def test_wrong_successor(self): self.changed_record(lambda x:x['reservations'][0].update(successor_id='other'),'differ from accepted')
    def test_duplicate_reservation(self): self.changed_record(lambda x:x['reservations'].append(copy.deepcopy(x['reservations'][0])),'Duplicate retired')
    def test_not_permanent(self): self.changed_record(lambda x:x['reservations'][0].update(permanently_reserved=False),'True was expected')
    def test_record_drift(self):
        self.query['withdrawal_record']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Bound bytes changed'): self.result()
    def test_normalization_drift(self): self.changed_record(lambda x:x['normalization'].update(sha256='0'*64),'Bound bytes changed')
    def test_padded_identifier(self):
        self.query['proposed_ids']=[' CAV2-D70 ']
        with self.assertRaisesRegex(ValueError,'whitespace'): self.result()
    def test_empty_allocation(self):
        self.query['proposed_ids']=[]; self.assertEqual(self.result()['outcome'],'no-listed-collision')
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'query.json'
            for expected in [0,1,2]:
                if expected==1: self.query['proposed_ids']=['CAV2-D70']
                if expected==2: self.query['authorized']=True
                dump(path,self.query); result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(self.path),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
