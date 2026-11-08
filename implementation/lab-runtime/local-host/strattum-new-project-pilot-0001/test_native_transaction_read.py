"""Prove exact native transaction custody and no-follow refusal offline."""
import ast
import base64
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest


SOURCE = Path(__file__).with_name('pilot.py')
SNAPSHOT = Path('/home/vlad_/.local/share/cyberalchemy-lab/t03-long-fixture-private-0001/legacy-local-fb234116c28181e8/branch.snapshot')
tree = ast.parse(SOURCE.read_bytes())
function = ast.Module(body=[node for node in tree.body
                            if isinstance(node, ast.FunctionDef) and
                            node.name == 'read_native_transaction'], type_ignores=[])
ns = {'os': os, 'stat': stat}
exec(compile(function, str(SOURCE), 'exec'), ns)


class NativeTransactionReadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cal-native-transaction-test-')
        self.root = Path(self.temp.name)
        self.transactions = self.root / 'native-store/transactions'
        self.transactions.mkdir(parents=True)
        snapshot = json.loads(SNAPSHOT.read_bytes())
        self.raw = base64.b64decode(snapshot['files']['transactions/0000000002.json']['base64_original_bytes'],
                                    validate=True)
        (self.transactions / '0000000002.json').write_bytes(self.raw)

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_original_bytes(self):
        self.assertEqual(ns['read_native_transaction'](self.root, 2), self.raw)

    def test_symlink_refused(self):
        (self.transactions / '0000000002.json').unlink()
        (self.transactions / '0000000002.json').symlink_to('/etc/passwd')
        with self.assertRaises(OSError):
            ns['read_native_transaction'](self.root, 2)

    def test_wrong_sequence_refused(self):
        with self.assertRaises(FileNotFoundError):
            ns['read_native_transaction'](self.root, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
