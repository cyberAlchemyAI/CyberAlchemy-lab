"""Real exclusive installation and unsafe archive/ownership refusals."""
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
import zipfile
import install as I
import preflight as P

ROOT=Path(__file__).resolve().parents[6]
SELECTION=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/dependency-selection.json'
PIN=hashlib.sha256(SELECTION.read_bytes()).hexdigest()

class Installation(unittest.TestCase):
    def setUp(self):
        self.scope=tempfile.TemporaryDirectory(prefix='cal-T07-install-test-');self.addCleanup(self.scope.cleanup)
        self.root=Path(self.scope.name);self.root.chmod(0o700);s=self.root.stat();self.identity=(s.st_dev,s.st_ino)
    def archive(self,name='module.py',raw=b'# original technical fixture\n',mode=0o100644):
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as a:
            info=zipfile.ZipInfo(name);info.external_attr=mode<<16;a.writestr(info,raw)
        return data.getvalue()
    def test_real_empty_install_and_existing_generation_preserved(self):
        report=I.install(SELECTION,PIN,self.root,self.identity,'first')
        self.assertEqual(report['result'],'PASS');self.assertTrue(report['native_abi_entrypoint_probe']['expected_usage_observed'])
        native=self.root/'first/bin/lab-context-native-reader'
        self.assertEqual(native.stat().st_mode&0o777,0o755)
        original=(self.root/'first/installation.json').read_bytes()
        with self.assertRaises(FileExistsError):I.install(SELECTION,PIN,self.root,self.identity,'first')
        self.assertEqual((self.root/'first/installation.json').read_bytes(),original)
        self.assertFalse(report['native_history_replay_proven']);self.assertFalse(report['runtime_start_proven'])
    def test_existing_foreign_sibling_preserved(self):
        d=self.root/'foreign';d.mkdir();(d/'data').write_bytes(b'keep exact foreign bytes')
        with self.assertRaises(FileExistsError):I.install(SELECTION,PIN,self.root,self.identity,'foreign')
        self.assertEqual((d/'data').read_bytes(),b'keep exact foreign bytes')
    def test_wrong_selected_parent_inode_refused(self):
        with self.assertRaisesRegex(ValueError,'identity differs'):I.install(SELECTION,PIN,self.root,(self.identity[0],self.identity[1]+1),'fresh')
        self.assertFalse((self.root/'fresh').exists())
    def test_nonprivate_parent_refused(self):
        self.root.chmod(0o755)
        with self.assertRaisesRegex(ValueError,'mode0700'):I.install(SELECTION,PIN,self.root,self.identity,'fresh')
        self.assertFalse((self.root/'fresh').exists())
    def test_symlink_parent_refused(self):
        alias=self.root/'alias';alias.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(OSError):I.install(SELECTION,PIN,alias,self.identity,'fresh')
        self.assertFalse((self.root/'fresh').exists())
    def test_tampered_selection_before_directory_creation(self):
        document=self.root/'selection.json';document.write_bytes(SELECTION.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'selection differs'):I.install(document,PIN,self.root,self.identity,'fresh')
        self.assertFalse((self.root/'fresh').exists())
    def test_original_copy_refuses_changed_input(self):
        p=self.root/'input.bin';p.write_bytes(b'changed');p.chmod(0o600)
        row={'path':str(p),'sha256':P.digest(b'original'),'size_bytes':7,'mode':0o600}
        with self.assertRaisesRegex(ValueError,'digest differs'):I.selected_bytes(row)
    def test_traversal_hook_absolute_and_symlink_wheels_refused(self):
        for name in ('../escape.py','/absolute.py','module/../../escape.py','x.pth','pkg/../escape.py','pkg//module.py'):
            with self.subTest(name=name),self.assertRaises(ValueError):I.wheel_files(self.archive(name))
        with self.assertRaisesRegex(ValueError,'symlink'):I.wheel_files(self.archive('link',mode=stat.S_IFLNK|0o777))
    def test_selected_valid_original_wheel_bytes(self):
        raw=b'original module bytes\n';self.assertEqual(I.wheel_files(self.archive(raw=raw)),{'module.py':raw})
    def test_exclusive_write_preserves_existing_bytes(self):
        p=self.root/'existing';p.write_bytes(b'original')
        with self.assertRaises(FileExistsError):I.write_file(self.root,'existing',b'changed',0o600)
        self.assertEqual(p.read_bytes(),b'original')

if __name__=='__main__':unittest.main(verbosity=2)
