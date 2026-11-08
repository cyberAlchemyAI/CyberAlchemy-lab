"""Focused true-origin and closed-selection checks for the API36 T06 successor."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
SDK = ROOT / "product/lab/release-candidates/v1/interface/composite-operator-v1-current-api36-0001/revision-0001"
BRANCH = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api36-0001/revision-0001"
API = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v36-current-t06-0001"
sys.path.insert(0, str(SDK))
import composite as sdk


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def row(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path.read_bytes())}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CurrentSuccessorTests(unittest.TestCase):
    def test_api36_installed_environment_and_host_refusal(self):
        interface = API.parent
        sys.path.insert(0, str(interface))
        import importlib
        guard = importlib.import_module(API.name + ".guard")
        receipt = json.loads((API / "rebind-receipt.json").read_bytes())
        self.assertEqual(len(guard.verify(receipt["successor_manifest_sha256"])["files"]), 207)
        install = ROOT / "implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001"
        program = ("import importlib,json,sys; from pathlib import Path; "
                   "sys.path[:0]=[sys.argv[1],sys.argv[2],sys.argv[3]]; "
                   "name=sys.argv[4]; g=importlib.import_module(name+'.guard'); "
                   "p=importlib.import_module(name+'.protocol'); "
                   "r=json.loads((Path(sys.argv[1])/name/'rebind-receipt.json').read_text()); "
                   "print(len(g.verify(r['successor_manifest_sha256'])['files']),"
                   "len(p.Schemas(r['profile_binding']['sha256']).profile['files']))")
        command = [str(install / "lib/abi/ld-linux-x86-64.so.2"), "--inhibit-cache", "--library-path",
                   str(install / "lib/abi"), str(install / "bin/python"), "-I", "-X", "utf8", "-B", "-S", "-c",
                   program, str(interface), str(ROOT / "implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay"), str(install / "deps"), API.name]
        child = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertEqual(child.stdout.strip(), "207 32138")
        no_overlay = list(command)
        no_overlay.remove(str(ROOT / "implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay"))
        no_overlay[no_overlay.index("-c") + 1] = program.replace("sys.argv[3]]", "sys.argv[2]]").replace("sys.argv[4]", "sys.argv[3]")
        refused = subprocess.run(no_overlay, capture_output=True, text=True)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("API environment differs", refused.stderr)
        members = json.loads((API / "integration-members.json").read_bytes())
        self.assertEqual(members["members"]["governance"]["directory"],
                         "api-governance-integration-v5-current-t12-0001")
        with self.assertRaises(ValueError):
            guard.verify("0" * 64)

    def test_historical_installation_metadata_is_pinned_at_runtime(self):
        control = load(SDK / "control.py", "t06_current_control_metadata_test")
        source = ROOT / "implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001/installation.json"
        raw = source.read_bytes()
        self.assertEqual((sha(raw), len(raw)),
                         (control.INSTALLATION_METADATA_SHA, control.INSTALLATION_METADATA_SIZE))
        with tempfile.TemporaryDirectory(prefix="cal-T06-metadata-test-") as scratch:
            path = Path(scratch) / "installation.json"
            path.write_bytes(raw)
            os.chmod(path, 0o600)
            self.assertEqual(control.installed(Path(scratch), {}), 0)
            changed = bytearray(raw)
            changed[0] ^= 1
            path.write_bytes(changed)
            with self.assertRaises(ValueError):
                control.installed(Path(scratch), {})
            path.write_bytes(raw)
            os.chmod(path, 0o644)
            with self.assertRaises(ValueError):
                control.installed(Path(scratch), {})

    def test_task_local_installation_is_closed_and_launcher_reaches_child(self):
        destination = ROOT / "implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001"
        receipt = json.loads((destination.parent / "INSTALLATION-0001.json").read_bytes())
        self.assertEqual(receipt["destination"], str(destination))
        self.assertEqual((receipt["selected_file_count"], receipt["inventory_file_count"]), (1010, 1011))
        self.assertEqual(list(destination.rglob("*.pyc")), [])
        launch = load(SDK / "launch.py", "t06_current_launcher_test")
        self.assertEqual(launch.INSTALL, destination)
        with mock.patch.object(sys, "argv", ["launch.py", "--launcher-source-sha256",
                                           sha((SDK / "source-manifest.json").read_bytes()),
                                           "--config", "/tmp/nonexistent-t06-config",
                                           "--config-sha256", "0" * 64]), \
             mock.patch.object(launch.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as child:
            self.assertEqual(launch.main(), 0)
        self.assertEqual(child.call_count, 1)
        self.assertEqual(Path(child.call_args.args[0][0]), destination / "lib/abi/ld-linux-x86-64.so.2")
        self.assertEqual(Path(child.call_args.args[0][4]), destination / "bin/python")

    def test_inherited_three_branch_config_semantics(self):
        historical = ROOT / "product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/checks.py"
        checks = load(historical, "t06_historical_fixture_checks")
        owned, config, _, _ = checks.fixture()
        try:
            sdk.config_shape(config)
            self.assertEqual(config["source"]["directory"], str(API))
            absent = copy.deepcopy(config)
            del absent["branches"]["governance"]
            with self.assertRaises(ValueError):
                sdk.config_shape(absent)
            promoted = copy.deepcopy(config)
            promoted["purpose"] = "admitted-operation"
            with self.assertRaises(ValueError):
                sdk.config_shape(promoted)
        finally:
            shutil.rmtree(owned)

    def test_manifest_exact_executable_rows(self):
        manifest = json.loads((SDK / "source-manifest.json").read_bytes())
        self.assertEqual(manifest["schema_version"], "lab-T06-current-api36-sdk-source/v1-candidate")
        expected = {row(SDK / name)["path"] for name in
                    ("bootstrap.py", "composite.py", "control.py", "framing.py", "launch.py", "composite.config.schema.json")}
        self.assertEqual({item["path"] for item in manifest["files"]}, expected)
        for item in manifest["files"]:
            raw = (ROOT / item["path"]).read_bytes()
            self.assertEqual((sha(raw), len(raw)), (item["sha256"], item["size_bytes"]))

    def test_branch_selection_true_origin_and_retained_historical_material(self):
        selection = json.loads((BRANCH / "driver-selection.json").read_bytes())
        self.assertEqual(selection["schema_version"], "lab-T06-current-api36-branch-driver-selection/v1-candidate")
        paths = {item["path"] for item in selection["files"]}
        self.assertIn(row(BRANCH / "prepare_branches.py")["path"], paths)
        self.assertIn(row(BRANCH / "drive_operator.py")["path"], paths)
        self.assertIn("docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-0001/action_fixture_signer_retained_v1.py", paths)
        for item in selection["files"]:
            self.assertEqual(sha((ROOT / item["path"]).read_bytes()), item["sha256"])
        preparer = load(BRANCH / "prepare_branches.py", "t06_current_preparer_test")
        self.assertEqual(preparer.HISTORICAL_FIXTURE,
                         ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-0001")
        self.assertEqual(preparer.INTERFACE, API.parent)
        for suffix in ("protocol", "guard", "fixtures", "legacy_fixture_selection"):
            self.assertIn("api-integration-v36-current-t06-0001." + suffix, preparer.prepare.__code__.co_consts)

    def test_driver_configures_exact_api36_and_refuses_historical_sdk(self):
        driver = load(BRANCH / "drive_operator.py", "t06_current_driver_test")
        with tempfile.TemporaryDirectory(prefix="cal-T06-branch-fixtures-") as scratch:
            record = {"root": scratch, "source_sha256": "a" * 64, "profile_sha256": "b" * 64,
                      "branches": {}, "issuers": {}}
            args = argparse.Namespace(sdk_directory=str(SDK),
                                      sdk_source_sha256=sha((SDK / "source-manifest.json").read_bytes()),
                                      provisioning_path="docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result.json",
                                      provisioning_sha256="c" * 64)
            config, path, digest = driver.configure(record, args)
            self.assertEqual(config["source"]["directory"], str(API))
            self.assertEqual(config["source"]["members_sha256"], sha((API / "integration-members.json").read_bytes()))
            self.assertEqual(digest, sha(path.read_bytes()))
        with tempfile.TemporaryDirectory(prefix="cal-T06-branch-fixtures-") as scratch:
            args.sdk_directory = str(API.parent / "composite-operator-v1-completion-0001/revision-0003")
            with self.assertRaisesRegex(ValueError, "current API36 SDK"):
                driver.configure({**record, "root": scratch}, args)
            self.assertFalse((Path(scratch) / "operator-config.json").exists())

    def test_software_guard_requires_source_profile_and_selected_successor_rows(self):
        members_raw = (API / "integration-members.json").read_bytes()
        files = [*json.loads((SDK / "source-manifest.json").read_bytes())["files"],
                 row(SDK / "source-manifest.json"), row(BRANCH / "prepare_branches.py"),
                 row(BRANCH / "drive_operator.py"), row(BRANCH / "driver-selection.json"),
                 row(ROOT / "implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/source-manifest.json"),
                 *(row(ROOT / item["path"]) for item in json.loads((ROOT / "implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/source-manifest.json").read_bytes())["files"])]
        profile = {"authority_effect": "none", "actual_owner_outcome": None,
                   "implemented_operations": [*("base." + str(n) for n in range(28)), *sdk.ACTION, *sdk.GOVERNANCE],
                   "integration_members_binding": row(API / "integration-members.json"), "files": files}

        def run(profile_value, source_profile_pin=None, selected_api=API, sdk_manifest_raw=None):
            profile_raw = sdk.compact(profile_value)
            profile_pin = sha(profile_raw)
            source = {"profile_binding": {"path": row(API / "contract-profile.json")["path"],
                                          "sha256": source_profile_pin or profile_pin}}
            source_raw = sdk.compact(source)
            source_pin = sha(source_raw)
            cache = {row(API / "source-manifest.json")["path"]: source_raw,
                     row(API / "contract-profile.json")["path"]: profile_raw}
            if sdk_manifest_raw is not None:
                cache[row(SDK / "source-manifest.json")["path"]] = sdk_manifest_raw

            def selected(binding):
                raw = cache.get(binding["path"])
                if raw is None:
                    raw = (ROOT / binding["path"]).read_bytes()
                if sha(raw) != binding["sha256"]:
                    raise ValueError("selected byte mutation")
                return raw

            bootstrap = [row(path) for path in (*SDK.glob("*.py"),
                         *(API / name for name in ("guard.py", "__init__.py", "source-manifest.json", "contract-profile.json", "integration-members.json")))]
            for item in bootstrap:
                if item["path"] == row(API / "source-manifest.json")["path"]:
                    item["sha256"] = source_pin
                elif item["path"] == row(API / "contract-profile.json")["path"]:
                    item["sha256"] = profile_pin
            config = {"source": {"directory": str(selected_api), "source_sha256": source_pin,
                                 "profile_sha256": profile_pin, "members_sha256": sha(members_raw),
                                 "bootstrap_bindings": bootstrap}, "dependencies": {}}
            with mock.patch.object(sdk, "public", side_effect=selected), mock.patch.object(sdk, "dependency_guard", return_value=1010):
                return sdk.software_guard(config)

        result = run(profile)
        self.assertEqual(result[1]["members"].keys(), {"actions", "governance"})
        old_member_origin = copy.deepcopy(profile)
        old_member_origin["integration_members_binding"]["path"] = "product/lab/release-candidates/v1/interface/api-integration-v16/integration-members.json"
        with self.assertRaisesRegex(ValueError, "current API36 member binding"):
            run(old_member_origin)
        missing = copy.deepcopy(profile)
        missing["files"] = [item for item in missing["files"] if item["path"] != row(BRANCH / "prepare_branches.py")["path"]]
        with self.assertRaises(ValueError):
            run(missing)
        with self.assertRaisesRegex(ValueError, "Source/profile binding"):
            run(profile, source_profile_pin="0" * 64)
        with self.assertRaisesRegex(ValueError, "current API36"):
            run(profile, selected_api=API.parent / "api-integration-v17")
        omitted = json.loads((SDK / "source-manifest.json").read_bytes())
        omitted["files"] = [item for item in omitted["files"] if not item["path"].endswith("/launch.py")]
        omitted_raw = sdk.compact(omitted)
        changed = copy.deepcopy(profile)
        next(item for item in changed["files"] if item["path"] == row(SDK / "source-manifest.json")["path"])["sha256"] = sha(omitted_raw)
        with self.assertRaisesRegex(ValueError, "closed current SDK executable inventory"):
            run(changed, sdk_manifest_raw=omitted_raw)


if __name__ == "__main__":
    unittest.main()
