"""Disposable construction checks; no host T35 effect or unit acceptance."""
from __future__ import annotations

import ast
import copy
import datetime as dt
import hashlib
import importlib
import importlib.util
import json
import os
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest.mock import patch

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
sys.path.insert(0, str(REPO / 'implementation/lab-runtime/candidates/runtime-completion-0001'))

from t35_external_v1 import (binding_adapter, constructor_paths, held_paths, path_contract,
                             phase_rebind, role_stage, runtime_capture, writer_bridge)
import lifecycle_probe


def row(path: str, raw: bytes = b'x') -> dict:
    return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}


def intent() -> dict:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    instance = 'legacy-external-test-1'
    sample = row('source/file.json')
    return {
        'schema_version': path_contract.INTENT_VERSION, 'authority_effect': 'none',
        'instance': instance,
        'output_family_path': str(path_contract.family_path(instance)),
        'storage_root_identity': {'dev': 1, 'ino': 2, 'mount_id': 3},
        'output_parent_identity': {'dev': 1, 'ino': 4, 'mount_id': 3},
        'service_uid': 20001, 'service_gid': 20001,
        'supervisor_unit': f'cal-source8-writer@{instance}.service',
        'cgroup_path': f'/system.slice/cal-source8-writer@{instance}.service',
        'mount_namespace': 'mnt:[12345]',
        'not_before': (now - dt.timedelta(hours=1)).isoformat(),
        'expires_at': (now + dt.timedelta(hours=23)).isoformat(),
        'signed_period_binding': row('receipts/period.json'),
        'slot_lock_binding': row('receipts/slot.lock'),
        'slot_lock_identity': {'dev': 1, 'ino': 5},
        't02_custody_receipt_binding': row('receipts/t02.json'),
        'input_snapshot_path': str(path_contract.SNAPSHOT_PARENT / ('a' * 64)),
        'input_snapshot_identity': {'dev': 1, 'ino': 6, 'mount_id': 7},
        'input_manifest_binding': row('selection/inputs.json'),
        'code_bindings': {'stage': sample},
        'api_bindings': {'api': row('api/guard.py')},
    }


