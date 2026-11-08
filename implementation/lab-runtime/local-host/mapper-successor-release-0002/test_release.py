from datetime import datetime, timezone
from pathlib import Path
from unittest import TestCase, main, mock

import release as R

NOW = datetime(2026, 10, 20, 15, 45, tzinfo=timezone.utc)


def fixture():
    """Actual Source metadata; synthetic future Reader effect metadata only."""
    mapper = R.frozen_selector()
    reader = mapper.reader_adapter()
    source_root = R.STATE / 'source-attempt/root'
    source_raw = (reader.PROFILE / 'generated' / reader.SOURCE /
                  'source-manifest.json').read_bytes()
    package = source_root / reader.SOURCE / 'packages/0001'
    package_raw = (package / 'manifest.json').read_bytes()
    period_raw = (package / 'period.json').read_bytes()
    terminal_raw = (R.STATE / 'source-attempt/evidence/source-once.terminal.json').read_bytes()
    review_raw = (R.LOCAL /
                  'context-successor-source-independent-effect-review-0001/review.json').read_bytes()
    selected = reader.select(source_raw, package_raw, terminal_raw,
                             period_raw, review_raw, R.SOURCE_REVIEW_SHA, NOW)
    reader_raw = reader.encoded(selected['reader_manifest'])
    receipt_raw = R.encoded({
        'schema_version': 'lab-disposable-reader-receipt/v1-private',
        'reader_manifest_sha256': R.sha(reader_raw),
        'source_manifest_sha256': reader.SOURCE_MANIFEST_SHA,
        'source_package_manifest_sha256': R.sha(package_raw),
        'authority_effect': 'none', 'actual_owner_outcome': None})
    reader_terminal_raw = R.encoded({
        'overall': 'PASS', 'operation': 'PASS', 'cleanup': 'PASS',
        'reader_effect': 'DISPOSABLE_READER_DIAGNOSTIC',
        'receipt_sha256': R.sha(receipt_raw), 'no_retry': True})
    external_raw = R.encoded({
        'schema': 'lab-successor-reader-external-exit/v1',
        'exit_code': 0, 'attempt': str(mapper.READER_ATTEMPT)})
    reader_review_raw = R.encoded({
        'schema': 'lab-successor-reader-effect-review/v1',
        'verdict': 'PASS_BOUNDED_READER_COLD_OPEN',
        'attempt': str(mapper.READER_ATTEMPT),
        'source_manifest_sha256': reader.SOURCE_MANIFEST_SHA,
        'source_package_manifest_sha256': R.sha(package_raw),
        'reader_manifest_sha256': R.sha(reader_raw),
        'receipt_sha256': R.sha(receipt_raw),
        'terminal_sha256': R.sha(reader_terminal_raw),
        'external_sha256': R.sha(external_raw)})
    return dict(source_manifest_raw=source_raw,
                source_package_raw=package_raw,
                source_terminal_raw=terminal_raw,
                period_raw=period_raw,
                source_review_raw=review_raw,
                outside_source_review_sha=R.SOURCE_REVIEW_SHA,
                reader_manifest_raw=reader_raw,
                reader_receipt_raw=receipt_raw,
                reader_terminal_raw=reader_terminal_raw,
                reader_external_raw=external_raw,
                reader_review_raw=reader_review_raw,
                outside_reader_review_sha=R.sha(reader_review_raw),
                now=NOW)


def replace_external_exit(data, exit_code):
    """Mutate the synthetic future evidence coherently, including review pin."""
    mapper = R.frozen_selector()
    external = mapper.parse(data['reader_external_raw'])
    external['exit_code'] = exit_code
    data['reader_external_raw'] = R.encoded(external)
    review = mapper.parse(data['reader_review_raw'])
    review['external_sha256'] = R.sha(data['reader_external_raw'])
    data['reader_review_raw'] = R.encoded(review)
    data['outside_reader_review_sha'] = R.sha(data['reader_review_raw'])
    return data


