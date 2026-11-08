import io
import unittest
import zipfile

import bundle


def rewrite(blob, mutate):
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(blob)) as source, zipfile.ZipFile(output, "w") as target:
        for index, info in enumerate(source.infolist()):
            replacement = mutate(index, info.filename, source.read(info.filename))
            if replacement is None:
                continue
            name, raw = replacement
            target.writestr(*bundle.zip_entry(name, raw))
    return output.getvalue()


class BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = bundle.build()

    def test_clean_replay_and_byte_identical_build(self):
        result = bundle.replay(self.blob)
        self.assertEqual(result["original_members"], 363)
        self.assertEqual(result["replayed_public_files"], 681)
        self.assertFalse(result["final_package"])
        self.assertEqual(self.blob, bundle.build())

    def test_changed_selected_body_refuses(self):
        altered = rewrite(self.blob, lambda i, n, raw: (n, raw + b"x") if i == 3 else (n, raw))
        with self.assertRaisesRegex(ValueError, "original file bytes changed"):
            bundle.replay(altered)

    def test_escaped_member_refuses(self):
        altered = rewrite(self.blob, lambda i, n, raw: ("files/../escape", raw) if i == 3 else (n, raw))
        with self.assertRaisesRegex(ValueError, "noncanonical bundle path"):
            bundle.replay(altered)

    def test_missing_member_refuses(self):
        altered = rewrite(self.blob, lambda i, n, raw: None if i == 3 else (n, raw))
        with self.assertRaisesRegex(ValueError, "bundle member count"):
            bundle.replay(altered)

    def test_changed_control_refuses(self):
        altered = rewrite(self.blob, lambda i, n, raw: (n, raw + b"x") if i == 0 else (n, raw))
        with self.assertRaisesRegex(ValueError, "original controls changed"):
            bundle.replay(altered)

    def test_duplicate_manifest_key_refuses(self):
        def duplicate(i, name, raw):
            if i == 2:
                raw = raw.replace(b'"final_package":false', b'"final_package":true,"final_package":false', 1)
            return name, raw

        altered = rewrite(self.blob, duplicate)
        with self.assertRaisesRegex(ValueError, "duplicate bundle JSON key"):
            bundle.replay(altered)

    def test_unaccounted_zip_comment_refuses(self):
        output = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.blob)) as source, zipfile.ZipFile(output, "w") as target:
            for info in source.infolist():
                target.writestr(*bundle.zip_entry(info.filename, source.read(info)))
            target.comment = b"foreign archive comment"
        with self.assertRaisesRegex(ValueError, "noncanonical bundle bytes"):
            bundle.replay(output.getvalue())

    def test_trailing_residue_refuses(self):
        with self.assertRaisesRegex(ValueError, "noncanonical bundle bytes"):
            bundle.replay(self.blob + b"foreign")


if __name__ == "__main__":
    unittest.main()
