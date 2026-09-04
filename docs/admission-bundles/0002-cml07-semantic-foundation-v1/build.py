#!/usr/bin/env python3
"""Build and validate the non-effectful CML-07 pre-S2 admission bundle."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
CORE = LAB.parent / "domainspec-core"
BUNDLE_PATH = ROOT / "bundle.json"
DECISION_ID = "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1"
IDENTITY_SOURCES = LAB / "authority/decisions/source-admission/craft-identity-v1/v1/admissions.json"
SEMANTIC_SOURCES = LAB / "authority/decisions/source-admission/cml07-semantic-closure/v1/admissions.json"
OWNER_BINDINGS = LAB / "authority/owners/foundation-01/v1/candidates/0004-craft-identity/owner-bindings.json"
OWNER_PREDECESSOR = LAB / "authority/owners/foundation-01/v1/candidates/0003-craft-product/owners.json"
CANDIDATE_0006 = LAB / "authority/definitions/candidates/0006-craft-identity/candidate.json"
CANDIDATE_0007 = LAB / "authority/definitions/candidates/0007-cml07-semantic-closure/candidate.json"
CANDIDATE_REGISTRY = LAB / "authority/definitions/candidates/0007-cml07-semantic-closure/registry-postimage.json"
ARTIFACT_TYPE_V2 = LAB / "authority/artifact-types/artifact-type/v2/artifact.json"
CHAIN_0002 = LAB / "docs/identity-packs/0002-craft-identity-chain-semantic-closure/chain.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected(path: Path, item: dict[str, Any]) -> bytes:
    if item["selector_kind"] == "whole-file-v1":
        return path.read_bytes()
    lines = path.read_bytes().splitlines(keepends=True)
    return b"".join(lines[item["start_line"] - 1:item["end_line"]])


def render_index(registry: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit machine sources and run build.py. -->",
        "",
        "# CyberAlchemy Lab Definition Index",
        "",
        f"- Status: `{registry['status']}`",
        f"- Prospective admission decision: `{registry['admission_decision_ref']}`",
        "",
        "| ID | Version | Term | Lifecycle | Path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in registry["entries"]:
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | `{item['lifecycle_state']}` | `{item['path']}` |")
    lines.extend(["", "## Current lookup", ""])
    lines.extend(f"- `{key}` -> `{value}`" for key, value in registry["current_lookup"].items())
    lines.extend(["", "## Claim ceiling", "", registry["claim_ceiling"]])
    return "\n".join(lines)


def build_registry(bundle: dict[str, Any]) -> dict[str, Any]:
    candidate = load(CANDIDATE_REGISTRY)
    live = load(LAB / "authority/definitions/registry.json")
    entries = deepcopy(candidate["entries"])
    promoted = 0
    for item in entries:
        if item["lifecycle_state"] == "candidate-unadmitted":
            item["lifecycle_state"] = "admitted"
            item["admission_decision_ref"] = DECISION_ID
            promoted += 1
    return {
        "schema_version": live["schema_version"],
        "record_id": live["record_id"],
        "artifact_type_ref": live["artifact_type_ref"],
        "status": "owner-admitted",
        "authority_effect": "thirty-two-exact-definition-versions-canonical",
        "owner_ref": "role:definition-owner",
        "definition_artifact_type_ref": live["definition_artifact_type_ref"],
        "admission_decision_ref": DECISION_ID,
        "predecessor": {
            "path": "authority/definitions/registry.json",
            "sha256": bundle["live_preimages"][0]["sha256"],
            "entry_count": len(live["entries"]),
            "admission_decision_ref": live["admission_decision_ref"],
        },
        "entries": sorted(entries, key=lambda x: (x["definition_id"], x["version"])),
        "current_lookup": dict(sorted(candidate["proposed_current_lookup"].items())),
        "identity_rule": live["identity_rule"],
        "index_policy": "generated-only",
        "source_direction": {
            "canonical": "registry.json",
            "human_projection": "DEFINITIONS-INDEX.md",
            "projection_policy": "generated-only",
            "generator_ref": "cal.generator.cml07-semantic-foundation-bundle/v1",
        },
        "claim_ceiling": f"This prospective postimage promotes exactly {promoted} Definition versions through {DECISION_ID} while preserving all 18 admitted predecessors. It does not admit identity carriers or establish implementation or runtime conformance.",
    }


def build_drift(registry_path: Path) -> dict[str, Any]:
    return {
        "schema_version": "cyberalchemy-lab-definition-drift-audit/v1",
        "record_id": "CAL-DEFINITION-DRIFT-AUDIT-CML07-PRE-S2-SEMANTIC-FOUNDATION-V1",
        "artifact_type_ref": "cal.artifact-type.drift-audit/v1",
        "status": "prospective-current-evidence",
        "authority_effect": "definition-drift-evidence-only",
        "owner_ref": "role:evidence-conformance-owner",
        "registry_ref": "authority/definitions/registry.json",
        "registry_sha256": sha(registry_path),
        "admission_decision_ref": DECISION_ID,
        "findings": [
            {
                "finding_id": "CML07-PRE-S2-001",
                "severity": "resolved-on-admission",
                "status": "prospective",
                "target": "CML-07 semantic vocabulary",
                "condition": "Six identity Definitions and eight semantic-closure Definitions become current through separate requests in one immutable decision set.",
                "remediation": "Require every exact request and digest to be selected together; otherwise perform zero live writes.",
            },
            {
                "finding_id": "CML07-PRE-S2-002",
                "severity": "resolved-on-admission",
                "status": "prospective",
                "target": "CAV2-D38 CAV2-D56 CAV2-D65",
                "condition": "The three exact external selectors become admitted only for the stated semantic-closure use.",
                "remediation": "Do not widen selector use without a successor source-admission decision.",
            },
            {
                "finding_id": "CML07-PRE-S2-003",
                "severity": "successor-readiness",
                "status": "evaluable-after-admission",
                "target": "CML07-S2-AUTHOR-IDENTITY-ARTIFACT-TYPES",
                "condition": "Artifact Type/v2, semantic Definitions, exact sources, and accountable owners are dependency-closed by this transaction.",
                "remediation": "After successful admission, author S2 candidates under Artifact Type/v2; do not infer their admission or conformance.",
            },
            {
                "finding_id": "CML07-PRE-S2-004",
                "severity": "claim-boundary",
                "status": "preserved",
                "target": "conformance",
                "condition": "Schema and identity-contract conformance remain distinct from implementation and runtime conformance.",
                "remediation": "Evaluate each scope through its own complete profile and evidence set.",
            },
        ],
        "summary": {
            "definition_versions_after_effect": 32,
            "current_definition_terms_after_effect": 30,
            "source_selections_in_workflow": 11,
            "new_owner_bindings_in_workflow": 4,
            "s2_posture_after_effect": "evaluable-not-authorized-by-implication",
            "implementation_conformance": "not_evaluable",
            "runtime_conformance": "not_evaluable",
        },
        "source_direction": {
            "canonical": "drift-audit.json",
            "human_projection": "DEFINITION-DRIFT-AUDIT.md",
            "projection_policy": "generated-only",
            "generator_ref": "cal.generator.cml07-semantic-foundation-bundle/v1",
        },
        "claim_ceiling": "This prospective audit closes only pre-S2 semantic dependencies. It does not author S2, admit identity carriers, establish conformance, or authorize publication.",
    }


def render_drift(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit machine sources and run build.py. -->",
        "",
        "# CML-07 Pre-S2 Definition Drift Audit",
        "",
        "> Prospective post-admission projection; noncanonical until the bound transaction succeeds.",
        "",
    ]
    for item in data["findings"]:
        lines.extend([
            f"## {item['finding_id']} — {item['status']}",
            "",
            item["condition"],
            "",
            f"Remediation: {item['remediation']}",
            "",
        ])
    lines.extend(["## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def build_owners(bindings: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(load(OWNER_PREDECESSOR))
    result["record_id"] = "CAL-OWNERS-CRAFT-IDENTITY-0004"
    result["status"] = "candidate-unadmitted"
    result["authority_effect"] = "none-until-bound-decision"
    result["predecessor"] = {
        "path": str(OWNER_PREDECESSOR.relative_to(LAB)),
        "sha256": sha(OWNER_PREDECESSOR),
        "admission_decision_ref": "CAL-DECISION-0028-CRAFT-FOUNDATION-V1",
    }
    result["role_assignments"] = result["role_assignments"] + deepcopy(bindings["assignments"])
    result["separation_rule"] = bindings["separation_rule"]
    result["source_direction"] = {
        "canonical": "owners.json",
        "human_projection": "OWNERS.md",
        "projection_policy": "generated-only",
        "generator_ref": "cal.generator.cml07-semantic-foundation-bundle/v1",
    }
    result["claim_ceiling"] = "This prospective owner-registry postimage preserves sixteen decision-bound assignments and adds four separately scoped Craft identity roles only if the exact CML-07 semantic-foundation decision succeeds. Shared principal identity merges no authority."
    return result


def render_owners(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit owner-bindings.json and run build.py. -->",
        "",
        "# CML-07 Owner Registry Postimage",
        "",
        "> Prospective postimage; roles are not activated by this projection.",
        "",
        "| Role | Principal | Scope |",
        "| --- | --- | --- |",
    ]
    for item in data["role_assignments"]:
        lines.append(f"| `{item['role_id']}` | `{item['principal_id']}` | {item['scope']} |")
    lines.extend(["", "## Separation rule", "", data["separation_rule"], "", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def build() -> int:
    bundle = load(BUNDLE_PATH)
    identity_sources = load(IDENTITY_SOURCES)
    semantic_sources = load(SEMANTIC_SOURCES)
    owner_bindings = load(OWNER_BINDINGS)
    candidate_0006 = load(CANDIDATE_0006)
    candidate_0007 = load(CANDIDATE_0007)
    artifact_v2 = load(ARTIFACT_TYPE_V2)
    chain = load(CHAIN_0002)
    post = ROOT / "postimages"

    registry_path = post / "authority/definitions/registry.json"
    registry = build_registry(bundle)
    dump(registry_path, registry)
    write(post / "authority/definitions/DEFINITIONS-INDEX.md", render_index(registry))
    drift = build_drift(registry_path)
    dump(post / "authority/definitions/drift-audit.json", drift)
    write(post / "authority/definitions/DEFINITION-DRIFT-AUDIT.md", render_drift(drift))
    owners = build_owners(owner_bindings)
    owner_path = post / "authority/owners/foundation-01/v1/candidates/0004-craft-identity/owners.json"
    dump(owner_path, owners)
    write(owner_path.with_name("OWNERS.md"), render_owners(owners))

    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    bound = bundle["candidate_inputs"] + bundle["live_preimages"]
    observed = {x["path"]: sha(LAB / x["path"]) if (LAB / x["path"]).is_file() else "missing" for x in bound}
    check("all-bound-inputs-current", all(observed[x["path"]] == x["sha256"] for x in bound), observed)

    all_sources = identity_sources["admissions"] + semantic_sources["admissions"]
    source_results = []
    for item in all_sources:
        source_path = CORE / item["source_path"]
        actual_file = sha(source_path) if source_path.is_file() else "missing"
        actual_selection = hashlib.sha256(selected(source_path, item)).hexdigest() if source_path.is_file() else "missing"
        source_results.append({
            "admission_id": item["admission_id"],
            "file_expected": item["source_file_sha256_at_authoring"],
            "file_actual": actual_file,
            "selected_expected": item["selected_sha256"],
            "selected_actual": actual_selection,
        })
    check("eleven-source-selections-current", len(all_sources) == 11 and all(x["file_expected"] == x["file_actual"] and x["selected_expected"] == x["selected_actual"] for x in source_results), source_results)
    check("source-candidates-non-effectful", identity_sources["status"] == semantic_sources["status"] == "candidate-unadmitted" and identity_sources["authority_effect"].startswith("none") and semantic_sources["authority_effect"].startswith("none"), "both source records remain candidate-unadmitted")

    for receipt_path in [
        LAB / "authority/decisions/source-admission/cml07-semantic-closure/v1/receipts/validation.json",
        LAB / "authority/definitions/candidates/0006-craft-identity/receipts/validation.json",
        LAB / "authority/definitions/candidates/0007-cml07-semantic-closure/receipts/validation.json",
        LAB / "authority/artifact-types/artifact-type/v2/receipts/validation.json",
        LAB / "docs/identity-packs/0002-craft-identity-chain-semantic-closure/receipts/validation.json",
    ]:
        receipt = load(receipt_path)
        result = receipt.get("result", receipt.get("status"))
        check(f"receipt-pass:{receipt_path.parent.parent.name}", result == "PASS", {"path": str(receipt_path.relative_to(LAB)), "result": result})

    defs_0006 = {x["definition_id"] for x in candidate_0006["definitions"]}
    defs_0007 = {x["definition_id"] for x in candidate_0007["definitions"]}
    check("definition-cohort-orthogonal", len(defs_0006) == 6 and len(defs_0007) == 8 and not defs_0006 & defs_0007, {"candidate_0006": sorted(defs_0006), "candidate_0007": sorted(defs_0007)})
    check("frozen-candidate-0006-bound", sha(CANDIDATE_0006) == "36cdfaf7faf206fdcd387289b66838a46e3fa731b3667eb974c649cd1417cd72", sha(CANDIDATE_0006))

    semantic_ref = "cal.definition.artifact-type@1.0.0-candidate.1"
    check("artifact-type-v2-semantic-binding", semantic_ref in artifact_v2.get("semantic_definition_refs", []) and "cal.definition.artifact-type" in defs_0007, artifact_v2.get("semantic_definition_refs"))
    check("chain-selects-exact-predecessors", chain["semantic_predecessors"][0]["sha256"] == sha(CANDIDATE_0006) and chain["semantic_predecessors"][1]["sha256"] == sha(CANDIDATE_0007) and chain["artifact_type_predecessor"]["sha256"] == sha(ARTIFACT_TYPE_V2), chain["chain_id"])
    check("chain-preserves-conformance-scopes", set(chain["conformance_vocabulary"]) >= {"schema_conformance", "identity_contract_conformance", "implementation_conformance", "runtime_conformance"}, sorted(chain["conformance_vocabulary"]))

    roles = [x["role_id"] for x in owners["role_assignments"]]
    check("owner-predecessor-current", sha(OWNER_PREDECESSOR) == owner_bindings["predecessor_registry"]["sha256"], sha(OWNER_PREDECESSOR))
    check("twenty-owner-roles-unique", len(roles) == len(set(roles)) == 20, roles)
    check("shared-principal-does-not-merge-roles", all(x["decision_separation"] == "required" for x in owners["role_assignments"]), "all 20 assignments require decision separation")

    keys = [(x["definition_id"], x["version"]) for x in registry["entries"]]
    refs = {f"{definition_id}@{version}" for definition_id, version in keys}
    check("registry-has-32-unique-versions", len(keys) == len(set(keys)) == 32, {"entries": len(keys), "unique": len(set(keys))})
    check("registry-has-30-current-terms", len(registry["current_lookup"]) == 30 and set(registry["current_lookup"].values()) <= refs, len(registry["current_lookup"]))
    promoted_entries = [x for x in registry["entries"] if x.get("admission_decision_ref") == DECISION_ID]
    check("exactly-fourteen-definitions-promoted", len(promoted_entries) == 14 and {x["definition_id"] for x in promoted_entries} == defs_0006 | defs_0007, sorted(x["definition_id"] for x in promoted_entries))

    request_ids = [x["request_id"] for x in bundle["decision_requests"]]
    check("one-boundary-eight-separate-requests", bundle["decision_boundary"]["mode"] == "single-checkpoint" and len(request_ids) == len(set(request_ids)) == 8, request_ids)
    check("bundle-remains-non-effectful", bundle["status"] == "candidate-unadmitted" and bundle["authority_effect"] == "none", bundle["claim_ceiling"])
    check("final-s4-bundle-reservation-preserved", not (LAB / "docs/admission-bundles/0002-craft-identity-v1/manifest.json").exists(), "final S4 manifest has not been collapsed into this pre-S2 workflow")
    check("machine-canonical-human-generated", registry["source_direction"]["projection_policy"] == drift["source_direction"]["projection_policy"] == owners["source_direction"]["projection_policy"] == "generated-only", "all postimage projections are generated-only")

    postimage_hashes = {path: sha(ROOT / path) if (ROOT / path).is_file() else "missing" for path in bundle["postimages"]}
    check("six-postimages-complete", len(postimage_hashes) == 6 and "missing" not in postimage_hashes.values(), postimage_hashes)

    manifest = {
        "schema_version": "cyberalchemy-lab-cml07-semantic-foundation-manifest/v1",
        "manifest_id": "CAL-CML07-SEMANTIC-FOUNDATION-V1-MANIFEST",
        "status": "candidate-ready-for-exact-owner-decision",
        "authority_effect": "none",
        "bundle_path": str(BUNDLE_PATH.relative_to(LAB)),
        "bundle_sha256": sha(BUNDLE_PATH),
        "prospective_decision_id": DECISION_ID,
        "workflow_type": bundle["workflow_type"],
        "decision_boundary": bundle["decision_boundary"],
        "decision_requests": bundle["decision_requests"],
        "candidate_inputs": bundle["candidate_inputs"],
        "live_preimages": bundle["live_preimages"],
        "postimages": [{"path": path, "sha256": sha(ROOT / path)} for path in bundle["postimages"]],
        "rollback_policy": bundle["rollback_policy"],
        "excluded_effects": bundle["excluded_effects"],
        "claim_ceiling": "This immutable manifest is ready for one exact digest-bound owner decision only after its validation receipt passes. It has no admission, construction, conformance, publication, or deployment effect by itself.",
    }
    dump(ROOT / "manifest.json", manifest)

    blocked = [x for x in checks if x["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-cml07-semantic-foundation-validation/v1",
        "subject": manifest["manifest_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "promotion_eligibility": "eligible-for-one-exact-digest-bound-owner-decision" if not blocked else "blocked",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "materials": {"manifest_sha256": sha(ROOT / "manifest.json"), "bundle_sha256": sha(BUNDLE_PATH)},
        "claim_ceiling": "PASS proves exact dependency closure, source currentness, owner separation, postimage completeness, and a single configured decision boundary only. It does not admit or install the postimages, execute S2, or establish conformance.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    write(ROOT / "BUNDLE.md", "\n".join([
        "<!-- GENERATED FILE: edit bundle.json and run build.py. -->",
        "",
        "# CML-07 Pre-S2 Semantic Foundation v1",
        "",
        f"- Result: `{receipt['result']}`",
        f"- Manifest SHA-256: `{receipt['materials']['manifest_sha256']}`",
        f"- Validation receipt SHA-256: `{sha(ROOT / 'receipts/validation.json')}`",
        f"- Decision boundary: `{bundle['decision_boundary']['placement']}`",
        f"- Independent requests: `{len(bundle['decision_requests'])}`",
        "",
        "This set closes the semantic prerequisites for S2 through eight independently owned requests presented at one human checkpoint. A successful later transaction makes S2 evaluable; it does not execute S2.",
        "",
        "## Claim ceiling",
        "",
        manifest["claim_ceiling"],
    ]))

    print(f"CML07_SEMANTIC_FOUNDATION_BUNDLE={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"MANIFEST_SHA256={receipt['materials']['manifest_sha256']}")
    print(f"RECEIPT_SHA256={sha(ROOT / 'receipts/validation.json')}")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(build())
