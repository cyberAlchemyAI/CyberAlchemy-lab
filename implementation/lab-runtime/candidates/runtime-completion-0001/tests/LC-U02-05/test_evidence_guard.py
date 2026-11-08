"""No-replace numbered evidence and exact historical byte checks."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
sys.path.insert(0, str(REPO / 'implementation/lab-runtime/candidates/runtime-completion-0001'))
from t35_external_v1 import evidence_guard


class EvidenceGuardTests(unittest.TestCase):
    def test_no_replace_and_exact_audit(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-evidence-') as temporary:
            root = Path(temporary)
            first = evidence_guard._publish_in(root, 'construction-0001.json', b'{"v":1}\n')
            self.assertEqual(evidence_guard._audit_in(root, first), None)
            with self.assertRaises(FileExistsError):
                evidence_guard._publish_in(root, 'construction-0001.json', b'{"v":2}\n')
            self.assertEqual((root / 'construction-0001.json').read_bytes(), b'{"v":1}\n')
            (root / 'construction-0001.json').write_bytes(b'{"v":2}\n')
            with self.assertRaises(ValueError):
                evidence_guard._audit_in(root, first)

    def test_path_alias_and_symlink_refused(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-evidence-') as temporary:
            root = Path(temporary)
            for name in ('../construction-0001.json', 'construction-0001.json/../x',
                         'construction-1.json', 'cases.json'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    evidence_guard._publish_in(root, name, b'x')
            leaf = root / 'test-normal-0001.txt'
            leaf.symlink_to(root / 'outside.txt')
            with self.assertRaises(FileExistsError):
                evidence_guard._publish_in(root, leaf.name, b'x')
            selected = evidence_guard._publish_in(root, 'construction-0002.json', b'good')
            alias = root / 'alias'
            os.link(root / 'construction-0002.json', alias)
            with self.assertRaises(ValueError):
                evidence_guard._audit_in(root, selected)
            alias.unlink()
            (root / 'construction-0002.json').unlink()
            (root / 'construction-0002.json').symlink_to(root / 'outside.txt')
            with self.assertRaises((ValueError, OSError)):
                evidence_guard._audit_in(root, selected)

    def test_final_directory_detachment_refused(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-evidence-') as temporary:
            root = Path(temporary) / 'selected'
            root.mkdir()
            real_fsync = os.fsync
            calls = 0
            def detach_on_directory_fsync(fd):
                nonlocal calls
                calls += 1
                if calls == 2:
                    root.rename(root.with_name('detached'))
                    root.mkdir()
                return real_fsync(fd)
            with patch.object(evidence_guard.os, 'fsync', side_effect=detach_on_directory_fsync):
                with self.assertRaises(ValueError):
                    evidence_guard._publish_in(root, 'construction-0001.json', b'x')
            self.assertFalse((root / 'construction-0001.json').exists())

    def test_public_publish_audit_round_trip_in_disposable_root(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-evidence-') as temporary:
            repo = Path(temporary)
            root = repo / 'unit-evidence'
            root.mkdir()
            with patch.object(evidence_guard, 'REPO', repo), \
                 patch.object(evidence_guard, 'EVIDENCE', root):
                row = evidence_guard.publish_numbered('construction-0001.json', b'{"v":1}\n')
                self.assertEqual(row['path'], 'unit-evidence/construction-0001.json')
                self.assertEqual(evidence_guard.audit_evidence([row]), 1)
                with self.assertRaises(FileExistsError):
                    evidence_guard.publish_numbered('construction-0001.json', b'{"v":2}\n')

    def test_exact_v6_and_v9_evidence_bindings(self):
        packet = REPO / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-05/construction-0009.json'
        raw = packet.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '2ba72cf058c6cf8624190db69ac58f6be2085e8af18f6a867140f2746f25ba8c')
        selected = json.loads(raw)
        rows = [selected['predecessor_construction_binding'],
                selected['predecessor_independent_review_binding'],
                selected['superseded_v8_review_binding'],
                *selected['evidence_correction']['v6_log_bindings'],
                *(result['output_binding'] for result in selected['test_results'].values())]
        self.assertEqual(evidence_guard.audit_evidence(rows), len(rows))
        alias = rows[0].copy()
        alias['path'] = str(REPO / alias['path'])
        with self.assertRaises(ValueError):
            evidence_guard.audit_evidence([rows[0], alias])


if __name__ == '__main__':
    unittest.main()
