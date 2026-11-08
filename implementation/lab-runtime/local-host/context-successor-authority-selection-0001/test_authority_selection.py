"""Causal effect-disabled checks over the actual reviewed Mapper selection."""
import copy
import datetime as dt
import json
import os
import unittest
from unittest import mock

import authority_selection as A

NOW = dt.datetime(2026,10,20,18,30,tzinfo=dt.timezone.utc)


class SelectionTests(unittest.TestCase):
    def test_actual_1570_rows_and_unminted_auth(self):
        selected = A.current_selection(NOW)
        self.assertEqual(selected['status'],'ACTUAL_MAPPER_SELECTED_AUTHORITY_HOLD')
        self.assertEqual(len(selected['stage']['bound_rows']),1570)
        self.assertEqual(selected['stage']['final_count_with_auth'],1571)
        self.assertEqual(selected['stage']['auth_placeholder']['sha256'],
                         'UNMINTED_UNSELECTED')
        self.assertEqual(selected['source']['period_end'],
                         '2026-10-21T15:00:00+00:00')
        self.assertEqual(selected['required_signed_scope']['status'],
                         'NOT_OPENED_REQUIRES_REVIEWED_READER_SIGNED_VIEW')
        self.assertEqual(selected['policy_topology']['host_private_root'],
                         selected['stage']['topology']['private_root'])
        self.assertEqual(selected['issuer'],'UNSELECTED')

    def test_authorization_template_does_not_promote_row_or_scope(self):
        selected = A.current_selection(NOW)
        candidate = A.auth_template(selected,NOW)
        value = A.parse(candidate['bytes'])
        self.assertEqual(candidate['status'],'UNTRUSTED_UNISSUED_AUTH_TEMPLATE_ONLY')
        self.assertEqual(candidate['actual_bound_count'],1570)
        self.assertEqual(candidate['would_be_final_count'],1571)
        self.assertEqual(candidate['path'],A.AUTH_PATH)
        self.assertEqual(candidate['sha256'],A.sha(candidate['bytes']))
        self.assertEqual(value['scope_ref'],A.SCOPE)
        self.assertEqual(value['period_binding']['sha256'],A.SOURCE_PERIOD_SHA)
        self.assertEqual(A.utc(value['expires_at'])-A.utc(value['not_before']),
                         dt.timedelta(minutes=20))
        self.assertEqual(selected['auth_row'],'UNMINTED_UNSELECTED')
        self.assertEqual(candidate['signed_scope'],'NOT_OPENED')

    def test_forged_source_period_and_expiry_refuse(self):
        selected = A.current_selection(NOW)
        forged = dict(selected,source=dict(selected['source'],
                                           period_end='2026-10-30T15:00:00+00:00'))
        with self.assertRaisesRegex(A.Refused,'CURRENT_SOURCE_RECHECK'):
            A.auth_template(forged,NOW)
        expired = dt.datetime(2026,10,21,15,0,tzinfo=dt.timezone.utc)
        with self.assertRaises((A.Refused,ValueError)):
            A.current_selection(expired)
        with self.assertRaises((A.Refused,ValueError)):
            A.auth_template(selected,expired)

    def test_policy_topology_drift_refuses_actual_selection(self):
        selector,policy = A.checked_modules()
        class Drift:
            @staticmethod
            def topology():
                return dict(policy.topology(),child_policy_root='/workspace/private')
        with self.assertRaisesRegex(A.Refused,'SIX_BIND_PRIVATE_TOPOLOGY'):
            A.current_selection(NOW,modules=lambda:(selector,Drift))

    def test_private_source_body_never_opened_by_selection(self):
        actual = os.open
        seen = []
        def guarded(path,*args,**kwargs):
            if str(path).endswith('/branch.snapshot'):
                raise AssertionError('private body opened')
            seen.append(str(path))
            return actual(path,*args,**kwargs)
        with mock.patch.object(os,'open',side_effect=guarded):
            selected = A.current_selection(NOW)
        self.assertEqual(selected['stage']['protected_archive_metadata']['body'],
                         'UNOPENED')
        self.assertGreater(len(seen),0)

    def test_proof_first_invalid_request_consumes_one_use_opportunity(self):
        _,policy = A.checked_modules()
        proof = policy.ProofModel(policy_sha='a'*64,
                                  expires_at='2026-10-20T18:50:00+00:00',
                                  attempt='local-fixture',peer=(123,1000,1000))
        with self.assertRaises(policy.Refused):
            proof.consume(b'bad',peer=(123,1000,1000),current=True)
        self.assertEqual(proof.state,'UNKNOWN_CONSUMED')
        with self.assertRaisesRegex(policy.Refused,'PROOF_ALREADY_CONSUMED'):
            proof.consume(b'{}',peer=(123,1000,1000),current=True)
        with self.assertRaises(policy.Refused): proof.sign()
        with self.assertRaises(policy.Refused): proof.restart()

    def test_proof_durability_failure_is_consumed_without_signature(self):
        _,policy = A.checked_modules()
        proof = policy.ProofModel(policy_sha='a'*64,
                                  expires_at='2026-10-20T18:50:00+00:00',
                                  attempt='local-fixture',peer=(123,1000,1000))
        challenge = {'schema_version':'lab-context-host-challenge/v1-candidate',
                     'host_instance_ref':'host:R03-context:fixture',
                     'connection_ref':'connection:R03-context:fixture',
                     'nonce':'b'*64,'policy_sha256':'a'*64,
                     'expires_at':'2026-10-20T18:50:00+00:00',
                     'authority_effect':'none'}
        raw = policy.compact({'schema':'context-parent-proof-request/v1',
                              'attempt':'local-fixture','challenge':challenge})
        receipt = proof.consume(raw,peer=(123,1000,1000),current=True)
        self.assertEqual(proof.state,'CONSUMED_PENDING_DURABILITY')
        with self.assertRaisesRegex(policy.Refused,'NO_SIGN_DURABILITY_UNKNOWN'):
            proof.durable(retained_request_sha=receipt['request_sha256'],
                          fsync_observed=False,current=True)
        self.assertEqual(proof.state,'UNKNOWN_CONSUMED')
        with self.assertRaises(policy.Refused): proof.sign()

    def test_failed_retention_release_poisoned_and_cleanup_refused(self):
        _,policy = A.checked_modules()
        retention = policy.RetentionModel()
        retention.closed_channel(channel_closed=True,
                                 local_proof_handle_dropped=True,
                                 policy_attached=True)
        with self.assertRaises(policy.Refused):
            retention.release_transport_scratch(37,scratch_empty=True,
                                                policy_attached=True)
        self.assertEqual(retention.state,'UNKNOWN')
        with self.assertRaises(policy.Refused):
            retention.release_transport_scratch(38,scratch_empty=True,
                                                policy_attached=True)
        with self.assertRaises(policy.Refused): retention.cleanup_effect()

    def test_order_and_every_effect_refusal(self):
        selected = A.current_selection(NOW)
        design = A.ordered_design(selected)
        steps = design['steps']
        self.assertLess(steps.index('HOLD_NOFOLLOW_STAGE_PARENT_AND_EXCLUSIVE_ROOT_CLAIM'),
                        steps.index('DURABLE_NO_RETRY_STAGE_MARKER_BEFORE_CONTENT'))
        self.assertLess(steps.index('DURABLE_NO_RETRY_STAGE_MARKER_BEFORE_CONTENT'),
                        steps.index('COPY_AND_REHASH_1570_BOUND_ROWS_WITH_PRIVATE_BODY_CUSTODY'))
        self.assertLess(steps.index('RECHECK_PERIOD_SIGNED_SCOPE_AND_ISSUER_BEFORE_AUTH_EFFECT'),
                        steps.index('ISSUE_EXACT_AUTH_AND_WRITE_1571ST_ROW_ONCE'))
        self.assertLess(steps.index('CONSUME_FIRST_PROOF_REQUEST_BEFORE_VALIDATION'),
                        steps.index('FSYNC_DURABLE_PROOF_CONSUMPTION_BEFORE_SINGLE_SIGNATURE'))
        self.assertLess(steps.index('VERIFY_OS_OUTPUT_CID_NAME_ABSENCE_BEFORE_ANY_PRIVATE_CLEANUP'),
                        steps.index('ELIGIBLE_HELD_PRIVATE_CLEANUP_ONLY_AFTER_EXTERNAL_GATE'))
        for fn in (A.open_signed_scope,A.issue_auth_row,
                   A.create_private_policy_or_key,A.launch_context):
            with self.assertRaisesRegex(A.Refused,'EFFECT_DISABLED'):
                fn()


if __name__ == '__main__': unittest.main(verbosity=2)
