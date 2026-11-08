"""Focused regression-equivalence and changed-source refusals."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t15_api39_equivalence", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class MethodEquivalence(unittest.TestCase):
    def test_selected_successor_has_exact_inherited_ast(self):
        result = verify.verify()
        self.assertEqual(result["method_count_each"], 345)
        self.assertEqual((result["missing"], result["added"], result["changed"]), ([], [], []))
        self.assertFalse(result["inherited_methods_executed"])

    def test_method_body_change_is_observable(self):
        base = verify.methods(b"class C:\n def test_a(self):\n  return 1\n", "test_x.py")
        changed = verify.methods(b"class C:\n def test_a(self):\n  return 2\n", "test_x.py")
        self.assertEqual(set(base), set(changed))
        self.assertNotEqual(base, changed)

    def test_duplicate_method_and_unsafe_origin_refuse(self):
        with self.assertRaisesRegex(ValueError, "duplicate test method"):
            verify.methods(b"class C:\n def test_a(self):\n  return 1\n def test_a(self):\n  return 2\n", "x.py")
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "real").mkdir()
            (root / "real" / "x.py").write_bytes(b"pass\n")
            (root / "alias").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "source parent changed"):
                verify.regular(root, "alias/x.py")


if __name__ == "__main__":
    unittest.main()
