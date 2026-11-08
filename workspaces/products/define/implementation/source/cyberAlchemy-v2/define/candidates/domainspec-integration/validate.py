#!/usr/bin/env python3
"""Validate the candidate DomainSpec integration Definition Pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECTS = HERE.parents[3]
PACK = HERE / "DOMAINSPEC-INTEGRATION-DEFINITION-PACK.v1-candidate.json"
VOICES = {
    "normative_voice",
    "formal_voice",
    "plain_language_voice",
    "domain_context_voice",
    "boundary",
}
REQUIRED_AXIOMS = {
    "entity != table",
    "value-object != record",
    "domain-event != message",
    "operation != endpoint",
    "operation != message-consumer",
    "query != external-api-call",
    "dependency-contract != provider-adapter",
    "queue != topic",
    "topic != stream",
    "provider-acceptance != transport-delivery",
    "transport-delivery != application-commit",
    "application-commit != business-completion",
    "runtime-receipt != external-effect",
    "failure-classification != continuation-selection",
    "orodi-observation != runtime-control",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads(PACK.read_text(encoding="utf-8"))
    if data.get("schema_version") != "cav2-define-definition-pack/v1-candidate":
        fail("unexpected schema_version")
    if data.get("status") != "candidate":
        fail("pack status must remain candidate")

    concepts = data.get("concepts", [])
    ids = [concept.get("concept_id") for concept in concepts]
    required = data.get("required_concept_ids", [])
    if len(ids) != len(set(ids)):
        fail("duplicate concept_id")
    if len(required) != len(set(required)):
        fail("duplicate required_concept_id")
    if set(ids) != set(required):
        fail(f"required concept mismatch: missing={sorted(set(required) - set(ids))}, extra={sorted(set(ids) - set(required))}")

    known = set(ids)
    for concept in concepts:
        concept_id = concept["concept_id"]
        disposition = concept.get("current_disposition")
        if disposition not in {"reuse", "specialize", "propose"}:
            fail(f"{concept_id}: invalid disposition {disposition!r}")
        definition = concept.get("definition", {})
        if set(definition) != VOICES or any(not str(definition[key]).strip() for key in VOICES):
            fail(f"{concept_id}: incomplete definition voices")
        if disposition == "reuse":
            for key in ("canonical_source_ref", "canonical_selector", "canonical_sha256"):
                if not concept.get(key):
                    fail(f"{concept_id}: reuse missing {key}")
            source = PROJECTS / concept["canonical_source_ref"]
            if not source.is_file() or digest(source) != concept["canonical_sha256"]:
                fail(f"{concept_id}: canonical source is missing or drifted")
        if disposition == "specialize" and concept.get("parent_definition_ref") not in known:
            fail(f"{concept_id}: unresolved specialization parent")

    for relationship in data.get("relationships", []):
        if relationship.get("from") not in known or relationship.get("to") not in known:
            fail(f"unresolved relationship endpoint: {relationship}")
        if not relationship.get("relation"):
            fail(f"relationship lacks relation: {relationship}")

    axioms = set(data.get("non_collapse_axioms", []))
    if axioms != REQUIRED_AXIOMS:
        fail(f"non-collapse axiom mismatch: missing={sorted(REQUIRED_AXIOMS - axioms)}, extra={sorted(axioms - REQUIRED_AXIOMS)}")

    for source_ref in data.get("source_refs", []):
        source = PROJECTS / source_ref["path"]
        if not source.is_file():
            fail(f"missing source: {source}")
        if digest(source) != source_ref["sha256"]:
            fail(f"source digest drift: {source_ref['path']}")

    if data.get("open_questions_and_conflicts") != []:
        fail("candidate must expose a settled baseline without open questions")
    for effect in ("authority_effect", "implementation_effect", "promotion_effect"):
        if data.get(effect) != "none":
            fail(f"{effect} must be none")
    if data.get("define_session", {}).get("authority_effect") != "none":
        fail("Define session authority_effect must be none")

    print(f"PASS: {data['pack_id']} ({len(concepts)} concepts, {len(data['relationships'])} relationships, {len(axioms)} non-collapse axioms)")


if __name__ == "__main__":
    main()
