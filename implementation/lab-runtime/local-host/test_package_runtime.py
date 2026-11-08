"""Causal tests for the selected public image package and cold byte checks."""

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module("cal_package_builder", HERE / "package_runtime.py")
checker = module("cal_package_checker", HERE / "verify_package.py")


class PackageRuntimeTests(unittest.TestCase):
    def make_package(self):
        temp = tempfile.TemporaryDirectory(prefix="cal-package-test-")
        self.addCleanup(temp.cleanup)
        context = Path(temp.name)
        manifest = builder.load_manifest(builder.MANIFEST)
        builder.stage(builder.REPO, context, manifest)
        return context, manifest

    def test_exact_selected_package_starts_without_checkout_mount(self):
        context, manifest = self.make_package()
        checker.verify(context / "workspace", context / "package-manifest.json")
        self.assertEqual((context / "workspace" / builder.CANONICAL_REGISTRY).read_bytes(),
                         (context / "workspace" / builder.PUBLIC_REGISTRY).read_bytes())
        self.assertEqual(len(manifest["materials"]), 698)
        self.assertEqual(len(manifest["namespace_only"]), 78)
        self.assertTrue(all((context / "workspace" / name).stat().st_size == 0
                            for name in manifest["namespace_only"]))

    def test_missing_selected_file_refuses_before_run(self):
        context, _ = self.make_package()
        (context / "workspace/implementation/lab-runtime/v1/profile.json").unlink()
        with self.assertRaisesRegex(checker.PackageRefused, "MISSING_PACKAGE_FILE"):
            checker.verify(context / "workspace", context / "package-manifest.json")

    def test_changed_selected_byte_refuses_before_run(self):
        context, _ = self.make_package()
        path = context / "workspace/implementation/lab-runtime/local-product/run.py"
        path.write_bytes(path.read_bytes() + b"\n# changed after packaging\n")
        with self.assertRaisesRegex(checker.PackageRefused, "CHANGED_PACKAGE_BYTE"):
            checker.verify(context / "workspace", context / "package-manifest.json")

    def test_changed_staged_dockerfile_refuses_before_build(self):
        context, _ = self.make_package()
        path = context / "Dockerfile"
        path.write_bytes(path.read_bytes() + b"\n# changed after staging\n")
        with self.assertRaisesRegex(checker.PackageRefused, "CHANGED_BUILD_INPUT:Dockerfile"):
            checker.verify(context / "workspace", context / "package-manifest.json")

    def test_changed_staged_lock_refuses_before_build(self):
        context, _ = self.make_package()
        path = context / "requirements.lock"
        path.write_bytes(path.read_bytes() + b"\n# changed after staging\n")
        with self.assertRaisesRegex(checker.PackageRefused, "CHANGED_BUILD_INPUT:requirements.lock"):
            checker.verify(context / "workspace", context / "package-manifest.json")

    def test_changed_host_build_pin_refuses_before_context_copy(self):
        manifest = copy.deepcopy(builder.load_manifest(builder.MANIFEST))
        manifest["build_inputs"]["Dockerfile"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="cal-build-pin-test-") as temp:
            context = Path(temp)
            with self.assertRaisesRegex(builder.PackageRefused, "BUILD_INPUT_CHANGED:Dockerfile"):
                builder.stage(builder.REPO, context, manifest)
            self.assertEqual(list(context.iterdir()), [])

    def test_release_pin_binds_selected_manifest(self):
        manifest = builder.load_manifest(builder.MANIFEST)
        builder.verify_release_pin(manifest)
        changed = copy.deepcopy(manifest)
        changed["build_inputs"]["Dockerfile"] = "0" * 64
        with self.assertRaisesRegex(builder.PackageRefused, "PACKAGE_RELEASE_CHANGED"):
            builder.verify_release_pin(changed)

    def test_extra_file_refuses_before_run(self):
        context, _ = self.make_package()
        (context / "workspace/protected.bin").write_bytes(b"synthetic sentinel")
        with self.assertRaisesRegex(checker.PackageRefused, "EXTRA_PACKAGE_FILE"):
            checker.verify(context / "workspace", context / "package-manifest.json")

    def test_changed_source_pin_refuses_before_context_copy(self):
        manifest = copy.deepcopy(builder.load_manifest(builder.MANIFEST))
        manifest["materials"]["implementation/lab-runtime/v1/profile.json"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="cal-package-pin-test-") as temp:
            context = Path(temp)
            with self.assertRaisesRegex(builder.PackageRefused, "CHANGED_BYTE"):
                builder.stage(builder.REPO, context, manifest)
            self.assertEqual(list(context.iterdir()), [])

    def test_epoch_inventory_change_refuses_before_context_copy(self):
        manifest = copy.deepcopy(builder.load_manifest(builder.MANIFEST))
        manifest["epoch_inventory"]["recorded_decisions"].append(
            "docs/decisions/not-selected/decision.json")
        with tempfile.TemporaryDirectory(prefix="cal-package-epoch-test-") as temp:
            context = Path(temp)
            with self.assertRaisesRegex(builder.PackageRefused, "EPOCH_INVENTORY_CHANGED"):
                builder.stage(builder.REPO, context, manifest)
            self.assertEqual(list(context.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
