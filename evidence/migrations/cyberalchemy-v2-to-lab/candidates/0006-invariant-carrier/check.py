#!/usr/bin/env python3
"""Check a bounded integer invariant against one explicitly scoped observation."""
import argparse
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from support import LAB, PACKAGE, load, sha, need


def validate_record(record):
    artifact = load(PACKAGE / "artifact.json")
    need(sha(PACKAGE / "schema.json") == artifact["schema_digest"], "Invariant schema drift")
    for ref in artifact["semantic_definition_bindings"]:
        need(sha(LAB / ref["path"]) == ref["sha256"], "Invariant Definition drift")
    validator = Draft202012Validator(load(PACKAGE / "schema.json"))
    errors = sorted(x.message for x in validator.iter_errors(record))
    need(not errors, "; ".join(errors))
    identifiers = [x["check_id"] for x in record["checks"]]
    need(len(identifiers) == len(set(identifiers)), "Duplicate check identity")
    need(all(type(x["expected"]) is int for x in record["checks"]), "Expected values must be JSON integers without coercion")


def evaluate(record, observation):
    validate_record(record)
    need(isinstance(observation, dict) and set(observation) == {"scope_ref", "subject_ref", "values"}, "Observation requires exactly scope_ref, subject_ref and values")
    need(isinstance(observation["values"], dict), "Observation values must be an object")
    matches = observation["scope_ref"] == record["scope_ref"] and observation["subject_ref"] == record["subject_ref"]
    outcomes = []
    for predicate in record["checks"]:
        item = {"check_id": predicate["check_id"], "field": predicate["field"], "operator": predicate["operator"], "expected": predicate["expected"]}
        value = observation["values"].get(predicate["field"])
        if not matches:
            item.update(state="not-evaluable", reason="observation-scope-or-subject-mismatch")
        elif predicate["field"] not in observation["values"]:
            item.update(state="not-evaluable", reason="missing-observation")
        elif type(value) is not int:
            item.update(state="not-evaluable", reason="observation-is-not-an-integer")
        else:
            operator = predicate["operator"]
            expected = predicate["expected"]
            passed = {"equals": value == expected, "at-least": value >= expected, "at-most": value <= expected}[operator]
            item.update(state="satisfied" if passed else "violated", observed=value)
        outcomes.append(item)
    states = {x["state"] for x in outcomes}
    state = "violated" if "violated" in states else "not-evaluable" if "not-evaluable" in states else "satisfied"
    return {"schema_version": "cal-invariant-observation-check/v1", "invariant_id": record["invariant_id"],
        "state": state, "observation_complete": "not-evaluable" not in states, "checks": outcomes,
        "authority_effect": "none", "enforcement_performed": False,
        "claim_ceiling": "Integer comparisons over this supplied observation only. No observation authenticity, freshness, continuous invariant proof, domain-wide conformance or effect authority is established."}


def read_input(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError("Non-JSON numeric constant: " + value)
    return json.loads(path.read_text(), object_pairs_hook=unique, parse_constant=invalid_constant)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("invariant", type=Path)
    parser.add_argument("observation", nargs="?", type=Path)
    args = parser.parse_args()
    try:
        record = read_input(args.invariant)
        if args.observation:
            result = evaluate(record, read_input(args.observation))
            code = {"satisfied": 0, "violated": 1, "not-evaluable": 2}[result["state"]]
        else:
            validate_record(record)
            result = {"record_valid": True, "state": "not-evaluated", "authority_effect": "none"}
            code = 0
    except (OSError, ValueError) as exc:
        result = {"record_valid": False, "state": "invalid-input", "error": str(exc), "authority_effect": "none"}
        code = 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
