"""Actual selected code-origin checks with synthetic retained transport only."""
import copy
import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import producer as P
import test_review_scope as RS

class TypedPlugin(unittest.TestCase):
 def setUp(self):
  self.fixture=RS.ReviewScope();self.fixture.setUp();f=self.fixture
  self.observed=copy.deepcopy(f.observed)
  self.observed.update(outputs=list(f.records.values()),terminal_binding={'ref':'synthetic:terminal','sha256':'t'*64})
  self.path=Path(P.__file__).with_name('review_scope.py')
  self.digest=hashlib.sha256(self.path.read_bytes()).hexdigest()
  self.plugin={'module_binding':{'path':str(self.path.relative_to(P.ROOT)),'sha256':self.digest},'entrypoint':'produce','controls':{'review_observation_ref':'synthetic:review-observation'}}
  self.mock=patch.object(P.R,'consume',return_value=self.observed);self.mock.start();self.addCleanup(self.mock.stop)
  self.selections=[{'synthetic_transport_only':True}]
  self.ref='bundle:synthetic@1'
 def proof(self):return P.ArchiveProof(self.selections,transitions={'transition:synthetic:review':[self.ref]},typed_productions=[self.plugin])
 def test_actual_selected_plugin_produces_separate_private_candidate_receipt(self):
  p=self.proof();self.assertTrue(p.guard());self.assertEqual(len(p.records),4);self.assertEqual(len(p.api_returned_refs),2)
  self.assertEqual(len(p.typed_receipt_raws),1)
  raw=next(iter(p.typed_receipt_raws.values()));self.assertIn(b'"new_candidates_were_returned_by_API":false',raw)
 def test_wrong_selected_module_digest_or_external_path_refuses(self):
  self.plugin['module_binding']['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'producer code'):self.proof()
  self.plugin['module_binding']['path']='/tmp/foreign-producer.py'
  with self.assertRaisesRegex(ValueError,'archive member'):self.proof()
 def test_preloaded_foreign_same_name_module_refuses(self):
  self.proof();name='_cal_t31_private_typed_'+self.digest;module=sys.modules[name];old=module.__file__;module.__file__='/tmp/foreign-review-scope.py'
  try:
   with self.assertRaisesRegex(ValueError,'function origin'):self.proof()
  finally:module.__file__=old
 def test_actual_function_code_rebinding_refuses_even_with_same_name(self):
  self.proof();name='_cal_t31_private_typed_'+self.digest;module=sys.modules[name];old=module.produce.__code__
  namespace={};exec(compile('def produce(**kwargs):\n return {}\n',str(self.path),'exec'),namespace);module.produce.__code__=namespace['produce'].__code__
  try:
   with self.assertRaisesRegex(ValueError,'code object'):self.proof()
  finally:module.produce.__code__=old
 def test_undeclared_plugin_field_or_mutated_control_refuses(self):
  p=self.proof();p.typed_productions[0]['controls']['undeclared']=True
  with self.assertRaisesRegex(ValueError,'controls changed'):p.guard()
  self.plugin['undeclared']=True
  with self.assertRaisesRegex(ValueError,'closed private'):self.proof()

if __name__=='__main__':unittest.main()
