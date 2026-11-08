"""Inert Source/Reader selection and actual emitted Context seam probes."""
import ast
import copy
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import admission as A
import closure as C
import emit_adapter as E
import inert_protocol as P

WHEN = dt.datetime(2026, 10, 20, 11, 40, tzinfo=dt.timezone.utc)


def require(value, message):
    if not value:
        raise P.Refused(message)


def actual_emit(here, bridge):
    tree = ast.parse((A.HERE / 'adapted-build-inert.py').read_bytes())
    node = E.function(tree, 'emit')
    namespace = {'HERE': here, 'require': require, 'encoded': P.encoded,
                 '_ctx_emit': bridge}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<actual-emitted-emit>', 'exec'), namespace)
    return namespace['emit'], tree


def fixture(fault=None):
    here = Path('/tmp/cal-context-integration-0002-inert/context')
    out = here / 'packages/0001'
    emitted = {}

    def binding(path, raw=None):
        if raw is not None:
            emitted[str(path)] = raw
        return {'path': str(path), 'sha256': P.sha(emitted[str(path)])}

    source = {'path': 'selected-source/source-manifest.json',
              'sha256': A.selection()['source']['source_manifest_sha256']}
    transcript = P.InertTranscript(out, binding, source, fault=fault)

    def bridge(path, raw):
        transcript.emit(path, raw)
        emitted[str(path)] = raw

    emit, tree = actual_emit(here, bridge)
    for number, leaf in enumerate(P.LEAVES[:39]):
        if number == 0:
            emit(out / leaf, None, raw=b'raw-choice-probe')
        elif number == 1:
            emit(out / leaf, {'encoded_choice_probe': True})
        else:
            emit(out / leaf, None, raw=(f'inert-{number}').encode())
    manifest = {
        'schema_version': 'lab-actual-context-delivery-package/v1-candidate',
        'files': sorted(transcript.rows, key=lambda row: row['path']),
        'source_manifest_binding': source, 'authority_effect': 'none',
        'actual_owner_outcome': None,
        'delivery_binding': transcript.rows[P.LEAVES.index('delivery.json')],
        'provenance_binding': transcript.rows[P.LEAVES.index('delivery-provenance.json')],
        'claim_ceiling': P.CLAIM,
    }
    return out, manifest, emit, tree, transcript, emitted, binding


def run_actual_tail(out, manifest, emit, tree, binding):
    build = E.function(tree, 'build')
    tail = ast.Module(body=build.body[-2:], type_ignores=[])
    printed = []
    namespace = {'out': out, 'manifest': manifest, 'emit': emit, 'binding': binding,
                 'print': lambda *args, **kwargs: printed.append(args[0]), 'json': json}
    exec(compile(tail, '<actual-emitted-build-tail>', 'exec'), namespace)
    return printed


