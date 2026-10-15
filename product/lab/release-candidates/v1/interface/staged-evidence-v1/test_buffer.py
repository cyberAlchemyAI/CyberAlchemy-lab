"""Pure staging cases; synthetic callbacks supply no authenticated host proof."""
import hashlib
import json
import unittest
from .buffer import EvidenceBuffer, MAX_OBJECT_BYTES, MAX_OBJECTS, MAX_TOTAL_BYTES


class BufferTests(unittest.TestCase):
    def setUp(self):
        self.checked = []
        self.written = []
        self.events = []
        self.buffer = EvidenceBuffer('fixture:owned-workspace', self.validate)

    def validate(self, raw):
        self.checked.append(raw)
        body = json.loads(raw)
        if 'private_key' in body:
            raise ValueError('fixture privacy refusal')

    def outside(self):
        self.events.append('outside')

    def write(self, raw):
        self.events.append('write')
        self.written.append(raw)
        digest = hashlib.sha256(raw).hexdigest()
        return {'ref': 'workspace-object:fixture:owned-workspace:' + digest,
                'sha256': digest}

    def test_01_staging_creates_no_durable_write(self):
        self.buffer.object(b'{"check":"one"}')
        self.assertEqual(self.written, [])

    def test_02_exact_original_bytes_bound(self):
        raw = b'{ "check" : "one" }\n'
        binding = self.buffer.object(raw)
        self.assertEqual(binding['sha256'], hashlib.sha256(raw).hexdigest())
        self.buffer.commit(self.write, self.outside)
        self.assertEqual(self.written, [raw])

    def test_03_duplicate_bytes_are_deduplicated(self):
        self.assertEqual(self.buffer.object(b'{}'), self.buffer.object(b'{}'))
        self.buffer.commit(self.write, self.outside)
        self.assertEqual(self.written, [b'{}'])

    def test_04_written_order_retained(self):
        for raw in [b'{"n":2}', b'{"n":1}', b'{"n":2}']:
            self.buffer.object(raw)
        self.buffer.commit(self.write, self.outside)
        self.assertEqual(self.written, [b'{"n":2}', b'{"n":1}'])

    def test_05_every_write_has_current_boundary_check(self):
        self.buffer.object(b'{}'); self.buffer.object(b'{"n":1}')
        self.buffer.commit(self.write, self.outside)
        self.assertEqual(self.events, ['outside', 'outside', 'write', 'outside', 'write'])

    def test_06_exit_refusal_prevents_all_writes(self):
        self.buffer.object(b'{}')
        def refused():
            raise ValueError('actual boundary refused')
        with self.assertRaisesRegex(ValueError, 'boundary refused'):
            self.buffer.commit(self.write, refused)
        self.assertEqual(self.written, [])
        self.assertTrue(self.buffer.closed)

    def test_07_discard_prevents_publication(self):
        self.buffer.object(b'{}'); self.buffer.discard()
        with self.assertRaisesRegex(ValueError, 'closed'):
            self.buffer.commit(self.write, self.outside)
        self.assertEqual(self.written, [])

    def test_08_discard_clears_temporary_output(self):
        self.buffer.object(b'{}'); self.buffer.discard()
        self.assertEqual(self.buffer._objects, {})
        self.assertEqual(self.buffer._total, 0)

    def test_09_closed_buffer_cannot_stage(self):
        self.buffer.discard()
        with self.assertRaisesRegex(ValueError, 'closed'):
            self.buffer.object(b'{}')

    def test_10_commit_is_not_repeatable(self):
        self.buffer.object(b'{}'); self.buffer.commit(self.write, self.outside)
        with self.assertRaisesRegex(ValueError, 'closed'):
            self.buffer.commit(self.write, self.outside)
        self.assertEqual(len(self.written), 1)

    def test_11_nonbyte_inputs_refused(self):
        for raw in ['{}', bytearray(b'{}'), {}, None]:
            with self.assertRaisesRegex(ValueError, 'bounded evidence bytes'):
                self.buffer.object(raw)

    def test_12_original_per_object_ceiling_preserved(self):
        with self.assertRaisesRegex(ValueError, 'bounded evidence bytes'):
            self.buffer.object(b' ' * (MAX_OBJECT_BYTES + 1))

    def test_13_object_count_ceiling(self):
        for n in range(MAX_OBJECTS):
            self.buffer.object(json.dumps({'n': n}).encode())
        with self.assertRaisesRegex(ValueError, 'aggregate'):
            self.buffer.object(b'{"new":"over-bound"}')

    def test_14_aggregate_byte_ceiling(self):
        local = EvidenceBuffer('fixture:owned-workspace', lambda raw: None)
        for n in range(MAX_TOTAL_BYTES // MAX_OBJECT_BYTES):
            local.object(bytes([n]) * MAX_OBJECT_BYTES)
        with self.assertRaisesRegex(ValueError, 'aggregate'):
            local.object(b'over-bound')
        local.discard()

    def test_15_privacy_refusal_does_not_stage(self):
        with self.assertRaisesRegex(ValueError, 'privacy refusal'):
            self.buffer.object(b'{"private_key":"fixture-never-a-key"}')
        self.assertEqual(self.buffer._objects, {})

    def test_16_original_json_bytes_not_reencoded(self):
        self.assertNotEqual(self.buffer.object(b'{}'), self.buffer.object(b'{ }'))

    def test_17_privacy_rechecked_before_publication(self):
        self.buffer.object(b'{}'); self.buffer.commit(self.write, self.outside)
        self.assertEqual(self.checked, [b'{}', b'{}'])

    def test_18_changed_staged_bytes_refused(self):
        binding = self.buffer.object(b'{}')
        self.buffer._objects[binding['sha256']] = b'{"changed":true}'
        with self.assertRaisesRegex(ValueError, 'bytes changed'):
            self.buffer.commit(self.write, self.outside)
        self.assertEqual(self.written, [])

    def test_19_actual_writer_binding_must_match(self):
        self.buffer.object(b'{}')
        with self.assertRaisesRegex(ValueError, 'writer binding differs'):
            self.buffer.commit(lambda raw: {'ref': 'foreign', 'sha256': '0' * 64}, self.outside)
        self.assertTrue(self.buffer.closed)

    def test_20_writer_failure_clears_buffer_and_is_not_retried(self):
        self.buffer.object(b'{}')
        def refused(raw):
            self.written.append(raw)
            raise OSError('synthetic durable writer failed')
        with self.assertRaises(OSError):
            self.buffer.commit(refused, self.outside)
        self.assertTrue(self.buffer.closed)
        self.assertEqual(self.written, [b'{}'])

    def test_21_constructor_requires_exact_workspace_and_validator(self):
        for workspace, validator in [('', self.validate), (None, self.validate),
                                     ('fixture:workspace', None)]:
            with self.assertRaises(ValueError):
                EvidenceBuffer(workspace, validator)

    def test_22_empty_commit_still_checks_boundary(self):
        self.buffer.commit(self.write, self.outside)
        self.assertEqual(self.events, ['outside'])
        self.assertTrue(self.buffer.closed)
