#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_chain(data: dict) -> str:
    plan = data["work_plan"]
    product = plan["product_construction"]
    lines = [
        "<!-- GENERATED FILE: edit chain.json and run build.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Planning candidate only. Prototype construction is non-authoritative; product approval grants no operational authority.",
        "",
        f"- Chain: `{data['chain_id']}`",
        f"- Status: `{data['status']}`",
        f"- Predecessor disposition: `{data['predecessor_chain']['disposition']}`",
        f"- Current product frontier: `{product['current_product_frontier']}`",
        f"- Continuation: `{product['continuation_status']}`",
        "",
        "## Outcome",
        "",
        data["objective"],
        "",
        "## Construction invariant",
        "",
    ]
    lines += [f"{index + 1}. `{item}`" for index, item in enumerate(data["construction_invariant"]["order"])]
    lines += ["", data["construction_invariant"]["prototype_rule"], "", "## Product-construction sequence", ""]
    for stage in data["stages"]:
        lines += [
            f"### {stage['stage_id']}",
            "",
            f"State: `{stage['state']}`  ",
            f"Authority effect: `{stage['authority_effect']}`",
            "",
            stage["decision_question"],
            "",
            "Included:",
            "",
        ]
        lines += [f"- {item}" for item in stage["included"]]
        lines += ["", "Outputs:", ""]
        lines += [f"- `{item}`" for item in stage["outputs"]]
        lines += ["", "Exit evidence:", ""]
        lines += [f"- {item}" for item in stage["exit_evidence"]]
        lines += ["", f"Promotion: {stage['promotion_effect']}", ""]
    lines += ["## Runnable now", ""]
    for task in product["runnable_now"]:
        lines.append(f"- `{task['task_id']}` — {task['scope']}")
    lines += ["", "## Future construction prerequisites", ""]
    for item in product["future_frontier_prerequisites"]:
        lines.append(f"- `{item['prerequisite_id']}` → `{item['applies_to_stage']}` — {item['detail']}")
    lines += ["", "## Operational support residue", ""]
    for task in plan["operational_support"]:
        applies = task["applies_to_stage"] or "no product stage"
        lines.append(f"- `{task['task_id']}` — `{task['state']}`; owner `{task['owner_route']}`; applies to `{applies}`; {task['detail']}")
    checkpoint = data["product_approval_checkpoint"]
    lines += [
        "",
        "## Single product-approval checkpoint",
        "",
        f"`{checkpoint['checkpoint_id']}` is eligible only after `{checkpoint['eligible_only_after_stage']}`. Approval effect is `{checkpoint['effect_if_approved']}`.",
        "",
        "The checkpoint may not contain:",
        "",
    ]
    lines += [f"- {item}" for item in checkpoint["prohibited_members"]]
    lines += ["", "## Recommended next unit", "", f"`{data['recommended_next_unit']['unit_id']}` — {data['recommended_next_unit']['scope']}", "", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def render_layering(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit chain.json and run build.py. -->",
        "",
        "# Craft First Product Candidate Implementation Layering",
        "",
        "> Five layers from the minimum thin vertical to one product-approval-only decision.",
        "",
        "| Layer | Theme | Decision unlocked |",
        "| --- | --- | --- |",
    ]
    for layer in data["layers"]:
        decision = layer["decision_question"].removeprefix("After this layer, we know whether ").rstrip(".")
        lines.append(f"| `{layer['layer_id']}` | {layer['theme']} | {decision} |")
    for layer in data["layers"]:
        lines += [
            "",
            f"## {layer['layer_id']} — {layer['theme']}",
            "",
            layer["decision_question"],
            "",
            f"- Minimum working unit: {layer['minimum_working_unit']}",
            f"- Included: {layer['included_scope']}",
            f"- Deferred: {layer['deferred_scope']}",
            f"- Visible outcome: {layer['visible_outcome']}",
            f"- Risk reduced: {layer['risk_reduced']}",
            f"- Main cost drivers: {layer['main_cost_drivers']}",
            f"- Exit evidence: {layer['exit_evidence']}",
            f"- Promotion: {layer['promotion_decision']}",
            f"- Non-regression: {layer['non_regression_guarantee']}",
            f"- Next: {layer['next_layer']}",
        ]
    lines += [
        "",
        "## Boundary",
        "",
        "L4 ends product construction with one product-approval-only decision. Every authority, admission, activation, cutover, migration, publication, release, deployment, credential, destructive, or external effect belongs to a later separately routed workflow.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    data = load(ROOT / "chain.json")
    (ROOT / "CHAIN.md").write_text(render_chain(data), encoding="utf-8")
    (ROOT / "IMPLEMENTATION-LAYERING.md").write_text(render_layering(data), encoding="utf-8")

    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    predecessor = data["predecessor_chain"]
    predecessor_receipt = load(LAB / predecessor["validation_receipt_path"])
    check(
        "predecessor-byte-preserved",
        sha(LAB / predecessor["path"]) == predecessor["sha256"]
        and sha(LAB / predecessor["validation_receipt_path"]) == predecessor["validation_receipt_sha256"]
        and predecessor_receipt.get("result") == "PASS",
        {"chain": predecessor["sha256"], "receipt_result": predecessor_receipt.get("result")},
    )
    check(
        "predecessor-supersession-explicit",
        predecessor["disposition"] == "preserved-historical-candidate-superseded-for-current-construction"
        and len(predecessor["superseded"]) >= 4,
        predecessor,
    )

    planning = data["planning_basis"]
    check("planning-basis-current", sha(LAB / planning["path"]) == planning["sha256"], planning)

    binding = data["prototype_contract_binding"]
    source_root = Path(binding["repository"])
    bound_files = {
        "construction_registry": (binding["construction_registry_path"], binding["construction_registry_sha256"]),
        "scaffold_registry": (binding["ontology_scaffold_registry_path"], binding["ontology_scaffold_registry_sha256"]),
        "construction_bindings": (binding["construction_binding_registry_path"], binding["construction_binding_registry_sha256"]),
        "prototype_amendment": (binding["prototype_amendment_path"], binding["prototype_amendment_sha256"]),
        "two_lane_amendment": (binding["two_lane_amendment_path"], binding["two_lane_amendment_sha256"]),
    }
    bound_results = {name: sha(source_root / path) == digest for name, (path, digest) in bound_files.items()}
    check("prototype-contract-files-current", all(bound_results.values()), bound_results)

    construction_registry = load(source_root / binding["construction_registry_path"])
    construction = next((item for item in construction_registry.get("constructions", []) if item.get("construction_id") == binding["construction_ref"]), None)
    check(
        "tested-prototype-contract-selected",
        construction is not None
        and construction.get("state") == "tested"
        and construction.get("authority_effect") == "none"
        and construction.get("testable_product_candidate", {}).get("manifest_sha256") == binding["tested_contract_candidate_manifest_sha256"],
        construction or "missing",
    )
    scaffold_registry = load(source_root / binding["ontology_scaffold_registry_path"])
    scaffold = next((item for item in scaffold_registry.get("scaffolds", []) if item.get("scaffold_id") == binding["ontology_scaffold_ref"]), None)
    check(
        "ontology-scaffold-non-authoritative",
        scaffold is not None
        and scaffold.get("canonicality") == "non-authoritative"
        and scaffold.get("lifecycle_posture") == "prototype-scaffold"
        and scaffold.get("authority_effect") == "none",
        scaffold or "missing",
    )

    expected_order = [
        "definition_prototypes",
        "ontology_scaffolds",
        "product_capability_prototype",
        "business_ontology_prototype",
        "domainspec_source_prototype",
        "compiled_graph_prototype",
        "system_ontology_prototype",
        "implementation_prototype",
        "testable_product_candidate",
        "product_test_evidence",
        "product_approval",
    ]
    check("current-d65-order-exact", data["construction_invariant"]["order"] == expected_order, data["construction_invariant"]["order"])

    stages = data["stages"]
    stage_ids = [stage["stage_id"] for stage in stages]
    seen: set[str] = set()
    topology_ok = True
    for stage in stages:
        topology_ok = topology_ok and set(stage["depends_on"]) <= seen
        seen.add(stage["stage_id"])
    check("stage-order-topological", topology_ok and len(stage_ids) == len(set(stage_ids)), stage_ids)
    check("product-construction-lane-only", all(stage["lane"] == "product-construction" for stage in stages), [stage["lane"] for stage in stages])
    check("stage-decision-questions-explicit", all(stage["decision_question"].startswith("After this stage, we know whether") for stage in stages), [stage["decision_question"] for stage in stages])
    check(
        "preapproval-zero-authority",
        all(stage["authority_effect"] == "none" for stage in stages[:-1])
        and stages[-1]["authority_effect"] == "product-approval-only",
        [{"stage": stage["stage_id"], "effect": stage["authority_effect"]} for stage in stages],
    )
    check(
        "product-approval-after-current-tests",
        stages[-1]["construction_state"] == "product_approval"
        and stages[-1]["depends_on"] == ["CML12-P5-COLLECT-CURRENT-PRODUCT-TEST-EVIDENCE"],
        stages[-1],
    )

    outputs = [output for stage in stages for output in stage["outputs"]]
    check("output-surfaces-unique", len(outputs) == len(set(outputs)), outputs)
    check(
        "prototype-root-does-not-imply-final-placement",
        "not pre-decide final context" in data["prototype_root"]["final_placement_posture"].lower()
        and "frozen product candidate manifest" in data["prototype_root"]["final_placement_posture"].lower(),
        data["prototype_root"],
    )

    required_layer_fields = {
        "decision_question",
        "minimum_working_unit",
        "included_scope",
        "deferred_scope",
        "visible_outcome",
        "risk_reduced",
        "main_cost_drivers",
        "exit_evidence",
        "promotion_decision",
        "non_regression_guarantee",
        "next_layer",
    }
    layers = data["layers"]
    check(
        "five-layer-contract-complete",
        len(layers) == 5
        and all(required_layer_fields <= set(layer) and set(layer["stages"]) <= set(stage_ids) for layer in layers),
        [layer["layer_id"] for layer in layers],
    )
    check("layer-questions-explicit", all(layer["decision_question"].startswith("After this layer, we know whether") for layer in layers), [layer["decision_question"] for layer in layers])
    check(
        "layer-zero-is-end-to-end-minimum-proof",
        "smallest Product Capability-to-implementation slice" in layers[0]["minimum_working_unit"],
        layers[0]["minimum_working_unit"],
    )

    plan = data["work_plan"]
    product = plan["product_construction"]
    check(
        "current-frontier-runnable",
        product["current_product_frontier"] == "definition_prototypes"
        and product["continuation_status"] == "runnable"
        and len(product["runnable_now"]) >= 1
        and product["current_causal_blockers"] == [],
        product,
    )
    current_frontier_stage = product["runnable_now"][0]["stage_id"]
    current_blocking_ops = [
        task
        for task in plan["operational_support"]
        if task["applies_to_stage"] == current_frontier_stage and task["blocking_basis"] != "none"
    ]
    check("operational-support-does-not-hide-frontier", not current_blocking_ops, current_blocking_ops)
    check(
        "operational-support-typed",
        all(
            task["lane"] == "operational-support"
            and "owner_route" in task
            and "applies_to_stage" in task
            and "blocking_basis" in task
            for task in plan["operational_support"]
        ),
        plan["operational_support"],
    )
    check(
        "future-prerequisites-do-not-block-current-frontier",
        all(item["applies_to_stage"] != current_frontier_stage for item in product["future_frontier_prerequisites"]),
        product["future_frontier_prerequisites"],
    )

    checkpoint = data["product_approval_checkpoint"]
    check(
        "single-product-approval-only-checkpoint",
        checkpoint["decision_mode"] == "single"
        and checkpoint["effect_if_approved"] == "product-approval-only"
        and checkpoint["authority_request_eligibility_before_approval"] == "not_eligible"
        and checkpoint["authority_request_refs"] == [],
        checkpoint,
    )
    prohibited = " ".join(checkpoint["prohibited_members"]).lower()
    check(
        "operational-effects-excluded-from-approval",
        all(term in prohibited for term in ("authority", "admission", "activation", "cutover", "publication", "release", "deployment")),
        checkpoint["prohibited_members"],
    )

    check(
        "canonical-generated-direction-explicit",
        data["source_direction"]["canonical"] == "chain.json"
        and data["source_direction"]["projection_policy"] == "generated-only",
        data["source_direction"],
    )
    chain_projection = render_chain(data)
    layering_projection = render_layering(data)
    check("chain-projection-parity", (ROOT / "CHAIN.md").read_text(encoding="utf-8") == chain_projection, sha(ROOT / "CHAIN.md"))
    check("layering-projection-parity", (ROOT / "IMPLEMENTATION-LAYERING.md").read_text(encoding="utf-8") == layering_projection, sha(ROOT / "IMPLEMENTATION-LAYERING.md"))

    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-construction-chain-validation/v2",
        "subject": data["chain_id"],
        "result": "PASS" if not failed else "FAIL",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {
            "chain_sha256": sha(ROOT / "chain.json"),
            "chain_projection_sha256": sha(ROOT / "CHAIN.md"),
            "layering_projection_sha256": sha(ROOT / "IMPLEMENTATION-LAYERING.md"),
        },
        "current_product_frontier": product["current_product_frontier"],
        "runnable_product_work": product["runnable_now"],
        "operational_support": plan["operational_support"],
        "causal_construction_blockers": product["current_causal_blockers"],
        "deferred_operational_residue": [task for task in plan["operational_support"] if task["state"] != "complete"],
        "recommended_next_unit": data["recommended_next_unit"],
        "claim_ceiling": "PASS proves only that the successor planning candidate preserves its predecessor, binds the current tested prototype-navigation contract, follows the prototype-to-tested-product D65 order, exposes a runnable product frontier and separate operational residue, reproduces its projections, and excludes every operational effect from product approval. It does not execute, test, freeze, or approve the product and grants no authority.",
    }
    receipt_path = ROOT / "receipts/validation.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CRAFT_PRODUCT_CANDIDATE_CHAIN={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"CURRENT_FRONTIER={receipt['current_product_frontier']}")
    print(f"CHAIN_SHA256={receipt['materials']['chain_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
