"""Actual original kindless schemas and causal identity/header substitution."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'))
from jsonschema import Draft202012Validator
path=HERE/'api73-reference-overlay-0003/owned_workflow_semantics.py'
spec=importlib.util.spec_from_file_location('_owned_kindless_semantics',path);S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)

class Identity(unittest.TestCase):
    def setUp(self):
        file=ROOT/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/instances/legacy-local-4636eca980a5d94d/source/packages/0001/setup-artifacts/product.json'
        raw=file.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'47cd5140bb3dc191fcb3283761a6c366f771184d37d7a6174de33ea9c40082b6')
        self.product=json.loads(raw);self.schema=json.loads((ROOT/'authority/artifact-types/product-identity/v2/schema.json').read_bytes())
        self.h={'scope_ref':'project:cyberalchemy-v2-to-lab-migration','identity_ref':self.product['product_id'],
          'version_ref':self.product['product_id']+'@'+self.product['version'],'carrier_ref':'cal.artifact-type.product-identity/v2','byte_sha256':hashlib.sha256(raw).hexdigest()}
    def check(self,body,header,schema):
        Draft202012Validator(schema).validate(body);return S.original_identity(body,header)
    def test_actual_selected_ProductIdentity_original_schema_and_axis(self):
        self.assertEqual(self.check(self.product,self.h,self.schema),self.product['product_id'])
    def test_schema_valid_another_Product_cannot_satisfy_selected_header(self):
        body=copy.deepcopy(self.product);body['product_id']='product:another'
        Draft202012Validator(self.schema).validate(body)
        with self.assertRaisesRegex(ValueError,'identity/revision'):self.check(body,self.h,self.schema)
    def test_header_identity_or_revision_substitution_refused(self):
        for key,value in [('identity_ref','product:another'),('version_ref','product:another@1')]:
            h=copy.deepcopy(self.h);h[key]=value
            with self.assertRaisesRegex(ValueError,'identity/revision'):self.check(self.product,h,self.schema)
    def test_new_Node_field_cannot_hide_changed_Product_axis(self):
        body=copy.deepcopy(self.product);body['node_id']=self.h['identity_ref'];body['product_id']='product:another'
        with self.assertRaises(Exception):self.check(body,self.h,self.schema)
    def test_original_migration_manifest_schema_identity_and_substitution(self):
        base=ROOT/'authority/artifact-types/repository-migration-manifest/v1/candidates/0001'
        body=json.loads((base/'fixtures/valid/migration.json').read_bytes());schema=json.loads((base/'schema.json').read_bytes())
        identity=body['migration_manifest_id'];h={'carrier_ref':'cal.artifact-type.repository-migration-manifest/v1','identity_ref':identity,'version_ref':identity+'@'+body['version']}
        self.assertEqual(self.check(body,h,schema),identity)
        body['migration_manifest_id']='migration-manifest:another';Draft202012Validator(schema).validate(body)
        with self.assertRaisesRegex(ValueError,'identity/revision'):self.check(body,h,schema)
    def test_ordinary_node_identity_contract_preserved(self):
        body=json.loads((ROOT/'authority/artifact-types/intent-resolution/v1/fixtures/valid/record.json').read_bytes())
        schema=json.loads((ROOT/'authority/artifact-types/intent-resolution/v1/schema.json').read_bytes());identity=body['node_id']
        self.assertEqual(self.check(body,{'carrier_ref':'cal.artifact-type.intent-resolution/v1','identity_ref':identity,'version_ref':identity+'@fixture.1'},schema),identity)

if __name__=='__main__':unittest.main()
