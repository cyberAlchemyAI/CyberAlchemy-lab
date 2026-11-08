"""Focused parser, no-follow and effect-boundary checks for committed-cut recovery."""
import ast
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest


SOURCE = Path(__file__).with_name('reconcile_native.py')
TREE = ast.parse(SOURCE.read_bytes())
FUNCTIONS = ast.Module(body=[node for node in TREE.body
                             if isinstance(node, ast.FunctionDef) and node.name in
                             {'sha', 'bounded_json', 'read_owned'}], type_ignores=[])
NS = {'hashlib': hashlib, 'json': json, 'os': os, 'Path': Path, 'stat': stat}
exec(compile(FUNCTIONS, str(SOURCE), 'exec'), NS)


class NativeRecoveryBoundaryTests(unittest.TestCase):
    def test_large_exact_transaction_parses_without_api_input_budget(self):
        raw = b'{"payload":"' + b'x' * (1024 * 1024 + 1) + b'"}'
        self.assertEqual(len(NS['bounded_json'](raw)['payload']), 1024 * 1024 + 1)

    def test_duplicate_and_oversize_refuse(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            NS['bounded_json'](b'{"a":1,"a":2}')
        with self.assertRaisesRegex(ValueError, 'exceeds'):
            NS['bounded_json'](b'x' * (16 * 1024 * 1024 + 1))

    def test_owned_read_refuses_symlink(self):
        with tempfile.TemporaryDirectory(prefix='cal-native-recovery-read-') as name:
            root = Path(name)
            (root / 'file.json').write_bytes(b'{}')
            self.assertEqual(NS['read_owned'](root, 'file.json', 10), b'{}')
            (root / 'linked.json').symlink_to('file.json')
            with self.assertRaises(OSError):
                NS['read_owned'](root, 'linked.json', 10)

    def test_recovery_has_no_store_write_operation(self):
        called = {node.attr for node in ast.walk(TREE)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                  for node in [node.func]}
        self.assertNotIn('apply', called)
        self.assertNotIn('initialize', called)
        self.assertNotIn('recover', called)


if __name__ == '__main__':
    unittest.main(verbosity=2)
