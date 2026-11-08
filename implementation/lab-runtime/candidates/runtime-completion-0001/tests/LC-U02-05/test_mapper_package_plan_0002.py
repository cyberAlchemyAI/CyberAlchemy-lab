"""Pure contract checks; no Source/Reader/Mapper/native process is launched."""
from pathlib import Path
import unittest

from t35_external_v1.phase_scoped_v2 import mapper_package_plan_0002 as plan


class MapperPackagePlanTests(unittest.TestCase):
    def test_selected_generated_build_is_still_sealed(self):
        observation = plan.inspect_generated_builder()
        self.assertEqual(observation['guard_calls'], 2)
        self.assertEqual(observation['seal_calls'], 2)
        self.assertEqual(observation['cold_read_calls'], 2)
        self.assertEqual(observation['sealed_write_or_temp_sites'], 5)
        self.assertEqual(observation['selected_event_count'], 25)
        self.assertEqual(observation['expected_package_leaf_count'], 55)
        self.assertTrue(observation['bridge_native_refused'])
        self.assertTrue(observation['precreated_package_conflicts_with_builder'])
        self.assertFalse(observation['package_effect_ready'])
        self.assertEqual(len(observation['generated_build_sha256']), 64)

    def test_exact_four_native_argument_vectors(self):
        for step in range(4):
            args = plan.native_args(step)
            plan.validate_native_args(step, args)
            self.assertTrue(all(value.startswith('/work/') for value in args[1:]))
        self.assertEqual(plan.native_args(2), plan.native_args(3))
        for step in range(4):
            with self.subTest(step=step):
                with self.assertRaises(plan.ContractError):
                    plan.validate_native_args(step, (*plan.native_args(step), '--extra'))
        with self.assertRaises(plan.ContractError):
            plan.validate_native_args(0, plan.native_args(1))
        with self.assertRaises(plan.ContractError):
            plan.native_args(True)
        with self.assertRaises(plan.ContractError):
            plan.native_args(4)

    def test_exact_read_only_native_sandbox_vectors(self):
        scratch = Path('/tmp/lc-u02-05-mapper-package-synthetic')
        for step in range(4):
            argv = plan.native_sandbox_argv(scratch, step)
            plan.validate_native_sandbox_argv(scratch, step, argv)
            self.assertNotIn('--bind', argv)
            self.assertEqual(argv.count('--ro-bind'), 5)
            self.assertEqual(argv[-len(plan.native_args(step)):],
                             plan.native_args(step))
            with self.assertRaises(plan.ContractError):
                plan.validate_native_sandbox_argv(
                    scratch, step, (*argv[:9], '--ro-bind-try', *argv[9:]))
        with self.assertRaises(plan.ContractError):
            plan.native_sandbox_argv(Path('/tmp/other'), 0)

    def test_builder_has_no_writable_host_mount(self):
        scratch = Path('/tmp/lc-u02-05-mapper-package-synthetic')
        argv = plan.builder_sandbox_argv(scratch)
        plan.validate_builder_sandbox_argv(scratch, argv)
        self.assertNotIn('--bind', argv)
        self.assertNotIn('--bind-try', argv)
        self.assertNotIn('--tmpfs', argv)
        self.assertEqual(argv.count('--ro-bind'), 6)
        for injected in ('--bind', '--tmpfs', '--dev'):
            with self.subTest(injected=injected):
                with self.assertRaises(plan.ContractError):
                    plan.validate_builder_sandbox_argv(
                        scratch, (*argv[:9], injected, '/work/extra', *argv[9:]))

    def test_exact_synthetic_package_leaf_closure(self):
        files = plan.expected_package_files(25)
        self.assertEqual(len(files), 55)
        plan.validate_package_paths(sorted(files), 25)
        for changed in (files | {'../context/manifest.json'},
                        files | {'semantic/00000026.json'},
                        files - {'manifest.json'}):
            with self.assertRaises(plan.ContractError):
                plan.validate_package_paths(sorted(changed), 25)
        with self.assertRaises(plan.ContractError):
            plan.validate_package_paths([*files, 'manifest.json'], 25)
        for bad in (True, 24, 26, 35, 257):
            with self.assertRaises(plan.ContractError):
                plan.expected_package_files(bad)

    def test_package_custody_model_refuses_aliases_and_manifest_drift(self):
        names = plan.expected_package_files(25)
        uid, gid = 1001, 1001
        dirs = {name: {'type': 'directory', 'mode': 0o700,
                       'uid': uid, 'gid': gid}
                for name in ('.', 'semantic', 'governance')}
        files = {name: {'type': 'regular', 'mode': 0o600,
                        'uid': uid, 'gid': gid, 'nlink': 1,
                        'sha256': '0' * 64}
                 for name in names}
        manifest = {name: '0' * 64 for name in names - {'manifest.json'}}
        plan.validate_inventory_model(dirs, files, manifest, uid=uid, gid=gid)
        for change in ({'type': 'symlink'}, {'nlink': 2},
                       {'mode': 0o666}, {'uid': 0}):
            altered = {name: dict(row) for name, row in files.items()}
            altered['semantic/00000001.json'].update(change)
            with self.assertRaises(plan.ContractError):
                plan.validate_inventory_model(dirs, altered, manifest,
                                              uid=uid, gid=gid)
        changed_manifest = dict(manifest)
        changed_manifest['request.json'] = '1' * 64
        with self.assertRaises(plan.ContractError):
            plan.validate_inventory_model(dirs, files, changed_manifest,
                                          uid=uid, gid=gid)
        extra_dirs = dict(dirs)
        extra_dirs['other'] = dict(dirs['.'])
        with self.assertRaises(plan.ContractError):
            plan.validate_inventory_model(extra_dirs, files, manifest,
                                          uid=uid, gid=gid)

    def test_no_effect_entrypoint(self):
        with self.assertRaisesRegex(plan.ContractError, 'not installed'):
            plan.require_effect_unavailable()
        self.assertFalse(hasattr(plan, 'run_and_publish'))
        self.assertFalse(hasattr(plan, 'probe'))


if __name__ == '__main__':
    unittest.main()
