import hashlib
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from closure import Refused, SCHEMA, verify
import closure


class TypedClosureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.private = self.base / "private"
        self.private.mkdir(mode=0o700)

    def public(self, name, raw, kind="semantic-artifact", depends=()):
        path = self.repo / name
        path.write_bytes(raw)
        return {"kind": kind, "ref": name, "path": name,
                "sha256": hashlib.sha256(raw).hexdigest(), "depends_on": list(depends)}

    def protected(self, name, raw):
        path = self.private / name
        path.write_bytes(raw)
        path.chmod(0o600)
        return {"kind": "protected-host", "ref": "host:" + name,
                "path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                "depends_on": []}

    def manifest(self, *rows):
        return {"schema": SCHEMA, "roots": ["root.json"], "bindings": list(rows)}

    def test_mixed_27mb_proof_is_verified_without_becoming_semantic_edge(self):
        leaf = self.public("leaf.json", b'{}')
        root = self.public("root.json", b'{"evidence":{"ref":"proof.bin"}}',
                           depends=["leaf.json"])
        proof = self.public("proof.bin", b"proof" * (27 * 1024 * 1024 // 5),
                            kind="provenance-evidence")
        host = self.protected("secret.bin", b"private evidence")
        result = verify(self.manifest(root, leaf, proof, host), self.repo)
        self.assertEqual((result["verified_bindings"], result["semantic_nodes"],
                          result["semantic_edges"], result["protected_bytes_exposed"]),
                         (4, 2, 1, 0))

    def test_substitution_cycle_and_proof_edge_refuse(self):
        root = self.public("root.json", b"root", depends=["leaf.json"])
        leaf = self.public("leaf.json", b"leaf", depends=["root.json"])
        with self.assertRaisesRegex(Refused, "SEMANTIC_CYCLE_REFUSED"):
            verify(self.manifest(root, leaf), self.repo)
        leaf["depends_on"] = []
        leaf["sha256"] = "0" * 64
        with self.assertRaisesRegex(Refused, "BYTES_SUBSTITUTED"):
            verify(self.manifest(root, leaf), self.repo)
        leaf["sha256"] = hashlib.sha256(b"leaf").hexdigest()
        proof = self.public("proof.txt", b"proof", kind="provenance-evidence",
                            depends=["leaf.json"])
        with self.assertRaisesRegex(Refused, "PROOF_EDGE_REFUSED"):
            verify(self.manifest(root, leaf, proof), self.repo)

    def test_protected_symlink_and_world_readable_refuse(self):
        root = self.public("root.json", b"root")
        host = self.protected("private.bin", b"secret")
        path = Path(host["path"])
        path.chmod(0o644)
        with self.assertRaisesRegex(Refused, "PROTECTED_CUSTODY_REFUSED"):
            verify(self.manifest(root, host), self.repo)
        path.chmod(0o600)
        link = self.private / "link.bin"
        link.symlink_to(path)
        host["path"] = str(link)
        with self.assertRaisesRegex(Refused, "SYMLINK_OR_PATH_REFUSED"):
            verify(self.manifest(root, host), self.repo)
        host["path"] = str(self.private / ".." / "repo" / "root.json")
        with self.assertRaisesRegex(Refused, "PATH_TRAVERSAL_REFUSED"):
            verify(self.manifest(root, host), self.repo)

    def test_fifo_refuses_without_waiting_for_a_writer(self):
        root = self.public("root.json", b"root")
        fifo = self.repo / "proof.fifo"
        os.mkfifo(fifo)
        proof = {"kind": "provenance-evidence", "ref": "fifo-proof",
                 "path": "proof.fifo", "sha256": "0" * 64, "depends_on": []}
        with self.assertRaisesRegex(Refused, "FILE_IDENTITY_REFUSED"):
            verify(self.manifest(root, proof), self.repo)

    def test_named_protected_path_replacement_during_read_refuses(self):
        root = self.public("root.json", b"root")
        host = self.protected("host.bin", b"selected bytes")
        path = Path(host["path"])
        selected_inode = path.stat().st_ino
        original_read = os.read
        changed = False

        def replace_then_read(fd, count):
            nonlocal changed
            if not changed and os.fstat(fd).st_ino == selected_inode:
                path.rename(self.private / "old.bin")
                path.write_bytes(b"substituted bytes")
                path.chmod(0o600)
                changed = True
            return original_read(fd, count)

        with mock.patch.object(closure.os, "read", side_effect=replace_then_read):
            with self.assertRaisesRegex(Refused, "FILE_CHANGED_DURING_READ"):
                verify(self.manifest(root, host), self.repo)
        self.assertTrue(changed)

    def test_protected_mode_change_during_read_refuses(self):
        root = self.public("root.json", b"root")
        host = self.protected("host.bin", b"selected bytes")
        path = Path(host["path"])
        selected_inode = path.stat().st_ino
        original_read = os.read
        changed = False

        def chmod_then_read(fd, count):
            nonlocal changed
            if not changed and os.fstat(fd).st_ino == selected_inode:
                path.chmod(0o644)
                changed = True
            return original_read(fd, count)

        with mock.patch.object(closure.os, "read", side_effect=chmod_then_read):
            with self.assertRaisesRegex(Refused, "FILE_CHANGED_DURING_READ"):
                verify(self.manifest(root, host), self.repo)
        self.assertTrue(changed)


if __name__ == "__main__":
    unittest.main()
