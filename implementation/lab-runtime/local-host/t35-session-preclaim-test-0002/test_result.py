import hashlib
import importlib.util
import json
from datetime import datetime
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v33-t35-session-preflight-0002'
OBS = ROOT / 'implementation/lab-runtime/local-host/t35-phase-observer-session-preflight-0002'
BUILD = ROOT / 'implementation/lab-runtime/local-host/t35-api33-session-preflight-rebind-0002/build.py'
RUNNER_SHA = '5969048a092787a73492ec4bfbf4b34fe4842b668aad5d1eb5b4682c06b12803'
RESULT_SHA = '5956408d7afc8bc3242244cd9d47e536d1e880355020448c0c529634dcff20df'
MANIFEST_SHA = '094d456fb4cddca37a83b03f1562b26afc3527d98d4bede752a69a0f63b7884f'
SELECTION_SHA = '83239f99116e2fe02142534a3c14e5d57d1946be0d2e9cabce000b2249a335f6'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def loaded(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PreclaimReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((HERE / 'RESULT.json').read_bytes())

    def test_pinned_product_and_observer_closure(self):
        self.assertEqual(sha(HERE / 'run.py'), RUNNER_SHA)
        self.assertEqual(sha(HERE / 'RESULT.json'), RESULT_SHA)
        self.assertEqual(sha(API / 'source-manifest.json'), MANIFEST_SHA)
        self.assertEqual(self.result['runner_sha256'], RUNNER_SHA)
        self.assertEqual(self.result['selected_api_source_manifest_sha256'], MANIFEST_SHA)
        observer = loaded('_cal_t35_preclaim_observer_test', OBS / 'observe.py')
        selected = observer.verify_boundary_selection(OBS / 'selected-boundaries.json', SELECTION_SHA, ROOT)
        self.assertEqual(len(selected), 15)
        self.assertEqual(self.result['selected_boundary_selection_sha256'], SELECTION_SHA)
        with patch.object(observer, 'API_SOURCE_SHA256', '0' * 64):
            with self.assertRaisesRegex(observer.BoundaryRefusal, 'BOUNDARY_SELECTION_CONTRACT_REFUSED'):
                observer.verify_boundary_selection(OBS / 'selected-boundaries.json', SELECTION_SHA, ROOT)

    def test_actual_causal_refusals_and_clocks(self):
        r = self.result
        self.assertEqual(r['schema_version'], 'lab-T35-current-source8-session-preclaim-refusal/v1')
        self.assertEqual([(c['operation'], c['reply_kind']) for c in r['calls']],
                         [('context.get', 'result'), ('session.open', 'error'), ('session.open', 'error')])
        self.assertEqual(r['missing_native_contract_error_code'], 'unresolved-reference')
        self.assertTrue(r['missing_native_contract_refused_before_claim'])
        self.assertEqual(r['vault_claim_calls_for_missing_contract'], 0)
        self.assertTrue(r['owned_journal_unchanged_for_missing_contract'])
        self.assertTrue(r['expired_request_refused_without_live_or_journal_effect'])
        self.assertTrue(r['owned_temporary_fixture_removed'])
        self.assertEqual(r['authority_effect'], 'none')
        obs = r['observation']
        self.assertEqual((obs['callback_count'], obs['pure_scope_boundary_count']), (4, 0))
        self.assertEqual([e['name'] for e in obs['events']],
                         ['Service.call', 'ContextSessions.delivery', 'Service.call', 'Service.call'])
        source_end = datetime.fromisoformat(r['source_period_expires_at'])
        reader_end = datetime.fromisoformat(r['reader_lease_expires_at'])
        for event in obs['events']:
            start = datetime.fromisoformat(event['started_at_utc'])
            end = datetime.fromisoformat(event['completed_at_utc'])
            self.assertEqual(event['status'], 'PASS')
            self.assertTrue(start <= end < min(source_end, reader_end))
            self.assertAlmostEqual((end-start).total_seconds(), event['monotonic_elapsed_seconds'], delta=0.05)

    def test_wrong_service_edit_refuses(self):
        builder = loaded('_cal_t35_preclaim_builder_test', BUILD)
        old = (builder.OLD / 'service.py').read_bytes()
        new = (builder.NEW / 'service.py').read_bytes()
        builder.verify_service_edit(old, new)
        with self.assertRaisesRegex(ValueError, 'sole service change'):
            builder.verify_service_edit(old, old)
        with self.assertRaisesRegex(ValueError, 'sole service change'):
            builder.verify_service_edit(old, new + b'\n# unrelated mutation\n')


if __name__ == '__main__':
    unittest.main()
