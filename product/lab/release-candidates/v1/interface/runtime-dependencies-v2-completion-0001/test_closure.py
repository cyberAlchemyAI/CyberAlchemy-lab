"""Actual bundled cold startup and fail-closed dependency mutations."""
import copy
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import time
import unittest
import closure as C

COMPONENT=Path(__file__).resolve().parent
RUN=C.ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002'
SELECTION=RUN/'dependency-selection-0002.json'
PIN=json.loads((RUN/'selection-pin-0002.json').read_text())['sha256']

class RuntimeClosure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent=COMPONENT/'test-owned-0001'
        cls.parent.mkdir(mode=0o700) # Exclusive and retained; never adopt a prior test generation.
        info=cls.parent.stat();cls.parent_identity=(info.st_dev,info.st_ino)
        cls.selection,_=C.load_selection(SELECTION,PIN)
        cls.report=C.install(SELECTION,PIN,cls.parent,cls.parent_identity,'candidate')
        cls.destination=cls.parent/'candidate'

    def variation(self,label,mutator):
        selection=copy.deepcopy(self.selection);mutator(selection)
        raw=(json.dumps(selection,sort_keys=True,indent=2)+'\n').encode()
        p=self.parent/(label+'.json');p.write_bytes(raw);return p,C.sha(raw)

    def test_actual_full_cold_closure_versions_and_functional_probes(self):
        probe=C.cold_probe(self.destination,self.selection)
        self.assertEqual(probe['result'],'PASS')
        self.assertTrue(probe['python']['sqlite_transaction'])
        self.assertTrue(probe['python']['utf8_roundtrip'])
        self.assertTrue(probe['python']['ed25519_signature'])
        self.assertTrue(probe['python']['schema_validation'])
        self.assertTrue(probe['python']['compression_roundtrips'])
        self.assertFalse(probe['full_lab_startup_proven'])
        self.assertFalse(probe['protected_inputs_provisioned'])

    def test_every_loaded_python_and_elf_origin_is_bundled(self):
        p=self.report['cold_probe']['python']
        self.assertTrue(p['mapped_files']);self.assertGreater(len(p['module_origins']),100)
        self.assertTrue(all(Path(x).is_relative_to(self.destination) for x in p['mapped_files']))
        self.assertTrue(all(Path(x).is_relative_to(self.destination) for x in p['module_origins'].values()))

    def test_host_stdlib_is_bundled_and_sqlite_has_recursive_library(self):
        files=C.installed_files(self.selection)
        self.assertIn('lib/python3.14/lib-dynload/_sqlite3.cpython-314-x86_64-linux-gnu.so',files)
        self.assertIn('lib/abi/libsqlite3.so.0',files)
        self.assertTrue(any(r['kind']=='stdlib' for r in self.selection['inputs']))
        self.assertNotIn('lib/python3.14/sitecustomize.py',files)

    def test_missing_declared_transitive_library_refuses_selection(self):
        p,pin=self.variation('missing-sqlite',lambda x:x['elf_graph'].pop('lib/abi/libsqlite3.so.0'))
        with self.assertRaisesRegex(ValueError,'transitive ELF dependency missing'):C.load_selection(p,pin)

    def test_removed_actual_edge_refuses_preflight(self):
        p,pin=self.variation('omitted-edge',lambda x:x['elf_graph']['bin/python']['needed'].remove('libm.so.6'))
        with self.assertRaisesRegex(ValueError,'actual ELF dependency graph differs'):C.preflight(p,pin)

    def test_omitted_wheel_elf_refuses_preflight(self):
        def remove(x):
            row=x['wheel_elf_bindings'].pop();x['elf_graph'].pop(row['destination'])
        p,pin=self.variation('omitted-wheel-elf',remove)
        with self.assertRaisesRegex(ValueError,'wheel ELF closure omitted'):C.preflight(p,pin)

    def test_omitted_standard_library_file_refuses_preflight(self):
        p,pin=self.variation('omitted-stdlib',lambda x:x['inputs'].remove(next(r for r in x['inputs'] if r['kind']=='stdlib' and r['path'].endswith('/pathlib/__init__.py'))))
        with self.assertRaisesRegex(ValueError,'standard library inventory differs'):C.preflight(p,pin)

    def test_changed_public_private_class_refuses(self):
        p,pin=self.variation('false-class',lambda x:x['inputs'][0].__setitem__('classification','protected-key'))
        with self.assertRaisesRegex(ValueError,'disclosure class differs'):C.load_selection(p,pin)

    def test_unsupported_architecture_refuses_before_installation(self):
        p,pin=self.variation('wrong-architecture',lambda x:x['environment'].__setitem__('machine','aarch64'))
        with self.assertRaisesRegex(ValueError,'unsupported dependency environment'):C.install(p,pin,self.parent,self.parent_identity,'unsupported')
        self.assertFalse((self.parent/'unsupported').exists())

    def test_full_original_proof_cannot_be_replaced_with_execution_subset(self):
        p,pin=self.variation('truncated-proof',lambda x:x['original_full_proof'].__setitem__('rows',720))
        with self.assertRaisesRegex(ValueError,'full original proof binding differs'):C.load_selection(p,pin)

    def test_existing_generation_and_foreign_sibling_remain_exact(self):
        native=(self.destination/'bin/lab-context-native-reader').read_bytes()
        with self.assertRaises(FileExistsError):C.install(SELECTION,PIN,self.parent,self.parent_identity,'candidate')
        self.assertEqual((self.destination/'bin/lab-context-native-reader').read_bytes(),native)
        sibling=self.parent/'foreign';sibling.mkdir();(sibling/'keep').write_bytes(b'preserve foreign bytes')
        with self.assertRaises(FileExistsError):C.install(SELECTION,PIN,self.parent,self.parent_identity,'foreign')
        self.assertEqual((sibling/'keep').read_bytes(),b'preserve foreign bytes')

    def test_wrong_selected_parent_identity_refuses(self):
        with self.assertRaisesRegex(ValueError,'identity differs'):C.install(SELECTION,PIN,self.parent,(self.parent_identity[0],self.parent_identity[1]+1),'wrong-parent')
        self.assertFalse((self.parent/'wrong-parent').exists())

    def test_changed_sqlite_library_refuses_before_execution(self):
        p=self.destination/'lib/abi/libsqlite3.so.0';raw=p.read_bytes()
        try:
            p.write_bytes(bytes([raw[0]^1])+raw[1:])
            with self.assertRaisesRegex(ValueError,'digest differs'):C.cold_probe(self.destination,self.selection)
        finally:p.write_bytes(raw)
        C.verify_installed(self.destination,self.selection)

    def test_missing_sqlite_library_refuses_before_execution(self):
        p=self.destination/'lib/abi/libsqlite3.so.0';saved=self.parent/'temporarily-selected-sqlite';p.rename(saved)
        try:
            with self.assertRaises(FileNotFoundError):C.cold_probe(self.destination,self.selection)
        finally:saved.rename(p)

    def test_symlinked_sqlite_module_refuses_before_execution(self):
        p=self.destination/'lib/python3.14/lib-dynload/_sqlite3.cpython-314-x86_64-linux-gnu.so';saved=self.parent/'temporarily-selected-module';p.rename(saved);p.symlink_to(saved)
        try:
            with self.assertRaises(OSError):C.cold_probe(self.destination,self.selection)
        finally:p.unlink();saved.rename(p)

    def test_changed_native_execute_mode_refuses_before_execution(self):
        p=self.destination/'bin/lab-context-native-reader';p.chmod(0o644)
        try:
            with self.assertRaisesRegex(ValueError,'mode differs'):C.cold_probe(self.destination,self.selection)
        finally:p.chmod(0o755)

    def test_extra_installed_hook_refuses_before_execution(self):
        p=self.destination/'lib/python3.14/sitecustomize.py';p.write_bytes(b'raise RuntimeError("unselected hook")\n')
        try:
            with self.assertRaisesRegex(ValueError,'unexpected installed dependency bytes'):C.cold_probe(self.destination,self.selection)
        finally:p.unlink()

    def test_hostile_python_environment_cannot_replace_selected_origins(self):
        code="import sys,json,sqlite3;print(json.dumps({'path':sys.path,'sqlite':sqlite3.__file__}))"
        env=dict(C.ENV,PYTHONPATH='/nonexistent/untrusted',PYTHONHOME='/nonexistent/untrusted',PYTHONUSERBASE='/nonexistent/untrusted',LD_LIBRARY_PATH='/nonexistent/untrusted')
        result=subprocess.run(C.python_command(self.destination,code),env=env,capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        value=json.loads(result.stdout);self.assertTrue(Path(value['sqlite']).is_relative_to(self.destination));self.assertTrue(all(Path(x).is_relative_to(self.destination) for x in value['path']))

    def test_exact_independent_selection_digest_required(self):
        p=self.parent/'tampered-selection.json';p.write_bytes(SELECTION.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'independent closure selection differs'):C.preflight(p,PIN)

    def test_final_originals_and_owned_public_generation_unchanged(self):
        C.preflight(SELECTION,PIN);C.verify_installed(self.destination,self.selection)

def main():
    stream=io.StringIO();start=time.monotonic();suite=unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeClosure)
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    report={'schema_version':'lab-runtime-dependency-closure-tests/v2-candidate','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'result':'PASS' if result.wasSuccessful() else 'FAIL','elapsed_seconds':time.monotonic()-start,'selection_sha256':PIN,'output':stream.getvalue(),'retained_owned_test_parent':str(COMPONENT/'test-owned-0001'),'task_complete':False,'goal_complete':False,'authority_effect':'none'}
    with (RUN/'test-report-0001.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print(stream.getvalue());return 0 if result.wasSuccessful() else 1

if __name__=='__main__':raise SystemExit(main())
