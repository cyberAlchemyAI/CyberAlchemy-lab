"""Actual signed-source snapshot checks; all mutations stay in owned RAM."""
import copy
from dataclasses import replace
from contextlib import ExitStack
import unittest
from unittest.mock import patch

from .protocol import source
from . import artifact_model as M
from .guarded_reads import model_read_batch, participation_snapshot


class GuardedReads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack = ExitStack()
        cls.view = cls.stack.enter_context(source.replay_source('custody-participation'))
        cls.parent = cls.view.custody_signed_sources
        cls.delivery = source.custody_delivery()

    @classmethod
    def tearDownClass(cls):
        cls.parent.guard()
        cls.stack.close()

    def tearDown(self):
        self.parent.guard()

    def test_all_original_facts_and_witnesses(self):
        with participation_snapshot(self.parent, self.delivery) as snapshot:
            self.assertIs(type(snapshot), self.delivery.EL.ExactSources)
            self.assertEqual(set(snapshot.records), set(self.parent.sources.records))
            for version, original in self.parent.sources.records.items():
                selected, body = snapshot.get(original.artifact)
                self.assertEqual(selected.original, original.original)
                self.assertEqual(selected.revision_witness, original.revision_witness)
                self.assertEqual(selected.artifact, original.artifact)
                self.assertEqual(body, self.delivery.EL.parse(original.original))

    def test_snapshot_header_mutation_rejected(self):
        with self.assertRaises(ValueError):
            with participation_snapshot(self.parent, self.delivery) as snapshot:
                next(iter(snapshot.records.values())).artifact['byte_sha256'] = '0' * 64
                snapshot.guard()

    def test_snapshot_original_byte_mutation_rejected(self):
        with self.assertRaises(ValueError):
            with participation_snapshot(self.parent, self.delivery) as snapshot:
                key = next(iter(snapshot.records))
                record = snapshot.records[key]
                snapshot.records[key] = replace(record, original=record.original + b' ')
                snapshot.guard()

    def test_snapshot_schema_mutation_rejected(self):
        with self.assertRaises(ValueError):
            with participation_snapshot(self.parent, self.delivery) as snapshot:
                key = next(iter(snapshot.schemas))
                spec = snapshot.schemas[key]
                snapshot.schemas[key] = replace(spec, original_schema=spec.original_schema + b' ')
                snapshot.guard()

    def test_snapshot_validator_mutation_rejected(self):
        with self.assertRaises(ValueError):
            with participation_snapshot(self.parent, self.delivery) as snapshot:
                next(iter(snapshot.validators.values())).schema['fake'] = True
                snapshot.guard()

    def test_snapshot_scope_mutation_rejected(self):
        with self.assertRaises(ValueError):
            with participation_snapshot(self.parent, self.delivery) as snapshot:
                snapshot.scope_ref = 'project:other'
                snapshot.guard()

    def test_snapshot_cut_mutation_rejected(self):
        with self.assertRaises(ValueError):
            with participation_snapshot(self.parent, self.delivery) as snapshot:
                snapshot.source_cut['commit_sha256'] = '0' * 64
                snapshot.guard()

    def test_snapshot_witness_mutation_rejected(self):
        with self.assertRaises(ValueError):
            with participation_snapshot(self.parent, self.delivery) as snapshot:
                record = next(r for r in snapshot.records.values() if r.revision_witness is not None)
                record.revision_witness.source_cut['commit_sha256'] = '0' * 64
                snapshot.guard()

    def test_original_guard_callback_preserved(self):
        callback = self.parent.sources.current_guard
        with participation_snapshot(self.parent, self.delivery) as snapshot:
            self.assertEqual(self.parent.sources.current_guard, callback)
            self.assertNotEqual(snapshot.current_guard, callback)
            snapshot.guard()
        self.assertEqual(self.parent.sources.current_guard, callback)

    def test_snapshot_closed_after_use(self):
        with participation_snapshot(self.parent, self.delivery) as snapshot:
            snapshot.guard()
        with self.assertRaises(ValueError):
            snapshot.guard()

    def test_parent_corruption_detected_before_snapshot_returns(self):
        original = self.view.data['config']['scope_ref']
        try:
            with self.assertRaises(ValueError):
                with participation_snapshot(self.parent, self.delivery) as snapshot:
                    self.view.data['config']['scope_ref'] = 'project:owned-corruption'
                    # A copied fact stays consistent; the full parent exit guard
                    # refuses to release the pure plan from a changed source.
                    row = next(iter(snapshot.records.values()))
                    snapshot.get(row.artifact)
        finally:
            self.view.data['config']['scope_ref'] = original

    def test_batch_keeps_exact_headers_and_original_bytes(self):
        subject = next(s for s in self.view.subjects.values() if s['identity'] == 'work:R03-original-reader')
        expected = self.delivery.reader.adapter.model.artifact_ref(self.view, subject)
        raw = self.delivery.reader.adapter.model.record_bytes(self.view, subject)
        with model_read_batch(self.view):
            self.assertEqual(M.artifact_ref(self.view, subject), expected)
            self.assertEqual(M.record_bytes(self.view, subject), raw)

    def test_batch_full_delivery_preflight_at_both_boundaries(self):
        subjects = [s for s in self.view.subjects.values() if s['category'] not in ('artifact-type', 'definition', 'relation-kind')][:10]
        with patch.object(source, 'custody_delivery', wraps=source.custody_delivery) as calls:
            with model_read_batch(self.view):
                for subject in subjects:
                    self.assertEqual(M.artifact_ref(self.view, subject), self.delivery.reader.adapter.model.artifact_ref(self.view, subject))
            self.assertEqual(calls.call_count, 2)

    def test_outside_batch_full_preflight_is_retained(self):
        subject = next(s for s in self.view.subjects.values() if s['identity'] == 'work:R03-original-reader')
        with patch.object(source, 'custody_delivery', wraps=source.custody_delivery) as calls:
            M.artifact_ref(self.view, subject)
            self.assertEqual(calls.call_count, 1)

    def test_batch_changed_view_rejected_at_exit(self):
        original = self.view.data['config']['scope_ref']
        try:
            with self.assertRaises(ValueError):
                with model_read_batch(self.view):
                    self.view.data['config']['scope_ref'] = 'project:owned-corruption'
        finally:
            self.view.data['config']['scope_ref'] = original

    def test_batch_nested_same_view_retains_outer_guards(self):
        with patch.object(source, 'custody_delivery', wraps=source.custody_delivery) as calls:
            with model_read_batch(self.view):
                with model_read_batch(self.view):
                    self.assertEqual(M.references(self.view), M.references(self.view))
            self.assertEqual(calls.call_count, 2)

    def test_batch_nested_different_view_rejected(self):
        with self.assertRaises(ValueError):
            with model_read_batch(self.view):
                with model_read_batch(copy.copy(self.view)):
                    self.fail('foreign view must not enter the batch')
