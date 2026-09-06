from __future__ import annotations

import argparse
import ast
import base64
from dataclasses import FrozenInstanceError, asdict
import dis
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


class PythonEntityObserverError(Exception):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def inspect_source(source: str) -> dict[str, Any]:
    try:
        module = ast.parse(source, filename="entity_v1.py")
    except SyntaxError as error:
        raise PythonEntityObserverError("PY_ENTITY_SOURCE_INVALID") from error
    forbidden_nodes = (
        ast.AsyncFunctionDef,
        ast.Await,
        ast.Yield,
        ast.YieldFrom,
        ast.Global,
        ast.Nonlocal,
        ast.With,
        ast.AsyncWith,
    )
    if any(isinstance(node, forbidden_nodes) for node in ast.walk(module)):
        raise PythonEntityObserverError("PY_ENTITY_SOURCE_SURFACE_UNSUPPORTED")
    allowed_imports = {"__future__", "dataclasses", "hashlib", "typing"}
    for node in module.body:
        if isinstance(node, ast.Import):
            if any(alias.name not in allowed_imports for alias in node.names):
                raise PythonEntityObserverError("PY_ENTITY_IMPORT_UNSUPPORTED")
        if isinstance(node, ast.ImportFrom) and node.module not in allowed_imports:
            raise PythonEntityObserverError("PY_ENTITY_IMPORT_UNSUPPORTED")
    forbidden_names = {
        "open", "eval", "compile", "__import__", "globals", "locals",
        "getattr", "setattr", "delattr", "input", "breakpoint",
    }
    for node in ast.walk(module):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in forbidden_names:
                raise PythonEntityObserverError("PY_ENTITY_CALL_UNSUPPORTED")
    required = (
        "@dataclass(frozen=True, slots=True, eq=False, init=False)\n"
        "    class SettlementEntitySnapshot:",
        "if observed is not construction_token:",
        "return self.identity == other.identity",
        "return _stable_hash(self.identity.canonical_tuple)",
        "return BASE_VALIDATORS\n",
        "return (*BASE_VALIDATORS, DUPLICATE_BLOCKED_VALIDATOR)",
        "return IDENTITY_RESOLVER_REF",
        "if self.mode != \"base\":\n            return None",
        "for ordinal, validator in enumerate(self.validators, start=1):",
        'if route_id not in (\n            "factory",\n'
        '            "deserialization-reconstruction",\n'
        '            "lifecycle-transition",\n        ):',
        "False,\n                    None,\n                    (failure_code,)",
        "return self._execute(\"deserialization-reconstruction\", input_data)",
        "predecessor.identity.settlement_id.normalized_value_sha256",
        "def direct_constructor(self) -> None:\n        return None",
        '"canonical-identity-only",\n    "canonical-identity-only"',
        '"additive-only",\n    "acyclic"',
    )
    if any(token not in source for token in required):
        raise PythonEntityObserverError("PY_ENTITY_REQUIRED_SEMANTIC")
    if "per_call_validator" in source:
        raise PythonEntityObserverError("PY_ENTITY_PER_CALL_VALIDATOR_SURFACE")
    namespace: dict[str, Any] = {}
    exec(compile(module, "entity_v1.py", "exec"), namespace)
    factory_type = namespace.get("SettlementEntityFactory")
    snapshot_type = namespace.get("SettlementEntitySnapshot")
    if not isinstance(factory_type, type) or not isinstance(snapshot_type, type):
        raise PythonEntityObserverError("PY_ENTITY_SYMBOL_MISSING")
    methods = (
        factory_type._execute,
        factory_type.create,
        factory_type.reconstruct,
        factory_type.transition,
        factory_type.extend_with_duplicate_blocked,
        snapshot_type.__eq__,
        snapshot_type.__hash__,
    )
    instructions = [item for method in methods for item in dis.get_instructions(method)]
    forbidden_prefixes = (
        "IMPORT", "STORE_GLOBAL", "DELETE_GLOBAL", "STORE_ATTR", "DELETE_ATTR",
        "YIELD", "GET_AWAITABLE",
    )
    if any(
        instruction.opname.startswith(prefix)
        for instruction in instructions
        for prefix in forbidden_prefixes
    ):
        raise PythonEntityObserverError("PY_ENTITY_BYTECODE_EFFECT_INVALID")
    return {
        "schema_version": "PythonEntityClosedSubsetProof/v1",
        "source_sha256": sha256_bytes(source.encode("utf8")),
        "mechanism": "hash-locked-source-ast-bytecode-plus-runtime-observation",
        "bytecode_opnames": sorted({item.opname for item in instructions}),
        "authority_effect": "none",
    }


