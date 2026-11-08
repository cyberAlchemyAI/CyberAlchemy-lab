"""Retained original bytes, independent later computation, and claim limits."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from observed_replay import RUN, consume_observed, run
from output_store import sha


class RetainedProducerOutputTests(unittest.TestCase):
    def copy(self):
        temp = tempfile.TemporaryDirectory(prefix='t31-observed-test-')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / 'producer'
        shutil.copytree(RUN, root)
        return root

    def test_original_outputs_enter_real_journal_and_later_computation(self):
        result = run()
        self.assertEqual(len(result['transitions']), 2)
        self.assertTrue(result['original_output_bytes_unchanged'])
        self.assertFalse(result['original_producer_rerun'])
        self.assertFalse(result['current_native_source_qualified'])
        self.assertFalse(result['T31_complete'])
        engineering, research = result['transitions']
        self.assertEqual(engineering['later_consumer']['observed_default_regression'], 'FLAG')
        self.assertFalse(engineering['later_consumer']['retained_code_executed'])
        self.assertEqual(research['later_consumer']['research_assessment'], 'inconclusive')
        self.assertAlmostEqual(research['later_consumer']['entropy_nats'], 0.6365141682948128)

    def test_changed_retained_output_refuses(self):
        root = self.copy()
        path = root / 'engineering/workflow/generated-output.json'
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'retained original output differs'):
            run(root)

    def test_changed_actual_consumer_refuses(self):
        root = self.copy()
        path = root / 'engineering/workflow/work.json'
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'retained original consumer differs'):
            run(root)

    def test_changed_label_bytes_refuse_even_if_entropy_unchanged(self):
        root = self.copy()
        receipt = json.loads((root / 'RESULT.json').read_bytes())
        row = next(r for r in receipt['new_output_transitions'] if ':research:' in r['transition_ref'])
        consumed = [(h, (root / p).read_bytes()) for h, p in zip(row['output_artifact_refs'], row['output_original_paths'])]
        path = root / 'research/assessment.json'
        original = json.loads(path.read_bytes())
        original['labels'] = ['invented-a', 'invented-a', 'invented-b']
        path.write_text(json.dumps(original))
        with self.assertRaisesRegex(ValueError, 'selected retained input bytes differ'):
            consume_observed('research', consumed, root)

    def test_coordinated_evidence_and_assessment_substitution_refuses(self):
        root = self.copy()
        path = root / 'engineering/evidence/default-regression-complete.json'
        path.write_bytes(path.read_bytes() + b' ')
        assessment_path = root / 'engineering/assessment.json'
        assessment = json.loads(assessment_path.read_bytes())
        assessment['checks']['default-regression-complete']['evidence_sha256'] = sha(path.read_bytes())
        assessment_path.write_text(json.dumps(assessment))
        with self.assertRaisesRegex(ValueError, 'selected retained input bytes differ'):
            run(root)


if __name__ == '__main__':
    unittest.main()
