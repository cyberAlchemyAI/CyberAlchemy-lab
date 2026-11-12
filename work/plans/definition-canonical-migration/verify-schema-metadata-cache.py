from pathlib import Path
import sys,json,unittest
from copy import deepcopy
from jsonschema import Draft202012Validator,FormatChecker
from jsonschema.exceptions import SchemaError,ValidationError
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'implementation/lab-runtime/alchlang/shared-records'))
from schema_metadata_cache import install

class Checks(unittest.TestCase):
 def setUp(self):
  self.calls=[]
  outer=self
  class Counting:
   @classmethod
   def check_schema(cls,schema,*args,**kwargs):
    outer.calls.append((cls,deepcopy(schema)))
    return Draft202012Validator.check_schema(schema,*args,**kwargs)
  self.validator=Counting;self.stats=install(Counting,maximum=2)
 def test_exact_success_is_reused(self):
  self.validator.check_schema({'type':'string'});self.validator.check_schema({'type':'string'})
  self.assertEqual(len(self.calls),1);self.assertEqual(self.stats['hits'],1)
 def test_changed_schema_and_invalid_schema_are_rechecked(self):
  schema={'type':'string'};self.validator.check_schema(schema);schema['type']='invalid-type'
  for _ in range(2):
   with self.assertRaises(SchemaError):self.validator.check_schema(schema)
  self.assertEqual(len(self.calls),3);self.assertEqual(self.stats['size'],1)
 def test_every_instance_is_still_validated(self):
  schema={'type':'string'}
  for _ in range(2):self.validator.check_schema(schema)
  Draft202012Validator(schema).validate('valid')
  with self.assertRaises(ValidationError):Draft202012Validator(schema).validate(123)
  self.assertEqual(self.stats['hits'],1)
 def test_nondefault_options_bypass_cache(self):
  for _ in range(2):self.validator.check_schema({'type':'string'},format_checker=FormatChecker())
  self.assertEqual(len(self.calls),2);self.assertEqual(self.stats['bypassed'],2)
 def test_capacity_evicts_without_skipping_validation(self):
  for t in ['string','number','object','string']:self.validator.check_schema({'type':t})
  self.assertEqual(len(self.calls),4);self.assertEqual(self.stats['size'],2)
 def test_class_method_dispatch_is_preserved(self):
  class Child(self.validator):pass
  self.validator.check_schema({'type':'string'});Child.check_schema({'type':'string'});Child.check_schema({'type':'string'})
  self.assertEqual([c[0] for c in self.calls],[self.validator,Child]);self.assertEqual(self.stats['hits'],1)
 def test_non_json_values_are_not_cached(self):
  schema={'enum':('a','b')}
  for _ in range(2):
   try:self.validator.check_schema(schema)
   except SchemaError:pass
  self.assertEqual(len(self.calls),2);self.assertEqual(self.stats['bypassed'],2)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():sys.exit(1)
 (Path(__file__).resolve().parent/'SCHEMA-METADATA-CACHE-VERIFICATION.json').write_text(json.dumps({'status':'PASS','checks':result.testsRun,'scope':'Metadata checks only; invalid schemas and all instance validation remain checked; bounded process-local reuse.'},indent=2)+'\n')
