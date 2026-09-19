import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from check import assess, read_input
from support import ROOT, PACKAGE, load, dump, binding
class Gate(unittest.TestCase):
    def setUp(self):
        self.path=PACKAGE/'fixtures/valid/gate-record.json'; self.record=load(self.path); self.obs=load(ROOT/'examples/supported.json')
    def result(self): return assess(self.path,self.obs)
    def with_evidence(self,data):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'evidence.json'; dump(path,data); self.obs['evidence'][0]['binding']=binding(path); return self.result()
    def test_supported(self):
        result=self.result(); self.assertEqual(result['proposed_verdict'],'pass')
        for key in ['owner_verdict_recorded','effect_authorized','effect_executed']: self.assertFalse(result[key])
    def test_missing(self):
        self.obs['evidence']=[]; self.assertEqual(self.result()['proposed_verdict'],'defer')
    def test_unmet(self):
        self.assertEqual(self.with_evidence({'result':'BLOCK'})['proposed_verdict'],'block')
    def test_missing_field(self):
        self.assertEqual(self.with_evidence({})['proposed_verdict'],'defer')
    def test_strict_type(self):
        self.assertEqual(self.with_evidence({'result':True})['proposed_verdict'],'block')
    def test_scope(self):
        self.obs['scope_ref']='other'; result=self.result(); self.assertEqual(result['proposed_verdict'],'block'); self.assertTrue(result['boundary_mismatch'])
    def test_record_drift(self):
        self.obs['gate']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Bound bytes changed'): self.result()
    def test_subject_mismatch(self):
        self.obs['subject']=self.obs['gate']
        with self.assertRaisesRegex(ValueError,'another subject'): self.result()
    def test_evidence_drift(self):
        self.obs['evidence'][0]['binding']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Bound bytes changed'): self.result()
    def test_unknown_criterion(self):
        self.obs['evidence'][0]['criterion_ref']='unknown'
        with self.assertRaisesRegex(ValueError,'Unknown criterion'): self.result()
    def test_duplicate_evidence(self):
        self.obs['evidence'].append(copy.deepcopy(self.obs['evidence'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate criterion evidence'): self.result()
    def test_duplicate_criterion(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'record.json'; self.record['criteria']*=2; dump(path,self.record); self.obs['gate']=binding(path)
            with self.assertRaisesRegex(ValueError,'Duplicate criterion'): assess(path,self.obs)
    def test_escalation(self):
        self.obs['evidence']=[]; self.assertEqual(self.result()['suggested_route'],self.record['escalation_route'])
    def test_unmet_with_missing(self):
        self.obs['evidence']=self.obs['evidence'][:1]; result=self.with_evidence({'result':'BLOCK'}); self.assertEqual(result['proposed_verdict'],'block'); self.assertIn('defer',[x['state'] for x in result['criteria']])
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input.json'; path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): read_input(path)
    def test_flag(self):
        self.obs=load(ROOT/'examples/flagged.json'); result=self.result(); self.assertEqual(result['proposed_verdict'],'flag'); self.assertTrue(result['risks'][0]['follow_up'])
    def test_flag_and_missing(self):
        self.obs=load(ROOT/'examples/flagged.json'); self.obs['evidence']=self.obs['evidence'][1:]; result=self.result(); self.assertEqual(result['proposed_verdict'],'defer'); self.assertEqual(len(result['risks']),1)
    def test_effect_mismatch(self):
        self.obs['requested_effect']='execute-unrelated'; self.assertEqual(self.result()['proposed_verdict'],'block')
    def test_flag_requires_risk(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'record.json'; self.record['criteria'][1]['risk']=None; dump(path,self.record); self.obs['gate']=binding(path)
            with self.assertRaisesRegex(ValueError,'Flag requires risk'): assess(path,self.obs)
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'obs.json'
            for expected in [0,1,2]:
                if expected==1: self.obs['evidence']=[]
                if expected==2: self.obs['completed']=True
                dump(path,self.obs)
                result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(self.path),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
