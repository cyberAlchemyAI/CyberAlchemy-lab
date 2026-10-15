"""Causal local file/environment refusals in newly owned copies."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
spec=importlib.util.spec_from_file_location('_cal_dependency_preflight_tested',HERE/'preflight.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
SELECTION=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/dependency-selection.json'

class Preflight(unittest.TestCase):
    def setUp(self):
        self.scope=tempfile.TemporaryDirectory(prefix='cal-T07-preflight-');self.addCleanup(self.scope.cleanup)
        self.root=Path(self.scope.name);self.root.chmod(0o700)
        self.original=self.root/'data.bin';self.original.write_bytes(b'exact independently selected technical fixture\n');self.original.chmod(0o600)
        self.pin=hashlib.sha256(self.original.read_bytes()).hexdigest()
    def selected_copy(self, document):
        path=self.root/'selection.json';raw=json.dumps(document,sort_keys=True).encode();path.write_bytes(raw)
        return path,hashlib.sha256(raw).hexdigest()
    def test_actual_closed_host_dependencies(self):
        v=M.verify(SELECTION,hashlib.sha256(SELECTION.read_bytes()).hexdigest())
        self.assertEqual(len(v['verified_inputs']),13);self.assertFalse(v['native_executed']);self.assertFalse(v['execution_authorized'])
    def test_actual_changed_bytes_refused(self):
        self.original.write_bytes(b'real changed bytes\n')
        with self.assertRaisesRegex(ValueError,'digest differs'):M.anchored_read(self.original,expected_sha256=self.pin)
    def test_final_symlink_refused_without_reading_target(self):
        link=self.root/'link.bin';link.symlink_to(self.original)
        with self.assertRaises(OSError):M.anchored_read(link,expected_sha256=self.pin)
        self.assertEqual(hashlib.sha256(self.original.read_bytes()).hexdigest(),self.pin)
    def test_ancestor_symlink_refused(self):
        directory=self.root/'directory';directory.mkdir();p=directory/'data.bin';p.write_bytes(self.original.read_bytes())
        (self.root/'alias').symlink_to(directory,target_is_directory=True)
        with self.assertRaises(OSError):M.anchored_read(self.root/'alias/data.bin',expected_sha256=self.pin)
    def test_actual_wrong_mode_refused(self):
        self.original.chmod(0o640)
        with self.assertRaisesRegex(ValueError,'mode differs'):M.anchored_read(self.original,expected_sha256=self.pin,expected_mode=0o600)
    def test_actual_wrong_size_refused(self):
        with self.assertRaisesRegex(ValueError,'size differs'):M.anchored_read(self.original,expected_sha256=self.pin,expected_size=1)
    def test_unsupported_environment_refused_before_dependencies(self):
        doc=json.loads(SELECTION.read_bytes());doc['environment']['machine']='unsupported-architecture'
        p,pin=self.selected_copy(doc)
        with self.assertRaisesRegex(ValueError,'environment differs'):M.verify(p,pin)
    def test_duplicate_selected_input_refused(self):
        doc=json.loads(SELECTION.read_bytes());doc['inputs'].append(copy.deepcopy(doc['inputs'][0]))
        p,pin=self.selected_copy(doc)
        with self.assertRaisesRegex(ValueError,'duplicate dependency path'):M.verify(p,pin)
    def test_credential_suffix_refused_before_open(self):
        with self.assertRaisesRegex(ValueError,'credential/cache'):M.anchored_read(self.root/'does-not-exist.pem',expected_sha256=self.pin)
    def test_independent_selector_tamper_refused(self):
        doc=json.loads(SELECTION.read_bytes());p,pin=self.selected_copy(doc);p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'selection differs'):M.verify(p,pin)

if __name__=='__main__':unittest.main(verbosity=2)