class ContractTests(unittest.TestCase):
    def test_closed_intent_and_authority_classes(self):
        selected = intent()
        self.assertIs(path_contract.validate_intent(selected), selected)
        family = path_contract.family_path(selected['instance'])
        self.assertEqual(path_contract.check_binding(row(str(family / 'source' / 'base.py')),
                                                    kind='output', family=family)['path'],
                         str(family / 'source' / 'base.py'))
        self.assertEqual(path_contract.check_binding(row('product/lab/source.py'),
                                                    kind='source_api')['path'],
                         'product/lab/source.py')
        for bad in ('/var/lib/cyberalchemy-lab/source8-v1/instances2/legacy-x/file',
                    str(family) + '2/file', str(family) + '/./file',
                    str(family) + '/../file', str(family) + '//file',
                    '/home/vlad_/projects/CyberAlchemy-lab/file'):
            with self.subTest(bad=bad), self.assertRaises(path_contract.ContractError):
                path_contract.check_binding(row(bad), kind='output', family=family)
        for bad in ('/etc/passwd', '../escape', 'a/../b', 'a//b', 'a/./b', 'a\\b'):
            with self.subTest(bad=bad), self.assertRaises(path_contract.ContractError):
                path_contract.check_binding(row(bad), kind='source_api')
        with self.assertRaises(path_contract.ContractError):
            path_contract.check_binding(row(str(family / 'source/base.py')),
                                        kind='source_api')
        with self.assertRaises(path_contract.ContractError):
            path_contract.check_binding(row('source/base.py'), kind='output', family=family)

    def test_intent_identity_and_period_negatives(self):
        for key, value in (
            ('service_uid', 1000), ('service_gid', 1000), ('mount_namespace', 'mnt:[0]'),
            ('cgroup_path', '/init.scope'), ('output_family_path', '/tmp/legacy-x'),
            ('input_snapshot_path', '/tmp/snapshot'), ('supervisor_unit', 'other.service')):
            bad = copy.deepcopy(intent()); bad[key] = value
            with self.subTest(key=key), self.assertRaises(path_contract.ContractError):
                path_contract.validate_intent(bad)
        bad = intent(); bad['expires_at'] = bad['not_before']
        with self.assertRaises(path_contract.ContractError):
            path_contract.validate_intent(bad)

    def test_strict_intent_parse_and_snapshot_copy(self):
        selected = intent()
        encoded = json.dumps(selected, sort_keys=True).encode()
        self.assertEqual(path_contract.parse_intent(encoded), selected)
        duplicate = encoded[:-1] + b',"instance":"legacy-other"}'
        with self.assertRaises(path_contract.ContractError):
            path_contract.parse_intent(duplicate)
        nonfinite = encoded.replace(b'"service_uid": 20001', b'"service_uid": NaN')
        with self.assertRaises(path_contract.ContractError):
            path_contract.parse_intent(nonfinite)
        manifest = json.dumps({
            'schema_version': 'lab-T35-external-root-input-selection/v1-inactive',
            'authority_effect': 'none',
            'files': [selected['code_bindings']['stage'], selected['api_bindings']['api']],
        }).encode()
        with patch.object(held_paths, '_read_selected', return_value=manifest):
            held = held_paths.SelectedSnapshot(selected)
        selected['input_snapshot_path'] = '/tmp/attacker'
        self.assertNotEqual(held.intent['input_snapshot_path'], selected['input_snapshot_path'])
        leaked = held.intent; leaked['input_snapshot_path'] = '/tmp/attacker'
        self.assertNotEqual(held.intent['input_snapshot_path'], leaked['input_snapshot_path'])
        with patch.object(held_paths, '_read_selected', return_value=b'x'):
            self.assertEqual(held.read(held.rows['source/file.json']), b'x')
        bad = intent(); bad['storage_root_identity']['mount_id'] = 0
        with self.assertRaises(path_contract.ContractError):
            path_contract.validate_intent(bad)

    def test_process_and_parent_wrong_identity_refuse_before_host_walk(self):
        selected = intent()
        with tempfile.TemporaryDirectory() as folder:
            fd = os.open(folder, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with self.assertRaises(path_contract.ContractError):
                    path_contract.verify_process_and_parent(selected, fd)
                info = os.fstat(fd)
                selected['output_parent_identity'] = {
                    'dev': info.st_dev, 'ino': info.st_ino,
                    'mount_id': path_contract.fd_mount_id(fd)}
                with patch.object(path_contract.os, 'getresuid', return_value=(20001,) * 3), \
                     patch.object(path_contract.os, 'getresgid', return_value=(20001,) * 3), \
                     patch.object(path_contract.os, 'getgroups', return_value=[]), \
                     patch.object(path_contract.os, 'readlink', return_value='mnt:[99999]'):
                    with self.assertRaisesRegex(path_contract.ContractError, 'mount namespace'):
                        path_contract.verify_process_and_parent(selected, fd)
                with patch.object(path_contract.os, 'getresuid', return_value=(20001,) * 3), \
                     patch.object(path_contract.os, 'getresgid', return_value=(20001,) * 3), \
                     patch.object(path_contract.os, 'getgroups', return_value=[]), \
                     patch.object(path_contract.os, 'readlink', return_value='mnt:[12345]'), \
                     patch.object(path_contract, 'current_cgroup', return_value='/init.scope'):
                    with self.assertRaisesRegex(path_contract.ContractError, 'cgroup'):
                        path_contract.verify_process_and_parent(selected, fd)
            finally:
                os.close(fd)

    def test_held_chain_detects_detach_and_ancestor_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); parent = base / 'outer'; parent.mkdir()
            child = parent / 'held'; child.mkdir()
            with held_paths.HeldCanonicalDirectory(str(child)) as held:
                self.assertTrue(held.attached())
                child.rename(parent / 'moved')
                child.mkdir()
                self.assertFalse(held.attached())
            (parent / 'held').rmdir()
            (parent / 'held').symlink_to(parent / 'moved', target_is_directory=True)
            with self.assertRaises(OSError):
                held_paths.HeldCanonicalDirectory(str(parent / 'held'))

    def test_selected_manifest_membership(self):
        selected = intent()
        files = [selected['code_bindings']['stage'], selected['api_bindings']['api']]
        raw = json.dumps({'schema_version': 'lab-T35-external-root-input-selection/v1-inactive',
                          'authority_effect': 'none', 'files': files}).encode()
        self.assertEqual(held_paths.selected_manifest_rows(raw, selected)[files[0]['path']], files[0])
        bad = json.dumps({'schema_version': 'lab-T35-external-root-input-selection/v1-inactive',
                          'authority_effect': 'none', 'files': [files[0]]}).encode()
        with self.assertRaises(path_contract.ContractError):
            held_paths.selected_manifest_rows(bad, selected)
        bad = json.dumps({'schema_version': 'lab-T35-external-root-input-selection/v1-inactive',
                          'authority_effect': 'none', 'files': files + [files[0]]}).encode()
        with self.assertRaises(path_contract.ContractError):
            held_paths.selected_manifest_rows(bad, selected)

    def test_activation_sealed(self):
        with self.assertRaises(RuntimeError):
            binding_adapter.activation_capability(intent())
        with self.assertRaises(RuntimeError):
            constructor_paths.write_effect(intent())
        for action in (writer_bridge.mkdir_child, writer_bridge.write_leaf,
                       writer_bridge.dispatch_stage_or_preview):
            with self.subTest(action=action.__name__), self.assertRaises(RuntimeError):
                action(intent())


