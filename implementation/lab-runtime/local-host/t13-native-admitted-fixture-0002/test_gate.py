"""Cold contract tests; native sealing/appending is exercised by run.py."""
import copy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

import gate
import run


def fixture():
    rows, events, bodies, observed = [], [], [], []
    for position in range(1, 89):
        semantic = {'semantic_event_id': 'fixture:semantic:' + str(position),
                    'semantic_event_digest': str(position).zfill(64),
                    'semantic_cursor': position}
        predecessor = {'event_id': 'fixture:predecessor:' + str(position),
                       'event_digest': str(position + 100).zfill(64),
                       'governance_cursor': position}
        stream = 'fixture:T13:stream:' + str(position)
        row = {'position': position, 'member_ref': 'fixture:T13:member:' + str(position),
               'intent_binding': {'path': 'fixture/T13/intent/' + str(position),
                                  'sha256': str(position + 200).zfill(64)},
               'predecessor_governance_tuple': predecessor,
               'predecessor_stream_id': stream, 'expected_stream_version': 1,
               'semantic_tuple': semantic,
               'draft_event_id': 'fixture:T13:inert-governance:' + str(position),
               'draft_governance_cursor': 88 + position,
               'actual_owner_Decision_binding': None, 'authority_effect': 'none'}
        event = {'source_kind': 'canonical_event', 'event_family': 'governance',
                 'event_id': row['draft_event_id'], 'event_digest': gate.ZERO,
                 'stream_id': stream, 'semantic_ref': semantic,
                 'governance_cursor': 88 + position,
                 'previous_event_digest': predecessor['event_digest'],
                 'complete_resulting_governance_state': {
                     'semantic_ref': semantic, 'authority_effect': 'none',
                     'candidate_or_maturity_status': 'admitted-representation',
                     'promotion_state_or_handle': gate.FIXTURE_PROMOTION,
                     'authority_kind_and_posture': {
                         'kind': 'ontology-representation',
                         'posture': 'synthetic-fixture-no-governing-authority'},
                     'owner_route': gate.FIXTURE_OWNER,
                     'challenge_contract': {'owner_route': gate.FIXTURE_OWNER},
                     'provenance': [gate.admitted_marker(row)]}}
        digest = gate.sha(gate.encoded(event) + b'\n')
        event['event_digest'] = digest
        rows.append(row)
        events.append(event)
        bodies.append(gate.encoded(event) + b'\n')
        observed.append({**predecessor, 'stream_id': stream})
    plan = gate.fixed_plan(rows, events, bodies, account_sha='a' * 64,
                           archive_sha='b' * 64, native_sha='c' * 64)
    key = Ed25519PrivateKey.generate()
    now = datetime.now(timezone.utc)
    public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
    ctx = gate.context(public, now)
    payload = gate.response_payload(plan, ctx, now.isoformat(),
                                    (now + timedelta(minutes=5)).isoformat())
    response = gate.encoded({'payload': payload,
        'signature_hex': key.sign(gate.RESPONSE_DOMAIN + gate.encoded(payload)).hex()})
    decision = gate.encoded(gate.decision(plan, ctx, response)) + b'\n'
    witness = gate.encoded(gate.witness(plan, ctx, response, decision)) + b'\n'
    return (rows, events, bodies, observed, plan, ctx, response, decision,
            witness, now, copy.deepcopy(observed), key)


