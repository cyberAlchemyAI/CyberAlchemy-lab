import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cal_current_authority_adapter_under_test",
                                             HERE / "current_authority_adapter.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class CurrentAuthorityAdapter(unittest.TestCase):
    def test_current_t12_chain(self):
        snapshot = adapter.capture()
        self.assertEqual([row["target_count"] for row in snapshot["successors"]], [4, 12])
        self.assertEqual(snapshot["current_state"]["identity"],
                         "project-state:cyberalchemy-v2-to-lab-migration:specialist-owner-bootstrap-0003")

    def test_wrong_current_lookup_pin_refused(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_DIGEST_REFUSED"):
            adapter.capture(expected_lookup_sha256="0" * 64)

    def test_changed_successor_body_refused(self):
        source = adapter.ROOT
        with tempfile.TemporaryDirectory(prefix="cal-t12-source-copy-") as directory:
            repo = Path(directory)

            def copy(relative):
                target = repo / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source / relative, target)

            profile_name = adapter.BASE_PROFILE.relative_to(source).as_posix()
            copy(profile_name)
            copy(adapter.LOOKUP)
            profile = json.loads((source / profile_name).read_bytes())
            copy(profile["current_selection"]["bundle_path"])
            copy(profile["current_selection"]["state_path"])
            for name in ("lab-repository-owner-bootstrap-v1-0005",
                         "lab-specialist-owner-bootstrap-v1-0003"):
                bundle_name = "authority/admissions/" + name + "/bundle.json"
                copy(bundle_name)
                bundle = json.loads((source / bundle_name).read_bytes())
                for row in bundle["files"]:
                    copy("authority/admissions/" + name + "/" + row["path"])
            self.assertEqual(len(adapter.capture(repo)["successors"]), 2)
            changed = repo / "authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/definition-owner-role.json"
            changed.write_bytes(changed.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SOURCE_DIGEST_REFUSED"):
                adapter.capture(repo)


if __name__ == "__main__":
    unittest.main()
