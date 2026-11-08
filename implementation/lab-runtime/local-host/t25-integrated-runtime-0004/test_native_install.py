"""Atomic installer mechanics with tiny1010-member fake data; no ABI claim."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cal_T25_native_installer_component',HERE/'native_install.py')
N = importlib.util.module_from_spec(spec)
spec.loader.exec_module(N)


class NativeInstall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='cal-T25-native-component-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.payload = cls.root/'payload'
        cls.payload.mkdir(mode=0o700)
        cls.members = {}
        for number in range(1010):
            name = 'files/member-'+str(number).zfill(4)+'.bin'
            raw = ('public-component-fixture-'+str(number)).encode()
            path = cls.payload/name
            path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            path.write_bytes(raw)
            path.chmod(0o644)
            cls.members[name] = {'sha256':N.sha(raw),'size_bytes':len(raw),'mode':0o644}
        cls.pin = '1'*64

    def setUp(self):
        self.temp_root = tempfile.TemporaryDirectory(prefix='cal-T25-install-destination-',dir=self.root)
        self.addCleanup(self.temp_root.cleanup)
        self.private = Path(self.temp_root.name)
        self.private.chmod(0o700)

    def install(self):
        return N.install(self.private,self.payload,self.members,self.pin)

    def test_exact_bytes_fresh_identity_and_replay(self):
        result = self.install()
        self.assertEqual(result['files'],1010)
        self.assertEqual(result['identity'],N.identity(self.private/'native'))
        self.assertEqual(result,N.verify(self.private/'native',self.members,self.pin))
        receipt = json.loads((self.private/'native/installation.json').read_bytes())
        self.assertEqual(receipt['payload_manifest_sha256'],N.sha(N.encoded(self.members)))

    def test_two_roots_keep_payload_bytes_and_new_attestations(self):
        first = self.install()
        second_private = self.private/'second'
        second_private.mkdir(mode=0o700)
        second = N.install(second_private,self.payload,self.members,self.pin)
        self.assertNotEqual(first['identity'],second['identity'])
        self.assertNotEqual(first['sha256'],second['sha256'])
        for name in self.members:
            self.assertEqual((self.private/'native'/name).read_bytes(),
                             (second_private/'native'/name).read_bytes())

    def test_changed_input_refuses_without_publication(self):
        path = self.payload/'files/member-0000.bin'
        original = path.read_bytes()
        try:
            path.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                self.install()
        finally:
            path.write_bytes(original)
        self.assertFalse((self.private/'native').exists())
        self.assertEqual(list(self.private.iterdir()),[])

    def test_existing_target_and_unrelated_file_preserved(self):
        destination = self.private/'native'
        destination.mkdir(mode=0o700)
        (destination/'keep').write_bytes(b'unrelated')
        with self.assertRaisesRegex(ValueError,'destination already exists'):
            self.install()
        self.assertEqual((destination/'keep').read_bytes(),b'unrelated')

    def test_atomic_publication_does_not_replace_even_empty_target(self):
        stage = self.private/'stage'
        target = self.private/'target'
        stage.mkdir(mode=0o700)
        target.mkdir(mode=0o700)
        (stage/'owned').write_bytes(b'stage')
        before = N.identity(target)
        with self.assertRaises(FileExistsError):
            N.publish(stage,target)
        self.assertEqual(N.identity(target),before)
        self.assertEqual((stage/'owned').read_bytes(),b'stage')

    def test_unselected_mode_zero_input_is_not_read_or_copied(self):
        foreign = self.payload/'foreign-private.key'
        foreign.write_bytes(b'component-owned-unselected-marker')
        foreign.chmod(0)
        try:
            self.install()
            self.assertFalse((self.private/'native/foreign-private.key').exists())
        finally:
            foreign.unlink()

    def test_changed_installed_bytes_and_receipt_mode_refuse(self):
        self.install()
        path = self.private/'native/files/member-0000.bin'
        original = path.read_bytes()
        path.write_bytes(b'changed')
        try:
            with self.assertRaises(ValueError):
                N.verify(self.private/'native',self.members,self.pin)
        finally:
            path.write_bytes(original)
        receipt = self.private/'native/installation.json'
        receipt.chmod(0o644)
        try:
            with self.assertRaisesRegex(ValueError,'receipt ownership'):
                N.verify(self.private/'native',self.members,self.pin)
        finally:
            receipt.chmod(0o600)

    def test_linked_payload_is_refused_before_effect(self):
        alias = self.private/'payload-link'
        alias.symlink_to(self.payload,target_is_directory=True)
        with self.assertRaises(ValueError):
            N.install(self.private,alias,self.members,self.pin)
        self.assertFalse((self.private/'native').exists())


if __name__=='__main__':
    unittest.main(verbosity=2)
