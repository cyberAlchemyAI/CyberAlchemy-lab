"""Synthetic causal checks only; no private archive, native role, or Docker effect."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

import controller
import docker_protocol
from held_stage import HeldAttempt
import output_verifier
from root_guard import RootGuard


def raw(value):
    return (json.dumps(value, sort_keys=True) + '\n').encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def synthetic_package(base: Path, mutate=None):
    parent = base / 'packages'
    parent.mkdir(mode=0o700)
    package = parent / '0001'
    package.mkdir(mode=0o700)
    for family in ('semantic', 'governance'):
        (package / family).mkdir(mode=0o700)
    semantic = {}
    docs = {}
    for index in range(1, 26):
        name = f'semantic/{index:08d}.json'
        event = {'event_family': 'semantic', 'semantic_cursor': index,
                 'event_id': f'semantic:{index}', 'event_digest': f'{index:064x}'}
        semantic[index] = event
        docs[name] = event
    for index in range(1, 26):
        event = semantic[index]
        docs[f'governance/{index:08d}.json'] = {
            'event_family': 'governance', 'governance_cursor': index,
            'semantic_ref': {'semantic_cursor': index,
                             'semantic_event_id': event['event_id'],
                             'semantic_event_digest': event['event_digest']}}
    docs['request.json'] = {'selector': 'synthetic'}
    docs['native-output.json'] = {'authority_effect': 'none',
                                  'cut': {'semantic_cursor': 25},
                                  'governance_cursor': 25,
                                  'governed_nodes': [{} for _ in range(15)]}
    docs['mapping.json'] = {
        'source_package_binding': {'path': output_verifier.SOURCE +
                                   '/packages/0001/manifest.json',
                                   'sha256': output_verifier.SOURCE_PACKAGE_SHA},
        'native_seal_processes': 2, 'actual_cold_native_read_processes': 2,
        'native_domain_mapping_supplied': True,
        'context_or_ontology_view_carriers_generated': False,
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'semantic_cursor': 25, 'governance_cursor': 25,
        'rows': [{} for _ in range(25)]}
    docs['build-result.json'] = {
        'result': 'PASS', 'node_count': 15, 'edge_count': 10,
        'exact_governance_joins': 25, 'cold_native_replay_byte_parity': True,
        'same_signed_source_cut': True,
        'source_sha256': output_verifier.MAPPER_SHA,
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'task_complete': False}
    if mutate is not None:
        mutate(docs)
    for name, value in docs.items():
        path = package / name
        path.write_bytes(raw(value))
        path.chmod(0o600)
    docs['manifest.json'] = {
        'schema_version': 'lab-mapped-context-package/v1-candidate',
        'files': [{'path': output_verifier.MAPPER + '/packages/0001/' + name,
                   'sha256': sha((package / name).read_bytes())}
                  for name in sorted(docs)],
        'source_manifest_binding': {'path': output_verifier.MAPPER +
                                    '/source-manifest.json',
                                    'sha256': output_verifier.MAPPER_SHA},
        'authority_effect': 'none', 'actual_owner_outcome': None}
    (package / 'manifest.json').write_bytes(raw(docs['manifest.json']))
    (package / 'manifest.json').chmod(0o600)
    return parent, package, list(docs)


class CandidateTests(unittest.TestCase):
    def test_selector_allocation_failure_reaps_and_attempts_both_closes(self):
        class Pipe:
            def __init__(self, fails=False):
                self.fails = fails
                self.closes = 0
            def close(self):
                self.closes += 1
                if self.fails:
                    raise OSError('synthetic close failure')
        class Process:
            pid = 12345
            def __init__(self):
                self.stdout, self.stderr = Pipe(True), Pipe()
                self.reaped = False
            def poll(self):
                return None
            def wait(self, *, timeout):
                self.reaped = True
                return -9
        proc = Process()
        with mock.patch.object(docker_protocol.subprocess, 'Popen', return_value=proc), \
             mock.patch.object(docker_protocol.selectors, 'DefaultSelector',
                               side_effect=RuntimeError('synthetic selector allocation')), \
             mock.patch.object(docker_protocol.os, 'killpg') as kill:
            with self.assertRaisesRegex(RuntimeError, 'selector allocation') as caught:
                docker_protocol.SubprocessDocker._run(['/usr/bin/docker', 'inspect'],
                                                      deadline=time.monotonic() + 10)
        self.assertEqual(proc.stdout.closes, 1)
        self.assertEqual(proc.stderr.closes, 1)
        self.assertTrue(proc.reaped)
        kill.assert_called_once_with(proc.pid, docker_protocol.signal.SIGKILL)
        self.assertEqual(caught.exception.secondary_cleanup_errors[0][0], 'stdout')

    def test_successful_child_with_close_fault_cannot_return_pass(self):
        class Pipe:
            def __init__(self, fails=False):
                self.fails = fails
                self.closes = 0
            def fileno(self):
                return 3
            def close(self):
                self.closes += 1
                if self.fails:
                    raise OSError('synthetic close failure')
        class Process:
            def __init__(self):
                self.stdout, self.stderr = Pipe(True), Pipe()
            def wait(self, *, timeout):
                return 0
        class Selector:
            def __init__(self):
                self.closes = 0
            def register(self, *args):
                pass
            def get_map(self):
                return {}
            def close(self):
                self.closes += 1
        proc, selector = Process(), Selector()
        with mock.patch.object(docker_protocol.subprocess, 'Popen', return_value=proc), \
             mock.patch.object(docker_protocol.selectors, 'DefaultSelector',
                               return_value=selector), \
             mock.patch.object(docker_protocol.os, 'set_blocking'):
            with self.assertRaises(BaseExceptionGroup):
                docker_protocol.SubprocessDocker._run(['/usr/bin/docker', 'inspect'],
                                                      deadline=time.monotonic() + 10)
        self.assertEqual((selector.closes, proc.stdout.closes, proc.stderr.closes),
                         (1, 1, 1))

    def fake_protocol(self, *, client_exit=0, daemon_exit=0, interrupt=False):
        selection = controller.trusted_selection()
        label, cid = 'b' * 32, 'a' * 64
        args = controller.docker_create_argv(selection, label=label)
        class Fake:
            created = started = removed = False
            create_calls = 0
            def lookup_name(self, name, *, deadline):
                return [self.inspect(cid, deadline=deadline)] if self.created and not self.removed else []
            def create(self, argv, *, deadline):
                self.create_calls += 1
                self.created = True
                return cid
            def inspect(self, item, *, deadline):
                return {'Id': cid, 'Name': '/' + controller.NAME,
                        'Image': controller.IMAGE,
                        'Config': {'Image': controller.IMAGE,
                                   'Labels': {'cal.mapper.attempt': label}},
                        'State': {'Status': 'exited' if self.started else 'created',
                                  'ExitCode': daemon_exit}}
            def start_wait(self, item, *, deadline):
                self.started = True
                if interrupt:
                    raise KeyboardInterrupt('synthetic ordinary interruption')
                return client_exit
            def remove(self, item, *, force, deadline):
                self.removed = True
                self.forced = force
            def absent(self, item, *, deadline):
                return self.removed
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            base.chmod(0o700)
            claim = HeldAttempt(base / 'attempt')
            try:
                claim.claim()
                claim.mkdir('evidence', 0o700)
                fake = Fake()
                error = None
                try:
                    result = docker_protocol.reconcile_once(
                        fake, args, image=controller.IMAGE, label=label,
                        name=controller.NAME, evidence_dir=claim.path / 'evidence',
                        evidence_claim=claim, expected_args=args)
                except docker_protocol.OneShotUnknown as caught:
                    error = caught
                    result = caught.evidence
                terminal = json.loads((claim.path / 'evidence/terminal.json').read_bytes())
                self.assertEqual(terminal['overall'], result['overall'])
                self.assertEqual(fake.create_calls, 1)
                self.assertTrue(fake.removed)
                self.assertTrue(result['container_absent'])
                return result, error, fake
            finally:
                claim.close()

    def test_docker_fake_pass_and_strict_scalar_exits(self):
        result, error, fake = self.fake_protocol()
        self.assertIsNone(error)
        self.assertEqual(result['overall'], 'PASS')
        self.assertFalse(fake.forced)
        for value in (False, 0.0):
            with self.subTest(value=value):
                result, error, fake = self.fake_protocol(client_exit=value)
                self.assertIsInstance(error, docker_protocol.OneShotUnknown)
                self.assertEqual(result['overall'], 'UNKNOWN')
                self.assertTrue(fake.forced)
                result, error, fake = self.fake_protocol(daemon_exit=value)
                self.assertIsInstance(error, docker_protocol.OneShotUnknown)
                self.assertEqual(result['overall'], 'UNKNOWN')
                self.assertTrue(fake.forced)

    def test_docker_ordinary_interrupt_closes_owned_container(self):
        result, error, fake = self.fake_protocol(interrupt=True)
        self.assertIsInstance(error, docker_protocol.OneShotUnknown)
        self.assertIsInstance(error.primary, KeyboardInterrupt)
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertTrue(fake.forced and fake.removed)

    def test_real_stage_read_only_and_effect_disabled(self):
        selection = controller.trusted_selection()
        self.assertEqual(len(selection['verifier']['expected_package_members']), 55)
        self.assertEqual(controller.preflight()['effect'], 'NOT_RUN')
        with self.assertRaisesRegex(controller.Refused, 'EFFECT_DISABLED'):
            controller.execute()
        self.assertFalse(controller.DOCKER_ATTEMPT.exists())

    def test_output_positive_original_native_shape(self):
        with tempfile.TemporaryDirectory() as temp:
            parent, _, members = synthetic_package(Path(temp))
            fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                result = output_verifier.verify(fd, members)
                self.assertEqual(result['files'], 55)
            finally:
                os.close(fd)

    def test_output_rejects_nested_only_governance_cursor(self):
        with tempfile.TemporaryDirectory() as temp:
            def wrong(docs):
                docs['native-output.json']['cut']['governance_cursor'] = 25
                del docs['native-output.json']['governance_cursor']
            parent, _, members = synthetic_package(Path(temp), wrong)
            fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                with self.assertRaisesRegex(output_verifier.Refused, 'NATIVE_CUT'):
                    output_verifier.verify(fd, members)
            finally:
                os.close(fd)

    def test_output_rejects_coherent_wrong_join(self):
        with tempfile.TemporaryDirectory() as temp:
            def wrong(docs):
                docs['governance/00000001.json']['semantic_ref']['semantic_event_id'] = 'wrong'
            parent, _, members = synthetic_package(Path(temp), wrong)
            fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                with self.assertRaisesRegex(output_verifier.Refused, 'GOVERNANCE_JOIN'):
                    output_verifier.verify(fd, members)
            finally:
                os.close(fd)

    def test_output_rejects_package_replacement(self):
        with tempfile.TemporaryDirectory() as temp:
            parent, package, members = synthetic_package(Path(temp))
            fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            original = output_verifier.owned_dir(fd, '0001')
            try:
                package.rename(parent / 'displaced')
                (parent / '0001').mkdir(mode=0o700)
                with self.assertRaisesRegex(output_verifier.Refused, 'INVENTORY_DRIFT'):
                    output_verifier.verify(fd, members)
                self.assertNotEqual(os.fstat(original).st_ino,
                                    (parent / '0001').stat().st_ino)
            finally:
                os.close(original)
                os.close(fd)

    def test_output_rejects_package_swap_during_held_read(self):
        with tempfile.TemporaryDirectory() as temp:
            parent, package, members = synthetic_package(Path(temp))
            fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            original_leaf = output_verifier.leaf
            called = False
            def swap_after_first(*args, **kwargs):
                nonlocal called
                result = original_leaf(*args, **kwargs)
                if not called:
                    called = True
                    package.rename(parent / 'displaced')
                    (parent / '0001').mkdir(mode=0o700)
                return result
            try:
                with mock.patch.object(output_verifier, 'leaf', side_effect=swap_after_first):
                    with self.assertRaisesRegex(output_verifier.Refused,
                                                'OUTPUT_PACKAGE_DETACHED'):
                        output_verifier.verify(fd, members)
            finally:
                os.close(fd)

    def test_root_guard_rejects_swap(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / 'root'
            target = root / 'product/lab/packages'
            target.mkdir(parents=True, mode=0o700)
            root.chmod(0o755)
            guard = RootGuard(root, 'product/lab/packages')
            try:
                guard.acquire()
                guard.attached()
                root.rename(base / 'displaced')
                root.mkdir(mode=0o755)
                with self.assertRaisesRegex(ValueError, 'detached'):
                    guard.attached()
            finally:
                guard.close()

    def test_root_guard_rejects_package_parent_swap(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / 'root'
            target = root / 'product/lab/packages'
            target.mkdir(parents=True, mode=0o700)
            root.chmod(0o755)
            guard = RootGuard(root, 'product/lab/packages')
            try:
                guard.acquire()
                target.rename(root / 'product/lab/displaced')
                target.mkdir(mode=0o700)
                with self.assertRaisesRegex(ValueError, 'detached'):
                    guard.attached()
            finally:
                guard.close()

    def test_held_evidence_rejects_same_uid_subdir_swap(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            base.chmod(0o700)
            claim = HeldAttempt(base / 'attempt')
            try:
                claim.claim()
                claim.mkdir('evidence', 0o700)
                first = docker_protocol.durable_json(claim.path / 'evidence/a.json',
                                                     {'phase': 'A'}, claim=claim)
                docker_protocol.verify_evidence_anchor(first)
                (claim.path / 'evidence').rename(claim.path / 'old-evidence')
                foreign = claim.path / 'evidence'
                foreign.mkdir(mode=0o700)
                with self.assertRaises(docker_protocol.EvidenceAttachmentUnknown):
                    docker_protocol.durable_json(foreign / 'b.json',
                                                 {'phase': 'B'}, claim=claim)
                self.assertEqual(list(foreign.iterdir()), [])
                self.assertTrue((claim.path / 'old-evidence/a.json').exists())
            finally:
                claim.close()


if __name__ == '__main__':
    unittest.main()
