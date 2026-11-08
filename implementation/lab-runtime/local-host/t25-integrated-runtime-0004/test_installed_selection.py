"""Private bootstrap selection boundary, using tiny owned fixture roots."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile
import unittest
import uuid

HERE = Path(__file__).resolve().parent
sha = lambda raw:hashlib.sha256(raw).hexdigest()
encoded = lambda value:(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()


class InstalledSelection(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cal-T25-private-selection-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.mod,self.root,self.private,self.package,self.config,self.receipt = self.fixture(self.base/'a')

    def fixture(self, directory):
        directory.mkdir(mode=0o700)
        root = directory/'repository'
        module_path = root/'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/installed_selection.py'
        module_path.parent.mkdir(parents=True,mode=0o700)
        shutil.copyfile(HERE/'installed_selection.py',module_path)
        spec = importlib.util.spec_from_file_location('_cal_T25_selection_'+uuid.uuid4().hex,module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        private = directory/'.cal-runtime'
        private.mkdir(mode=0o700)
        (private/'native').mkdir(mode=0o700)
        (private/'bindings').mkdir(mode=0o700)
        native_receipt = encoded({'schema':'cal-clean-installed-native-runtime/v1',
            'identity':mod.identity(private/'native'),'selection_sha256':'1'*64,
            'file_count':1010,'payload_manifest_sha256':'3'*64})
        self.write(private/'native/installation.json',native_receipt)
        bindings = {}
        for slot in sorted(mod.BINDINGS):
            relative = 'generated/'+slot.replace('.','/')+'.json'
            path = root/relative
            path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            raw = encoded({'fixture_slot':slot})
            self.write(path,raw)
            bindings[slot] = {'path':relative,'sha256':sha(raw)}
        dataset = {'family':'fixture-family','store':'fixture-store','scope':'fixture-scope'}
        package = {'schema_version':'lab-stable-runtime-package/v1','authority_effect':'none',
                   'dataset':dataset,'generated_metadata_paths':[row['path'] for row in bindings.values()],
                   'binding_paths':{slot:row['path'] for slot,row in bindings.items()},'members':[]}
        package_raw = encoded(package)
        self.write(root/'.cal-package-manifest.json',package_raw)
        config = {'schema_version':'lab-private-host-selection/v1','authority_effect':'none','fixture_only':True,
                  'package_manifest_sha256':sha(package_raw),'repository_root':str(root),'bindings':bindings,
                  'values':{'identity.family':'fixture-family','identity.store':'fixture-store',
                    'identity.source_name':'completion-legacy:fixture-family','identity.scope':'fixture-scope',
                    'native.root':str(private/'native'),'native.identity':mod.identity(private/'native'),
                    'native.receipt':{'path':str(private/'native/installation.json'),'sha256':sha(native_receipt)},
                    'native.dependency_selection':{'path':'fixture-selection.json','sha256':'1'*64},
                    'archive.path':str(private/'fixture-archives/branch.snapshot'),'archive.sha256':'2'*64,
                    'period.not_before':'2026-10-24T00:00:00+00:00','period.expires_at':'2026-10-25T00:00:00+00:00'}}
        config_raw = encoded(config)
        self.write(private/'bindings/host-selection.json',config_raw)
        receipt = {'schema_version':'lab-private-installation-receipt/v1','authority_effect':'none','fixture_only':True,
                   'phase':'ready',
                   'package_manifest_sha256':sha(package_raw),'host_selection_sha256':sha(config_raw),
                   'private_root_identity':mod.identity(private)}
        self.write(private/'installation.json',encoded(receipt))
        return mod,root,private,package,config,receipt

    @staticmethod
    def write(path, raw):
        path.write_bytes(raw)
        path.chmod(0o600)

    def select(self):
        return self.mod.activate(sha((self.private/'installation.json').read_bytes()))

    def rewrite_config(self, config):
        raw = encoded(config)
        self.write(self.private/'bindings/host-selection.json',raw)
        receipt = copy.deepcopy(self.receipt)
        receipt['host_selection_sha256'] = sha(raw)
        self.write(self.private/'installation.json',encoded(receipt))

    def test_selected_owned_root_binds_before_runtime_import(self):
        selected = self.select()
        self.assertTrue(selected.guard())
        self.assertEqual(self.mod.root(),self.root)
        self.assertEqual(self.mod.binding('family.source'),self.config['bindings']['family.source'])
        value = self.mod.binding('family.source')
        value['sha256'] = '0'*64
        self.assertNotEqual(value,self.mod.binding('family.source'))

    def test_unselected_runtime_import_refuses(self):
        with self.assertRaisesRegex(ValueError,'bootstrap has not selected'):
            self.mod.binding('family.source')

    def test_selection_cannot_activate_twice(self):
        self.select()
        with self.assertRaisesRegex(ValueError,'already activated'):
            self.select()

    def test_construction_phase_cannot_import_or_activate_runtime(self):
        config = copy.deepcopy(self.config)
        for slot in ('family.context_package','family.delivery','family.cold','api.source','api.profile'):
            config['bindings'][slot] = None
        self.rewrite_config(config)
        receipt = json.loads((self.private/'installation.json').read_bytes())
        receipt['phase'] = 'construct-context'
        self.write(self.private/'installation.json',encoded(receipt))
        pin = sha(encoded(receipt))
        with self.assertRaisesRegex(ValueError,'provisional construction'):
            self.mod.activate(pin)
        selected = self.mod.activate(pin,purpose='construct-context')
        self.assertTrue(selected.guard())
        self.assertEqual(self.mod.binding('family.source'),self.config['bindings']['family.source'])
        with self.assertRaisesRegex(ValueError,'construction binding is unresolved'):
            self.mod.binding('family.context_package')
        with self.assertRaisesRegex(ValueError,'finalized runtime'):
            self.mod.require_runtime_ready()

    def test_control_file_mutation_refuses_after_activation(self):
        selected = self.select()
        path = self.private/'bindings/host-selection.json'
        original = path.read_bytes()
        try:
            self.write(path,original+b' ')
            with self.assertRaises(ValueError):
                selected.guard()
        finally:
            self.write(path,original)
        self.assertTrue(selected.guard())

    def test_private_selection_and_receipt_modes_enforced(self):
        selected = self.select()
        for path in (self.private/'bindings/host-selection.json',self.private/'installation.json',
                     self.private/'native/installation.json'):
            with self.subTest(path=path.name):
                path.chmod(0o644)
                try:
                    with self.assertRaisesRegex(ValueError,'owner/mode'):
                        selected.guard()
                finally:
                    path.chmod(0o600)

    def test_same_path_native_inode_replacement_refuses(self):
        selected = self.select()
        old = self.private/'native'
        backup = self.private/'native-old'
        old.rename(backup)
        try:
            shutil.copytree(backup,old)
            old.chmod(0o700)
            with self.assertRaisesRegex(ValueError,'native root identity'):
                selected.guard()
        finally:
            shutil.rmtree(old)
            backup.rename(old)
        self.assertTrue(selected.guard())

    def test_private_captured_map_mutation_refuses(self):
        selected = self.select()
        original = selected.value['bindings']['family.source']['sha256']
        try:
            selected.value['bindings']['family.source']['sha256'] = '0'*64
            with self.assertRaisesRegex(ValueError,'captured installed selection'):
                selected.guard()
        finally:
            selected.value['bindings']['family.source']['sha256'] = original

    def test_public_package_nested_maps_are_immutable(self):
        selected=self.select()
        with self.assertRaises(TypeError):selected.package['dataset']['family']='retargeted'
        with self.assertRaises(TypeError):selected.package['binding_paths']['family.source']='other.json'
        with self.assertRaises(AttributeError):selected.package['members'].append({'path':'extra'})
        self.assertTrue(selected.guard())

    def test_public_package_physical_mutation_still_refuses(self):
        selected=self.select()
        path=self.root/'.cal-package-manifest.json'
        original=path.read_bytes()
        path.write_bytes(original.replace(b'fixture-family',b'changed-family'))
        with self.assertRaisesRegex(ValueError,'digest|bytes|stamp'):selected.guard()

    def test_package_write_with_restored_mtime_still_refuses(self):
        selected=self.select();path=self.root/'.cal-package-manifest.json';before=path.stat()
        path.write_bytes(path.read_bytes().replace(b'fixture-family',b'changed-family'))
        os.utime(path,ns=(before.st_atime_ns,before.st_mtime_ns))
        self.assertEqual(path.stat().st_mtime_ns,before.st_mtime_ns)
        with self.assertRaisesRegex(ValueError,'stamp'):selected.guard()

    def test_package_same_bytes_new_inode_refuses(self):
        selected=self.select();path=self.root/'.cal-package-manifest.json';replacement=path.with_name('replacement')
        replacement.write_bytes(path.read_bytes());replacement.chmod(path.stat().st_mode&0o777);os.replace(replacement,path)
        with self.assertRaisesRegex(ValueError,'stamp'):selected.guard()

    def test_forged_frozen_package_object_refuses(self):
        selected=self.select();value=copy.deepcopy(self.package);value['dataset']['family']='forged'
        object.__setattr__(selected,'package',self.mod.freeze_package(value))
        with self.assertRaisesRegex(ValueError,'captured installed selection'):selected.guard()

    def test_unknown_control_field_refuses(self):
        config = copy.deepcopy(self.config)
        config['wire_selected_root'] = '/tmp/other'
        self.rewrite_config(config)
        with self.assertRaisesRegex(ValueError,'closed installed host selection'):
            self.select()

    def test_public_slot_cannot_choose_another_locator(self):
        config = copy.deepcopy(self.config)
        config['bindings']['family.source'] = copy.deepcopy(config['bindings']['family.context_source'])
        self.rewrite_config(config)
        with self.assertRaisesRegex(ValueError,'binding path differs'):
            self.select()

    def test_public_artifact_dataset_identity_is_fixed(self):
        config = copy.deepcopy(self.config)
        config['values']['identity.store'] = 'other-store'
        self.rewrite_config(config)
        with self.assertRaisesRegex(ValueError,'artifact meaning'):
            self.select()

    def test_wrong_identity_receipt_cannot_be_rehashed_into_selection(self):
        path = self.private/'native/installation.json'
        wrong = json.loads(path.read_bytes())
        wrong['identity'][1] += 1
        self.write(path,encoded(wrong))
        config = copy.deepcopy(self.config)
        config['values']['native.receipt']['sha256'] = sha(encoded(wrong))
        self.rewrite_config(config)
        with self.assertRaisesRegex(ValueError,'receipt body identity'):
            self.select()

    def test_fresh_roots_use_different_actual_attestations(self):
        self.select()
        mod,root,private,package,config,receipt = self.fixture(self.base/'b')
        selected = mod.activate(sha((private/'installation.json').read_bytes()))
        self.assertTrue(selected.guard())
        self.assertEqual(package,self.package)
        self.assertNotEqual(config['values']['native.identity'],self.config['values']['native.identity'])
        self.assertNotEqual(sha((private/'installation.json').read_bytes()),
                            sha((self.private/'installation.json').read_bytes()))
        self.assertEqual((root/'.cal-package-manifest.json').read_bytes(),
                         (self.root/'.cal-package-manifest.json').read_bytes())


if __name__=='__main__':
    unittest.main(verbosity=2)
