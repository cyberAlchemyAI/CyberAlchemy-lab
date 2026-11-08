"""Synthetic bounded protocol checks only; no transport or native authority."""
import base64
import json
import unittest

from t35_external_v1.phase_scoped_v2 import mapper_package_ipc_model_0004 as ipc

PEER = (123, 456, 1000, 1000)
PINS = dict.fromkeys(('mapper', 'source', 'reader', 'adapter'), '1'*64)


def model():
    return ipc.ProtocolModel(attempt_id='synthetic-0001', selection_sha256='2'*64,
                             begin_pins=PINS, peer=PEER)


def packet(m, selected_verb, payload, **changes):
    value = ipc.envelope(m.attempt_id, m.selection_sha256, m.ordinal, selected_verb, payload)
    value.update(changes)
    return ipc.encode(value)


def send(m, verb, payload):
    return m.receive(packet(m, verb, payload), peer=PEER)


def complete(m, action):
    m.complete_synthetic(action['action_id'], success=True)


def begin(m):
    complete(m, send(m, 'BEGIN', PINS))


def upload(m, verb, target, raw):
    blob = m.ordinal
    send(m, 'BLOB_BEGIN', {'size_bytes': len(raw), 'sha256': ipc.sha(raw), 'purpose': verb, 'target': target})
    for offset in range(0, len(raw), ipc.CHUNK_MAX):
        send(m, 'BLOB_CHUNK', {'blob_id': blob, 'offset': offset,
                              'data': base64.b64encode(raw[offset:offset+ipc.CHUNK_MAX]).decode()})
    send(m, 'BLOB_END', {'blob_id': blob})
    return blob


