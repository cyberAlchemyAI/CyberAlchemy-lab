"""Causal, effect-free probes for the provisional Context constructor."""
import copy
import hashlib
import importlib.util
import json
import os
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path, PurePosixPath

import constructor as C
import completion_model as M


class ConstructionTests(unittest.TestCase):
    def test_exact_render_and_inverse(self):
        rows = C.render()
        self.assertEqual(len(rows), 11)
        self.assertEqual(len({row['path'] for row in rows.values()}), 11)
        for name, row in rows.items():
            self.assertEqual(C.sha(row['render_bytes']), row['render_sha256'])
            self.assertEqual(row['preimage_sha256'], (C.CODE_PINS | C.ROLE_PINS)[name])
            self.assertTrue(PurePosixPath(row['path']).is_relative_to(C.FAMILY / 'context'))
        self.assertEqual(sum(sum(row.get('predecessor_occurrences', {}).values()) for row in rows.values()), 5)

    def test_preimage_mutation_refused(self):
        original = C.CODE_PINS['base.py']
        try:
            C.CODE_PINS['base.py'] = '0' * 64
            with self.assertRaisesRegex(C.Refused, 'input changed'):
                C.render()
        finally:
            C.CODE_PINS['base.py'] = original

    def test_helper_mutation_refused(self):
        original = C.HELPER_PINS['hardener.py']
        try:
            C.HELPER_PINS['hardener.py'] = '0' * 64
            with self.assertRaisesRegex(C.Refused, 'input changed'):
                C.render()
        finally:
            C.HELPER_PINS['hardener.py'] = original

    def test_helper_preverify_precedes_side_effect_and_cache_spoof(self):
        sources = {name: C.raw_at(C.ENGINE / 't35_external_v1' / name)
                   for name in C.HELPER_PINS}
        poison = sources.copy()
        poison['role_stage.py'] += b'\nraise RuntimeError("POISON_EXECUTED")\n'
        existing = {k for k in sys.modules if k.startswith('_ctx_verified_0003_')}
        with self.assertRaisesRegex(C.Refused, 'before execution'):
            C.load_verified_sources(poison)
        self.assertEqual(existing, {k for k in sys.modules if k.startswith('_ctx_verified_0003_')})
        key = 't35_external_v1.role_stage'
        old = sys.modules.get(key)
        fake = types.SimpleNamespace(__file__=str(C.ENGINE / 't35_external_v1/role_stage.py'),
                                     render_python=lambda *_a, **_k: b'fake')
        try:
            sys.modules[key] = fake
            selected, _ = C.engine()
            self.assertIsNot(selected, fake)
            self.assertEqual(len(C.render()), 11)
        finally:
            if old is None:
                del sys.modules[key]
            else:
                sys.modules[key] = old

    def test_held_source_preverify_and_cached_module_spoof(self):
        original = C.raw_at(C.HERE / 'held_inputs.py', C.HELD_SOURCE_SHA)
        with tempfile.TemporaryDirectory(prefix='cal-held-import-test-') as tmp:
            sentinel = Path(tmp) / 'poison-executed'
            poison = original + ('\nopen(' + repr(str(sentinel)) + ', "x").write("bad")\n').encode()
            with self.assertRaisesRegex(C.Refused, 'before execution'):
                C.load_verified_held_source(poison)
            self.assertFalse(sentinel.exists())
            fake = types.ModuleType('held_inputs')
            fake.__file__ = str(C.HERE / 'held_inputs.py')
            class FakeHeld:
                pass
            fake.HeldPredecessors = FakeHeld
            previous = sys.modules.get('held_inputs')
            try:
                sys.modules['held_inputs'] = fake
                spec = importlib.util.spec_from_file_location('constructor_cache_probe', C.HERE / 'constructor.py')
                fresh = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(fresh)
                self.assertIsNot(fresh.HeldPredecessors, FakeHeld)
                self.assertIsNot(fresh.HeldPredecessors, C.HeldPredecessors)
            finally:
                if previous is None:
                    del sys.modules['held_inputs']
                else:
                    sys.modules['held_inputs'] = previous

    def test_unobserved_mapper_refused(self):
        with self.assertRaisesRegex(C.Refused, 'held-FD'):
            C.project_held_predecessors(C.render(), {})
        with self.assertRaisesRegex(C.Refused, 'Mapper package'):
            C.final_source_manifest()

    def test_pin_projection_with_synthetic_held_fds_and_attachment(self):
        """Real FDs over disposable test bytes exercise custody, not Mapper semantics."""
        original_family, original_snapshot = C.FAMILY, C.SNAPSHOT
        with tempfile.TemporaryDirectory(prefix='cal-context-held-test-') as tmp:
            family = Path(tmp) / 'family' / C.INSTANCE
            C.FAMILY = PurePosixPath(str(family))
            C.SNAPSHOT = PurePosixPath(str(Path(tmp) / 'snapshot'))
            try:
                values = {k: ('synthetic-held-' + k).encode() for k in C.HELD_PIN_PATHS}
                bindings = {}
                for key, suffix in C.HELD_PIN_PATHS.items():
                    path = family / suffix
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(values[key])
                    bindings[key] = {'path': str(path), 'sha256': C.sha(values[key])}
                rows = C.render()
                with C.HeldPredecessors(str(family), bindings) as held:
                    changed_binding_view = held.bindings
                    changed_binding_view['source']['sha256'] = 'f' * 64
                    self.assertEqual(held.read(bindings['source']['path']), values['source'])
                    result = C.project_held_predecessors(rows, held)
                    self.assertEqual(set(result), {'base.py', 'build.py', 'generation.py'})
                    changed = copy.deepcopy(rows)
                    changed['control.py']['render_bytes'] += b'\n'
                    with self.assertRaisesRegex(C.Refused, 'full selected renderer'):
                        C.project_held_predecessors(changed, held)
                    target = Path(bindings['mapped_package']['path'])
                    target.unlink()
                    target.write_bytes(values['mapped_package'])
                    with self.assertRaisesRegex(C.HeldRefused, 'attachment changed'):
                        held.read(str(target))
                with self.assertRaisesRegex(C.HeldRefused, 'closed'):
                    held.read(bindings['source']['path'])
                bad = copy.deepcopy(bindings)
                bad['mapped_package']['path'] = str(family / 'reader/packages/0001/manifest.json')
                with self.assertRaisesRegex(C.HeldRefused, 'same-family'):
                    C.HeldPredecessors(str(family), bad)
                target.unlink()
                target.symlink_to(family / C.HELD_PIN_PATHS['source'])
                with self.assertRaises((C.HeldRefused, OSError)):
                    C.HeldPredecessors(str(family), bindings)
            finally:
                C.FAMILY, C.SNAPSHOT = original_family, original_snapshot

    def test_fifo_socket_and_device_link_refused_without_blocking(self):
        with tempfile.TemporaryDirectory(prefix='cx-') as tmp:
            family = Path(tmp) / 'family' / C.INSTANCE
            bindings = {}
            for key, suffix in C.HELD_PIN_PATHS.items():
                path = family / suffix
                path.parent.mkdir(parents=True, exist_ok=True)
                raw = ('synthetic-' + key).encode()
                path.write_bytes(raw)
                bindings[key] = {'path': str(path), 'sha256': C.sha(raw)}
            target = Path(bindings['source']['path'])
            target.unlink()
            os.mkfifo(target)
            script = ('import constructor as C,json,sys\n'
                      'try:C.HeldPredecessors(sys.argv[1],json.loads(sys.argv[2]))\n'
                      'except C.HeldRefused:print("REFUSED")\n'
                      'else:raise RuntimeError("NONREGULAR_ACCEPTED")\n')
            proc = subprocess.run([sys.executable, '-B', '-c', script, str(family),
                                   json.dumps(bindings)], capture_output=True, text=True,
                                  timeout=2)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), 'REFUSED')
            target.unlink()
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.bind(str(target))
                with self.assertRaisesRegex(C.HeldRefused, 'bounded regular'):
                    C.HeldPredecessors(str(family), bindings)
            target.unlink()
            target.symlink_to('/dev/null')
            with self.assertRaisesRegex(C.HeldRefused, 'bounded regular'):
                C.HeldPredecessors(str(family), bindings)

    def test_historical_closure_is_metadata_only(self):
        audit = C.historical_closure_candidates()
        self.assertEqual(len(audit['rows']), 1804)
        self.assertTrue(any(row['state'] == 'protected_archive_excluded' for row in audit['rows']))
        self.assertTrue(all(row['state'] != 'selected' for row in audit['rows']))

    def test_completion_contract_remains_inert(self):
        contract = C.completion_contract()
        self.assertEqual(contract['effect'], 'NOT_RUN')
        self.assertEqual(contract['sequence'][-2:], ['checked-client-close', 'original-summary'])
        self.assertEqual(contract['finish_calls'], 1)

    def test_completion_order_and_faults(self):
        hashes = [c * 64 for c in 'abcdef123']
        selected = M.Selection('synthetic-attempt', 'synthetic-peer', *hashes,
                               'synthetic-selected-schema')
        start = M.begin(selected)
        common = {'attempt': selected.attempt, 'peer': selected.peer}
        manifest = common | {'ordinal': 40, 'manifest_sha256': selected.manifest_sha256,
            'prior_39_durable': True, 'release_private_ack': True,
            'private_root_absent': True, 'build_result_durable': True,
            'manifest_durable': True, 'manifest_readback_fsync': True,
            'request_sha256': selected.manifest_request_sha256,
            'response_sha256': selected.manifest_response_sha256,
            'selected_leaf_sha256': selected.selected_leaf_sha256}
        self.assertEqual(M.next_state(start, 'FINISH_ACK', common).step, 'UNKNOWN')
        self.assertEqual(M.next_state(start, 'MANIFEST_EMIT_ACK', manifest | {'ordinal': 99}).step,
                         'UNKNOWN')
        self.assertEqual(M.next_state(start, 'MANIFEST_EMIT_ACK', manifest | {'request_sha256': 'z' * 64}).step,
                         'UNKNOWN')
        self.assertEqual(M.next_state(start, 'MANIFEST_EMIT_ACK', manifest | {'peer': 'switched'}).step,
                         'UNKNOWN')
        self.assertEqual(M.next_state(start, 'TIMEOUT', common).step, 'UNKNOWN')
        after_manifest = M.next_state(start, 'MANIFEST_EMIT_ACK', manifest)
        self.assertEqual(after_manifest.step, 'await_finish_send')
        self.assertEqual(M.next_state(after_manifest, 'MANIFEST_EMIT_ACK', manifest).step, 'UNKNOWN')
        finish_send = common | {'ordinal': 41, 'action_payload': {},
            'request_sha256': selected.finish_request_sha256,
            'send_count': 1, 'transport_send_observed': True}
        self.assertEqual(M.next_state(after_manifest, 'FINISH_ACK', common).step, 'UNKNOWN')
        self.assertEqual(M.next_state(after_manifest, 'FINISH_SENT', finish_send | {'send_count': True}).step,
                         'UNKNOWN')
        self.assertEqual(M.next_state(after_manifest, 'FINISH_SENT', finish_send | {'send_count': 2}).step,
                         'UNKNOWN')
        after_send = M.next_state(after_manifest, 'FINISH_SENT', finish_send)
        self.assertEqual(after_send.step, 'await_finish_ack')
        self.assertEqual(after_send.finish_send_count, 1)
        self.assertEqual(M.next_state(after_send, 'FINISH_SENT', finish_send).step, 'UNKNOWN')
        finish_ack = common | {'ordinal': 41,
            'schema_version': selected.finish_ack_schema, 'effect': 'none',
            'original_profile_valid': True, 'forty_leaves_valid': True,
            'thirty_nine_rows_valid': True, 'writer_readback': True,
            'writer_closed': True, 'private_root_absent': True,
            'completion_observed': True,
            'request_sha256': selected.finish_request_sha256,
            'response_sha256': selected.finish_response_sha256,
            'model_request_sha256': selected.model_request_sha256,
            'inventory_sha256': selected.inventory_sha256}
        self.assertEqual(M.next_state(after_send, 'FINISH_ACK', finish_ack | {'writer_closed': False}).step,
                         'UNKNOWN')
        self.assertEqual(M.next_state(after_send, 'FINISH_ACK', finish_ack | {'ordinal': True}).step,
                         'UNKNOWN')
        self.assertEqual(M.next_state(after_send, 'FINISH_ACK', finish_ack | {'response_sha256': 'z' * 64}).step,
                         'UNKNOWN')
        after_finish = M.next_state(after_send, 'FINISH_ACK', finish_ack)
        self.assertEqual(after_finish.step, 'await_client_close')
        close = common | {'checked': True, 'close_count': 1,
                          'close_receipt_sha256': selected.close_receipt_sha256}
        self.assertEqual(M.next_state(after_finish, 'CLIENT_CLOSED', close | {'checked': False}).step, 'UNKNOWN')
        self.assertEqual(M.next_state(after_finish, 'CLIENT_CLOSED', close | {'close_count': True}).step, 'UNKNOWN')
        done = M.next_state(after_finish, 'CLIENT_CLOSED', close)
        self.assertEqual(done.step, 'summary_permitted')
        self.assertEqual(M.next_state(done, 'FINISH_ACK', finish_ack).step, 'UNKNOWN')

    def test_frozen_outputs_match_selected_render(self):
        selected = json.loads((C.HERE / 'selection.json').read_bytes())
        rows = C.render()
        self.assertFalse(selected['source_pin_frozen'])
        self.assertEqual(selected['source_manifest_status'],
                         'REFUSED_PENDING_FRESH_MAPPER_AND_COMPLETE_CLOSURE')
        self.assertEqual(len(selected['role_rows']), 11)
        for name, row in rows.items():
            self.assertEqual((C.HERE / 'rendered' / name).read_bytes(), row['render_bytes'])
        audit = json.loads((C.HERE / 'historical-closure-candidates.json').read_bytes())
        self.assertEqual(audit, C.historical_closure_candidates())


if __name__ == '__main__':
    unittest.main(verbosity=2)
