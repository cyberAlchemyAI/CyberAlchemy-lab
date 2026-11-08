import copy
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


prepare = module("cal_prepare_installed_under_test", HERE / "prepare_installed_runtime.py")
role = module("cal_installed_context_role_under_test", HERE / "installed_context_role.py")


class CleanInstalledRuntimeTests(unittest.TestCase):
    def test_selected_clean_install_has_exact_payload(self):
        selected, _ = prepare.closure.load_selection(
            prepare.SELECTION, prepare.sha(prepare.SELECTION.read_bytes()))
        self.assertEqual(len(prepare.closure.installed_files(selected)), 1010)
        self.assertEqual(len(prepare.closure.verify_installed(role.INSTALL, selected)), 1010)
        receipt = json.loads((role.INSTALL / "installation.json").read_bytes())
        self.assertEqual(receipt["file_count"], 1010)
        self.assertEqual(receipt["identity"][2:], [os.getuid(), 0o700])

    def test_role_refuses_substituted_install_and_receipt(self):
        selection = HERE / "instances/legacy-local-947e6c2a5b3d10f8/source/context-native-role.json"
        selected = json.loads(selection.read_bytes())
        self.assertIs(role.validate(selected), selected)
        wrong = copy.deepcopy(selected)
        wrong["installation"]["path"] = "/tmp/some-other-install"
        with self.assertRaisesRegex(ValueError, "selected0004 owned identity"):
            role.validate(wrong)
        wrong = copy.deepcopy(selected)
        wrong["installation_receipt_binding"]["path"] = "/tmp/some-other-receipt"
        with self.assertRaisesRegex(ValueError, "clean successor installation receipt"):
            role.validate(wrong)

    def test_installer_refuses_repository_and_weak_parent(self):
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            with self.assertRaisesRegex(ValueError, "CLEAN_INSTALL_ORIGIN_REFUSED"):
                prepare.install(Path(directory) / "fresh")
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            parent.chmod(0o755)
            with self.assertRaisesRegex(ValueError, "CLEAN_INSTALL_PARENT_OWNER_MODE_REFUSED"):
                prepare.install(parent / "fresh")


if __name__ == "__main__":
    unittest.main()
