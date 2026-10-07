#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / "_candidate_pack.py"


def hostile(subject):
    failures = set()
    if subject.get("source_kind") == "*" or subject.get("target_kind") == "*":
        failures.add("connection-extension-must-not-use-wildcard")
    if subject.get("infers_cartesian_product") is True:
        failures.add("connection-extension-must-declare-exact-pair")
    if subject.get("endpoint_registration_implies_connection") is True:
        failures.add("endpoint-registration-must-not-create-connection")
    if subject.get("effective") is True and subject.get("admitted_contract_version") is not True:
        failures.add("unadmitted-extension-must-not-be-effective")
    if subject.get("effective") is True and subject.get("endpoint_contracts_resolved") is not True:
        failures.add("connection-extension-must-resolve-endpoint-contracts")
    if subject.get("effective") is True and subject.get("qualifier_schema_bound") is not True:
        failures.add("connection-extension-must-bind-qualifier-schema")
    if subject.get("effective") is True and subject.get("connection_scope") not in {"global", "ontology-local"}:
        failures.add("connection-extension-must-declare-scope")
    if subject.get("effective") is True and subject.get("canonical_relation_authority") not in {"typed-relation", "specialized-carrier"}:
        failures.add("connection-extension-must-declare-canonical-authority")
    if subject.get("effective") is True and subject.get("contestability_contract_bound") is not True:
        failures.add("connection-extension-must-bind-contestability")
    if subject.get("effective") is True and subject.get("predecessor_effective_state_resolved") is not True:
        failures.add("connection-extension-must-resolve-effective-predecessor")
    return failures


if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("candidate_pack", SHARED)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.hostile_failures = hostile
    raise SystemExit(module.validate(ROOT, {"cal.definition.typed-connection-extension-rule"}))
