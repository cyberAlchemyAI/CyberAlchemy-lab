import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from jsonschema import ValidationError
from check import assess, read_input
from support import ROOT, PACKAGE, load, dump
class AuthorityClaim(unittest.TestCase):
    def setUp(self): self.record=load(PACKAGE/'fixtures/valid/authority-claim-record.json')
    def reject(self,message):
        with self.assertRaisesRegex(ValueError,message): assess(self.record)
    def test_bound_claim(self):
        result=assess(self.record); self.assertTrue(result['bindings_verified']); self.assertEqual(result['routing']['outcome'],'requires-owner-gate')
        for key in ['claim_authenticated','basis_sufficient','gate_verdict_present','action_authorized']: self.assertFalse(result[key])
    def test_object_drift(self):
        self.record['governed_object']['binding']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_model_drift(self):
        self.record['authority_surface']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_basis_drift(self):
        self.record['basis'][0]['binding']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_object_identity(self):
        self.record['governed_object']['object_ref']='other'; self.reject('Object identity mismatch')
    def test_identity_collapse(self):
        self.record['claim_id']=self.record['governed_object']['object_ref']; self.reject('identity collapses')
    def test_duplicate_basis(self):
        self.record['basis'].append(copy.deepcopy(self.record['basis'][0])); self.reject('Duplicate basis')
    def test_owner_route(self):
        self.record['owner_route']='route:other'; self.reject('owner route differs')
    def test_scope(self):
        self.record['scope_ref']='other'; self.assertEqual(assess(self.record)['routing']['outcome'],'not-applicable')
    def test_effect_blocked(self):
        self.record.update(operation_ref='request-admission',intended_effect='admit'); self.assertEqual(assess(self.record)['routing']['reason'],'effect-blocked')
    def test_effect_mismatch(self):
        self.record['intended_effect']='admit'; self.assertEqual(assess(self.record)['routing']['reason'],'operation-effect-mismatch')
    def test_missing_basis(self):
        self.record['basis']=[]
        with self.assertRaises(ValidationError): assess(self.record)
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input.json'; path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): read_input(path)
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'claim.json'
            for expected in [0,1,2]:
                if expected==1: self.record['scope_ref']='other'
                if expected==2: self.record['authenticated']=True
                dump(path,self.record)
                result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
