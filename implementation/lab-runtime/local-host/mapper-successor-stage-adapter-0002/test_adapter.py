from datetime import datetime, timezone
from pathlib import Path
from unittest import TestCase, main, mock

import adapter as A

NOW = datetime(2026, 10, 20, 16, 20, tzinfo=timezone.utc)


class DirectActualMapperTests(TestCase):
    def test_actual_reader_review_direct_991_file_plan(self):
        selected = A.select_actual(now=NOW)
        plan, copy, verifier = (selected['stage_plan'], selected['copy_plan'],
                                selected['verifier_plan'])
        self.assertEqual(selected['status'],
                         'ACTUAL_READER_DIRECT_MAPPER_PLAN_PENDING_STATIC_REVIEW')
        self.assertEqual(selected['stage_plan_sha256'],
                         '9041aeedc8b349f6d7315e7ac2544aabda85afdb748663010e00af25e0b9ca2e')
        self.assertEqual(len(plan['files']), 991)
        self.assertEqual((copy['source_rows'], copy['generated_mapper_rows']), (986, 5))
        self.assertEqual((copy['source_directories'], copy['target_directories']),
                         (931, 933))
        self.assertEqual(copy['private_source_package_rows'], 37)
        self.assertIn(A.frozen_mapper_release().frozen_selector().SOURCE + '/receipts',
                      copy['target_directory_names'])
        self.assertEqual(plan['reader_effect_review_sha256'], A.ACTUAL_REVIEW_SHA)
        self.assertEqual(plan['reader_external_observation_sha256'], A.ACTUAL_EXTERNAL_SHA)
        self.assertEqual(plan['mapper_manifest_sha256'],
                         'bad889d50a0ba302ae83c9f4d5d9b664417af50cf4a6e4c408dfb50f8680d947')
        self.assertEqual(plan['native_sha256'], A.NATIVE_SHA)
        self.assertEqual(verifier['template_sha256'], A.VERIFIER_SHA)
        self.assertEqual(len(verifier['expected_package_members']), 55)
        self.assertEqual(verifier['expected_checks']['node_count'], 15)
        self.assertEqual(verifier['expected_checks']['edge_count'], 10)
        self.assertEqual(verifier['expected_checks']['exact_governance_joins'], 25)
        self.assertFalse(verifier['effect_verifier_adapted'])
        self.assertFalse(selected['actual_reader_provenance']['compatibility_projection_used'])
        self.assertFalse(selected['effect_enabled'])
        self.assertEqual(selected['copy_plan_sha256'], A.sha(A.encoded(copy)))
        self.assertNotEqual(A.ACTUAL_STDOUT_SHA, A.ACTUAL_FINAL_SHA)
        self.assertEqual(A.parse(A._actual_effect_bytes()['stdout']),
                         A.parse(A._actual_effect_bytes()['final']))

    def test_actual_selection_never_opens_private_archive_body(self):
        original = Path.read_bytes

        def guard(path):
            if path.name == 'branch.snapshot':
                raise AssertionError('private archive body opened')
            return original(path)

        with mock.patch.object(Path, 'read_bytes', guard):
            self.assertEqual(A.select_actual(now=NOW)['status'],
                             'ACTUAL_READER_DIRECT_MAPPER_PLAN_PENDING_STATIC_REVIEW')

    def test_actual_external_exit_rejects_scalar_aliases(self):
        raw = A.ACTUAL_EXTERNAL.read_bytes()
        self.assertEqual(A.strict_actual_external(raw)['os_exit_code'], 0)
        for invalid in (False, 0.0, True, 1, -1, '0', None):
            with self.subTest(exit_code=invalid):
                value = A.parse(raw)
                value['os_exit_code'] = invalid
                with self.assertRaisesRegex(A.Refused,
                                            'ACTUAL_READER_EXTERNAL_OBSERVER'):
                    A.strict_actual_external(A.encoded(value))

    def test_original_review_and_swapped_terminal_bytes_refuse(self):
        raws = A._actual_effect_bytes()
        stage = A.stage_basis()
        self.assertEqual(A._validated_actual_reader(raws, stage)['review']['verdict'],
                         'PASS_BOUNDED_READER_ONLY_EFFECT')
        changed = dict(raws)
        changed['final'], changed['provisional'] = raws['provisional'], raws['final']
        with self.assertRaisesRegex(A.Refused, 'ACTUAL_READER_ORIGINAL_DIGEST'):
            A._validated_actual_reader(changed, stage)
        changed = dict(raws)
        review = A.parse(raws['review'])
        review['verdict'] = 'HOLD'
        changed['review'] = A.encoded(review)
        with self.assertRaisesRegex(A.Refused, 'ACTUAL_READER_ORIGINAL_DIGEST'):
            A._validated_actual_reader(changed, stage)

    def test_changed_stdout_with_coherent_hashes_still_refuses(self):
        raws = A._actual_effect_bytes()
        changed = dict(raws)
        parsed = A.parse(raws['stdout'])
        parsed['overall'] = 'UNKNOWN'
        changed['stdout'] = A.encoded(parsed)
        external = A.parse(raws['external'])
        external['stdout_sha256'] = A.sha(changed['stdout'])
        external['stdout_size'] = len(changed['stdout'])
        changed['external'] = A.encoded(external)
        review = A.parse(raws['review'])
        review['external_observation_sha256'] = A.sha(changed['external'])
        changed['review'] = A.encoded(review)
        with (mock.patch.object(A, 'ACTUAL_STDOUT_SHA', A.sha(changed['stdout'])),
              mock.patch.object(A, 'ACTUAL_EXTERNAL_SHA', A.sha(changed['external'])),
              mock.patch.object(A, 'ACTUAL_REVIEW_SHA', A.sha(changed['review']))):
            with self.assertRaisesRegex(A.Refused, 'ACTUAL_READER_EXTERNAL_STREAM_JOIN'):
                A._validated_actual_reader(changed, A.stage_basis())

    def test_wrong_container_identity_and_cross_family_refuse(self):
        raws = A._actual_effect_bytes()
        changed = dict(raws)
        cid = A.parse(raws['cid_receipt'])
        cid['container_id'] = '0' * 64
        changed['cid_receipt'] = A.encoded(cid)
        with mock.patch.object(A, 'ACTUAL_CID_RECEIPT_SHA', A.sha(changed['cid_receipt'])):
            with self.assertRaisesRegex(A.Refused, 'ACTUAL_READER_CONTAINER_IDENTITY_JOIN'):
                A._validated_actual_reader(changed, A.stage_basis())
        changed = dict(raws)
        receipt = A.parse(raws['receipt'])
        receipt['source_package_manifest_sha256'] = '0' * 64
        changed['receipt'] = A.encoded(receipt)
        review = A.parse(raws['review'])
        review['receipt_sha256'] = A.sha(changed['receipt'])
        changed['review'] = A.encoded(review)
        with (mock.patch.object(A, 'ACTUAL_RECEIPT_SHA', A.sha(changed['receipt'])),
              mock.patch.object(A, 'ACTUAL_REVIEW_SHA', A.sha(changed['review']))):
            with self.assertRaisesRegex(A.Refused, 'ACTUAL_READER_CLOSED_EVIDENCE_JOIN'):
                A._validated_actual_reader(changed, A.stage_basis())
        changed = dict(raws)
        review = A.parse(raws['review'])
        review['attempt'] = '/tmp/wrong-reader-attempt'
        changed['review'] = A.encoded(review)
        with mock.patch.object(A, 'ACTUAL_REVIEW_SHA', A.sha(changed['review'])):
            with self.assertRaisesRegex(A.Refused,
                                        'ACTUAL_INDEPENDENT_READER_EFFECT_JOIN'):
                A._validated_actual_reader(changed, A.stage_basis())

    def test_final_marker_unknown_and_frozen_input_drift_refuse(self):
        marker = A.ACTUAL_ATTEMPT / 'evidence/reader-once.finalized'
        original_lstat = Path.lstat

        def missing_marker(path):
            if path == marker:
                raise FileNotFoundError(path)
            return original_lstat(path)

        with mock.patch.object(Path, 'lstat', missing_marker):
            with self.assertRaisesRegex(A.Refused, 'ACTUAL_READER_FINAL_MARKER_MISSING'):
                A._marker_observed()
        with mock.patch('adapter.os.path.lexists', return_value=True):
            with self.assertRaisesRegex(A.Refused,
                                        'ACTUAL_READER_UNKNOWN_RELEASE_RECEIPT'):
                A._marker_observed()
        with mock.patch.object(A, 'STAGE_REVIEW_SHA', '0' * 64):
            with self.assertRaisesRegex(A.Refused,
                                        'READER_STAGE_REVIEW_OR_TERMINAL_DRIFT'):
                A.stage_basis()
        with mock.patch.object(A, 'READER_RELEASE_FREEZE_SHA', '0' * 64):
            with self.assertRaisesRegex(A.Refused,
                                        'READER_RELEASE_FREEZE_OR_REVIEW_DRIFT'):
                A.stage_basis()

    def test_period_expiry_and_all_effects_refuse(self):
        with self.assertRaisesRegex(ValueError, 'PERIOD_CURRENT'):
            A.select_actual(now=datetime(2026, 10, 21, 15,
                                         tzinfo=timezone.utc))
        for effect in (A.execute_stage, A.execute_mapper, A.verify_output):
            with self.subTest(effect=effect.__name__):
                with self.assertRaisesRegex(A.Refused, 'EFFECT_DISABLED'):
                    effect()


if __name__ == '__main__':
    main()