class ProtocolTests(unittest.TestCase):
    def test_complete_ordered_trace_55_leaves_and_four_pending_native_actions(self):
        m = model()
        for verb, target in ipc.schedule():
            if verb == 'BEGIN':
                payload = PINS
            elif verb in ('SEAL', 'EMIT'):
                # Arbitrary synthetic bytes deliberately make no semantic event claim.
                raw = ('synthetic:'+str(target)).encode()
                b = upload(m, verb, target, raw)
                payload = {'blob_id': b}
                if verb == 'EMIT':
                    payload['leaf'] = target
            elif verb == 'COLD_READ':
                payload = {'index': target}
            else:
                payload = {'manifest_sha256': m.manifest_sha256}
            action = send(m, verb, payload)
            self.assertFalse(action['effect_performed'])
            self.assertFalse(action['durable_ack'])
            self.assertIsNotNone(m.pending)
            complete(m, action)
        self.assertEqual(len([x for x in m.trace if x['verb'] == 'EMIT']), 55)
        self.assertEqual([(x['verb'], x['target']) for x in m.trace if x['verb'] in ('SEAL', 'COLD_READ')],
                         [('SEAL', 'semantic'), ('SEAL', 'governance'), ('COLD_READ', 2), ('COLD_READ', 3)])
        self.assertEqual(len(m.trace), 61)
        self.assertLess(m.ordinal, ipc.PACKETS_MAX)
        with self.assertRaises(ipc.Refusal):
            send(m, 'FINISH', {'manifest_sha256': m.manifest_sha256})

    def test_canonical_controls_reject_duplicates_floats_surrogates_depth(self):
        bad = [b'{"a":1,"a":2}', b'{"a":1.0}', b'{"a":NaN}', b'{"a":1e309}',
               b'{"a":-1}', b'{"a":9223372036854775808}', b'{"a":"\\ud800"}',
               b'{ "a":1}', b'['*65+b'0'+b']'*65, b'\xff', b'x'*(ipc.FRAME_MAX+1)]
        for raw in bad:
            with self.subTest(raw=raw[:30]), self.assertRaises(ipc.Refusal):
                ipc.decode(raw)
        value = {'a': '\u0301\U0001f30d', 'b': 2**63-1, 'c': [None, True, False]}
        self.assertEqual(ipc.decode(ipc.encode(value)), value)

    def test_closed_frame_subject_verb_and_ordinal(self):
        for change in ({'extra': 1}, {'selection_sha256': '3'*64}, {'attempt_id': 'other'},
                       {'ordinal': True}, {'ordinal': 1}, {'verb': 'EXEC'}, {'schema_version': 'other'}):
            m = model()
            with self.subTest(change=change), self.assertRaises(ipc.Refusal):
                m.receive(packet(m, 'BEGIN', PINS, **change), peer=PEER)
            self.assertTrue(m.failed)

    def test_synthetic_transport_mismatch_and_truncation_poison(self):
        for options in ({'peer': (124,456,1000,1000)}, {'truncated': True}, {'ancillary_truncated': True},
                        {'credential_count': 0}, {'credential_count': 2}, {'rights_present': True},
                        {'unknown_ancillary': True}):
            m = model(); args = {'peer': PEER}; args.update(options)
            with self.subTest(options=options), self.assertRaises(ipc.Refusal):
                m.receive(packet(m, 'BEGIN', PINS), **args)
            self.assertTrue(m.failed)

    def test_pending_replay_and_disconnect_cannot_resume(self):
        m = model(); raw = packet(m, 'BEGIN', PINS); m.receive(raw, peer=PEER)
        with self.assertRaises(ipc.Refusal):
            m.receive(raw, peer=PEER)
        self.assertTrue(m.failed)
        m = model(); begin(m); m.disconnect()
        with self.assertRaises(ipc.Refusal):
            send(m, 'BEGIN', PINS)
        self.assertEqual(m.first_failure, 'DISCONNECTED')

    def test_wrong_or_failed_synthetic_completion_poison(self):
        for action_id, success in [('0'*64, True), (None, False)]:
            m = model(); action = send(m, 'BEGIN', PINS)
            with self.assertRaises(ipc.Refusal):
                m.complete_synthetic(action_id or action['action_id'], success=success)
            self.assertEqual(m.step, 0)
            self.assertTrue(m.failed)

    def test_multichunk_exact_offset_and_digest(self):
        m = model(); begin(m)
        raw = b'x'*(ipc.CHUNK_MAX+7)
        b = upload(m, 'SEAL', 'semantic', raw)
        action = send(m, 'SEAL', {'blob_id': b})
        self.assertEqual(action['blob_sha256'], ipc.sha(raw))
        self.assertEqual(action['size_bytes'], len(raw))
        complete(m, action)

    def test_blob_scope_length_encoding_contiguity_and_hash_refuse(self):
        mutations = ['scope', 'size', 'parallel', 'offset', 'encoding', 'overflow', 'hash', 'short', 'bool']
        for mutation in mutations:
            m = model(); begin(m)
            payload = {'size_bytes': 3, 'sha256': ipc.sha(b'abc'), 'purpose': 'SEAL', 'target': 'semantic'}
            if mutation == 'scope': payload['target'] = '../outside'
            if mutation == 'size': payload['size_bytes'] = ipc.BLOB_MAX+1
            blob = m.ordinal
            with self.subTest(mutation=mutation), self.assertRaises(ipc.Refusal):
                send(m, 'BLOB_BEGIN', payload)
                if mutation == 'parallel': send(m, 'BLOB_BEGIN', payload)
                data = b'abd' if mutation == 'hash' else (b'abcd' if mutation == 'overflow' else b'abc')
                if mutation != 'short':
                    send(m, 'BLOB_CHUNK', {'blob_id': True if mutation == 'bool' else blob,
                                          'offset': 1 if mutation == 'offset' else 0,
                                          'data': '!!!!' if mutation == 'encoding' else base64.b64encode(data).decode()})
                send(m, 'BLOB_END', {'blob_id': blob})
            self.assertTrue(m.failed)

    def test_out_of_order_native_emit_finish_and_wrong_begin_pins(self):
        for verb, payload in [('SEAL', {'blob_id': 0}), ('COLD_READ', {'index': 2}),
                              ('EMIT', {'blob_id': 0, 'leaf': 'request.json'}),
                              ('FINISH', {'manifest_sha256': '0'*64}),
                              ('BEGIN', dict(PINS, source='0'*64))]:
            m = model()
            with self.subTest(verb=verb), self.assertRaises(ipc.Refusal): send(m, verb, payload)

    def test_completed_blob_is_immediately_single_consumption(self):
        m = model(); begin(m)
        b = upload(m, 'SEAL', 'semantic', b'abc')
        complete(m, send(m, 'SEAL', {'blob_id': b}))
        with self.assertRaises(ipc.Refusal): send(m, 'SEAL', {'blob_id': b})

    def test_no_native_or_file_api(self):
        for name in ('serve', 'run_native_checked', 'open', 'socket', 'subprocess', 'write', 'publish'):
            self.assertFalse(hasattr(ipc, name))


if __name__ == '__main__':
    unittest.main()
