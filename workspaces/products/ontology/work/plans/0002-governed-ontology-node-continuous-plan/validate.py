#!/usr/bin/env python3
"""Validate the plan graph, source bindings, generated views, and claim ceiling."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import render


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "continuous-plan.json"
RECEIPT = ROOT / "receipts" / "plan-validation.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    plan = json.loads(SOURCE.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def record(check_id: str, passed: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    record("schema-version", plan.get("schema_version") == "cal.continuous-plan-candidate/v1", plan.get("schema_version"))
    record(
        "authority-ceiling",
        plan.get("execution_authority") == "none"
        and plan.get("execution_entry", {}).get("task_session_allowed") is False
        and plan.get("execution_entry", {}).get("next_route") == "decision-gate",
        plan.get("execution_entry"),
    )

    source_results = []
    for source in plan.get("source_refs", []):
        path = Path(source["path"])
        current = path.is_file() and digest(path) == source["sha256"] and path.stat().st_size == source["size"]
        source_results.append({"id": source["id"], "current": current})
    record("source-currentness", bool(source_results) and all(item["current"] for item in source_results), source_results)

    layers = plan.get("layers", [])
    waves = plan.get("waves", [])
    wave_ids = [wave["id"] for wave in waves]
    layer_ids = {layer["id"] for layer in layers}
    validation_ids = [validation["id"] for validation in plan.get("validations", [])]
    record("unique-wave-ids", len(wave_ids) == len(set(wave_ids)) == 9, wave_ids)
    record("unique-validation-ids", len(validation_ids) == len(set(validation_ids)), validation_ids)
    record("layer-closure", all(wave["layer"] in layer_ids for wave in waves), sorted(layer_ids))

    earlier: set[str] = set()
    ordered = True
    for wave in waves:
        if not set(wave.get("depends_on", [])) <= earlier:
            ordered = False
        earlier.add(wave["id"])
    record("wave-topology", ordered and wave_ids == [f"W{i}" for i in range(9)], wave_ids)

    swu_ids: list[str] = []
    swu_validations_close = True
    swu_shape = True
    for wave in waves:
        if not wave.get("swus") or not wave.get("gate", {}).get("pass_condition"):
            swu_shape = False
        for swu in wave.get("swus", []):
            swu_ids.append(swu.get("id", ""))
            if not swu.get("primary_behavior") or not swu.get("owner") or not swu.get("write_scope") or not swu.get("done_criteria") or not swu.get("split_analysis"):
                swu_shape = False
            if not set(swu.get("validation_ids", [])) <= set(validation_ids):
                swu_validations_close = False
    record("swu-shape", swu_shape and len(swu_ids) == len(set(swu_ids)), swu_ids)
    record("swu-validation-closure", swu_validations_close, {"validations": validation_ids})

    final = plan.get("final_validation", {})
    w8 = waves[-1] if waves else {}
    required = set(final.get("required_validation_ids", []))
    record(
        "terminal-aggregate",
        final.get("wave_id") == "W8"
        and final.get("requires_all_prior_waves") is True
        and final.get("collect_all") is True
        and set(w8.get("swus", [{}])[0].get("validation_ids", [])) == required == set(validation_ids)
        and final.get("result_authority_ceiling") == "validated implementation candidate only",
        {"wave": final.get("wave_id"), "required_count": len(required), "authority": final.get("result_authority_ceiling")},
    )

    w7 = next((wave for wave in waves if wave["id"] == "W7"), {})
    record(
        "migration-boundary",
        w7.get("status") == "conditional-pending-accepted-W6-candidate"
        and w7.get("depends_on") == ["W6"]
        and "accepted" in w7.get("gate", {}).get("pass_condition", "").lower()
        and any("cutover" in item.lower() for item in plan.get("scope", {}).get("excluded", [])),
        {"status": w7.get("status"), "depends_on": w7.get("depends_on")},
    )

    rendered_results = []
    for name, expected in render.rendered(plan).items():
        path = ROOT / name
        matches = path.is_file() and path.read_text(encoding="utf-8") == expected
        rendered_results.append({"path": name, "current": matches})
    record("generated-view-currentness", all(item["current"] for item in rendered_results), rendered_results)

    dispatch = json.loads((ROOT / "dispatch.json").read_text(encoding="utf-8"))
    distill = json.loads((ROOT / "distill-validation.json").read_text(encoding="utf-8"))
    record(
        "planning-companion-closure",
        dispatch.get("dispatch_id") == "CAL-DISPATCH-PLAN-0002"
        and dispatch.get("subagent_strategy", {}).get("authorization") == "blocked"
        and distill.get("verdict", {}).get("plan_coherence") == "pass_candidate"
        and distill.get("verdict", {}).get("execution_readiness") == "block",
        {"dispatch": dispatch.get("dispatch_id"), "distill_verdict": distill.get("verdict")},
    )
    dispatch_validator = Path("/home/vrondelli/projects/domainspec-core/.agents/skills/dispatch-spec/scripts/validate-dispatch.py")
    dispatch_result = subprocess.run(
        ["python3", str(dispatch_validator), "dispatch.json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    record(
        "dispatch-spec-validation",
        dispatch_result.returncode == 0 and "VALIDATION=pass" in dispatch_result.stdout,
        dispatch_result.stdout.strip().splitlines(),
    )

    passed = all(check["result"] == "PASS" for check in checks)
    receipt = {
        "schema_version": "cal.plan-validation-receipt/v1",
        "plan_id": plan.get("plan_id"),
        "result": "PASS" if passed else "BLOCK",
        "validated_sha256": digest(SOURCE),
        "checks": checks,
        "claim_ceiling": "This receipt validates plan coherence, source currentness, and generated-view parity only. It grants no execution, admission, acceptance, publication, deployment, or cutover authority."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PLAN_VALIDATION={receipt['result']}")
    for check in checks:
        print(f"{check['check_id']}={check['result']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
