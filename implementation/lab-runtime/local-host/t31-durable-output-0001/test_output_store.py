"""Output custody, crash/retry, and independent later-consumer boundaries."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from output_store import J, O, ROOT, OutputJournal, sha

FIXTURE = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/current-api30-output-fixture-20261023/test_output_journal.py'
if sha(FIXTURE.read_bytes()) != 'ca61ee8b23e1d9c14331d520bdb90bed7c948c42a5fc62770f44bbf48407b880':
    raise ValueError('selected existing fixture changed')
spec = importlib.util.spec_from_file_location('_t31_output_fixture', FIXTURE)
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)


def fixture():
    plan, before, header = F.candidate_plan()
    body = json.loads((ROOT / 'authority/artifact-types/challenge-event/v1/fixtures/valid/record.json').read_bytes())
    body['scope_ref'] = header['scope_ref']
    raw = J.K.encoded(body)
    if sha(raw) != header['byte_sha256']:
        raise ValueError('fixture output differs')
    return plan, before, header, raw


class DurableOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='t31-durable-')
        self.addCleanup(self.temp.cleanup)
        self.plan, before, self.header, self.raw = fixture()
        self.store = OutputJournal.initialize(Path(self.temp.name) / 'journal', before,
                                               self.header['scope_ref'],
                                               self.plan['next_run']['actor']['principal_ref'])
        self.originals = {self.header['version_ref']: self.raw}
        self.request = F.binding('fixture:durable-request', J.K.encoded({'route': self.plan['event']['transition_ref']}))
        self.guard = lambda: None  # Synthetic fixture authorization, never qualification.

    def apply(self, **kwargs):
        return self.store.apply(self.plan, originals=self.originals,
                                 request_binding=self.request, host_guard=self.guard, **kwargs)

    def test_real_journal_retry_and_separate_process_consumer(self):
        tx = self.apply()
        self.assertEqual(self.apply(), tx)
        self.assertEqual(self.store.replay()[0]['sequence'], 1)
        child = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('output_store.py')),
                                str(self.store.root), self.store.journal.config_sha256, '1'],
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                               capture_output=True, text=True, check=True)
        result = json.loads(child.stdout)
        self.assertEqual(result['outputs'][0]['sha256'], sha(self.raw))
        self.assertEqual(result['outputs'][0]['byte_size'], len(self.raw))
        self.assertEqual(self.store.consume(1), [(self.header, self.raw)])
        self.assertEqual(tx['canonical_admissions'], 0)

    def test_missing_or_changed_bytes_refuse_before_claim(self):
        for values in ({}, {self.header['version_ref']: self.raw + b' '}):
            with self.assertRaises(ValueError):
                self.store.apply(self.plan, originals=values,
                                 request_binding=self.request, host_guard=self.guard)
        self.assertEqual(self.store.replay()[0]['sequence'], 0)
        self.assertEqual(list((self.store.root / 'claims').iterdir()), [])

    def test_deleted_output_refuses_cold_open(self):
        self.apply()
        (self.store.root / 'outputs' / sha(self.raw)).unlink()
        with self.assertRaises((ValueError, OSError)):
            OutputJournal(self.store.root, self.store.journal.config_sha256)

    def test_changed_output_refuses_later_consumer(self):
        self.apply()
        (self.store.root / 'outputs' / sha(self.raw)).write_bytes(self.raw + b' ')
        with self.assertRaises(ValueError):
            self.store.consume(1)

    def test_linked_output_refuses(self):
        self.apply()
        target = Path(self.temp.name) / 'foreign'
        target.write_bytes(self.raw)
        target.chmod(0o600)
        path = self.store.root / 'outputs' / sha(self.raw)
        path.unlink()
        path.symlink_to(target)
        with self.assertRaises((ValueError, OSError)):
            self.store.consume(1)
        self.assertEqual(target.read_bytes(), self.raw)

    def test_recovery_requires_originals_before_head_advances(self):
        with self.assertRaises(J.Indeterminate):
            self.apply(crash_at='after-transaction')
        cold = OutputJournal(self.store.root, self.store.journal.config_sha256)
        fingerprint = J.digest({'request_binding': self.request, 'plan': self.plan})
        output = self.store.root / 'outputs' / sha(self.raw)
        output.write_bytes(self.raw + b' ')
        with self.assertRaises(ValueError):
            cold.recover(self.plan['event']['idempotency_key'], fingerprint, host_guard=self.guard)
        self.assertEqual(cold.journal.replay()[0]['sequence'], 0)
        output.write_bytes(self.raw)
        cold.recover(self.plan['event']['idempotency_key'], fingerprint, host_guard=self.guard)
        self.assertEqual(cold.replay()[0]['sequence'], 1)
        self.assertEqual(cold.consume(1), [(self.header, self.raw)])

    def test_after_claim_never_redispatches(self):
        with self.assertRaises(J.Indeterminate):
            self.apply(crash_at='after-claim')
        with self.assertRaises(J.Indeterminate):
            self.apply()
        self.assertEqual(self.store.replay()[0]['sequence'], 0)
        with self.assertRaises(ValueError):
            self.store.consume(1)

    def test_output_removed_after_claim_refuses_before_transaction(self):
        calls = []
        def guard():
            calls.append(1)
            if len(calls) == 4:
                (self.store.root / 'outputs' / sha(self.raw)).unlink()
        with self.assertRaises((ValueError, OSError)):
            self.store.apply(self.plan, originals=self.originals, request_binding=self.request,
                             host_guard=guard)
        self.assertEqual(self.store.journal.replay()[0]['sequence'], 0)
        self.assertEqual(list((self.store.root / 'transactions').iterdir()), [])

    def test_output_removed_during_recovery_refuses_before_head(self):
        with self.assertRaises(J.Indeterminate):
            self.apply(crash_at='after-transaction')
        calls = []
        def guard():
            calls.append(1)
            if len(calls) == 3:
                (self.store.root / 'outputs' / sha(self.raw)).unlink()
        fingerprint = J.digest({'request_binding': self.request, 'plan': self.plan})
        with self.assertRaises((ValueError, OSError)):
            self.store.recover(self.plan['event']['idempotency_key'], fingerprint, host_guard=guard)
        self.assertEqual(self.store.journal.replay()[0]['sequence'], 0)

    def test_private_mode_and_uncommitted_orphan_are_checked(self):
        self.store._stage(self.plan, self.originals)
        with self.assertRaises(ValueError):
            self.store.consume(1)
        self.apply()
        path = self.store.root / 'outputs' / sha(self.raw)
        path.chmod(0o644)
        with self.assertRaises(ValueError):
            self.store.consume(1)


if __name__ == '__main__':
    unittest.main()
