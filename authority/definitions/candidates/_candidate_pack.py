#!/usr/bin/env python3
"""Candidate-only rendering and collect-all validation for Definition packs."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import jsonschema


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


def selected_bytes(path: Path, selector: dict[str, Any]) -> bytes:
    kind = selector["kind"]
    if kind == "whole-file":
        return path.read_bytes()
    if kind == "line-range":
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        return "".join(lines[selector["start"] - 1 : selector["end"]]).encode()
    raise ValueError(f"unsupported selector kind: {kind}")


def definition_generator(lab: Path):
    path = lab / "authority/artifact-types/definition/v1/generator.py"
    spec = importlib.util.spec_from_file_location("cal_definition_generator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def registry_postimage(root: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    lab = root.parents[3]
    live = load(lab / candidate["predecessor_registry"]["path"])
    entries = list(live["entries"])
    lookup = dict(live["current_lookup"])
    for item in candidate["definitions"]:
        source = lab / item["path"]
        record = load(source)
        entries.append({
            "definition_id": record["definition_id"],
            "version": record["version"],
            "term": record["term"],
            "path": item["path"],
            "sha256": sha(source),
            "lifecycle_state": "candidate-unadmitted",
        })
        lookup[record["definition_id"]] = f"{record['definition_id']}@{record['version']}"
    entries.sort(key=lambda x: (x["definition_id"], x["version"]))
    return {
        "schema_version": "cyberalchemy-lab-definition-registry-postimage/v1",
        "record_id": candidate["registry_postimage_id"],
        "status": "candidate-postimage",
        "authority_effect": "none",
        "owner_ref": "role:definition-owner",
        "predecessor": candidate["predecessor_registry"],
        "candidate_source": "candidate.json",
        "entries": entries,
        "proposed_current_lookup": dict(sorted(lookup.items())),
        "source_direction": {
            "canonical": "registry-postimage.json",
            "human_projection": "DEFINITIONS-INDEX.md",
            "projection_policy": "generated-only",
            "generator_ref": candidate["source_direction"]["generator_ref"],
            "generator_sha256": sha(root / "render.py"),
        },
        "claim_ceiling": candidate["registry_claim_ceiling"],
    }


def render_registry(data: dict[str, Any], title: str) -> str:
    lines = [
        "<!-- GENERATED FILE: edit machine sources and run render.py. -->",
        "",
        f"# {title} proposed Definition index",
        "",
        "> Candidate projection; the live canonical registry remains unchanged.",
        "",
        f"- Record: `{data['record_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "| ID | Version | Term | Lifecycle | Path | Digest |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in data["entries"]:
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | `{item['lifecycle_state']}` | `{item['path']}` | `{item['sha256']}` |")
    lines.extend(["", "## Proposed current lookup", ""])
    for key, value in data["proposed_current_lookup"].items():
        lines.append(f"- `{key}` -> `{value}`")
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def render_drift(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Candidate evidence; this view is not canonical.",
        "",
        "## Summary",
        "",
    ]
    lines.extend(f"- {k.replace('_', ' ').title()}: `{v}`" for k, v in data["summary"].items())
    lines.extend(["", "## Findings", ""])
    for item in data["findings"]:
        lines.extend([
            f"### {item['finding_id']} ({item['severity']}, {item['status']})",
            "",
            item["condition"],
            "",
            f"Target: `{item['target']}`",
            "",
            f"Remediation: {item['remediation']}",
            "",
        ])
    lines.extend(["## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def render_candidate(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit candidate.json and run render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Machine-canonical candidate with no admission or authority effect.",
        "",
        f"- Candidate: `{data['candidate_id']}`",
        f"- Status: `{data['status']}`",
        f"- Semantic owner: `{data['semantic_owner_ref']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Definitions",
        "",
        "| ID | Version | Disposition | Path |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["definitions"]:
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | `{item['disposition']}` | `{item['path']}` |")
    lines.extend(["", "## Ownership boundary", "", data["ownership_boundary"], "", "## Promotion blockers", ""])
    if data["promotion_blockers"]:
        lines.extend(f"- {item}" for item in data["promotion_blockers"])
    else:
        lines.append("- None before exact owner review; validation is still not admission.")
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def render(root: Path) -> None:
    candidate = load(root / "candidate.json")
    lab = root.parents[3]
    generator = definition_generator(lab)
    for item in candidate["definitions"]:
        source = lab / item["path"]
        projection = lab / item["human_projection_path"]
        write(projection, generator.render(load(source)))
    registry = registry_postimage(root, candidate)
    dump(root / "registry-postimage.json", registry)
    write(root / "DEFINITIONS-INDEX.md", render_registry(registry, candidate["title"]))
    drift = load(root / "drift-audit-postimage.json")
    write(root / "DEFINITION-DRIFT-AUDIT.md", render_drift(drift))
    write(root / "CANDIDATE.md", render_candidate(candidate))


def hostile_failures(subject: dict[str, Any]) -> set[str]:
    failures: set[str] = set()
    if subject.get("kind") == "decision-checkpoint" and subject.get("authority_effect") != "none":
        failures.add("checkpoint-must-not-carry-authority")
    if subject.get("kind") == "user-decision-preference" and subject.get("changes_authority_scope") is True:
        failures.add("preference-must-not-widen-authority")
    if subject.get("kind") == "decision-request-set" and subject.get("merges_member_authority") is True:
        failures.add("request-set-must-not-merge-authority")
    if subject.get("kind") == "representation-revision" and subject.get("normative_meaning_equal") is True and subject.get("semantic_epoch_equal") is not True:
        failures.add("representation-only-change-must-not-create-semantic-epoch")
    if subject.get("kind") == "derived-refresh" and subject.get("canonical_input_digest_unchanged") is not True:
        failures.add("derived-refresh-must-not-change-canonical-input")
    return failures


def validate(root: Path, expected_ids: set[str]) -> int:
    candidate = load(root / "candidate.json")
    lab = root.parents[3]
    source_repo = Path("/home/vrondelli/projects/domainspec-core")
    schema_path = lab / "authority/artifact-types/definition/v1/schema.json"
    generator_path = lab / "authority/artifact-types/definition/v1/generator.py"
    schema = load(schema_path)
    schema_validator = jsonschema.Draft202012Validator(schema)
    generator = definition_generator(lab)
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("candidate-no-authority-effect", candidate["authority_effect"] == "none", candidate["authority_effect"])
    check("definition-schema-current", sha(schema_path) == candidate["definition_contract"]["schema_sha256"], sha(schema_path))
    check("definition-generator-current", sha(generator_path) == candidate["definition_contract"]["generator_sha256"], sha(generator_path))
    live_path = lab / candidate["predecessor_registry"]["path"]
    live = load(live_path)
    check("live-registry-preserved", sha(live_path) == candidate["predecessor_registry"]["sha256"] and len(live["entries"]) == candidate["predecessor_registry"]["entry_count"], {"sha256": sha(live_path), "entries": len(live["entries"])})

    records: dict[str, dict[str, Any]] = {}
    projection_results = []
    digest_results = []
    identity_results = []
    schema_errors = {}
    for item in candidate["definitions"]:
        path = lab / item["path"]
        projection = lab / item["human_projection_path"]
        record = load(path)
        records[record["definition_id"]] = record
        identity_results.append({
            "manifest_id": item["definition_id"],
            "record_id": record["definition_id"],
            "manifest_version": item["version"],
            "record_version": record["version"],
            "match": item["definition_id"] == record["definition_id"] and item["version"] == record["version"],
        })
        schema_errors[record["definition_id"]] = [error.message for error in schema_validator.iter_errors(record)]
        expected_projection = generator.render(record)
        projection_results.append({"id": record["definition_id"], "exists": projection.is_file(), "parity": projection.is_file() and projection.read_text(encoding="utf-8") == expected_projection, "deterministic": expected_projection == generator.render(record)})
        digest_results.append({"id": record["definition_id"], "sha256": sha(path)})
    check("exact-definition-set", set(records) == expected_ids and len(records) == len(candidate["definitions"]), sorted(records))
    check("manifest-definition-identities", all(x["match"] for x in identity_results), identity_results)
    check("semantic-owner-consistency", all(r["semantic_owner_ref"] == candidate["semantic_owner_ref"] for r in records.values()), {key: value["semantic_owner_ref"] for key, value in records.items()})
    check("all-schema-valid", all(not errors for errors in schema_errors.values()), schema_errors)
    check("three-voice-contract", all(r["voices"]["plain_language"]["normative"] is False and r["voices"]["domain_context"]["normative"] is False and r["voices"]["scientific_formal"]["normative_statement"] for r in records.values()), sorted(records))
    check("machine-canonical-human-generated", all(r["source_direction"]["canonical"] == "definition.json" and r["source_direction"]["projection_policy"] == "generated-only" for r in records.values()), sorted(records))
    check("definition-projection-parity", all(x["exists"] and x["parity"] and x["deterministic"] for x in projection_results), projection_results)

    binding_by_id = {item["source_ref"]: item for item in candidate["source_bindings"]}
    binding_results = []
    for source_id, binding in binding_by_id.items():
        base = lab if binding["repository"] == "CyberAlchemy-lab" else source_repo
        path = base / binding["path"]
        actual = hashlib.sha256(selected_bytes(path, binding["selector"])).hexdigest()
        binding_results.append({"source_ref": source_id, "expected": binding["sha256"], "actual": actual, "current": actual == binding["sha256"]})
    check("source-bindings-current", all(x["current"] for x in binding_results), binding_results)
    source_ref_results = []
    for record in records.values():
        for source in record["source_refs"]:
            binding = binding_by_id.get(source["source_ref"])
            source_ref_results.append({"definition_id": record["definition_id"], "source_ref": source["source_ref"], "known": binding is not None, "digest_match": binding is not None and source["content_sha256"] == binding["sha256"], "posture_match": binding is not None and source["admission_posture"] == binding["admission_posture"]})
    check("definition-source-closure", all(x["known"] and x["digest_match"] and x["posture_match"] for x in source_ref_results), source_ref_results)

    expected_registry = registry_postimage(root, candidate)
    registry_path = root / "registry-postimage.json"
    actual_registry = load(registry_path)
    check("registry-postimage-current", actual_registry == expected_registry, {"entries": len(actual_registry["entries"]), "sha256": sha(registry_path)})
    check("generated-index-parity", (root / "DEFINITIONS-INDEX.md").read_text(encoding="utf-8") == render_registry(actual_registry, candidate["title"]).rstrip() + "\n", sha(root / "DEFINITIONS-INDEX.md"))
    drift = load(root / "drift-audit-postimage.json")
    check("generated-drift-parity", (root / "DEFINITION-DRIFT-AUDIT.md").read_text(encoding="utf-8") == render_drift(drift).rstrip() + "\n", sha(root / "DEFINITION-DRIFT-AUDIT.md"))
    check("candidate-projection-parity", (root / "CANDIDATE.md").read_text(encoding="utf-8") == render_candidate(candidate).rstrip() + "\n", sha(root / "CANDIDATE.md"))

    fixture_results = []
    for path in sorted((root / "fixtures/invalid").glob("*.json")):
        fixture = load(path)
        failures = hostile_failures(fixture["subject"])
        fixture_results.append({"fixture_id": fixture["fixture_id"], "expected_rule": fixture["expected_rule"], "failures": sorted(failures), "rejected": fixture["expected_rule"] in failures})
    check("hostile-fixtures-rejected", len(fixture_results) == len(candidate["hostile_fixture_rules"]) and all(x["rejected"] for x in fixture_results), fixture_results)
    check("hostile-rule-coverage", {x["expected_rule"] for x in fixture_results} == set(candidate["hostile_fixture_rules"]), fixture_results)

    failed = [x for x in checks if x["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    promotion = "not-eligible" if result == "FAIL" else ("blocked-by-declared-dependencies" if candidate["promotion_blockers"] else "eligible-for-exact-owner-review")
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-candidate-validation/v1",
        "subject": candidate["candidate_id"],
        "result": result,
        "promotion_eligibility": promotion,
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "total": len(checks), "failed": len(failed)},
        "materials": {
            "candidate_json_sha256": sha(root / "candidate.json"),
            "candidate_md_sha256": sha(root / "CANDIDATE.md"),
            "definition_digests": {x["id"]: x["sha256"] for x in digest_results},
            "registry_postimage_sha256": sha(registry_path),
            "drift_audit_postimage_sha256": sha(root / "drift-audit-postimage.json"),
        },
        "promotion_blockers": candidate["promotion_blockers"],
        "claim_ceiling": "PASS proves candidate structure, exact selected sources, three voices, deterministic projections, synchronized proposed registry state, and hostile-fixture rejection only. It does not admit a Definition, select a bounded context, migrate authority, authorize execution, publish, release, or deploy.",
    }
    dump(root / "receipts/validation.json", receipt)
    print(f"DEFINITION_CANDIDATE_VALIDATION={result}")
    print(f"PROMOTION_ELIGIBILITY={promotion}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    if failed:
        print("FAILED=" + ",".join(x["check_id"] for x in failed))
    return 0 if result == "PASS" else 1
