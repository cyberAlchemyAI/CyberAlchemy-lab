import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from jsonschema import ValidationError
from check import assess, read_input
from support import ROOT, LAB, PACKAGE, load, dump, binding

class Discipline(unittest.TestCase):
    def setUp(self): self.record=load(PACKAGE/'fixtures/valid/discipline-record.json')
    def reject(self, message=None):
        if message:
            with self.assertRaisesRegex(ValueError,message): assess(self.record)
        else:
            with self.assertRaises((ValueError,ValidationError)): assess(self.record)
    def receipt_case(self, edit, message):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'receipts/validation.json'
            receipt=load(LAB/self.record['recurrence_evidence'][0]['receipt']['path']); edit(receipt); dump(path,receipt)
            self.record['recurrence_evidence'][0]['receipt']=binding(path); self.reject(message)
    def test_supported(self):
        result=assess(self.record); self.assertTrue(result['recurrence_supported']); self.assertEqual(result['capabilities_checked'],2)
        self.assertEqual(result['maturity_status'],'candidate'); self.assertFalse(result['promotion_authorized']); self.assertFalse(result['hardening_completed'])
    def test_duplicate_occurrence(self):
        self.record['recurrence_evidence'][1]['occurrence_id']=self.record['recurrence_evidence'][0]['occurrence_id']; self.reject('Duplicate occurrence')
    def test_reused_receipt(self):
        self.record['recurrence_evidence'][1]['receipt']=self.record['recurrence_evidence'][0]['receipt']; self.reject('Reused receipt')
    def test_duplicate_capability(self):
        self.record['capabilities'][1]['capability_ref']=self.record['capabilities'][0]['capability_ref']; self.reject('Duplicate capability')
    def test_alias_capability(self):
        self.record['capabilities'][1]['artifact']=self.record['capabilities'][0]['artifact']; self.reject('alias')
    def test_unknown_capability(self):
        self.record['recurrence_evidence'][0]['capability_ref']='unknown'; self.reject('Unknown capability')
    def test_wrong_artifact_receipt(self):
        self.record['recurrence_evidence'][0]['capability_ref']='capability:method'; self.reject('does not bind')
    def test_receipt_drift(self):
        self.record['recurrence_evidence'][0]['receipt']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_canonical_rejected(self):
        self.record['maturity_status']='canonical'; self.reject()
    def test_no_steward(self):
        self.record['steward_ref']=' '; self.reject()
    def test_failed_receipt(self):
        self.receipt_case(lambda x:x.update(result='BLOCK'),'did not pass')
    def test_empty_checks(self):
        self.receipt_case(lambda x:x.update(checks=[]),'missing or failed checks')
    def test_material_path_escape(self):
        self.receipt_case(lambda x:x.update(materials={'../outside':'0'*64}),'Unsafe receipt material path')
    def test_missing_materials(self):
        self.receipt_case(lambda x:x.update(materials={}),'Missing receipt materials')
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input.json'; path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): read_input(path)
    def test_cli(self):
        result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(PACKAGE/'fixtures/valid/discipline-record.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr); self.assertTrue(json.loads(result.stdout)['recurrence_supported'])
        result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(PACKAGE/'fixtures/invalid/canonical.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,2); self.assertFalse(json.loads(result.stdout)['input_valid'])
if __name__=='__main__': unittest.main()
