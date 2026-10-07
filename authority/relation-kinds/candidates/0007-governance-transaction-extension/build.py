#!/usr/bin/env python3
"""Build the closed governance transaction relation model successor."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
BASE = LAB / "authority/relation-kinds/candidates/0005-definition-complete-extension/model.json"
ADMITTED_REGISTRY = LAB / "authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


ADDITIONS = {
    "relation.member-of": [
        ("decision", "decision-bundle"),
    ],
    "relation.governed-by": [
        ("admission-transaction", "policy"),
        ("authority-boundary", "policy"),
        ("decision-bundle", "policy"),
        ("decision-checkpoint", "policy"),
        ("user-decision-preference", "policy"),
        ("workflow-decision-profile", "policy"),
    ],
    "relation.scopes-authority-over": [
        ("authority-boundary", "decision-scope"),
    ],
}


def main() -> None:
    base = load(BASE)
    model = copy.deepcopy(base)
    model.update(
        schema_version="cyberalchemy-lab-governance-transaction-relation-model/v1",
        model_id="CAL-GOVERNANCE-TRANSACTION-RELATION-MODEL-0007",
        status="candidate-complete-awaiting-owner-review",
        authority_effect="none",
        predecessor={
            "path": str(BASE.relative_to(LAB)),
            "sha256": sha(BASE),
            "relation_kind_count": len(base["entries"]),
            "admission_decision_ref": "CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION",
        },
        claim_ceiling="This candidate extends the admitted relation surface for governance transaction carriers. It admits no Relation Kind, endpoint pair, Typed Relation, Artifact Type, instance, decision, or runtime effect.",
    )

    entries = {entry["relation_kind_id"]: entry for entry in model["entries"]}
    for relation_id, pairs in ADDITIONS.items():
        entry = entries[relation_id]
        current = {(p["source_kind"], p["target_kind"]) for p in entry["allowed_endpoint_pairs"]}
        current.update(pairs)
        entry["allowed_endpoint_pairs"] = [
            {"source_kind": source, "target_kind": target}
            for source, target in sorted(current)
        ]
        entry["source_kinds"] = sorted({source for source, _ in current})
        entry["target_kinds"] = sorted({target for _, target in current})

    authority = entries["relation.scopes-authority-over"]
    authority["unique_question"] = "What governed scope is bounded by this explicit Authority Claim or Authority Boundary?"
    authority["operational_effect"] = "Records an explicit authority subject's bounded scope without granting permission, authenticating the subject, or executing an effect."

    materializes = {
        "relation_kind_id": "relation.materializes-consequence",
        "axis_id": "axis.transaction-consequence-materialization",
        "group": "governance",
        "status": "candidate-axis-orthogonal",
        "authority_effect": "none",
        "unique_question": "Which declared deterministic consequence did this Admission Transaction materialize?",
        "operational_effect": "Records a deterministic output created while atomically applying an already authorized Decision Bundle; it grants no additional authority and proves no semantic correctness.",
        "required_qualifier_axes": ["application_receipt_ref", "consequence_role", "output_digest"],
        "forbidden_inferences": ["new-authorization", "semantic-correctness", "runtime-activation", "external-effect"],
        "absorbed_relation_kinds": ["relation.materializes-consequence"],
        "allowed_endpoint_pairs": [
            {"source_kind": "admission-transaction", "target_kind": "generated-output"},
            {"source_kind": "admission-transaction", "target_kind": "project-governance-event-history"},
            {"source_kind": "admission-transaction", "target_kind": "project-semantic-event-history"},
            {"source_kind": "admission-transaction", "target_kind": "project-state"},
        ],
        "source_kinds": ["admission-transaction"],
        "target_kinds": ["generated-output", "project-governance-event-history", "project-semantic-event-history", "project-state"],
    }
    model["entries"] = sorted([*entries.values(), materializes], key=lambda item: item["relation_kind_id"])

    lifecycle = "Each Typed Relation binds exact endpoint revisions and has its own lifecycle; endpoint or carrier lifecycle never silently creates, rewrites, or retires the relation."
    extensions = []
    for relation_id, pairs in ADDITIONS.items():
        entry = next(item for item in model["entries"] if item["relation_kind_id"] == relation_id)
        extensions.append({
            "relation_kind_id": relation_id,
            "extension_kind": "exact-pair-extension",
            "added_pairs": [{"source_kind": s, "target_kind": t} for s, t in pairs],
            "unique_question": entry["unique_question"],
            "required_qualifier_axes": entry["required_qualifier_axes"],
            "forbidden_inferences": entry["forbidden_inferences"],
            "lifecycle_rule": lifecycle,
        })
    extensions.append({
        "relation_kind_id": materializes["relation_kind_id"],
        "extension_kind": "new-axis",
        "added_pairs": materializes["allowed_endpoint_pairs"],
        "unique_question": materializes["unique_question"],
        "required_qualifier_axes": materializes["required_qualifier_axes"],
        "forbidden_inferences": materializes["forbidden_inferences"],
        "lifecycle_rule": lifecycle,
    })
    model["connection_extensions"] = extensions
    all_pairs = sum(len(entry["allowed_endpoint_pairs"]) for entry in model["entries"])
    all_kinds = {kind for entry in model["entries"] for pair in entry["allowed_endpoint_pairs"] for kind in pair.values()}
    model["counts"] = {
        "active_relation_kinds": len(model["entries"]),
        "base_relation_kinds": len(base["entries"]),
        "new_relation_kinds": 1,
        "extended_relation_kinds": len(ADDITIONS),
        "added_endpoint_pairs": sum(map(len, ADDITIONS.values())) + len(materializes["allowed_endpoint_pairs"]),
        "declared_endpoint_pairs": all_pairs,
        "endpoint_kinds": len(all_kinds),
        "extension_groups": len(extensions),
        "deferred_relation_kinds": len(model.get("deferred_axes", [])),
    }
    model["non_collapse_assessment"] = [
        {
            "left": "relation.materializes-consequence",
            "right": "relation.produces",
            "distinction": "Materialization is the transaction-scoped deterministic application of an authorized bundle; production attributes an output to an Agent Action and does not imply authorized application.",
        },
        {
            "left": "relation.materializes-consequence",
            "right": "relation.declares-effect-on",
            "distinction": "A Decision declares an effect on an exact target; an Admission Transaction materializes only consequences already covered by that declaration.",
        },
        {
            "left": "relation.member-of",
            "right": "payload references",
            "distinction": "Decision membership in a closed bundle is set membership. Presentation at a checkpoint and profile allowance remain typed payload references because they answer different contract questions.",
        },
    ]
    dump(ROOT / "model.json", model)

    lines = [
        "<!-- GENERATED FILE: canonical data is model.json. -->",
        "",
        "# Governance transaction relation extension",
        "",
        f"- Relation Kinds: `{model['counts']['active_relation_kinds']}`",
        f"- New axis: `relation.materializes-consequence`",
        f"- Added exact endpoint pairs: `{model['counts']['added_endpoint_pairs']}`",
        "- Authority effect: `none`",
        "",
        "## Exact extensions",
        "",
    ]
    for extension in extensions:
        lines += [f"### `{extension['relation_kind_id']}`", "", extension["unique_question"], ""]
        lines += [f"- `{p['source_kind']}` -> `{p['target_kind']}`" for p in extension["added_pairs"]]
        lines.append("")
    lines += ["## No-collapse conclusions", ""]
    lines += [f"- `{item['left']}` vs `{item['right']}`: {item['distinction']}" for item in model["non_collapse_assessment"]]
    lines += ["", "## Claim ceiling", "", model["claim_ceiling"], ""]
    (ROOT / "MODEL.md").write_text("\n".join(lines), encoding="utf-8")

    admitted = load(ADMITTED_REGISTRY)
    admitted_by_id = {item["relation_kind_id"]: item for item in admitted["entries"]}
    instance_entries = []
    for relation_id in ["relation.governed-by", "relation.member-of", "relation.scopes-authority-over", "relation.materializes-consequence"]:
        entry = next(item for item in model["entries"] if item["relation_kind_id"] == relation_id)
        predecessor = admitted_by_id.get(relation_id)
        qualifier_properties = {axis: {"type": "string", "minLength": 1} for axis in entry["required_qualifier_axes"]}
        instance = {
            "schema_version": "cyberalchemy-lab-relation-kind/v2",
            "node_id": relation_id + "@candidate.2" if predecessor else relation_id + "@candidate.1",
            "kind": "relation-kind",
            "name": relation_id.removeprefix("relation.").replace("-", " ").title(),
            "lifecycle_state": "candidate",
            "authority_effect": "none",
            "owner_ref": "role:relation-owner",
            "scope_ref": "scope:governance-transaction-relation-model",
            "evidence_refs": ["evidence:approval-admission-boundary-audit"],
            "challenge_route": "route:relation-governance-challenge",
            "successor_refs": [],
            "relation_refs": ([{
                "relation_kind_ref": "relation.successor-of",
                "direction": "source",
                "counterpart_kind": "relation-kind",
                "counterpart_ref": relation_id + "@sha256:" + predecessor["instance_sha256"],
            }] if predecessor else []),
            "payload": {
                "relation_kind_id": relation_id,
                "axis_id": entry["axis_id"],
                "predicate": relation_id.removeprefix("relation."),
                "group": entry["group"],
                "unique_question": entry["unique_question"],
                "operational_effect": entry["operational_effect"],
                "source_kinds": entry["source_kinds"],
                "target_kinds": entry["target_kinds"],
                "allowed_endpoint_pairs": entry["allowed_endpoint_pairs"],
                "qualifier_contract": {"closed": True, "required_axes": entry["required_qualifier_axes"], "properties": qualifier_properties},
                "forbidden_inferences": entry["forbidden_inferences"],
                "absorbed_relation_kinds": entry["absorbed_relation_kinds"],
                "inverse_ref": None,
            },
            "claim_ceiling": "Candidate Relation Kind revision for exact governance transaction endpoints. It creates no connection, authority, admission, inference, or runtime effect.",
        }
        path = ROOT / "instances/relation-kinds" / (relation_id.removeprefix("relation.") + ".json")
        dump(path, instance)
        instance_entries.append({
            "relation_kind_id": relation_id,
            "posture": "successor-of-admitted-current" if predecessor else "new-axis",
            "path": str(path.relative_to(LAB)),
            "sha256": sha(path),
            "predecessor_path": predecessor["instance_path"] if predecessor else None,
            "predecessor_sha256": predecessor["instance_sha256"] if predecessor else None,
            "exact_endpoint_pair_count": len(entry["allowed_endpoint_pairs"]),
        })
    dump(ROOT / "relation-kind-successor-manifest.json", {
        "schema_version": "cyberalchemy-lab-relation-kind-successor-manifest/v1",
        "status": "candidate-awaiting-owner-review",
        "authority_effect": "none",
        "predecessor_registry": {"path": str(ADMITTED_REGISTRY.relative_to(LAB)), "sha256": sha(ADMITTED_REGISTRY)},
        "entries": instance_entries,
        "claim_ceiling": "This manifest binds three Relation Kind successors and one new Relation Kind. It admits none of them.",
    })


if __name__ == "__main__":
    main()