class MapperReleaseTests(TestCase):
    def test_exact_future_stage_and_original_verifier_contract(self):
        data = fixture()
        result = R.select_stage(**data)
        plan = result['plan']
        rows = plan['files']
        self.assertEqual((len(rows), len({r['path'] for r in rows})), (991, 991))
        self.assertEqual(sum(r['source_kind'] == 'reviewed-reader-stage'
                             for r in rows), 986)
        self.assertEqual(sum(r['source_kind'] == 'generated-mapper'
                             for r in rows), 5)
        self.assertEqual(plan['source_package_manifest_sha256'],
                         R.sha(data['source_package_raw']))
        self.assertEqual(plan['reader_manifest_sha256'],
                         R.sha(data['reader_manifest_raw']))
        self.assertEqual(plan['reader_effect_review_sha256'],
                         data['outside_reader_review_sha'])
        archive = next(r for r in rows if r['path'].endswith('/branch.snapshot'))
        self.assertEqual((archive['source_mode'], archive['target_mode']),
                         ('0600', '0600'))
        self.assertEqual(len(plan['expected_package_members']), 55)
        self.assertEqual(len(set(plan['expected_package_members'])), 55)
        self.assertEqual(plan['native_sha256'], R.frozen_selector().NATIVE_SHA)
        self.assertEqual(plan['output_acceptance_contract']['node_count'], 15)
        self.assertEqual(plan['output_acceptance_contract']['edge_count'], 10)
        self.assertEqual(plan['output_acceptance_contract']['exact_governance_joins'], 25)
        self.assertEqual(plan['output_acceptance_contract']['actual_cold_native_read_processes'], 2)
        self.assertFalse(plan['output_acceptance_contract']['verifier_rebound'])
        self.assertFalse(result['output_contract']['effect_verifier_adapted'])
        self.assertFalse(result['effect_enabled'])
        self.assertEqual(result['plan_sha256'], R.sha(R.encoded(plan)))

    def test_selection_never_opens_private_archive_body(self):
        data = fixture()
        original = Path.read_bytes

        def guard(path):
            if path.name == 'branch.snapshot':
                raise AssertionError('private body opened')
            return original(path)

        with mock.patch.object(Path, 'read_bytes', guard):
            self.assertEqual(R.select_stage(**data)['status'],
                             'SELECTION_ONLY_EFFECT_DISABLED')

    def test_outside_effect_pins_and_reader_exit_refuse(self):
        data = fixture()
        data['outside_source_review_sha'] = '0' * 64
        with self.assertRaisesRegex(R.Refused, 'SOURCE_EFFECT_REVIEW_PIN'):
            R.select_stage(**data)
        data = fixture()
        data['outside_reader_review_sha'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'OUTSIDE_READER_REVIEW_PIN'):
            R.select_stage(**data)
        for invalid in (False, 0.0, 1, True):
            with self.subTest(exit_code=invalid):
                data = replace_external_exit(fixture(), invalid)
                self.assertEqual(data['outside_reader_review_sha'],
                                 R.sha(data['reader_review_raw']))
                self.assertEqual(R.frozen_selector().parse(data['reader_review_raw'])
                                 ['external_sha256'], R.sha(data['reader_external_raw']))
                with self.assertRaisesRegex(R.Refused,
                                            'READER_EXTERNAL_OS_INTEGER_ZERO'):
                    R.select_stage(**data)
        self.assertEqual(R.select_stage(**replace_external_exit(fixture(), 0))
                         ['status'], 'SELECTION_ONLY_EFFECT_DISABLED')

    def test_reader_manifest_and_period_refuse(self):
        data = fixture()
        data['reader_manifest_raw'] = b'{}\n'
        with self.assertRaisesRegex(ValueError, 'READER_MANIFEST_DYNAMIC_JOIN'):
            R.select_stage(**data)
        data = fixture()
        data['now'] = datetime(2026, 10, 21, 15, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, 'PERIOD_CURRENT'):
            R.select_stage(**data)

    def test_docker_envelope_and_effect_refusal(self):
        with self.assertRaisesRegex(R.Refused, 'UNREVIEWED_STAGE_IDENTITY'):
            R.docker_envelope(0, 1, '0' * 64)
        envelope = R.docker_envelope(3, 7, 'a' * 64)
        self.assertEqual(envelope['stage_id'], '3:7')
        self.assertEqual(envelope['network'], 'none')
        self.assertEqual(envelope['userns'], 'host')
        self.assertTrue(envelope['root_bind']['read_only'])
        self.assertFalse(envelope['package_bind']['read_only'])
        self.assertFalse(envelope['create_argv_available'])
        with self.assertRaisesRegex(R.Refused, 'EFFECT_DISABLED'):
            R.execute_stage()
        with self.assertRaisesRegex(R.Refused, 'EFFECT_DISABLED'):
            R.execute_mapper()


if __name__ == '__main__':
    main()
