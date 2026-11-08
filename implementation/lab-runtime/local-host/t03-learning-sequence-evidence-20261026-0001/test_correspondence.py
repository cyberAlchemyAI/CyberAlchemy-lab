"""Causal cold-correspondence checks; no native learning run is simulated."""
import ast,importlib.util,json,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cold_correspondence',HERE/'verify.py');V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
class Tests(unittest.TestCase):
 def names(self):
  caller=HERE.parent/'t03-installed-learning-caller-0004/consume_run.py';tree=ast.parse(caller.read_bytes())
  node=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='leaves' for t in n.targets))
  return list(ast.literal_eval(node.value))
 def test_exact_actual_consumer_leaf_contract_is_accepted(self):
  names=self.names();self.assertEqual(set(V.consumed_names([{'name':n} for n in names])),set(names))
 def test_duplicate_or_application_substitution_is_refused_even_with_four_rows(self):
  names=self.names()
  for changed in (names[:3]+names[:1],names[:3]+['later-application-result.json']):
   with self.subTest(changed=changed),self.assertRaisesRegex(ValueError,'exact four distinct'):V.consumed_names([{'name':n} for n in changed])
 def test_missing_or_extra_assessed_leaf_is_refused(self):
  names=self.names()
  for changed in (names[:3],names+['application-candidate-original.json']):
   with self.subTest(changed=changed),self.assertRaisesRegex(ValueError,'exact four distinct'):V.consumed_names([{'name':n} for n in changed])
 def test_event_and_receipt_reads_use_the_same_link_refusal(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'events.jsonl').write_bytes(b'{"actual":"controlled bytes"}\n');(root/'linked-events').symlink_to(root/'events.jsonl')
   self.assertEqual(V.checked_bytes(root/'events.jsonl'),b'{"actual":"controlled bytes"}\n')
   with self.assertRaisesRegex(ValueError,'linked evidence'):V.checked_bytes(root/'linked-events')
   (root/'link-parent').symlink_to(root,target_is_directory=True)
   with self.assertRaisesRegex(ValueError,'linked evidence'):V.checked_bytes(root/'link-parent/events.jsonl')
if __name__=='__main__':unittest.main()
