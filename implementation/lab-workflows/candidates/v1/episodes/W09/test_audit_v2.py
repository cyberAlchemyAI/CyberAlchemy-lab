"""Strict negative archive tests; no domain actions are repeated."""
from audit_v2 import *
sys.path.insert(0,str(ROOT/'implementation/lab-runtime/candidates/repeatable-operation'))
import base64
import unittest
class GenesisTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='cal-W09-reader-negative-');self.root=Path(self.temp.name)
        self.parent=CASE_PATHS['engineering']/'context-branch.snapshot';self.value=load(self.parent);self.pins=copy.deepcopy(self.value['project_pins'])
    def tearDown(self):self.temp.cleanup()
    def reject(self,value,message,pin=None):
        p=self.root/'input.snapshot';p.write_bytes(encoded(value))
        with self.assertRaisesRegex(ValueError,message):restore_genesis(p,pin or sha(p.read_bytes()),self.root/'restored',self.pins)
        self.assertFalse((self.root/'restored').exists())
    def test_wrong_pin(self):self.reject(self.value,'genesis archive pin differs','0'*64)
    def test_private_key_claim(self):self.value['private_key_included']=True;self.reject(self.value,'authority/custody differs')
    def test_memory_claim(self):self.value['Session_memory_included']=True;self.reject(self.value,'authority/custody differs')
    def test_owner_claim(self):self.value['actual_owner_outcome']='admit';self.reject(self.value,'authority/custody differs')
    def test_authority_claim(self):self.value['authority_effect']='admit';self.reject(self.value,'authority/custody differs')
    def test_unexpected_schema(self):self.value['schema_version']='other';self.reject(self.value,'authority/custody differs')
    def test_wrong_pins(self):self.value['project_pins']['expected_head']='0'*64;self.reject(self.value,'authority/custody differs')
    def test_extra_path(self):self.value['files']['../escape']=self.value['files']['HEAD.json'];self.reject(self.value,'archive closure required')
    def test_extra_transaction(self):self.value['files']['transactions/0000000001.json']=self.value['files']['transactions/0000000000.json'];self.reject(self.value,'archive closure required')
    def test_missing_baseline(self):del self.value['files']['baseline.json'];self.reject(self.value,'archive closure required')
    def test_existing_destination(self):
        p=self.root/'input.snapshot';p.write_bytes(encoded(self.value));dest=self.root/'restored';dest.mkdir()
        with self.assertRaisesRegex(ValueError,'archive closure required'):restore_genesis(p,sha(p.read_bytes()),dest,self.pins)
    def test_repo_destination(self):
        with self.assertRaisesRegex(ValueError,'archive closure required'):restore_genesis(self.parent,sha(self.parent.read_bytes()),HERE/'forbidden-reader-output',self.pins)
if __name__=='__main__':unittest.main(verbosity=2)