class GateTests(unittest.TestCase):
    def verify(self, values):
        return gate.verify_bundle(*values[:10], expected_originals=values[10])

    def test_exact_signed_88_and_deterministic_external_records(self):
        values = fixture()
        self.assertTrue(self.verify(values))

    def test_original88_inert_drafts_become_separate_admitted_fixture(self):
        module = run.selected_append().selected_preparation()
        account = module.parse(module.exact(module.ACCOUNT, module.ACCOUNT_SHA))
        snapshot = module.parse(module.exact(module.ARCHIVE, module.ARCHIVE_SHA))
        original, rows = module.prepare(account, snapshot)
        admitted = gate.admitted_drafts(original, rows)
        self.assertEqual(len(admitted), 88)
        self.assertEqual(sum(d['complete_resulting_governance_state']
                             ['candidate_or_maturity_status'] == 'admitted-representation'
                             for d in admitted), 88)
        self.assertTrue(all(d['complete_resulting_governance_state']['authority_effect'] == 'none'
                            for d in admitted))
        self.assertTrue(all(d['complete_resulting_governance_state']['provenance'][-1] ==
                            gate.admitted_marker(row)
                            for d, row in zip(admitted, rows)))
        self.assertEqual({d['complete_resulting_governance_state']['provenance'][-1]
                          ['source_ref'] for d in admitted}, {gate.FIXTURE_DECISION})
        self.assertTrue(all(d['complete_resulting_governance_state']
                            ['candidate_or_maturity_status'] == 'candidate-unadmitted'
                            for d in original))

    def test_signed_wrong_target_commitment_refuses(self):
        values = list(fixture())
        payload = copy.deepcopy(gate.parse(values[6])['payload'])
        payload['plan_byte_sha256'] = 'f' * 64
        key = values[-1]
        values[6] = gate.encoded({'payload': payload,
            'signature_hex': key.sign(gate.RESPONSE_DOMAIN + gate.encoded(payload)).hex()})
        with self.assertRaises(ValueError):
            self.verify(values)

    def test_changed_sealed_target_refuses(self):
        values = list(fixture())
        values[2] = list(values[2])
        values[2][0] += b' '
        with self.assertRaises(ValueError):
            self.verify(values)

    def test_changed_observed_predecessor_refuses(self):
        values = list(fixture())
        values[3] = copy.deepcopy(values[3])
        values[3][0]['event_digest'] = 'f' * 64
        with self.assertRaises(ValueError):
            self.verify(values)

    def test_changed_full_observed_predecessor_refuses(self):
        values = list(fixture())
        values[3] = copy.deepcopy(values[3])
        values[3][0]['unexpected_field'] = 'drift'
        with self.assertRaises(ValueError):
            self.verify(values)

    def test_expired_response_refuses(self):
        values = list(fixture())
        values[9] = values[9] + timedelta(minutes=6)
        with self.assertRaises(ValueError):
            self.verify(values)

    def test_wrong_family_refuses_before_response(self):
        values = list(fixture())
        values[1] = copy.deepcopy(values[1])
        values[1][0]['event_family'] = 'semantic'
        values[2] = list(values[2])
        values[1][0]['event_digest'] = gate.ZERO
        values[1][0]['event_digest'] = gate.sha(gate.encoded(values[1][0]) + b'\n')
        values[2][0] = gate.encoded(values[1][0]) + b'\n'
        with self.assertRaises(ValueError):
            self.verify(values)

    def test_native_seal_scratch_redirect_exact_call(self):
        module = run.selected_append().selected_preparation()
        with tempfile.TemporaryDirectory(prefix='t13-redirect-test-', dir=Path(__file__).parent) as root:
            run.redirect_native_tempfile(module, root)
            with module.tempfile.TemporaryDirectory(prefix='cal-t13-inert-', dir='/tmp') as name:
                self.assertEqual(Path(name).parent, Path(root))
            with self.assertRaises(ValueError):
                module.tempfile.TemporaryDirectory(prefix='wrong-', dir='/tmp')

    def test_negative_guard_snapshot_covers_nested_native_files(self):
        with tempfile.TemporaryDirectory(prefix='t13-snapshot-test-', dir=Path(__file__).parent) as root:
            root = Path(root)
            nested = root / 'native-subdirectory'
            nested.mkdir()
            (nested / 'head.json').write_bytes(b'first')
            before = run.files_digest(root)
            (nested / 'head.json').write_bytes(b'changed')
            self.assertNotEqual(before, run.files_digest(root))
            (nested / 'link').symlink_to('head.json')
            with self.assertRaises(ValueError):
                run.files_digest(root)

    def test_changed_decision_or_witness_refuses(self):
        for position in (7, 8):
            values = list(fixture())
            values[position] += b' '
            with self.assertRaises(ValueError):
                self.verify(values)


if __name__ == '__main__':
    unittest.main()
