"""Causal selected error-domain and rule-source tests; no native effect claim."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(Path(__file__).resolve().parent)]
from jsonschema import Draft202012Validator
from referencing import Registry,Resource
import control_probe as C
BASE=ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas'
ERROR=json.loads((BASE/'error-result.schema.json').read_bytes());COMMON=json.loads((BASE/'common.schema.json').read_bytes())
REGISTRY=Registry().with_resources([(v['$id'],Resource.from_contents(v)) for v in (ERROR,COMMON)])
class Schemas:
 operations={'failure.assess':{'error_schema':{'resource_uri':ERROR['$id']}}}
 def valid(self,name,value):return True  # Outer transport deliberately accepts an object.
 def protocol_valid(self,uri,value):
  if uri!=ERROR['$id']:return False
  return Draft202012Validator(ERROR,registry=REGISTRY).is_valid(value)
class Probe(unittest.TestCase):
 def setUp(self):
  self.raw=b'actual controlled request bytes';self.profile={'ref':'synthetic-profile','sha256':'a'*64}
  body=json.loads((ROOT/'docs/proposals/0007-lab-integrated-schema-package/examples/error-result.json').read_bytes());body['code']='closure-missing';body['request_binding']['sha256']=C.sha(self.raw)
  self.reply={'kind':'error','request_binding':{'sha256':C.sha(self.raw)},'contract_profile_binding':self.profile,'message':body}
 def test_actual_selected_error_domain_schema_accepts_known_refusal(self):
  self.assertIs(C.validate_known_refusal(Schemas(),self.raw,self.reply,self.profile),self.reply)
 def test_envelope_valid_but_domain_invalid_reply_refused(self):
  self.reply['message']['unselected_domain_field']=True
  with self.assertRaisesRegex(ValueError,'operation-domain schema'):C.validate_known_refusal(Schemas(),self.raw,self.reply,self.profile)
 def test_independent_rule_source_path_and_digest_cannot_be_substituted(self):
  wanted={'ref':C.RULE_SOURCE_REF,'sha256':C.RULE_SOURCE_SHA};self.assertEqual(C.validate_rule_source(wanted),wanted)
  for changed in ({**wanted,'sha256':'0'*64},{**wanted,'ref':'foreign/source-manifest.json'},{**wanted,'extra':True}):
   with self.subTest(changed=changed),self.assertRaisesRegex(ValueError,'rule-source binding'):C.validate_rule_source(changed)
 def test_control_subject_is_semantic_identity_not_file_locator(self):
  self.assertTrue(C.CONTROL_ID.startswith('validator:'));self.assertNotIn('/',C.CONTROL_ID);self.assertNotIn('@',C.CONTROL_ID)
if __name__=='__main__':unittest.main()
