import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t11_one_native", HERE / "run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class SelectedNativeFixtureTests(unittest.TestCase):
    def test_runtime_closed_recut(self):
        manifest = runner.selected_runtime()
        self.assertEqual(len(manifest["files"]), 45)
        self.assertEqual({row["path"] for row in manifest["files"] if row["changed"]},
                         {"lab_runtime/store.py", "lab_runtime/operations.py", "profile.json"})

    def test_exact_selected_member_and_body(self):
        route, raw, body = runner.selected_body()
        self.assertEqual(route["member_ref"], runner.MEMBER)
        self.assertEqual(runner.sha(raw), runner.BODY_SHA)
        self.assertEqual(body["scope_ref"], runner.SCOPE)

    def test_wrong_runtime_manifest_pin_refuses(self):
        with patch.object(runner, "MANIFEST_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "selected bytes changed"):
                runner.selected_runtime()

    def test_changed_matrix_target_refuses(self):
        real = runner.read_pinned

        def changed(path, digest):
            raw = real(path, digest)
            if path == runner.ROOT / runner.MATRIX_PATH:
                body = json.loads(raw)
                target = next(row for row in body["routes"] if row["member_ref"] == runner.MEMBER)
                target["body_binding"]["sha256"] = "0" * 64
                return json.dumps(body).encode()
            return raw

        with patch.object(runner, "read_pinned", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "candidate route differs"):
                runner.selected_body()

    def test_historical_mirror_contains_selected_runtime_and_imports(self):
        with tempfile.TemporaryDirectory(prefix="cal-T11-static-mirror-") as temp:
            root = Path(temp) / "source"
            count = runner.historical_snapshot(root)
            self.assertGreater(count, 4000)
            manifest = runner.selected_runtime()
            for row in manifest["files"]:
                target = root / manifest["copied_root"] / row["path"]
                self.assertEqual(runner.sha(target.read_bytes()), row["sha256"])
            script = ("import json,sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);"
                      "import lab_runtime.store,lab_runtime.operations,lab_runtime.custody,lab_runtime.sources;"
                      "root=Path(sys.argv[1]).resolve();"
                      "print(json.dumps({k:v.__file__ for k,v in list(sys.modules.items()) "
                      "if k.startswith('lab_runtime') and hasattr(v,'__file__')}))")
            child = subprocess.run([sys.executable, "-I", "-B", "-c", script,
                                    str(runner.RUNTIME)], capture_output=True, text=True,
                                   timeout=30, check=True)
            origins = json.loads(child.stdout)
            self.assertGreater(len(origins), 5)
            self.assertTrue(all(Path(path).resolve().is_relative_to(runner.RUNTIME.resolve())
                                for path in origins.values()))

    def test_expected_native_negative_reasons_are_selected(self):
        operations = (runner.RUNTIME / "lab_runtime/operations.py").read_text()
        custody = (runner.RUNTIME / "lab_runtime/custody.py").read_text()
        for phrase in ("proposal outside provisioned scope", "stale expected HEAD",
                       "T11 exact member, scope or original bytes differ"):
            self.assertIn(phrase, operations)
        self.assertIn("original content size or byte digest differs", custody)


if __name__ == "__main__":
    unittest.main()
