import importlib.util
import json
import unittest
from pathlib import Path

PATH = Path(__file__).with_name('preflight.py')
spec = importlib.util.spec_from_file_location('t08_current_preflight_review', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def packed(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


class PreflightTests(unittest.TestCase):
    def sample(self):
        profile = {'files': [{'path': 'b', 'sha256': 'b' * 64}],
                   'external_execution_dependency_bindings': [{'path': 'c', 'sha256': 'c' * 64}]}
        profile_raw = packed(profile)
        source = {'profile_binding': {'path': module.API + '/contract-profile.json',
                                      'sha256': module.sha(profile_raw)},
                  'files': [{'path': 'a', 'sha256': 'a' * 64}]}
        return source, profile

    def run_selected(self, source, profile):
        source_raw, profile_raw = packed(source), packed(profile)
        return module.inspect(source_raw, profile_raw, module.sha(source_raw), module.sha(profile_raw))

    def test_exact_ordered_rows_only_no_physical_claim(self):
        source, profile = self.sample()
        result = self.run_selected(source, profile)
        self.assertEqual(result['ordered_proof_occurrences_required'], 3)
        self.assertEqual(result['physical_rows_verified'], 0)
        self.assertFalse(result['protected_reader_boundary_executed'])

    def test_changed_profile_pin_and_duplicate_row_refuse(self):
        source, profile = self.sample()
        raw_source, raw_profile = packed(source), packed(profile)
        with self.assertRaisesRegex(ValueError, 'pin differs'):
            module.inspect(raw_source, raw_profile, module.sha(raw_source), '0' * 64)
        source['files'].append(source['files'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate path'):
            self.run_selected(source, profile)

    def test_old_profile_origin_and_unsafe_path_refuse(self):
        source, profile = self.sample()
        source['profile_binding']['path'] = 'product/lab/release-candidates/v1/interface/api-integration-v16/contract-profile.json'
        with self.assertRaisesRegex(ValueError, 'binding differs'):
            self.run_selected(source, profile)
        source, profile = self.sample()
        profile['files'][0]['path'] = '../b'
        source['profile_binding']['sha256'] = module.sha(packed(profile))
        with self.assertRaisesRegex(ValueError, 'noncanonical'):
            self.run_selected(source, profile)


if __name__ == '__main__':
    unittest.main()
