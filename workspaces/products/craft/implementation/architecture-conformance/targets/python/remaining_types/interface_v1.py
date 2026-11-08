"""Candidate-local native Python witness for the WP-RMT-002 Interface slice."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Protocol


class SettlementPortV1(Protocol):
    def complete_settlement(self, request: dict[str, object]) -> dict[str, object]: ...
    def find_settlement(self, request_id: str) -> dict[str, object] | None: ...


@dataclass(frozen=True)
class VersionedBoundary:
    contract_id: str
    version: str
    inside: str
    outside: str
    domain_contract_id: str
    transport_adapter_id: str


def _major(version: str) -> int | None:
    try:
        parts = version.split(".")
        if not 1 <= len(parts) <= 3 or any(not part.isdigit() for part in parts):
            return None
        return int(parts[0])
    except (TypeError, ValueError):
        return None


def evaluate_interface(descriptor: dict[str, object], observed: dict[str, object]) -> tuple[str, tuple[str, ...]]:
    findings: list[str] = []
    declared = {item["binding_id"]: item for item in descriptor["exposed_bindings"]}  # type: ignore[index]
    actual = {item["binding_id"]: item for item in observed["exposed_bindings"]}  # type: ignore[index]
    extras = set(actual) - set(declared)
    if extras:
        findings.append("RMT_IFACE_UNDECLARED_EXPOSURE")
    if not extras and [
        {key: value for key, value in item.items() if key != "internal_type_ids"}
        for item in observed["exposed_bindings"]  # type: ignore[index]
    ] != descriptor["exposed_bindings"]:
        findings.append("RMT_IFACE_EXPOSURE_DRIFT")
    if any(item.get("internal_type_ids") for item in observed["exposed_bindings"]):  # type: ignore[index]
        findings.append("RMT_IFACE_INTERNAL_TYPE_LEAK")

    checks = observed["compatibility_checks"]  # type: ignore[index]
    expected_major = _major(str(descriptor["exact_version"]))
    if observed["version"] != descriptor["exact_version"] or any(
        _major(str(check["provider_version"])) is None
        or expected_major is None
        or _major(str(check["provider_version"])) < expected_major
        for check in checks
    ):
        findings.append("RMT_IFACE_VERSION_REGRESSION")
    if observed["compatibility_direction"] != descriptor["compatibility_direction"]:
        findings.append("RMT_IFACE_COMPATIBILITY_DIRECTION_FLIP")
    if any(check["accepted"] and _major(str(check["consumer_version"])) != _major(str(check["provider_version"])) for check in checks):
        findings.append("RMT_IFACE_COMPATIBILITY_OVERCLAIM")
    if (observed["inside_boundary"], observed["outside_boundary"]) != (descriptor["inside_boundary"], descriptor["outside_boundary"]) \
            or observed["inside_boundary"] == observed["outside_boundary"]:
        findings.append("RMT_IFACE_BOUNDARY_CROSSING")
    if any(item not in observed["mapping_obligations"] for item in descriptor["mapping_obligations"]):  # type: ignore[operator]
        findings.append("RMT_IFACE_MAPPING_OBLIGATION_MISSING")
    if observed["domain_contract_id"] == observed["transport_adapter_id"] \
            or observed["domain_contract_id"] != descriptor["domain_contract_id"] \
            or observed["transport_adapter_id"] != descriptor["transport_adapter_id"]:
        findings.append("RMT_IFACE_TRANSPORT_DOMAIN_COLLAPSE")
    if any(route["side"] != "outside" for route in observed["consumer_routes"]):  # type: ignore[index]
        findings.append("RMT_IFACE_CONSUMER_ROUTE_OUTSIDE")
    return ("pass" if not findings else "reject"), tuple(findings)


def evaluate_case(case: dict[str, object]) -> dict[str, object]:
    descriptor = case["descriptor"]  # type: ignore[assignment]
    observation = case["observation"]  # type: ignore[assignment]
    verdict, findings = evaluate_interface(descriptor, observation)  # type: ignore[arg-type]
    w3_descriptor = case["w3_descriptor"]  # type: ignore[assignment]
    w3_observation = case["w3_observation"]  # type: ignore[assignment]
    if w3_descriptor["contract_id"] != w3_observation["contract_id"] \
            or w3_descriptor["exact_version"] != w3_observation["version"] \
            or w3_descriptor["exposed_bindings"] != w3_observation["exposed_bindings"]:
        findings = (*findings, "ARCH_INTERFACE_CONTRACT_DRIFT")
        verdict = "reject"
    if verdict != "pass":
        raise ValueError(f"RMT_IFACE_PYTHON_REJECTED:{','.join(findings)}")
    portable = {
        "schema_version": "domainspec.interface-portable-result/v1",
        "result": "pass",
        "meta_type": "Interface",
        "contract_id": descriptor["contract_id"],
        "version": descriptor["exact_version"],
        "compatibility_direction": descriptor["compatibility_direction"],
        "exposed_bindings": sorted(f'{item["kind"]}:{item["binding_id"]}' for item in descriptor["exposed_bindings"]),
        "mapping_obligations": sorted(f'{item["binding_id"]}:{item["direction"]}:{item["mapping_id"]}' for item in descriptor["mapping_obligations"]),
        "boundary": {"inside": descriptor["inside_boundary"], "outside": descriptor["outside_boundary"]},
        "transport_domain_separated": True,
        "authority_effect": "none",
    }
    return {"portable": portable, "native_evidence": {"language": "python", "mechanism": "protocol-and-frozen-dataclass-boundary"}}


if __name__ == "__main__" and sys.argv[1:] == ["--evaluate"]:
    try:
        print(json.dumps(evaluate_case(json.load(sys.stdin)), sort_keys=True, separators=(",", ":")))
    except Exception as error:  # preserve native non-zero failure
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error
