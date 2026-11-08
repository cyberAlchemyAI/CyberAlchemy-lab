"""Exercise the selected release evidence reader before any Service effect."""
import ast
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

HERE = Path(__file__).resolve().parent
OLD = HERE/'installation_release-preimage.py'
NEW = HERE/'installation_release.py'


def need(value, message):
    if not value:
        raise ValueError(message)


def reader(path, root, calls):
    tree = ast.parse(path.read_text())
    owner = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'InstallationRelease')
    method = next(node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == 'read')
    space = {'ROOT': root, 'Path': Path, 'privacy': lambda raw: None,
             'source': SimpleNamespace(require=need, sha=lambda raw: hashlib.sha256(raw).hexdigest()),
             'C': SimpleNamespace(read=lambda p: calls.append(p) or p.read_bytes())}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), space)
    return lambda selected: space['read'](SimpleNamespace(completion=None, vault=None), selected)


class ReleaseEvidencePath(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='cal-release-path-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)/'.local/share/installed/repository'
        self.root.mkdir(parents=True)
        self.ref = 'product/lab/release-candidates/v1/release-scope.json'
        self.raw = b'{"scope":"candidate"}\n'
        path = self.root/self.ref
        path.parent.mkdir(parents=True)
        path.write_bytes(self.raw)
        self.binding = {'ref': self.ref, 'sha256': hashlib.sha256(self.raw).hexdigest()}

    def test_causal_installed_local_parent_and_valid_relative_evidence(self):
        old_reads = []
        with self.assertRaisesRegex(ValueError, 'unselected release evidence path'):
            reader(OLD, self.root, old_reads)(self.binding)
        self.assertEqual(old_reads, [])
        new_reads = []
        self.assertEqual(reader(NEW, self.root, new_reads)(self.binding), self.raw)
        self.assertEqual(new_reads, [self.root/self.ref])

    def test_relative_private_traversal_and_absolute_refs_still_refuse(self):
        for ref in ('.local/secret.json', '.env/private.json', '../outside.json', '/tmp/elsewhere.json'):
            reads = []
            with self.subTest(ref=ref), self.assertRaisesRegex(ValueError, 'unselected release evidence path'):
                reader(NEW, self.root, reads)({'ref': ref, 'sha256': '0'*64})
            self.assertEqual(reads, [])

    def test_wrong_digest_still_refuses(self):
        reads = []
        with self.assertRaisesRegex(ValueError, 'exact original evidence binding differs'):
            reader(NEW, self.root, reads)({'ref': self.ref, 'sha256': '0'*64})
        self.assertEqual(reads, [self.root/self.ref])


if __name__ == '__main__':
    unittest.main()
