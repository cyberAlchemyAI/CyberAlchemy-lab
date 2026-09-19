import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from check import assess, read_input
from support import ROOT, PACKAGE, load

class Method(unittest.TestCase):
    def setUp(self): self.record=load(PACKAGE/'fixtures/valid/method-record.json')
    def reject(self):
        with self.assertRaises((ValueError, __import__('jsonschema').ValidationError)): assess(self.record)
    def test_coherent(self):
        result=assess(self.record); self.assertTrue(result['declaration_coherent'])
        self.assertEqual([x['action_id'] for x in result['ordered_plan']],['inspect','review'])
        for key in ['instructions_executed','gates_evaluated','outcome_proven','execution_authorized']: self.assertFalse(result[key])
    def test_forward_read(self):
        self.record['actions'].reverse(); self.reject()
    def test_duplicate_action(self):
        self.record['actions'][1]['action_id']='inspect'; self.reject()
    def test_duplicate_output(self):
        self.record['outputs'].append(copy.deepcopy(self.record['outputs'][0])); self.reject()
    def test_overwrite_input(self):
        self.record['outputs'][0]['slot_id']='proposal'; self.reject()
    def test_unknown_role(self):
        self.record['actions'][0]['role_ref']='unknown'; self.reject()
    def test_unknown_gate_role(self):
        self.record['gates'][0]['role_ref']='unknown'; self.reject()
    def test_missing_output(self):
        self.record['outputs'].append({'slot_id':'missing','description':'Never produced'}); self.reject()
    def test_duplicate_producer(self):
        self.record['actions'][1]['writes'].append('assessment'); self.reject()
    def test_undeclared_output(self):
        self.record['actions'][0]['writes']=['missing']; self.reject()
    def test_future_gate_subject(self):
        self.record['gates'][0]['subject_refs']=['review']; self.reject()
    def test_unknown_gate(self):
        self.record['actions'][0]['gate_refs']=['missing']; self.reject()
    def test_uncovered_output(self):
        self.record['gates'][1]['subject_refs']=['assessment']; self.reject()
    def test_skipped_completion_gate(self):
        self.record['validation_rule']['required_gate_refs']=['shape-check']; self.reject()
    def test_residue_owner(self):
        self.record['residue_rule']['owner_ref']='unknown'; self.reject()
    def test_reuse_overlap(self):
        self.record['reuse']['fixed_fields'].append('scope_ref'); self.reject()
    def test_reuse_omission(self):
        self.record['reuse']['fixed_fields'].remove('boundary'); self.reject()
    def test_evidence_drift(self):
        self.record['evidence'][0]['sha256']='0'*64; self.reject()
    def test_instructions_remain_text(self):
        with tempfile.TemporaryDirectory() as d:
            marker=Path(d)/'never-execute'
            self.record['actions'][0]['instruction']='touch '+str(marker)
            assess(self.record); self.assertFalse(marker.exists())
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input.json'; path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): read_input(path)
    def test_cli(self):
        path=PACKAGE/'fixtures/valid/method-record.json'
        result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr); self.assertTrue(json.loads(result.stdout)['declaration_coherent'])
        result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(PACKAGE/'fixtures/invalid/authority.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,2); self.assertFalse(json.loads(result.stdout)['input_valid'])
if __name__=='__main__': unittest.main()
