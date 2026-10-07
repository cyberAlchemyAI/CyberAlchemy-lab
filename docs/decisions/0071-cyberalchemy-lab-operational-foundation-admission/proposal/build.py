#!/usr/bin/env python3
"""Build the exact Decision 0071 operational foundation admission postimage."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
HERE = ROOT.parent
LAB = HERE.parents[2]
CANDIDATE = LAB / "authority/operational-foundations/candidates/0001-cyberalchemy-lab-foundation"
POSTIMAGE = ROOT / "bundle-postimage"
DECISION = "CAL-DECISION-0071-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-ADMISSION"
FINAL = "authority/admissions/cyberalchemy-lab-operational-foundation/v1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_bound(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def main() -> None:
    foundation = load(CANDIDATE / "foundation.json")
    validation = load(CANDIDATE / "receipts/validation.json")
    if validation["result"] != "PASS" or validation["foundation_sha256"] != sha(CANDIDATE / "foundation.json"):
        raise RuntimeError("candidate validation is not current and PASS")
    if POSTIMAGE.exists():
        shutil.rmtree(POSTIMAGE)

    copy_bound(CANDIDATE / "foundation.json", POSTIMAGE / "source-foundation.json")
    copy_bound(CANDIDATE / "FOUNDATION.md", POSTIMAGE / "FOUNDATION.md")
    copy_bound(CANDIDATE / "history-declarations.json", POSTIMAGE / "history-declarations.json")
    copy_bound(CANDIDATE / "receipts/validation.json", POSTIMAGE / "receipts/candidate-validation.json")

    artifact_admissions = []
    for item in foundation["artifacts"]:
        source = LAB / item["path"]
        target = POSTIMAGE / "instances" / "artifacts" / source.name
        copy_bound(source, target)
        artifact_admissions.append(
            {
                "identity_ref": item["identity_ref"],
                "semantic_kind": item["semantic_kind"],
                "carrier_type_ref": item["carrier_type_ref"],
                "version_ref": item["version_ref"],
                "source_path": item["path"],
                "source_sha256": item["sha256"],
                "admitted_instance_path": f"{FINAL}/instances/artifacts/{source.name}",
                "admitted_instance_sha256": sha(target),
                "lifecycle_state": "admitted-current",
                "admission_decision_ref": DECISION,
            }
        )
    dump(
        POSTIMAGE / "artifact-instance-admission.json",
        {
            "schema_version": "cyberalchemy-lab-artifact-instance-admission/v1",
            "decision_id": DECISION,
            "status": "owner-admitted-postimage",
            "authority_effect": "foundation-artifact-instance-admission-only",
            "count": len(artifact_admissions),
            "entries": artifact_admissions,
            "runtime_activations": 0,
            "claim_ceiling": "Admits only the nine exact foundation artifact instances bound here. Embedded candidate status is preserved as immutable source provenance; this overlay supplies effective admitted state.",
        },
    )

    relation_admissions = []
    for item in foundation["typed_relations"]:
        source = LAB / item["path"]
        target = POSTIMAGE / "instances" / "typed-relations" / source.name
        copy_bound(source, target)
        relation_admissions.append(
            {
                "relation_id": item["relation_id"],
                "relation_kind_ref": item["relation_kind_ref"],
                "source_kind": item["source_kind"],
                "source_ref": item["source_ref"],
                "target_kind": item["target_kind"],
                "target_ref": item["target_ref"],
                "version_ref": item["version_ref"],
                "source_path": item["path"],
                "source_sha256": item["sha256"],
                "admitted_instance_path": f"{FINAL}/instances/typed-relations/{source.name}",
                "admitted_instance_sha256": sha(target),
                "lifecycle_state": "admitted-current",
                "admission_decision_ref": DECISION,
            }
        )
    dump(
        POSTIMAGE / "typed-relation-admission.json",
        {
            "schema_version": "cyberalchemy-lab-typed-relation-instance-admission/v1",
            "decision_id": DECISION,
            "status": "owner-admitted-postimage",
            "authority_effect": "foundation-typed-relation-admission-only",
            "count": len(relation_admissions),
            "entries": relation_admissions,
            "runtime_activations": 0,
            "claim_ceiling": "Admits only the thirteen exact Typed Relation instances bound here. No relation beyond the declared axes and qualifiers may be inferred.",
        },
    )

    dump(
        POSTIMAGE / "foundation-admission.json",
        {
            "schema_version": "cyberalchemy-lab-operational-foundation-effective-state/v1",
            "foundation_id": foundation["foundation_id"],
            "decision_id": DECISION,
            "lifecycle_state": "admitted-current",
            "authority_effect": "operational-foundation-admission-only",
            "source_foundation": {
                "path": "source-foundation.json",
                "sha256": sha(POSTIMAGE / "source-foundation.json"),
                "embedded_status": foundation["status"],
                "embedded_authority_effect": foundation["authority_effect"],
            },
            "counts": {"artifact_instances_admitted": 9, "typed_relation_instances_admitted": 13, "history_streams_declared": 2, "runtime_activations": 0},
            "successor_state_obligation": "Decision 0071 and this bundle are inputs to the first successor of project-state:cyberalchemy-v2-to-lab-migration:decision-0070.",
            "claim_ceiling": "This effective-state overlay admits the exact operational roots. It does not create an Agent, Context View, Evidence Set, ontology projection, implementation, or active runtime.",
        },
    )

    files = []
    for path in sorted(item for item in POSTIMAGE.rglob("*") if item.is_file() and item.name != "bundle.json"):
        files.append({"path": str(path.relative_to(POSTIMAGE)), "sha256": sha(path)})
    bundle = {
        "schema_version": "cyberalchemy-lab-operational-foundation-admission-bundle/v1",
        "bundle_id": "CAL-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-BUNDLE-0071",
        "decision_id": DECISION,
        "status": "owner-admitted-postimage",
        "authority_effect": "operational-foundation-instance-admission-only",
        "counts": {"artifact_instances_admitted": 9, "typed_relation_instances_admitted": 13, "history_streams_declared": 2, "runtime_activations": 0},
        "files": files,
        "excluded_effects": foundation["excluded_effects"],
        "claim_ceiling": "Immutable postimage for Decision 0071. It takes effect only when atomically installed at the final admission path with the bound owner authorization.",
    }
    dump(POSTIMAGE / "bundle.json", bundle)

    proposal = {
        "schema_version": "cyberalchemy-lab-operational-foundation-admission-proposal/v1",
        "decision_id": DECISION,
        "title": "CyberAlchemy Lab smallest real operational foundation admission",
        "status": "candidate-awaiting-owner-authorization",
        "authority_effect": "none",
        "authorization_present": False,
        "inputs": {
            "foundation_candidate": {"path": str((CANDIDATE / "foundation.json").relative_to(LAB)), "sha256": sha(CANDIDATE / "foundation.json")},
            "candidate_validation": {"path": str((CANDIDATE / "receipts/validation.json").relative_to(LAB)), "sha256": sha(CANDIDATE / "receipts/validation.json"), "result": "PASS"},
        },
        "postimage": {"path": str((POSTIMAGE / "bundle.json").relative_to(LAB)), "sha256": sha(POSTIMAGE / "bundle.json"), "final_path": FINAL},
        "proposed_effects": {"artifact_instances_admitted": 9, "typed_relation_instances_admitted": 13, "history_streams_declared": 2, "runtime_activations": 0},
        "atomic_transaction": ["Verify candidate and proposal digests", "Verify exact owner authorization", "Install the immutable admission bundle", "Write Decision 0071 and validation receipts"],
        "excluded_effects": foundation["excluded_effects"],
        "claim_ceiling": "This proposal has no authority effect before exact owner authorization and atomic application.",
    }
    dump(ROOT / "proposal.json", proposal)
    lines = [
        "<!-- GENERATED FILE: canonical data is proposal.json and bundle-postimage. -->",
        "",
        "# Decision 0071 proposal",
        "",
        "Admit the smallest real operational foundation for CyberAlchemy Lab.",
        "",
        "- Artifact instances: `9`",
        "- Typed Relations: `13`",
        "- Empty history stream declarations: `2`",
        "- Runtime activations: `0`",
        f"- Foundation candidate: `{proposal['inputs']['foundation_candidate']['sha256']}`",
        f"- Bundle postimage: `{proposal['postimage']['sha256']}`",
        "",
        "The initial Project State stops at Decision 0070. This decision becomes an input to its first governed successor, which avoids a self-referential bootstrap digest.",
        "",
        "## Excluded effects",
        "",
    ]
    lines.extend(f"- {item}" for item in proposal["excluded_effects"])
    lines.extend(["", "## Claim ceiling", "", proposal["claim_ceiling"], ""])
    (ROOT / "PROPOSAL.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"bundle_sha256": proposal["postimage"]["sha256"], "artifacts": 9, "relations": 13}, sort_keys=True))


if __name__ == "__main__":
    main()
