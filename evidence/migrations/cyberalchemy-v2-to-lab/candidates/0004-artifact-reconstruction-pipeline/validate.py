#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

import author


ROOT = Path(__file__).resolve().parent


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def all_authority_effects(value) -> list:
    results = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "authority_effect":
                results.append(child)
            results.extend(all_authority_effects(child))
    elif isinstance(value, list):
        for child in value:
            results.extend(all_authority_effects(child))
    return results


def render_receipt(receipt: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is validation.json. -->",
        "",
        "# Artifact Reconstruction Pipeline Validation",
        "",
        f'- Result: `{receipt["result"]}`',
        f'- Checks: `{receipt["summary"]["passed"]}/{receipt["summary"]["total"]}`',
        f'- Authority effect: `{receipt["authority_effect"]}`',
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    for item in receipt["checks"]:
        lines.append(f'| `{item["check_id"]}` | `{item["result"]}` | {item["detail"]} |')
    lines += ["", "## Claim ceiling", "", receipt["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> None:
    checks = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "BLOCK", "detail": detail})

    candidate = load(ROOT / "candidate.json")
    plan = load(ROOT / "implementation-layering.json")
    registry = load(ROOT / "registry.json")
    relations = load(ROOT / "relations.json")
    drift = load(ROOT / "drift-audit.json")
    manifest = load(ROOT / "manifest.json")
    decision = load(author.DECISION)
    d65 = load(author.D65)
    target_index = load(author.TARGET_INDEX)
    definition_path = ROOT / "definitions/prototype-first-domainspec-construction-invariant/v1/definition.json"
    definition = load(definition_path)
    definition_renderer = author.module(author.DEFINITION_GENERATOR, "definition_generator_validation")
    artifact_renderer = author.module(author.ARTIFACT_GENERATOR, "artifact_generator_validation")
    shared_validator = author.module(author.ARTIFACT_VALIDATOR, "artifact_validator_validation")

    check(
        "approved-planning-input-current",
        decision["status"] == "selected-planning-baseline"
        and decision["decision_effect"]["d65_successor"] == "selected-as-normalization-planning-baseline"
        and candidate["predecessor_decision"]["sha256"] == sha(author.DECISION),
        "The exact selected 0003 planning decision is current and bound.",
    )
    selected_d65_targets = [item["target_id"] for item in d65["recommended_targets"]]
    registry_normalized = {item["target_id"] for item in registry["entries"] if item["normalized_target"]}
    check(
        "d65-target-closure",
        set(selected_d65_targets) <= registry_normalized
        and len(selected_d65_targets) == 6
        and registry["normalized_target_count"] == 7,
        "All six selected D65 targets plus the Evaluation dependency are represented once.",
    )
    source_target_ids = {item["target_id"] for item in target_index["entries"]}
    check(
        "approved-backlog-dependency",
        "type.evaluation" in source_target_ids
        and "type.evaluation" in registry_normalized
        and candidate["target_counts"]["dependency_from_approved_backlog"] == 1,
        "The additional Evaluation target comes from the already selected 176-target refinement baseline.",
    )
    support = [item for item in registry["entries"] if not item["normalized_target"]]
    check(
        "profile-result-orthogonality",
        len(support) == 1
        and support[0]["target_id"] == "support.evaluation-profile-v2"
        and support[0]["predecessor_ref"] == "cal.artifact-type.evaluation-profile/v1"
        and candidate["dependency_resolution"]["evaluation_target"] == "type.evaluation"
        and candidate["dependency_resolution"]["profile_carrier"] == "cal.artifact-type.evaluation-profile/v2",
        "Evaluation results and Evaluation Profiles use distinct successor-compatible carriers.",
    )

    definition_schema = load(author.DEFINITION_SCHEMA)
    definition_errors = list(Draft202012Validator(definition_schema).iter_errors(definition))
    check("definition-schema", not definition_errors, "The D65 Definition conforms to admitted Definition/v1 shape.")
    check(
        "definition-voices",
        set(definition["voices"]) == {"scientific_formal", "plain_language", "domain_context"}
        and definition["voices"]["plain_language"]["normative"] is False
        and definition["voices"]["domain_context"]["normative"] is False,
        "Scientific/formal, plain-language, and Lab domain-context voices are colocated and bounded.",
    )
    check(
        "definition-projection",
        (definition_path.parent / "DEFINITION.md").read_text(encoding="utf-8")
        == definition_renderer.render(definition),
        "The Definition human view is generated exactly from definition.json.",
    )
    actual_section_sha = hashlib.sha256(
        author.markdown_h2_section(author.CAV2_DEFINITIONS, definition["source_refs"][0]["selector"])
    ).hexdigest()
    check(
        "definition-source-current",
        actual_section_sha == definition["source_refs"][0]["content_sha256"]
        and drift["selected_source_current"] is True,
        "The selected CAV2-D65 section bytes remain exact.",
    )
    check(
        "definition-boundaries",
        len(definition["boundaries"]) == 4
        and any("Evaluation Profile" in item and "Evaluation" in item for item in definition["boundaries"]),
        "Carrier, binding, profile, and result meanings are explicitly non-collapsed.",
    )

    type_roots = sorted((ROOT / "artifact-types").glob("*/v*"))
    shared_results = []
    for type_root in type_roots:
        try:
            shared_results.append((type_root, shared_validator.validate_package(type_root)))
        except Exception as exc:
            shared_results.append((type_root, f"exception:{exc}"))
    check(
        "artifact-type-shared-validation",
        len(shared_results) == 5 and all(result == 0 for _, result in shared_results),
        "All five Artifact Types pass the existing shared Lab validator and hostile fixtures.",
    )
    artifacts = [load(path / "artifact.json") for path in type_roots]
    check(
        "artifact-type-definition-bindings",
        all(item["semantic_definition_refs"] for item in artifacts)
        and all(item["authority_effect"] == "none" for item in artifacts),
        "Every new Artifact Type has semantic Definition bindings and no authority effect.",
    )
    schema_versions = []
    for type_root in type_roots:
        schema = load(type_root / "schema.json")
        const = schema["properties"]["schema_version"]["const"]
        schema_versions.append(const)
    check(
        "content-resolution-discriminators",
        len(schema_versions) == len(set(schema_versions)) == 5,
        "Every candidate Artifact Type has one unique content discriminator independent of directory placement.",
    )

    profile_paths = sorted((ROOT / "profiles").glob("*/v1/profile.json"))
    profile_schema = load(ROOT / "artifact-types/evaluation-profile/v2/schema.json")
    profiles = [load(path) for path in profile_paths]
    profile_errors = [
        list(Draft202012Validator(profile_schema).iter_errors(profile))
        for profile in profiles
    ]
    check(
        "profile-schema-closure",
        len(profiles) == 2 and all(not errors for errors in profile_errors),
        "Both selected D65 evaluation profiles conform to the generalized Evaluation Profile/v2 candidate.",
    )
    evaluation_profile_artifact = load(ROOT / "artifact-types/evaluation-profile/v2/artifact.json")
    check(
        "profile-projection-closure",
        all(
            path.with_name("PROFILE.md").read_text(encoding="utf-8")
            == artifact_renderer.render_instance(evaluation_profile_artifact, profile)
            for path, profile in zip(profile_paths, profiles)
        ),
        "Both profile human views are exact generated projections.",
    )
    check(
        "profile-decision-separation",
        all(
            "approve" in profile["claim_ceiling"]
            and ("cannot" in profile["claim_ceiling"] or "does not" in profile["claim_ceiling"])
            for profile in profiles
        )
        and all(profile["evaluation_mode"] == "collect-all" for profile in profiles),
        "Profiles collect all results and cannot grant product approval or post-approval authority.",
    )

    expected_relations = set(d65["reused_normalized_relations"])
    check(
        "relation-reuse-only",
        {item["relation_id"] for item in relations["relations"]} == expected_relations
        and all(item["posture"] == "reuse-normalized-identity-no-new-axis" for item in relations["relations"]),
        "Exactly six selected relation identities are reused; no relation kind is minted.",
    )
    check(
        "registry-identity-closure",
        len(registry["entries"]) == 8
        and len({item["target_id"] for item in registry["entries"]}) == 8
        and len({item["proposed_home"] for item in registry["entries"]}) == 8
        and all(sha(author.LAB / item["candidate_path"]) == item["candidate_sha256"] for item in registry["entries"]),
        "Eight candidate identities and proposed homes are unique and digest-bound.",
    )
    check(
        "candidate-only-authority",
        set(all_authority_effects({"candidate": candidate, "registry": registry, "relations": relations, "definition": definition, "profiles": profiles, "artifacts": artifacts})) == {"none"},
        "Every candidate authority_effect remains none.",
    )
    check(
        "layering-complete",
        [item["layer_id"] for item in plan["layers"]] == ["L0", "L1", "L2", "L3"]
        and all(item["decision_question"].startswith("After this layer, we know whether") for item in plan["layers"]),
        "Four evidence-gated layers expose distinct decision questions and deferrals.",
    )

    expected_projections = {
        "CANDIDATE.md": author.render_candidate(candidate),
        "IMPLEMENTATION-LAYERING.md": author.render_plan(plan),
        "REGISTRY.md": author.render_registry(registry),
        "RELATIONS.md": author.render_relations(relations),
        "DRIFT-AUDIT.md": author.render_drift(drift),
        "MANIFEST.md": author.render_manifest(manifest),
    }
    check(
        "top-level-projections",
        all((ROOT / path).read_text(encoding="utf-8") == value for path, value in expected_projections.items()),
        "Every top-level human view is generated from canonical machine data.",
    )
    check(
        "manifest-material-closure",
        all((ROOT / item["path"]).is_file() and sha(ROOT / item["path"]) == item["sha256"] for item in manifest["materials"]),
        "Every candidate material matches the immutable manifest digest.",
    )
    source_roots = {"cyberalchemy-lab": author.LAB, "cyberalchemy-v2-source": author.SOURCE}
    check(
        "manifest-source-closure",
        all((source_roots[item["repository_id"]] / item["path"]).is_file() and sha(source_roots[item["repository_id"]] / item["path"]) == item["sha256"] for item in manifest["source_bindings"]),
        "Every selected Lab and CyberAlchemy-v2 source binding is current.",
    )
    check(
        "claim-ceiling",
        candidate["authority_effect"] == "none"
        and "does not admit or install" in candidate["claim_ceiling"]
        and candidate["status"] == "prototype-construction-candidate",
        "The tested object remains a prototype construction candidate, not an admitted product or runtime.",
    )

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    family_counts = Counter(item["family"] for item in registry["entries"])
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-reconstruction-validation/v1",
        "candidate_id": candidate["candidate_id"],
        "result": result,
        "checks": checks,
        "summary": {
            "passed": sum(item["result"] == "PASS" for item in checks),
            "total": len(checks),
            "normalized_targets": registry["normalized_target_count"],
            "supporting_artifacts": registry["supporting_artifact_count"],
            "artifact_types": family_counts["artifact-type"] + family_counts["artifact-type-successor"],
            "definitions": family_counts["definition"],
            "profiles": family_counts["profile"],
            "reused_relations": len(relations["relations"]),
        },
        "authority_effect": "none",
        "claim_ceiling": "PASS proves the exact L0 reconstruction vertical, its dependency closure, schemas, hostile fixtures, generated projections, and source bindings. It does not admit or install artifacts, activate a registry or runtime, execute migration, commit, push, publish, release, or deploy.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    (ROOT / "receipts/VALIDATION.md").write_text(render_receipt(receipt), encoding="utf-8")
    print(f"ARTIFACT_RECONSTRUCTION_PIPELINE={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    if result != "PASS":
        for item in checks:
            if item["result"] != "PASS":
                print(f"BLOCK {item['check_id']}: {item['detail']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
