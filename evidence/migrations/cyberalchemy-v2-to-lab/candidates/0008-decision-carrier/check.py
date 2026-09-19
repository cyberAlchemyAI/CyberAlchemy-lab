#!/usr/bin/env python3
"""Inspect exact decision bindings; never authenticate or execute the recorded choice."""
import argparse
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from support import ROOT, LAB, PACKAGE, load, sha, need


def read_input(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("Invalid JSON constant: " + value)
    return json.loads(path.read_text(), object_pairs_hook=unique, parse_constant=invalid)


def resolve(ref):
    relative = Path(ref["path"])
    need(not relative.is_absolute() and ".." not in relative.parts, "Binding must be Lab-relative")
    path = LAB / relative
    need(path.resolve().is_relative_to(LAB.resolve()), "Binding escapes Lab")
    need(not any(p.is_symlink() for p in [path, *path.parents]), "Symlink binding rejected")
    need(path.is_file() and sha(path) == ref["sha256"], "Binding missing or changed: " + ref["path"])
    return path


def shape(data, schema_name):
    schema = load(PACKAGE / schema_name)
    errors = sorted(x.message for x in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data))
    need(not errors, "; ".join(errors))


def inspect(record):
    artifact = load(PACKAGE / "artifact.json")
    need(sha(PACKAGE / "schema.json") == artifact["schema_digest"], "Decision schema drift")
    for ref in artifact["semantic_definition_bindings"]:
        resolve(ref)
    contracts = load(ROOT / "contracts.json")
    for ref in contracts["schemas"]:
        resolve(ref)
    shape(record, "schema.json")
    proposal = read_input(resolve(record["proposal"]))
    shape(proposal, "proposal.schema.json")
    need(record["proposal_id"] == proposal["proposal_id"], "Proposal identity mismatch")
    need(record["scope_ref"] == proposal["scope_ref"], "Decision scope differs from proposal")
    need(record["subject"] == proposal["subject"], "Decision subject differs from proposal")
    resolve(record["subject"])
    manifest = read_input(resolve(record["subject"]["material_manifest"]))
    need(isinstance(manifest, dict) and isinstance(manifest.get("materials"), list) and manifest["materials"], "Subject material manifest is incomplete")
    names = set()
    for ref in manifest["materials"]:
        need(isinstance(ref, dict) and set(ref) == {"path", "sha256"} and isinstance(ref["path"], str)
             and isinstance(ref["sha256"], str), "Invalid subject material binding")
        need(ref["path"] not in names, "Duplicate subject material")
        names.add(ref["path"])
        resolve(ref)
    need({"path": record["subject"]["path"], "sha256": record["subject"]["sha256"]} in manifest["materials"], "Subject is absent from its material manifest")
    options = {x["option_id"]: x for x in proposal["options"]}
    need(len(options) == len(proposal["options"]), "Duplicate proposal option")
    need(record["selected_option_id"] in options, "Unknown selected option")
    chosen = options[record["selected_option_id"]]
    need(record["declared_effect"] == chosen["declared_effect"], "Decision effect differs from selected option")
    need(record["actor"]["role_ref"] == proposal["owner_role_ref"], "Decision role differs from proposal owner route")
    statement = read_input(resolve(record["statement"]))
    shape(statement, "statement.schema.json")
    for key in ["proposal_id", "selected_option_id", "scope_ref", "subject", "actor", "recorded_at", "provenance_kind"]:
        need(record[key] == statement[key], "Statement mismatch: " + key)
    need(statement["proposal_sha256"] == record["proposal"]["sha256"], "Statement refers to another proposal version")
    return {"schema_version": "cal-decision-integrity-inspection/v1", "record_valid": True,
        "decision_id": record["decision_id"], "proposal_id": proposal["proposal_id"],
        "subject": record["subject"], "scope_ref": record["scope_ref"],
        "selected_option_id": chosen["option_id"], "selected_option_description": chosen["description"],
        "declared_effect": chosen["declared_effect"], "provenance_kind": record["provenance_kind"],
        "binding_integrity": "verified", "principal_authenticated": False, "role_authority_verified": False,
        "subject_materials_verified": len(names),
        "effect_authorized_by_checker": False, "effect_executed": False, "authority_effect": "none",
        "claim_ceiling": "The record, proposal, statement and subject agree on exact bytes, choice, role and scope. Identity and role are assertions, not authenticated authority; no effect follows from this check."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision", type=Path)
    args = parser.parse_args()
    try:
        result = inspect(read_input(args.decision)); code = 0
    except (ValueError, OSError) as exc:
        result = {"record_valid": False, "error": str(exc), "authority_effect": "none", "effect_authorized_by_checker": False}; code = 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
