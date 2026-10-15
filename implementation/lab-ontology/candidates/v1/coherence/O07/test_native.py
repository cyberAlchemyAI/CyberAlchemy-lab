"""Actual cold native reader; malformed owned originals fail before authority."""
import unittest
from base import *

class NativeCoherenceGuards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  migration=ONTOLOGY/'migration/adapters';sys.path.insert(0,str(migration));module('build',migration/'build.py');cls.check=module('_O07_guard_check',migration/'check.py')
  cls.archive=load(ORIGINAL/'native.snapshot');cls.executable=original(CONTEXT)['execution_locator_binding'];bound(cls.executable,external=True)
 def test_actual_native_original_replay_without_cache(self):
  r=self.check.read_native(copy.deepcopy(self.archive),self.executable);self.assertEqual(r['checkpoint_parity'],'PASS');self.assertEqual((len(r['semantic_events']),len(r['governance_events'])),(88,88))
 def test_actual_native_malformed_semantic_governance_tuple_rejected(self):
  value=copy.deepcopy(self.archive);name='governance/00000001-ontology-governance:O05:1.json';event=parse(base64.b64decode(value['files'][name]['base64_original_bytes']));event['semantic_ref']['semantic_event_digest']='0'*64
  raw=encoded(event);value['files'][name]={'sha256':sha(raw),'base64_original_bytes':base64.b64encode(raw).decode()}
  with self.assertRaisesRegex(ValueError,'native cold replay rejected'):self.check.read_native(value,self.executable)
 def test_actual_native_unselected_private_file_rejected(self):
  value=copy.deepcopy(self.archive);raw=b'owned harmless guard fixture';value['files']['private-body.json']={'sha256':sha(raw),'base64_original_bytes':base64.b64encode(raw).decode()}
  with self.assertRaisesRegex(ValueError,'unselected native archive entry'):self.check.read_native(value,self.executable)

if __name__=='__main__':unittest.main()