def decode_payload(encoded: str) -> dict[str, Any]:
    try:
        value = json.loads(base64.b64decode(encoded, validate=True).decode("utf8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PythonEntityObserverError("PY_ENTITY_PAYLOAD_INVALID") from error
    if type(value) is not dict or set(value) != {"snapshots", "validation_failure"}:
        raise PythonEntityObserverError("PY_ENTITY_PAYLOAD_INVALID")
    if type(value["snapshots"]) is not list or type(value["validation_failure"]) is not dict:
        raise PythonEntityObserverError("PY_ENTITY_PAYLOAD_INVALID")
    return value


def execute(source_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    source = source_path.read_text(encoding="utf8")
    source_proof = inspect_source(source)
    namespace: dict[str, Any] = {}
    exec(compile(source, str(source_path), "exec"), namespace)
    input_type = namespace["SettlementEntityInput"]
    snapshot_type = namespace["SettlementEntitySnapshot"]
    base_factory = namespace["create_settlement_entity_factory"]()
    factory = base_factory.extend_with_duplicate_blocked()
    if factory is None or factory.extend_with_duplicate_blocked() is not None:
        raise PythonEntityObserverError("PY_ENTITY_EXTENSION_GRAPH_INVALID")
    if factory.direct_constructor is not None:
        raise PythonEntityObserverError("PY_ENTITY_DIRECT_CONSTRUCTOR_EXPOSED")

    snapshots_by_id: dict[str, Any] = {}
    route_results: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    for owner in payload["snapshots"]:
        route_id = owner["route_id"]
        identity = owner["identity_values"]
        if route_id == "lifecycle-transition":
            predecessor = snapshots_by_id.get(owner["predecessor_snapshot_id"])
            if predecessor is None:
                raise PythonEntityObserverError("PY_ENTITY_PREDECESSOR_MISSING")
            result = factory.transition(
                predecessor,
                snapshot_id=owner["snapshot_id"],
                state_sha256=owner["state_sha256"],
                amount_minor=100,
            )
        else:
            source_input = input_type(
                owner["snapshot_id"],
                owner["entity_case_id"],
                owner["sequence"],
                owner["predecessor_snapshot_id"],
                identity["organization_id"],
                identity["settlement_id"],
                identity["organization_id"],
                100,
                False,
                owner["state_sha256"],
            )
            if route_id == "factory":
                result = factory.create(source_input)
            elif route_id == "deserialization-reconstruction":
                result = factory.reconstruct(source_input)
            else:
                raise PythonEntityObserverError("PY_ENTITY_ROUTE_UNSUPPORTED", route_id)
        if not result.ok:
            raise PythonEntityObserverError("PY_ENTITY_OWNER_CASE_FAILED", owner["snapshot_id"])
        snapshot = result.value
        before = snapshot.state_sha256
        try:
            setattr(snapshot, "state_sha256", "0" * 64)
        except FrozenInstanceError:
            pass
        mutation_observed = snapshot.state_sha256 != before
        row = {
            "snapshot_id": snapshot.snapshot_id,
            "entity_case_id": snapshot.entity_case_id,
            "sequence": snapshot.sequence,
            "route_id": snapshot.route_id,
            "predecessor_snapshot_id": snapshot.predecessor_snapshot_id,
            "identity": [
                asdict(snapshot.identity.organization_id),
                asdict(snapshot.identity.settlement_id),
            ],
            "state_sha256": snapshot.state_sha256,
            "frozen": not mutation_observed,
            "mutation_observed": mutation_observed,
            "hash": str(hash(snapshot)),
        }
        if any(row[key] != owner[key] for key in (
            "snapshot_id", "entity_case_id", "sequence", "route_id",
            "predecessor_snapshot_id", "state_sha256",
        )):
            raise PythonEntityObserverError("PY_ENTITY_SNAPSHOT_OWNER_MISMATCH")
        snapshots_by_id[snapshot.snapshot_id] = snapshot
        rows.append(row)
        route_results.setdefault(route_id, result)

    direct_inaccessible = False
    first = next(iter(snapshots_by_id.values()))
    try:
        snapshot_type(
            object(),
            "snapshot.direct-bypass",
            first.entity_case_id,
            0,
            "language-visible-direct-constructor",
            None,
            first.identity,
            first.state_sha256,
        )
    except TypeError as error:
        direct_inaccessible = str(error) == "SETTLEMENT_ENTITY_DIRECT_CONSTRUCTOR_INACCESSIBLE"
    if not direct_inaccessible:
        raise PythonEntityObserverError("PY_ENTITY_DIRECT_CONSTRUCTOR_EXPOSED")
    raw_constructor_helper_exposed = any(name in namespace for name in (
        "_construct_snapshot",
        "_define_snapshot_type",
        "_factory_construction_authority",
    ))
    if raw_constructor_helper_exposed:
        raise PythonEntityObserverError("PY_ENTITY_DIRECT_CONSTRUCTOR_EXPOSED")
    rejected_route_ids = []
    for route_id in ("language-visible-direct-constructor", "undeclared-route"):
        try:
            factory._execute(route_id, input_type(
                "snapshot.route-bypass",
                first.entity_case_id,
                0,
                None,
                first.identity.organization_id.normalized_value_sha256,
                first.identity.settlement_id.normalized_value_sha256,
                first.identity.organization_id.normalized_value_sha256,
                100,
                False,
                first.state_sha256,
            ))
        except ValueError as error:
            if str(error) == "SETTLEMENT_ENTITY_CONSTRUCTION_ROUTE_UNSUPPORTED":
                rejected_route_ids.append(route_id)
        if route_id not in rejected_route_ids:
            raise PythonEntityObserverError("PY_ENTITY_ROUTE_BYPASS", route_id)

    route_traces = []
    for route_id in ("factory", "deserialization-reconstruction", "lifecycle-transition"):
        result = route_results[route_id]
        route_traces.append({
            "route_id": route_id,
            "input_class": "valid",
            "normalization_ordinal": result.trace.normalization_ordinal,
            "validator_trace": [asdict(item) for item in result.trace.validator_trace],
            "identity_resolution_ordinal": result.trace.identity_resolution_ordinal,
            "construction_ordinal": result.trace.construction_ordinal,
            "immutability_ordinal": result.trace.immutability_ordinal,
            "direct_constructor_policy": "not-applicable",
            "result": {
                "status": "formed",
                "snapshot_created": True,
                "snapshot_id": result.value.snapshot_id,
            },
        })
    route_traces.append({
        "route_id": "language-visible-direct-constructor",
        "input_class": "valid",
        "normalization_ordinal": None,
        "validator_trace": [],
        "identity_resolution_ordinal": None,
        "construction_ordinal": None,
        "immutability_ordinal": None,
        "direct_constructor_policy": "private-inaccessible",
        "result": {
            "status": "constructor-inaccessible",
            "snapshot_created": False,
            "snapshot_id": None,
        },
    })

    failure_owner = payload["validation_failure"]
    baseline_owner = payload["snapshots"][0]
    baseline_identity = baseline_owner["identity_values"]
    failure = factory.create(input_type(
        "snapshot.invalid",
        "settlement-invalid",
        0,
        None,
        baseline_identity["organization_id"],
        baseline_identity["settlement_id"],
        baseline_identity["organization_id"],
        0,
        False,
        baseline_owner["state_sha256"],
    ))
    if failure.ok or failure.value is not None:
        raise PythonEntityObserverError("PY_ENTITY_INVALID_INPUT_FORMED_SNAPSHOT")
    validation_failure = {
        "probe_id": failure_owner["probe_id"],
        "route_id": "factory",
        "validator_trace": [asdict(item) for item in failure.validator_trace],
        "identity_resolution_ordinal": failure.identity_resolution_ordinal,
        "construction_ordinal": failure.construction_ordinal,
        "result": {
            "status": "validation-failure",
            "snapshot_created": failure.value is not None,
            "failure_codes": list(failure.failure_codes),
        },
    }

    equality_probes = []
    created = snapshots_by_id["snapshot.settlement-a.created"]
    completed = snapshots_by_id["snapshot.settlement-a.completed"]
    distinct = snapshots_by_id["snapshot.settlement-b.created"]
    for probe_id, left, right, relation in (
        (
            "probe.settlement.same-identity-different-state/v1",
            created,
            completed,
            "same-identity-different-state",
        ),
        (
            "probe.settlement.distinct-identity/v1",
            created,
            distinct,
            "distinct-identity",
        ),
    ):
        equality_probes.append({
            "probe_id": probe_id,
            "left_snapshot_id": left.snapshot_id,
            "right_snapshot_id": right.snapshot_id,
            "relation": relation,
            "comparison_basis": "canonical-identity-only",
            "references_distinct": left is not right,
            "observed_equal": left == right,
            "left_hash": str(hash(left)),
            "right_hash": str(hash(right)),
        })

    base_validators = [asdict(item) for item in base_factory.validators]
    extension_validators = [asdict(item) for item in factory.validators]
    extension = {
        "base_factory_ref": asdict(base_factory.factory_ref),
        "extension_factory_ref": asdict(factory.factory_ref),
        "base_validators_preserved": extension_validators[:len(base_validators)]
            == base_validators,
        "added_validators": extension_validators[len(base_validators):],
        "identity_resolver_preserved": (
            base_factory.identity_resolver_ref == factory.identity_resolver_ref
        ),
        "altered_facets": [],
        "cycle_detected": factory.extend_with_duplicate_blocked() is not None,
    }
    executable = Path(os.path.realpath(sys.executable))
    return {
        "schema_version": "PythonEntityRuntimeObservation/v1",
        "pid": os.getpid(),
        "source_proof": source_proof,
        "route_traces": route_traces,
        "validation_failure_probe": validation_failure,
        "snapshots": rows,
        "equality_probes": equality_probes,
        "extension": extension,
        "per_call_validator_supplied": False,
        "direct_constructor_inaccessible": direct_inaccessible,
        "raw_constructor_helper_exposed": raw_constructor_helper_exposed,
        "rejected_route_ids": rejected_route_ids,
        "toolchain": {
            "python_version": sys.version.split()[0],
            "executable_path": str(executable),
            "executable_sha256": sha256_bytes(executable.read_bytes()),
        },
        "authority_effect": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--payload-base64", required=True)
    arguments = parser.parse_args()
    try:
        if not arguments.source.is_file() or arguments.source.is_symlink():
            raise PythonEntityObserverError("PY_ENTITY_SOURCE_MISSING")
        result = execute(arguments.source, decode_payload(arguments.payload_base64))
        sys.stdout.write(canonical_json(result))
        return 0
    except PythonEntityObserverError as error:
        sys.stderr.write(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
