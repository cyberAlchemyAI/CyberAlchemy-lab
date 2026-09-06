#!/usr/bin/env python3
"""Executable, read-only Artifact Surface candidate-2 resolver and auditor.

Package validation is the sole mode that writes, and it writes only the
candidate package's validation receipt. Resolution and audit emit JSON to
stdout and never modify the inspected subject.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import jsonschema


LAB = Path(__file__).resolve().parents[2]
GENERATOR = LAB / "tooling/generators/artifact_surface.py"
DEFINITION_REGISTRY = LAB / "authority/definitions/registry.json"
DEFAULT_REGISTRY = LAB / "authority/artifact-types/candidates/0001-artifact-surface-foundation/registry.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pointer_get(subject: Any, pointer: str) -> Any:
    if pointer == "":
        return subject
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON pointer: {pointer}")
    current = subject
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            return None
        current = current[token]
    return current


def resolve(registry: dict[str, Any], artifact: dict[str, Any], artifact_path: str) -> dict[str, Any]:
    """Resolve by declared classification or registered discriminator only."""
    admitted = list(registry["entries"])
    current = [entry for entry in admitted if entry["lifecycle_state"] == "admitted-current"]
    evidence: list[dict[str, Any]] = []
    matched: dict[str, dict[str, Any]] = {}

    explicit = pointer_get(artifact, "/classification/artifact_type_ref")
    if isinstance(explicit, str):
        hits = [entry for entry in admitted if entry["artifact_type_ref"] == explicit]
        evidence.append({"kind": "explicit-classification", "pointer": "/classification/artifact_type_ref", "value": explicit, "matches": [x["artifact_type_ref"] for x in hits]})
        for entry in hits:
            matched[entry["artifact_type_ref"]] = entry

    for entry in current:
        discriminator = entry["instance_discriminator"]
        actual = pointer_get(artifact, discriminator["path"])
        if actual == discriminator["value"]:
            matched[entry["artifact_type_ref"]] = entry
            evidence.append({"kind": "registry-discriminator", "pointer": discriminator["path"], "value": actual, "matches": [entry["artifact_type_ref"]]})

    matches = sorted(matched)
    outcome = "resolved" if len(matches) == 1 else "unresolved" if not matches else "ambiguous"
    return {
        "schema_version": "cyberalchemy-lab-artifact-type-resolution-result/v1",
        "artifact_path": artifact_path,
        "registry_id": registry["registry_id"],
        "outcome": outcome,
        "match_count": len(matches),
        "matches": matches,
        "matched_entries": [
            {
                "artifact_type_ref": matched[ref]["artifact_type_ref"],
                "lifecycle_state": matched[ref]["lifecycle_state"],
                "artifact_path": matched[ref]["artifact_path"],
                "artifact_sha256": matched[ref]["artifact_sha256"],
                "schema_path": matched[ref]["schema_path"],
                "schema_sha256": matched[ref]["schema_sha256"],
                "admission_decision_ref": matched[ref]["admission_decision_ref"],
            }
            for ref in matches
        ],
        "evidence": evidence,
        "inference_exclusions": ["directory", "filename", "extension", "nearest-name"],
        "authority_effect": "none",
    }


def audit(registry: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    blocked = 0
    for item in plan["entries"]:
        path = LAB / item["path"]
        if item["operation"] == "resolve-json":
            if not path.is_file():
                actual = "missing"
                resolution = None
            else:
                resolution = resolve(registry, load(path), item["path"])
                actual = resolution["outcome"]
            ok = actual == item["expected_outcome"]
            findings.append({
                "finding_id": item["finding_id"],
                "path": item["path"],
                "classification": actual,
                "expected": item["expected_outcome"],
                "result": "PASS" if ok else "BLOCK",
                "statement": item["statement"],
                "treatment": item["treatment"],
                "subject_sha256": sha(path) if path.is_file() else None,
                "resolution": resolution,
            })
        elif item["operation"] == "inventory-directory":
            files = sorted(str(p.relative_to(path)) for p in path.rglob("*") if p.is_file()) if path.is_dir() else []
            actual = "package-boundary-open" if path.is_dir() and files else "missing-or-empty"
            ok = actual == item["expected_outcome"]
            findings.append({
                "finding_id": item["finding_id"],
                "path": item["path"],
                "classification": actual,
                "expected": item["expected_outcome"],
                "result": "PASS" if ok else "BLOCK",
                "statement": item["statement"],
                "treatment": item["treatment"],
                "observed_file_count": len(files),
                "observed_files_sha256": hashlib.sha256("\n".join(files).encode()).hexdigest(),
            })
        elif item["operation"] == "check-represented-type-registration":
            if not path.is_file():
                actual = "missing"
                represented_ref = None
            else:
                represented_ref = load(path).get("artifact_type_ref")
                registered = {entry["artifact_type_ref"] for entry in registry["entries"]}
                actual = "registered" if represented_ref in registered else "candidate-type-not-admitted"
            ok = actual == item["expected_outcome"]
            findings.append({
                "finding_id": item["finding_id"],
                "path": item["path"],
                "classification": actual,
                "expected": item["expected_outcome"],
                "result": "PASS" if ok else "BLOCK",
                "statement": item["statement"],
                "treatment": item["treatment"],
                "represented_artifact_type_ref": represented_ref,
                "subject_sha256": sha(path) if path.is_file() else None,
            })
        else:
            raise ValueError(f"unsupported audit operation: {item['operation']}")
        if not ok:
            blocked += 1
    return {
        "schema_version": "cyberalchemy-lab-artifact-surface-audit/v2",
        "audit_id": plan["audit_id"],
        "title": plan["title"],
        "status": "candidate-diagnostic",
        "result": "PASS" if blocked == 0 else "BLOCK",
        "authority_effect": "none",
        "registry_ref": plan["registry_ref"],
        "plan_sha256": hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "summary": {"passed": len(findings) - blocked, "blocked": blocked, "total": len(findings)},
        "findings": findings,
        "claim_ceiling": "Computed selected-surface diagnostic only. It does not establish repository-wide conformance, choose package boundaries, admit types, or authorize migration.",
    }


def generator_module():
    spec = importlib.util.spec_from_file_location("artifact_surface_generator", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def manifest_semantic_failures(subject: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    entries = subject.get("surface_entries", [])
    paths = [entry.get("path") for entry in entries]
    if len(paths) != len(set(paths)):
        failures.append("surface-paths-must-be-unique")
    self_entries = [entry for entry in entries if entry.get("path") == "package.json"]
    if len(self_entries) != 1:
        failures.append("manifest-must-classify-itself-exactly-once")
    elif self_entries[0] != {"path": "package.json", "role": "canonical-instance", "artifact_type_ref": "cal.artifact-type.canonical-package-manifest/v1", "resolution_count": 1}:
        failures.append("manifest-self-entry-must-be-canonical")
    for entry in entries:
        canonical = entry.get("role") == "canonical-instance"
        if canonical and (not entry.get("artifact_type_ref") or entry.get("resolution_count") != 1):
            failures.append(f"canonical-entry-must-resolve:{entry.get('path')}")
        if not canonical and entry.get("artifact_type_ref") is not None:
            failures.append(f"noncanonical-entry-must-not-claim-type:{entry.get('path')}")
    return sorted(set(failures))


def registry_semantic_failures(subject: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    refs = [entry["artifact_type_ref"] for entry in subject.get("entries", [])]
    if len(refs) != len(set(refs)):
        failures.append("artifact-type-refs-must-be-unique")
    current = [entry for entry in subject.get("entries", []) if entry["lifecycle_state"] == "admitted-current"]
    keys = [(entry["instance_discriminator"]["path"], entry["instance_discriminator"]["value"]) for entry in current]
    if len(keys) != len(set(keys)):
        failures.append("current-discriminators-must-be-unique")
    return failures


def request_semantic_failures(subject: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    discriminator = subject.get("proposed_discriminator")
    matches = []
    if isinstance(discriminator, dict):
        for entry in registry["entries"]:
            if entry["lifecycle_state"] == "admitted-current" and entry["instance_discriminator"] == discriminator:
                matches.append(entry["artifact_type_ref"])
    if matches:
        failures.append("request-requires-zero-current-resolution-matches")
    if subject.get("resolution_evidence", {}).get("matches") != []:
        failures.append("request-declared-matches-must-be-empty")
    if subject.get("consumed_as_subject") is not False:
        failures.append("request-must-not-be-consumed-as-subject")
    return failures


def semantic_failures(subject: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    version = subject.get("schema_version")
    if version == "cyberalchemy-lab-canonical-package-manifest/v1":
        return manifest_semantic_failures(subject)
    if version == "cyberalchemy-lab-artifact-type-registry/v1":
        return registry_semantic_failures(subject)
    if version == "cyberalchemy-lab-artifact-type-request/v1":
        return request_semantic_failures(subject, registry)
    return []


def validate_package(root: Path, registry_path: Path) -> int:
    artifact = load(root / "artifact.json")
    schema = load(root / "schema.json")
    registry = load(registry_path)
    generator = generator_module()
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    check("candidate-non-effect", artifact.get("status") == "candidate-unadmitted" and artifact.get("authority_effect") == "none", {"status": artifact.get("status"), "authority_effect": artifact.get("authority_effect")})
    check("schema-digest-current", artifact.get("schema_digest") == sha(root / "schema.json"), {"declared": artifact.get("schema_digest"), "actual": sha(root / "schema.json")})
    check("closed-instance-schema", schema.get("type") == "object" and schema.get("additionalProperties") is False, {"type": schema.get("type"), "additionalProperties": schema.get("additionalProperties")})
    refs = set(artifact["semantic_definition_refs"])
    bindings = {item["definition_ref"]: item for item in artifact["semantic_definition_bindings"]}
    check("definition-ref-closure", refs == set(bindings), {"refs": sorted(refs), "bindings": sorted(bindings)})
    live = {f"{item['definition_id']}@{item['version']}": item for item in load(DEFINITION_REGISTRY)["entries"] if item["lifecycle_state"] == "admitted"}
    binding_results = []
    for ref, binding in bindings.items():
        path = LAB / binding["path"]
        actual = sha(path) if path.is_file() else "missing"
        admitted = ref in live
        ok = path.is_file() and actual == binding["sha256"] and ((admitted and binding["admission_posture"] == "admitted") or (not admitted and binding["admission_posture"] == "candidate-unadmitted"))
        binding_results.append({"definition_ref": ref, "ok": ok, "actual": actual})
    check("semantic-bindings-current", all(item["ok"] for item in binding_results), binding_results)

    positive_path = root / artifact["validation_contract"]["positive_witness"]
    positive = load(positive_path)
    schema_errors = sorted(error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(positive))
    semantic_errors = semantic_failures(positive, registry)
    check("positive-witness-valid", not schema_errors and not semantic_errors, {"schema": schema_errors, "semantic": semantic_errors})

    negative_results = []
    for relative in artifact["validation_contract"]["negative_witnesses"]:
        subject = load(root / relative)
        errors = sorted(error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(subject))
        semantics = semantic_failures(subject, registry)
        negative_results.append({"path": relative, "rejected": bool(errors or semantics), "schema": errors, "semantic": semantics})
    check("hostile-fixtures-rejected", bool(negative_results) and all(item["rejected"] for item in negative_results), negative_results)

    artifact_projection = root / "ARTIFACT.md"
    witness_projection = root / artifact["validation_contract"]["positive_projection"]
    check("artifact-projection-parity", artifact_projection.is_file() and artifact_projection.read_text(encoding="utf-8") == generator.render_artifact(artifact), sha(artifact_projection) if artifact_projection.is_file() else "missing")
    check("witness-projection-parity", witness_projection.is_file() and witness_projection.read_text(encoding="utf-8") == generator.render_instance(artifact, positive), sha(witness_projection) if witness_projection.is_file() else "missing")
    source = artifact["source_direction"]
    check("shared-generator-current", source["shared_generator_path"] == str(GENERATOR.relative_to(LAB)) and source["shared_generator_sha256"] == sha(GENERATOR), source)
    validator = artifact["validation_contract"]
    check("shared-validator-current", validator["shared_validator_path"] == str(Path(__file__).relative_to(LAB)) and validator["shared_validator_sha256"] == sha(Path(__file__)), validator)

    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-surface-type-validation/v2",
        "subject": artifact["artifact_type_ref"],
        "candidate_version": artifact["version"],
        "result": "PASS" if not blocked else "BLOCK",
        "authority_effect": "none",
        "assessment": {"schema_conformance": "PASS" if not blocked else "NOT_ESTABLISHED", "admission_posture": "candidate-unadmitted", "implementation_conformance": "PASS" if not blocked else "NOT_ESTABLISHED", "runtime_conformance": "not_evaluable"},
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "materials": {"artifact_sha256": sha(root / "artifact.json"), "schema_sha256": sha(root / "schema.json"), "positive_witness_sha256": sha(positive_path), "registry_sha256": sha(registry_path)},
        "claim_ceiling": "PASS proves candidate schema, semantic checks, executable bindings, and fixture behavior for this exact package only. It does not admit the Artifact Type or any instance.",
    }
    dump(root / "receipts/validation.json", receipt)
    print(f"{artifact['artifact_type_id'].upper().replace('.', '_').replace('-', '_')}={receipt['result']}")
    return 0 if not blocked else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    resolver = sub.add_parser("resolve")
    resolver.add_argument("--registry", type=Path, required=True)
    resolver.add_argument("--artifact", type=Path, required=True)
    auditor = sub.add_parser("audit")
    auditor.add_argument("--registry", type=Path, required=True)
    auditor.add_argument("--plan", type=Path, required=True)
    package = sub.add_parser("validate-package")
    package.add_argument("package", type=Path)
    package.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()
    if args.command == "resolve":
        print(json.dumps(resolve(load(args.registry.resolve()), load(args.artifact.resolve()), str(args.artifact)), indent=2, sort_keys=True))
        return 0
    if args.command == "audit":
        result = audit(load(args.registry.resolve()), load(args.plan.resolve()))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["result"] == "PASS" else 1
    return validate_package(args.package.resolve(), args.registry.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
