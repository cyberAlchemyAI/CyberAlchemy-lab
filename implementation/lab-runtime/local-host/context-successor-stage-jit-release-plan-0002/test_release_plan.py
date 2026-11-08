"""Effect-disabled successor design checks, including causal refusal probes."""
import datetime as dt
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

SOURCE = Path(__file__).with_name('release_plan.py')
spec = importlib.util.spec_from_file_location('release_plan_tested', SOURCE)
plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan)


class ReleasePlanTests(unittest.TestCase):
    def test_current_reviewed_plan_is_waiting(self):
        result = plan.plan()
        self.assertEqual(result['status'], 'WAIT_OUTSIDE_PINNED_MAPPER_EFFECT')
        self.assertFalse(result['effect_enabled'])
        self.assertEqual(result['mapper_source_rows_required'], 953)
        self.assertEqual((result['bound_rows_after_mapper'],
                          result['final_rows_after_issued_auth']), (1570,1571))
        self.assertEqual(result['protected_archive']['body'], 'UNOPENED')
        self.assertEqual(result['authorization'], 'UNMINTED')
        self.assertEqual(result['signed_scope'], 'NOT_OPENED')

    def test_order_preserves_stage_then_signed_scope_then_auth_then_docker(self):
        steps = plan.plan()['sequence']
        self.assertEqual(len(steps),len(set(steps)))
        self.assertLess(steps.index('COPY_EXACT_1570_FILES_WITH_HASH_MODE_AND_HELD_READBACK'),
                        steps.index('OPEN_READER_SIGNED_SCOPE_ONCE_AND_JOIN_CURRENT_SOURCE_PERIOD'))
        self.assertLess(steps.index('OPEN_READER_SIGNED_SCOPE_ONCE_AND_JOIN_CURRENT_SOURCE_PERIOD'),
                        steps.index('WRITE_AUTH_EXCLUSIVE_OWNER_0600_NOFOLLOW_FSYNC_AND_HELD_READBACK'))
        self.assertLess(steps.index('WRITE_AUTH_EXCLUSIVE_OWNER_0600_NOFOLLOW_FSYNC_AND_HELD_READBACK'),
                        steps.index('DISPATCH_EXACT_CONTEXT_DOCKER_RELEASE_AND_OBSERVE_EXTERNAL_OS_EXIT'))

    def test_exclusive_root_is_consumed_then_durable_marker_before_content(self):
        result = plan.plan()
        steps = result['sequence']
        self.assertLess(steps.index('EXCLUSIVELY_CREATE_STAGE_ROOT_AS_CONSUMED_ATTEMPT_CLAIM'),
                        steps.index('WRITE_CLOSE_AND_FSYNC_DURABLE_NO_RETRY_MARKER_BEFORE_STAGE_CONTENT'))
        self.assertLess(steps.index('WRITE_CLOSE_AND_FSYNC_DURABLE_NO_RETRY_MARKER_BEFORE_STAGE_CONTENT'),
                        steps.index('COPY_EXACT_1570_FILES_WITH_HASH_MODE_AND_HELD_READBACK'))
        self.assertEqual(result['premarker_uncertainty'],
                         'UNKNOWN_PRESERVE_ROOT_INODE_EVIDENCE_NO_RETRY')
        self.assertEqual(result['marker_requirement'],
                         'DURABLE_BEFORE_FIRST_STAGE_CONTENT_MUTATION')

    def test_docker_absence_before_private_cleanup(self):
        steps = plan.plan()['sequence']
        self.assertLess(steps.index('CLOSE_CHANNEL_AND_DROP_IN_MEMORY_KEY_KEEP_PRIVATE_EVIDENCE'),
                        steps.index('VERIFY_TERMINAL_OUTPUT_EXTERNAL_OS_AND_DOCKER_ABSENCE_BEFORE_CLEANUP'))
        self.assertLess(steps.index('VERIFY_TERMINAL_OUTPUT_EXTERNAL_OS_AND_DOCKER_ABSENCE_BEFORE_CLEANUP'),
                        steps.index('REMOVE_ONLY_HELD_VERIFIED_EPHEMERAL_INODES_AFTER_ABSENCE'))

    def test_causal_sequence_reordering_refuses(self):
        original = list(plan.SEQUENCE)
        for first,second in (
            ('EXCLUSIVELY_CREATE_STAGE_ROOT_AS_CONSUMED_ATTEMPT_CLAIM',
             'WRITE_CLOSE_AND_FSYNC_DURABLE_NO_RETRY_MARKER_BEFORE_STAGE_CONTENT'),
            ('WRITE_CLOSE_AND_FSYNC_DURABLE_NO_RETRY_MARKER_BEFORE_STAGE_CONTENT',
             'COPY_EXACT_1570_FILES_WITH_HASH_MODE_AND_HELD_READBACK'),
            ('VERIFY_TERMINAL_OUTPUT_EXTERNAL_OS_AND_DOCKER_ABSENCE_BEFORE_CLEANUP',
             'REMOVE_ONLY_HELD_VERIFIED_EPHEMERAL_INODES_AFTER_ABSENCE')):
            altered = list(original)
            a,b = altered.index(first),altered.index(second)
            altered[a],altered[b] = altered[b],altered[a]
            with self.subTest(first=first), mock.patch.object(plan,'SEQUENCE',tuple(altered)):
                with self.assertRaisesRegex(plan.Refused,
                                            'RELEASE_SEQUENCE_CUSTODY_ORDER'):
                    plan.plan()

    def test_expired_source_period_refuses(self):
        with self.assertRaises(ValueError):
            plan.plan(dt.datetime(2026,10,21,15,0,tzinfo=dt.timezone.utc))

    def test_review_pin_drift_refuses(self):
        bad = dict(plan.PINS)
        bad[plan.FINAL_REVIEW] = '0'*64
        with mock.patch.object(plan,'PINS',bad):
            with self.assertRaisesRegex(plan.Refused,'PUBLIC_PIN_DRIFT'):
                plan.plan()

    def test_count_and_private_topology_drift_refuse(self):
        final,jit = plan.reviewed_modules()
        original = final.preflight_plan()
        topology = jit.topology()
        for field,value in (('final_file_count_if_all_gates_pass',1570),
                            ('private_root',topology['stage_root']+'/bad-private')):
            selected = dict(original)
            selected[field] = value
            fake_final = mock.Mock(preflight_plan=mock.Mock(return_value=selected))
            fake_jit = mock.Mock(topology=mock.Mock(return_value=topology))
            with self.subTest(field=field), mock.patch.object(
                    plan,'reviewed_modules',return_value=(fake_final,fake_jit)):
                with self.assertRaisesRegex(plan.Refused,
                                            'REVIEWED_FINAL_JIT_TOPOLOGY_CLOSURE'):
                    plan.plan()

    def test_caller_asserted_mapper_review_never_selects(self):
        with self.assertRaisesRegex(plan.Refused,'MAPPER_REVIEW_NOT_OUTSIDE_SELECTED'):
            plan.select_after_mapper(mapper_review_raw=b'fixture',
                                     outside_mapper_review_sha='0'*64)

    def test_effect_entrypoints_unconditionally_refuse(self):
        for entry in (plan.copy_final_stage,plan.issue_authorization,
                      plan.create_private_root_key_or_policy,plan.launch_context):
            with self.subTest(entry=entry.__name__):
                with self.assertRaises(plan.Refused):
                    entry()


if __name__ == '__main__':
    unittest.main()
