"""Proof rows and disclosure selectors cannot be silently omitted or redirected."""
import copy
import io
import json
from pathlib import Path
import time
import unittest
import closure_hardened_0003 as C

COMPONENT=Path(__file__).resolve().parent
RUN=C.ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002'
SELECTION=RUN/'dependency-selection-0002.json'
PIN=json.loads((RUN/'selection-pin-0002.json').read_text())['sha256']

class Provenance(unittest.TestCase):
    def setUp(self):self.selection,_=C.load_selection(SELECTION,PIN)
    def reject(self,mutator,message):
        selected=copy.deepcopy(self.selection);mutator(selected)
        with self.assertRaisesRegex(ValueError,message):C.strict_structure(selected)
    def test_exact_all_five_original_bindings_verified(self):
        report=C.preflight(SELECTION,PIN);self.assertTrue(report['complete_original_bindings_required'])
    def test_each_omitted_original_binding_is_refused(self):
        for index in range(5):
            with self.subTest(index=index):self.reject(lambda x:x['original_bindings'].pop(index),'complete exact original bindings')
    def test_duplicate_original_binding_is_refused(self):self.reject(lambda x:x['original_bindings'].append(x['original_bindings'][0]),'complete exact original bindings')
    def test_redirected_original_binding_is_refused(self):self.reject(lambda x:x['original_bindings'][0].__setitem__('path','operator-state.json'),'complete exact original bindings')
    def test_renamed_or_changed_native_digest_is_refused(self):self.reject(lambda x:next(r for r in x['inputs'] if r['kind']=='native-executable').__setitem__('sha256','0'*64),'original native digest')
    def test_changed_wheel_digest_is_refused(self):self.reject(lambda x:next(r for r in x['inputs'] if r['kind']=='wheel').__setitem__('sha256','0'*64),'original wheel digest')
    def test_changed_interpreter_digest_is_refused(self):self.reject(lambda x:next(r for r in x['inputs'] if r['kind']=='interpreter').__setitem__('sha256','0'*64),'original interpreter digest')
    def test_redirected_wheel_elf_path_is_refused_before_read(self):self.reject(lambda x:x['wheel_elf_bindings'][0].__setitem__('path','/home/vlad_/.private/operator.json'),'wheel ELF original provenance')
    def test_duplicate_wheel_elf_binding_is_refused(self):self.reject(lambda x:x['wheel_elf_bindings'].append(x['wheel_elf_bindings'][0]),'duplicate wheel ELF binding')
    def test_changed_abi_soname_target_is_refused(self):
        def change(x):
            row=next(r for r in x['inputs'] if r['kind']=='host-abi' and r['soname']=='libsqlite3.so.0');row['path']=str(C.BASE.resolve_soname('libc.so.6'))
        self.reject(change,'host ABI soname target')
    def test_inspection_tool_cannot_be_redirected(self):self.reject(lambda x:x['inspection_tool'].__setitem__('path','/home/vlad_/untrusted'),'closed exact inspection tool')
    def test_unknown_wheel_binding_fields_refused(self):self.reject(lambda x:x['wheel_elf_bindings'][0].__setitem__('grant','invented'),'closed wheel ELF binding')
    def test_actual_retained_successor_cold_probe(self):
        result=C.cold_probe(COMPONENT/'installations/0002',self.selection)
        self.assertEqual(result['result'],'PASS');self.assertTrue(result['python']['utf8_roundtrip'])

def main():
    out=io.StringIO();start=time.monotonic();result=unittest.TextTestRunner(stream=out,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Provenance))
    report={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'result':'PASS' if result.wasSuccessful() else 'FAIL','output':out.getvalue(),'selection_sha256':PIN,'elapsed_seconds':time.monotonic()-start,'task_complete':False}
    with (RUN/'provenance-tests-0002.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print(out.getvalue());return 0 if result.wasSuccessful() else 1

if __name__=='__main__':raise SystemExit(main())
