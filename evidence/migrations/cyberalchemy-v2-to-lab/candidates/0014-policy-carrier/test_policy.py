import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from jsonschema import ValidationError
from check import assess, read_input
from support import ROOT, PACKAGE, load, dump
class Policy(unittest.TestCase):
    def setUp(self):
        self.record=load(PACKAGE/'fixtures/valid/policy-record.json'); self.challenge=load(ROOT/'examples/ready.json')
    def result(self): return assess(self.record,self.challenge)
    def test_ready(self):
        result=self.result(); self.assertEqual(result['outcome'],'ready-for-owner-review'); self.assertEqual(result['suggested_route'],self.record['owner_route'])
        for key in ['gate_completed','challenge_resolved','confidence_changed','route_executed','action_authorized']: self.assertFalse(result[key])
    def test_missing(self):
        self.challenge['answers']={}; self.assertEqual(self.result()['outcome'],'indeterminate')
    def test_blocked(self):
        self.challenge['answers']['evidence-attached']=False; self.assertEqual(self.result()['outcome'],'blocked')
    def test_blocked_and_missing(self):
        self.challenge['answers']={'evidence-attached':False}; result=self.result(); self.assertEqual(result['outcome'],'blocked'); self.assertEqual(result['missing_answers'],['subject-confirmed'])
    def test_scope(self):
        self.challenge['scope_ref']='other'; self.assertEqual(self.result()['outcome'],'not-applicable'); self.assertIsNone(self.result()['suggested_route'])
    def test_subject(self):
        self.challenge['subject_ref']='other'; self.assertEqual(self.result()['outcome'],'not-applicable')
    def test_policy(self):
        self.challenge['policy_ref']='other'; self.assertEqual(self.result()['outcome'],'not-applicable')
    def test_mode(self):
        self.challenge['challenge_mode']='override'; self.assertEqual(self.result()['outcome'],'unsupported-mode')
    def test_unknown_answer(self):
        self.challenge['answers']['unknown']=True
        with self.assertRaisesRegex(ValueError,'Unknown answer'): self.result()
    def test_no_boolean_coercion(self):
        for value in [1,'true',None]:
            self.challenge['answers']['evidence-attached']=value
            with self.assertRaises(ValidationError): self.result()
    def test_duplicate_questions(self):
        self.record['blocking_questions']*=2
        with self.assertRaisesRegex(ValueError,'Duplicate question'): self.result()
    def test_conflicting_links(self):
        self.record['contradiction_edges']=['edge:one']; self.record['validation_edges']=['edge:one']
        with self.assertRaisesRegex(ValueError,'contradictory roles'): self.result()
    def test_residue_route(self):
        self.challenge['answers']={}; self.assertEqual(self.result()['suggested_route'],self.record['challenge_residue_route'])
    def test_confidence_excluded(self):
        self.record['evidence_confidence']=0.8
        with self.assertRaises(ValidationError): self.result()
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input.json'; path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): read_input(path)
    def test_cli(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'challenge.json'
            for expected in [0,1,2]:
                if expected==1: self.challenge['answers']={}
                if expected==2: self.challenge['answers']={'evidence-attached':1}
                dump(path,self.challenge)
                result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(PACKAGE/'fixtures/valid/policy-record.json'),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
