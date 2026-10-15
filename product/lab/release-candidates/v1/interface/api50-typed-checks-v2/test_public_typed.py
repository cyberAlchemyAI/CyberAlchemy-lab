"""Actual public typed preparation, source/permission refusal and uncertainty."""
import copy
import importlib
import unittest
import uuid
from . import fixture

API = None
SOURCE = None
PROFILE = None


class PublicTypedChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.P = importlib.import_module(API + '.protocol')
        cls.Auth = importlib.import_module(API + '.auth')
        cls.W = importlib.import_module(API + '.workspace')
        cls.guard = importlib.import_module(API + '.guard')
        cls.guard.verify(SOURCE)
        cls.schemas = cls.P.Schemas(PROFILE)
        cls.manager = cls.P.source.replay_source('custody-participation')
        cls.view = cls.manager.__enter__()
        cls.original_projection = cls.P.compact(cls.view.data['projection'])
        cls.original_config = cls.P.compact(cls.view.data['config'])
        cls.observations = []

    @classmethod
    def tearDownClass(cls):
        assert cls.P.compact(cls.view.data['projection']) == cls.original_projection
        assert cls.P.compact(cls.view.data['config']) == cls.original_config
        cls.manager.__exit__(None, None, None)
        cls.guard.verify(SOURCE)
        cls.original_reader_guarded_exit_completed = True

    def example(self, **kwargs):
        return self.enterContext(fixture.example(API, self.view, self.schemas, **kwargs))

    def journal(self, host):
        return {p.name: p.read_bytes() for p in (host.vault.root / 'journal').glob('*') if p.is_file()}

    def invoke(self, host, request):
        raw = self.P.compact(request)
        reply = host.call(raw)
        self.W.privacy(reply)
        if 'kind' in reply:
            self.assertTrue(self.schemas.valid('api-reply', reply), reply)
            self.assertEqual(reply['request_binding']['sha256'], self.P.source.sha(raw))
        self.observations.append({'request': copy.deepcopy(request), 'reply': copy.deepcopy(reply)})
        return reply

    def test_01_exact_proposal_scope_refusal_and_zero_admission(self):
        host, call, selected = self.example()
        reply = self.invoke(host, call)
        self.assertEqual(reply['kind'], 'result', reply)
        self.assertEqual(reply['message'], selected['proposal'])
        self.assertEqual(reply['handler_binding']['ref'], str((self.P.HERE / 'typed_preparation.py').relative_to(self.P.ROOT)))
        reports = [self.P.frame_parse(p.read_bytes()) for p in (host.vault.root / 'objects').glob('*.json')]
        reports = [r for r in reports if r.get('schema_version') == 'lab-typed-host-preparation-checks/v1-candidate']
        self.assertEqual(len(reports), 1)
        checked = reports[0]
        self.assertFalse(checked['runtime_admission_authorized'])
        self.assertFalse(checked['operational_preparation_ready'])
        self.assertFalse(checked['genuine_semantic_owner_verdict_provided'])
        self.assertEqual(checked['postimage']['actual_transactions_written'], 0)
        self.assertEqual(checked['postimage']['scope_preparation']['actual_scope_refusal'], 'target outside authorized scope')
        self.assertIsNone(checked['actual_owner_outcome'])
        self.assertLess(self.Auth.now(), self.Auth.instant(call['deadline']))
        before = self.journal(host)
        retry = copy.deepcopy(call)
        retry['call_id'] = 'call:R03-typed-retry:' + uuid.uuid4().hex
        again = self.invoke(host, retry)
        self.assertEqual(again['kind'], 'result', again)
        self.assertEqual(again['message'], reply['message'])
        self.assertEqual(self.journal(host), before)

    def test_02_actor_spoof_refused_before_claim(self):
        host, call, _ = self.example()
        before = self.journal(host)
        call['message']['actor']['principal_ref'] = 'principal:untrusted-claim'
        reply = self.invoke(host, call)
        self.assertEqual(reply['message']['code'], 'unauthorized', reply)
        self.assertEqual(self.journal(host), before)

    def test_03_unselected_operation_refused_before_claim(self):
        host, call, _ = self.example(grant=False)
        before = self.journal(host)
        reply = self.invoke(host, call)
        self.assertEqual(reply['code'], 'unsupported-operation', reply)
        self.assertFalse(reply['effect_may_have_started'])
        self.assertEqual(self.journal(host), before)

    def test_04_changed_actual_route_refused_before_claim(self):
        host, call, selected = self.example()
        before = self.journal(host)
        path = host.vault.root / 'objects' / (selected['routing_binding']['sha256'] + '.json')
        original = path.read_bytes()
        try:
            path.write_bytes(original + b' ')
            reply = self.invoke(host, call)
            self.assertEqual(reply['code'], 'unauthenticated-channel', reply)
            self.assertFalse(reply['effect_may_have_started'])
            self.assertEqual(self.journal(host), before)
        finally:
            path.write_bytes(original)

    def test_05_incomplete_core_stays_pending(self):
        host, call, _ = self.example(mode='bad-core')
        reply = self.invoke(host, call)
        self.assertEqual(reply['message']['code'], 'indeterminate', reply)
        self.assertTrue(any(name.endswith('.claim.json') for name in self.journal(host)))
        self.assertFalse(any(name.endswith('.result.json') for name in self.journal(host)))
        retry = copy.deepcopy(call)
        retry['call_id'] = 'call:R03-typed-pending:' + uuid.uuid4().hex
        again = self.invoke(host, retry)
        self.assertEqual(again['message']['code'], 'recovery-required', again)

    def test_06_duplicate_schema_destination_refused_before_claim(self):
        host, call, _ = self.example(mode='duplicate-path')
        before = self.journal(host)
        reply = self.invoke(host, call)
        self.assertEqual(reply['message']['code'], 'invalid-contract', reply)
        self.assertEqual(self.journal(host), before)

    def test_07_review_covering_another_proposal_is_not_an_owner_verdict(self):
        host, call, _ = self.example(mode='bad-review')
        reply = self.invoke(host, call)
        self.assertEqual(reply['message']['code'], 'indeterminate', reply)
        self.assertFalse(any(name.endswith('.result.json') for name in self.journal(host)))

    def test_08_expired_call_refused_before_claim(self):
        host, call, _ = self.example()
        before = self.journal(host)
        call['deadline'] = '2000-01-01T00:00:00+00:00'
        reply = self.invoke(host, call)
        self.assertEqual(reply['message']['code'], 'deadline-exceeded', reply)
        self.assertEqual(self.journal(host), before)


    def test_09_mismatched_inspection_proposal_refused_before_claim(self):
        host, call, _ = self.example(mode='mismatched-proposal')
        before = self.journal(host)
        reply = self.invoke(host, call)
        self.assertEqual(reply['message']['code'], 'invalid-contract', reply)
        self.assertEqual(self.journal(host), before)
        self.assertLess(self.Auth.now(), self.Auth.instant(call['deadline']))

    def test_10_mismatched_inspection_successor_refused_before_claim(self):
        host, call, _ = self.example(mode='mismatched-successor')
        before = self.journal(host)
        reply = self.invoke(host, call)
        self.assertEqual(reply['message']['code'], 'invalid-contract', reply)
        self.assertEqual(self.journal(host), before)
        self.assertLess(self.Auth.now(), self.Auth.instant(call['deadline']))
