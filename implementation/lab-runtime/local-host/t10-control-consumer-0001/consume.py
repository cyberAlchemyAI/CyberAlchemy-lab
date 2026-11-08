#!/usr/bin/env python3
"""Consume T10 member 14 as an exact, read-only workflow validation contract."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[4]
CONTROL = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/protocol-review-alternatives-preparation-0001/bound-controls/14-workflow-run-schemas.json"
CONTROL_SHA256 = "4f95040ffb32055b6cbe24c5509ae4d8b00ab42d1b11ca0ffd4e8e0a9bf20b2c"
MANIFEST_SCHEMA = "docs/proposals/0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json"
MANIFEST_SCHEMA_SHA256 = "52f4efabb39e3a9ac26da208ffe0950f85a8f51d3d591097eb5c19a544e46e60"
RUN = "implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001/research/workflow-run.json"
T31_RESULT = "implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001/RESULT.json"
T31_RESULT_SHA256 = "c9f85acd1b9316489d26eb1bbbb3e43d617f2903b7e627b74b86983c2c9e1445"
EXPECTED_BINDINGS = (
    ("implementation/lab-workflows/candidates/v1/review/W08/packages/0001/postimages/schemas/common.schema.json", "d41f2b8811d0cbea6845f13f1c586665afe03d49ddf7c0974d0632bb3ceded74"),
    ("implementation/lab-workflows/candidates/v1/review/W08/packages/0001/postimages/schemas/workflow-run.schema.json", "257df967d6c5dd1ac4f7f38ddd6833e803e48bfe9289fce51ee5ebc63d262a6f"),
)


def read_pinned(binding):
    path = binding["path"]
    target = ROOT / path
    raw = target.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
        raise ValueError(f"changed bound bytes: {path}")
    if "size_bytes" in binding and len(raw) != binding["size_bytes"]:
        raise ValueError(f"changed bound size: {path}")
    return json.loads(raw)


def pointer(document, selector):
    value = document
    for token in selector.split("/")[1:]:
        value = value[token.replace("~1", "/").replace("~0", "~")]
    return value


def selected_validator(control):
    if (control["member_ref"] != "protocol:W08:workflow-run-schemas"
            or control["control_kind"] != "validation-contract"
            or control["option_id"] != "T10:control-option:14"
            or control["native_or_runtime_use_allowed"] is not False
            or control["selected_choice"] is not None
            or control["authority_effect"] != "none"):
        raise ValueError("wrong selected control")
    read_pinned(control["original_wrapper_binding"])
    read_pinned(control["original_disposition_binding"])
    if tuple((binding["path"], binding["sha256"]) for binding in control["control_bindings"]) != EXPECTED_BINDINGS:
        raise ValueError("workflow contract requires the exact two ordered schemas")
    common, schema = (read_pinned(binding) for binding in control["control_bindings"])
    for fact in control["source_facts"]:
        if pointer(read_pinned(fact["binding"]), fact["selector"]) != fact["exact_value"]:
            raise ValueError(f"changed selected clause: {fact['selector']}")
    manifest = read_pinned({"path": MANIFEST_SCHEMA, "sha256": MANIFEST_SCHEMA_SHA256})
    if manifest["$id"] != "urn:cyberalchemy-lab:candidate-storage:artifact-package-manifest:v1":
        raise ValueError("wrong storage contract")
    for item in (common, schema, manifest):
        Draft202012Validator.check_schema(item)
    registry = Registry().with_resources((item["$id"], Resource.from_contents(item)) for item in (common, manifest))
    return Draft202012Validator(schema, registry=registry)


def validate_run(validator, run):
    errors = list(validator.iter_errors(run))
    if errors:
        error = min(errors, key=lambda e: (len(e.absolute_path), list(map(str, e.absolute_path))))
        raise ValueError(f"workflow run invalid at {'/'.join(map(str, error.absolute_path))}: {error.message}")


def verify_lineage(result, run_digest):
    selected_transitions = [row for row in result["new_output_transitions"]
                            if row["transition_ref"] == "transition:research:executed"]
    if len(selected_transitions) != 1 or selected_transitions[0]["workflow_run_sha256"] != run_digest:
        raise ValueError("T31 output lineage mismatch")


def consume():
    control_raw = (ROOT / CONTROL).read_bytes()
    if hashlib.sha256(control_raw).hexdigest() != CONTROL_SHA256:
        raise ValueError("changed control bytes")
    control = json.loads(control_raw)
    validator = selected_validator(control)
    run_raw = (ROOT / RUN).read_bytes()
    run_digest = hashlib.sha256(run_raw).hexdigest()
    result = read_pinned({"path": T31_RESULT, "sha256": T31_RESULT_SHA256})
    verify_lineage(result, run_digest)
    validate_run(validator, json.loads(run_raw))
    return {
        "schema_version": "lab-t10-control-consumer/v1",
        "member_ref": control["member_ref"],
        "control_path": CONTROL,
        "control_sha256": CONTROL_SHA256,
        "source_run_path": RUN,
        "source_run_sha256": run_digest,
        "source_result_sha256": T31_RESULT_SHA256,
        "result": "PASS",
        "effect": "read-only validation of one current candidate run",
    }


if __name__ == "__main__":
    print(json.dumps(consume(), indent=2, sort_keys=True))
