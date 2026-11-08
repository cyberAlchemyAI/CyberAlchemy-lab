"""Focused source-selection checks for the current T12 governance member."""

import importlib
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[4]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
API = INTERFACE / 'api-integration-v76-current-repairs-0001'
GOVERNANCE = INTERFACE / 'api-governance-integration-v5-current-t12-0001'
sys.path.insert(0, str(INTERFACE))
D = importlib.import_module(GOVERNANCE.name + '.dependencies')


class CurrentT12GovernanceMember(unittest.TestCase):
    def test_selected_member_and_current_native_source(self):
        member = json.loads((API / 'integration-members.json').read_bytes())['members']['governance']
        self.assertEqual(member, {
            'directory': GOVERNANCE.name,
            'operations': ['checkpoint.resolve', 'admission.apply', 'capability.adoption.prepare'],
            'profile_sha256': D.sha((GOVERNANCE / 'contract-profile.json').read_bytes()),
            'source_sha256': D.sha((GOVERNANCE / 'source-manifest.json').read_bytes()),
        })
        D.guard(member['source_sha256'])
        profile = json.loads((D.NATIVE / 'profile.json').read_bytes())
        self.assertEqual(profile['current_selection']['history_cursor'], 7)
        self.assertEqual(profile['current_selection']['bundle_path'],
                         'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/bundle.json')

    def test_stale_or_foreign_governance_source_refused(self):
        member = json.loads((API / 'integration-members.json').read_bytes())['members']['governance']
        self.assertNotEqual(member['directory'], 'api-governance-integration-v4')
        with self.assertRaises(Exception):
            D.guard('ff7c71a891276dbdbf81f3997e79bf3b486611fb13f1cff374e5986e9ce3b415')
        with self.assertRaises(Exception):
            D.guard('0' * 64)


if __name__ == '__main__':
    unittest.main()