class IntegrationTests(unittest.TestCase):
    def test_selector_hash_precedes_all_selected_path_opens(self):
        original = (A.HERE / 'selection.json').read_bytes()
        for edit in (
            lambda s: s['reader'].__setitem__('entrypoint', 'UnreviewedReader.open_signed'),
            lambda s: s['reader'].__setitem__('reader_code_path', '/tmp/branch.snapshot'),
        ):
            with self.subTest(edit=edit.__code__.co_consts), tempfile.TemporaryDirectory() as temp:
                chosen = json.loads(original)
                edit(chosen)
                (Path(temp) / 'selection.json').write_text(json.dumps(chosen))
                opened = []
                real = A.read_exact
                def observed(path, pin):
                    opened.append(str(path))
                    return real(path, pin)
                with mock.patch.object(A, 'HERE', Path(temp)), mock.patch.object(A, 'read_exact', observed):
                    with self.assertRaisesRegex(A.Refused, 'bytes changed'):
                        A.verify(WHEN)
                self.assertEqual(opened, [str(Path(temp) / 'selection.json')])

    def test_closed_selector_rejects_entrypoint_and_path_before_selected_open(self):
        selected = A.selection()
        for role, field, value in (
            ('reader', 'entrypoint', 'UnreviewedReader.open_signed'),
            ('reader', 'reader_code_path', '/tmp/branch.snapshot'),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(selected)
                changed[role][field] = value
                touched = []
                def fake_read(path, pin):
                    touched.append(str(path))
                    if path == A.HERE / 'selection.json':
                        return json.dumps(changed).encode()
                    raise AssertionError('selected target opened before selector rejection')
                # This isolates closed-schema validation after exact-byte
                # admission; the preceding test exercises the real hash pin.
                with mock.patch.object(A, 'read_exact', fake_read):
                    with self.assertRaises(A.Refused):
                        A.verify(WHEN)
                self.assertEqual(touched, [str(A.HERE / 'selection.json')])

    def test_metadata_read_growth_is_incrementally_capped(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'growing.json'
            path.write_bytes(b'')
            counts = []
            def growing_read(fd, count):
                counts.append(count)
                return b'x' * count
            with mock.patch.object(A.os, 'read', growing_read):
                with self.assertRaisesRegex(A.Refused, 'grew during bounded read'):
                    A.read_exact(path, A.sha(b''))
            self.assertEqual(counts, [1])
            self.assertEqual(sum(counts), 1)
            path.write_bytes(b'x' * A.LIMIT)
            counts.clear()
            with mock.patch.object(A.os, 'read', growing_read):
                with self.assertRaisesRegex(A.Refused, 'grew during bounded read'):
                    A.read_exact(path, A.sha(b'x' * A.LIMIT))
            self.assertEqual(counts, [1024 * 1024, 1024 * 1024, 1])
            self.assertEqual(sum(counts), A.LIMIT + 1)

    def test_controller_preflight_and_launch_refusal(self):
        command = [sys.executable, '-B', str(A.HERE / 'controller.py')]
        ready = subprocess.run(command + ['--preflight'], capture_output=True, text=True,
                               timeout=10, cwd=A.HERE)
        self.assertEqual(ready.returncode, 2, ready.stderr)
        value = json.loads(ready.stdout)
        self.assertEqual(value['status'], 'HOLD_MAPPER')
        self.assertEqual(value['effect'], 'NOT_RUN')
        self.assertEqual(value['context_launch'], 'REFUSED')
        blocked = subprocess.run(command + ['--launch'], capture_output=True, text=True,
                                 timeout=10, cwd=A.HERE)
        self.assertEqual(blocked.returncode, 2)
        self.assertEqual(json.loads(blocked.stdout)['status'], 'REFUSED')

    def test_frozen_partial_closure_map(self):
        frozen = json.loads((A.HERE / 'closure-map.json').read_bytes())
        replay = C.plan(dt.datetime.fromisoformat(frozen['observed_at']))
        self.assertEqual(replay, frozen)
        self.assertEqual(frozen['historical_row_states']['protected_archive_excluded'], 6)
        self.assertEqual(frozen['mapper_package'], 'UNSELECTED')
        self.assertEqual(frozen['context_source_manifest'], 'REFUSED')

    def test_reviewed_source_reader_metadata_join_without_archive(self):
        touched = []
        original = A.read_exact
        try:
            def observed(path, pin):
                touched.append(str(path))
                return original(path, pin)
            A.read_exact = observed
            result = A.verify(WHEN)
        finally:
            A.read_exact = original
        self.assertEqual(result['status'], 'SOURCE_READER_METADATA_JOIN_PASS')
        self.assertEqual(result['mapper_package'], 'UNSELECTED')
        self.assertEqual(result['context_launch'], 'REFUSED')
        self.assertFalse(any(path.endswith('/branch.snapshot') for path in touched))
        self.assertTrue(all(path.endswith(('.json', '.py', '.md')) for path in touched))

    def test_expired_and_fabricated_mapper_refused(self):
        with self.assertRaisesRegex(A.Refused, 'not current'):
            A.verify(dt.datetime(2026, 10, 22, tzinfo=dt.timezone.utc))
        chosen = A.selection()
        chosen['mapper_package'] = {'sha256': 'f' * 64}
        original = A.selection
        try:
            A.selection = lambda: chosen
            with self.assertRaisesRegex(A.Refused, 'selection differs'):
                A.verify(WHEN)
        finally:
            A.selection = original
        with self.assertRaisesRegex(A.Refused, 'Mapper package'):
            A.final_context_source_manifest()
        with self.assertRaisesRegex(A.Refused, 'effect-disabled'):
            A.launch_context()

    def test_exact_adapter_inverse_and_frozen_code(self):
        adapted, proof = E.adapt()
        self.assertEqual(adapted, (A.HERE / 'adapted-build-inert.py').read_bytes())
        self.assertEqual(proof, json.loads((A.HERE / 'emit-ast-proof.json').read_bytes()))
        self.assertTrue(proof['full_ast_inverse_equal'])
        self.assertEqual(proof['adapted_effect_refusals'], 4)

    def test_actual_emit_raw_encoded_and_original_summary_order(self):
        out, manifest, emit, tree, transcript, emitted, binding = fixture()
        self.assertEqual(emitted[str(out / P.LEAVES[0])], b'raw-choice-probe')
        self.assertEqual(emitted[str(out / P.LEAVES[1])], P.encoded({'encoded_choice_probe': True}))
        self.assertEqual(len(transcript.rows), 39)
        self.assertFalse(any(event[0] == 'FINISH_SENT' for event in transcript.trace))
        printed = run_actual_tail(out, manifest, emit, tree, binding)
        self.assertEqual(len(printed), 1)
        self.assertEqual([event[0] for event in transcript.trace[-5:]],
                         ['EMIT', 'MANIFEST_EMIT_ACK', 'FINISH_SENT', 'FINISH_ACK', 'CLIENT_CLOSED'])
        self.assertEqual(transcript.trace[-1][1], 'summary_permitted')
        self.assertEqual(sum(event[0] == 'FINISH_SENT' for event in transcript.trace), 1)
        self.assertTrue(transcript.poisoned)

    def test_faults_suppress_original_summary_and_retry(self):
        for fault in ('manifest_ack_loss', 'finish_send_loss', 'finish_ack_loss',
                      'writer_close_failure', 'client_close_failure'):
            with self.subTest(fault=fault):
                out, manifest, emit, tree, transcript, emitted, binding = fixture(fault)
                printed = []
                build = E.function(tree, 'build')
                tail = ast.Module(body=build.body[-2:], type_ignores=[])
                namespace = {'out': out, 'manifest': manifest, 'emit': emit, 'binding': binding,
                             'print': lambda *args, **kwargs: printed.append(args[0]), 'json': json}
                with self.assertRaises(P.Refused):
                    exec(compile(tail, '<actual-fault-tail>', 'exec'), namespace)
                self.assertEqual(printed, [])
                self.assertTrue(transcript.poisoned)
                with self.assertRaisesRegex(P.Refused, 'poisoned'):
                    emit(out / 'manifest.json', manifest)

    def test_manifest_and_boundary_refusals(self):
        out, manifest, emit, tree, transcript, emitted, binding = fixture()
        changed = copy.deepcopy(manifest)
        changed['files'] = changed['files'][:-1]
        with self.assertRaisesRegex(P.Refused, 'manifest/39-row'):
            emit(out / 'manifest.json', changed)
        self.assertTrue(transcript.poisoned)
        out, manifest, emit, tree, transcript, emitted, binding = fixture()
        with self.assertRaisesRegex(P.Refused, 'boundary escaped'):
            emit(out.parent.parent / 'unselected.json', None, raw=b'x')
        self.assertEqual(len(transcript.rows), 39)


if __name__ == '__main__':
    unittest.main(verbosity=2)
