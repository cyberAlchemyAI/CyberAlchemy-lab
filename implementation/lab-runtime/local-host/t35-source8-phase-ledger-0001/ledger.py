#!/usr/bin/env python3
"""Cold, public T35 timing ledger over two frozen T02 receipts."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
V4 = ("implementation/lab-runtime/local-host/source8-api30-rebind-0004/working/whole-classes-result-0001.json",
      "90c3c6ca270031930351485ff9a70660240d55b2186393abe46c32f55d26427f")
V5 = ("implementation/lab-runtime/local-host/source8-api30-rebind-0005/working/remainder-result-0001.json",
      "20b649f019253210123a4b345d9a6a8305a6cc5e7b11b158345e341ac307e143")
RUNNER4 = ("implementation/lab-runtime/local-host/source8-api30-rebind-0004/run_whole.py",
           "03ef57c50c519375e99e656fcf885135f63f5b941ea295032ad6af8e3e170f0b")
RUNNER5 = ("implementation/lab-runtime/local-host/source8-api30-rebind-0005/run_remainder.py",
           "0511ceca71d145c4753a469e56a8ac99655d1565b65ef91e57c35593421a02ea")
TIMER = ("implementation/lab-runtime/local-host/source8-api30-rebind-0004/timer_test.py",
         "787a94892aa60386ae18acc2c8d8112339f348c50b130c3c1dcf22e06dc5c6a1")
OLD_PERIOD = ("product/lab/release-candidates/v1/interface/session-participation-v2/packages/0001/period.json",
              "2c0a79e0a8f471114822cc8aed489edf514c7064942442d2670dfdccb2c0a082")
LEASE_KEYS = ("reader_policy", "reader_context", "context_delivery", "session")
EXPIRED_CASE = "_cal_api30_current_source8_successor_0001.test_current_controls.CurrentControls.test_01_expired_legacy_source_refuses_new_session_grant"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def selected(binding: tuple[str, str]) -> bytes:
    path = ROOT / binding[0]
    need(path.is_file() and not path.is_symlink(), "selected file absent or linked")
    raw = path.read_bytes()
    need(digest(raw) == binding[1], "selected file bytes changed: " + binding[0])
    return raw


def utc(value: str) -> datetime:
    need(type(value) is str, "timestamp is not text")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("timestamp is malformed") from error
    need(result.tzinfo is not None and result.utcoffset() == timedelta(0), "timestamp is not UTC")
    return result.astimezone(timezone.utc)


def validate_window(start: str, end: str, monotonic: float, *, tolerance: float = 0.02) -> None:
    wall = (utc(end) - utc(start)).total_seconds()
    need(type(monotonic) in (int, float) and monotonic >= 0 and wall >= 0 and
         abs(wall - monotonic) <= tolerance, "UTC and monotonic clocks disagree")


def validate_receipts(v4: dict, v5: dict) -> None:
    need(v4["schema"] == "cal-api33-versioned-whole-classes-timer/v1" and
         v4["result"] == "FAIL" and v4["tests_run"] == 69 and
         len(v4["case_rows"]) == 69 and len(v4["selected_case_ids"]) == 99 and
         len(set(v4["selected_case_ids"])) == 99 and
         [r["test_id"] for r in v4["case_rows"]] == v4["selected_case_ids"][:69] and
         [r["result"] for r in v4["case_rows"]] == ["PASS"] * 68 + ["FAIL"] and
         v4["errors"] == [] and len(v4["failures"]) == 1 and
         v4["failures"][0][0] == EXPIRED_CASE and
         "selected R02 participation environment differs" in v4["failures"][0][1] and
         v4["expired_original_negative_passed"] is False and
         v4["wrong_origin_old_source_refused"] is True and
         all(v4[k] is True for k in ("source_unchanged_during_run", "harness_unchanged_during_run",
                                      "t06_operator_unchanged_during_run",
                                      "stable_native_executable_unchanged_during_run")),
         "frozen v4 case selection or refusal differs")
    need(v5["result"] == "FAIL" and v5["tests_run"] == 17 and
         v5["predecessor_result_sha256"] == V4[1] and
         v5["selected_case_ids"] == v4["selected_case_ids"][68:] and
         len(v5["case_rows"]) == 17 and
         [r["test_id"] for r in v5["case_rows"]] == v5["selected_case_ids"][:17] and
         all(r["result"] == "PASS" for r in v5["case_rows"]) and
         v5["case_rows"][0]["test_id"] == EXPIRED_CASE and
         v5["failures"] == [] and len(v5["errors"]) == 1 and
         "setUpClass" in v5["errors"][0][0] and
         "NameError: name 'PROFILE' is not defined" in v5["errors"][0][1] and
         v5["expired_original_claim"] ==
         "constructor refuses at historical environment; exact policy period guard separately refuses expired Assignment with source preflight disabled" and
         v5["source_unchanged_during_run"] is True and
         v5["source_manifest_sha256"] == v4["successor_manifest_sha256"] and
         v5["runner_sha256"] == RUNNER5[1],
         "frozen v5 suffix, expired refusal, or stop differs")
    source_expiry = utc(v4["selected_source_period_expires_at"])
    validate_window(v4["started_at_utc"], v4["completed_at_utc"], v4["monotonic_elapsed_seconds"])
    need(utc(v4["completed_at_utc"]) < utc(v5["started_at_utc"]), "v4/v5 run order differs")
    need(utc(v5["started_at_utc"]) <= utc(v5["completed_at_utc"]) < source_expiry,
         "source period was not current across observed run windows")
    for version, rows, start, end in (("v4", v4["case_rows"], v4["started_at_utc"], v4["completed_at_utc"]),
                                      ("v5", v5["case_rows"], v5["started_at_utc"], v5["completed_at_utc"])):
        previous_end = utc(start)
        for row in rows:
            validate_window(row["started_at_utc"], row["completed_at_utc"], row["monotonic_elapsed_seconds"])
            case_start, case_end = utc(row["started_at_utc"]), utc(row["completed_at_utc"])
            need(previous_end <= case_start and case_end <= utc(end) and case_end < source_expiry,
                 version + " case clock order or source period differs")
            previous_end = case_end
            if version == "v4":
                leases = row["observed_lease_expiries"]
                need(set(leases) == set(LEASE_KEYS), "v4 lease snapshot shape differs")
                for value in leases.values():
                    if value is not None:
                        utc(value)
            else:
                need("observed_lease_expiries" not in row, "v5 lease instrumentation claim differs")
    positive = v4["case_rows"][:68]
    observed = {name: [r["observed_lease_expiries"][name] for r in positive
                       if r["observed_lease_expiries"][name] is not None] for name in LEASE_KEYS}
    need({name: len(values) for name, values in observed.items()} ==
         {"reader_policy": 68, "reader_context": 0, "context_delivery": 56, "session": 2},
         "positive lease observation counts differ")
    for name, values in observed.items():
        summary = v4["observed_lease_expiries"][name]
        need(summary == {"observations": len(values), "earliest_expires_at": min(values) if values else None,
                         "latest_expires_at": max(values) if values else None},
             "v4 lease summary differs")
    timers = [r for r in positive if r["observed_lease_expiries"]["session"] is not None]
    need(len(timers) == 2 and all("test_27_actual_expiry_timer_disposes" in r["test_id"] and
         utc(r["started_at_utc"]) < utc(r["observed_lease_expiries"]["session"]) <=
         utc(r["completed_at_utc"]) for r in timers), "actual Session expiry timer evidence differs")


def validate_original_period(period: dict, v5: dict) -> None:
    need(period["period_ref"] == "protocol:R03-fresh-assignment-period/v1" and
         period["principal_ref"] == "principal:R03-fresh-reader" and
         period["authority_effect"] == "none" and
         utc(period["not_before"]) < utc(period["expires_at"]) <
         utc(v5["case_rows"][0]["started_at_utc"]),
         "historical absolute Assignment period was not expired at refusal")


def build() -> dict:
    for binding in (RUNNER4, RUNNER5, TIMER):
        selected(binding)
    v4_raw, v5_raw = selected(V4), selected(V5)
    v4, v5 = json.loads(v4_raw), json.loads(v5_raw)
    period = json.loads(selected(OLD_PERIOD))
    validate_receipts(v4, v5)
    validate_original_period(period, v5)
    rows = []
    for version, selected_rows in (("v4", v4["case_rows"][:68]), ("v5", v5["case_rows"])):
        for item in selected_rows:
            rows.append({"receipt": version, "test_id": item["test_id"], "result": "PASS",
                         "started_at_utc": item["started_at_utc"],
                         "completed_at_utc": item["completed_at_utc"],
                         "monotonic_elapsed_seconds": item["monotonic_elapsed_seconds"],
                         "lease_capture": "exit_snapshot" if version == "v4" else "not_instrumented",
                         "observed_lease_expiries": item["observed_lease_expiries"] if version == "v4" else None})
    timer_rows = [row for row in rows if row["observed_lease_expiries"] and
                  row["observed_lease_expiries"]["session"] is not None]
    return {
        "schema_version": "lab-T35-frozen-case-phase-ledger/v1",
        "input_bindings": [{"path": path, "sha256": sha} for path, sha in (V4, V5, RUNNER4, RUNNER5, TIMER, OLD_PERIOD)],
        "source_phase": {"selected_source_period_expires_at": v4["selected_source_period_expires_at"],
                         "source_manifest_sha256": v4["successor_manifest_sha256"],
                         "v4_started_at_utc": v4["started_at_utc"],
                         "v5_completed_at_utc": v5["completed_at_utc"],
                         "observed_case_windows_before_source_expiry": True},
        "observed_lease_phase": {"v4_positive_case_exit_snapshots": 68,
                                 "reader_policy_expiries": 68, "reader_context_expiries": 0,
                                 "context_delivery_expiries": 56, "session_expiries": 2,
                                 "v5_lease_capture": "not_instrumented"},
        "session_expiry_timers": [{"test_id": r["test_id"],
                                   "session_expires_at": r["observed_lease_expiries"]["session"],
                                   "case_started_at_utc": r["started_at_utc"],
                                   "case_completed_at_utc": r["completed_at_utc"],
                                   "case_monotonic_elapsed_seconds": r["monotonic_elapsed_seconds"]}
                                  for r in timer_rows],
        "case_rows": rows,
        "case_counts": {"v4_pass": 68, "v4_next_fail": 1, "v5_pass": 17,
                        "v5_setup_errors": 1, "positive_total": 85, "selected_total": 99},
        "expiry_refusal": {"v4_case69": "FAIL: historical environment mismatch; not proof of expiry refusal",
                           "v4_case69_monotonic_seconds": v4["case_rows"][68]["monotonic_elapsed_seconds"],
                           "v5_case1": "PASS: historical constructor environment refusal plus separate expired Assignment policy guard with source preflight disabled",
                           "v5_case1_monotonic_seconds": v5["case_rows"][0]["monotonic_elapsed_seconds"],
                           "historical_absolute_assignment_expires_at": period["expires_at"],
                           "v5_ended_on": "MachineTransport setUpClass NameError PROFILE; no Machine case result"},
        "claim_ceiling": "Posthoc public case windows and exit deadline snapshots from frozen T02 v4/v5. No internal Source/Reader/Context/Session phase durations, private callback counts, positive expired-original use, 99-case pass, or original T35 completion.",
        "runner_sha256": digest(Path(__file__).read_bytes()),
    }


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
