"""Real native source-input substitution and private coordination scope checks."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'), str(HERE)]
import owned_coordination_capsule as C

class Capsule(unittest.TestCase):
    def setUp(self):
        raw = (Path.home()/'.local/share/cyberalchemy-lab/t22-native-agent-diagnostics/21a4b1ff86e8495aaa4d6f55e59731d9/first-emitter-receipt.json').read_bytes()
        self.assertEqual(C.sha(raw), '033f45624326e621a17fe1e0f620be86b83ff58db3f2b3abfbd13d666c7ab4fa')
        self.emission = json.loads(raw)
    def build(self):
        return C.build(self.emission, run_ref='workflow-run:independent-capsule-negative', principal_ref=self.emission['principal_ref'], scope_ref=self.emission['scope_ref'])
    def replace(self, kind, change):
        row = next(r for r in self.emission['coordination_inputs'] if r['origin']['semantic_kind'] == kind)
        body = json.loads(base64.b64decode(row['private_original_base64']))
        change(body)
        raw = C.encoded(body)
        row['private_original_base64'] = base64.b64encode(raw).decode()
        row['sha256'] = row['artifact']['byte_sha256'] = C.sha(raw)
    def test_actual_originals_build_five_schema_valid_private_candidates(self):
        capsule, raws = self.build()
        self.assertEqual(len(raws), 5)
        self.assertEqual(capsule['actual_owner_outcome'], None)
        self.assertEqual(capsule['authority_effect'], 'none')
    def test_coordinated_assignment_body_and_header_substitution_refused(self):
        self.replace('agent-assignment', lambda b: b['payload'].update(work_ref='work:another@1'))
        with self.assertRaisesRegex(ValueError, 'does not close'): self.build()
    def test_coordinated_goal_selection_substitution_refused(self):
        self.replace('work', lambda b: b['payload'].update(goal_refs=['goal:another@1']))
        with self.assertRaisesRegex(ValueError, 'does not close'): self.build()
    def test_hash_valid_foreign_project_context_refused(self):
        self.replace('coordination-context', lambda b: b.update(project_ref='project:foreign'))
        with self.assertRaisesRegex(ValueError, 'does not close'): self.build()
    def test_missing_input_and_hash_corruption_refused(self):
        original = copy.deepcopy(self.emission)
        self.emission['coordination_inputs'].pop()
        with self.assertRaisesRegex(ValueError, 'input set'): self.build()
        self.emission = original
        self.emission['coordination_inputs'][0]['private_original_base64'] = base64.b64encode(b'{}').decode()
        with self.assertRaisesRegex(ValueError, 'original/header'): self.build()

if __name__ == '__main__': unittest.main()
