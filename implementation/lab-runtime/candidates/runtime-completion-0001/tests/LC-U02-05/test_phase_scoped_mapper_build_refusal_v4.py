"""Pure/synthetic v4 Mapper build guard checks; no fixture child or effect."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1 import role_stage
from t35_external_v1.path_contract import ContractError, require
from t35_external_v1.phase_scoped_v2 import mapper_prepare_0002 as prepare
from t35_external_v1.phase_scoped_v2 import mapper_build_refusal_0004 as guard
import test_phase_scoped_mapper_late_native_v2 as previous
import test_phase_scoped_mapper_prepare_v2 as previous_receipt


class MapperBuildRefusalV4Tests(unittest.TestCase):
    def projected(self):
        planned, rows, source_raw, package_raw, reader_raw, native_raw, members = (
            previous.LateNativeMapperTests().fixture())
        rendered, mapper_raw, _ = prepare.project(
            planned, rows, source_raw, package_raw, reader_raw, native_raw,
            expected_package_members=members)
        return rendered, mapper_raw

    def test_fresh_projected_build_has_guard_then_first_sealed_effect(self):
        rendered, mapper_raw = self.projected()
        runner = guard.render_guard_runner(mapper_raw, rendered['build.py'])
        self.assertIn(hashlib.sha256(mapper_raw).hexdigest().encode(), runner)
        self.assertIn(str(role_stage.NATIVE_REL).encode(), runner)
        self.assertNotIn(b'__MAPPER_SHA__', runner)
        self.assertNotIn(b'__NATIVE_REL__', runner)
        self.assertEqual(guard.RECEIPT_NAME,
                         'phase-mapper-build-refusal-result-0004.json')
        head, delimiter, body = rendered['build.py'].partition(b'def build(pin):\n')
        self.assertTrue(delimiter)
        changed = head + delimiter + body.replace(
            b'    _t35_effect_refused()\n', b'    pass\n', 1)
        self.assertNotEqual(changed, rendered['build.py'])
        with self.assertRaises(ContractError):
            guard.render_guard_runner(mapper_raw, changed)

    def test_selected_generated_guard_passes_then_build_refuses_before_package(self):
        rendered, mapper_raw = self.projected()
        pin = hashlib.sha256(mapper_raw).hexdigest()
        guard.verify_build_effect_order(rendered['build.py'])
        with tempfile.TemporaryDirectory(prefix='t35-mapper-build-v4-') as temp:
            root = Path(temp)
            mapped = root/'mapped'
            mapped.mkdir()
            native = root/'native'
            native.write_bytes(b'synthetic selected native bytes')
            native.chmod(0o400)
            package = types.ModuleType('_t35_synthetic_mapper_v4')
            package.__path__ = [str(mapped)]
            base = types.ModuleType(package.__name__ + '.base')
            seen = []
            def verify_source(selected_pin):
                self.assertEqual(selected_pin, pin)
                seen.append('verified')
            base.__dict__.update({
                'HERE': mapped, 'ROOT': root,
                'sha': lambda raw: hashlib.sha256(raw).hexdigest(),
                'encoded': lambda value: json.dumps(value).encode(),
                'load': None, 'require': require, 'binding': None,
                'original': None, 'reader': None, 'records': None,
                'verify_source': verify_source,
            })
            build = types.ModuleType(package.__name__ + '.build')
            build.__package__ = package.__name__
            with patch.dict(sys.modules, {package.__name__: package,
                                          base.__name__: base,
                                          build.__name__: build}):
                exec(compile(rendered['build.py'], '<selected-mapper-build-v4>',
                             'exec'), build.__dict__)
                build.EXE = native
                build.EXE_SHA = hashlib.sha256(native.read_bytes()).hexdigest()
                with patch.object(build.subprocess, 'run',
                                  side_effect=AssertionError('native process reached')):
                    build.guard(pin)
                    with self.assertRaisesRegex(
                            RuntimeError, 'Generated T35 role effects require'):
                        build.build(pin)
            self.assertEqual(seen, ['verified', 'verified'])
            self.assertFalse((mapped/'packages').exists())
            self.assertFalse((root/'context').exists())

    def test_closed_guard_result_refuses_mutation(self):
        pin = 'a'*64
        result = {'result': 'PASS-fixture-mapper-build-refusal',
                  'mapper_manifest_sha256': pin, 'guard_passed': True,
                  'build_refused_at_effect_gate': True,
                  'mapped_package_absent': True, 'context_absent': True,
                  'native_copy_nonexecutable': True,
                  'sandbox_host_checkout_absent': True,
                  'sandbox_protected_roots_absent': True,
                  'authority_effect': 'none', 'actual_owner_outcome': None}
        raw = (json.dumps(result, sort_keys=True) + '\n').encode()
        self.assertEqual(guard.validate_guard_result(raw, mapper_sha=pin), result)
        for changed in ({**result, 'guard_passed': False},
                        {**result, 'build_refused_at_effect_gate': False},
                        {**result, 'mapped_package_absent': False},
                        {**result, 'context_absent': False},
                        {**result, 'mapper_manifest_sha256': 'b'*64}):
            with self.assertRaises(ContractError):
                guard.validate_guard_result(
                    (json.dumps(changed) + '\n').encode(), mapper_sha=pin)

    def test_closed_four_child_success_receipt_requires_guard_refusal(self):
        valid = previous_receipt.MapperPreparationTests().success_receipt()
        valid.update({
            'status': 'PASS-disposable-mapper-build-refusal',
            'selected_mapper_input_count': 1762,
            'late_mapper_native_sha256': role_stage.NATIVE_SHA,
            'late_mapper_native_nonexecutable': True,
            'mapper_guard_elapsed_milliseconds': 100,
            'mapper_guard_stdout_sha256': 'a'*64,
            'mapper_guard_stdout_bytes': 10,
            'mapper_guard_runner_sha256': 'a'*64,
            'build_guard_passed': True,
            'build_refused_at_effect_gate': True,
            'native_invocation_reachable_before_refusal': False,
        })
        for row in valid['child_process_observations'].values():
            row['forced_group_cleanup'] = False
        valid['child_process_observations']['mapper_build_guard'] = dict(
            valid['child_process_observations']['mapper_readonly'])
        self.assertEqual(guard._safe_success(valid), valid)
        for field, bad in (('build_guard_passed', False),
                           ('build_refused_at_effect_gate', False),
                           ('native_invocation_reachable_before_refusal', True)):
            with self.subTest(field=field):
                changed = dict(valid)
                changed[field] = bad
                with self.assertRaises(ContractError):
                    guard._safe_success(changed)

    def test_guard_child_uses_readonly_mapper_family_mount(self):
        with tempfile.TemporaryDirectory(prefix='t35-mapper-guard-argv-v4-') as temp:
            root = Path(temp)
            snapshot = root/'snapshot'
            family = root/'output'/'legacy-fixture-source'
            snapshot.mkdir()
            family.mkdir(parents=True)
            bridge = snapshot/'_t35_mapper_bridge.py'
            bridge.write_bytes(b'# selected bridge placeholder\n')
            argv = guard._guard_argv(snapshot, family, bridge)
            self.assertEqual(argv[-1],
                             str(guard.SNAPSHOT/'_t35_mapper_guard_runner.py'))
            self.assertNotIn('--bind', argv)
            self.assertEqual(sum(argv[index:index+3] == [
                '--ro-bind', str(family), str(guard.FAMILY)]
                for index in range(len(argv)-2)), 1)
            self.assertEqual(argv.count(str(family)), 1)


if __name__ == '__main__':
    unittest.main()
