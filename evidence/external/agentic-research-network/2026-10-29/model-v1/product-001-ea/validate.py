"""Check EA source pins, whole-model coverage and stored synthetic results."""

import json
from pathlib import Path

from build_model import ROOT, TASK_SPECS, reports
from integrated_scenario import report as integrated_report
from lead_loop import report as lead_report


def check() -> None:
    expected = reports()
    for name, value in expected.items():
        stored = json.loads((ROOT / name).read_text())
        if stored != value:
            raise SystemExit(f"FAIL EA whole model: stale or altered {name}")
    manifest = expected["source-manifest.json"]
    cross = expected["crosswalk.json"]
    catalog = expected["task-catalog.json"]
    counts = (len(cross["goals"]), len(cross["capabilities"]),
              len(cross["inquiries"]), len(cross["experiment_designs"]))
    if counts != (6, 7, 10, 15):
        raise SystemExit(f"FAIL EA whole model: source coverage {counts}")
    if len(manifest["files"]) != 88 or cross["relation_proposal_count"] != 124:
        raise SystemExit("FAIL EA whole model: source cut or relation count changed")
    if len(cross["roles"]) != 27:
        raise SystemExit("FAIL EA whole model: role inventory changed")
    if len(catalog["tasks"]) != len(TASK_SPECS):
        raise SystemExit("FAIL EA whole model: task coverage changed")
    design_refs = {row["experiment_ref"] for row in cross["experiment_designs"]}
    task_refs = {task["experiment_ref"] for task in catalog["tasks"]}
    if design_refs != task_refs:
        raise SystemExit("FAIL EA whole model: task/design mismatch")
    if any(task["offer_state"] != "no-task-offer" or
           task["result_state"] != "no-ARN-run-or-finding"
           for task in catalog["tasks"]):
        raise SystemExit("FAIL EA whole model: catalog claims an effect")
    if any(row["lab_link_state"] != "candidate-unapplied"
           for row in cross["experiment_designs"]):
        raise SystemExit("FAIL EA whole model: crosswalk claims applied relation")
    saved_result = json.loads((ROOT / "fixtures/integrated-results.json").read_text())
    if saved_result != integrated_report():
        raise SystemExit("FAIL EA whole model: stale integrated scenario")
    lead_proposal = json.loads((ROOT / "lead-platform-proposal.json").read_text())
    if (lead_proposal["status"] != "candidate-unadmitted" or
        lead_proposal["authority_effect"] != "none" or
        lead_proposal["branch_state"] != "disabled-in-ea-mvp" or
        len(lead_proposal["channels"]) != 4 or
        set(lead_proposal["reward_classes"]) != {"E", "W", "U", "F"}):
        raise SystemExit("FAIL EA whole model: lead branch claims authority or loses a channel/reward boundary")
    saved_lead = json.loads((ROOT / "fixtures/lead-loop-results.json").read_text())
    if saved_lead != lead_report():
        raise SystemExit("FAIL EA whole model: stale lead cohort scenario")
    visibility = json.loads((ROOT / "visibility-service-proposal.json").read_text())
    if (visibility["status"] != "candidate-unadmitted" or
        visibility["authority_effect"] != "none" or
        visibility["service_state"] != "disabled" or
        visibility["organic_rank_effect"] != "none" or
        visibility["assessment_score_effect"] != "none" or
        visibility["buyer_data_access_effect"] != "none" or
        visibility["price_w_units"] is not None):
        raise SystemExit("FAIL EA whole model: visibility service claims an operative or assessment effect")
    print(f"PASS EA source cut: {len(manifest['files'])} exact files; {manifest['source_cut_sha256']}")
    print("PASS EA crosswalk: 6 goals, 7 capabilities, 10 inquiries, 15 designs, 27 roles; 124 candidate relation proposals")
    print(f"PASS EA task catalog: {len(catalog['tasks'])} candidate families; no task offers or results")
    print(f"PASS EA integration: {len(saved_result['cases'])} synthetic research-to-payout cases match the runner")
    print(f"PASS EA lead branch: {len(saved_lead['cases'])} synthetic cohort cases; disabled in EA MVP")
    print("PASS EA W visibility: candidate disabled service; no organic, assessment or buyer-access effect")


if __name__ == "__main__":
    check()
