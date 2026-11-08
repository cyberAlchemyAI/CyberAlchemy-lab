"""Static and synthetic release tests; never copy private body or call Docker."""
from __future__ import annotations

import json
import os
import hashlib
import ast
import contextlib
import copy
import io
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest import mock

import controller
import docker_protocol
import mapper_once

REAL_ABSENT = docker_protocol.SubprocessDocker.absent

LABEL = 'b' * 32
CID = 'a' * 64
NAME = 'cal-mapper-only-20261020-0001-release3'


class FakeDocker:
    def __init__(self, *, wrong_exit=False, unavailable=False):
        self.wrong_exit = wrong_exit
        self.unavailable = unavailable
        self.created = False
        self.started = False
        self.removed = False
        self.create_calls = 0

    def lookup_name(self, name, *, deadline):
        if self.unavailable:
            raise ConnectionError('synthetic daemon unavailable')
        return [self.inspect(CID, deadline=deadline)] if self.created and not self.removed else []

    def create(self, args, *, deadline):
        self.create_calls += 1
        self.created = True
        return CID

    def inspect(self, cid, *, deadline):
        return {'Id': cid, 'Name': '/' + NAME, 'Image': controller.IMAGE,
                'Config': {'Image': controller.IMAGE,
                           'Labels': {'cal.mapper.attempt': LABEL}},
                'State': {'Status': 'exited' if self.started else 'created',
                          'ExitCode': 1 if self.wrong_exit else 0}}

    def start_wait(self, cid, *, deadline):
        self.started = True
        return 1 if self.wrong_exit else 0

    def remove(self, cid, *, force, deadline):
        self.removed = True

    def absent(self, cid, *, deadline):
        return self.removed


class SelectedResponseDocker(FakeDocker):
    """Fake create/start/remove with the real production absence parser."""
    def _run(self, args, *, deadline):
        cid = args[-1]
        return subprocess.CompletedProcess(
            args, 1, b'[]\n',
            ('Error response from daemon: No such container: ' + cid + '\n').encode())

    def absent(self, cid, *, deadline):
        return REAL_ABSENT(self, cid, deadline=deadline)


