"""Synthetic selection tests; no protected material or role effect."""
import sys
import importlib.util
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adapter as C


def fixture():
    M = C.mapper_adapter()
    test_path = C.MAPPER_ADAPTER.parent / 'test_adapter.py'
    spec = importlib.util.spec_from_file_location('cal_mapper_selector_tests', test_path)
    mapper_tests = importlib.util.module_from_spec(spec)
    original = sys.modules['adapter']
    sys.modules['adapter'] = M
    try:
        spec.loader.exec_module(mapper_tests)
    finally:
        sys.modules['adapter'] = original
    upstream = mapper_tests.fixture()
    selected = M.select(**upstream)
    manifest_raw = M.encoded(selected['mapper_manifest'])
    package = {'schema_version':'lab-mapped-context-package/v1-candidate',
               'authority_effect':'none','actual_owner_outcome':None,
               'source_manifest_binding':{'path':C.MAPPER+'/source-manifest.json',
                                          'sha256':selected['mapper_manifest_sha256']},
               'files':[{'path':C.MAPPER+'/packages/0001/'+name,
                         'sha256':f'{index+1:064x}'}
                        for index,name in enumerate(selected['expected_package_members'])
                        if name != 'manifest.json']}
    package_raw = C.encoded(package)
    terminal_raw = C.encoded({'overall':'PASS','operation':'PASS','cleanup':'PASS',
                              'no_retry':True,'package_manifest_sha256':C.sha(package_raw)})
    external_raw = C.encoded({'schema':'lab-successor-mapper-external-exit/v1',
                              'attempt':str(C.MAPPER_ATTEMPT),'exit_code':0})
    review_raw = C.encoded({'schema':'lab-successor-mapper-effect-review/v1',
                            'verdict':'PASS_BOUNDED_MAPPER_COLD_NATIVE',
                            'attempt':str(C.MAPPER_ATTEMPT),
                            'source_manifest_sha256':M.reader_adapter().SOURCE_MANIFEST_SHA,
                            'source_package_manifest_sha256':selected['source_package_manifest_sha256'],
                            'reader_manifest_sha256':selected['reader_manifest_sha256'],
                            'mapper_manifest_sha256':selected['mapper_manifest_sha256'],
                            'mapper_package_manifest_sha256':C.sha(package_raw),
                            'terminal_sha256':C.sha(terminal_raw),
                            'external_sha256':C.sha(external_raw)})
    return dict(**upstream,mapper_manifest_raw=manifest_raw,
                mapper_package_raw=package_raw,mapper_terminal_raw=terminal_raw,
                mapper_external_raw=external_raw,mapper_review_raw=review_raw,
                outside_mapper_review_sha=C.sha(review_raw))


class ContextSelectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = fixture()

    def test_fresh_family_is_bound_through_context_and_api(self):
        result = C.select(**self.data)
        self.assertEqual(result['status'],'CONTEXT_DYNAMIC_SELECTION_ONLY')
        self.assertFalse(result['effect_enabled'])
        self.assertEqual(result['context_launch'],'REFUSED')
        self.assertEqual(len(result['projected_api']),5)
        self.assertEqual(len(result['projected_context']),7)
        selection = C.parse(result['projected_api']['source-selection.json'])
        self.assertEqual(selection['mapper_package_binding']['sha256'],
                         C.sha(self.data['mapper_package_raw']))
        self.assertEqual(C.parse(result['projected_context']['implementation-binding.json'])
                         ['code_binding']['ref'], '/workspace/'+C.READER+'/reader.py')
        self.assertIn(C.MAPPER.rsplit('/',1)[-1].encode(),
                      result['projected_context']['base.py'])
        self.assertNotIn(C.OLD['mapper'].encode(),result['projected_context']['base.py'])

    def test_outside_mapper_review_pin_and_join(self):
        data=dict(self.data,outside_mapper_review_sha='0'*64)
        with self.assertRaisesRegex(C.Refused,'OUTSIDE_MAPPER_REVIEW_PIN'):
            C.select(**data)
        review=C.parse(self.data['mapper_review_raw'])
        review['reader_manifest_sha256']='0'*64
        raw=C.encoded(review)
        data=dict(self.data,mapper_review_raw=raw,outside_mapper_review_sha=C.sha(raw))
        with self.assertRaisesRegex(C.Refused,'INDEPENDENT_MAPPER_EFFECT_JOIN'):
            C.select(**data)

    def test_package_and_exit_cannot_be_assumed(self):
        data=dict(self.data,mapper_package_raw=b'{}\n')
        with self.assertRaisesRegex(C.Refused,'MAPPER_PACKAGE_BINDING'):
            C.select(**data)
        external=C.parse(self.data['mapper_external_raw'])
        external['exit_code']=1
        data=dict(self.data,mapper_external_raw=C.encoded(external))
        with self.assertRaisesRegex(C.Refused,'MAPPER_EXTERNAL_OS_JOIN'):
            C.select(**data)

    def test_old_mapper_manifest_and_context_effect_refused(self):
        data=dict(self.data,mapper_manifest_raw=b'{}\n')
        with self.assertRaisesRegex(C.Refused,'MAPPER_MANIFEST_DYNAMIC_JOIN'):
            C.select(**data)
        with self.assertRaisesRegex(C.Refused,'EFFECT_DISABLED'):
            C.execute_context()


if __name__=='__main__':
    unittest.main()
