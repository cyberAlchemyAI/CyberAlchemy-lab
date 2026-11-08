"""Exercise the current legacy API33 SQL projection and canonical parity."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
import time

from run_successor import OUTPUT, digest, package_at


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    script = Path(__file__).resolve()
    script_sha = digest(script)
    manifest_sha = digest(OUTPUT / "source-manifest.json")
    module = importlib.import_module(package_at(OUTPUT) + ".test_custody_sessions")
    module.PROFILE = digest(OUTPUT / "contract-profile.json")
    cls = module.Sessions
    case = cls("test_00_all_eleven_actual_operations")
    report = {"result": "FAIL", "started_at_utc": now(),
              "script_sha256": script_sha, "source_manifest_sha256": manifest_sha,
              "phases": []}

    def phase(label, fn):
        started = now()
        monotonic = time.monotonic()
        try:
            return fn()
        finally:
            row = {"name": label, "started_at_utc": started,
                   "completed_at_utc": now(),
                   "elapsed_seconds": round(time.monotonic() - monotonic, 3)}
            report["phases"].append(row)
            print("PHASE", label, row["elapsed_seconds"], flush=True)

    try:
        phase("setUpClass", cls.setUpClass)
        phase("setUp", case.setUp)
        call = module.call(case.channel.context, "artifact.query", module.cut(case.view))
        call["message"]["query_basis"] = "projection"
        reply = phase("artifact.query", lambda: case.service.call(module.compact(call)))
        report["reply_kind"] = reply.get("kind")
        report["reply_code"] = reply.get("message", {}).get("code") if reply.get("kind") != "result" else None
        if reply.get("kind") == "result":
            message = reply["message"]
            gaps = [row for row in message["gaps"] if row["blocking_use"] == "artifact-representation-unavailable"]
            expected = set(importlib.import_module(package_at(OUTPUT) + ".native_dispositions").EXCLUDED)
            found = {row["subject_ref"] for row in gaps}
            report.update({"basis": message["query_basis"], "result_count": len(message["results"]),
                           "connection_count": len(message["connections"]),
                           "explicit_native_gap_count": len(gaps),
                           "exact_native_gaps": found == expected,
                           "result": "PASS" if found == expected and len(gaps) == 8
                           and message["query_basis"] == "projection"
                           and message["projection_generation"] is not None else "FAIL"})
    except BaseException as error:
        report["exception_type"] = type(error).__name__
        raise
    finally:
        if hasattr(case, "service"):
            phase("tearDown", case.tearDown)
        case.doCleanups()
        cls.doClassCleanups()
        report["completed_at_utc"] = now()
        report["script_unchanged_during_run"] = digest(script) == script_sha
        report["source_unchanged_during_run"] = digest(OUTPUT / "source-manifest.json") == manifest_sha
        out = script.parent / "working" / "probe-projection-positive-result.json"
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print("RESULT", report["result"], flush=True)
    return report


if __name__ == "__main__":
    raise SystemExit(0 if main()["result"] == "PASS" else 1)
