"""Causal inert checks for the original staged Reader code-buffer closure."""
import builtins
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import checked_loader as c


class CheckedLoaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captured=c.capture()

    def test_public_capture_excludes_private_archive_and_reopens(self):
        self.assertEqual(len(self.captured.code),40)
        self.assertEqual(len(self.captured.engine_rows),45)
        self.assertEqual(len(self.captured.source_manifest['files']),940)
        self.assertEqual(len(self.captured.reader_rows),948)
        self.assertTrue(all(not p.endswith('branch.snapshot')
                            for p in self.captured.metadata_buffers))
        self.captured.guard_metadata()
        self.assertFalse(self.captured.summary()['host_environment_matches'])

    def test_manifest_row_escape_and_duplicate_refuse(self):
        digest='0'*64
        with self.assertRaisesRegex(c.Refused,'BOUND_ROW_PATH_OR_DIGEST'):
            c._bound_rows([{'path':'safe/../branch.snapshot','sha256':digest}],'safe/')
        with self.assertRaisesRegex(c.Refused,'BOUND_ROW_PATH_OR_DIGEST'):
            c._bound_rows([{'path':'safe/a','sha256':digest},
                           {'path':'safe/a','sha256':digest}],'safe/')

    def test_original_reader_loads_from_buffers_without_staged_code_open(self):
        actual_open=builtins.open
        actual_io_open=io.open
        def forbid(file,*args,**kwargs):
            if str(file).startswith(str(c.ROOT)) and str(file).endswith('.py'):
                raise AssertionError('staged code pathname reopened')
            return actual_open(file,*args,**kwargs)
        def forbid_io(file,*args,**kwargs):
            if str(file).startswith(str(c.ROOT)) and str(file).endswith('.py'):
                raise AssertionError('staged code pathname reopened')
            return actual_io_open(file,*args,**kwargs)
        with patch.object(builtins,'open',forbid),patch.object(io,'open',forbid_io):
            with c.checked_modules(self.captured) as (reader,finder):
                self.assertEqual(reader.SelectedReader.__module__,c.READER_NAME+'.reader')
                self.assertGreaterEqual(len(finder.executed),13)
                self.assertTrue(all(d==c.sha(self.captured.code[p])
                                    for _,p,d in finder.executed))

    def test_mutated_captured_code_refuses(self):
        changed=c.capture()
        key=str(c.ROOT/c.READER_ROLE/'reader.py')
        changed.code[key]=changed.code[key]+b'\n# altered after capture\n'
        with self.assertRaisesRegex(c.Refused,'EXECUTED_BUFFER_DRIFT'):
            with c.checked_modules(changed):pass

    def test_mutated_captured_metadata_refuses(self):
        changed=c.capture()
        key=next(iter(changed.metadata_buffers))
        changed.metadata_buffers[key]+=b'altered'
        with self.assertRaisesRegex(c.Refused,'CAPTURED_METADATA_BUFFER_DRIFT'):
            with c.checked_modules(changed):pass

    def test_stale_configuration_refuses_before_import(self):
        changed=c.capture()
        original=c.read_pin
        stale=next(iter(changed.metadata_buffers))
        def bad(path,expected,maximum=2*1024*1024):
            if str(path)==str(c.ROOT/stale):raise c.Refused('PIN_BYTES_OR_ID_DRIFT')
            return original(path,expected,maximum)
        with patch.object(c,'read_pin',bad):
            with self.assertRaisesRegex(c.Refused,'PIN_BYTES_OR_ID_DRIFT'):
                with c.checked_modules(changed):pass

    def test_dynamic_unselected_path_refuses(self):
        finder=c.CheckedFinder(self.captured)
        with self.assertRaisesRegex(c.Refused,'DYNAMIC_SELECTED_PATH_DRIFT'):
            finder.checked_spec_from_file_location(c.SOURCE_NAME,
                c.ROOT/c.SOURCE_ROLE/'swapped.py',submodule_search_locations=[str(c.ROOT/c.SOURCE_ROLE)])
        with self.assertRaisesRegex(c.Refused,'UNSELECTED_DYNAMIC_MODULE'):
            finder.checked_spec_from_file_location('unselected',c.ROOT/c.READER_ROLE/'reader.py')

    def test_engine_copied_path_is_buffer_backed(self):
        finder=c.CheckedFinder(self.captured)
        root=Path('/tmp/cal-R03-pinned-engine-0123456789/captured/implementation/lab-runtime/v2/lab_runtime')
        name=c.ENGINE_PREFIX+'0'*32
        spec=finder.checked_spec_from_file_location(name,root/'__init__.py',
            submodule_search_locations=[str(root)])
        self.assertEqual(spec.loader.raw,
                         self.captured.code[str(c.ROOT/c.CORRECTION_ROLE/'runtime/lab_runtime/__init__.py')])
        child=finder.find_spec(name+'.common')
        self.assertIsNotNone(child)
        self.assertEqual(child.loader.raw,
                         self.captured.code[str(c.ROOT/c.CORRECTION_ROLE/'runtime/lab_runtime/common.py')])
        package_module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(package_module)
        common_module=importlib.util.module_from_spec(child)
        child.loader.exec_module(common_module)
        self.assertEqual(package_module.__version__,'0.1.0')
        self.assertTrue(callable(common_module.byte_digest))
        with self.assertRaisesRegex(c.Refused,'ENGINE_CAPTURED_PATH_DRIFT'):
            finder.checked_spec_from_file_location(c.ENGINE_PREFIX+'1'*32,
                Path('/tmp/other/captured/implementation/lab-runtime/v2/lab_runtime/__init__.py'),
                submodule_search_locations=[str(root)])

    def test_synthetic_signed_scope_only(self):
        basis={'manifest_sha256':self.captured.selected['reader']['source_package_manifest_sha256'],
               'source_manifest_sha256':self.captured.selected['reader']['source_manifest_sha256'],
               'adapter_source_sha256':c.READER_MANIFEST_SHA}
        expected=self.captured.selected['scope_expected']
        signed=SimpleNamespace(guard=lambda:True,
            view=SimpleNamespace(data={'config':{'scope_ref':expected}}),
            sources=SimpleNamespace(scope_ref=expected),
            selected={'candidate_selection_basis':basis})
        self.assertEqual(c.observe_synthetic_scope(self.captured,signed)['actual_reader_open'],'NOT_RUN')
        signed.sources.scope_ref='forged'
        with self.assertRaisesRegex(c.Refused,'SYNTHETIC_SIGNED_SCOPE_OR_BASIS'):
            c.observe_synthetic_scope(self.captured,signed)
        with self.assertRaisesRegex(c.Refused,'EFFECT_DISABLED'):
            c.open_actual_signed()


if __name__=='__main__':unittest.main()
