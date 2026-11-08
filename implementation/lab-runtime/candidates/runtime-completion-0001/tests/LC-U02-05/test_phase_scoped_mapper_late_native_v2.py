"""Versioned late-native Mapper selection; no Source/Reader/Mapper child run."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1 import role_stage, scratch_reader_probe as reader
from t35_external_v1 import scratch_source_probe as source
from t35_external_v1.phase_scoped_v2 import mapper_prepare_0002 as mapper
from t35_external_v1.phase_scoped_v2 import mapper_readonly_0002 as readonly
from t35_external_v1.phase_scoped_v2 import prefix_probe
import test_phase_scoped_mapper_prepare_v2 as previous_mapper_tests


class LateNativeMapperTests(unittest.TestCase):
    def fixture(self):
        planned, rows, _, package_raw, _, members = (
            previous_mapper_tests.MapperPreparationTests().fixture())
        native_name = str(role_stage.NATIVE_REL)
        self.assertIn(native_name, rows)
        del rows[native_name]
        replacement = 'synthetic/late-native-excluded.json'
        rows[replacement] = {'path': replacement, 'sha256': 'b'*64}
        _, source_raw = prefix_probe._source_selection(planned, rows)
        package = json.loads(package_raw)
        package['source_manifest_binding'] = mapper._binding(
            planned.layout.family / reader.SOURCE_REL, source_raw)
        package_raw = reader._json(package)
        reader_raw = reader._reader_manifest(source_raw, package_raw)
        native_raw = readonly._held_native(source.REPO / role_stage.NATIVE_REL,
                                           mode=0o755)
        return planned, rows, source_raw, package_raw, reader_raw, native_raw, members

    def test_authentic_source_selection_omits_mapper_native(self):
        rows, captured = source._source_rows()
        self.assertEqual(len(rows), 1703)
        self.assertEqual(len(captured), 1703)
        self.assertNotIn(str(role_stage.NATIVE_REL), rows)
        native = readonly._held_native(source.REPO / role_stage.NATIVE_REL,
                                       mode=0o755)
        self.assertEqual(len(native), 20243600)
        self.assertEqual(source._sha(native), role_stage.NATIVE_SHA)

    def test_mapper_only_native_projection_and_wrong_selection_refuse(self):
        planned, rows, source_raw, package_raw, reader_raw, native_raw, members = self.fixture()
        rendered, mapper_raw, _ = mapper.project(
            planned, rows, source_raw, package_raw, reader_raw, native_raw,
            expected_package_members=members)
        value = json.loads(mapper_raw)
        self.assertEqual(len(value['files']), 1762)
        native_row = {'path': str(role_stage.NATIVE_REL), 'sha256': role_stage.NATIVE_SHA}
        self.assertEqual([row for row in value['files'] if row['path'] == native_row['path']],
                         [native_row])
        self.assertNotIn(native_row, json.loads(source_raw)['files'])
        self.assertNotIn(native_row, json.loads(reader_raw)['files'])
        self.assertEqual(set(rendered), mapper.MAPPER_NAMES)
        with self.assertRaises(ValueError):
            mapper.project(planned, rows, source_raw, package_raw, reader_raw,
                           native_raw[:-1]+b'X', expected_package_members=members)
        rows[str(role_stage.NATIVE_REL)] = native_row
        with self.assertRaises(ValueError):
            mapper.project(planned, rows, source_raw, package_raw, reader_raw,
                           native_raw, expected_package_members=members)

    def test_late_native_copy_is_exclusive_nonexecutable_and_held(self):
        native_raw = readonly._held_native(source.REPO / role_stage.NATIVE_REL,
                                           mode=0o755)
        with tempfile.TemporaryDirectory(prefix='t35-mapper-native-') as temp:
            snapshot = Path(temp)/'snapshot'
            snapshot.mkdir()
            self.assertEqual(readonly._select_native_for_mapper(snapshot), native_raw)
            target = snapshot / role_stage.NATIVE_REL
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o400)
            self.assertEqual(readonly._held_native(target, mode=0o400), native_raw)
            with self.assertRaises(ValueError):
                readonly._select_native_for_mapper(snapshot)
            target.chmod(0o600)
            with self.assertRaises(ValueError):
                readonly._held_native(target, mode=0o400)
        with tempfile.TemporaryDirectory(prefix='t35-mapper-native-alias-') as temp:
            snapshot = Path(temp)/'snapshot'
            snapshot.mkdir()
            target = snapshot / role_stage.NATIVE_REL
            target.parent.mkdir(parents=True)
            target.symlink_to(source.REPO / role_stage.NATIVE_REL)
            with self.assertRaises(ValueError):
                readonly._select_native_for_mapper(snapshot)

    def test_bridge_map_contains_only_late_native_and_cli_status_matches_receipt(self):
        planned, rows, source_raw, package_raw, reader_raw, native_raw, members = self.fixture()
        rendered, mapper_raw, _ = mapper.project(
            planned, rows, source_raw, package_raw, reader_raw, native_raw,
            expected_package_members=members)
        stage_control, _ = prefix_probe._source_selection(planned, rows)
        bridge = readonly.render_bridge(source_raw, package_raw, reader_raw,
                                        mapper_raw, stage_control, rendered)
        self.assertIn(b"expected['" + str(role_stage.NATIVE_REL).encode() +
                      b"']=NATIVE_SHA", bridge)
        self.assertIn(b'stat.S_IMODE(before.st_mode)!=0o400', bridge)
        self.assertNotIn(b'__NATIVE_REL__', bridge)
        self.assertEqual(readonly.RECEIPT_NAME, 'phase-mapper-readonly-result-0002.json')
        for status, expected in [('PASS-disposable-mapper-base-readonly', 0),
                                 ('FAIL-disposable-mapper-readonly', 1)]:
            with self.subTest(status=status), \
                 patch.object(readonly, 'run_and_publish', return_value={
                     'receipt_binding': {'path': 'fixture-result',
                                         'sha256': 'a'*64, 'size_bytes': 1},
                     'status': status}), redirect_stdout(io.StringIO()) as output:
                self.assertEqual(readonly.main(), expected)
                self.assertEqual(json.loads(output.getvalue())['status'], status)

    def test_public_cli_exit_matches_published_success_or_failure(self):
        valid = previous_mapper_tests.MapperPreparationTests().success_receipt()
        valid['late_mapper_native_sha256'] = role_stage.NATIVE_SHA
        valid['late_mapper_native_nonexecutable'] = True
        valid['selected_mapper_input_count'] = 1762
        for child in valid['child_process_observations'].values():
            child['forced_group_cleanup'] = False
        self.assertEqual(readonly._safe_success(valid), valid)
        for successful in (True, False):
            with self.subTest(successful=successful), \
                 tempfile.TemporaryDirectory(prefix='t35-mapper-cli-') as temp:
                root = Path(temp)
                with patch.object(readonly.evidence_guard, 'EVIDENCE', root), \
                     patch.object(readonly.evidence_guard, 'REPO', root.parent), \
                     patch.object(readonly, '_probe_owned',
                                  return_value=valid if successful else None,
                                  side_effect=None if successful else
                                  RuntimeError('private fixture failure')), \
                     redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(readonly.main(), 0 if successful else 1)
                public = json.loads(output.getvalue())
                recorded = json.loads((root/readonly.RECEIPT_NAME).read_bytes())
                self.assertEqual(public['status'], recorded['status'])
                self.assertEqual(recorded['containment_scope'],
                                 'observed_process_groups_only')
                self.assertIs(recorded['escaped_session_absence_proven'], False)
                self.assertEqual(public['receipt_binding']['sha256'],
                                 source._sha((root/readonly.RECEIPT_NAME).read_bytes()))

    def test_exited_leader_cannot_leave_late_group_writer(self):
        with tempfile.TemporaryDirectory(prefix='t35-mapper-group-') as temp:
            marker = Path(temp)/'late-marker'
            descendant = ("import pathlib,sys,time; time.sleep(2.5); "
                          "pathlib.Path(sys.argv[1]).write_text('late')")
            leader = ("import subprocess,sys,time; "
                      "subprocess.Popen([sys.executable,'-c',sys.argv[2],sys.argv[1]],"
                      "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,"
                      "close_fds=True); "
                      "time.sleep(0.2)")
            rc, stdout, stderr, observed = readonly._run_child(
                [sys.executable, '-c', leader, str(marker), descendant], timeout=3)
            self.assertEqual((rc, stdout, stderr), (126, b'', b''))
            self.assertTrue(observed['reaped_observed'])
            self.assertTrue(observed['process_group_absent_observed'])
            self.assertTrue(observed['forced_group_cleanup'])
            time.sleep(2.7)
            self.assertFalse(marker.exists())

    def test_delayed_leader_wait_is_execution_time_not_group_drain(self):
        rc, out, err, observed = readonly._run_child(
            [sys.executable, '-c',
             'import os,time;os.close(1);os.close(2);time.sleep(5.2)'], timeout=7)
        self.assertEqual((rc, out, err), (0, b'', b''))
        self.assertGreater(observed['elapsed_milliseconds'], 5000)
        self.assertLess(observed['group_wait_milliseconds'], 30000)
        self.assertFalse(observed['forced_group_cleanup'])
        self.assertEqual(readonly._safe_children({'source': observed}, complete=False),
                         {'source': observed})

    def test_closed_pipes_do_not_extend_original_child_timeout(self):
        rc, out, err, observed = readonly._run_child(
            [sys.executable, '-c',
             'import os,time;os.close(1);os.close(2);time.sleep(2.5)'], timeout=1)
        self.assertEqual((rc, out, err), (124, b'', b''))
        self.assertTrue(observed['forced_timeout'])
        self.assertTrue(observed['forced_group_cleanup'])
        self.assertTrue(observed['reaped_observed'])
        self.assertTrue(observed['process_group_absent_observed'])

    def test_scan_failure_retains_unknown_and_selector_failure_reaps(self):
        original = readonly.subprocess.Popen
        for injection, target, failure in (
                ('scan', '_live_group_members', TimeoutError('injected alarm')),
                ('selector', 'selectors.DefaultSelector', RuntimeError('injected setup'))):
            with self.subTest(injection=injection):
                started = []
                state = {'children': {'mapper_readonly': {}}}
                observed = state['children']['mapper_readonly']
                def launch(*args, **kwargs):
                    process = original(*args, **kwargs)
                    started.append(process)
                    return process
                owner, name = (readonly, target) if injection == 'scan' else \
                              (readonly.selectors, 'DefaultSelector')
                with readonly._scratch_custody(state) as scratch:
                    with patch.object(readonly.subprocess, 'Popen', side_effect=launch), \
                         patch.object(owner, name, side_effect=failure):
                        with self.assertRaises(type(failure)):
                            readonly._run_child(
                                [sys.executable, '-c', 'import time;time.sleep(0.2)'],
                                timeout=2, observation=observed)
                self.assertEqual(len(started), 1)
                if injection == 'scan':
                    self.assertTrue(observed['forced_group_cleanup'])
                    self.assertFalse(observed['reaped_observed'])
                    self.assertTrue(state['scratch_retained_unknown'])
                    self.assertTrue(Path(scratch).exists())
                    held = readonly._UNCLOSED_CHILDREN.pop(started[0].pid)
                    self.assertFalse(readonly._live_group_members(held.pid))
                    held.wait(timeout=1)
                    self.assertTrue(readonly.milestone._wait_group_absent(held.pid)[0])
                    shutil.rmtree(scratch)
                else:
                    self.assertIsNotNone(started[0].poll())
                    self.assertTrue(observed['reaped_observed'])
                    self.assertTrue(observed['process_group_absent_observed'])
                    self.assertTrue(readonly.milestone._group_absent(started[0].pid))
                    self.assertFalse(Path(scratch).exists())

    def test_first_cleanup_signal_error_retries_while_leader_is_held(self):
        original = readonly._signal_held_group
        calls = []
        observed = {}
        def one_shot(pid):
            calls.append(pid)
            if len(calls) == 1:
                raise TimeoutError('injected one-shot alarm')
            return original(pid)
        with patch.object(readonly, '_signal_held_group', side_effect=one_shot):
            with self.assertRaises(TimeoutError):
                readonly._run_child(
                    [sys.executable, '-c',
                     'import os,time;os.close(1);os.close(2);time.sleep(2.5)'],
                    timeout=1, observation=observed)
        self.assertGreaterEqual(len(calls), 2)
        self.assertTrue(observed['forced_group_cleanup'])
        self.assertTrue(observed['reaped_observed'])
        self.assertTrue(observed['process_group_absent_observed'])

    def test_repeated_signal_failure_retains_live_group_and_scratch(self):
        state = {'children': {'mapper_readonly': {}}}
        observed = state['children']['mapper_readonly']
        scratch = None
        held = None
        leader = ("import subprocess,sys,time; "
                  "subprocess.Popen([sys.executable,'-c','import time;time.sleep(2)'],"
                  "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);"
                  "time.sleep(0.1)")
        try:
            with readonly._scratch_custody(state) as scratch:
                with patch.object(readonly, '_signal_held_group',
                                  side_effect=PermissionError('injected signal failure')):
                    with self.assertRaises(PermissionError):
                        readonly._run_child([sys.executable, '-c', leader], timeout=3,
                                            observation=observed)
            self.assertTrue(state['scratch_retained_unknown'])
            self.assertTrue(Path(scratch).exists())
            self.assertFalse(observed['reaped_observed'])
            self.assertFalse(observed['process_group_absent_observed'])
            self.assertTrue(observed['forced_group_cleanup'])
            self.assertEqual(len(readonly._UNCLOSED_CHILDREN), 1)
            held = next(iter(readonly._UNCLOSED_CHILDREN.values()))
            self.assertTrue(readonly._held_leader_exited(held.pid))
            self.assertTrue(readonly._live_group_members(held.pid))
        finally:
            if held is not None:
                deadline = time.monotonic() + 4
                while readonly._live_group_members(held.pid) and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertFalse(readonly._live_group_members(held.pid))
                held.wait(timeout=1)
                readonly._UNCLOSED_CHILDREN.pop(held.pid, None)
            if scratch is not None:
                shutil.rmtree(scratch)

    def test_post_reap_absence_failure_retains_scratch_and_refuses(self):
        state = {'children': {'mapper_readonly': {}}}
        observed = state['children']['mapper_readonly']
        with readonly._scratch_custody(state) as scratch:
            with patch.object(readonly.milestone, '_wait_group_absent',
                              return_value=(False, 2000)):
                with self.assertRaises(readonly.ContractError):
                    readonly._run_child(
                        [sys.executable, '-c', 'pass'], timeout=2,
                        observation=observed)
        self.assertTrue(observed['reaped_observed'])
        self.assertFalse(observed['process_group_absent_observed'])
        self.assertTrue(state['scratch_retained_unknown'])
        self.assertTrue(Path(scratch).exists())
        for pid, process in tuple(readonly._UNCLOSED_CHILDREN.items()):
            if process.returncode is not None:
                readonly._UNCLOSED_CHILDREN.pop(pid)
        shutil.rmtree(scratch)

    def test_launch_attempt_without_closure_retains_scratch(self):
        state = {'children': {'mapper_readonly': {'launch_attempted': True,
                                                'leader_started': False}}}
        with readonly._scratch_custody(state) as scratch:
            self.assertTrue(Path(scratch).exists())
        self.assertTrue(state['scratch_retained_unknown'])
        self.assertTrue(Path(scratch).exists())
        shutil.rmtree(scratch)


if __name__ == '__main__':
    unittest.main()
