from datetime import datetime,timezone
import unittest

import adapter as M


NOW=datetime(2026,10,20,15,30,tzinfo=timezone.utc)


def fixture():
    A=M.reader_adapter()
    source_raw=(A.PROFILE/'generated'/A.SOURCE/'source-manifest.json').read_bytes()
    period={'not_before':'2026-10-20T15:00:00+00:00',
            'expires_at':'2026-10-21T15:00:00+00:00'}
    period_raw=A.encoded(period)
    archive={'path':A.SOURCE+'/packages/0001/branch.snapshot','sha256':'a'*64}
    period_binding={'path':A.SOURCE+'/packages/0001/period.json','sha256':A.sha(period_raw)}
    rows=[archive,period_binding]+[
        {'path':A.SOURCE+f'/packages/0001/file-{i:02d}.json','sha256':f'{i:064x}'}
        for i in range(34)]
    package={'files':rows,'archive_binding':archive,'period_binding':period_binding,
             'source_manifest_binding':{'path':A.SOURCE+'/source-manifest.json',
                                        'sha256':A.SOURCE_MANIFEST_SHA}}
    package_raw=A.encoded(package)
    source_terminal_raw=A.encoded({'overall':'PASS','operation':'PASS','cleanup':'PASS',
        'no_retry':True,'package_manifest_sha256':A.sha(package_raw)})
    source_review_raw=A.encoded({'schema':'lab-successor-source-effect-review/v1',
        'verdict':'PASS_BOUNDED_SOURCE_ONLY_EFFECT','source_manifest_sha256':A.SOURCE_MANIFEST_SHA,
        'package_manifest_sha256':A.sha(package_raw),
        'terminal_sha256':A.sha(source_terminal_raw),'attempt':str(A.SOURCE_ATTEMPT)})
    selected=A.select(source_raw,package_raw,source_terminal_raw,period_raw,
                      source_review_raw,A.sha(source_review_raw),NOW)
    reader_manifest_raw=A.encoded(selected['reader_manifest'])
    receipt_raw=M.encoded({'schema_version':'lab-disposable-reader-receipt/v1-private',
        'reader_manifest_sha256':A.sha(reader_manifest_raw),
        'source_manifest_sha256':A.SOURCE_MANIFEST_SHA,
        'source_package_manifest_sha256':A.sha(package_raw),
        'authority_effect':'none','actual_owner_outcome':None})
    terminal_raw=M.encoded({'overall':'PASS','operation':'PASS','cleanup':'PASS',
        'reader_effect':'DISPOSABLE_READER_DIAGNOSTIC','receipt_sha256':M.sha(receipt_raw),
        'no_retry':True})
    external_raw=M.encoded({'schema':'lab-successor-reader-external-exit/v1',
        'exit_code':0,'attempt':str(M.READER_ATTEMPT)})
    review_raw=M.encoded({'schema':'lab-successor-reader-effect-review/v1',
        'verdict':'PASS_BOUNDED_READER_COLD_OPEN','attempt':str(M.READER_ATTEMPT),
        'source_manifest_sha256':A.SOURCE_MANIFEST_SHA,
        'source_package_manifest_sha256':M.sha(package_raw),
        'reader_manifest_sha256':M.sha(reader_manifest_raw),
        'receipt_sha256':M.sha(receipt_raw),'terminal_sha256':M.sha(terminal_raw),
        'external_sha256':M.sha(external_raw)})
    return dict(source_manifest_raw=source_raw,source_package_raw=package_raw,
        source_terminal_raw=source_terminal_raw,period_raw=period_raw,
        source_review_raw=source_review_raw,outside_source_review_sha=M.sha(source_review_raw),
        reader_manifest_raw=reader_manifest_raw,reader_receipt_raw=receipt_raw,
        reader_terminal_raw=terminal_raw,reader_external_raw=external_raw,
        reader_review_raw=review_raw,outside_reader_review_sha=M.sha(review_raw),now=NOW)


class MapperSelectorTests(unittest.TestCase):
    def test_dynamic_selection_projects_original_mapper_and_55_members(self):
        data=fixture()
        result=M.select(**data)
        self.assertEqual(result['status'],'MAPPER_DYNAMIC_SELECTION_ONLY')
        self.assertEqual(len(result['mapper_manifest']['files']),953)
        self.assertEqual(len(result['expected_package_members']),55)
        self.assertEqual(result['output_contract']['function'],'verify_mapped_output')
        self.assertEqual(result['source_package_manifest_sha256'],M.sha(data['source_package_raw']))
        self.assertIn(data['outside_reader_review_sha'],result['reader_effect_review_sha256'])
        self.assertFalse(result['effect_enabled'])

    def test_reader_effect_review_independence_refused(self):
        data=fixture()
        data['outside_reader_review_sha']='0'*64
        with self.assertRaisesRegex(M.Refused,'OUTSIDE_READER_REVIEW_PIN'):
            M.select(**data)
        data=fixture()
        review=M.parse(data['reader_review_raw'])
        review['reader_manifest_sha256']='0'*64
        data['reader_review_raw']=M.encoded(review)
        data['outside_reader_review_sha']=M.sha(data['reader_review_raw'])
        with self.assertRaisesRegex(M.Refused,'INDEPENDENT_READER_EFFECT_JOIN'):
            M.select(**data)

    def test_reader_receipt_or_external_exit_refused(self):
        data=fixture()
        receipt=M.parse(data['reader_receipt_raw'])
        receipt['source_package_manifest_sha256']='0'*64
        data['reader_receipt_raw']=M.encoded(receipt)
        with self.assertRaisesRegex(M.Refused,'READER_RECEIPT_JOIN'):
            M.select(**data)
        data=fixture()
        external=M.parse(data['reader_external_raw'])
        external['exit_code']=2
        data['reader_external_raw']=M.encoded(external)
        with self.assertRaisesRegex(M.Refused,'READER_EXTERNAL_OS_JOIN'):
            M.select(**data)

    def test_old_reader_manifest_and_period_refused(self):
        data=fixture()
        data['reader_manifest_raw']=b'{}\n'
        with self.assertRaisesRegex(M.Refused,'READER_MANIFEST_DYNAMIC_JOIN'):
            M.select(**data)
        data=fixture()
        data['now']=datetime(2026,10,21,15,tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError,'PERIOD_CURRENT'):
            M.select(**data)

    def test_effect_refused(self):
        with self.assertRaisesRegex(M.Refused,'EFFECT_DISABLED'):
            M.execute_mapper()


if __name__=='__main__':
    unittest.main()
