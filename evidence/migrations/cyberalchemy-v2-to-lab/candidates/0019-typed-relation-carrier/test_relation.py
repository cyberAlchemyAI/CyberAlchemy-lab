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
class Relation(unittest.TestCase):
    def setUp(self): self.record=load(PACKAGE/'fixtures/valid/typed-relation-record.json')
    def reject(self,message):
        with self.assertRaisesRegex(ValueError,message): assess(self.record)
    def changed_source(self,edit,message):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'source.json'; source=load(LAB/self.record['source']['binding']['path']); edit(source); dump(path,source); self.record['source']['binding']=binding(path); self.reject(message)
    def test_binding(self):
        result=assess(self.record); self.assertTrue(result['binding_conforms'])
        for key in ['owner_authenticated','owner_local_semantics_interpreted','relation_kind_admitted','effect_executed']: self.assertFalse(result[key])
    def test_reverse_endpoints(self):
        self.record['source'],self.record['target']=self.record['target'],self.record['source']; self.reject('Source must be')
    def test_same_endpoint(self):
        self.record['target']=copy.deepcopy(self.record['source']); self.reject('Endpoints must be distinct')
    def test_source_identity(self):
        self.record['source']['object_ref']='other'; self.reject('Source identity mismatch')
    def test_target_identity(self):
        self.record['target']['object_ref']='other'; self.reject('Target identity mismatch')
    def test_source_drift(self):
        self.record['source']['binding']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_target_drift(self):
        self.record['target']['binding']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_evidence_drift(self):
        self.record['evidence'][0]['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_duplicate_evidence(self):
        self.record['evidence']*=2; self.reject('Duplicate evidence')
    def test_undeclared_target(self):
        self.changed_source(lambda x:x.update(semantic_definition_refs=[]),'exactly one matching')
    def test_duplicate_binding(self):
        self.changed_source(lambda x:x['semantic_definition_bindings'].append(copy.deepcopy(x['semantic_definition_bindings'][0])),'exactly one matching')
    def test_wrong_source_binding_digest(self):
        self.changed_source(lambda x:x['semantic_definition_bindings'][0].update(sha256='0'*64),'Bound bytes changed')
    def test_relation_identity(self):
        self.record['relation_id']=self.record['source']['object_ref']; self.reject('identity collapses')
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'relation.json'
            for expected in [0,2]:
                if expected==2: self.record['direction']='target-to-source'
                dump(path,self.record); result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
