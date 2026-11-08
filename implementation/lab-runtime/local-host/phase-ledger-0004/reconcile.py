"""Bind current native/API clocks, including deliberate Session-expiry tests."""

import argparse
import datetime as dt
import hashlib
import json
import os
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHAIN = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/NATIVE-CHAIN-RECEIPT-0001.json"
API = ROOT / "implementation/lab-runtime/local-host/source8-api30-rebind-0004/working/whole-classes-result-0001.json"
OUTPUT = Path(__file__).resolve().parent / "observed-current-family-0002.json"
LEASES = ("reader_policy", "reader_context", "context_delivery", "session")
PHASES = ("source", "cold", "reader", "mapped", "context")
API_PACKAGE = "_cal_api30_current_source8_successor_0001"
DELIBERATE_SESSION_EXPIRY_CASES = frozenset({
    API_PACKAGE + ".test_custody_sessions.Sessions.test_27_actual_expiry_timer_disposes",
    API_PACKAGE + ".run_session_checks.Sessions.test_27_actual_expiry_timer_disposes",
    API_PACKAGE + ".test_machine_transport.MachineTransport.test_13_real_original_expiry_closes_transport_without_renewal",
})
TIMER_SUCCESSOR_SHA = "787a94892aa60386ae18acc2c8d8112339f348c50b130c3c1dcf22e06dc5c6a1"


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def utc(value):
    need(type(value) is str, "UTC_TEXT_REQUIRED")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("UTC_INVALID") from None
    need(parsed.tzinfo is not None and parsed.utcoffset() == dt.timedelta(), "UTC_REQUIRED")
    return parsed


def checked(root, row, *, family=None):
    need(type(row) is dict and set(row) == {"path", "sha256"}, "BINDING_SHAPE_REFUSED")
    name = row["path"]
    need(type(name) is str and not Path(name).is_absolute() and ".." not in Path(name).parts,
         "BINDING_PATH_REFUSED")
    path = root / name
    need(not root.is_symlink(), "BINDING_ROOT_SYMLINK_REFUSED")
    cursor = root
    for part in Path(name).parts:
        cursor = cursor / part
        need(not cursor.is_symlink(), "BINDING_ANCESTOR_SYMLINK_REFUSED")
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root),
         "BINDING_ORIGIN_REFUSED")
    if family is not None:
        need(path.is_relative_to(family), "FAMILY_BINDING_REFUSED")
    raw = path.read_bytes()
    need(sha(raw) == row["sha256"], "BINDING_DIGEST_CHANGED " + name)
    return path, raw


