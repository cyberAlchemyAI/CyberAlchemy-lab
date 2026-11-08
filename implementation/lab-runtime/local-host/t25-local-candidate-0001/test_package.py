import io
import json
from pathlib import Path
import tempfile
import sys
import types
import unittest
from unittest.mock import patch
import zipfile

import package


def rewrite(blob, transform):
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(blob)) as source, zipfile.ZipFile(output, "w") as target:
        for index, info in enumerate(source.infolist()):
            row = transform(index, info.filename, source.read(info))
            if row is not None:
                target.writestr(*package.entry(*row))
    return output.getvalue()


class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = package.build()

    def test_clean_replay_and_deterministic_build(self):
        result = package.replay(self.blob)
        self.assertEqual((result["original_members"], result["original_public_files"],
                          result["replayed_additions"]), (363, 681, 799))
        self.assertFalse(result["task_complete"])
        self.assertEqual(self.blob, package.build())

    def test_extracted_clean_fixture_context_verifies(self):
        with tempfile.TemporaryDirectory(prefix="cal-t25-test-") as directory:
            target = Path(directory)
            result = package.extract_verified(self.blob, target)
            self.assertTrue(result["extracted_fixture_context_verified"])
            self.assertEqual(package.sha((target / "fixture/package-manifest.json").read_bytes()),
                             package.FIXTURE_SHA)
            self.assertTrue((target / "META/original-public-inputs.zip").is_file())

    def test_exact_inventory_exposes_original_and_addition_rows(self):
        document = package.inventory(self.blob)
        self.assertEqual(len(document["original_member_ids"]), 363)
        self.assertEqual(len(set(document["original_member_ids"])), 363)
        self.assertEqual(len(document["additions"]), 799)
        self.assertEqual(document["archive_sha256"], package.sha(self.blob))
        self.assertFalse(document["task_complete"])

    def test_missing_addition_refuses(self):
        altered = rewrite(self.blob, lambda i, name, raw: None if i == 2 else (name, raw))
        with self.assertRaisesRegex(ValueError, "candidate inventory changed"):
            package.replay(altered)

    def test_altered_addition_refuses(self):
        altered = rewrite(self.blob, lambda i, name, raw: (name, raw + b"x") if i == 2 else (name, raw))
        with self.assertRaisesRegex(ValueError, "candidate addition bytes changed"):
            package.replay(altered)

    def test_altered_original_refuses(self):
        altered = rewrite(self.blob, lambda i, name, raw: (name, raw + b"x") if i == 1 else (name, raw))
        with self.assertRaisesRegex(ValueError, "original bundle bytes changed"):
            package.replay(altered)

    def test_manifest_cannot_claim_completion(self):
        def change(index, name, raw):
            if index == 0:
                document = json.loads(raw)
                document["original_member_dispositions_complete"] = True
                raw = package.encoded(document)
            return name, raw
        altered = rewrite(self.blob, change)
        with self.assertRaisesRegex(ValueError, "candidate manifest changed"):
            package.replay(altered)

    def test_escaped_path_refuses(self):
        altered = rewrite(self.blob, lambda i, name, raw: ("fixture/../escape", raw) if i == 2 else (name, raw))
        with self.assertRaisesRegex(ValueError, "unsafe candidate path"):
            package.replay(altered)

    def test_zip_comment_refuses(self):
        output = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.blob)) as source, zipfile.ZipFile(output, "w") as target:
            for info in source.infolist():
                target.writestr(*package.entry(info.filename, source.read(info)))
            target.comment = b"foreign"
        with self.assertRaisesRegex(ValueError, "noncanonical candidate archive"):
            package.replay(output.getvalue())

    def test_original_code_pin_refuses_before_import(self):
        name = package.ORIGINAL.relative_to(package.ROOT).as_posix()
        with patch.dict(package.ORIGINAL_CODE_PINS, {name: "0" * 64}):
            with self.assertRaisesRegex(ValueError, "selected bytes changed"):
                package.original_module()

    def test_ambient_account_module_cannot_replace_selected_code(self):
        false_account = types.ModuleType("account")
        false_account.ROOT = "wrong checkout"
        previous = sys.modules.get("account")
        sys.modules["account"] = false_account
        try:
            loaded = package.original_module()
            self.assertIsNot(loaded.account, false_account)
            self.assertEqual(loaded.account.__file__, str(package.ORIGINAL_ACCOUNT))
            self.assertIs(sys.modules["account"], false_account)
        finally:
            if previous is None:
                sys.modules.pop("account", None)
            else:
                sys.modules["account"] = previous

    def test_equal_bytes_behind_linked_original_parent_refuse(self):
        with tempfile.TemporaryDirectory(dir=package.TASK) as directory:
            alias = Path(directory) / "linked-original"
            alias.symlink_to(package.ORIGINAL.parent, target_is_directory=True)
            linked = alias / "bundle.py"
            key = linked.relative_to(package.ROOT).as_posix()
            original_key = package.ORIGINAL.relative_to(package.ROOT).as_posix()
            original_pin = package.ORIGINAL_CODE_PINS[original_key]
            with patch.object(package, "ORIGINAL", linked), patch.dict(
                    package.ORIGINAL_CODE_PINS, {key: original_pin}, clear=True):
                with self.assertRaisesRegex(ValueError, "selected symlink"):
                    package.original_module()

    def test_source_swap_after_precheck_cannot_execute_changed_code(self):
        with tempfile.TemporaryDirectory(dir=package.TASK) as directory:
            root = Path(directory)
            bundle = root / "bundle.py"
            account = root / "account.py"
            marker = root / "unselected-code-ran"
            bundle.write_bytes(package.ORIGINAL.read_bytes())
            account.write_bytes(package.ORIGINAL_ACCOUNT.read_bytes())
            paths = {p.relative_to(package.ROOT).as_posix(): package.sha(p.read_bytes())
                     for p in (bundle, account)}
            original_read = package.read_exact
            reads = 0

            def swap_after_prechecks(name, digest):
                nonlocal reads
                raw = original_read(name, digest)
                reads += 1
                if reads == 2:
                    bundle.write_bytes(bundle.read_bytes() +
                                       ("\nfrom pathlib import Path\nPath(" + repr(str(marker)) +
                                        ").write_text('ran')\n").encode())
                return raw

            with patch.object(package, "ORIGINAL", bundle), patch.object(
                    package, "ORIGINAL_ACCOUNT", account), patch.dict(
                    package.ORIGINAL_CODE_PINS, paths, clear=True), patch.object(
                    package, "read_exact", side_effect=swap_after_prechecks):
                with self.assertRaisesRegex(ValueError, "selected bytes changed"):
                    package.original_module()
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
