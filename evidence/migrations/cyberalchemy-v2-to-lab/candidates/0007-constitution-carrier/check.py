#!/usr/bin/env python3
"""Read-only preview of a candidate constitution's exact selectors."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PREVIOUS, PACKAGE, load, sha, need


def unique(records, key):
    result = {x[key]: x for x in records}
    need(len(result) == len(records), "Duplicate " + key)
    return result


def validate_record(record):
    artifact = load(PACKAGE / "artifact.json")
    need(sha(PACKAGE / "schema.json") == artifact["schema_digest"], "Constitution schema drift")
    for ref in artifact["semantic_definition_bindings"]:
        need(sha(LAB / ref["path"]) == ref["sha256"], "Constitution Definition drift")
    errors = sorted(x.message for x in Draft202012Validator(load(PACKAGE / "schema.json")).iter_errors(record))
    need(not errors, "; ".join(errors))
    selectors = unique(record["selectors"], "selector_id")
    rules = unique(record["rules"], "rule_id")
    bindings = unique(record["validation_bindings"], "binding_id")
    unique(record["policies"], "policy_id")
    need(set(record["precedence"]) == set(rules) and len(record["precedence"]) == len(rules), "Precedence must name every rule exactly once")
    used_bindings = set()
    used_selectors = set()
    for rule in rules.values():
        need(set(rule["selector_ids"]) <= set(selectors), "Unknown rule selector")
        used_selectors.update(rule["selector_ids"])
        selected = rule["validation_binding_id"]
        if rule["validation_mode"] in {"deterministic", "hybrid"}:
            need(selected in bindings, "Deterministic or hybrid rule requires an exact validation binding")
        else:
            need(selected is None, "Review or none-yet mode cannot claim an executable binding in this profile")
        if selected is not None:
            used_bindings.add(selected)
    need(used_bindings == set(bindings), "Unused validation binding")
    need(used_selectors == set(selectors), "Unused selector")
    for policy in record["policies"]:
        need(set(policy["rule_ids"]) <= set(rules), "Unknown policy rule")
    for ref in bindings.values():
        relative = Path(ref["path"])
        need(not relative.is_absolute() and ".." not in relative.parts, "Binding must be a local relative path")
        path = LAB / relative
        need(path.resolve().is_relative_to(LAB.resolve()), "Binding escapes Lab")
        need(not any(p.is_symlink() for p in [path, *path.parents]), "Binding symlinks are not supported")
        need(path.is_file() and sha(path) == ref["sha256"], "Validation binding missing or changed")
        bound = load(path)
        need(bound.get("artifact_type_ref") == "cal.artifact-type.invariant/v1"
             and bound.get("invariant_id") == ref["invariant_id"]
             and bound.get("evaluation_profile") == ref["evaluation_profile"], "Binding target identity or profile mismatch")
        need(bound.get("scope_ref") == record["scope_ref"], "Binding scope differs from constitution scope")
        result = subprocess.run([sys.executable, str(PREVIOUS / "check.py"), str(path)], capture_output=True, text=True)
        need(result.returncode == 0, "Bound invariant record is invalid: " + result.stdout + result.stderr)
    return selectors, rules


def preview(record, subject):
    selectors, rules = validate_record(record)
    need(isinstance(subject, dict) and set(subject) == {"scope_ref", "subject_kind", "attributes"}, "Subject requires scope_ref, subject_kind and attributes")
    need(isinstance(subject["scope_ref"], str) and isinstance(subject["subject_kind"], str)
         and isinstance(subject["attributes"], dict), "Invalid subject shape")
    in_scope = subject["scope_ref"] == record["scope_ref"] and subject["subject_kind"] in record["subject_kinds"]
    selector_results = {}
    for ident, selector in selectors.items():
        value = subject["attributes"].get(selector["attribute"])
        state = "indeterminate" if not isinstance(value, str) else "matches" if value == selector["equals"] else "does-not-match"
        selector_results[ident] = state
    result = []
    for ident in record["precedence"]:
        rule = rules[ident]
        states = [selector_results[key] for key in rule["selector_ids"]]
        match = "does-not-match" if not in_scope or "does-not-match" in states else "indeterminate" if "indeterminate" in states else "matches"
        result.append({"rule_id": ident, "selector_state": match, "validation_mode": rule["validation_mode"],
            "validation_binding_id": rule["validation_binding_id"], "validation_executed": False, "governs": False})
    return {"schema_version": "cal-constitution-selector-preview/v1", "constitution_id": record["constitution_id"],
        "version": record["version"], "scope_matches": in_scope, "rules": result,
        "matching_rules": [x["rule_id"] for x in result if x["selector_state"] == "matches"],
        "indeterminate_rules": [x["rule_id"] for x in result if x["selector_state"] == "indeterminate"],
        "governs": False, "adoption_verified": False, "authority_effect": "none", "enforcement_performed": False,
        "reason": "Candidate selector preview only. Governing requires separate exact-version owner adoption and applicable scope; matching alone grants nothing.",
        "composition": record["composition"], "conflict_route": record["conflict_route"]}


def read_input(path):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique_keys)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("constitution", type=Path)
    parser.add_argument("subject", nargs="?", type=Path)
    args = parser.parse_args()
    try:
        record = read_input(args.constitution)
        if args.subject:
            result = preview(record, read_input(args.subject))
        else:
            validate_record(record)
            result = {"record_valid": True, "governs": False, "authority_effect": "none"}
        code = 0
    except (OSError, ValueError) as exc:
        result = {"record_valid": False, "error": str(exc), "governs": False, "authority_effect": "none"}
        code = 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
