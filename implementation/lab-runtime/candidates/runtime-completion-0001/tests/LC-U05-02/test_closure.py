import bootstrap
from bootstrap import R,E,S,checked
import argparse,copy,json,tempfile,unittest
from pathlib import Path
from lab_contracts.codec import canonical,sha,Refusal
from lab_packaging.selection import prepare
from fixtures import public_selection,full_payload,ORIGINAL_RAW,PRIOR_RAW,terminal

class ClosureTests(unittest.TestCase):
    def setUp(self):self.reader,self.policy=public_selection()
    def run_selection(self,policy=None,original=None,pin=None):
        raw=canonical(policy or self.policy)
        return prepare(self.reader,raw,pin or sha(raw),original or ORIGINAL_RAW,PRIOR_RAW,repository=str(R))
    def refusal(self,change):
        p=copy.deepcopy(self.policy);change(p)
        with self.assertRaisesRegex(Refusal,'^PUBLIC_PACKAGE_REFUSED$'):self.run_selection(p)
    def test_complete_720_originals_and_290_members(self):
        p=self.run_selection();self.assertEqual(p.manifest['input_occurrences'],720);self.assertEqual(p.manifest['wheel_members'],290)
        self.assertEqual(len(p.files),1011);self.assertFalse(p.manifest['source_rebuild_reproduced'])
        raw=p.verify();self.assertNotIn(b'/home/',raw);self.assertNotIn(b'private',raw)
        self.assertNotIn('original_value',p.manifest);self.assertEqual(p.manifest['construction'],'exact-prebuilt')
    def test_missing_public_export_permission(self):self.refusal(lambda p:p.pop('purpose'))
    def test_actual_authority_is_not_fixture_export(self):self.refusal(lambda p:p.update(posture='actual'))
    def test_protected_body_is_never_read(self):
        calls=[]
        class Provider:
            def read(self,*a,**kw):calls.append(1);raise RuntimeError('PRIVATE_MARKER')
        self.reader.protected_provider=Provider()
        self.refusal(lambda p:p['reads'][0]['binding'].update(kind='protected-input'));self.assertEqual(calls,[])
    def test_coherent_original_unused_stdlib_omission(self):
        value=json.loads(ORIGINAL_RAW);i=next(i for i,r in enumerate(value['inputs']) if r['kind']=='stdlib' and r['destination'] not in value['elf_graph'])
        r=value['inputs'].pop(i);self.policy['reads'].pop(i);self.policy['exports'].pop(r['destination'])
        with self.assertRaises(Refusal):self.run_selection(original=canonical(value))
    def test_coherent_original_abi_omission(self):
        value=json.loads(ORIGINAL_RAW);i=next(i for i,r in enumerate(value['inputs']) if r['kind']=='host-abi')
        r=value['inputs'].pop(i);self.policy['reads'].pop(i);self.policy['exports'].pop(r['destination']);value['elf_graph'].pop(r['destination'])
        with self.assertRaises(Refusal):self.run_selection(original=canonical(value))
    def test_original_order_preserved(self):
        v=json.loads(ORIGINAL_RAW);v['inputs'].reverse();self.policy['reads'].reverse()
        with self.assertRaises(Refusal):self.run_selection(original=canonical(v))
    def test_export_omission(self):self.refusal(lambda p:p['exports'].pop(next(iter(p['exports']))))
    def test_export_mode_change(self):self.refusal(lambda p:p['exports']['bin/python'].update(mode=0o777))
    def test_same_name_wrong_library_hash(self):self.refusal(lambda p:p['exports']['lib/abi/libsqlite3.so.0'].update(sha256='0'*64))
    def test_unselected_source_alias_refuses(self):self.refusal(lambda p:p['reads'][0]['binding'].update(root_id='same-byte-foreign-root'))
    def test_duplicate_read_cannot_hide_omission(self):self.refusal(lambda p:p['reads'].__setitem__(1,copy.deepcopy(p['reads'][0])))
    def test_wrong_expected_export_anchor(self):
        with self.assertRaises(Refusal):self.run_selection(pin='0'*64)
    def test_export_provenance_locators_not_permitted(self):self.refusal(lambda p:p['exports'].update({'proof/private-locator.json':{'sha256':'0'*64,'size_bytes':1,'mode':0o644}}))
    def test_unknown_policy_fields_refuse(self):self.refusal(lambda p:p.update(new_permission=True))
    def test_reordered_read_table_refuses(self):self.refusal(lambda p:p['reads'].reverse())
    def test_qualified_module_origin_does_not_replace_third_party_packaging(self):
        import lab_packaging
        self.assertEqual(Path(lab_packaging.__file__),S/'packaging/lab_packaging/__init__.py')
        self.assertFalse((S/'packaging/__init__.py').exists())
    def test_exact_native_build_provenance_is_distinct_from_reproduction(self):
        value=json.loads(checked(E/'native-build-provenance-0001.json','7284d6c3d2a11cc19aa3fbf21fe4760ae1c608b24c1fe6110015565b4c97ba66'))
        self.assertEqual(len(value['registry_archives']),32);self.assertEqual(len(value['selected_inputs']),51)
        self.assertFalse(value['build_executed']);self.assertFalse(value['source_rebuild_reproduced'])
        self.assertEqual(len(value['missing_reproducible_build_prerequisites']),5)
        self.assertFalse(value['excluded_original_rows'][0]['body_read'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);a=p.parse_args()
    if a.temp_root!=E:raise ValueError('owned root')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ClosureTests));raise SystemExit(terminal(result,[]))
