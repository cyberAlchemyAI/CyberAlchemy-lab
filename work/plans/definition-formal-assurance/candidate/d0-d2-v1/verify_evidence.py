#!/usr/bin/env python3
"""Check exact evidence set, bindings, case outcomes and independent witnesses."""
import json
import platform
import sys
from pathlib import Path

import jsonschema
import checker
import replay

HERE = Path(__file__).resolve().parent


def verify(evidence):
    jsonschema.Draft202012Validator(checker.load(HERE / "evidence.schema.json")).validate(evidence)
    expected = checker.bundle()
    if evidence != expected:
        raise ValueError("Evidence is stale, incomplete, altered, or not reproducible under the current provider")
    submitted_cases = [c["case"] for c in evidence["cases"]]
    if len(set(submitted_cases)) != 9:
        raise ValueError("Missing or duplicate case")
    checks = 0
    for case in evidence["cases"]:
        if checker.canonical_digest(case["input"]) != case["input_sha256"]:
            raise ValueError("Case input digest mismatch")
        for obligation in case["result"]["obligations"]:
            if obligation["witness"]:
                if not replay.verify(obligation["witness"], case["input"], obligation["obligation_id"]):
                    raise ValueError("Witness fails independent replay")
                checks += 1
    return checks


if __name__ == "__main__":
    evidence = checker.load(HERE / "evidence.json")
    count = verify(evidence)
    receipt = {"schema_version": "definition-assurance-replay-receipt/v1-candidate", "authority_effect": "none",
               "result": "PASS", "evidence_sha256": checker.sha(HERE / "evidence.json"),
               "verifier_sha256": checker.sha(__file__), "replay_sha256": checker.sha(HERE / "replay.py"),
               "schema_sha256": checker.sha(HERE / "evidence.schema.json"), "python_version": platform.python_version(),
               "python_executable_sha256": checker.sha(sys.executable), "cases_checked": 9,
               "witnesses_replayed": count, "fidelity_review": "pending", "claim_ceiling": "Current finite candidate bundle reproduced and witnesses replayed; no kernel proof or admission."}
    (HERE / "replay-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2))
