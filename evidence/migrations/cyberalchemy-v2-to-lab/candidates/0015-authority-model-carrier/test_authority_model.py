import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from check import assess, read_input
from support import ROOT, PACKAGE, load, dump
class AuthorityModel(unittest.TestCase):
    def setUp(self):
        self.record=load(PACKAGE/'fixtures/valid/authority-model-record.json'); self.claim=load(ROOT/'examples/ready.json')
    def result(self): return assess(self.record,self.claim)
    def test_route(self):
        result=self.result(); self.assertEqual(result['outcome'],'requires-owner-gate'); self.assertEqual(result['owner_route'],'route:definition-owner')
        for key in ['claim_authenticated','gate_verdict_present','action_authorized']: self.assertFalse(result[key])
    def test_unknown_kind(self):
        self.claim['kind_ref']='unknown'; result=self.result(); self.assertEqual(result['reason'],'unknown-kind'); self.assertEqual(result['owner_route'],self.record['amendment_route'])
    def test_unknown_posture(self):
        self.claim['posture_ref']='admitted'; self.assertEqual(self.result()['reason'],'unknown-posture')
    def test_unknown_operation(self):
        self.claim['operation_ref']='execute'; self.assertEqual(self.result()['reason'],'unknown-operation')
    def test_effect_mismatch(self):
        self.claim['intended_effect']='admit'; self.assertEqual(self.result()['reason'],'operation-effect-mismatch')
    def test_blocked(self):
        self.claim.update(operation_ref='request-admission',intended_effect='admit'); self.assertEqual(self.result()['reason'],'effect-blocked')
    def test_scope(self):
        self.claim['scope_ref']='other'; self.assertEqual(self.result()['outcome'],'not-applicable')
    def test_model(self):
        self.claim['model_ref']='other'; self.assertEqual(self.result()['outcome'],'not-applicable')
    def test_rule_conflict(self):
        rule=copy.deepcopy(self.record['rules'][0]); rule['rule_id']='conflict'; self.record['rules'].append(rule)
        with self.assertRaisesRegex(ValueError,'Conflicting'): self.result()
    def test_effect_overlap(self):
        self.record['rules'][0]['allowed_effects'].append('admit')
        with self.assertRaisesRegex(ValueError,'partition'): self.result()
    def test_effect_omission(self):
        self.record['rules'][0]['blocked_effects']=[]
        with self.assertRaisesRegex(ValueError,'partition'): self.result()
    def test_kind_without_owner(self):
        self.record['authority_kinds'].append('orphan')
        with self.assertRaisesRegex(ValueError,'lacks an owner'): self.result()
    def test_duplicate_operation(self):
        self.record['operations'].append(copy.deepcopy(self.record['operations'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate operation'): self.result()
    def test_unmapped_posture(self):
        self.record['postures'].append('reviewed'); self.claim['posture_ref']='reviewed'; self.assertEqual(self.result()['reason'],'no-routing-rule')
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input.json'; path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): read_input(path)
    def test_cli(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'claim.json'
            for expected in [0,1,2]:
                if expected==1: self.claim['kind_ref']='unknown'
                if expected==2: self.claim['authenticated']=True
                dump(path,self.claim)
                result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(PACKAGE/'fixtures/valid/authority-model-record.json'),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