class RoleMappingTests(unittest.TestCase):
    def layout(self, base: Path) -> role_stage.DisposableLayout:
        return role_stage.DisposableLayout(PurePosixPath(str(base / 'out' / 'legacy-disposable')),
                                           PurePosixPath(str(base / 'snapshot')),
                                           'legacy-disposable')

    def test_disposable_lifecycle_observation(self):
        observation = lifecycle_probe.observe()
        self.assertEqual(observation['result'], 'PASS')
        self.assertFalse(observation['pre_state']['family_exists'])
        self.assertEqual(observation['post_state']['stage_leaf_count'], 30)
        self.assertEqual(observation['post_state']['unselected_leaf_count'], 0)
        self.assertEqual(observation['effect_state']['protected_or_host_effects'], 0)
        self.assertTrue(observation['cleanup_state']['root_absent'])
        self.assertFalse(observation['root_path_disclosed'])

    def test_27_role_render_and_constructor_in_disposable_scratch(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); layout = self.layout(base)
            source_root = REPO
            rows = role_stage.stage_rows(layout,
                                         lambda name: (source_root / name).read_bytes())
            self.assertEqual(len(rows), 27)
            self.assertEqual({r['role'] for r in rows},
                             {'source', 'reader', 'mapped', 'context'})
            by_path = constructor_paths.stage_output_membership(layout, rows)
            self.assertEqual(len(by_path), 27)
            self.assertEqual(sum(r['output']['path'].endswith('.py') for r in rows), 20)
            generated = {(item['role'], Path(item['output']['path']).name): item['bytes']
                         for item in rows}
            self.assertEqual(sum(name.endswith('.py') for _, name in generated), 20)
            self.assertIn(b'_t35_external_runtime_capture', generated['source', 'base.py'])
            self.assertIn(b'B.verify_inputs', generated['reader', 'reader.py'])
            self.assertIn(b'reader.adapter.source.B.verify_inputs', generated['mapped', 'base.py'])
            self.assertIn(b'run_native', generated['mapped', 'build.py'])
            self.assertIn(b'reader.adapter.source.B.verify_inputs', generated['context', 'base.py'])
            self.assertNotIn(role_stage.OLD_NATIVE.encode(), generated['mapped', 'build.py'])
            for (role, name), raw in generated.items():
                if not name.endswith('.py'):
                    continue
                tree = ast.parse(raw)
                self.assertNotIn(b'HERE.parents[5]', raw)
                self.assertNotIn(b'HERE.parents[8]', raw)
                self.assertNotIn(b'INSTANCES', raw)
                self.assertNotIn(role_stage.OLD_NATIVE.encode(), raw)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                        if (node.func.attr == 'as_posix' and
                            isinstance(node.func.value, ast.Call) and
                            isinstance(node.func.value.func, ast.Attribute) and
                            node.func.value.func.attr == 'relative_to' and
                            len(node.func.value.args) == 1 and
                            isinstance(node.func.value.args[0], ast.Name) and
                            node.func.value.args[0].id == 'ROOT'):
                            self.fail(f'unrewritten generated ROOT output binding: {role}/{name}')
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == 'os':
                            self.assertNotIn(node.func.attr, role_stage._EffectCalls.OS_CALLS,
                                             (role, name, node.lineno))
                        self.assertNotIn(node.func.attr, role_stage._EffectCalls.METHODS,
                                         (role, name, node.lineno))
            policy = next(item for item in rows if item['role'] == 'context' and
                          item['output']['path'].endswith('/protocols/policy.json'))
            self.assertIn(('protocol:completion-' + layout.instance + '-policy/v1').encode(),
                          policy['bytes'])
            for item in rows:
                path = Path(item['output']['path'])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(item['bytes'])
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                                 item['output']['sha256'])
                if path.suffix == '.py':
                    compile(path.read_bytes(), str(path), 'exec', optimize=0)
                    compile(path.read_bytes(), str(path), 'exec', optimize=2)
            episode = b'{"schema_version":"disposable-episode"}\n'
            context_role = b'{"schema_version":"disposable-context-role"}\n'
            selected = {
                'schema_version': 'lab-T35-external-root-stage-selection/v1-inactive',
                'authority_effect': 'none', 'instance': layout.instance,
                'output_family_path': str(layout.family),
                'template_rows': [{key: item[key] for key in ('role', 'input', 'output')}
                                  for item in rows],
                'episode_binding': row(str(layout.family / 'source/episode-contract.json'), episode),
                'current_role_binding': row(str(layout.family / 'source/context-native-role.json'), context_role),
                'status': 'staged-unqualified',
            }
            controls = {'episode_contract': episode, 'context_native_role': context_role,
                        'construction_selection': json.dumps(selected, sort_keys=True).encode()}
            closed = constructor_paths.stage_30_membership(layout, rows, controls)
            self.assertEqual(len(closed), 30)
            for name, suffix in constructor_paths.STAGE_CONTROLS.items():
                output = Path(layout.family / suffix)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(controls[name])
                self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(),
                                 closed[str(output)]['sha256'])
            # Import each rendered role package's actual __init__.py from
            # disposable scratch and inspect its resolved external location.
            for role in role_stage.ROLE_FILES:
                init = Path(layout.family / role / '__init__.py')
                package_name = '_t35_disposable_' + role
                spec = importlib.util.spec_from_file_location(
                    package_name, init, submodule_search_locations=[str(init.parent)])
                package = importlib.util.module_from_spec(spec)
                sys.modules[package_name] = package
                try:
                    spec.loader.exec_module(package)
                    self.assertEqual(Path(package.__file__), init)
                    self.assertEqual(list(package.__path__), [str(init.parent)])
                finally:
                    sys.modules.pop(package_name, None)
            source_base = next(r for r in rows if r['role'] == 'source' and
                               r['output']['path'].endswith('/base.py'))
            tree = ast.parse(source_base['bytes'])
            helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and
                          n.name == '_t35_binding_path')
            unit = ast.Module(body=[helper], type_ignores=[])
            ast.fix_missing_locations(unit)
            scope = {}
            exec(compile(unit, '<binding-helper>', 'exec'), scope)
            self.assertEqual(scope['_t35_binding_path'](Path(layout.family / 'source/base.py')),
                             str(layout.family / 'source/base.py'))
            self.assertEqual(scope['_t35_binding_path'](Path(layout.snapshot / 'product/file.py')),
                             'product/file.py')
            with self.assertRaises(ValueError):
                scope['_t35_binding_path'](Path('/etc/passwd'))
            paths = constructor_paths.runtime_role_paths(layout)
            for name, path in paths.items():
                p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
                if not p.exists(): p.write_text('{"role":"' + name + '"}\n')
            result = constructor_paths.bind_nine_roles(layout, lambda name: Path(name).read_bytes())
            self.assertEqual(set(result['role_bindings']), set(constructor_paths.NINE_ROLES))
            self.assertTrue(result['reader_entrypoint_ref'].startswith(str(layout.family)))
            self.assertFalse(result['runtime_executed'])
            tampered = copy.deepcopy(rows); tampered[0]['output']['path'] += '2'
            with self.assertRaises(path_contract.ContractError):
                constructor_paths.stage_output_membership(layout, tampered)
            corrupt = dict(controls)
            changed = dict(selected); changed['template_rows'] = selected['template_rows'][:-1]
            corrupt['construction_selection'] = json.dumps(changed).encode()
            with self.assertRaises(path_contract.ContractError):
                constructor_paths.stage_30_membership(layout, rows, corrupt)
            duplicated = dict(controls)
            duplicated['construction_selection'] = controls['construction_selection'][:-1] + b',"status":"staged-unqualified"}'
            with self.assertRaises(path_contract.ContractError):
                constructor_paths.stage_30_membership(layout, rows, duplicated)

    def test_disposable_layout_cannot_impersonate_host(self):
        selected = intent()
        with self.assertRaises(path_contract.ContractError):
            role_stage.DisposableLayout(path_contract.family_path(selected['instance']),
                                        PurePosixPath('/tmp/snapshot'), selected['instance'])
        with self.assertRaises(path_contract.ContractError):
            role_stage.DisposableLayout(
                path_contract.OUTPUT_PARENT / 'legacy-real' / selected['instance'],
                PurePosixPath('/tmp/snapshot'), selected['instance'])
        with self.assertRaises(path_contract.ContractError):
            role_stage.DisposableLayout(
                PurePosixPath('/tmp/out') / selected['instance'],
                path_contract.SNAPSHOT_PARENT / 'fake' / ('a' * 64),
                selected['instance'])
        for family, snapshot in (
            (path_contract.SNAPSHOT_PARENT / selected['instance'], PurePosixPath('/tmp/input')),
            (PurePosixPath('/tmp/out') / selected['instance'],
             path_contract.STORAGE_ROOT / 'fake'),
            (PurePosixPath('/tmp/same') / selected['instance'],
             PurePosixPath('/tmp/same')),
        ):
            with self.subTest(family=family, snapshot=snapshot), \
                 self.assertRaises(path_contract.ContractError):
                role_stage.DisposableLayout(family, snapshot, selected['instance'])

    def test_pure_mapped_context_predecessor_rebinding(self):
        with tempfile.TemporaryDirectory() as folder:
            layout = self.layout(Path(folder))
            rows = role_stage.stage_rows(layout, lambda name: (REPO / name).read_bytes())
            for role in ('mapped', 'context'):
                rendered = {Path(item['output']['path']).name: item['bytes'] for item in rows
                            if item['role'] == role and
                            Path(item['output']['path']).name in phase_rebind.PHASE_FILES[role]}
                previous = {name: row(str(layout.family / phase_rebind.PIN_PATHS[name]),
                                      ('new-' + name).encode())
                            for name in phase_rebind.PHASE_PREDECESSORS[role]}
                rebound = phase_rebind.rebind(layout, role, rendered, previous)
                self.assertEqual(set(rebound), set(phase_rebind.PHASE_FILES[role]))
                for name, raw in rebound.items():
                    compile(raw, name, 'exec', optimize=0)
                    compile(raw, name, 'exec', optimize=2)
                    self.assertTrue(all(pin.encode() not in raw
                                        for pin in phase_rebind.ORIGINAL_PINS.values()))
                bad = copy.deepcopy(previous)
                first = next(iter(bad)); bad[first]['path'] = '/etc/passwd'
                with self.assertRaises(path_contract.ContractError):
                    phase_rebind.rebind(layout, role, rendered, bad)
                no_selectors = {name: b'pass\n' for name in rendered}
                with self.assertRaises(path_contract.ContractError):
                    phase_rebind.rebind(layout, role, no_selectors, previous)

    def test_selected_30_leaf_capture_and_fabricated_stage_refusal(self):
        selected = intent()
        source_bytes = {source: (REPO / source).read_bytes()
                        for _, source, _ in role_stage.entries(role_stage.ProductionLayout(selected))}
        episode = (REPO / 'product/lab/release-candidates/v1/interface/'
                   'legacy-session-fixture-source-v1-action-0148/episode-contract.json').read_bytes()
        context_role = b'{"schema_version":"selected-disposable-context"}\n'
        selected['code_bindings'] = {
            **{f'role-{index}': row(path, raw)
               for index, (path, raw) in enumerate(source_bytes.items())},
            'stage_episode_contract': constructor_paths.ORIGINAL_EPISODE,
            'stage_context_native_role': row('selected/context-native-role.json', context_role),
            'native_mapper': {'path': str(role_stage.NATIVE_REL),
                              'sha256': role_stage.NATIVE_SHA},
            'runtime_bridge': role_stage.RUNTIME_BRIDGE,
            **{'source_dependency_' + key: binding
               for key, binding in role_stage.SOURCE_DEPENDENCIES.items()},
        }
        inputs = dict(source_bytes)
        inputs[constructor_paths.ORIGINAL_EPISODE['path']] = episode
        inputs['selected/context-native-role.json'] = context_role
        inputs[str(role_stage.NATIVE_REL)] = b'synthetic native mock only'
        inputs[role_stage.RUNTIME_BRIDGE['path']] = (REPO / role_stage.RUNTIME_BRIDGE['path']).read_bytes()
        for binding in role_stage.SOURCE_DEPENDENCIES.values():
            inputs[binding['path']] = (REPO / binding['path']).read_bytes()
        manifest = json.dumps({
            'schema_version': 'lab-T35-external-root-input-selection/v1-inactive',
            'authority_effect': 'none',
            'files': [selected['code_bindings']['native_mapper'] if path == str(role_stage.NATIVE_REL)
                      else constructor_paths.ORIGINAL_EPISODE if path == constructor_paths.ORIGINAL_EPISODE['path']
                      else row(path, raw) for path, raw in inputs.items()] +
                     [selected['api_bindings']['api']],
        }, sort_keys=True).encode()
        selected['input_manifest_binding'] = row('selection/inputs.json', manifest)
        inputs['selection/inputs.json'] = manifest
        outputs = {}
        def selected_read(_intent, binding, *, kind, **_):
            table = inputs if kind == 'source_api' else outputs
            return table[binding['path']]
        with patch.object(held_paths, '_read_selected', side_effect=selected_read), \
             patch.object(held_paths.SelectedSnapshot, 'read_executable', return_value=b'synthetic native mock only'), \
             patch.object(binding_adapter, '_read_selected', side_effect=selected_read):
            snapshot = held_paths.SelectedSnapshot(selected)
            rows = role_stage.selected_stage_rows(snapshot)
            capture = binding_adapter.RootBoundCapture(snapshot, rows)
            self.assertEqual(len(capture._outputs), 30)
            episode_rendered = json.loads(capture.control_bytes['episode_contract'])
            self.assertEqual(episode_rendered['not_before'], selected['not_before'])
            self.assertEqual(episode_rendered['expires_at'], selected['expires_at'])
            self.assertIn('completion-' + selected['instance'],
                          episode_rendered['episode_ref'])
            outputs.update({item['output']['path']: item['bytes'] for item in rows})
            for name, suffix in constructor_paths.STAGE_CONTROLS.items():
                outputs[str(capture.layout.family / suffix)] = capture.control_bytes[name]
            for binding in capture._outputs.values():
                self.assertEqual(capture.read(binding), outputs[binding['path']])
            with runtime_capture.selected_read_scope(capture):
                import _t35_external_runtime_capture as bridge
                self.assertEqual(bridge.read(next(iter(capture._outputs.values()))),
                                 outputs[next(iter(capture._outputs))])
                self.assertEqual(Path(bridge.__file__),
                                 Path(capture.layout.snapshot / role_stage.RUNTIME_BRIDGE['path']))
            self.assertNotIn(runtime_capture.MODULE_NAME, sys.modules)
            changed = copy.deepcopy(rows)
            changed[0]['bytes'] = b'forged generated code'
            changed[0]['output']['sha256'] = hashlib.sha256(changed[0]['bytes']).hexdigest()
            with self.assertRaises(path_contract.ContractError):
                binding_adapter.RootBoundCapture(snapshot, changed)
            removed_native = snapshot.intent
            removed_native['code_bindings'].pop('native_mapper')
            with patch.object(held_paths.SelectedSnapshot, 'intent',
                              new_callable=lambda: property(lambda _: removed_native)):
                with self.assertRaises(path_contract.ContractError):
                    role_stage.selected_stage_rows(snapshot)
            removed_dependency = snapshot.intent
            removed_dependency['code_bindings'].pop('source_dependency_custody_loader')
            with patch.object(held_paths.SelectedSnapshot, 'intent',
                              new_callable=lambda: property(lambda _: removed_dependency)):
                with self.assertRaises(path_contract.ContractError):
                    role_stage.selected_stage_rows(snapshot)
            arbitrary = row(str(capture.layout.family / 'source/extra.json'))
            with self.assertRaises(path_contract.ContractError):
                capture.read(arbitrary)
            bad_episode = dict(inputs)
            bad_episode[constructor_paths.ORIGINAL_EPISODE['path']] = b'{"schema_version":"other"}'
            with patch.object(held_paths, '_read_selected',
                              side_effect=lambda i, b, *, kind, **kw: bad_episode.get(b['path'],
                                                                                      selected_read(i, b, kind=kind, **kw))):
                with self.assertRaises(path_contract.ContractError):
                    binding_adapter.RootBoundCapture(snapshot, rows)

    def test_actual_import_dependency_boundary(self):
        """Source/reader import; later roles refuse without selected bridge/phase output."""
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            snapshot = base / 'snapshot'
            dependency = snapshot / 'product/lab/release-candidates/v1/interface/custody-correction-v4'
            dependency.mkdir(parents=True)
            original = REPO / 'product/lab/release-candidates/v1/interface/custody-correction-v4'
            for name in ('loader.py', 'reader_adapter.py'):
                shutil.copyfile(original / name, dependency / name)
            layout = role_stage.DisposableLayout(
                PurePosixPath(str(base / 'out/legacy-import')),
                PurePosixPath(str(snapshot)), 'legacy-import')
            rows = role_stage.stage_rows(layout, lambda name: (REPO / name).read_bytes())
            for item in rows:
                path = Path(item['output']['path']); path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(item['bytes'])
            for role in ('source', 'reader', 'mapped', 'context'):
                package_name = '_t35_actual_import_' + role
                path = Path(layout.family / role)
                spec = importlib.util.spec_from_file_location(
                    package_name, path / '__init__.py', submodule_search_locations=[str(path)])
                package = importlib.util.module_from_spec(spec)
                sys.modules[package_name] = package
                spec.loader.exec_module(package)
                try:
                    if role in ('source', 'reader'):
                        loaded = importlib.import_module(package_name + '.base')
                        self.assertEqual(Path(loaded.__file__), path / 'base.py')
                        self.assertEqual(loaded.ROOT, snapshot)
                        if role == 'source':
                            with self.assertRaises(ModuleNotFoundError):
                                loaded.original(row('product/file.json'))
                            with self.assertRaisesRegex(RuntimeError, 'uninstalled T02 custody gate'):
                                loaded.emit(path / 'packages/0001/no-effect.json', {'test': True})
                            self.assertFalse((path / 'packages').exists())
                            builder = importlib.import_module(package_name + '.build')
                            with patch.object(builder, 'verify_source', return_value={}):
                                with self.assertRaisesRegex(RuntimeError, 'uninstalled T02 custody gate'):
                                    builder.main('0' * 64)
                            self.assertFalse((path / 'packages').exists())
                    else:
                        with self.assertRaises(ModuleNotFoundError) as failure:
                            importlib.import_module(package_name + '.base')
                        self.assertIn('_t35_external_runtime_capture',
                                      str(failure.exception))
                finally:
                    for key in tuple(sys.modules):
                        if key == package_name or key.startswith(package_name + '.'):
                            sys.modules.pop(key, None)
            for role in ('mapped', 'context'):
                raw = Path(layout.family / role / 'build.py').read_bytes()
                tree = ast.parse(raw)
                selected_nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                                  and node.name in ('emit', '_t35_effect_refused')]
                scope = {'HERE': Path(layout.family / role),
                         'require': lambda good, message: good or (_ for _ in ()).throw(ValueError(message))}
                exec(compile(ast.Module(body=selected_nodes, type_ignores=[]),
                             '<effect-refusal>', 'exec'), scope)
                leaf = Path(layout.family / role / 'packages/0001/no-effect.json')
                with self.assertRaisesRegex(RuntimeError, 'uninstalled T02 custody gate'):
                    scope['emit'](leaf, {'test': True})
                self.assertFalse(leaf.exists())


if __name__ == '__main__':
    unittest.main()
