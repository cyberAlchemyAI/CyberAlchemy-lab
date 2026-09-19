import copy
import tempfile
import unittest
from pathlib import Path
from check import assess, read_input
from support import ROOT, PACKAGE, LAB, load, dump, binding

class Changes(unittest.TestCase):
    def setUp(self): self.record=load(PACKAGE/'fixtures/valid/schema-change-record.json')
    def reject(self):
        with self.assertRaises(Exception): assess(self.record)
    def test_breaking_and_migration(self):
        result=assess(self.record)
        self.assertEqual(result['compatibility'],'breaking-on-witnesses')
        self.assertEqual(result['changed_top_level_fields'],['constraints'])
        self.assertFalse(result['rollout_authorized']); self.assertFalse(result['obligations_executed']); self.assertFalse(result['universal_compatibility_proven'])
    def test_digest_drift(self):
        self.record['preimage']['sha256']='0'*64; self.reject()
    def test_no_change(self):
        self.record['postimage']=self.record['preimage']; self.reject()
    def test_scope(self):
        self.record['scope_ref']='other'; self.reject()
    def test_no_witnesses(self):
        self.record['witnesses']=[]; self.reject()
    def test_wrong_expectation(self):
        self.record['witnesses'][0]['expected_after_on_original']=True; self.reject()
    def test_false_compatibility(self):
        self.record['compatibility_claim']='compatible-on-witnesses'; self.reject()
    def test_failed_migration(self):
        self.record['witnesses'][0]['after']=self.record['witnesses'][0]['before']; self.reject()
    def test_duplicate_witness(self):
        self.record['witnesses']*=2; self.reject()
    def test_unbound_source(self):
        self.record['source_evidence'][0]['sha256']='0'*64; self.reject()
    def test_unsupported_validator(self):
        self.record['validator_ref']=self.record['preimage']; self.reject()
    def test_no_authority(self):
        self.record['authority_effect']='admit'; self.reject()
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input.json'; path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): read_input(path)
    def test_additive_witness_compatibility(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'post.json'; post=load(LAB/self.record['postimage']['path']); post['constraints'][0]['fields'][-1]['required']=False; dump(path,post)
            self.record['postimage']=binding(path); self.record['compatibility_claim']='compatible-on-witnesses'; self.record['witnesses'][0]['expected_after_on_original']=True
            result=assess(self.record); self.assertEqual(result['compatibility'],'compatible-on-witnesses'); self.assertFalse(result['universal_compatibility_proven'])
    def test_cross_identity(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'post.json'; post=load(LAB/self.record['postimage']['path']); post['schema_id']='other'; dump(path,post)
            self.record['postimage']=binding(path); self.reject()

if __name__=='__main__': unittest.main()
