import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import reconcile


class ExactMemberReconciliation(unittest.TestCase):
    def setUp(self):
        self.original = reconcile.selected(reconcile.ORIGINAL)
        self.matrix = reconcile.selected(reconcile.OWNER_MATRIX)
        self.candidate = reconcile.selected(reconcile.CANDIDATE)
        self.inputs = reconcile.selected(reconcile.INPUTS)

    def test_cold_exact_363_and_retained_receipt(self):
        raw = reconcile.read_frozen(reconcile.HERE / 'RECONCILIATION.json')
        receipt = reconcile.cold_verify()
        self.assertEqual(reconcile.canonical(receipt), reconcile.read_frozen(reconcile.HERE / 'RESULT.json'))
        self.assertEqual(len(json.loads(raw)['members']), 363)
        self.assertEqual(receipt['unresolved_member_count'], 363)
        self.assertFalse(receipt['original_member_dispositions_complete'])
        self.assertFalse(receipt['task_complete'])

    def test_missing_duplicate_and_extra_original_id_refuse(self):
        for change in ('missing', 'duplicate', 'extra'):
            candidate = copy.deepcopy(self.candidate)
            ids = candidate['original_member_ids']
            if change == 'missing':
                ids.pop()
            elif change == 'duplicate':
                ids[-1] = ids[0]
            else:
                ids.append('fabricated:additional-member')
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'exact original member selection differs'):
                reconcile.derive(self.original, self.matrix, candidate, self.inputs)

    def test_historical_route_or_effect_drift_refuses(self):
        matrix = copy.deepcopy(self.matrix)
        matrix['members'][0]['required_roles'] = ['role:repository-owner']
        with self.assertRaisesRegex(ValueError, 'historical member/owner metadata differs'):
            reconcile.derive(self.original, matrix, self.candidate, self.inputs)
        actual = reconcile.expected()
        actual['members'][0]['historical_effect_proposal_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'reconciliation differs'):
            reconcile.verify(reconcile.canonical(actual))

    def test_forged_owner_outcome_or_completion_refuses(self):
        for field, value in (('owner_outcome', 'admit'),
                             ('selected_successor_effect', {'operation': 'admit'}),
                             ('current_authority_evidence', {'principal': 'fabricated'})):
            actual = reconcile.expected()
            actual['members'][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'reconciliation differs'):
                reconcile.verify(reconcile.canonical(actual))
        actual = reconcile.expected()
        actual['original_member_dispositions_complete'] = True
        with self.assertRaisesRegex(ValueError, 'reconciliation differs'):
            reconcile.verify(reconcile.canonical(actual))

    def test_duplicate_key_and_noncanonical_bytes_refuse(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            reconcile.verify(b'{"schema_version":"a","schema_version":"b"}\n')
        raw = (reconcile.HERE / 'RECONCILIATION.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'reconciliation differs'):
            reconcile.verify(raw + b' ')

    def test_changed_or_linked_selected_source_refuses(self):
        relative, _ = reconcile.CANDIDATE
        with self.assertRaisesRegex(ValueError, 'selected source changed'):
            reconcile.selected((relative, '0' * 64))
        with tempfile.TemporaryDirectory(prefix='lab-t25-link-probe-') as temp:
            root = Path(temp)
            target = root / 'target.json'
            target.write_text('{}\n')
            (root / 'link').symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'linked selected source'):
                reconcile.selected(('link/target.json', reconcile.sha(target.read_bytes())), root)

    def test_frozen_symlink_refuses_without_following(self):
        with tempfile.TemporaryDirectory(prefix='lab-t25-frozen-link-') as name:
            root = Path(name)
            (root / 'RECONCILIATION.json').symlink_to(reconcile.HERE / 'RECONCILIATION.json')
            (root / 'RESULT.json').write_bytes(reconcile.read_frozen(reconcile.HERE / 'RESULT.json'))
            with patch.object(reconcile, 'HERE', root), self.assertRaisesRegex(ValueError, 'linked frozen evidence'):
                reconcile.cold_verify()
            (root / 'RECONCILIATION.json').unlink()
            (root / 'RECONCILIATION.json').write_bytes(reconcile.read_frozen(reconcile.HERE / 'RECONCILIATION.json'))
            (root / 'RESULT.json').unlink()
            (root / 'RESULT.json').symlink_to(reconcile.HERE / 'RESULT.json')
            with patch.object(reconcile, 'HERE', root), self.assertRaisesRegex(ValueError, 'linked frozen evidence'):
                reconcile.cold_verify()

    def test_repeat_write_mode_is_disabled_and_frozen_bytes_stay(self):
        paths = [reconcile.HERE / name for name in ('RECONCILIATION.json', 'RESULT.json')]
        before = [reconcile.sha(reconcile.read_frozen(path)) for path in paths]
        result = subprocess.run([sys.executable, '-B', str(reconcile.HERE / 'reconcile.py'), '--write'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('read-only', result.stderr)
        self.assertEqual(before, [reconcile.sha(reconcile.read_frozen(path)) for path in paths])


if __name__ == '__main__':
    unittest.main()
