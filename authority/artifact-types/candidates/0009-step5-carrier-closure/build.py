#!/usr/bin/env python3
"""Build the complete Step 5 Artifact Type carrier closure plan."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


SUCCESSOR_TARGETS = {
    "cal.artifact-type.artifact-type/v2": "cal.artifact-type.artifact-type/v3",
    "cal.artifact-type.bounded-context/v2": "cal.artifact-type.bounded-context/v3",
    "cal.artifact-type.capability-instance/v1": "cal.artifact-type.capability-instance/v2",
    "cal.artifact-type.capability-realization-binding/v1": "cal.artifact-type.capability-realization-binding/v2",
    "cal.artifact-type.context-lineage-record/v1": "cal.artifact-type.context-lineage-record/v2",
    "cal.artifact-type.context-map/v2": "cal.artifact-type.context-map/v3",
    "cal.artifact-type.context-migration-manifest/v1": "cal.artifact-type.context-migration-manifest/v2",
    "cal.artifact-type.definition/v1": "cal.artifact-type.definition/v2",
    "cal.artifact-type.ubiquitous-language/v1": "cal.artifact-type.ubiquitous-language/v2",
}

REBIND_TARGETS = {
    "cal.artifact-type.context-profile/v1": ["cal.definition.context-profile@1.0.0-candidate.1"],
    "cal.artifact-type.measurement-method/v1": ["cal.definition.measurement-method@1.0.0-candidate.1"],
    "cal.artifact-type.measurement-result/v1": ["cal.definition.measurement-result@1.0.0-candidate.1"],
    "cal.artifact-type.model-instance-binding/v1": ["cal.definition.model-instance-binding@1.0.0-candidate.1"],
    "cal.artifact-type.ontology-package/v1": [
        "cal.definition.ontology@1.0.0-candidate.1",
        "cal.definition.generated-output@1.0.0-candidate.1",
    ],
}

DISTINCTIONS = {
    "authority-claim": ["identity-claim", "role-assignment"],
    "constitution": ["policy", "contract"],
    "contract": ["challenge-contract", "policy"],
    "decision": ["decision-checkpoint", "effect"],
    "decision-scope": ["decision", "authority-claim"],
    "effect": ["decision", "execution"],
    "evaluation": ["measurement-result", "review"],
    "evidence-set": ["finding", "observation"],
    "generated-output": ["source", "evidence-set"],
    "governed-model": ["ontology", "schema"],
    "hypothesis": ["product-thesis", "premise"],
    "implementation": ["capability-realization-binding", "schema"],
    "ontology-node": ["ontology", "typed-relation"],
    "person": ["person-reference", "agent"],
    "policy": ["constitution", "contract"],
    "relation-kind": ["typed-relation", "schema"],
    "responsibility": ["role", "role-assignment"],
    "review": ["evaluation", "finding"],
    "schema": ["artifact-type", "contract"],
    "source": ["evidence-set", "generated-output"],
    "typed-relation": ["relation-kind", "ontology-node"],
    "work": ["project", "goal"],
}

EXAMPLES = [
    {
        "example_id": "STEP5-EX-01-PERSON-REFERENCE",
        "explanation": "A durable Person Reference asserts identity of a Person; the reference record and the human being remain different carriers.",
        "relation": {"relation_kind_ref": "relation.asserts-identity-of", "source_kind": "person-reference", "source_ref": "person-reference:vrondelli", "target_kind": "person", "target_ref": "person:vrondelli"},
    },
    {
        "example_id": "STEP5-EX-02-IMPLEMENTATION",
        "explanation": "One executable implementation realizes a Product Capability; the Capability Realization Binding separately records the governed connection and evidence posture.",
        "relation": {"relation_kind_ref": "relation.realizes", "source_kind": "implementation", "source_ref": "implementation:registry-validator@beb873", "target_kind": "product-capability", "target_ref": "product-capability:effective-state-resolution"},
    },
    {
        "example_id": "STEP5-EX-03-HYPOTHESIS-EVIDENCE",
        "explanation": "An Evidence Set bears on one falsifiable Hypothesis without becoming the Hypothesis or deciding its truth.",
        "relation": {"relation_kind_ref": "relation.evidence-bears-on", "source_kind": "evidence-set", "source_ref": "evidence-set:registry-determinism", "target_kind": "hypothesis", "target_ref": "hypothesis:registry-build-is-deterministic"},
    },
    {
        "example_id": "STEP5-EX-04-DECISION-EFFECT",
        "explanation": "A Decision declares an Effect on a Relation Kind; the declaration and the effect remain explicit endpoints.",
        "relation": {"relation_kind_ref": "relation.declares-effect-on", "source_kind": "decision", "source_ref": "decision:relation-kind-admission", "target_kind": "relation-kind", "target_ref": "relation-kind:member-of"},
    },
    {
        "example_id": "STEP5-EX-05-ONTOLOGY-MEMBERSHIP",
        "explanation": "A Typed Relation is a member of an Ontology, while its Relation Kind remains the reusable predicate contract.",
        "relation": {"relation_kind_ref": "relation.member-of", "source_kind": "typed-relation", "source_ref": "typed-relation:implementation-realizes-capability:001", "target_kind": "ontology", "target_ref": "ontology:lab-integrated-model"},
    },
    {
        "example_id": "STEP5-EX-06-WORK-PROJECT",
        "explanation": "A bounded Work record is a member of a Project; the Project coordinates many Work records and persists beyond any one of them.",
        "relation": {"relation_kind_ref": "relation.member-of", "source_kind": "work", "source_ref": "work:materialize-carrier-closure", "target_kind": "project", "target_ref": "project:lab-semantic-governance"},
    },
]


def build() -> dict:
    candidate = load(ROOT / "candidate.json")
    inputs = candidate["inputs"]
    audit = load(LAB / inputs["content_audit"]["path"])
    definition_registry = load(LAB / inputs["definition_registry"]["path"])
    endpoint_inventory = load(LAB / inputs["endpoint_inventory"]["path"])
    relation_model = load(LAB / inputs["relation_model"]["path"])

    current_by_ref = {
        f"{entry['definition_id']}@{entry['version']}": entry
        for entry in definition_registry["entries"]
        if entry["lifecycle_state"] == "admitted"
        and definition_registry["current_lookup"].get(entry["definition_id"]) == f"{entry['definition_id']}@{entry['version']}"
    }
    actionable = [
        entry for entry in audit["entries"]
        if entry["content_posture"] in {"admitted-current-remediation-required", "candidate-revision-required"}
    ]
    existing_actions = []
    for entry in actionable:
        ref = entry["artifact_type_ref"]
        issue_codes = [issue["code"] for issue in entry["issues"]]
        if ref in SUCCESSOR_TARGETS:
            action = {
                "action": "author-immutable-successor",
                "source_artifact_type_ref": ref,
                "target_artifact_type_ref": SUCCESSOR_TARGETS[ref],
                "required_changes": [
                    "preserve admitted predecessor bytes and lifecycle evidence",
                    "add all integrated Artifact Type/v2 contract sections",
                    "bind exact current admitted semantic Definitions",
                    "declare explicit candidate Relation Kind surface without admitting relations",
                    "validate positive, negative, hostile non-collapse, and deterministic projection cases",
                ],
            }
            if "validation-evidence-not-pass" in issue_codes:
                action["required_changes"].insert(1, "refresh predecessor validation evidence against unchanged admitted bytes")
            if ref == "cal.artifact-type.capability-realization-binding/v1":
                action["required_changes"] = [
                    "preserve v1 as admitted historical only after v2 admission",
                    "replace the Product Capability primary binding with cal.definition.capability-realization-binding@1.0.0-candidate.1",
                    "retain Product Capability as a referenced endpoint, not the carrier's semantic identity",
                    "validate one binding per exact capability realization and preserve lifecycle, evidence, owner, and challenge route",
                ]
        else:
            action = {
                "action": "revise-unadmitted-candidate-in-place",
                "source_artifact_type_ref": ref,
                "target_artifact_type_ref": ref,
                "replacement_semantic_definition_refs": REBIND_TARGETS[ref],
                "required_changes": [
                    "replace borrowed, noncurrent, or external semantic bindings with the listed current admitted Definitions",
                    "update exact Definition paths and digests",
                    "regenerate the human projection and validation receipt deterministically",
                    "keep status candidate-unadmitted and authority_effect none",
                ],
            }
        action.update({
            "content_posture": entry["content_posture"],
            "effective_state": entry["effective_state"],
            "finding_codes": issue_codes,
        })
        existing_actions.append(action)

    missing = [entry for entry in endpoint_inventory["entries"] if entry["lifecycle_state"] == "referenced-no-canonical-carrier"]
    new_carriers = []
    for endpoint in missing:
        kind = endpoint["endpoint_kind"]
        definition_ref = f"cal.definition.{kind}"
        current_ref = definition_registry["current_lookup"].get(definition_ref)
        definition = current_by_ref[current_ref]
        new_carriers.append({
            "action": "materialize-new-candidate-carrier",
            "artifact_type_ref": f"cal.artifact-type.{kind}/v1",
            "endpoint_kind": kind,
            "semantic_definition_binding": {
                "definition_ref": current_ref,
                "path": definition["path"],
                "sha256": definition["sha256"],
            },
            "must_remain_distinct_from": DISTINCTIONS[kind],
            "source_for": endpoint["source_for"],
            "target_for": endpoint["target_for"],
            "required_contract": [
                "Artifact Type/v2 root binding",
                "closed instance schema and explicit discriminator",
                "exact current admitted semantic Definition binding",
                "canonical machine source and deterministic human projection",
                "owner, lifecycle, evidence, challenge route, and claim ceiling",
                "only the exact candidate relation kinds and endpoint roles listed here",
                "positive witness plus missing-field, extra-field, authority-escalation, and non-collapse negatives",
            ],
        })

    pairs = {
        entry["relation_kind_id"]: {(pair["source_kind"], pair["target_kind"]) for pair in entry["allowed_endpoint_pairs"]}
        for entry in relation_model["entries"]
    }
    examples = []
    for example in EXAMPLES:
        relation = example["relation"]
        examples.append({
            **example,
            "declared_endpoint_pair": (relation["source_kind"], relation["target_kind"]) in pairs[relation["relation_kind_ref"]],
            "authority_effect": "none",
            "lifecycle_state": "candidate-example",
        })

    return {
        "schema_version": "cyberalchemy-lab-artifact-type-carrier-closure-plan/v1",
        "plan_id": "CAL-ARTIFACT-TYPE-STEP5-CARRIER-CLOSURE-0001",
        "status": "candidate-complete-awaiting-owner-review",
        "authority_effect": "none",
        "objective": "Close the Artifact Type carrier layer before Relation Kind admission by repairing every actionable existing contract and materializing a distinct candidate carrier for every named relation endpoint kind.",
        "counts": {
            "existing_contract_actions": len(existing_actions),
            "immutable_successors": sum(action["action"] == "author-immutable-successor" for action in existing_actions),
            "candidate_revisions": sum(action["action"] == "revise-unadmitted-candidate-in-place" for action in existing_actions),
            "new_endpoint_carriers": len(new_carriers),
            "total_artifact_type_work_items": len(existing_actions) + len(new_carriers),
            "realistic_examples": len(examples),
        },
        "execution_order": [
            {"order": 1, "gate": "repair-positive-semantic-bindings", "work": "Revise the five unadmitted candidates so exact positive Definitions and provenance are current."},
            {"order": 2, "gate": "author-current-contract-successors", "work": "Author nine immutable successors; never rewrite admitted predecessor contracts."},
            {"order": 3, "gate": "materialize-missing-endpoint-carriers", "work": "Materialize 22 distinct candidate carriers from their admitted Definitions and exact relation endpoint roles."},
            {"order": 4, "gate": "hostile-non-collapse", "work": "Reject every listed neighboring concept substitution and every undeclared relation endpoint pair."},
            {"order": 5, "gate": "refresh-derived-surfaces", "work": "Generate a successor effective-state registry and endpoint inventory; require 50 of 50 endpoint kinds to resolve to carriers and zero referenced-no-canonical-carrier entries."},
            {"order": 6, "gate": "owner-review", "work": "Show all exact postimages and examples before any admission; admit only exact reviewed bytes in a later decision."},
        ],
        "existing_contract_actions": sorted(existing_actions, key=lambda item: item["source_artifact_type_ref"]),
        "new_endpoint_carriers": sorted(new_carriers, key=lambda item: item["endpoint_kind"]),
        "realistic_examples": examples,
        "completion_gates": [
            "All 14 actionable existing contracts have PASS postimages or explicit preserved predecessor dispositions.",
            "All 22 missing endpoint kinds have distinct schema-valid candidate carriers bound to current admitted Definitions.",
            "Every candidate carrier rejects authority escalation, unknown fields, missing required fields, neighboring-concept substitution, and undeclared endpoint roles.",
            "The successor registry reports zero semantic rebind obligations for promotable candidates and exact immutable lineage for all admitted predecessors.",
            "The relation endpoint inventory reports 50 named endpoint kinds, 50 canonical carriers, zero missing carriers, 147 unchanged explicit endpoint pairs, and zero wildcards.",
            "No Artifact Type, Relation Kind, Typed Relation instance, consumer, or runtime changes state until a later exact owner decision.",
        ],
        "claim_ceiling": candidate["claim_ceiling"],
        "source_bindings": {name: {**binding, "current": sha(LAB / binding["path"]) == binding["sha256"]} for name, binding in inputs.items()},
    }


def write_projection(plan: dict) -> None:
    c = plan["counts"]
    lines = [
        "<!-- GENERATED FILE: canonical data is plan.json. -->",
        "",
        "# Step 5 — Artifact Type carrier closure",
        "",
        f"- Status: `{plan['status']}`",
        f"- Authority effect: `{plan['authority_effect']}`",
        f"- Existing contract actions: `{c['existing_contract_actions']}` (`{c['immutable_successors']}` successors + `{c['candidate_revisions']}` candidate revisions)",
        f"- New endpoint carriers: `{c['new_endpoint_carriers']}`",
        f"- Total work items: `{c['total_artifact_type_work_items']}`",
        "",
        "## Execution order",
        "",
    ]
    for step in plan["execution_order"]:
        lines.append(f"{step['order']}. **{step['gate']}** — {step['work']}")
    lines += ["", "## Existing contract actions", "", "| Current ref | Action | Target ref | Findings |", "| --- | --- | --- | --- |"]
    for action in plan["existing_contract_actions"]:
        lines.append(f"| `{action['source_artifact_type_ref']}` | `{action['action']}` | `{action['target_artifact_type_ref']}` | `{', '.join(action['finding_codes'])}` |")
    lines += ["", "## Missing endpoint carriers", "", "| Endpoint kind | Candidate Artifact Type | Definition | Must remain distinct from |", "| --- | --- | --- | --- |"]
    for item in plan["new_endpoint_carriers"]:
        lines.append(f"| `{item['endpoint_kind']}` | `{item['artifact_type_ref']}` | `{item['semantic_definition_binding']['definition_ref']}` | `{', '.join(item['must_remain_distinct_from'])}` |")
    lines += ["", "## Realistic examples", ""]
    for example in plan["realistic_examples"]:
        relation = example["relation"]
        lines += [
            f"### {example['example_id']}",
            "",
            example["explanation"],
            "",
            "```json",
            json.dumps({**relation, "authority_effect": example["authority_effect"], "lifecycle_state": example["lifecycle_state"]}, indent=2, sort_keys=True),
            "```",
            "",
        ]
    lines += ["## Completion gates", ""]
    lines.extend(f"- {gate}" for gate in plan["completion_gates"])
    lines += ["", "## Claim ceiling", "", plan["claim_ceiling"]]
    (ROOT / "PLAN.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    value = build()
    dump(ROOT / "plan.json", value)
    write_projection(value)
