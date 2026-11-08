"""Seal N00 evidence without changing the frozen successor proposal."""
import json
from pathlib import Path

from verify_n00 import HERE, ROOT, binding


def check(b):
    assert binding(ROOT / b["path"]) == b, b["path"]


def main():
    out = HERE / "execution/n00"
    report = json.loads((out / "verification.json").read_text())
    assert report["result"] == "pass"
    assert report["inherited_discharges"] == 0
    assert len(report["records"]) == 10
    for key in ["compiler", "kernel_library", "toolchain_lock", "driver", "inherited_inventory"]:
        check(report[key])
    for b in report["sources"]:
        check(b)
    for rec in report["records"]:
        assert rec["exit_code"] == 0
        assert set(rec["axioms"]) <= set(report["allowed_axioms"])
        for key in ["source", "log", "olean"]:
            check(rec[key])
    context_path = out / "context-pack.json"
    context = json.loads(context_path.read_text())
    assert context["strict_coverage"] == "pass"
    for src in context["sources"]:
        check(src["binding"])
    plan_path = HERE / "execution/plan.json"
    plan = json.loads(plan_path.read_text())
    check(plan["source_plan"])
    task = next(t for t in plan["tasks"] if t["id"] == "N00")
    assert task["depends_on"] == []
    refresh = HERE / "execution/review-current.json"
    refresh_data = json.loads(refresh.read_text())
    assert refresh_data["result"] == "pass" and refresh_data["inherited_pending"] == 263
    receipt = {
        "schema": "relational.successor-task-acceptance/v1", "task": "N00", "result": "accepted",
        "source_plan": plan["source_plan"], "context": binding(context_path),
        "evidence": [binding(out / "verification.json"), binding(HERE / "formal-contract.md"),
                     binding(HERE / "trust-premise-register.json"), binding(refresh)],
        "criteria": [
            {"source": task["exit_criteria"][0], "result": "pass",
             "basis": "33 common universal theorems pass fresh pinned compilation and separate replay; every theorem's axioms inspected."},
            {"source": task["exit_criteria"][1], "result": "pass",
             "basis": "12 synthetic witnesses include legitimate owned condition, complete two-criterion fulfillment, AST replacement, criterion omission and unsupported caller yes."}
        ],
        "source_inventory": {"count": 263, "new_discharges": 0,
                             "note": "Exact string IDs are audited independently; listing/count/conditional full-coverage theorems are not semantic discharges."},
        "actual_owner_assessment": "not established; required by N01",
        "authority_effect": "none"
    }
    receipt_path = out / "acceptance.json"
    if receipt_path.exists():
        assert json.loads(receipt_path.read_text()) == receipt, "accepted receipt is immutable"
    else:
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    task["status"] = "accepted"
    task["acceptance"] = binding(receipt_path)
    plan["status"] = "executing"
    plan_path.write_text(json.dumps(plan, indent=2) + "\n")
    (HERE / "execution/PROGRESS.md").write_text(
        "N00 accepted: 33 common universal theorems, 12 synthetic witnesses and two inventory theorems "
        "pass fresh pinned Lean compilation and separate replay.\n\n"
        "Successor completion: 1/20 tasks. Inherited semantic discharges: 0/263. "
        "All seven extension families, 41 relation kinds and 550 ordered endpoint pairs remain in scope.\n\n"
        "Next ready task: N01, concrete definitions and actual exact owner meaning assessment. "
        "Prior original R06/G4 acceptance stays in its original scope. Full successor goal remains active.\n")
    print("N00 accepted; 1/20 successor tasks; 0/263 inherited semantic discharges")


if __name__ == "__main__":
    main()
