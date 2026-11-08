"""Pure Mapper projection and disposable exclusive-write oracles; no child run."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1 import role_stage, scratch_reader_probe as reader
from t35_external_v1 import scratch_source_probe as source
from t35_external_v1.phase_scoped_v2 import mapper_prepare_0001 as mapper
from t35_external_v1.phase_scoped_v2 import mapper_readonly_0001 as readonly
from t35_external_v1.phase_scoped_v2 import plan as phase, prefix_probe


class MapperPreparationTests(unittest.TestCase):
    def fixture(self):
        layout = role_stage.DisposableLayout(
            PurePosixPath('/work/out/legacy-fixture-source'),
            PurePosixPath('/work/snapshot'), 'legacy-fixture-source')
        stage = []
        for role, original, output in role_stage.entries(layout):
            name = PurePosixPath(original).name
            if role == 'mapped' and name in ('base.py', 'build.py'):
                raw = source._held_input({'path': original,
                                          'sha256': source.ROLE_TEMPLATE_SHA[original]})
                generated = role_stage.render_python(raw, layout=layout,
                                                     role=role, name=name)
            else:
                generated = (role + '/' + name + '\n').encode()
            stage.append({'role': role,
                          'input': {'path': original,
                                    'sha256': source.ROLE_TEMPLATE_SHA[original]},
                          'output': {'path': output,
                                     'sha256': hashlib.sha256(generated).hexdigest()},
                          'bytes': generated})
        planned = phase.plan(layout, stage, episode_raw=b'episode\n', role_raw=b'role\n')
        repository = {f'synthetic/{i:04d}.json':
                      {'path': f'synthetic/{i:04d}.json', 'sha256': 'a'*64}
                      for i in range(1702)}
        native = str(role_stage.NATIVE_REL)
        repository[native] = {'path': native, 'sha256': role_stage.NATIVE_SHA}
        _, source_raw = prefix_probe._source_selection(planned, repository)
        members = {'artifacts/' + f'{i:02d}.json' for i in range(21)}
        members.update({'application.json', 'approval.json', 'branch.snapshot',
                        'build-result.json', 'expected-replay.json', 'period.json',
                        'project-setup-application.json', 'project-setup-approval.json',
                        'project-setup-proposal.json', 'proposal.json', 'record-index.json',
                        'retry.json', 'review.json', 'setup-artifacts/product.json',
                        'setup-artifacts/project.json'})
        package_rows = [
            {'path': str(layout.family / 'source/packages/0001' / name),
             'sha256': hashlib.sha256(name.encode()).hexdigest()}
            for name in sorted(members)]
        package = {
            'schema_version': 'lab-owned-current-participation-package/v1-candidate',
            'files': package_rows,
            'source_manifest_binding': mapper._binding(
                layout.family / reader.SOURCE_REL, source_raw),
            'archive_binding': next(row for row in package_rows
                                    if row['path'].endswith('/branch.snapshot')),
            'expected_replay_binding': next(row for row in package_rows
                                            if row['path'].endswith('/expected-replay.json')),
            'period_binding': next(row for row in package_rows
                                   if row['path'].endswith('/period.json')),
            'episode_contract_binding': mapper._binding(
                layout.family / 'source/episode-contract.json', planned.episode_raw),
            'visibility': 'private-candidate-original-custody',
            'public_package_export_allowed': False,
            'authority_effect': 'none', 'actual_owner_outcome': None,
        }
        package_raw = reader._json(package)
        reader_raw = reader._reader_manifest(source_raw, package_raw)
        return planned, repository, source_raw, package_raw, reader_raw, members

    def test_exact_mapper_projection_and_no_future_context(self):
        planned, rows, source_raw, package_raw, reader_raw, members = self.fixture()
        rendered, manifest_raw, pins = mapper.project(
            planned, rows, source_raw, package_raw, reader_raw,
            expected_package_members=members)
        self.assertEqual(set(rendered), mapper.MAPPER_NAMES)
        self.assertEqual(set(pins), {'source', 'source_package', 'reader'})
        value = json.loads(manifest_raw)
        self.assertEqual(set(value), {'schema_version', 'files', 'environment',
                        'original_source_binding', 'original_package_binding',
                        'adapter_source_binding', 'selected_native_executable',
                        'fixture_only', 'qualification', 'authority_effect',
                        'actual_owner_outcome'})
        self.assertEqual(len(value['files']), 1761)
        self.assertFalse(value['qualification'])
        self.assertTrue(all('/context/' not in row['path'] for row in value['files']))
        self.assertNotIn(str(planned.layout.family / mapper.MAPPER_MANIFEST),
                         {row['path'] for row in value['files']})
        self.assertNotIn('mapped/packages/0001/manifest.json',
                         {row['path'] for row in value['files']})
        self.assertEqual(value['selected_native_executable']['sha256'],
                         role_stage.NATIVE_SHA)

    def test_predecessor_and_membership_mutations_refused(self):
        planned, rows, source_raw, package_raw, reader_raw, members = self.fixture()
        with self.assertRaises(ValueError):
            mapper.project(planned, rows, source_raw, package_raw, reader_raw+b' ',
                           expected_package_members=members)
        altered = json.loads(package_raw)
        altered['authority_effect'] = 'host'
        with self.assertRaises(ValueError):
            mapper.project(planned, rows, source_raw, reader._json(altered), reader_raw,
                           expected_package_members=members)
        altered = json.loads(package_raw)
        altered['files'].append(dict(altered['files'][0]))
        with self.assertRaises(ValueError):
            mapper.project(planned, rows, source_raw, reader._json(altered), reader_raw,
                           expected_package_members=members)
        for key in ('archive_binding', 'expected_replay_binding', 'period_binding',
                    'episode_contract_binding'):
            altered = json.loads(package_raw)
            altered[key] = {'path': altered[key]['path'], 'sha256': '0'*64}
            with self.subTest(key=key), self.assertRaises(ValueError):
                mapper.project(planned, rows, source_raw, reader._json(altered), reader_raw,
                               expected_package_members=members)
        native = str(role_stage.NATIVE_REL)
        rows[native] = {'path': native, 'sha256': '0'*64}
        with self.assertRaises(ValueError):
            mapper.project(planned, rows, source_raw, package_raw, reader_raw,
                           expected_package_members=members)

    def test_exclusive_materialization_and_alias_refusal(self):
        planned, rows, source_raw, package_raw, reader_raw, members = self.fixture()
        mapper.project(planned, rows, source_raw, package_raw, reader_raw,
                       expected_package_members=members)
        with tempfile.TemporaryDirectory(prefix='t35-mapper-pure-') as temp:
            family = Path(temp) / 'legacy-fixture-source'
            (family / 'source').mkdir(parents=True)
            (family / 'reader').mkdir()
            (family / 'source/base.py').write_bytes(b'unchanged source')
            (family / 'reader/base.py').write_bytes(b'unchanged reader')
            pre = source._tree_files(family)
            dirs = source._tree_dirs(family)
            post, post_dirs, manifest_raw, _ = mapper.materialize(
                family, planned, rows, source_raw, package_raw, reader_raw,
                expected_package_members=members, pre_files=pre, pre_dirs=dirs)
            self.assertEqual(len(post), len(pre)+5)
            self.assertEqual(post_dirs, dirs | {'mapped'})
            self.assertEqual({name: post[name] for name in pre}, pre)
            self.assertFalse((family/'mapped/packages').exists())
            self.assertFalse((family/'context').exists())
            with self.assertRaises(ValueError):
                mapper.materialize(family, planned, rows, source_raw, package_raw,
                                   reader_raw, expected_package_members=members,
                                   pre_files=pre, pre_dirs=dirs)
        with tempfile.TemporaryDirectory(prefix='t35-mapper-alias-') as temp:
            family = Path(temp) / 'legacy-fixture-source'
            family.mkdir()
            (family/'source').mkdir()
            (family/'reader').mkdir()
            outside = Path(temp)/'outside'
            outside.mkdir()
            (family/'mapped').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                mapper.materialize(family, planned, rows, source_raw, package_raw,
                                   reader_raw, expected_package_members=members,
                                   pre_files={}, pre_dirs={'source', 'reader'})

    def test_readonly_bridge_and_result_are_closed(self):
        planned, rows, source_raw, package_raw, reader_raw, members = self.fixture()
        rendered, manifest_raw, _ = mapper.project(
            planned, rows, source_raw, package_raw, reader_raw,
            expected_package_members=members)
        stage_control, _ = prefix_probe._source_selection(planned, rows)
        bridge = readonly.render_bridge(source_raw, package_raw, reader_raw,
                                        manifest_raw, stage_control, rendered)
        self.assertIn(b'def _mapper():', bridge)
        self.assertNotIn(b'__MAPPER_SHA__', bridge)
        runner = readonly.render_runner(manifest_raw, 1761)
        self.assertIn(b'PASS-fixture-mapper-readonly', runner)
        good = {'result': 'PASS-fixture-mapper-readonly',
                'mapper_manifest_sha256': source._sha(manifest_raw),
                'selected_input_count': 1761,
                'sandbox_host_checkout_absent': True,
                'sandbox_protected_roots_absent': True,
                'mapped_package_absent': True, 'context_absent': True,
                'authority_effect': 'none', 'actual_owner_outcome': None}
        compact = lambda value: (json.dumps(value, sort_keys=True,
                                           separators=(',', ':')) + '\n').encode()
        self.assertEqual(readonly.validate_result(compact(good),
                         mapper_sha=source._sha(manifest_raw), selected_count=1761), good)
        for key, value in (('mapped_package_absent', False),
                           ('context_absent', False),
                           ('mapper_manifest_sha256', '0'*64)):
            altered = {**good, key: value}
            with self.subTest(key=key), self.assertRaises(ValueError):
                readonly.validate_result(compact(altered),
                                         mapper_sha=source._sha(manifest_raw),
                                         selected_count=1761)

    def test_actual_generated_hardened_mapper_verify_source_function(self):
        planned, rows, source_raw, package_raw, reader_raw, members = self.fixture()
        rendered, manifest_raw, pins = mapper.project(
            planned, rows, source_raw, package_raw, reader_raw,
            expected_package_members=members)
        tree = ast.parse(rendered['base.py'])
        function = next(node for node in tree.body
                        if isinstance(node, ast.FunctionDef) and
                        node.name == 'verify_source')
        code = compile(ast.fix_missing_locations(ast.Module(body=[function],
                                                 type_ignores=[])),
                       '<selected-generated-mapped-verify-source>', 'exec')
        calls = []
        family = Path('/work/out/legacy-fixture-source')
        def original(row):
            if row != {'path': str(family/'mapped/source-manifest.json'),
                       'sha256': source._sha(manifest_raw)}:
                raise ValueError('wrong mapped source manifest pin')
            return manifest_raw
        def verify_inputs(selected):
            calls.append('verify_inputs')
            self.assertEqual(selected, json.loads(manifest_raw)['files'])
        def binding(path):
            for name, origin in (('source', family/'source'),
                                 ('source_package', family/'source/packages/0001'),
                                 ('reader', family/'reader')):
                expected = origin / ('source-manifest.json' if name != 'source_package'
                                     else 'manifest.json')
                if path == expected:
                    return pins[name]
            raise AssertionError('unexpected binding path')
        selected_reader = SimpleNamespace(
            adapter=SimpleNamespace(source=SimpleNamespace(
                B=SimpleNamespace(verify_inputs=verify_inputs))),
            guard=lambda: calls.append('reader_guard'),
            package=lambda a, b: (calls.append('reader_package'),
                                  self.assertEqual((a, b),
                                      (pins['source']['sha256'],
                                       pins['source_package']['sha256']))))
        space = {'HERE': family/'mapped', 'SOURCE_ROOT': family/'source',
                 'ADAPTER_ROOT': family/'reader',
                 '_t35_binding_path': lambda value: str(value),
                 'original': original,
                 'source': SimpleNamespace(parse=lambda raw: json.loads(raw)),
                 'require': lambda condition, message: condition or
                            (_ for _ in ()).throw(ValueError(message)),
                 'platform': SimpleNamespace(python_version=lambda: '3.14.4'),
                 'importlib': SimpleNamespace(metadata=SimpleNamespace(
                     version=lambda package: {'jsonschema': '4.19.2',
                                              'cryptography': '46.0.5'}[package])),
                 'binding': binding, 'reader': selected_reader,
                 'SOURCE_PIN': pins['source']['sha256'],
                 'PACKAGE_PIN': pins['source_package']['sha256']}
        exec(code, space)
        selected = space['verify_source'](source._sha(manifest_raw))
        self.assertEqual(selected['schema_version'], mapper.MAPPER_SCHEMA)
        self.assertEqual(calls, ['verify_inputs', 'reader_guard', 'reader_package'])
        with self.assertRaises(ValueError):
            space['verify_source']('0'*64)

    def test_mapper_bridge_held_manifest_and_exact_selection(self):
        planned, rows, source_raw, package_raw, reader_raw, members = self.fixture()
        rendered, manifest_raw, _ = mapper.project(
            planned, rows, source_raw, package_raw, reader_raw,
            expected_package_members=members)
        stage_control, _ = prefix_probe._source_selection(planned, rows)
        bridge = readonly.render_bridge(source_raw, package_raw, reader_raw,
                                        manifest_raw, stage_control, rendered)
        space = {}
        exec(compile(bridge, '<selected-mapper-bridge>', 'exec'), space)
        space['_source'] = lambda: {row['path']: row['sha256']
                                    for row in json.loads(source_raw)['files']}
        space['_reader'] = lambda: {row['path']: row['sha256']
                                    for row in json.loads(reader_raw)['files']}
        with tempfile.TemporaryDirectory(prefix='t35-mapper-bridge-') as temp:
            manifest = Path(temp)/'source-manifest.json'
            manifest.write_bytes(manifest_raw)
            space['MAPPER'] = manifest
            selected = space['_mapper']()
            self.assertEqual(len(selected), 1761)
            self.assertEqual(selected[str(planned.layout.family/'mapped/base.py')],
                             source._sha(rendered['base.py']))
            alias = Path(temp)/'alias.json'
            alias.symlink_to(manifest)
            space['MAPPER'] = alias
            space['_mapper'].cache_clear()
            with self.assertRaises(ValueError):
                space['_mapper']()

    def test_child_exit_timeout_and_stream_limit_are_distinct(self):
        python = '/usr/bin/python3'
        rc, out, err, state = readonly._run_child(
            [python, '-c', 'print("ok")'], timeout=2)
        self.assertEqual((rc, out, err), (0, b'ok\n', b''))
        self.assertTrue(state['reaped_observed'])
        self.assertTrue(state['process_group_absent_observed'])
        rc, _, _, state = readonly._run_child(
            [python, '-c', 'raise SystemExit(124)'], timeout=2)
        self.assertEqual(rc, 124)
        self.assertFalse(state['forced_timeout'])
        rc, _, _, state = readonly._run_child(
            [python, '-c', 'import time;time.sleep(3)'], timeout=1)
        self.assertEqual(rc, 124)
        self.assertTrue(state['forced_timeout'])
        self.assertTrue(state['process_group_absent_observed'])
        rc, _, _, state = readonly._run_child(
            [python, '-c', 'import os;os.write(1,b"x"*140000)'], timeout=2)
        self.assertEqual(rc, 125)
        self.assertTrue(state['forced_output_limit'])
        self.assertTrue(state['process_group_absent_observed'])

    def test_child_selector_setup_failure_reaps_group(self):
        started = []
        original = readonly.subprocess.Popen
        def start(*args, **kwargs):
            process = original(*args, **kwargs)
            started.append(process)
            return process
        observation = {}
        with patch.object(readonly.subprocess, 'Popen', side_effect=start), \
             patch.object(readonly.selectors, 'DefaultSelector',
                          side_effect=RuntimeError('synthetic selector setup')):
            with self.assertRaises(RuntimeError):
                readonly._run_child(['/usr/bin/python3', '-c',
                                     'import time;time.sleep(10)'], timeout=2,
                                    observation=observation)
        self.assertEqual(len(started), 1)
        self.assertIsNotNone(started[0].poll())
        self.assertTrue(readonly.milestone._group_absent(started[0].pid))
        self.assertTrue(observation['leader_started'])
        self.assertTrue(observation['reaped_observed'])
        self.assertTrue(observation['process_group_absent_observed'])

    def success_receipt(self):
        digest = 'a'*64
        observed = {'launch_attempted': True, 'leader_started': True,
                    'elapsed_milliseconds': 100, 'forced_timeout': False,
                    'forced_output_limit': False, 'timeout_cap_seconds': 180,
                    'reaped_observed': True, 'process_group_absent_observed': True,
                    'group_wait_milliseconds': 0}
        result = {'status': 'PASS-disposable-mapper-base-readonly',
                  'selected_repository_input_count': 1703,
                  'selected_repository_input_sha256': digest,
                  'source_manifest_sha256': digest,
                  'source_package_manifest_sha256': digest,
                  'reader_manifest_sha256': digest,
                  'mapper_manifest_sha256': digest,
                  'plan_leaf_sha256': digest, 'stage_control_sha256': digest,
                  'mapped_role_sha256': {name: digest for name in mapper.MAPPER_NAMES},
                  'selected_mapper_input_count': 1761,
                  'source_package_leaf_count': 37,
                  'reader_selected_record_count': 29,
                  'reader_accounted_subject_count': 582,
                  'source_elapsed_milliseconds': 100,
                  'reader_elapsed_milliseconds': 100,
                  'mapper_read_elapsed_milliseconds': 100,
                  'child_process_observations': {name: dict(observed) for name in
                         ('source', 'reader', 'mapper_readonly')},
                  'effect_capture_watchdog_seconds': readonly.milestone.PAIR_WALL_SECONDS,
                  'source_stdout_sha256': digest, 'source_stdout_bytes': 10,
                  'reader_stdout_sha256': digest, 'reader_stdout_bytes': 10,
                  'mapper_stdout_sha256': digest, 'mapper_stdout_bytes': 10,
                  'child_stderr_bytes': 0,
                  'source_reader_prestate_preserved': True,
                  'mapped_package_absent': True, 'context_absent': True,
                  'bwrap_sha256': source.BWRAP_SHA,
                  'bwrap_version': 'bubblewrap 0.11.1',
                  'source_bridge_sha256': digest,
                  'reader_bridge_sha256': digest,
                  'mapper_bridge_sha256': digest,
                  'mapper_runner_sha256': digest,
                  'activation_allowed': False,
                  'actual_host_qualification': False,
                  'authority_effect': 'none', 'actual_owner_outcome': None,
                  'scratch_cleaned_after_return': True}
        self.assertEqual(readonly._safe_success(result), result)
        bad = {**result, 'source_elapsed_milliseconds': 101}
        with self.assertRaises(ValueError):
            readonly._safe_success(bad)
        bad = {**result, 'child_process_observations': {
            **result['child_process_observations'],
            'source': {**result['child_process_observations']['source'],
                       'group_wait_milliseconds': -1}}}
        with self.assertRaises(ValueError):
            readonly._safe_success(bad)
        return result

    def test_public_result_is_no_replace_and_sanitized(self):
        with tempfile.TemporaryDirectory(prefix='t35-mapper-receipt-') as temp:
            root = Path(temp)
            with patch.object(readonly.evidence_guard, 'EVIDENCE', root), \
                 patch.object(readonly.evidence_guard, 'REPO', root.parent):
                with patch.object(readonly, '_probe_owned',
                                  return_value=self.success_receipt()) as fake:
                    bound = readonly.run_and_publish()
                    self.assertEqual(bound['sha256'], source._sha(
                        (root/readonly.RECEIPT_NAME).read_bytes()))
                    self.assertEqual(json.loads((root/readonly.RECEIPT_NAME).read_bytes())['status'],
                                     'PASS-disposable-mapper-base-readonly')
                    self.assertEqual(fake.call_count, 1)
                    with self.assertRaises(ValueError):
                        readonly.run_and_publish()
                    self.assertEqual(fake.call_count, 1)
        with tempfile.TemporaryDirectory(prefix='t35-mapper-fail-receipt-') as temp:
            root = Path(temp)
            with patch.object(readonly.evidence_guard, 'EVIDENCE', root), \
                 patch.object(readonly.evidence_guard, 'REPO', root.parent), \
                 patch.object(readonly, '_probe_owned',
                              side_effect=RuntimeError('private detail')):
                readonly.run_and_publish()
                raw = (root/readonly.RECEIPT_NAME).read_bytes()
                self.assertNotIn(b'private detail', raw)
                self.assertEqual(json.loads(raw)['failure_code'], 'UNEXPECTED_EXCEPTION')
        with tempfile.TemporaryDirectory(prefix='t35-mapper-occupied-') as temp:
            root = Path(temp)
            (root/readonly.RECEIPT_NAME).symlink_to(root/'missing')
            with patch.object(readonly.evidence_guard, 'EVIDENCE', root), \
                 patch.object(readonly.evidence_guard, 'REPO', root.parent), \
                 patch.object(readonly, '_probe_owned') as fake:
                with self.assertRaises(ValueError):
                    readonly.run_and_publish()
                fake.assert_not_called()


if __name__ == '__main__':
    unittest.main()