class ReleaseStaticTests(unittest.TestCase):
    def test_exact_reviewed_release_selection_without_attempt(self):
        selected = controller.trusted_selection()
        self.assertTrue(controller.EFFECT_ENABLED and mapper_once.EFFECT_ENABLED)
        self.assertEqual(selected['fresh_attempt'], str(controller.ATTEMPT))
        self.assertEqual(selected['source_successor'], controller.SOURCE_SUCCESSOR)
        self.assertEqual(selected['reviewed_reader_successor'], controller.READER_SUCCESSOR)
        self.assertEqual(selected['controller4_freeze_sha256'], controller.CONTROLLER4_FREEZE_SHA)
        self.assertEqual(selected['controller4_review_sha256'], controller.CONTROLLER4_REVIEW_SHA)
        self.assertEqual(selected['container_identity']['runtime_user'], '1000:1000')
        self.assertEqual(selected['container_identity']['runtime_userns'], 'host')
        self.assertEqual(selected['release1_freeze_sha256'], controller.RELEASE1_FREEZE_SHA)
        self.assertEqual(selected['release1_review_sha256'], controller.RELEASE1_REVIEW_SHA)
        self.assertEqual(selected['release2_freeze_sha256'], controller.RELEASE2_FREEZE_SHA)
        self.assertEqual(selected['release2_review_sha256'], controller.RELEASE2_REVIEW_SHA)
        self.assertEqual(controller.docker_absence_observation_gate(selected)['result'],
                         'PASS_READ_ONLY_SELECTED_DOCKER_ABSENCE_GRAMMAR')
        self.assertFalse(os.path.lexists(controller.ATTEMPT))

    def test_source_reader_and_native_provenance_have_distinct_claims(self):
        selected = controller.trusted_selection()
        source = controller.source_predecessor_gate(selected)
        reader = controller.reader_predecessor_gate(selected)
        native = controller.native_load_gate(selected)
        self.assertEqual(source['result'], 'PASS_REVIEWED_SOURCE_PREDECESSOR')
        self.assertIsNone(source['external_os_exit_observation'])
        self.assertEqual(reader['external_exit'], 0)
        self.assertEqual(native['result'], 'PASS_LOAD_ONLY')
        self.assertFalse(source['archive_body_opened'])
        self.assertFalse(reader['archive_body_opened'])
        changed = dict(selected, source_successor={})
        with self.assertRaisesRegex(ValueError, 'Source successor'):
            controller.source_predecessor_gate(changed)

    def test_exact_effect_vector_and_privilege_injection_refused(self):
        args = controller.docker_create_argv(controller.trusted_selection(), label=LABEL)
        docker_protocol.exact_create_argv(args, LABEL)
        self.assertEqual(args[args.index('--name') + 1], NAME)
        self.assertEqual(args[args.index('--user') + 1], '1000:1000')
        self.assertEqual(args[args.index('--userns') + 1], 'host')
        self.assertIn('TMPDIR=/attempt/scratch', args)
        self.assertNotIn('--privileged', args)
        self.assertNotIn('--pid', args)
        for added in ('--privileged', '--device', '--pid', '--security-opt'):
            with self.subTest(added=added):
                with self.assertRaisesRegex(ValueError, 'vector differs'):
                    docker_protocol.exact_create_argv(args[:3] + [added] + args[3:], LABEL)

    def test_fake_one_shot_pass_and_unknown_are_closed(self):
        args = controller.docker_create_argv(controller.trusted_selection(), label=LABEL)
        with tempfile.TemporaryDirectory(prefix='cal-mapper-release-fake-') as temp:
            fake = FakeDocker()
            result = docker_protocol.reconcile_once(fake, args, image=controller.IMAGE,
                                                    label=LABEL, name=NAME,
                                                    evidence_dir=Path(temp))
            self.assertEqual(result['overall'], 'PASS')
            self.assertTrue(result['container_absent'] and fake.removed)
            self.assertEqual(fake.create_calls, 1)
        for options in ({'wrong_exit': True}, {'unavailable': True}):
            with self.subTest(options=options):
                with tempfile.TemporaryDirectory(prefix='cal-mapper-release-fake-') as temp:
                    fake = FakeDocker(**options)
                    with self.assertRaises(docker_protocol.OneShotUnknown):
                        docker_protocol.reconcile_once(fake, args, image=controller.IMAGE,
                                                        label=LABEL, name=NAME,
                                                        evidence_dir=Path(temp))
                    terminal = json.loads((Path(temp) / 'terminal.json').read_bytes())
                    self.assertEqual(terminal['overall'], 'UNKNOWN')
                    self.assertFalse(terminal['retry_allowed'])
                    self.assertEqual(fake.create_calls, 0 if options.get('unavailable') else 1)

    def test_authorization_gate_precedes_copy_and_docker(self):
        with mock.patch.object(controller, 'release_freeze_gate',
                               return_value={'freeze_sha256': 'a' * 64}), \
             mock.patch.object(controller, 'release_authorization_gate',
                               side_effect=ValueError('approval absent')) as approval, \
             mock.patch.object(controller, 'prepare_exact_attempt',
                               side_effect=AssertionError('copy reached')) as copy, \
             mock.patch.object(docker_protocol, 'SubprocessDocker',
                               side_effect=AssertionError('Docker reached')) as docker:
            with self.assertRaisesRegex(ValueError, 'approval absent'):
                controller.execute_reviewed_one_shot()
            approval.assert_called_once()
            copy.assert_not_called()
            docker.assert_not_called()

    def test_unapproved_release_does_not_exist(self):
        approval = controller.LOCAL / 'mapper-only-docker-release-0003-authorization.json'
        self.assertFalse(approval.exists())
        self.assertFalse(os.path.lexists(controller.ATTEMPT))

    def test_actual_selected_absence_grammar_and_ambiguity(self):
        observed = json.loads((controller.HERE / 'docker-absence-observation.json').read_bytes())
        self.assertEqual(observed['inspect_exit'], 1)
        self.assertEqual(observed['inspect_stdout'], '[]\n')
        self.assertEqual(observed['lookup_exit'], 0)
        cid = '0' * 64
        args = observed['inspect_argv']
        response = subprocess.CompletedProcess(args, 1,
                                               observed['inspect_stdout'].encode(),
                                               observed['inspect_stderr'].encode())
        driver = docker_protocol.SubprocessDocker()
        with mock.patch.object(driver, '_run', return_value=response):
            self.assertTrue(driver.absent(cid, deadline=999999999999))
        wrong = [
            (1, b'[]\n', response.stderr.replace(cid.encode(), b'1' * 64)),
            (1, b'[]\n', b'prefix ' + response.stderr),
            (1, b'[]\n', b'Cannot connect to Docker daemon\n'),
            (1, b'', response.stderr),
            (2, b'[]\n', response.stderr),
        ]
        for exit_code, stdout, stderr in wrong:
            with self.subTest(exit_code=exit_code, stdout=stdout, stderr=stderr):
                with mock.patch.object(driver, '_run', return_value=
                                       subprocess.CompletedProcess(args, exit_code,
                                                                   stdout, stderr)):
                    with self.assertRaises(docker_protocol.DockerCommandError):
                        driver.absent(cid, deadline=999999999999)
        with mock.patch.object(driver, '_run', side_effect=ConnectionError('daemon unavailable')):
            with self.assertRaisesRegex(ConnectionError, 'daemon unavailable'):
                driver.absent(cid, deadline=999999999999)

    def _synthetic_controller_run(self, *, drift_terminal=False):
        """Full controller/protocol join without stage copy or real Docker."""
        with tempfile.TemporaryDirectory(prefix='cal-mapper-release3-composition-') as temp:
            attempt = Path(temp) / 'attempt'
            selection = copy.deepcopy(controller.trusted_selection())
            old = selection['fresh_attempt']
            selection['fresh_attempt'] = str(attempt)
            selection['copy_to'] = str(attempt / 'root')
            selection['copy_and_mount_plan']['output_package_host'] = \
                selection['copy_and_mount_plan']['output_package_host'].replace(old, str(attempt))
            for row in selection['copy_and_mount_plan']['container_mounts']:
                if 'source' in row:
                    row['source'] = row['source'].replace(old, str(attempt))

            def prepare(*args):
                attempt.mkdir(mode=0o700)
                return {'attempt': str(attempt), 'stage_files': 986,
                        'projected_mapper_files': 5, 'native_sha256': 'f' * 64,
                        'entrypoint_sha256': 'e' * 64,
                        'source_stage_modified': False}

            def real_reconcile(*args, **kwargs):
                terminal = original_reconcile(*args, **kwargs)
                if drift_terminal:
                    leaf = kwargs['evidence_dir'] / 'terminal.json'
                    leaf.write_bytes(leaf.read_bytes() + b' ')
                return terminal

            original_reconcile = docker_protocol.reconcile_once
            fake = SelectedResponseDocker()
            output_gate = mock.Mock(return_value={'result': 'PASS_CANDIDATE_OUTPUT_ONLY',
                                                   'files': 55})
            with mock.patch.object(controller, 'ATTEMPT', attempt), \
                 mock.patch.object(controller, 'trusted_selection', return_value=selection), \
                 mock.patch.object(controller, 'release_freeze_gate',
                                   return_value={'freeze_sha256': 'a' * 64,
                                                 'entrypoint_sha256': 'e' * 64}), \
                 mock.patch.object(controller, 'release_authorization_gate'), \
                 mock.patch.object(controller, 'exact_stage_plan', return_value={'files': []}), \
                 mock.patch.object(controller, 'stage_metadata_gate'), \
                 mock.patch.object(controller, 'copy_plan'), \
                 mock.patch.object(controller, 'source_predecessor_gate'), \
                 mock.patch.object(controller, 'reader_predecessor_gate'), \
                 mock.patch.object(controller, 'native_load_gate'), \
                 mock.patch.object(controller, 'docker_absence_observation_gate'), \
                 mock.patch.object(controller, 'prepare_exact_attempt', side_effect=prepare), \
                 mock.patch.object(controller, 'verify_mapped_output', output_gate), \
                 mock.patch.object(controller.secrets, 'token_hex', return_value=LABEL), \
                 mock.patch.object(docker_protocol, 'SubprocessDocker', return_value=fake), \
                 mock.patch.object(docker_protocol, 'reconcile_once', side_effect=real_reconcile):
                if drift_terminal:
                    with self.assertRaisesRegex(ValueError, 'evidence bytes or identity differ'):
                        controller.execute_reviewed_one_shot()
                    output_gate.assert_not_called()
                    self.assertFalse((attempt / 'evidence/final.json').exists())
                else:
                    with contextlib.redirect_stdout(io.StringIO()):
                        controller.execute_reviewed_one_shot()
                    output_gate.assert_called_once()
                    terminal_raw = (attempt / 'evidence/terminal.json').read_bytes()
                    final = json.loads((attempt / 'evidence/final.json').read_bytes())
                    self.assertEqual(final['overall'], 'PASS')
                    self.assertEqual(final['terminal_sha256'],
                                     hashlib.sha256(terminal_raw).hexdigest())
                    self.assertEqual(terminal_raw,
                                     docker_protocol.evidence_json_bytes(json.loads(terminal_raw)))
                    self.assertTrue(fake.removed)
                    self.assertEqual(fake.create_calls, 1)

    def test_full_synthetic_controller_composition_pass(self):
        self._synthetic_controller_run()

    def test_full_synthetic_controller_rejects_terminal_drift(self):
        self._synthetic_controller_run(drift_terminal=True)

    def test_exact_55_leaf_verifier_builder_pin_and_separate_predecessor_pins(self):
        """Use only the pinned original result assignment AST; no builder effect."""
        selected = controller.trusted_selection()
        build_path = controller.V3 / 'generated' / controller.MAPPER / 'build.py'
        raw = build_path.read_bytes()
        expected_sha = controller.selected_projected_files(selected)[controller.MAPPER + '/build.py']
        self.assertEqual(controller.sha(raw), expected_sha)
        tree = ast.parse(raw)
        build = next(node for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name == 'build')
        assignment = next(node for node in build.body
                          if isinstance(node, ast.Assign) and
                          any(isinstance(target, ast.Name) and target.id == 'result'
                              for target in node.targets))
        scope = {'pin': selected['mapper_manifest_sha256'], 'started': 0,
                 'time': types.SimpleNamespace(monotonic=lambda: 1)}
        exec(compile(ast.Module(body=[assignment], type_ignores=[]),
                     str(build_path), 'exec'), scope)
        original_result = scope['result']
        self.assertEqual(original_result['source_sha256'], selected['mapper_manifest_sha256'])
        self.assertNotEqual(original_result['source_sha256'],
                            selected['manifest']['original_source_binding']['sha256'])

        with tempfile.TemporaryDirectory(prefix='cal-mapper-release3-output-') as temp:
            attempt = Path(temp)
            package = attempt / 'root' / controller.MAPPER / 'packages/0001'
            package.mkdir(parents=True, mode=0o700)
            names = selected['copy_and_mount_plan']['expected_package_members']
            self.assertEqual(len(names), 55)

            def put(name, value):
                path = package / name
                path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                path.write_bytes(controller.canonical(value))
                path.chmod(0o600)

            def manifest(*, mapper_pin=None):
                put('manifest.json', {
                    'schema_version': 'lab-mapped-context-package/v1-candidate',
                    'files': [{'path': controller.MAPPER + '/packages/0001/' + name,
                               'sha256': controller.sha((package / name).read_bytes())}
                              for name in sorted(set(names) - {'manifest.json'})],
                    'source_manifest_binding': {
                        'path': controller.MAPPER + '/source-manifest.json',
                        'sha256': selected['mapper_manifest_sha256']
                                  if mapper_pin is None else mapper_pin},
                    'authority_effect': 'none', 'actual_owner_outcome': None})

            for name in names:
                if name != 'manifest.json':
                    put(name, {})
            put('build-result.json', original_result)
            mapping = {'native_seal_processes': 2,
                       'actual_cold_native_read_processes': 2,
                       'native_domain_mapping_supplied': True,
                       'context_or_ontology_view_carriers_generated': False,
                       'authority_effect': 'none', 'actual_owner_outcome': None,
                       'source_package_binding':
                       selected['manifest']['original_package_binding']}
            put('mapping.json', mapping)
            put('native-output.json', {'authority_effect': 'none',
                                      'cut': {'semantic_cursor': 25},
                                      'governance_cursor': 25,
                                      'governed_nodes': [{}] * 15})
            manifest()
            with mock.patch.object(controller, 'ATTEMPT', attempt):
                positive = controller.verify_mapped_output(selected)
                self.assertEqual(positive['result'], 'PASS_CANDIDATE_OUTPUT_ONLY')
                self.assertEqual(positive['files'], 55)

                wrong_result = dict(original_result,
                                    source_sha256=selected['manifest']['original_source_binding']['sha256'])
                put('build-result.json', wrong_result)
                manifest()
                with self.assertRaisesRegex(ValueError, 'output manifest or bounded result differs'):
                    controller.verify_mapped_output(selected)
                put('build-result.json', original_result)

                wrong_mapping = dict(mapping, source_package_binding={
                    **mapping['source_package_binding'],
                    'sha256': selected['mapper_manifest_sha256']})
                put('mapping.json', wrong_mapping)
                manifest()
                with self.assertRaisesRegex(ValueError, 'output manifest or bounded result differs'):
                    controller.verify_mapped_output(selected)
                put('mapping.json', mapping)

                manifest(mapper_pin=selected['manifest']['original_source_binding']['sha256'])
                with self.assertRaisesRegex(ValueError, 'output manifest or bounded result differs'):
                    controller.verify_mapped_output(selected)


if __name__ == '__main__':
    unittest.main()
