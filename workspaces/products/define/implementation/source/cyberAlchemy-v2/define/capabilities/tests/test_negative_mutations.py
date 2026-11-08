#!/usr/bin/env python3
"""Hostile mutations that the Define Product Capability validator must reject."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = PACKAGE_ROOT / "scripts/validate.py"
SPEC = importlib.util.spec_from_file_location("define_capability_validator", VALIDATOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def load(relative: str) -> dict:
    return json.loads((PACKAGE_ROOT / relative).read_text(encoding="utf-8"))


CASES = []


def case(name: str, relative: str, mutate) -> None:
    value = load(relative)
    mutate(value)
    CASES.append((name, {relative: value}))


case("unknown-product-field", "define-shared-meaning.product-capability.json", lambda d: d.__setitem__("invented", True))
case("business-meaning-drift", "define-shared-meaning.product-capability.json", lambda d: d.__setitem__("business_ontology_ref", "B-OTHER"))
case("owner-route-collapse", "define-shared-meaning.product-capability.json", lambda d: d.__setitem__("owner_routes", d["owner_routes"][:1]))
case("missing-obligation-registry", "define-shared-meaning.product-capability.json", lambda d: d.pop("obligation_registry_ref"))
case("input-direction-flip", "contracts/define-shared-meaning.input-contract.json", lambda d: d.__setitem__("direction", "output"))
case("goal-no-longer-hard-gate", "contracts/define-shared-meaning.input-contract.json", lambda d: d["items"][0].__setitem__("required", False))
case("context-order-drift", "policies/define-shared-meaning.context-policy.json", lambda d: d["resolution_order"].reverse())
case("insufficient-can-continue", "policies/define-shared-meaning.context-policy.json", lambda d: d.__setitem__("continuation_state", "insufficient"))
case("invented-agent-identity", "realizations/define-cli.realization.json", lambda d: d.__setitem__("agent_capability_ref", "CAP-REF-AGENT-INVENTED"))
case("partial-mislabeled-complete", "realizations/define-cli.realization.json", lambda d: d.__setitem__("coverage", "complete"))
case("behavioral-conformance-inflation", "realizations/define-cli.realization.json", lambda d: d["conformance_posture"].__setitem__("state", "verified"))
case("duplicate-obligation-id", "obligations/define-shared-meaning.obligations.json", lambda d: d["obligations"][1].__setitem__("obligation_id", d["obligations"][0]["obligation_id"]))
case("obligation-conformance-inflation", "obligations/define-shared-meaning.obligations.json", lambda d: d["obligations"][10].__setitem__("current_status", "satisfied"))
case("authority-effect-inflation", "define-shared-meaning.product-capability.json", lambda d: d.__setitem__("authority_effect", "adopt"))


failures = []
for name, overrides in CASES:
    receipt = MODULE.validate_package(overrides=copy.deepcopy(overrides))
    if receipt["status"] != "BLOCK":
        failures.append(name)
    else:
        print(f"PASS {name}")

if failures:
    print("FAILED hostile cases: " + ", ".join(failures))
    raise SystemExit(1)

print(f"PASS {len(CASES)}/{len(CASES)} hostile mutations rejected")
