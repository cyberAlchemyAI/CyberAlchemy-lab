"""Original full metadata, causal accounting refusals and no-follow identities."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

import accounting as A

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/accounting-0001'


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def inputs():
    source = (RUN / 'original-source-manifest.json').read_bytes()
    profile = (RUN / 'original-contract-profile.json').read_bytes()
    missing = (RUN / 'unavailable-original-inputs.json').read_bytes()
    original = json.loads(source)['files']
    absent = {r['binding']['path'] for r in json.loads(missing)['rows']}
    selected = {'schema_version': A.VERSION, 'source_sha256': A.SOURCE_SHA,
                'profile_sha256': A.PROFILE_SHA, 'unavailable_sha256': A.UNAVAILABLE_SHA,
                'additions': [], 'consumption': [
                    {'binding': r, 'status': 'historical-metadata-only' if r['path'] in absent else 'required-current-byte',
                     'basis': 'Metadata accounting observation only; actual callback/byte closure independently required.'}
                    for r in original], 'authority_effect': 'none',
                'claim_ceiling': 'Complete original metadata and identities only; no current runtime or original physical PASS.'}
    current = [r for r in original if r['path'] not in absent]
    return source, profile, missing, selected, current


class AccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = inputs()

    def setUp(self):
        self.source, self.profile, self.missing, self.selection, self.current = copy.deepcopy(self.baseline)

    def verify(self):
        raw = encoded(self.selection)
        return A.verify(self.source, self.profile, self.missing, A.UNAVAILABLE_SHA,
                        raw, A.sha(raw), self.current, ROOT)

    def test_01_actual_full_original_metadata_preserved(self):
        report = self.verify()
        self.assertEqual(report['original_source_files'], json.loads(self.source)['files'])
        self.assertEqual(report['original_profile_files'], json.loads(self.profile)['files'])
        self.assertEqual(len(report['dispositions']), 24497)
        self.assertEqual(report['unavailable_original_count'], 25)
        self.assertEqual(report['historical_original_physical_closure'], 'REFUSED')
        self.assertFalse(report['input_bodies_read_or_exported'])
        self.assertEqual(report['current_execution_byte_guard'], 'REQUIRED-SEPARATE-NOT-RUN-BY-ACCOUNTING')

    def test_02_omitted_present_row(self):
        self.current.pop()
        with self.assertRaisesRegex(A.Refusal, 'omitted/reordered'):
            self.verify()

    def test_03_reordered_current_rows(self):
        self.current[0], self.current[1] = self.current[1], self.current[0]
        with self.assertRaisesRegex(A.Refusal, 'omitted/reordered'):
            self.verify()

    def test_04_current_hash_substitution(self):
        self.current[0] = dict(self.current[0], sha256='0' * 64)
        with self.assertRaisesRegex(A.Refusal, 'substituted'):
            self.verify()

    def test_05_duplicate_current_row(self):
        self.current.append(self.current[0])
        with self.assertRaisesRegex(A.Refusal, 'duplicate'):
            self.verify()

    def test_06_unknown_current_row_field(self):
        self.current[0] = dict(self.current[0], classification='metadata')
        with self.assertRaisesRegex(A.Refusal, 'closed'):
            self.verify()

    def test_07_original_table_row_or_order_change(self):
        original = json.loads(self.source)
        original['files'][0], original['files'][1] = original['files'][1], original['files'][0]
        self.source = encoded(original)
        with self.assertRaisesRegex(A.Refusal, 'pin differs'):
            self.verify()

    def test_08_original_profile_change(self):
        self.profile += b' '
        with self.assertRaisesRegex(A.Refusal, 'pin differs'):
            self.verify()

    def test_09_exact_missing_hash_or_classification_change(self):
        missing = json.loads(self.missing)
        missing['rows'][0]['binding']['sha256'] = '0' * 64
        self.missing = encoded(missing)
        with self.assertRaisesRegex(A.Refusal, 'pin differs'):
            self.verify()

    def test_10_caller_reselects_arbitrary_25_missing_rows(self):
        missing = json.loads(self.missing)
        missing['rows'][0]['classification'] = 'public'
        raw = encoded(missing)
        with self.assertRaisesRegex(A.Refusal, 'exact independently reviewed'):
            A.verify(self.source, self.profile, raw, A.sha(raw), encoded(self.selection),
                     A.sha(encoded(self.selection)), self.current, ROOT)

    def test_11_undeclared_execution_input(self):
        self.current.append({'path': 'undeclared-technical-file', 'sha256': '0' * 64})
        with self.assertRaisesRegex(A.Refusal, 'undeclared'):
            self.verify()

    def test_12_missing_consumption_status(self):
        self.selection['consumption'].pop()
        with self.assertRaisesRegex(A.Refusal, 'complete consumed'):
            self.verify()

    def test_13_unavailable_body_consumed_by_callback(self):
        entry = next(r for r in self.selection['consumption'] if r['status'] == 'historical-metadata-only')
        entry['status'] = 'required-unavailable-byte'
        entry['basis'] = 'Selected native/source/schema callback actually consumes this unavailable body.'
        with self.assertRaisesRegex(A.Refusal, 'required by selected callback'):
            self.verify()

    def test_14_present_parent_demoted_to_metadata(self):
        self.selection['consumption'][0]['status'] = 'historical-metadata-only'
        with self.assertRaisesRegex(A.Refusal, 'present original/addition excluded'):
            self.verify()

    def test_15_consumption_reordered(self):
        self.selection['consumption'][0], self.selection['consumption'][1] = self.selection['consumption'][1], self.selection['consumption'][0]
        with self.assertRaisesRegex(A.Refusal, 'row/order/type'):
            self.verify()

    def test_16_unknown_addition_or_alias(self):
        self.selection['additions'] = [{'binding': self.current[0], 'classification': 'successor-code', 'selection_reason': 'fake alias'}]
        with self.assertRaisesRegex(A.Refusal, 'aliases'):
            self.verify()
        self.selection['additions'][0]['classification'] = 'public-provenance-pass'
        with self.assertRaisesRegex(A.Refusal, 'unknown/unexplained'):
            self.verify()

    def test_17_independent_selection_pin(self):
        raw = encoded(self.selection)
        with self.assertRaisesRegex(A.Refusal, 'pin differs'):
            A.verify(self.source, self.profile, self.missing, A.UNAVAILABLE_SHA,
                     raw, '0' * 64, self.current, ROOT)

    def test_18_duplicate_and_nonfinite_json(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}'):
            with self.assertRaises(A.Refusal):
                A.parse(raw)

    def test_19_absence_rechecked_if_restored(self):
        with tempfile.TemporaryDirectory(dir=RUN) as temp:
            path = Path(temp) / 'absent'
            probe = A.AnchoredPresence(ROOT)
            try:
                probe.inspect({'path': str(path), 'sha256': '0' * 64}, unavailable=True)
                path.write_bytes(b'technical bytes')
                with self.assertRaisesRegex(A.Refusal, 'restored during'):
                    probe.finish()
            finally:
                probe.close()

    def test_20_restored_or_existing_missing_identity_refused(self):
        with tempfile.TemporaryDirectory(dir=RUN) as temp:
            path = Path(temp) / 'exists'; path.write_bytes(b'technical bytes')
            probe = A.AnchoredPresence(ROOT)
            try:
                with self.assertRaisesRegex(A.Refusal, 'exists or was restored'):
                    probe.inspect({'path': str(path), 'sha256': A.sha(path.read_bytes())}, unavailable=True)
            finally:
                probe.close()

    def test_21_symlink_ancestor_and_unreadable_refused(self):
        with tempfile.TemporaryDirectory(dir=RUN) as temp:
            root = Path(temp); (root / 'dir').mkdir(); (root / 'link').symlink_to(root / 'dir')
            path = root / 'unreadable'; path.write_bytes(b'x'); path.chmod(0)
            for name in (root / 'link' / 'absent', path):
                probe = A.AnchoredPresence(ROOT)
                try:
                    with self.assertRaisesRegex(A.Refusal, 'unsafe/unreadable'):
                        probe.inspect({'path': str(name), 'sha256': '0' * 64}, unavailable=True)
                finally:
                    probe.close()
            path.chmod(0o600)

    def test_22_directory_attachment_replaced(self):
        with tempfile.TemporaryDirectory(dir=RUN) as temp:
            root = Path(temp); (root / 'dir').mkdir()
            probe = A.AnchoredPresence(ROOT)
            try:
                probe.inspect({'path': str(root / 'dir' / 'absent'), 'sha256': '0' * 64}, unavailable=True)
                (root / 'dir').rename(root / 'old'); (root / 'dir').mkdir()
                with self.assertRaisesRegex(A.Refusal, 'attachment changed'):
                    probe.finish()
            finally:
                probe.close()

    def test_23_current_file_identity_replaced(self):
        with tempfile.TemporaryDirectory(dir=RUN) as temp:
            path = Path(temp) / 'current'; path.write_bytes(b'x')
            probe = A.AnchoredPresence(ROOT)
            try:
                probe.inspect({'path': str(path), 'sha256': '0' * 64}, unavailable=False)
                path.unlink(); path.write_bytes(b'y')
                with self.assertRaisesRegex(A.Refusal, 'identity changed'):
                    probe.finish()
            finally:
                probe.close()

    def test_24_exact_addition_and_complete_consumption(self):
        with tempfile.TemporaryDirectory(dir=RUN) as temp:
            path = Path(temp) / 'selected'; path.write_bytes(b'owned technical dependency')
            binding = {'path': str(path), 'sha256': A.sha(path.read_bytes())}
            self.selection['additions'] = [{'binding': binding, 'classification': 'host-dependency',
                                            'selection_reason': 'Owned technical addition coverage, not actual host ABI qualification.'}]
            self.selection['consumption'].append({'binding': binding, 'status': 'required-current-byte', 'basis': 'Exact independently selected technical byte input.'})
            self.current.append(binding)
            report = self.verify()
            self.assertEqual(report['current_guard_files'][-1], binding)


if __name__ == '__main__':
    unittest.main(verbosity=2)
