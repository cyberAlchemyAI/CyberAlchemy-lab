#!/usr/bin/env python3
"""Read-only validation of a proposition record against the candidate contracts."""
import argparse
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from common import ROOT, LAB, KINDS, load, sha, need


def check_instance(data, root=ROOT):
    kind = next((kind for kind in KINDS if data.get("artifact_type_ref") == f"cal.artifact-type.{kind}/v1"), None)
    need(kind is not None, "Unknown proposition Artifact Type")
    package = root / "artifact-types" / kind / "v1"
    artifact = load(package / "artifact.json")
    need(sha(package / "schema.json") == artifact["schema_digest"], "Schema digest drift")
    for ref in artifact["semantic_definition_bindings"]:
        need(sha(LAB / ref["path"]) == ref["sha256"], "Semantic Definition digest drift")
    schema = load(package / "schema.json")
    Draft202012Validator.check_schema(schema)
    errors = sorted(error.message for error in Draft202012Validator(schema).iter_errors(data))
    return {"result": "BLOCK" if errors else "PASS", "kind": kind, "errors": errors,
            "assessment_scope": "declared representation and proposition posture", "authority_effect": "none",
            "truth_assessed": False, "reference_targets_resolved": False,
            "explanation": {"axiom": "A starting proposition taken as given within an explicit scope.",
                            "premise": "A defeasible assumption provisionally used to proceed.",
                            "hypothesis": "A testable proposition that is not adopted as a working basis."}[kind]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        data = load(args.record)
        need(isinstance(data, dict), "Proposition must be a JSON object")
        result = check_instance(data)
    except (OSError, ValueError) as exc:
        result = {"result": "BLOCK", "errors": [str(exc)], "authority_effect": "none"}
    print(json.dumps(result, indent=2))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
