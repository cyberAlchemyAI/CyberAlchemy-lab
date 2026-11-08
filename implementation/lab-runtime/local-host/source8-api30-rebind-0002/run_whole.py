"""Run the exact 99 selected cases with a versioned actual-clock timer test."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import time
import unittest

OLD_HARNESS = Path(__file__).resolve().parent.with_name("source8-api30-rebind-0001")
sys.path.insert(0, str(OLD_HARNESS))
from prepare_successor import (OUTPUT, ROOT, MACHINE_HELPERS, digest, family_values, FAMILY,
                               STABLE_NATIVE_EXE, OLD_EPHEMERAL_NATIVE_EXE, NATIVE_EXE_SHA,
                               AUTHORITY_CURRENT, AUTHORITY_CURRENT_SHA, OLD_SYSTEM_LIBLZMA,
                               INSTALLED_LIBLZMA, SELECTED_LIBLZMA_SHA)
from timer_test import successor_class

TIMER_TEST = Path(__file__).with_name("timer_test.py")
TIMER_TEST_SHA = "ef89247404c3006f22bb635449fb41e9ea576c626532c2d7f43d636b5868826e"
ORIGINAL_TEST_SHA = "8ce3da4b1b4141e01c97f2168ff7483f836248c8d6693f079daee3f6ceb78e42"

EXPECTED_WHOLE_CLASSES = {
    "test_custody_sessions": (34, "59c43a942b64df4055de9306c93be78fdb1e7f23c98613cbefb599129e41fb4d"),
    "run_session_checks": (34, "59c43a942b64df4055de9306c93be78fdb1e7f23c98613cbefb599129e41fb4d"),
    "test_current_controls": (11, "b9222c75c10c41410643a25a3bd5a5c29de8727943d09f8ddc96145b71dc0e0a"),
    "test_termination_boundaries": (6, "bbad18cb2fddc1e1c48b5b4ef593b7a8d0eee88301adf9ce65632e823ed78327"),
    "test_machine_transport": (14, "4b6d15ea0127148c9a3ecc92225a11bf4635246f9f0c427928c7da7278587b2e"),
}


class SuccessResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_ids = set()
        self.lease_expiries = {"reader_policy": [], "reader_context": [], "context_delivery": [], "session": []}
        self.case_rows = {}
        self._case_monotonic = {}

    def startTest(self, test):
        super().startTest(test)
        self._case_monotonic[test.id()] = time.monotonic()
        self.case_rows[test.id()] = {"test_id": test.id(), "started_at_utc": datetime.now(timezone.utc).isoformat(),
                                     "result": "IN_PROGRESS"}

    def stopTest(self, test):
        row = self.case_rows[test.id()]
        row["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        row["monotonic_elapsed_seconds"] = round(time.monotonic() - self._case_monotonic.pop(test.id()), 3)
        row["observed_lease_expiries"] = self._expiry_snapshot(test)
        super().stopTest(test)

    def addError(self, test, error):
        super().addError(test, error)
        if test.id() in self.case_rows:
            self.case_rows[test.id()]["result"] = "ERROR"

    def addFailure(self, test, error):
        super().addFailure(test, error)
        if test.id() in self.case_rows:
            self.case_rows[test.id()]["result"] = "FAIL"

    @staticmethod
    def _expiry_snapshot(test):
        found = {"reader_policy": None, "reader_context": None, "context_delivery": None, "session": None}
        channel = getattr(test, "channel", None)
        if channel is not None:
            for name, value in (("reader_policy", getattr(channel, "policy", None)),
                                ("reader_context", getattr(channel, "context", None))):
                if isinstance(value, dict) and isinstance(value.get("expires_at"), str):
                    found[name] = value["expires_at"]
        delivery = getattr(test, "delivery_result", None)
        if isinstance(delivery, dict) and isinstance(delivery.get("expires_at"), str):
            found["context_delivery"] = delivery["expires_at"]
        resource = getattr(test, "resource", None)
        if resource is not None and isinstance(getattr(resource, "expires", None), datetime):
            found["session"] = resource.expires.isoformat()
        opened = getattr(test, "opened_result", None)
        if isinstance(opened, dict) and isinstance(opened.get("expires_at"), str):
            found["session"] = opened["expires_at"]
        return found

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed_ids.add(test.id())
        self.case_rows[test.id()]["result"] = "PASS"
        for name, value in self._expiry_snapshot(test).items():
            if value is not None:
                self.lease_expiries[name].append(value)


def lease_summary(*results: SuccessResult) -> dict:
    """Record observed public expiry instants only, never policies or keys."""
    combined = {name: [] for name in results[0].lease_expiries}
    for result in results:
        for name, values in result.lease_expiries.items():
            combined[name].extend(values)
    return {name: {"observations": len(values), "earliest_expires_at": min(values) if values else None,
                   "latest_expires_at": max(values) if values else None}
            for name, values in combined.items()}


def package_at(path: Path):
    name = "_cal_api30_current_source8_successor_0001"
    spec = importlib.util.spec_from_file_location(name, path / "__init__.py",
                                                  submodule_search_locations=[str(path)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return name


def stable_native_executable_current() -> bool:
    path = ROOT / STABLE_NATIVE_EXE
    if not path.is_file() or path.is_symlink():
        return False
    info = path.stat()
    with path.open("rb") as stream:
        header = stream.read(20)
    return (stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o755
            and info.st_uid == os.getuid() and info.st_size == 20243600
            and header[:6] == b"\x7fELF\x02\x01" and header[18:20] == b"\x3e\x00"
            and digest(path) == NATIVE_EXE_SHA)


def run(family: Path = FAMILY, output: Path = OUTPUT, context_path: Path | None = None) -> dict:
    harness_files = (Path(__file__).resolve(), TIMER_TEST,
                     OLD_HARNESS / "prepare_successor.py",
                     OLD_HARNESS / "test_prepare_successor.py")
    harness_binding = [{"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}
                       for path in harness_files]
    if digest(TIMER_TEST) != TIMER_TEST_SHA or digest(OUTPUT / "test_custody_sessions.py") != ORIGINAL_TEST_SHA:
        raise ValueError("versioned timer test or frozen original source differs")
    family = family.resolve(strict=True)
    values = family_values(family, context_path)
    if output != OUTPUT or not output.is_dir():
        raise ValueError("selected API30 successor does not exist")
    receipt_path = output / "rebind-receipt.json"
    receipt_sha = digest(receipt_path)
    receipt = json.loads(receipt_path.read_bytes())
    if receipt["family"] != values or receipt["whole_session_classes_tested"] is not False:
        raise ValueError("successor selection differs or was already tested")
    if receipt["successor_manifest_sha256"] != digest(output / "source-manifest.json"):
        raise ValueError("successor receipt does not bind selected manifest")
    t06_rows = receipt.get("selected_t06_operator_rows")
    if type(t06_rows) is not list or len(t06_rows) != 10 or len({row["path"] for row in t06_rows}) != 10:
        raise ValueError("exact T06 operator profile selection missing")
    profile_files = {row["path"]: row["sha256"] for row in json.loads((output / "contract-profile.json").read_bytes())["files"]}
    profile = json.loads((output / "contract-profile.json").read_bytes())
    members = receipt.get("current_integration_members_binding")
    if (members != {"path": (output / "integration-members.json").relative_to(ROOT).as_posix(),
                    "sha256": digest(output / "integration-members.json")} or
            profile["integration_members_binding"] != members or
            profile_files.get(members["path"]) != members["sha256"]):
        raise ValueError("current API33 integration members origin differs")
    stable_exe = {"path": STABLE_NATIVE_EXE, "sha256": NATIVE_EXE_SHA}
    if (receipt.get("stable_native_executable_binding") != stable_exe or
            OLD_EPHEMERAL_NATIVE_EXE in profile_files or
            profile_files.get(STABLE_NATIVE_EXE) != NATIVE_EXE_SHA or
            not stable_native_executable_current()):
        raise ValueError("stable native executable profile selection differs")
    selected_current_rows = receipt.get("current_authority_and_liblzma_bindings")
    if (selected_current_rows != {
            "current_authority": {"path": AUTHORITY_CURRENT, "sha256": AUTHORITY_CURRENT_SHA},
            "installed_liblzma": {"path": INSTALLED_LIBLZMA, "sha256": SELECTED_LIBLZMA_SHA},
            "retired_system_liblzma": {"path": OLD_SYSTEM_LIBLZMA, "sha256": SELECTED_LIBLZMA_SHA}}
            or profile_files.get(AUTHORITY_CURRENT) != AUTHORITY_CURRENT_SHA
            or profile_files.get(INSTALLED_LIBLZMA) != SELECTED_LIBLZMA_SHA
            or OLD_SYSTEM_LIBLZMA in profile_files):
        raise ValueError("current authority or installed liblzma selection differs")
    if any(profile_files.get(row["path"]) != row["sha256"] or not (ROOT / row["path"]).is_file()
           or (ROOT / row["path"]).is_symlink() or digest(ROOT / row["path"]) != row["sha256"]
           for row in t06_rows):
        raise ValueError("selected T06 operator profile bytes differ")
    selected_manifest_sha = receipt["successor_manifest_sha256"]
    manifest = json.loads((output / "source-manifest.json").read_bytes())
    expected_helpers = {((output.parent / helper / name).relative_to(ROOT).as_posix())
                        for helper in MACHINE_HELPERS for name in ("__init__.py", "generation.py")}
    bound_helpers = {item["path"] for item in receipt.get("external_machine_helpers", [])}
    if bound_helpers != expected_helpers or not bound_helpers.issubset({item["path"] for item in manifest["files"]}):
        raise ValueError("Machine helper closure is not pinned")
    for item in manifest["files"]:
        path = ROOT / item["path"]
        if not path.is_file() or path.is_symlink() or digest(path) != item["sha256"]:
            raise ValueError(f"successor byte closure differs: {item['path']}")
    package = package_at(output)
    source = __import__(package + ".source_bridge", fromlist=["current_legacy_delivery"])
    legacy = source.current_legacy_delivery()
    current = source.current_session_fixture_delivery()
    selected_context = ROOT / values["context_path"]
    if (legacy.HERE, current.HERE) != (selected_context, selected_context):
        raise ValueError("Context producer origin differs")
    for producer in (legacy, current):
        if producer.reader.source_pin != values["source_sha256"] or producer.reader.package_pin != values["source_package_sha256"]:
            raise ValueError("Reader source/package pins differ")
    old_source = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/fresh-legacy-current-runtime-preparation-0009/instances/legacy-source8-20261018-b/source"
    try:
        with legacy.reader.open_signed(digest(old_source / "source-manifest.json"),
                                       digest(old_source / "packages/0001/manifest.json")):
            pass
    except ValueError:
        wrong_origin_refused = True
    else:
        raise AssertionError("old source was accepted by current Reader")
    started_at = datetime.now(timezone.utc).isoformat()
    monotonic_start = time.monotonic()
    suite = unittest.TestSuite()
    counts = {}
    for filename, class_name in (("test_custody_sessions", "Sessions"),
                                 ("run_session_checks", "Sessions"),
                                 ("test_current_controls", "CurrentControls"),
                                 ("test_termination_boundaries", "TerminationBoundaries"),
                                 ("test_machine_transport", "MachineTransport")):
        module = __import__(package + "." + filename, fromlist=[class_name])
        module.PROFILE = digest(output / "contract-profile.json")
        cls = getattr(module, class_name)
        if filename == "test_custody_sessions":
            cls = successor_class(cls, module)
        methods = unittest.defaultTestLoader.getTestCaseNames(cls)
        method_sha = hashlib.sha256(json.dumps(methods, separators=(",", ":")).encode()).hexdigest()
        if (len(methods), method_sha) != EXPECTED_WHOLE_CLASSES[filename]:
            raise ValueError(f"whole {filename} test method selection differs")
        case = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
        counts[filename] = case.countTestCases()
        suite.addTests(case)
    result = unittest.TextTestRunner(verbosity=2, resultclass=SuccessResult, failfast=True).run(suite)
    expired_id = package + ".test_current_controls.CurrentControls.test_01_expired_legacy_source_refuses_new_session_grant"
    machine_context_id = package + ".test_machine_transport.MachineTransport.test_02_all_seven_public_read_operations_with_actual_Actor"
    session_module = sys.modules[package + ".test_custody_sessions"]
    machine_module = sys.modules[package + ".test_machine_transport"]
    current_session = __import__(package + ".current_context_sessions", fromlist=["D", "R"])
    originals = (session_module.PUBLIC_SOURCE_NAME, session_module.D, session_module.R, machine_module.D)
    current_result = None
    if result.wasSuccessful():
        try:
            session_module.PUBLIC_SOURCE_NAME = source.CURRENT_SOURCE8_NAME
            session_module.D = current_session.D
            session_module.R = current_session.R
            machine_module.D = current_session.D
            current_case = machine_module.MachineTransport("test_02_all_seven_public_read_operations_with_actual_Actor")
            current_result = unittest.TextTestRunner(verbosity=2, resultclass=SuccessResult, failfast=True).run(unittest.TestSuite([current_case]))
        finally:
            session_module.PUBLIC_SOURCE_NAME, session_module.D, session_module.R, machine_module.D = originals
    completed_at = datetime.now(timezone.utc).isoformat()
    elapsed_seconds = round(time.monotonic() - monotonic_start, 3)
    verdict = {"result": "PASS" if result.wasSuccessful() else "FAIL",
               "schema": "cal-api33-versioned-whole-classes-timer/v1",
               "test_27_selection": {"original_test_sha256": ORIGINAL_TEST_SHA,
                                     "successor_path": TIMER_TEST.relative_to(ROOT).as_posix(),
                                     "successor_sha256": TIMER_TEST_SHA,
                                     "reason": "frozen 70-second request deadline expired during actual guarded session.open"},
               "started_at_utc": started_at, "completed_at_utc": completed_at,
               "monotonic_elapsed_seconds": elapsed_seconds,
               "selected_source_period_expires_at": values["expires_at"],
               "historical_context_construction_delivery_expires_at": values["historical_context_construction_delivery_expires_at"],
               "historical_context_construction_host_permission_expires_at": values["historical_context_construction_host_permission_expires_at"],
               "observed_lease_expiries": lease_summary(result, *([current_result] if current_result is not None else [])),
               "case_rows": list(result.case_rows.values()),
               "current_source8_machine_case_rows": list(current_result.case_rows.values()) if current_result is not None else [],
               "tests_run": result.testsRun, "class_case_counts": counts,
               "errors": [(case.id(), str(error)[-1500:]) for case, error in result.errors],
               "failures": [(case.id(), str(error)[-1500:]) for case, error in result.failures],
               "wrong_origin_old_source_refused": wrong_origin_refused,
               "expired_original_negative_passed": expired_id in result.passed_ids,
               "current_legacy_machine_context_get_passed": machine_context_id in result.passed_ids,
               "current_source8_machine_context_get_passed": current_result is not None and current_result.wasSuccessful() and machine_context_id in current_result.passed_ids,
               "current_source8_machine_errors": [(case.id(), str(error)[-1500:]) for case, error in current_result.errors] if current_result is not None else [],
               "current_source8_machine_failures": [(case.id(), str(error)[-1500:]) for case, error in current_result.failures] if current_result is not None else [],
               "successor_manifest_sha256": selected_manifest_sha,
               "selected_t06_operator_rows": t06_rows,
               "current_integration_members_binding": members,
               "stable_native_executable_binding": stable_exe,
               "family_context_manifest_sha256": values["context_sha256"]}
    verdict["harness_bindings"] = harness_binding
    verdict["harness_unchanged_during_run"] = all(digest(ROOT / row["path"]) == row["sha256"]
                                                  for row in harness_binding)
    verdict["source_unchanged_during_run"] = (digest(output / "source-manifest.json") == selected_manifest_sha
        and digest(receipt_path) == receipt_sha
        and all((ROOT / row["path"]).is_file() and not (ROOT / row["path"]).is_symlink()
                and digest(ROOT / row["path"]) == row["sha256"] for row in manifest["files"]))
    verdict["t06_operator_unchanged_during_run"] = all(
        (ROOT / row["path"]).is_file() and not (ROOT / row["path"]).is_symlink()
        and digest(ROOT / row["path"]) == row["sha256"] for row in t06_rows)
    verdict["stable_native_executable_unchanged_during_run"] = stable_native_executable_current()
    expected_cases = sum(row[0] for row in EXPECTED_WHOLE_CLASSES.values())
    verdict["exact_whole_class_coverage"] = (result.testsRun == expected_cases
                                              and len(result.passed_ids) == expected_cases
                                              and not result.skipped and not result.unexpectedSuccesses
                                              and not result.expectedFailures)
    if not (verdict["expired_original_negative_passed"] and verdict["current_legacy_machine_context_get_passed"]
            and verdict["current_source8_machine_context_get_passed"] and verdict["exact_whole_class_coverage"]
            and verdict["harness_unchanged_during_run"] and verdict["source_unchanged_during_run"]
            and verdict["t06_operator_unchanged_during_run"]
            and verdict["stable_native_executable_unchanged_during_run"]):
        verdict["result"] = "FAIL"
    out = Path(__file__).resolve().parent / "working"
    out.mkdir(mode=0o700, exist_ok=True)
    result_path = out / "whole-classes-result-0001.json"
    if result_path.exists():
        raise ValueError("versioned whole-class result already exists")
    result_path.write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n")
    return verdict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", type=Path, default=FAMILY)
    parser.add_argument("--context-path", type=Path)
    args = parser.parse_args()
    result = run(args.family, context_path=args.context_path)
    print(json.dumps({"result": result["result"], "tests_run": result["tests_run"],
                      "errors": len(result["errors"]), "failures": len(result["failures"])}))
    raise SystemExit(0 if result["result"] == "PASS" else 1)
