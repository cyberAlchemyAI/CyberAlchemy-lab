"""Pure selected Source timing and cooperative ownership tests; no builder effects."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import subprocess
import sys
import tempfile
from types import CodeType
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1.path_contract import ContractError
from t35_external_v1.phase_scoped_v2 import prefix_pair_milestone_0001 as milestone


BASE_RAW = b'''def verify_source(pin):
    if pin == 'fail': raise ValueError('original sentinel')
    return pin
def emit(path, value=None):
    return path
'''
BUILD_RAW = b'''def main(pin):
    return pin
def archive(store, pins):
    return (store, pins)
'''


def vector():
    captured = {f'fixture/input-{i:04d}.json': str(i).encode() for i in range(1702)}
    captured[milestone.source.HISTORICAL_SOURCE_PACKAGE['path']] = b'{}\n'
    rows = {name: {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}
            for name, raw in captured.items()}
    return milestone.FrozenVector.from_selected(rows, captured,
        b'{"not_before":"2026-10-19T00:00:00+00:00",'
        b'"expires_at":"2026-10-21T00:00:00+00:00"}\n', b'role\n')


def synthetic_hooks(root: Path, *, broken_write: bool = False):
    source_dir = root / 'source'
    source_dir.mkdir()
    (source_dir / 'build.py').write_bytes(BUILD_RAW)
    (source_dir / 'base.py').write_bytes(BASE_RAW)
    build = types.ModuleType('synthetic.build')
    build.__package__ = 'synthetic'
    exec(compile(BUILD_RAW, str(source_dir / 'build.py'), 'exec'), build.__dict__)
    base = types.ModuleType('synthetic.base')
    exec(compile(BASE_RAW, str(source_dir / 'base.py'), 'exec'), base.__dict__)
    build.verify_source, build.emit = base.verify_source, base.emit
    events = []
    def write(fd, raw):
        assert fd == 2
        events.append(raw)
        return len(raw) - 1 if broken_write and len(events) > 1 else len(raw)
    namespace = {'family': root, 'build': build, 'Path': Path,
                 'hashlib': hashlib, 'os': types.SimpleNamespace(write=write)}
    exec(milestone._render_hooks(BUILD_RAW, BASE_RAW), namespace)
    return build, events


class MilestoneBoundaryTests(unittest.TestCase):
    def test_exact_generated_hooks_preserve_return_and_closed_order(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            build, events = synthetic_hooks(root)
            package = root / 'source/packages/0001'
            self.assertEqual(build.verify_source('one'), 'one')
            build.emit(package / 'retry.json')
            build.emit(package / 'expected-replay.json')
            build.emit(package / 'period.json')
            self.assertEqual(build.verify_source('two'), 'two')
            self.assertEqual(build.archive('store', 'pins'), ('store', 'pins'))
            for name in ('branch.snapshot', 'build-result.json', 'manifest.json'):
                build.emit(package / name)
            telemetry = milestone._parse_milestones(b''.join(events),
                forced_timeout=False, return_code=0)
            self.assertEqual(telemetry['status'], 'COMPLETE')
            self.assertEqual(tuple(row['code'] for row in telemetry['events']),
                             milestone.MILESTONE_SEQUENCE)
            self.assertEqual(milestone._safe_milestones(telemetry), telemetry)
            self.assertEqual(len(events), len(milestone.MILESTONE_SEQUENCE))
        with tempfile.TemporaryDirectory() as scratch:
            build, events = synthetic_hooks(Path(scratch))
            with self.assertRaisesRegex(ValueError, 'original sentinel'):
                build.verify_source('fail')
            self.assertEqual(len(events), 2)
            self.assertEqual(milestone._parse_milestones(b''.join(events),
                forced_timeout=False, return_code=1)['status'], 'INCOMPLETE_CHILD')

    def test_event_write_failure_cannot_produce_success(self):
        with tempfile.TemporaryDirectory() as scratch:
            build, events = synthetic_hooks(Path(scratch), broken_write=True)
            with self.assertRaisesRegex(RuntimeError, 'event write failed'):
                build.verify_source('one')
            self.assertEqual(len(events), 2)
            self.assertEqual(milestone._parse_milestones(b''.join(events),
                forced_timeout=False, return_code=0)['status'], 'INCOMPLETE_CHILD')

    def test_timeout_distinguishes_second_verify_from_archive(self):
        def raw_prefix(count):
            return b''.join(f'T35M1 {name} {index * 10}\n'.encode()
                            for index, name in enumerate(milestone.MILESTONE_SEQUENCE[:count]))
        second_verify = milestone._parse_milestones(raw_prefix(7),
            forced_timeout=True, return_code=124)
        archive = milestone._parse_milestones(raw_prefix(9),
            forced_timeout=True, return_code=124)
        self.assertEqual(second_verify['status'], 'INCOMPLETE_TIMEOUT')
        self.assertEqual(second_verify['events'][-1]['code'], 'VERIFY_2_ENTER')
        self.assertEqual(archive['status'], 'INCOMPLETE_TIMEOUT')
        self.assertEqual(archive['events'][-1]['code'], 'ARCHIVE_ENTER')
        self.assertNotEqual(second_verify['events'][-1], archive['events'][-1])

    def test_malformed_order_duplicate_and_incomplete_tail_refuse_pass(self):
        bad = [b'T35M1 ARCHIVE_ENTER 1\n',
               b'T35M1 RUNNER_READY 0\nT35M1 RUNNER_READY 1\n',
               b'T35M1 RUNNER_READY -1\n',
               b'T35M1 RUNNER_READY 0\nprivate diagnostic\n']
        for raw in bad:
            result = milestone._parse_milestones(raw, forced_timeout=False, return_code=0)
            self.assertEqual(result['status'], 'REFUSED')
            self.assertTrue(result['unrecognized_or_out_of_order_bytes_observed'])
            self.assertNotIn('private', json.dumps(result))
        tail = b'T35M1 RUNNER_READY 1\nT35M1 VERIFY_1_ENT'
        timeout = milestone._parse_milestones(tail, forced_timeout=True, return_code=124)
        self.assertEqual(timeout['status'], 'INCOMPLETE_TIMEOUT')
        self.assertTrue(timeout['incomplete_tail_observed'])
        self.assertEqual(len(timeout['events']), 1)
        self.assertEqual(milestone._parse_milestones(tail,
            forced_timeout=False, return_code=0)['status'], 'REFUSED')
        unexpected_tail = b'T35M1 RUNNER_READY 1\nprivate sensitive text'
        refused = milestone._parse_milestones(unexpected_tail,
            forced_timeout=True, return_code=124)
        self.assertEqual(refused['status'], 'REFUSED')
        self.assertEqual(refused['events'], [])
        self.assertNotIn('private', json.dumps(refused))

    def test_public_projection_rejects_forged_child_telemetry_status(self):
        selected = vector()
        prefix = b'T35M1 RUNNER_READY 0\n'
        telemetry = milestone._parse_milestones(prefix,
            forced_timeout=True, return_code=124)
        child = {'return_code': 124, 'stdout_bytes': 0,
                 'stdout_sha256': milestone.source._sha(b''),
                 'stderr_bytes': len(prefix), 'stderr_sha256': milestone.source._sha(prefix)}
        process = {'pid': 100, 'pgid': 100, 'elapsed_milliseconds': 180000,
                   'reaped_observed': True, 'process_group_absent_observed': True,
                   'group_wait_milliseconds': 100, 'timeout_cap_seconds': 180,
                   'forced_timeout': False, 'forced_output_limit': False}
        outcome = {'status': 'FAIL-disposable-prefix-diagnostic',
                   'input_vector_sha256': selected.sha256,
                   'failure_stage': 'source_child_postreturn',
                   'failure_code': 'CHILD_NONZERO',
                   'child_results': {'source': child},
                   'child_launch_attempted': ['source'],
                   'process_observations': {'source': process},
                   'partial_package': None,
                   'milestone_telemetry': telemetry,
                   'selection_sha256': {}, 'scratch_root_sha256': None,
                   'scratch_cleanup_observed': True,
                   'raw_stdout_stderr_or_exception_published': False,
                   'actual_host_qualification': False, 'activation_allowed': False}
        with self.assertRaises(ContractError):
            milestone._safe_attempt(1, outcome, selected)
        process['forced_timeout'] = True
        safe = milestone._safe_attempt(1, outcome, selected)
        self.assertEqual(safe['milestone_telemetry']['status'], 'INCOMPLETE_TIMEOUT')
        self.assertNotIn('pid', safe['process_observations']['source'])
        outcome['milestone_telemetry'] = milestone._parse_milestones(
            b''.join(f'T35M1 {name} {i}\n'.encode()
                     for i, name in enumerate(milestone.MILESTONE_SEQUENCE)),
            forced_timeout=False, return_code=0)
        with self.assertRaises(ContractError):
            milestone._safe_attempt(1, outcome, selected)
        outcome['milestone_telemetry'] = milestone._parse_milestones(
            b'T35M1 RUNNER_READY 0\nprivate diagnostic',
            forced_timeout=True, return_code=124)
        with patch.object(milestone, 'diagnose', side_effect=[outcome]) as invoked:
            result = milestone.pair(selected)
        self.assertEqual(invoked.call_count, 1)
        self.assertEqual(result['attempts'][1]['status'], 'SKIPPED-unclosed-prior-attempt')
        self.assertNotIn('private', json.dumps(result))

    def test_runner_bindings_and_code_loci_are_exact(self):
        runner = milestone._milestone_runner(BUILD_RAW, BASE_RAW)
        self.assertNotIn('__BUILD_SHA__', runner)
        self.assertNotIn('__BASE_SHA__', runner)
        self.assertNotIn('__MAIN_LINE__', runner)
        self.assertEqual(runner.count('build.main(pin)'), 1)
        with self.assertRaises(ContractError):
            milestone._milestone_runner(b'not Python', BASE_RAW)
        with self.assertRaises(ContractError):
            milestone._milestone_runner(BUILD_RAW, b'def other(): pass\n')

    def test_real_pinned_source_templates_render_exact_callable_loci(self):
        layout = milestone.role_stage.DisposableLayout(
            milestone.FAMILY, milestone.SNAPSHOT, 'legacy-fixture-source')
        generated = {}
        for name in ('build.py', 'base.py'):
            relative = str(milestone.role_stage.INTERFACE /
                milestone.role_stage.ORIGINS['source'] / name)
            raw = (milestone.evidence_guard.REPO / relative).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),
                             milestone.source.ROLE_TEMPLATE_SHA[relative])
            rendered = milestone.source._unsealed_source(raw, layout, name)
            functions = {item.co_name: item.co_firstlineno
                         for item in compile(rendered, relative, 'exec').co_consts
                         if isinstance(item, CodeType)}
            for fn in (('main', 'archive') if name == 'build.py'
                       else ('verify_source', 'emit')):
                self.assertEqual(functions[fn], milestone._function_line(rendered, fn))
            generated[name] = rendered
        runner = milestone._milestone_runner(generated['build.py'], generated['base.py'])
        self.assertIn(hashlib.sha256(generated['build.py']).hexdigest(), runner)
        self.assertIn(hashlib.sha256(generated['base.py']).hexdigest(), runner)

    def test_actual_selected_source_imports_hooks_in_read_only_bwrap(self):
        rows, captured = milestone.source._source_rows()
        self.assertEqual(len(rows), 1703)
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-hook-import-') as scratch:
            root = Path(scratch)
            snapshot, output = root / 'snapshot', root / 'output'
            snapshot.mkdir(); output.mkdir()
            milestone.source._copy_snapshot(snapshot, rows, captured)
            layout = milestone.role_stage.DisposableLayout(
                milestone.FAMILY, milestone.SNAPSHOT, 'legacy-fixture-source')
            staged = milestone.role_stage.stage_rows(layout, lambda name: captured[name])
            generated = {}
            for row in staged:
                name = PurePosixPath(row['output']['path']).name
                raw = row['bytes']
                if row['role'] == 'source' and name.endswith('.py'):
                    raw = milestone.source._unsealed_source(
                        captured[row['input']['path']], layout, name)
                row['bytes'] = raw
                row['output'] = milestone.source._bind(Path(row['output']['path']), raw)
                if row['role'] == 'source' and name in ('build.py', 'base.py'):
                    generated[name] = raw
            episode = milestone._fixture_episode(captured)
            role = b'{"schema_version":"lab-T35-disposable-native-role/v1","authority_effect":"none"}\n'
            planned = milestone.plan(layout, staged, episode_raw=episode, role_raw=role)
            family = output / 'legacy-fixture-source'
            for row in staged:
                if row['role'] not in milestone.ACTIVE_ROLES:
                    continue
                target = family / Path(row['output']['path']).relative_to(str(milestone.FAMILY))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(row['bytes'])
            for suffix, raw in (('source/episode-contract.json', episode),
                                ('source/context-native-role.json', role),
                                ('construction-selection.json', planned.plan_leaf_bytes)):
                target = family / suffix
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            stage_control, manifest = milestone._source_selection(planned, rows)
            (snapshot / '_t35_stage_selection.json').write_bytes(stage_control)
            (family / milestone.reader.SOURCE_REL).write_bytes(manifest)
            bridge = (milestone.source.SCRATCH_BRIDGE.replace(
                '__SOURCE_MANIFEST_SHA__', milestone.source._sha(manifest)).replace(
                '__STAGE_SELECTION_SHA__', milestone.source._sha(stage_control)))
            (snapshot / '_t35_external_runtime_capture.py').write_text(bridge)
            runner = milestone._milestone_runner(generated['build.py'], generated['base.py'])
            marker = 'build.main(pin)\n'
            self.assertEqual(runner.count(marker), 1)
            import_only = runner.split(marker)[0] + "print('{\"result\":\"IMPORT_ONLY_PASS\"}',flush=True)\n"
            (snapshot / '_t35_import_only_runner.py').write_text(import_only)
            before = milestone.source._tree_files(family)
            argv = milestone.reader._sandbox_argv(snapshot, family,
                                                 '_t35_import_only_runner.py')
            rc, stdout, stderr = milestone.source._run_bounded(argv, timeout=30)
            self.assertEqual(rc, 0, msg=f'import-only refusal; stderr_sha={hashlib.sha256(stderr).hexdigest()}')
            self.assertEqual(json.loads(stdout), {'result': 'IMPORT_ONLY_PASS'})
            ready = b'T35M1 RUNNER_READY '
            self.assertTrue(stderr.startswith(ready))
            self.assertEqual(len(stderr.splitlines()), 1)
            self.assertEqual(milestone._parse_milestones(stderr,
                forced_timeout=False, return_code=0)['events'][0]['code'], 'RUNNER_READY')
            self.assertEqual(milestone.source._tree_files(family), before)
            self.assertFalse((family / 'source/packages').exists())

    def test_live_two_process_lock_contention_before_capture(self):
        evidence = milestone.evidence_guard.EVIDENCE
        before = set(p.name for p in evidence.iterdir())
        command = [sys.executable, '-c',
            'from t35_external_v1.phase_scoped_v2 import prefix_pair_milestone_0001 as m\n'
            'from t35_external_v1.path_contract import ContractError\n'
            'from unittest.mock import patch\n'
            'try:\n'
            '    with patch.object(m,"_run_pair_owned",side_effect=RuntimeError("BAD_EFFECT")):\n'
            '        m.run_pair(publish=True)\n'
            '    print("BAD")\n'
            'except ContractError: print("REFUSED")\n']
        env = {**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[2])}
        with milestone._exclusive_controller() as held:
            self.assertTrue(held.attached())
            result = subprocess.run(command, env=env, cwd=milestone.evidence_guard.REPO,
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, 'REFUSED\n')
            self.assertEqual(result.stderr, '')
        self.assertEqual(set(p.name for p in evidence.iterdir()), before)

    def test_detached_held_directory_refuses_on_exit_and_releases(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch) / 'evidence'
            root.mkdir()
            with patch.object(milestone.evidence_guard, 'EVIDENCE', root):
                with self.assertRaises(ContractError):
                    with milestone._exclusive_controller() as held:
                        self.assertTrue(held.attached())
                        root.rename(root.with_name('detached'))
                self.assertFalse(root.exists())


if __name__ == '__main__':
    unittest.main()
