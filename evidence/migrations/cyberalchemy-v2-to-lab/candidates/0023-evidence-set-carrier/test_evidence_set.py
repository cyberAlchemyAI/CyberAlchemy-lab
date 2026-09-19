import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from jsonschema import ValidationError
from check import assess
from support import ROOT, LAB, PACKAGE, load, dump, binding
class EvidenceSet(unittest.TestCase):
    def setUp(self): self.record=load(PACKAGE/'fixtures/valid/evidence-set-record.json')
    def reject(self,message):
        with self.assertRaisesRegex(ValueError,message): assess(self.record)
    def test_inventory(self):
        result=assess(self.record); self.assertEqual(result['members_verified'],2); self.assertEqual(result['question_coverage']['general-proof']['counterevidence'],['limitations'])
        for key in ['evidence_sufficiency_proven','roles_independently_verified','conclusion_established','experiment_execution_proven']: self.assertFalse(result[key])
    def test_digest_drift(self):
        self.record['members'][0]['binding']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_duplicate_member(self):
        self.record['members'][1]['member_id']='validation'; self.reject('Duplicate member')
    def test_duplicate_path(self):
        self.record['members'][1]['binding']=self.record['members'][0]['binding']; self.reject('not distinct evidence')
    def test_copied_content(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'copy.json'; path.write_bytes((LAB/self.record['members'][0]['binding']['path']).read_bytes()); self.record['members'][1]['binding']=binding(path); self.reject('not distinct evidence')
    def test_unknown_contribution(self):
        self.record['members'][0]['contributions'][0]['question_ref']='unknown'; self.reject('Unknown contribution')
    def test_conflicting_roles(self):
        contribution=copy.deepcopy(self.record['members'][0]['contributions'][0]); contribution['role']='counterevidence'; self.record['members'][0]['contributions'].append(contribution); self.reject('unambiguous role')
    def test_duplicate_question(self):
        self.record['questions'].append(copy.deepcopy(self.record['questions'][0])); self.reject('Duplicate question')
    def test_uncovered_question(self):
        self.record['questions'].append({'question_id':'new','question':'Uncovered?'}); self.reject('lacks evidence')
    def test_unknown_gap(self):
        self.record['gaps'][0]['question_ref']='unknown'; self.reject('Unknown gap')
    def test_duplicate_gap(self):
        self.record['gaps']*=2; self.reject('Duplicate gap')
    def test_gaps_only(self):
        self.record['members']=[]; self.record['gaps'].append({'question_ref':'local-checks','missing':'Missing run record','owner_route':'route:owner','next_step':'Obtain evidence'})
        result=assess(self.record); self.assertEqual(result['members_verified'],0); self.assertFalse(result['conclusion_established'])
    def test_conclusion_rejected(self):
        self.record['conclusion']='proven'
        with self.assertRaises(ValidationError): assess(self.record)
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'record.json'
            for expected in [0,2]:
                if expected==2: self.record['members'][0]['binding']['sha256']='0'*64
                dump(path,self.record); result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
