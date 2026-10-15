"""Actual original installer calls in uniquely owned technical generation roots."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import unittest
import environment as E

REPOSITORY = None
RUN = None
R02 = None
DEPENDENCIES = None
ORIGINAL_GUARD = None
DESCRIPTOR = None
DESCRIPTOR_PIN = None


class CompositeTests(unittest.TestCase):
    def setUp(self):
        self.effects = RUN / 'effects' / self._testMethodName
        self.effects.mkdir(parents=True, mode=0o700)
        self.effects.chmod(0o700)
        self.scope = R02.OwnedScope(str(self.effects))
        self.adapter = E.CompositeEnvironment(DESCRIPTOR, DESCRIPTOR_PIN, REPOSITORY,
                                               R02, DEPENDENCIES, ORIGINAL_GUARD)
        self.package = REPOSITORY / 'product/lab/release-candidates/v1/packaging/R02/packages/0003'
        self.package_pin = hashlib.sha256((self.package / 'selection.json').read_bytes()).hexdigest()

    def changed(self, change):
        value = copy.deepcopy(self.adapter.value); change(value)
        path = self.effects / 'changed-descriptor.json'; raw = E.encoded(value); path.write_bytes(raw)
        return E.CompositeEnvironment(path, hashlib.sha256(raw).hexdigest(), REPOSITORY,
                                       R02, DEPENDENCIES, ORIGINAL_GUARD)

    def install(self, name='generation-one', adapter=None):
        return (adapter or self.adapter).transition('install', self.package, self.package_pin,
                                                    self.effects / name, self.scope, None)

    def test_01_complete_current_composite_checks_and_exact_R02_selection(self):
        result = self.adapter.guard(self.package, self.package_pin)
        self.assertFalse(result['full_original_proof_qualified'])
        self.assertEqual(len(result['host_ABI_library_bindings']), 23)
        self.assertEqual(result['R02_environment'], R02.load(self.package / 'selection.json')['environment'])

    def test_02_actual_immutable_R02_install_and_environment_receipt(self):
        result = self.install()
        verified = R02.verify_install(self.effects / 'generation-one', self.package, self.package_pin)
        self.assertGreater(verified['files'], 290)
        receipt = R02.load(self.effects / 'generation-one.environment.json')
        self.assertEqual(receipt, result['receipt'])
        self.assertEqual(receipt['verification']['composite_binding']['sha256'], DESCRIPTOR_PIN)

    def test_03_actual_upgrade_preserves_verified_predecessor(self):
        old = REPOSITORY / 'product/lab/release-candidates/v1/packaging/R02/packages/0002'
        old_pin = hashlib.sha256((old / 'selection.json').read_bytes()).hexdigest()
        first = self.adapter.transition('install', old, old_pin, self.effects / 'generation-one', self.scope, None)
        before = R02.tree(self.effects / 'generation-one')
        result = self.adapter.transition('upgrade', self.package, self.package_pin,
                                          self.effects / 'generation-two', self.scope, first['active'])
        self.assertEqual(before, R02.tree(self.effects / 'generation-one'))
        self.assertEqual(result['active']['generation'], 'generation-two')
        self.assertNotEqual(first['active']['package_sha256'], result['active']['package_sha256'])

    def test_04_actual_rollback_requires_retained_exact_environment(self):
        first = self.install()
        second = self.adapter.transition('upgrade', self.package, self.package_pin,
                                          self.effects / 'generation-two', self.scope, first['active'])
        before = R02.tree(self.effects / 'generation-two')
        result = self.adapter.transition('rollback', self.package, self.package_pin,
                                          self.effects / 'generation-one', self.scope, second['active'],
                                          expected_retained_receipt_binding=first['active']['receipt_binding'])
        self.assertEqual(result['active']['generation'], 'generation-one')
        self.assertEqual(before, R02.tree(self.effects / 'generation-two'))

    def test_05_changed_active_preimage_refused_before_generation(self):
        with self.assertRaisesRegex(ValueError, 'preimage changed'):
            self.adapter.transition('install', self.package, self.package_pin,
                                     self.effects / 'new', self.scope, {'generation': 'forged'})
        self.assertFalse((self.effects / 'new').exists())

    def test_06_unknown_composite_requirement_is_not_ignored(self):
        with self.assertRaisesRegex(ValueError, 'closed environment'):
            self.changed(lambda d: d.update(unknown_host_requirement=True))

    def test_07_unknown_R02_environment_field_is_not_ignored(self):
        changed = self.changed(lambda d: d['r02_selection']['environment'].update(unknown_runtime=True))
        with self.assertRaisesRegex(ValueError, 'closed environment'):
            changed.guard(self.package, self.package_pin)

    def test_08_omitted_ABI_requirement_is_refused(self):
        changed = self.changed(lambda d: d['host_ABI_library_bindings'].pop())
        with self.assertRaisesRegex(ValueError, 'ABI requirements'):
            changed.guard(self.package, self.package_pin)

    def test_09_incompatible_native_selection_is_refused(self):
        changed = self.changed(lambda d: d['host_native_binding'].update(sha256='0' * 64))
        with self.assertRaisesRegex(ValueError, 'native requirement'):
            changed.guard(self.package, self.package_pin)

    def test_10_incompatible_interpreter_environment_is_refused(self):
        changed = self.changed(lambda d: d['r02_selection']['environment'].update(python_version='3.13.0'))
        with self.assertRaisesRegex(ValueError, 'R02 subdocument'):
            changed.guard(self.package, self.package_pin)

    def test_11_unknown_runtime_execution_requirement_is_refused(self):
        changed = self.changed(lambda d: d['execution_dependencies']['execution_configuration'].update(network=True))
        with self.assertRaisesRegex(ValueError, 'runtime configuration'):
            changed.guard(self.package, self.package_pin)

    def test_12_full_original_proof_row_count_cannot_be_elided(self):
        changed = self.changed(lambda d: d['retained_full_proof'].update(source_rows=1))
        with self.assertRaisesRegex(ValueError, 'rows changed or elided'):
            changed.guard(self.package, self.package_pin)

    def test_13_rollback_different_environment_receipt_refused(self):
        first = self.install()
        receipt_path = self.effects / 'generation-one.environment.json'
        receipt = R02.load(receipt_path)
        receipt['verification']['R02_environment']['sqlite_version'] = '0.0.0'
        receipt_path.write_bytes(E.encoded(receipt))
        with self.assertRaisesRegex(ValueError, 'retained receipt bytes changed'):
            self.adapter.transition('rollback', self.package, self.package_pin,
                                     self.effects / 'generation-one', self.scope, first['active'],
                                     expected_retained_receipt_binding=first['active']['receipt_binding'])

    def test_14_actual_corrupted_owned_native_bytes_refused(self):
        installed = Path(self.adapter.value['execution_dependencies']['installed_root'])
        owned = self.effects / 'dependency-copy'; shutil.copytree(installed, owned); owned.chmod(0o700)
        def change(value):
            value['execution_dependencies']['installed_root'] = str(owned)
            value['host_native_binding']['path'] = str(owned / 'bin/lab-context-native-reader')
            for row in value['host_ABI_library_bindings']:
                row['path'] = str(owned / Path(row['path']).relative_to(installed))
        changed = self.changed(change)
        native = owned / 'bin/lab-context-native-reader'
        with native.open('ab') as handle:
            handle.write(b'owned causal corruption')
        with self.assertRaises(ValueError):
            changed.guard(self.package, self.package_pin)

    def test_15_unchanged_original_full_guard_still_refuses(self):
        with self.assertRaises((FileNotFoundError, AssertionError, ValueError)) as caught:
            self.adapter.require_full_original_proof()
        (self.effects / 'original-full-proof-refusal.txt').write_text(
            type(caught.exception).__name__ + ': ' + str(caught.exception) + '\n')

    def test_16_old_R02_fixture_environment_semantics_retained(self):
        package = R02.load(self.package / 'selection.json')
        R02.environment_guard(package['environment'])
        with self.assertRaisesRegex(ValueError, 'unselected interpreter'):
            R02.environment_guard(self.adapter.value)

    def test_17_corrupt_retained_package_refuses_upgrade(self):
        first = self.install()
        installed = self.effects / 'generation-one'
        (installed / 'selection.json').write_bytes(b'{}\n')
        with self.assertRaisesRegex(ValueError, 'installed original-byte'):
            self.adapter.transition('upgrade', self.package, self.package_pin,
                                     self.effects / 'generation-two', self.scope, first['active'])
        self.assertFalse((self.effects / 'generation-two').exists())

    def test_18_unknown_selector_version_is_refused(self):
        changed = self.changed(lambda d: d['r02_selection'].update(schema_version='unversioned'))
        with self.assertRaisesRegex(ValueError, 'versioned R02 selector'):
            changed.guard(self.package, self.package_pin)

    def mutate_retained(self, mutation, *, operation='rollback', select_changed=False):
        first = self.install()
        selected = self.adapter.transition('upgrade', self.package, self.package_pin,
                                            self.effects / 'generation-two', self.scope, first['active'])
        receipt_path = self.effects / 'generation-one.environment.json'
        value = R02.load(receipt_path); mutation(value); receipt_path.write_bytes(E.encoded(value))
        binding = first['active']['receipt_binding']
        if select_changed:
            # Even a fresh independent fixture selection must reject false
            # generation/byte-result/authority claims and unknown receipt fields.
            binding = {'path': str(receipt_path), 'sha256': hashlib.sha256(receipt_path.read_bytes()).hexdigest()}
        with self.assertRaises(ValueError) as caught:
            self.adapter.transition('rollback', self.package, self.package_pin,
                                     self.effects / 'generation-one', self.scope, selected['active'],
                                     expected_retained_receipt_binding=binding)
        self.assertEqual(R02.load(self.effects / 'active-composite.json'), selected['active'])
        return str(caught.exception)

    def test_19_changed_receipt_bytes_refused_against_independent_pin(self):
        self.assertIn('receipt bytes changed', self.mutate_retained(lambda v: v.update(generation='other')))

    def test_20_omitted_receipt_authority_field_refused(self):
        self.assertIn('closed environment', self.mutate_retained(lambda v: v.pop('authority_effect'), select_changed=True))

    def test_21_unknown_receipt_field_refused(self):
        self.assertIn('closed environment', self.mutate_retained(lambda v: v.update(ignored_field=True), select_changed=True))

    def test_22_wrong_receipt_generation_refused_even_with_new_pin(self):
        self.assertIn('receipt invariants', self.mutate_retained(lambda v: v.update(generation='other'), select_changed=True))

    def test_23_false_installed_result_refused_even_with_new_pin(self):
        self.assertIn('receipt invariants', self.mutate_retained(lambda v: v['installed'].update(files=0), select_changed=True))

    def test_24_forged_receipt_authority_flags_refused(self):
        self.assertIn('receipt invariants', self.mutate_retained(lambda v: v.update(authority_effect='admit', runtime_activations=1), select_changed=True))

    def test_25_upgrade_verifies_complete_predecessor_receipt(self):
        first = self.install()
        path = self.effects / 'generation-one.environment.json'
        receipt = R02.load(path); receipt['installed']['bytes'] = 0; path.write_bytes(E.encoded(receipt))
        with self.assertRaisesRegex(ValueError, 'retained receipt bytes changed'):
            self.adapter.transition('upgrade', self.package, self.package_pin,
                                     self.effects / 'generation-two', self.scope, first['active'])
        self.assertFalse((self.effects / 'generation-two').exists())

    def test_26_missing_independent_rollback_receipt_selection_refused(self):
        first = self.install()
        with self.assertRaisesRegex(ValueError, 'independent retained receipt selection'):
            self.adapter.transition('rollback', self.package, self.package_pin,
                                     self.effects / 'generation-one', self.scope, first['active'])

    def test_27_forged_predecessor_receipt_pin_refused(self):
        first = self.install(); forged = copy.deepcopy(first['active'])
        forged['receipt_binding']['sha256'] = '0' * 64
        (self.effects / 'active-composite.json').write_bytes(E.encoded(forged))
        with self.assertRaisesRegex(ValueError, 'retained receipt bytes changed'):
            self.adapter.transition('upgrade', self.package, self.package_pin,
                                     self.effects / 'generation-two', self.scope, forged)
        self.assertFalse((self.effects / 'generation-two').exists())
