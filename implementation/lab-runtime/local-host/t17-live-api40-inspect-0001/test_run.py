"""Fast byte-origin controls for the disposable Paperclip/API40 journey."""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import run
import reader


class ByteBootstrapTests(unittest.TestCase):
    def test_python_reader_changed_code_has_no_side_effect(self):
        with tempfile.TemporaryDirectory(prefix='cal-T23-python-origin-') as name:
            marker = Path(name) / 'executed'
            selected = Path(name) / 'reader.py'
            selected.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('bad')\n")
            child = subprocess.run([sys.executable, '-I', '-B', '-c', run.READER_BOOTSTRAP,
                                    hashlib.sha256(b'pass\n').hexdigest(), str(selected)],
                                   capture_output=True, timeout=10)
            self.assertNotEqual(child.returncode, 0)
            self.assertFalse(marker.exists())

    def test_session_startup_lock_is_separate_from_effect_journal(self):
        with tempfile.TemporaryDirectory(prefix='cal-T23-workspace-lock-') as name:
            root = Path(name)
            (root / 'objects').mkdir(mode=0o700)
            journal = root / 'journal'
            journal.mkdir(mode=0o700)
            policy = {'workspace': {'root': str(root)}}
            self.assertEqual(reader.count_workspace(policy),
                             {'objects': 0, 'effect_journal': 0, 'session_custody_lock': 0})
            descriptor = os.open(journal / '.session-custody.lock',
                                 os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(descriptor)
            self.assertEqual(reader.count_workspace(policy),
                             {'objects': 0, 'effect_journal': 0, 'session_custody_lock': 1})
            (journal / 'unexpected.claim.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'effect or unexpected journal'):
                reader.count_workspace(policy)

    def test_node_invoker_changed_code_has_no_side_effect(self):
        with tempfile.TemporaryDirectory(prefix='cal-T23-node-origin-') as name:
            marker = Path(name) / 'executed'
            selected = Path(name) / 'adapter.mjs'
            selected.write_text("import{writeFileSync}from'node:fs';"
                                f"writeFileSync({str(marker)!r},'bad');")
            child = subprocess.run([str(run.NODE), '--input-type=module', '--eval',
                                    run.NODE_BOOTSTRAP,
                                    hashlib.sha256(b'void 0;').hexdigest(), str(selected)],
                                   capture_output=True, timeout=10)
            self.assertNotEqual(child.returncode, 0)
            self.assertFalse(marker.exists())


if __name__ == '__main__':
    unittest.main()
