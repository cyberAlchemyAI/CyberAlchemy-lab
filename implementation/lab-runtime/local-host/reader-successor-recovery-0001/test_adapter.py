import copy
from datetime import datetime, timezone, timedelta
import unittest

import adapter as A


NOW = datetime(2026, 10, 20, 15, 30, tzinfo=timezone.utc)
SOURCE_RAW = (A.PROFILE / 'generated' / A.SOURCE / 'source-manifest.json').read_bytes()
PERIOD = {'not_before':'2026-10-20T15:00:00+00:00',
          'expires_at':'2026-10-21T15:00:00+00:00'}


def fixture():
    period_raw = A.encoded(PERIOD)
    archive = {'path':A.SOURCE+'/packages/0001/branch.snapshot','sha256':'a'*64}
    period = {'path':A.SOURCE+'/packages/0001/period.json','sha256':A.sha(period_raw)}
    rows = [archive,period] + [
        {'path':A.SOURCE+f'/packages/0001/file-{i:02d}.json','sha256':f'{i:064x}'}
        for i in range(34)]
    package = {'files':rows,'archive_binding':archive,'period_binding':period,
               'source_manifest_binding':{'path':A.SOURCE+'/source-manifest.json',
                                          'sha256':A.SOURCE_MANIFEST_SHA}}
    package_raw = A.encoded(package)
    terminal = {'overall':'PASS','operation':'PASS','cleanup':'PASS',
                'no_retry':True,'package_manifest_sha256':A.sha(package_raw)}
    terminal_raw = A.encoded(terminal)
    review = {'schema':'lab-successor-source-effect-review/v1',
              'verdict':'PASS_BOUNDED_SOURCE_ONLY_EFFECT',
              'source_manifest_sha256':A.SOURCE_MANIFEST_SHA,
              'package_manifest_sha256':A.sha(package_raw),
              'terminal_sha256':A.sha(terminal_raw),'attempt':str(A.SOURCE_ATTEMPT)}
    review_raw = A.encoded(review)
    return package,terminal,review,period_raw,package_raw,terminal_raw,review_raw


class AdapterTests(unittest.TestCase):
    def select(self, package_raw,terminal_raw,period_raw,review_raw,now=NOW):
        return A.select(SOURCE_RAW,package_raw,terminal_raw,period_raw,review_raw,
                        A.sha(review_raw),now)

    def test_dynamic_package_selection_and_role_projection(self):
        _,_,_,period_raw,package_raw,terminal_raw,review_raw=fixture()
        result=self.select(package_raw,terminal_raw,period_raw,review_raw)
        self.assertEqual(result['status'],'DYNAMIC_READER_SELECTION_ONLY')
        self.assertEqual(result['source_package_manifest_sha256'],A.sha(package_raw))
        self.assertEqual(len(result['projected_roles']),7)
        self.assertEqual(len(result['reader_manifest']['files']),948)
        self.assertFalse(result['effect_enabled'])

    def test_missing_or_forged_source_effect_review_refused(self):
        _,_,review,period_raw,package_raw,terminal_raw,review_raw=fixture()
        review['package_manifest_sha256']='0'*64
        with self.assertRaisesRegex(A.Refused,'INDEPENDENT_SOURCE_EFFECT_JOIN'):
            self.select(package_raw,terminal_raw,period_raw,A.encoded(review))
        with self.assertRaisesRegex(A.Refused,'OUTSIDE_EFFECT_REVIEW_PIN'):
            A.select(SOURCE_RAW,package_raw,terminal_raw,period_raw,review_raw,'0'*64,NOW)

    def test_package_and_terminal_drift_refused(self):
        package,terminal,review,period_raw,package_raw,terminal_raw,review_raw=fixture()
        package['archive_binding']['sha256']='b'*64
        with self.assertRaisesRegex(A.Refused,'SOURCE_TERMINAL'):
            self.select(A.encoded(package),terminal_raw,period_raw,review_raw)
        terminal['overall']='UNKNOWN'
        with self.assertRaisesRegex(A.Refused,'SOURCE_TERMINAL'):
            self.select(package_raw,A.encoded(terminal),period_raw,review_raw)

    def test_period_boundary_refused(self):
        _,_,_,period_raw,package_raw,terminal_raw,review_raw=fixture()
        with self.assertRaisesRegex(A.Refused,'PERIOD_CURRENT'):
            self.select(package_raw,terminal_raw,period_raw,review_raw,
                        datetime(2026,10,21,15,tzinfo=timezone.utc))

    def test_reader_effect_refused_and_live_absent(self):
        self.assertEqual(A.probe_live()['status'],'SOURCE_EFFECT_NOT_PRESENT')
        with self.assertRaisesRegex(A.Refused,'EFFECT_DISABLED'):
            A.execute_reader()


if __name__=='__main__':
    unittest.main()
