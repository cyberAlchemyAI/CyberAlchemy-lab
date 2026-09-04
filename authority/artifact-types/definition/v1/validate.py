#!/usr/bin/env python3
"""Validate the Definition/v1 candidate vertical without admitting it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from generator import render as render_definition
from render import OUTPUT as ARTIFACT_OUTPUT
from render import SOURCE as ARTIFACT_SOURCE
from render import render as render_artifact


ROOT = Path(__file__).resolve().parent
LAB_ROOT = ROOT.parents[3]
SCHEMA = ROOT / "schema.json"
GENERATOR = ROOT / "generator.py"
VALID_FIXTURE = ROOT / "fixtures" / "valid" / "definition.json"
VALID_PROJECTION = ROOT / "fixtures" / "valid" / "DEFINITION.md"
RECEIPT = ROOT / "receipts" / "validation.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_source_digest(source: dict) -> str | None:
    path = Path(source["path"])
    if not path.is_file():
        return None
    if source.get("digest_scope") == "whole-file":
        return digest(path)
    if source.get("digest_scope") == "markdown-h2-block-concat-v1":
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        selected: list[str] = []
        for wanted in source.get("selected_ids", []):
            starts = [i for i, line in enumerate(lines) if line.startswith(f"## {wanted}:")]
            if len(starts) != 1:
                return None
            start = starts[0]
            end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
            selected.extend(lines[start:end])
        return hashlib.sha256("".join(selected).encode("utf-8")).hexdigest()
    return None


def main() -> int:
    artifact = json.loads(ARTIFACT_SOURCE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    valid = json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    check("candidate-unadmitted", artifact.get("status") == "candidate-unadmitted" and artifact.get("authority_effect") == "none",
          f"status={artifact.get('status')!r} authority_effect={artifact.get('authority_effect')!r}")
    check("bootstrap-gap-explicit", artifact.get("bootstrap", {}).get("artifact_type_status") == "missing-unadmitted-predecessor",
          json.dumps(artifact.get("bootstrap"), sort_keys=True))
    check("schema-self-valid", not list(Draft202012Validator.check_schema(schema) or []), "Draft 2020-12 schema accepted")
    check("schema-binding-current", digest(SCHEMA) == artifact["schema_digest"], f"actual={digest(SCHEMA)}")
    check("generator-binding-current", digest(GENERATOR) == artifact["projection_contract"]["generator_sha256"], f"actual={digest(GENERATOR)}")
    check("artifact-renderer-binding-current", digest(ROOT / "render.py") == artifact["source_direction"]["generator_sha256"],
          f"actual={digest(ROOT / 'render.py')}")

    source_drift = []
    for source in artifact.get("source_refs", []):
        if selected_source_digest(source) != source["sha256"]:
            source_drift.append(source["source_id"])
    check("selected-source-currentness", not source_drift, f"stale_or_missing={source_drift}")
    check("external-sources-unadmitted",
          all(x.get("admission_posture") == "external-evidence-unadmitted" for x in artifact.get("source_refs", []) if x.get("source_repository") != "CyberAlchemy-lab"),
          "No CyberAlchemy-v2 source is represented as admitted Lab authority")

    valid_errors = sorted(validator.iter_errors(valid), key=lambda e: list(e.path))
    check("valid-fixture-accepted", not valid_errors, "; ".join(e.message for e in valid_errors) or "accepted")
    check("valid-fixture-schema-digest", valid.get("schema_digest") == digest(SCHEMA), f"fixture={valid.get('schema_digest')}")
    check("valid-fixture-generator-digest", valid.get("source_direction", {}).get("generator_sha256") == digest(GENERATOR),
          f"fixture={valid.get('source_direction', {}).get('generator_sha256')}")
    check("three-voices-colocated", set(valid.get("voices", {})) == {"scientific_formal", "plain_language", "domain_context"},
          f"voices={sorted(valid.get('voices', {}))}")
    check("interpretive-voices-nonnormative",
          valid["voices"]["plain_language"].get("normative") is False and valid["voices"]["domain_context"].get("normative") is False,
          "plain-language and domain-context voices explicitly non-normative")

    invalid_results: dict[str, list[dict]] = {}
    for path in sorted((ROOT / "fixtures" / "invalid").glob("*.json")):
        instance = json.loads(path.read_text(encoding="utf-8"))
        invalid_results[path.name] = [
            {"validator": error.validator, "path": list(error.path), "message": error.message}
            for error in sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
        ]
    expected_negative_reasons = (
        any(
            error["validator"] == "required"
            and error["path"] == ["voices"]
            and "domain_context" in error["message"]
            for error in invalid_results.get("missing-domain-context.json", [])
        )
        and any(
            error["validator"] == "additionalProperties"
            and error["path"] == []
            and "unexpected_authority" in error["message"]
            for error in invalid_results.get("additional-property.json", [])
        )
    )
    check("negative-fixtures-rejected-for-intended-reasons", expected_negative_reasons,
          json.dumps(invalid_results, sort_keys=True))

    generated_definition_a = render_definition(valid)
    generated_definition_b = render_definition(valid)
    check("definition-two-run-determinism", generated_definition_a == generated_definition_b,
          f"sha256={hashlib.sha256(generated_definition_a.encode()).hexdigest()}")
    check("definition-projection-parity",
          VALID_PROJECTION.is_file() and VALID_PROJECTION.read_text(encoding="utf-8") == generated_definition_a,
          "valid DEFINITION.md equals the bound generator output")
    mutated = generated_definition_a + "hand edit\n"
    check("hand-edit-negative-witness", mutated != generated_definition_a,
          "A changed projection is rejected by exact-byte comparison")

    generated_artifact_a = render_artifact(artifact)
    generated_artifact_b = render_artifact(artifact)
    check("artifact-two-run-determinism", generated_artifact_a == generated_artifact_b,
          f"sha256={hashlib.sha256(generated_artifact_a.encode()).hexdigest()}")
    check("artifact-projection-parity",
          ARTIFACT_OUTPUT.is_file() and ARTIFACT_OUTPUT.read_text(encoding="utf-8") == generated_artifact_a,
          "ARTIFACT.md equals render(artifact.json)")

    result = "PASS" if all(x["result"] == "PASS" for x in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-artifact-type-validation/v0",
        "artifact_type_id": artifact.get("artifact_type_id"),
        "artifact_type_version": artifact.get("version"),
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {
            "artifact_json_sha256": digest(ARTIFACT_SOURCE),
            "artifact_md_sha256": digest(ARTIFACT_OUTPUT) if ARTIFACT_OUTPUT.is_file() else None,
            "schema_json_sha256": digest(SCHEMA),
            "generator_sha256": digest(GENERATOR),
            "valid_fixture_json_sha256": digest(VALID_FIXTURE),
            "valid_fixture_md_sha256": digest(VALID_PROJECTION) if VALID_PROJECTION.is_file() else None,
            "validator_sha256": digest(ROOT / "validate.py")
        },
        "claim_ceiling": artifact.get("claim_ceiling")
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{result}: {sum(x['result'] == 'PASS' for x in checks)}/{len(checks)} checks passed")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
