"""Independent standard-schema checks for actual materialized profile data.
Open Questions: docs/U0-SHARED-CONTRACTS.md; runtime exports checked by Node tests.
"""
import copy,json,unittest
from pathlib import Path
from jsonschema import Draft202012Validator
CORE=Path(__file__).resolve().parents[2]
SCHEMA=json.loads((CORE/'contracts/profile-package-v4.schema.json').read_text())
PROFILE=json.loads((CORE/'profiles/node-http-entry-u0-v4/profile.json').read_text())
VALIDATOR=Draft202012Validator(SCHEMA)
class V4Schema(unittest.TestCase):
 def rejects(self,change):
  value=copy.deepcopy(PROFILE);change(value);self.assertTrue(list(VALIDATOR.iter_errors(value)))
 def test_actual_materialized_descriptor(self):
  Draft202012Validator.check_schema(SCHEMA);VALIDATOR.validate(PROFILE)
 def test_closed_versions_and_wire(self):
  for key in ['schema_version','engine','id','abi','source_contract','recipe']:
   self.rejects(lambda v:v.update({key:'unknown'}))
  self.rejects(lambda v:v.update(ready=True));self.rejects(lambda v:v['configuration'].update(request_bytes=0));self.rejects(lambda v:v['configuration'].update(arbitrary=True))
 def test_exact_distinct_native_roles_and_exports(self):
  self.rejects(lambda v:v['assets'].__setitem__(1,copy.deepcopy(v['assets'][0])))
  self.rejects(lambda v:v['assets'][0].update(role='database'))
  self.rejects(lambda v:v['assets'][0].update(exports=['invented']))
  self.rejects(lambda v:v['assets'].pop())
 def test_real_pin_operands_and_no_source_fallback(self):
  self.rejects(lambda v:v['assets'][0].update(sha256='locked'))
  self.rejects(lambda v:v['assets'][0].update(bytes=0))
  self.rejects(lambda v:v['assets'][0].update(path='../source.ts'))
  self.rejects(lambda v:v['scalar_producer'].update(path='src/producer.ts'))
  self.rejects(lambda v:v['build'].update(node='latest'))
if __name__=='__main__':unittest.main()
