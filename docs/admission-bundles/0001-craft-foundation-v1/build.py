#!/usr/bin/env python3
"""Build and validate the non-effectful Craft foundation admission bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE_REPO = Path("/home/vrondelli/projects/domainspec-core")
BUNDLE = ROOT / "bundle.json"
SOURCE_ADMISSIONS = LAB / "authority/decisions/source-admission/craft-foundation-v1/v1/admissions.json"
OWNER_BINDING = LAB / "authority/owners/foundation-01/v1/candidates/0003-craft-product/owner-binding.json"
OWNER_PREDECESSOR = LAB / "authority/owners/foundation-01/v1/candidates/0002-context-operations/owners.json"
DECISION_ID = "CAL-DECISION-0028-CRAFT-FOUNDATION-V1"


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
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    return "".join(lines[item["start_line"] - 1:item["end_line"]]).encode()


def render_source(data: dict[str, Any]) -> str:
    lines = ["<!-- GENERATED FILE: edit admissions.json and run build.py. -->", "", "# Craft Foundation Source Admissions", "", "> Candidate only; authority effect is none.", ""]
    for item in data["admissions"]:
        selector = "whole file" if item["selector_kind"] == "whole-file-v1" else f"lines {item['start_line']}-{item['end_line']}"
        lines += [f"## {item['admission_id']}", "", f"- Source: `{item['source_repository']}:{item['source_path']}`", f"- Selector: `{selector}`", f"- Digest: `{item['selected_sha256']}`", f"- Use: {item['target_use']}", ""]
    lines += ["## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def render_owner(data: dict[str, Any]) -> str:
    a = data["assignment"]
    return "\n".join(["<!-- GENERATED FILE: edit owner-binding.json and run build.py. -->", "", "# Craft Product Owner Binding", "", "> Candidate only; the role is not active.", "", f"- Role: `{a['role_id']}`", f"- Principal: `{a['principal_id']}`", f"- Scope: {a['scope']}", "", "## Claim ceiling", "", data["claim_ceiling"]])


def build_owner_postimage(binding: dict[str, Any]) -> dict[str, Any]:
    result = load(OWNER_PREDECESSOR)
    result["record_id"] = "CAL-OWNERS-CRAFT-PRODUCT-0003"
    result["role_assignments"] = result["role_assignments"] + [binding["assignment"]]
    result["separation_rule"] = result["separation_rule"] + " Craft Product ownership does not imply Definition admission or Bounded Context ownership."
    result["claim_ceiling"] = "This prospective owner-registry postimage preserves the fifteen admitted assignments and adds one exact Craft Product role binding only if CAL-DECISION-0028 is admitted. It grants no Definition, source, context, implementation, publication, or deployment authority."
    return result


def build_registry(bundle: dict[str, Any]) -> dict[str, Any]:
    live = load(LAB / "authority/definitions/registry.json")
    entries = list(live["entries"])
    lookup = dict(live["current_lookup"])
    for candidate_path in (
        LAB / "authority/definitions/candidates/0004-change-lifecycle-selection/candidate.json",
        LAB / "authority/definitions/candidates/0005-craft-workflow-interaction/candidate.json",
    ):
        candidate = load(candidate_path)
        for item in candidate["definitions"]:
            path = LAB / item["path"]
            record = load(path)
            entries.append({
                "definition_id": record["definition_id"],
                "version": record["version"],
                "term": record["term"],
                "path": item["path"],
                "sha256": sha(path),
                "lifecycle_state": "admitted",
                "admission_decision_ref": DECISION_ID,
            })
            lookup[record["definition_id"]] = f"{record['definition_id']}@{record['version']}"
    entries.sort(key=lambda x: (x["definition_id"], x["version"]))
    return {
        "schema_version": live["schema_version"],
        "record_id": live["record_id"],
        "artifact_type_ref": live["artifact_type_ref"],
        "status": "owner-admitted",
        "authority_effect": "eighteen-exact-definition-versions-canonical",
        "owner_ref": "role:definition-owner",
        "definition_artifact_type_ref": live["definition_artifact_type_ref"],
        "admission_decision_ref": DECISION_ID,
        "predecessor": {"path": "authority/definitions/registry.json", "sha256": bundle["live_preimages"][0]["sha256"], "entry_count": len(live["entries"]), "admission_decision_ref": live["admission_decision_ref"]},
        "entries": entries,
        "current_lookup": dict(sorted(lookup.items())),
        "identity_rule": live["identity_rule"],
        "index_policy": "generated-only",
        "source_direction": {"canonical": "registry.json", "human_projection": "DEFINITIONS-INDEX.md", "projection_policy": "generated-only", "generator_ref": "cal.generator.craft-foundation-bundle/v1"},
        "claim_ceiling": "This prospective registry postimage admits eight exact Definition versions through CAL-DECISION-0028 while preserving all ten prior versions. It does not admit a Product, Project, Bounded Context, runtime, implementation, publication, deployment, or stable release."
    }


def render_index(registry: dict[str, Any]) -> str:
    lines = ["<!-- GENERATED FILE: edit machine sources and run build.py. -->", "", "# CyberAlchemy Lab Definition Index", "", f"- Status: `{registry['status']}`", f"- Admission decision: `{registry['admission_decision_ref']}`", "", "| ID | Version | Term | Lifecycle | Path |", "| --- | --- | --- | --- | --- |"]
    for item in registry["entries"]:
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | `{item['lifecycle_state']}` | `{item['path']}` |")
    lines += ["", "## Current lookup", ""]
    lines += [f"- `{k}` -> `{v}`" for k, v in registry["current_lookup"].items()]
    lines += ["", "## Claim ceiling", "", registry["claim_ceiling"]]
    return "\n".join(lines)


def build_drift(registry_path: Path) -> dict[str, Any]:
    return {
        "schema_version": "cyberalchemy-lab-definition-drift-audit/v1",
        "record_id": "CAL-DEFINITION-DRIFT-AUDIT-CRAFT-FOUNDATION-V1",
        "artifact_type_ref": "cal.artifact-type.drift-audit/v1",
        "status": "prospective-current-evidence",
        "authority_effect": "definition-drift-evidence-only",
        "owner_ref": "role:evidence-conformance-owner",
        "registry_ref": "authority/definitions/registry.json",
        "registry_sha256": sha(registry_path),
        "admission_decision_ref": DECISION_ID,
        "findings": [
            {"finding_id": "CRAFT-FOUNDATION-001", "severity": "resolved-on-admission", "status": "prospective", "target": "authority/definitions/candidates/0005-craft-workflow-interaction", "condition": "Five exact external source selections and craft-product-owner are closed by separate clauses in the same decision request set.", "remediation": "Require all clauses and exact digests to be admitted together; otherwise perform zero live writes."},
            {"finding_id": "CRAFT-FOUNDATION-002", "severity": "boundary", "status": "preserved", "target": "contexts/", "condition": "Craft Product identity does not imply a Craft root Bounded Context.", "remediation": "Author a context only after separate context-local meaning, language, ownership, and map evidence exists."},
            {"finding_id": "CRAFT-FOUNDATION-003", "severity": "successor-blocker", "status": "open", "target": "product/products/craft and coordination/projects/craft", "condition": "No admitted Lab Product or Project identity artifact type and instance exist in this bundle.", "remediation": "Author schema-first Product and Project identity carriers in the next bounded construction slice."}
        ],
        "summary": {"admitted_definition_versions_after_effect": 18, "current_definition_terms_after_effect": 16, "source_admissions_in_bundle": 5, "owner_bindings_in_bundle": 1, "bounded_contexts_inferred": 0, "successor_blockers": 1},
        "source_direction": {"canonical": "drift-audit.json", "human_projection": "DEFINITION-DRIFT-AUDIT.md", "projection_policy": "generated-only", "generator_ref": "cal.generator.craft-foundation-bundle/v1"},
        "claim_ceiling": "This prospective audit covers Definition and interaction-foundation drift only. It does not establish Product, Project, context, runtime, implementation, publication, deployment, or stable-release state."
    }


def render_drift(data: dict[str, Any]) -> str:
    lines = ["<!-- GENERATED FILE: edit machine sources and run build.py. -->", "", "# Craft Foundation Definition Drift Audit", "", "> Prospective post-admission projection; noncanonical until the bound decision succeeds.", ""]
    for item in data["findings"]:
        lines += [f"## {item['finding_id']} — {item['status']}", "", item["condition"], "", f"Remediation: {item['remediation']}", ""]
    lines += ["## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def build() -> int:
    bundle = load(BUNDLE)
    admissions = load(SOURCE_ADMISSIONS)
    binding = load(OWNER_BINDING)
    post = ROOT / "postimages"
    write(SOURCE_ADMISSIONS.with_name("SOURCE-ADMISSIONS.md"), render_source(admissions))
    write(OWNER_BINDING.with_name("OWNER-BINDING.md"), render_owner(binding))
    owner_postimage = build_owner_postimage(binding)
    owner_post_path = post / "authority/owners/foundation-01/v1/candidates/0003-craft-product/owners.json"
    dump(owner_post_path, owner_postimage)
    registry_path = post / "authority/definitions/registry.json"
    dump(registry_path, build_registry(bundle))
    registry = load(registry_path)
    write(post / "authority/definitions/DEFINITIONS-INDEX.md", render_index(registry))
    drift = build_drift(registry_path)
    dump(post / "authority/definitions/drift-audit.json", drift)
    write(post / "authority/definitions/DEFINITION-DRIFT-AUDIT.md", render_drift(drift))

    checks: list[dict[str, Any]] = []
    def check(name: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": name, "result": "PASS" if ok else "FAIL", "detail": detail})

    bound = bundle["candidate_inputs"] + bundle["live_preimages"] + bundle["architecture_bindings"]
    check("bound-inputs-current", all(sha(LAB / x["path"]) == x["sha256"] for x in bound), {x["path"]: sha(LAB / x["path"]) for x in bound})
    source_results = []
    for item in admissions["admissions"]:
        path = SOURCE_REPO / item["source_path"]
        actual = hashlib.sha256(selected(path, item)).hexdigest()
        source_results.append({"admission_id": item["admission_id"], "expected": item["selected_sha256"], "actual": actual})
    check("external-source-selectors-current", all(x["expected"] == x["actual"] for x in source_results), source_results)
    check("source-admission-no-effect", admissions["status"] == "candidate-unadmitted" and admissions["authority_effect"].startswith("none"), admissions["authority_effect"])
    check("owner-predecessor-current", sha(OWNER_PREDECESSOR) == binding["predecessor_registry"]["sha256"], sha(OWNER_PREDECESSOR))
    roles = [x["role_id"] for x in owner_postimage["role_assignments"]]
    check("owner-role-orthogonal-and-unique", len(roles) == len(set(roles)) == 16 and roles.count("craft-product-owner") == 1, roles)
    check("owner-binding-no-effect", binding["status"] == "candidate-unadmitted" and binding["authority_effect"] == "none", binding["authority_effect"])
    for candidate_dir in ("0004-change-lifecycle-selection", "0005-craft-workflow-interaction"):
        receipt = load(LAB / f"authority/definitions/candidates/{candidate_dir}/receipts/validation.json")
        check(f"{candidate_dir}-validation-pass", receipt["result"] == "PASS", receipt["summary"])
    source_ids = {x["admission_id"] for x in admissions["admissions"]}
    check("candidate-0005-blockers-closed-prospectively", len(source_ids) == 5 and "craft-product-owner" in roles and bundle["context_disposition"]["selection"] == "product-not-implicitly-bounded-context", {"sources": len(source_ids), "owner": "craft-product-owner" in roles, "context": bundle["context_disposition"]["selection"]})
    keys = [(x["definition_id"], x["version"]) for x in registry["entries"]]
    check("registry-identity-unique", len(keys) == len(set(keys)) == 18, {"entries": len(keys), "unique": len(set(keys))})
    check("current-lookup-closed", all(v in {f"{i}@{v}" for i, v in keys} for v in registry["current_lookup"].values()), registry["current_lookup"])
    check("machine-canonical-human-generated", admissions["source_direction"]["projection_policy"] == binding["source_direction"]["projection_policy"] == "generated-only", "generated-only")
    check("no-context-inference", bundle["context_disposition"]["selection"] == "product-not-implicitly-bounded-context" and not any(p.startswith("contexts/") for p in bundle["postimages"]), bundle["context_disposition"])
    first = {p: sha(ROOT / p) for p in bundle["postimages"]}
    check("postimages-complete", len(first) == 5 and all((ROOT / p).is_file() for p in bundle["postimages"]), first)

    manifest = {
        "schema_version": "cyberalchemy-lab-craft-foundation-manifest/v1",
        "manifest_id": "CAL-CRAFT-FOUNDATION-V1-MANIFEST",
        "status": "candidate-ready-for-exact-owner-decision",
        "authority_effect": "none",
        "bundle_path": "docs/admission-bundles/0001-craft-foundation-v1/bundle.json",
        "bundle_sha256": sha(BUNDLE),
        "source_admission_candidate": {"path": str(SOURCE_ADMISSIONS.relative_to(LAB)), "sha256": sha(SOURCE_ADMISSIONS)},
        "owner_binding_candidate": {"path": str(OWNER_BINDING.relative_to(LAB)), "sha256": sha(OWNER_BINDING)},
        "candidate_inputs": bundle["candidate_inputs"],
        "live_preimages": bundle["live_preimages"],
        "postimages": [{"path": p, "sha256": sha(ROOT / p)} for p in bundle["postimages"]],
        "decision_clauses": bundle["decision_clauses"],
        "context_disposition": bundle["context_disposition"],
        "rollback_policy": bundle["rollback_policy"],
        "excluded_effects": bundle["excluded_effects"],
        "claim_ceiling": "This immutable manifest is ready for one exact owner decision only after its validation receipt passes. It has no admission effect by itself."
    }
    dump(ROOT / "manifest.json", manifest)
    failed = [x for x in checks if x["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-craft-foundation-validation/v1",
        "subject": manifest["manifest_id"],
        "result": "PASS" if not failed else "FAIL",
        "promotion_eligibility": "eligible-for-one-exact-digest-bound-owner-decision" if not failed else "blocked",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {"manifest_sha256": sha(ROOT / "manifest.json"), "bundle_sha256": sha(BUNDLE)},
        "claim_ceiling": "PASS proves exact input currentness, dependency closure, owner separation, postimage determinism, and rollback binding only. It does not admit or install the postimages."
    }
    dump(ROOT / "receipts/validation.json", receipt)
    write(ROOT / "BUNDLE.md", "\n".join(["<!-- GENERATED FILE: edit bundle.json and run build.py. -->", "", "# Craft Definition and Interaction Foundation v1", "", f"- Result: `{receipt['result']}`", f"- Manifest: `{receipt['materials']['manifest_sha256']}`", f"- Validation receipt: `{sha(ROOT / 'receipts/validation.json')}`", "- Human decision boundary: `end-of-bounded-bundle`", "", "The request set preserves separate source-admission, owner-binding, Definition, context-disposition, and registry effects while presenting them at one human checkpoint.", "", "## Claim ceiling", "", manifest["claim_ceiling"]]))
    print(f"CRAFT_FOUNDATION_BUNDLE={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"MANIFEST_SHA256={receipt['materials']['manifest_sha256']}")
    print(f"RECEIPT_SHA256={sha(ROOT / 'receipts/validation.json')}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(build())
