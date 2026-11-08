"""Synthetic causal tests; fake held readers cannot attest real authority."""
from __future__ import annotations

import copy
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

path = Path(__file__).with_name('integration.py')
spec = importlib.util.spec_from_file_location('context_runtime_integration_0003', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
PERIOD = path.parents[1].joinpath('context-jit-provision-0001/selected-period.json').read_bytes()
NOW = '2026-10-20T12:00:00Z'


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


class FakeHeld:
    def __init__(self, value):
        self.value = value

    def read_current_signed(self):
        return copy.deepcopy(self.value)

    def read_selected_authorization(self):
        return copy.deepcopy(self.value)

    def read_selected_policy(self):
        return copy.deepcopy(self.value)


def case():
    topology = m.plan()
    family = m.previous()._load('context-family-0001/selection.json')['family']
    source = {
        'period_raw': PERIOD, 'scope_ref': m.SCOPE,
        'family_ref': topology['stage_root'] + '/' + topology['source_role'],
        'source_manifest_sha256': family['source_manifest_sha256'],
        'source_package_sha256': family['source_package_sha256'],
        'reader_open_signed': True, 'source_guarded': True,
        'package_guarded': True, 'held_origin': 'synthetic-held-reader',
    }
    period = json.loads(PERIOD)
    auth_value = {
        'schema_version': 'lab-context-development-authorization/v1-candidate',
        'family_ref': topology['stage_root'] + '/' +
        'product/lab/release-candidates/v1/interface/docker-context-20261020-0001',
        'episode_ref': period['period_ref'], 'scope_ref': m.SCOPE,
        'period_binding': {'path': m.PERIOD_REL, 'sha256': m.PERIOD_SHA},
        'not_before': '2026-10-20T11:59:00Z',
        'expires_at': '2026-10-20T12:15:00Z',
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'claim_ceiling': m.CLAIM,
    }
    auth_raw = wire(auth_value)
    auth = {'raw': auth_raw, 'sha256': m.sha(auth_raw),
            'path': topology['stage_root'] + '/' + topology['auth_path'],
            'uid': 1000, 'gid': 1000, 'mode': '0600',
            'held_origin': 'synthetic-held-auth'}
    policy_value = {
        'schema_version': 'lab-context-host-policy/v1-candidate',
        'host_uid': 1000, 'principal_ref': period['principal_ref'],
        'scope_ref': m.SCOPE,
        'reader_public_key': base64.b64encode(b'\x02' * 32).decode(),
        'period_binding': {'path': m.PERIOD_REL, 'sha256': m.PERIOD_SHA},
        'not_before': '2026-10-20T12:00:00Z',
        'expires_at': '2026-10-20T12:10:00Z',
        'allowed_operations': ['context.get', 'session.open'],
        'max_input_bytes': 1048576, 'max_output_bytes': 2097152,
        'max_session_seconds': 900,
        'authority_effect': 'none', 'actual_owner_outcome': None,
    }
    policy_raw = wire(policy_value)
    policy = {'raw': policy_raw, 'sha256': m.sha(policy_raw),
              'path': topology['private_policy_root'] + '/permission.json',
              'uid': 1000, 'gid': 1000, 'mode': '0600',
              'held_origin': 'synthetic-held-policy'}
    receipt = {
        'uid': 1000, 'gid': 1000, 'namespace_count': 1571,
        'source_mode': '0700', 'auth_dir_mode': '0700', 'auth_leaf_mode': '0600',
        'root_mount': 'ro', 'native_mount': 'ro', 'child_output_mount': 'ro',
        'private_root_outside_public': True, 'post_ack_readback': True,
        'manifest_rows': 39, 'leaves': 40, 'finish_ordinal': 41,
        'trace': list(m.expected_trace()),
    }
    return source, auth, policy, receipt


def check(source, auth, policy, receipt, now=NOW):
    return m.check_synthetic(FakeHeld(source), FakeHeld(auth), FakeHeld(policy), receipt, now)


class IntegrationTests(unittest.TestCase):
    def test_frozen_selection_and_trace_identity(self):
        selected = json.loads(path.with_name('selection.json').read_text())
        self.assertFalse(selected['effect_enabled'])
        self.assertEqual(selected['predecessor_module_sha256'], m.PREVIOUS_SHA)
        self.assertEqual(selected['rejected_predecessor_freeze_sha256'], m.REJECTED_PREDECESSOR_SHA)
        self.assertEqual(selected['selected_bridge_sha256'], m.BRIDGE_SHA)
        self.assertEqual(selected['source_period_public_fixture_sha256'], m.PERIOD_SHA)
        raw = json.dumps(m.expected_trace(), separators=(',', ':')).encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), selected['trace_sha256'])
        self.assertEqual(selected['wire_request_count'], 42)

    def test_positive_42_request_trace_still_inert(self):
        source, auth, policy, receipt = case()
        result = check(source, auth, policy, receipt)
        self.assertEqual(result['status'], 'SYNTHETIC_COMPLETE_TRACE_ONLY')
        self.assertFalse(result['actual_source_read'])
        self.assertFalse(result['effect_enabled'])
        trace = receipt['trace']
        self.assertEqual(sum(x.startswith('send:') for x in trace), 42)
        self.assertEqual(sum(x.startswith('ack:') for x in trace), 42)
        self.assertLess(trace.index('private-root-absent'),
                        trace.index('send:39:EMIT:build-result.json'))
        self.assertLess(trace.index('writer-closed'), trace.index('ack:41:FINISH'))

    def test_actual_selected_client_wire_ordinals_accepted(self):
        contract = m.bridge_wire_contract()
        self.assertEqual(contract['source_sha256'], m.BRIDGE_SHA)
        self.assertEqual(contract['emit_offset'], 1)
        self.assertEqual(contract['release_private_action_ordinal'], 38)
        self.assertEqual(contract['finish_ordinal'], 41)
        source, auth, policy, receipt = case()
        trace = receipt['trace']
        for row_count, leaf in enumerate(m.expected_leaves()):
            wire_ordinal = row_count + contract['emit_offset']
            self.assertIn(f'send:{wire_ordinal}:EMIT:{leaf}', trace)
            self.assertIn(f'ack:{wire_ordinal}:EMIT:{leaf}', trace)
        self.assertLess(trace.index('ack:38:EMIT:delivery-provenance.json'),
                        trace.index('send:38:RELEASE_PRIVATE'))
        self.assertEqual(check(source, auth, policy, receipt)['status'],
                         'SYNTHETIC_COMPLETE_TRACE_ONLY')

    def test_rejected_zero_based_predecessor_trace(self):
        source, auth, policy, receipt = case()
        for i, leaf in enumerate(m.expected_leaves(), start=1):
            for action in ('send', 'ack'):
                receipt['trace'][receipt['trace'].index(f'{action}:{i}:EMIT:{leaf}')] = (
                    f'{action}:{i-1}:EMIT:{leaf}')
        self.assertIn('send:0:EMIT:request.json', receipt['trace'])
        with self.assertRaisesRegex(m.Refused, 'COMPLETE_42_REQUEST_TRACE'):
            check(source, auth, policy, receipt)

    def test_missing_or_reordered_protocol_event_refuses(self):
        expected = m.expected_trace()
        probes = [
            lambda t: t.remove('ack:1:EMIT:request.json'),
            lambda t: t.remove('ack:38:EMIT:delivery-provenance.json'),
            lambda t: t.remove('ack:38:RELEASE_PRIVATE'),
            lambda t: t.remove('private-root-absent'),
            lambda t: t.remove('ack:39:EMIT:build-result.json'),
            lambda t: t.remove('ack:40:EMIT:manifest.json'),
            lambda t: t.remove('ack:41:FINISH'),
            lambda t: t.remove('writer-closed'),
            lambda t: t.remove('client-closed'),
            lambda t: t.insert(t.index('send:39:EMIT:build-result.json') + 1,
                               'private-root-absent'),
            lambda t: t.insert(-1, 'send:41:FINISH'),
        ]
        for number, change in enumerate(probes):
            with self.subTest(number=number):
                source, auth, policy, receipt = case()
                change(receipt['trace'])
                self.assertNotEqual(tuple(receipt['trace']), expected)
                with self.assertRaisesRegex(m.Refused, 'COMPLETE_42_REQUEST_TRACE'):
                    check(source, auth, policy, receipt)

    def test_foreign_or_unguarded_signed_source_refuses(self):
        for key, value in (('scope_ref', 'scope:foreign'), ('source_guarded', False),
                           ('package_guarded', False), ('reader_open_signed', False),
                           ('source_manifest_sha256', '0'*64)):
            with self.subTest(key=key):
                source, auth, policy, receipt = case()
                source[key] = value
                with self.assertRaisesRegex(m.Refused, 'SIGNED_SOURCE_MODEL'):
                    check(source, auth, policy, receipt)

    def test_auth_must_be_nested_in_selected_source_period(self):
        for start, end in (('2026-10-20T08:19:59Z', '2026-10-20T12:15:00Z'),
                           ('2026-10-20T11:59:00Z', '2026-10-21T08:20:01Z'),
                           ('2026-10-20T12:01:00Z', '2026-10-20T12:15:00Z'),
                           ('2026-10-20T11:59:00Z', '2026-10-20T12:00:00Z')):
            with self.subTest(start=start, end=end):
                source, auth, policy, receipt = case()
                value = json.loads(auth['raw'])
                value['not_before'], value['expires_at'] = start, end
                auth['raw'] = wire(value)
                auth['sha256'] = m.sha(auth['raw'])
                with self.assertRaisesRegex(m.Refused, 'AUTH_WITHIN_SOURCE_PERIOD'):
                    check(source, auth, policy, receipt)

    def test_auth_and_policy_scope_or_period_binding_refuse(self):
        for which, key, value, code in (
            ('auth', 'scope_ref', 'scope:foreign', 'AUTH_PROFILE_JOIN'),
            ('auth', 'period_binding', {'path': m.PERIOD_REL, 'sha256':'0'*64}, 'AUTH_PROFILE_JOIN'),
            ('policy', 'scope_ref', 'scope:foreign', 'POLICY_JOIN'),
            ('policy', 'expires_at', '2026-10-20T12:16:00Z', 'POLICY_WITHIN_AUTH')):
            with self.subTest(which=which, key=key):
                source, auth, policy, receipt = case()
                target = auth if which == 'auth' else policy
                body = json.loads(target['raw'])
                body[key] = value
                target['raw'] = wire(body)
                target['sha256'] = m.sha(target['raw'])
                with self.assertRaisesRegex(m.Refused, code):
                    check(source, auth, policy, receipt)

    def test_source_expiry_and_uid_refuse(self):
        source, auth, policy, receipt = case()
        with self.assertRaisesRegex(m.Refused, 'SOURCE_PERIOD_CURRENT'):
            check(source, auth, policy, receipt, '2026-10-21T08:20:00Z')
        policy['uid'] = 1001
        with self.assertRaisesRegex(m.Refused, 'POLICY_HELD_MODEL'):
            check(source, auth, policy, receipt)

    def test_output_and_count_refusals(self):
        for key, value in (('namespace_count', 1570), ('child_output_mount', 'rw'),
                           ('manifest_rows', 38), ('leaves', 39),
                           ('finish_ordinal', 40), ('post_ack_readback', False)):
            with self.subTest(key=key):
                source, auth, policy, receipt = case()
                receipt[key] = value
                with self.assertRaisesRegex(m.Refused, 'COMPLETE_42_REQUEST_TRACE'):
                    check(source, auth, policy, receipt)

    def test_launch_is_effect_disabled(self):
        with self.assertRaisesRegex(m.Refused, 'effect disabled'):
            m.launch()


if __name__ == '__main__':
    unittest.main()
