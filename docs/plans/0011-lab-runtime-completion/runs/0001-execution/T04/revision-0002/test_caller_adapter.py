"""Bounded caller tests over actual retained replies, not runtime qualification."""
import ast
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from caller_adapter import classify, result_message, CallerBoundaryError, OwnedOperation, RecoveryGate

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_sources():
    selected = json.loads((HERE / 'fixtures.json').read_bytes())['sources']
    loaded = {}
    for row in selected:
        raw = (ROOT / row['path']).read_bytes()
        if digest(raw) != row['sha256']:
            raise AssertionError('Selected historical fixture changed')
        loaded[row['path']] = json.loads(raw)
    return loaded


class CallerBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = pinned_sources()
        status = next(v for k, v in cls.sources.items() if k.endswith('base--lab-status.json'))
        cls.success = status['actual_calls'][1]['actual_reply']
        cls.actual_base_request = status['actual_calls'][1]['original_request']
        cls.domain_error = status['actual_calls'][0]['actual_reply']
        lifecycle = next(v for k, v in cls.sources.items() if k.endswith('member--Source8-lifecycle.json'))
        cls.expired = lifecycle['actual_calls'][5]['actual_reply']
        cls.uncertain_observation = next(v for k, v in cls.sources.items() if k.endswith('eba80d0686a6414f9231a75037502c73.json'))
        cls.uncertain = cls.uncertain_observation['actual_public_reply']
        cls.inspection_observation = next(v for k, v in cls.sources.items() if k.endswith('6d0852101b2e40ab8f7b4cd034e4d445.json'))
        cls.inspection = cls.inspection_observation['actual_public_reply']
        cls.snapshot_hashes = {(k, x['path']): x['sha256'] for k, v in cls.sources.items()
                              for x in v.get('durable_journal_snapshots', [])}
        for v in (cls.uncertain_observation, cls.inspection_observation):
            for row in v['durable_journal_snapshots']:
                if digest(base64.b64decode(row['base64_original_bytes'], validate=True)) != row['sha256']:
                    raise AssertionError('Original journal bytes differ')

    @classmethod
    def tearDownClass(cls):
        if pinned_sources() != cls.sources:
            raise AssertionError('Original retained source changed during tests')

    def recovery(self):
        claim_row = next(x for x in self.uncertain_observation['durable_journal_snapshots']
                         if x['path'].endswith('.claim.json') and
                         json.loads(base64.b64decode(x['base64_original_bytes']))['operation'] == 'proposal.review')
        claim = json.loads(base64.b64decode(claim_row['base64_original_bytes']))
        owned = OwnedOperation('proposal.review', 'fixture:review',
                               self.uncertain['trusted_context_binding']['ref'],
                               claim['principal_ref'], claim['original_call_binding']['sha256'],
                               self.uncertain_observation['owned_workspace_ref'])
        # The old observation retains a digest, not the original wire body.
        # This explicit derived client selection tests planning only; it is not
        # represented as the missing actual request or as current authentication.
        original = {'operation': owned.operation, 'idempotency_key': owned.idempotency_key,
                    'caller_context_ref': owned.context_ref, 'call_id': self.uncertain['call_id'],
                    'deadline': self.actual_base_request['deadline'],
                    'expected_contract_profile_binding': copy.deepcopy(self.uncertain['contract_profile_binding']),
                    'expected_source_cut': None, 'max_response_bytes': 1048576,
                    'schema_version': 'lab-api-call/v2-candidate',
                    'message': {'actor': {'principal_ref': owned.principal_ref, 'agent_instance_ref': None,
                                         'assignment_ref': None, 'session_ref': None, 'role_assignment_refs': []},
                                'budget': copy.deepcopy(self.actual_base_request['message']['budget'])}}
        context = {'context_ref': owned.context_ref, 'principal_ref': owned.principal_ref}
        # Explicit controlled raw-frame derivative. The historical worker12 wire
        # body was not retained, so this is never asserted to be its missing bytes.
        original['message']['request_ref'] = 'request:T04-derived-contrôle'
        raw = json.dumps(original, ensure_ascii=False, indent=2).encode('utf-8') + b'\n'
        owned = OwnedOperation(owned.operation, owned.idempotency_key, owned.context_ref,
                               owned.principal_ref, digest(raw), owned.workspace_ref)
        uncertain = copy.deepcopy(self.uncertain)
        uncertain['request_binding']['sha256'] = digest(raw)
        return owned, RecoveryGate(owned, uncertain), original, context, raw

    def derived_inspection(self, gate):
        # Controlled binding derivative, not a new actual historical API result.
        reply = copy.deepcopy(self.inspection)
        reply['message']['original_call_binding']['sha256'] = gate.owned.original_call_sha256
        return reply

    def test_01_actual_success_preserves_domain_message(self):
        before = copy.deepcopy(self.success)
        self.assertEqual(classify(self.success).state, 'completed')
        self.assertEqual(result_message(self.success, 'lab.status'), self.success['message'])
        self.assertEqual(self.success, before)

    def test_02_actual_domain_Actor_refusal_is_not_transport_or_no_effect_claim(self):
        decision = classify(self.domain_error)
        self.assertEqual((decision.state, decision.envelope, decision.code),
                         ('refused', 'domain-error', 'unauthorized'))
        self.assertIsNone(decision.effect_may_have_started)
        with self.assertRaises(CallerBoundaryError):
            result_message(self.domain_error, 'lab.status')

    def test_03_actual_expired_source8_transport_has_no_domain_message(self):
        self.assertNotIn('message', self.expired)
        self.assertEqual(classify(self.expired).state, 'refused-no-effect')
        with self.assertRaises(CallerBoundaryError) as raised:
            result_message(self.expired, 'lesson.select')
        self.assertEqual(raised.exception.decision.code, 'unauthenticated-channel')
        self.assertNotIsInstance(raised.exception, KeyError)
        self.assertFalse(raised.exception.decision.retry_allowed)

    def test_04_exact_successor_source8_guard_stops_before_items_index(self):
        tree = ast.parse((HERE / 'caller.py').read_bytes())
        episode = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'source8_episode')
        guard = next(n for n in ast.walk(episode) if isinstance(n, ast.Assign) and
                     any(isinstance(t, ast.Name) and t.id == 'selection_message' for t in n.targets))
        scope = {'result_message': result_message, 'selection': copy.deepcopy(self.expired)}
        with self.assertRaises(CallerBoundaryError):
            exec(compile(ast.fix_missing_locations(ast.Module(body=[guard], type_ignores=[])),
                         str(HERE / 'caller.py'), 'exec'), scope)
        self.assertNotIn('selection_message', scope)

    def test_05_actual_uncertain_domain_requires_inspect_and_forbids_retry(self):
        decision = classify(self.uncertain)
        self.assertEqual((decision.state, decision.code, decision.effect_may_have_started),
                         ('uncertain', 'indeterminate', True))
        self.assertEqual(decision.next_action, 'inspect-owned-operation-then-reconcile')
        self.assertFalse(decision.retry_allowed)
        with self.assertRaises(CallerBoundaryError):
            result_message(self.uncertain, 'proposal.review')

    def test_06_retained_journal_unchanged_during_controlled_raw_inspection(self):
        owned, gate, original, context, raw = self.recovery()
        with tempfile.TemporaryDirectory(prefix='.owned-case-', dir=HERE) as temporary:
            root = Path(temporary); root.chmod(0o700)
            for row in self.uncertain_observation['durable_journal_snapshots']:
                p = root / row['path']; p.parent.mkdir(exist_ok=True, mode=0o700)
                p.write_bytes(base64.b64decode(row['base64_original_bytes'])); p.chmod(0o600)
            foreign = root / 'foreign-owned-marker.json'; foreign.write_bytes(b'foreign fixture bytes'); foreign.chmod(0o600)
            before = {p.relative_to(root).as_posix(): digest(p.read_bytes()) for p in root.rglob('*') if p.is_file()}
            claims_before = len(list((root / 'journal').glob('*.claim.json')))
            planned = gate.inspection_call(original, context, call_id='call:T04-owned-inspection', original_raw=raw)
            self.assertEqual(planned['operation'], 'operation.inspect')
            result = gate.observe_inspection(self.derived_inspection(gate))
            self.assertEqual(result['state'], 'reconciliation-required')
            self.assertFalse(result['retry_allowed'])
            self.assertEqual(claims_before, 2)
            self.assertEqual(len(list((root / 'journal').glob('*.claim.json'))), claims_before)
            self.assertEqual({p.relative_to(root).as_posix(): digest(p.read_bytes()) for p in root.rglob('*') if p.is_file()}, before)
            self.assertEqual(foreign.read_bytes(), b'foreign fixture bytes')
        self.assertFalse(root.exists())

    def test_07_inspection_preserves_exact_key_profile_Actor_and_original_deadline(self):
        owned, gate, original, context, raw = self.recovery(); before = copy.deepcopy(original)
        planned = gate.inspection_call(original, context, call_id='call:T04-fresh-inspect', original_raw=raw)
        self.assertEqual(planned['message']['lookup'], {'operation': owned.operation, 'idempotency_key': owned.idempotency_key})
        self.assertIsNone(planned['idempotency_key'])
        for field in ['deadline', 'expected_contract_profile_binding', 'caller_context_ref', 'max_response_bytes']:
            self.assertEqual(planned[field], original[field])
        self.assertEqual(planned['message']['actor'], original['message']['actor'])
        self.assertEqual(original, before)

    def test_08_foreign_context_or_principal_cannot_select_inspection(self):
        for field in ['context_ref', 'principal_ref']:
            _, gate, original, context, raw = self.recovery(); context[field] = 'foreign'
            with self.assertRaises(ValueError):
                gate.inspection_call(original, context, call_id='call:T04-inspect', original_raw=raw)
            self.assertFalse(gate.retry_allowed)

    def test_09_changed_operation_or_key_cannot_select_inspection(self):
        for field in ['operation', 'idempotency_key', 'caller_context_ref']:
            _, gate, original, context, raw = self.recovery(); original[field] = 'foreign'
            with self.assertRaises(ValueError):
                gate.inspection_call(original, context, call_id='call:T04-inspect', original_raw=raw)

    def test_10_foreign_original_digest_is_rejected(self):
        _, gate, original, context, raw = self.recovery(); gate.inspection_call(original, context, call_id='call:T04-inspect', original_raw=raw)
        reply = self.derived_inspection(gate); reply['message']['original_call_binding']['sha256'] = '0' * 64
        with self.assertRaises(ValueError):gate.observe_inspection(reply)
        self.assertFalse(gate.retry_allowed)

    def test_11_no_unplanned_inspection_can_close_uncertainty(self):
        _, gate, _, _, _ = self.recovery()
        with self.assertRaises(ValueError):gate.observe_inspection(self.inspection)

    def test_12_inspection_not_found_never_authorizes_original_retry(self):
        _, gate, original, context, raw = self.recovery(); gate.inspection_call(original, context, call_id='call:T04-inspect', original_raw=raw)
        refusal = copy.deepcopy(self.domain_error); refusal['message']['code'] = 'not-found'
        with self.assertRaises(CallerBoundaryError):gate.observe_inspection(refusal)
        self.assertFalse(gate.retry_allowed)

    def test_13_unknown_or_malformed_reply_is_bounded_no_KeyError(self):
        for reply in [None, [], {}, {'kind': 'result'}, {'kind': 'result', 'message': None}, {'kind': 'other'}]:
            with self.assertRaises(CallerBoundaryError) as raised:result_message(reply, 'lesson.select')
            self.assertNotIsInstance(raised.exception, KeyError)
            self.assertLess(len(str(raised.exception)), 220)

    def test_14_public_diagnostics_do_not_forward_unknown_private_error_text(self):
        reply = copy.deepcopy(self.domain_error)
        reply['message'].update(code='secret-test-credential', message='PRIVATE KEY controlled marker')
        with self.assertRaises(CallerBoundaryError) as raised:result_message(reply, 'lesson.select')
        self.assertNotIn('secret-test-credential', str(raised.exception))
        self.assertNotIn('PRIVATE KEY', str(raised.exception))

    def test_15_completed_inspection_still_has_no_retry_authority(self):
        # Explicit transformed branch fixture, not an asserted retained success.
        _, gate, original, context, raw = self.recovery(); gate.inspection_call(original, context, call_id='call:T04-inspect', original_raw=raw)
        reply = self.derived_inspection(gate); reply['message'].update(posture='completed', reconciliation_required=False)
        self.assertEqual(gate.observe_inspection(reply)['state'], 'observed-completed')
        self.assertFalse(gate.retry_allowed)

    def test_16_claimed_retry_permission_or_inconsistent_posture_is_refused(self):
        for change in [{'retry_allowed': True}, {'reconciliation_required': False}, {'posture': 'not-found'}]:
            _, gate, original, context, raw = self.recovery(); gate.inspection_call(original, context, call_id='call:T04-inspect', original_raw=raw)
            reply = self.derived_inspection(gate); reply['message'].update(change)
            with self.assertRaises(ValueError):gate.observe_inspection(reply)
            self.assertFalse(gate.retry_allowed)

    def test_17_reply_is_recorded_before_positive_boundary_exception(self):
        tree = ast.parse((HERE / 'caller.py').read_bytes())
        body = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'invoke').body
        record = next(i for i, n in enumerate(body) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                      and isinstance(n.value.func, ast.Attribute) and isinstance(n.value.func.value, ast.Name)
                      and n.value.func.value.id == 'CASES' and n.value.func.attr == 'append')
        boundary = next(i for i, n in enumerate(body) if isinstance(n, ast.If) and
                        any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == 'CallerBoundaryError' for x in ast.walk(n)))
        self.assertLess(record, boundary)
        names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
        self.assertIn('preserve_pending', names)
        self.assertIn('inspect_uncertain', names)

    def test_18_adapter_has_no_effect_dispatch_or_cleanup_callback(self):
        tree = ast.parse((HERE / 'caller_adapter.py').read_bytes())
        names = [n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)]
        self.assertNotIn('dispatch', names)
        self.assertNotIn('rmtree', names)
        self.assertNotIn('close', names)
        self.assertNotIn('unlink', names)


    def test_19_missing_historical_raw_bytes_cannot_be_reconstructed_from_digest(self):
        owned, _, original, context, _ = self.recovery()
        historical = OwnedOperation(owned.operation, owned.idempotency_key, owned.context_ref,
                                    owned.principal_ref, self.uncertain['request_binding']['sha256'],
                                    owned.workspace_ref)
        gate = RecoveryGate(historical, self.uncertain)
        with self.assertRaises(ValueError):
            gate.inspection_call(original, context, call_id='call:T04-missing-raw', original_raw=None)
        self.assertEqual(gate.state, 'inspection-required')
        self.assertEqual(self.inspection['message']['original_call_binding']['sha256'],
                         self.uncertain['request_binding']['sha256'])

    def test_20_original_whitespace_and_UTF8_bytes_are_bound_without_reencoding(self):
        owned, gate, original, context, raw = self.recovery()
        before = bytes(raw)
        self.assertIn(b'\n', raw)
        self.assertIn('contrôle'.encode('utf-8'), raw)
        compact = json.dumps(original, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        self.assertNotEqual(digest(raw), digest(compact))
        planned = gate.inspection_call(original, context, call_id='call:T04-whitespace', original_raw=raw)
        self.assertEqual(gate.owned.original_call_sha256, digest(before))
        self.assertEqual(raw, before)
        self.assertEqual(planned['deadline'], original['deadline'])
        self.assertEqual(planned['message']['budget'], original['message']['budget'])

    def test_21_semantically_equal_reencoded_original_frame_is_refused(self):
        _, gate, original, context, raw = self.recovery()
        rewritten = json.dumps(original, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        with self.assertRaises(ValueError):
            gate.inspection_call(original, context, call_id='call:T04-reencoded', original_raw=rewritten)
        self.assertEqual(gate.state, 'inspection-required')
        self.assertFalse(gate.retry_allowed)

    def test_22_altered_budget_is_causally_refused_against_original_frame(self):
        _, gate, original, context, raw = self.recovery()
        original['message']['budget']['max_actions'] += 1
        with self.assertRaisesRegex(ValueError, 'parsed controls differ'):
            gate.inspection_call(original, context, call_id='call:T04-budget', original_raw=raw)
        self.assertEqual(gate.state, 'inspection-required')

    def test_23_altered_outer_deadline_is_refused(self):
        _, gate, original, context, raw = self.recovery(); original['deadline'] = '2099-01-01T00:00:00+00:00'
        with self.assertRaisesRegex(ValueError, 'parsed controls differ'):
            gate.inspection_call(original, context, call_id='call:T04-deadline', original_raw=raw)

    def test_24_altered_inner_deadline_is_refused(self):
        _, gate, original, context, raw = self.recovery()
        original['message']['budget']['deadline'] = '2099-01-01T00:00:00+00:00'
        with self.assertRaisesRegex(ValueError, 'parsed controls differ'):
            gate.inspection_call(original, context, call_id='call:T04-inner-deadline', original_raw=raw)

    def test_25_altered_profile_binding_is_refused(self):
        _, gate, original, context, raw = self.recovery()
        original['expected_contract_profile_binding']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'parsed controls differ'):
            gate.inspection_call(original, context, call_id='call:T04-profile', original_raw=raw)

    def test_26_other_Actor_membership_changes_are_refused(self):
        for field, value in [('agent_instance_ref', 'agent-instance:foreign'),
                             ('session_ref', 'session:foreign'),
                             ('role_assignment_refs', ['role-assignment:foreign'])]:
            with self.subTest(field=field):
                _, gate, original, context, raw = self.recovery(); original['message']['actor'][field] = value
                with self.assertRaisesRegex(ValueError, 'parsed controls differ'):
                    gate.inspection_call(original, context, call_id='call:T04-Actor', original_raw=raw)
                self.assertFalse(gate.retry_allowed)

    def test_27_boolean_does_not_masquerade_as_equal_integer_budget(self):
        _, gate, original, context, raw = self.recovery()
        original['message']['budget']['max_actions'] = False  # Python False == 0.
        with self.assertRaisesRegex(ValueError, 'parsed controls differ'):
            gate.inspection_call(original, context, call_id='call:T04-budget-type', original_raw=raw)

    def test_28_uncertain_reply_from_other_original_call_cannot_create_gate(self):
        owned, _, _, _, _ = self.recovery()
        # Real historical reply belongs to its own old raw digest, not derived raw.
        with self.assertRaisesRegex(ValueError, 'not bound'):
            RecoveryGate(owned, self.uncertain)

    def test_29_strict_raw_parser_refuses_duplicates_and_nonfinite_JSON(self):
        from caller_adapter import verify_original_frame
        for raw in [b'{"x": 1, "x": 1}', b'{"x": NaN}']:
            with self.subTest(raw_kind='duplicate' if b'NaN' not in raw else 'nonfinite'):
                with self.assertRaisesRegex(ValueError, 'strict bounded JSON'):
                    verify_original_frame(raw, digest(raw), {'x': 1})

    def test_30_nonbyte_oversized_and_one_byte_changed_original_frames_refuse(self):
        _, gate, original, context, raw = self.recovery()
        for changed in [bytearray(raw), raw + b' ', b' ' * 1048577]:
            with self.subTest(kind=type(changed).__name__, length=len(changed)):
                with self.assertRaisesRegex(ValueError, 'digest or bounded byte input differs'):
                    gate.inspection_call(original, context, call_id='call:T04-frame', original_raw=changed)
                self.assertEqual(gate.state, 'inspection-required')

    def test_31_successor_passes_captured_raw_not_a_regenerated_request(self):
        tree = ast.parse((HERE / 'caller.py').read_bytes())
        inspection = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'inspect_uncertain')
        args = [n for n in ast.walk(inspection) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == 'inspection_call']
        self.assertEqual(len(args), 1)
        raw_arg = next(k.value for k in args[0].keywords if k.arg == 'original_raw')
        self.assertIsInstance(raw_arg, ast.Name)
        self.assertEqual(raw_arg.id, 'original_raw')
        invoke = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'invoke')
        forwarding = next(n for n in ast.walk(invoke) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                          and n.func.id == 'inspect_uncertain')
        self.assertEqual(forwarding.args[-1].id, 'raw')


if __name__ == '__main__':
    unittest.main(verbosity=2)