def reconcile(root, chain_path, api_path):
    chain_raw = chain_path.read_bytes()
    chain = json.loads(chain_raw)
    need(chain["schema"] == "cal-native-current-source8-local-chain-receipt/v1" and
         chain["protected_source8_qualification"] is False and chain["authority_effect"] == "none",
         "LOCAL_FAMILY_CLAIM_REFUSED")
    family = root / chain["family_path"]
    need(family.is_dir() and not family.is_symlink() and family.resolve().is_relative_to(root),
         "FAMILY_ORIGIN_REFUSED")
    phase = {}
    for name in PHASES:
        _, raw = checked(root, chain["phase_results"][name], family=family)
        phase[name] = json.loads(raw)
    _, period_raw = checked(root, chain["period_binding"], family=family)
    period = json.loads(period_raw)
    source_begin = utc(period["not_before"])
    source_end = utc(period["expires_at"])
    need(source_end - source_begin == dt.timedelta(hours=24) and
         chain["not_before"] == period["not_before"] and chain["expires_at"] == period["expires_at"],
         "SOURCE_PERIOD_BINDING_REFUSED")
    need(phase["cold"]["result"] == "PASS-native-cold" and
         phase["cold"]["independent_cold_replays"] == 2 and
         phase["cold"]["original_byte_parity"] is True and
         phase["reader"]["result"] == "PASS-current-reader" and
         phase["mapped"]["result"] == "PASS-native-mapper" and
         phase["context"]["result"] == "PASS-native-Context-construction",
         "NATIVE_CHAIN_PHASE_REFUSED")
    for result_name, fields in {
        "source": ("source_binding", "package_binding", "native_build_receipt"),
        "cold": ("source_binding", "package_binding", "period_binding"),
        "reader": ("reader_binding",),
        "mapped": ("mapper_binding", "package_binding"),
        "context": ("context_binding", "package_binding", "implementation_binding"),
    }.items():
        for field in fields:
            checked(root, phase[result_name][field], family=family)
    need(phase["source"]["source_binding"] == phase["cold"]["source_binding"] and
         phase["source"]["package_binding"] == phase["cold"]["package_binding"] and
         chain["period_binding"] == phase["cold"]["period_binding"],
         "SOURCE_COLD_LINK_REFUSED")
    _, delivery_raw = checked(root, json.loads((family / "context/packages/0001/manifest.json").read_bytes())
                              ["delivery_binding"], family=family)
    original_delivery = json.loads(delivery_raw)
    api_raw = api_path.read_bytes()
    api = json.loads(api_raw)
    need(api.get("schema") == "cal-api33-versioned-whole-classes-timer/v1" and
         api.get("test_27_selection", {}).get("successor_sha256") == TIMER_SUCCESSOR_SHA,
         "VERSIONED_TIMER_SELECTION_REFUSED")
    need(api["family_context_manifest_sha256"] == phase["context"]["context_binding"]["sha256"] and
         api["selected_source_period_expires_at"] == period["expires_at"],
         "API_FAMILY_BINDING_REFUSED")
    api_start, api_end = utc(api["started_at_utc"]), utc(api["completed_at_utc"])
    need(source_begin <= api_start <= api_end < source_end, "API_OUTSIDE_SOURCE_PERIOD")
    whole_rows = api.get("case_rows", [])
    machine_rows = api.get("current_source8_machine_case_rows", [])
    selected_ids = api.get("selected_case_ids")
    need(type(whole_rows) is list and type(machine_rows) is list and type(selected_ids) is list and
         all(type(row) is dict for row in whole_rows) and
         all(type(value) is str for value in selected_ids) and len(set(selected_ids)) == len(selected_ids) and
         len(whole_rows) == api["tests_run"] and 0 < len(whole_rows) <= len(selected_ids) and
         [row.get("test_id") for row in whole_rows] == selected_ids[:len(whole_rows)],
         "API_CASE_SET_REFUSED")
    extra_machine_id = (API_PACKAGE + ".test_machine_transport.MachineTransport."
                        "test_02_all_seven_public_read_operations_with_actual_Actor")
    need(len(machine_rows) <= 1 and
         all(type(row) is dict and row.get("test_id") == extra_machine_id for row in machine_rows),
         "EXTRA_MACHINE_CASE_SET_REFUSED")
    if api["result"] == "PASS":
        need(len(whole_rows) == len(selected_ids) == 99 and len(machine_rows) == 1,
             "COMPLETE_CASE_SET_REFUSED")
    rows = [("whole", row) for row in whole_rows] + [("current-source8-machine", row) for row in machine_rows]
    observed = []
    counts = {name: 0 for name in LEASES}
    deliberate_observed = set()
    for role, row in rows:
        need(type(row) is dict and row["result"] in ("PASS", "FAIL", "ERROR") and
             type(row["test_id"]) is str and type(row["monotonic_elapsed_seconds"]) in (int, float) and
             row["monotonic_elapsed_seconds"] >= 0, "CASE_ROW_REFUSED")
        begin, end = utc(row["started_at_utc"]), utc(row["completed_at_utc"])
        need(api_start <= begin <= end <= api_end and end < source_end, "CASE_TIME_REFUSED")
        leases = row["observed_lease_expiries"]
        need(type(leases) is dict and set(leases) == set(LEASES), "CASE_LEASE_SHAPE_REFUSED")
        actual = {"source": source_end}
        for name in LEASES:
            if leases[name] is not None:
                actual[name] = utc(leases[name])
                counts[name] += 1
        strictest = min(actual.values())
        expired = sorted(name for name, expires in actual.items() if end >= expires)
        deliberate = row["test_id"] in DELIBERATE_SESSION_EXPIRY_CASES
        if deliberate and row["result"] == "PASS":
            need("session" in expired, "DELIBERATE_SESSION_EXPIRY_NOT_OBSERVED")
            deliberate_observed.add(row["test_id"])
        observed.append({"test_id": row["test_id"], "case_role": role,
                         "result": row["result"],
                         "started_at_utc": begin.isoformat(), "completed_at_utc": end.isoformat(),
                         "monotonic_elapsed_seconds": row["monotonic_elapsed_seconds"],
                         "observed_lease_kinds": sorted(actual),
                         "strictest_observed_expires_at": strictest.isoformat(),
                         "ended_before_strictest_observed_expiry": end < strictest,
                         "expired_observed_lease_kinds_at_case_end": expired,
                         "deliberate_session_expiry_case": deliberate,
                         "session_expiry_lag_seconds": round((end - actual["session"]).total_seconds(), 3)
                            if deliberate and "session" in actual else None,
                         "callback_count": None, "pure_scope_boundary_count": None})
    if api["result"] == "PASS" and api["tests_run"] == 99:
        need(deliberate_observed == DELIBERATE_SESSION_EXPIRY_CASES,
             "COMPLETE_DELIBERATE_EXPIRY_COVERAGE_REFUSED")
    return {
        "schema": "cal-current-family-observed-phase-ledger/v2", "authority_effect": "none",
        "claim_ceiling": "Actual local native chain and API case clocks; deliberate Session-expiry tests are recorded separately. Callback/scope counts and missing lease origins remain unproven.",
        "chain_receipt_sha256": sha(chain_raw), "api_result_sha256": sha(api_raw),
        "family_instance": chain["instance"],
        "source_period_binding": chain["period_binding"],
        "source_period_not_before": period["not_before"], "source_period_expires_at": period["expires_at"],
        "original_context_construction_delivery_expires_at": original_delivery["expires_at"],
        "phase_result_bindings": chain["phase_results"],
        "api_result": api["result"], "api_monotonic_elapsed_seconds": api["monotonic_elapsed_seconds"],
        "api_started_at_utc": api["started_at_utc"], "api_completed_at_utc": api["completed_at_utc"],
        "wrong_origin_old_source_refused": api["wrong_origin_old_source_refused"],
        "expired_original_negative_passed": api["expired_original_negative_passed"],
        "case_count": len(observed), "observed_lease_counts": counts,
        "deliberate_session_expiry_test_ids": sorted(deliberate_observed),
        "deliberate_session_expiry_count": len(deliberate_observed),
        "cases": observed,
        "all_cases_passed": all(row["result"] == "PASS" for row in observed),
        "all_observed_lease_checks_current_at_case_end": all(
            row["ended_before_strictest_observed_expiry"] for row in observed),
        "all_nonexpiry_cases_current_at_case_end": all(
            row["ended_before_strictest_observed_expiry"] for row in observed
            if not row["deliberate_session_expiry_case"]),
        "unexpected_expired_observed_lease_cases": [
            {"test_id": row["test_id"], "lease_kinds": [
                name for name in row["expired_observed_lease_kinds_at_case_end"]
                if not (row["deliberate_session_expiry_case"] and name == "session")]}
            for row in observed if any(
                not (row["deliberate_session_expiry_case"] and name == "session")
                for name in row["expired_observed_lease_kinds_at_case_end"])],
    }


def write_new(path, value):
    need(path.parent.is_dir() and not path.parent.is_symlink(), "LEDGER_PARENT_REFUSED")
    parent = path.parent.stat()
    need(parent.st_uid == os.getuid() and not stat.S_IMODE(parent.st_mode) & 0o022,
         "LEDGER_PARENT_MODE_REFUSED")
    raw = json.dumps(value, sort_keys=True, indent=2).encode() + b"\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        need(stream.write(raw) == len(raw), "LEDGER_SHORT_WRITE")
        stream.flush()
        os.fsync(stream.fileno())
    return sha(raw)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chain", type=Path, default=CHAIN)
    parser.add_argument("--api", type=Path, default=API)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = reconcile(ROOT, args.chain, args.api)
    print(json.dumps({"output": str(args.output), "sha256": write_new(args.output, result),
                      "case_count": result["case_count"], "api_result": result["api_result"]},
                     sort_keys=True))
