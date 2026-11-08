"""Committed derived currentness without admission or borrowed runtime authority."""
import copy
import dataclasses
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

from currentness import OwnedCurrentness, Selection, S, ROOT

fixture_path = ROOT / 'implementation/lab-runtime/local-host/t31-durable-output-0001/test_output_store.py'
sys.path.insert(0, str(fixture_path.parent))
spec = importlib.util.spec_from_file_location('_t31_owned_test_fixture', fixture_path)
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)


class OwnedProducedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='t31-owned-current-')
        self.addCleanup(self.temp.cleanup)
        self.plan, before, self.header, self.raw = F.fixture()
        run = self.plan['next_run']
        self.store = S.OutputJournal.initialize(Path(self.temp.name) / 'journal', before,
                                                self.header['scope_ref'], run['actor']['principal_ref'])
        self.producer_paths = {}
        for index, row in enumerate(self.plan['producer_receipt_bindings']):
            path = Path(self.temp.name) / ('producer-' + str(index) + '.json')
            path.write_bytes(self.raw)
            path.chmod(0o600)
            self.producer_paths[row['ref']] = path
        self.selection = Selection.from_host(self.store, source_cut=run['source_cut'], actor=run['actor'],
            work=run['work'], run_ref=run['run_ref'], scope_ref=self.header['scope_ref'],
            producer_receipts=self.plan['producer_receipt_bindings'], producer_paths=self.producer_paths)
        self.request = F.F.binding('fixture:owned-request', S.J.K.encoded({'transition': self.plan['event']['transition_ref']}))

    def apply(self, crash_at=None):
        tx = self.store.apply(self.plan, originals={self.header['version_ref']: self.raw},
                              request_binding=self.request, host_guard=lambda: None, crash_at=crash_at)
        return tx, S.sha(S.read_owned(self.store.root / 'transactions/00000001.json'))

    def resolve(self, digest, selection=None, guard=lambda: None):
        return OwnedCurrentness(selection or self.selection, host_guard=guard).resolve(
            self.header, sequence=1, transaction_sha256=digest)

    def test_committed_fact_is_explicitly_owned_not_admitted(self):
        _, digest = self.apply()
        row = self.resolve(digest)
        self.assertEqual(row['posture'], 'owned-produced-current')
        self.assertEqual(row['artifact'], self.header)
        self.assertEqual(row['semantic_kind'], 'challenge-event')
        self.assertEqual(row['lineage_binding']['sha256'], digest)
        self.assertNotIn('admission', row)

    def test_source_actor_work_scope_run_or_producer_substitution_refuses(self):
        _, digest = self.apply()
        for field in ('source_cut', 'actor', 'work', 'scope_ref', 'run_ref', 'producer_receipts'):
            if field in ('scope_ref', 'run_ref'):
                changed = 'fixture:foreign'
            else:
                changed = S.J.K.encoded({'different': True})
            selected = dataclasses.replace(self.selection, **{field: changed})
            with self.assertRaises((ValueError, KeyError)):
                self.resolve(digest, selected)

    def test_unheaded_transaction_is_not_current(self):
        with self.assertRaises(S.J.Indeterminate):
            self.apply(crash_at='after-transaction')
        digest = S.sha(S.read_owned(self.store.root / 'transactions/00000001.json'))
        with self.assertRaisesRegex(ValueError, 'unheaded'):
            self.resolve(digest)

    def test_orphan_blob_is_not_current(self):
        self.store._stage(self.plan, {self.header['version_ref']: self.raw})
        with self.assertRaisesRegex(ValueError, 'unheaded'):
            self.resolve('0' * 64)

    def test_wrong_transaction_or_other_journal_refuses(self):
        _, digest = self.apply()
        with self.assertRaisesRegex(ValueError, 'transaction differs'):
            self.resolve('0' * 64)
        selected = dataclasses.replace(self.selection, config_sha256='0' * 64)
        with self.assertRaises(ValueError):
            self.resolve(digest, selected)

    def test_revoked_guard_or_post_guard_byte_change_refuses(self):
        _, digest = self.apply()
        def revoked():
            raise ValueError('fixture revoked host grant')
        with self.assertRaisesRegex(ValueError, 'revoked'):
            self.resolve(digest, guard=revoked)
        calls = []
        def mutate_after():
            calls.append(1)
            if len(calls) == 2:
                (self.store.root / 'outputs' / self.header['byte_sha256']).write_bytes(self.raw + b' ')
        with self.assertRaises(ValueError):
            self.resolve(digest, guard=mutate_after)

    def test_selection_is_not_mutated_by_original_caller_dicts(self):
        _, digest = self.apply()
        changed = copy.deepcopy(self.plan['next_run']['source_cut'])
        selected = Selection.from_host(self.store, source_cut=changed, actor=self.plan['next_run']['actor'],
            work=self.plan['next_run']['work'], run_ref=self.selection.run_ref,
            scope_ref=self.selection.scope_ref, producer_receipts=self.plan['producer_receipt_bindings'],
            producer_paths=self.producer_paths)
        changed['store_ref'] = 'fixture:changed-after-selection'
        self.assertEqual(self.resolve(digest, selected)['posture'], 'owned-produced-current')

    def test_missing_or_changed_original_producer_receipt_refuses(self):
        _, digest = self.apply()
        path = next(iter(self.producer_paths.values()))
        path.write_bytes(self.raw + b' ')
        with self.assertRaisesRegex(ValueError, 'producer receipt bytes'):
            self.resolve(digest)
        path.unlink()
        with self.assertRaises(OSError):
            self.resolve(digest)

    def test_later_committed_revision_retires_original_owned_fact(self):
        import template_fixture as T
        path = ROOT / 'docs/proposals/0007-lab-integrated-schema-package/workflows/challenge-handling.json'
        transitions = json.loads(path.read_bytes())['transitions']
        first = next(t for t in transitions if t['to_state'] == 'eligible')
        plan, before, originals = T.plan_for(path, first)
        header = plan['event']['output_artifact_refs'][0]
        store = S.OutputJournal.initialize(Path(self.temp.name) / 'revision-journal', before,
            header['scope_ref'], plan['next_run']['actor']['principal_ref'])
        selected = Selection.from_host(store, source_cut=plan['next_run']['source_cut'],
            actor=plan['next_run']['actor'], work=plan['next_run']['work'],
            run_ref=plan['next_run']['run_ref'], scope_ref=header['scope_ref'],
            producer_receipts=plan['producer_receipt_bindings'],
            producer_paths={r['ref']: next(iter(self.producer_paths.values()))
                            for r in plan['producer_receipt_bindings']})
        store.apply(plan, originals=originals, request_binding=self.request, host_guard=lambda: None)
        digest = S.sha(S.read_owned(store.root / 'transactions/00000001.json'))
        resolver = OwnedCurrentness(selected, host_guard=lambda: None)
        resolver.resolve(header, sequence=1, transaction_sha256=digest)
        successor = copy.deepcopy(header)
        successor['version_ref'] = header['identity_ref'] + '@candidate.2'
        second = next(t for t in transitions if t['to_state'] == 'responded')
        def continuation():
            message, facts = F.F.F.build()
            facts['run_raw'] = S.J.K.encoded(plan['next_run'])
            message['idempotency_key'] = 'fixture:owned-revision:second'
            return message, facts
        next_plan, next_before, next_originals = T.plan_for(path, second,
            build_witness=continuation, selected_outputs=[(successor, originals[header['version_ref']])])
        self.assertEqual(next_before, S.J.K.encoded(plan['next_run']))
        store.apply(next_plan, originals=next_originals, request_binding=self.request, host_guard=lambda: None)
        self.assertEqual(store.replay()[0]['sequence'], 2)
        with self.assertRaisesRegex(ValueError, 'later committed revision'):
            resolver.resolve(header, sequence=1, transaction_sha256=digest)


if __name__ == '__main__':
    unittest.main()
