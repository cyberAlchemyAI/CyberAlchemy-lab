from datetime import datetime, timezone
import unittest

import release as R

A = R.frozen_selector()
NOW = datetime(2026, 10, 20, 15, 30, tzinfo=timezone.utc)
SOURCE_RAW = (A.PROFILE / 'generated' / A.SOURCE / 'source-manifest.json').read_bytes()
PERIOD_RAW = A.encoded({'not_before': '2026-10-20T15:00:00+00:00',
                        'expires_at': '2026-10-21T15:00:00+00:00'})


def fixture(archive_sha='a' * 64):
    archive = {'path': A.SOURCE + '/packages/0001/branch.snapshot',
               'sha256': archive_sha}
    period = {'path': A.SOURCE + '/packages/0001/period.json',
              'sha256': A.sha(PERIOD_RAW)}
    rows = [archive, period] + [
        {'path': A.SOURCE + f'/packages/0001/file-{i:02d}.json',
         'sha256': f'{i:064x}'} for i in range(34)]
    package_raw = A.encoded({
        'files': rows, 'archive_binding': archive, 'period_binding': period,
        'source_manifest_binding': {'path': A.SOURCE + '/source-manifest.json',
                                    'sha256': A.SOURCE_MANIFEST_SHA}})
    terminal_raw = A.encoded({'overall': 'PASS', 'operation': 'PASS',
                              'cleanup': 'PASS', 'no_retry': True,
                              'package_manifest_sha256': A.sha(package_raw)})
    review_raw = A.encoded({
        'schema': 'lab-successor-source-effect-review/v1',
        'verdict': 'PASS_BOUNDED_SOURCE_ONLY_EFFECT',
        'source_manifest_sha256': A.SOURCE_MANIFEST_SHA,
        'package_manifest_sha256': A.sha(package_raw),
        'terminal_sha256': A.sha(terminal_raw),
        'attempt': str(A.SOURCE_ATTEMPT)})
    return package_raw, terminal_raw, review_raw


def selected(archive_sha='a' * 64):
    package_raw, terminal_raw, review_raw = fixture(archive_sha)
    return R.select_stage(SOURCE_RAW, package_raw, terminal_raw,
                          PERIOD_RAW, review_raw, A.sha(review_raw), NOW)


class ReleaseTests(unittest.TestCase):
    def test_exact_dynamic_986_file_plan_and_private_mode(self):
        result = selected()
        plan = result['plan']
        rows = plan['files']
        self.assertEqual(len(rows), 986)
        self.assertEqual(len({r['path'] for r in rows}), 986)
        self.assertEqual(sum(r['source_kind'] == 'source-attempt' for r in rows), 978)
        self.assertEqual(sum(r['source_kind'] == 'generated-reader' for r in rows), 8)
        archive = next(r for r in rows if r['path'].endswith('/branch.snapshot'))
        self.assertEqual(archive['source_path'], str(R.SOURCE_ROOT / archive['path']))
        self.assertEqual((archive['source_mode'], archive['target_mode']), ('0600', '0600'))
        self.assertEqual(plan['source_archive_sha256'], 'a' * 64)
        self.assertEqual(plan['stage_root'], str(R.STAGE_ROOT))
        self.assertEqual(plan['container_name'], R.CONTAINER_NAME)
        self.assertEqual(plan['reader_manifest_sha256'],
                         R.sha(result['generated_reader_bytes'][A.READER + '/source-manifest.json']))
        self.assertEqual(result['plan_sha256'], R.sha(R.encoded(plan)))
        self.assertFalse(result['effect_enabled'])

    def test_new_source_package_rebinds_plan_not_role_preimages(self):
        first, second = selected('a' * 64), selected('b' * 64)
        self.assertNotEqual(first['plan_sha256'], second['plan_sha256'])
        self.assertNotEqual(first['plan']['source_package_manifest_sha256'],
                            second['plan']['source_package_manifest_sha256'])
        self.assertNotEqual(first['plan']['reader_manifest_sha256'],
                            second['plan']['reader_manifest_sha256'])
        self.assertEqual(first['generated_reader_bytes'][A.READER + '/reader.py'],
                         second['generated_reader_bytes'][A.READER + '/reader.py'])

    def test_outside_review_pin_and_expiry_refuse(self):
        package_raw, terminal_raw, review_raw = fixture()
        with self.assertRaisesRegex(ValueError, 'OUTSIDE_EFFECT_REVIEW_PIN'):
            R.select_stage(SOURCE_RAW, package_raw, terminal_raw, PERIOD_RAW,
                           review_raw, '0' * 64, NOW)
        with self.assertRaisesRegex(ValueError, 'PERIOD_CURRENT'):
            R.select_stage(SOURCE_RAW, package_raw, terminal_raw, PERIOD_RAW,
                           review_raw, A.sha(review_raw),
                           datetime(2026, 10, 21, 15, tzinfo=timezone.utc))

    def test_docker_envelope_requires_stage_identity_and_is_not_runnable(self):
        with self.assertRaisesRegex(R.Refused, 'UNREVIEWED_STAGE_IDENTITY'):
            R.docker_envelope(0, 1, '0' * 64)
        envelope = R.docker_envelope(3, 7, 'a' * 64)
        self.assertEqual(envelope['stage_id'], '3:7')
        self.assertEqual(envelope['network'], 'none')
        self.assertTrue(envelope['stage_bind']['read_only'])
        self.assertFalse(envelope['create_argv_available'])
        self.assertEqual(envelope['entrypoint'], 'UNBOUND_NEW_READER_RELEASE_REQUIRED')

    def test_stage_and_reader_effect_refuse(self):
        with self.assertRaisesRegex(R.Refused, 'EFFECT_DISABLED_STAGE_RELEASE_REQUIRED'):
            R.execute_stage()
        with self.assertRaisesRegex(R.Refused, 'EFFECT_DISABLED_READER_RELEASE_REQUIRED'):
            R.execute_reader()


if __name__ == '__main__':
    unittest.main()
