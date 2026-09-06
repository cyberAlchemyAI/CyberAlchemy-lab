from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


DEFINITION_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/"
    "fixtures/settlement-value/definition.json"
)
DENOMINATOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/"
    "fixtures/settlement-value/denominator.json"
)
MUTATIONS_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/"
    "fixtures/settlement-value/mutants.json"
)
DESCRIPTOR_PATH = (
    "projects/domainspec-v2/development/remaining-meta-types/admissions/value-object/"
    "cross-language-realization-descriptor.json"
)
SOURCE_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/"
    "remaining_types/value_object_v1.py"
)
OBSERVER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/"
    "python/complete-value-v1/observe_python_value_object.py"
)
SUPERVISOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/"
    "python/complete-value-v1/run_python_value_object_proof.py"
)
PROOF_BUILDER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/"
    "python/complete-value-v1/index.ts"
)
PROVIDER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/"
    "python-value-object-v1.ts"
)
FAMILY_API_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/index.ts"
)
KERNEL_API_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/"
    "construction-observation/index.ts"
)
BINDING_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/"
    "python/complete-value-v1/python-binding.json"
)
EXPECTED_REFS = {
    "definition_ref": DEFINITION_PATH,
    "denominator_ref": DENOMINATOR_PATH,
    "mutation_catalogue_ref": MUTATIONS_PATH,
    "descriptor_ref": DESCRIPTOR_PATH,
    "source_ref": SOURCE_PATH,
    "observer_ref": OBSERVER_PATH,
    "supervisor_ref": SUPERVISOR_PATH,
    "proof_builder_ref": PROOF_BUILDER_PATH,
    "provider_ref": PROVIDER_PATH,
    "family_api_ref": FAMILY_API_PATH,
    "kernel_api_ref": KERNEL_API_PATH,
}


class PythonValueObjectProofError(Exception):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_bytes(root: Path, relative: str) -> bytes:
    target = root / relative
    if not target.is_file() or target.is_symlink():
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_INPUT_MISSING", relative)
    return target.read_bytes()


def read_json(root: Path, relative: str) -> dict[str, Any]:
    try:
        value = json.loads(read_bytes(root, relative))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_JSON_INVALID", relative) from error
    if type(value) is not dict:
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_JSON_INVALID", relative)
    return value


def document_digest(value: dict[str, Any], field: str) -> str:
    return sha256_bytes(canonical_json({
        key: child for key, child in value.items() if key != field
    }).encode("utf8"))


def validate_binding(root: Path) -> dict[str, Any]:
    binding = read_json(root, BINDING_PATH)
    expected_keys = {
        "schema_version", "binding_id", "target_id", "protocol_id",
        *EXPECTED_REFS.keys(), "observer_id", "observer_owner_ref",
        "proof_mechanism", "python_version", "python_executable_path",
        "python_executable_sha256", "authority_effect", "binding_sha256",
    }
    if set(binding) != expected_keys:
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_BINDING_SHAPE_INVALID")
    if document_digest(binding, "binding_sha256") != binding["binding_sha256"]:
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_BINDING_DIGEST_STALE")
    if (
        binding["schema_version"] != "PythonValueObjectBinding/v1"
        or binding["binding_id"] != "python.settlement-value.complete-value/v1"
        or binding["target_id"] != "value-object.python.settlement-value/v1"
        or binding["protocol_id"] != "python.owned-value-object-factory/v1"
        or binding["observer_id"]
            != "observer.python-value-object-closed-subset/v1"
        or binding["observer_owner_ref"] != "python-value-object-proof-harness"
        or binding["proof_mechanism"]
            != "exact-source-ast-bytecode-plus-two-fresh-processes"
        or binding["authority_effect"] != "none"
    ):
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_BINDING_POLICY_INVALID")
    for field, expected_path in EXPECTED_REFS.items():
        reference = binding[field]
        if (
            type(reference) is not dict
            or set(reference) != {"path", "sha256"}
            or reference.get("path") != expected_path
            or sha256_bytes(read_bytes(root, expected_path)) != reference.get("sha256")
        ):
            raise PythonValueObjectProofError(
                "PY_VALUE_OBJECT_BINDING_INPUT_STALE",
                field.removesuffix("_ref"),
            )
    executable = Path(os.path.realpath(sys.executable))
    if (
        binding["python_version"] != sys.version.split()[0]
        or binding["python_executable_path"] != str(executable)
        or binding["python_executable_sha256"] != sha256_bytes(executable.read_bytes())
    ):
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_TOOLCHAIN_STALE")
    return binding


def encode_payload(payload: dict[str, Any]) -> str:
    return base64.b64encode(canonical_json(payload).encode("utf8")).decode("ascii")


def observer_command(observer: Path, source: Path, payload: dict[str, Any]) -> list[str]:
    return [
        sys.executable,
        "-I",
        "-B",
        str(observer),
        "--source",
        str(source),
        "--payload-base64",
        encode_payload(payload),
    ]


def run_observer(observer: Path, source: Path, payload: dict[str, Any]) -> dict[str, Any]:
    completed = subprocess.run(
        observer_command(observer, source, payload),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf8",
        env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"},
        timeout=20,
        check=False,
    )
    if completed.returncode != 0 or completed.stderr:
        raise PythonValueObjectProofError(
            "PY_VALUE_OBJECT_OBSERVER_FAILED",
            completed.stderr.strip() or str(completed.returncode),
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_OBSERVER_OUTPUT_INVALID") from error
    if type(result) is not dict:
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_OBSERVER_OUTPUT_INVALID")
    return result


def run_pair(observer: Path, source: Path, payload: dict[str, Any]) -> dict[str, Any]:
    command = observer_command(observer, source, payload)
    processes = [
        subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf8",
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"},
        )
        for _ in range(2)
    ]
    observations: list[dict[str, Any]] = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=20)
        if process.returncode != 0 or stderr:
            raise PythonValueObjectProofError(
                "PY_VALUE_OBJECT_OBSERVER_FAILED",
                stderr.strip() or str(process.returncode),
            )
        value = json.loads(stdout)
        if type(value) is not dict:
            raise PythonValueObjectProofError("PY_VALUE_OBJECT_OBSERVER_OUTPUT_INVALID")
        observations.append(value)
    first, second = observations
    if type(first.get("pid")) is not int or type(second.get("pid")) is not int:
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_PROCESS_ISOLATION_FAILED")
    if first["pid"] == second["pid"]:
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_PROCESS_ISOLATION_FAILED")
    first_semantic = {key: value for key, value in first.items() if key != "pid"}
    second_semantic = {key: value for key, value in second.items() if key != "pid"}
    if canonical_json(first_semantic) != canonical_json(second_semantic):
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_PROCESS_REPLAY_MISMATCH")
    return first


def static_controls(source: str) -> dict[str, str]:
    controls = {
        "reference-identity": source.replace(
            "and self.settlement_account == other.settlement_account",
            "and self.settlement_account is other.settlement_account",
            1,
        ),
        "partial-tuple": source.replace(
            "and self.minor_units_sha256 == other.minor_units_sha256",
            "and True",
            1,
        ),
        "mutable-nested": source.replace(
            "@dataclass(frozen=True, slots=True)\nclass SettlementAccountValue:",
            "@dataclass(frozen=False, slots=True)\nclass SettlementAccountValue:",
            1,
        ),
        "nested-alias": source.replace(
            "input_data.settlement_account.account_ref,",
            "str(input_data.settlement_account),",
            1,
        ),
        "validator-bypass": source.replace(
            "for validator in self.validators:",
            "for validator in ():",
            1,
        ),
        "tuple-change": source.replace(
            "return _stable_hash((\n"
            "            self.currency_sha256,\n"
            "            self.minor_units_sha256,\n"
            "            self.settlement_account.protocol_id,\n"
            "            self.settlement_account.protocol_sha256,\n"
            "            self.settlement_account.normalized_value_sha256,\n"
            "        ))",
            "return _stable_hash((self.currency_sha256,))",
            1,
        ),
        "protocol-bypass": source.replace(
            "and observed.protocol_sha256 == expected.protocol_sha256",
            "and True",
            1,
        ),
        "invalid-forms": source.replace(
            "return ValidationFailure(\n                False,\n                None,",
            "return FormationSuccess(\n                True,\n                object(),",
            1,
        ),
    }
    if any(mutated == source for mutated in controls.values()):
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_STATIC_CONTROL_NOOP")
    return controls


def execute_static_controls(
    observer: Path,
    source: str,
    payload: dict[str, Any],
) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="domainspec-python-value-object-controls-") as raw:
        root = Path(raw)
        for index, (control_id, mutated) in enumerate(static_controls(source).items()):
            target = root / f"{index:02d}-{control_id}.py"
            target.write_text(mutated, encoding="utf8", newline="\n")
            completed = subprocess.run(
                observer_command(observer, target, payload),
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf8",
                env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"},
                timeout=20,
                check=False,
            )
            if completed.returncode == 0:
                raise PythonValueObjectProofError(
                    "PY_VALUE_OBJECT_STATIC_CONTROL_SURVIVED",
                    control_id,
                )
            code = completed.stderr.strip().split(":", 1)[0]
            if not code.startswith("PY_VALUE_OBJECT_"):
                raise PythonValueObjectProofError(
                    "PY_VALUE_OBJECT_STATIC_CONTROL_EVIDENCE_INVALID",
                    control_id,
                )
            results.append({
                "control_id": control_id,
                "evidence_kind": "python-static-binding-control",
                "status": "rejected",
                "error_code": code,
            })
    return results


def build_payload(definition: dict[str, Any]) -> dict[str, Any]:
    cases = []
    for test_case in definition["cases"]:
        cases.append({
            "case_id": test_case["case_id"],
            "input_class": test_case["input_class"],
            "components": {
                component["component_name"]: {
                    "protocol_id": component["protocol_id"].replace(
                        "typescript.", "python.", 1,
                    ),
                    "protocol_sha256": component["protocol_sha256"],
                    "normalized_value_sha256": test_case[
                        "normalized_component_values"
                    ][component["component_name"]],
                }
                for component in definition["components"]
            },
        })
    probes = [{
        **definition["equality_contract"]["equal_probe"],
        "relation": "equal-tuple",
        "varied_component_name": None,
    }]
    probes.extend({
        **variant,
        "relation": "component-variant",
        "varied_component_name": variant["component_name"],
    } for variant in definition["equality_contract"]["component_variants"])
    nested_variant = next(
        item for item in definition["equality_contract"]["component_variants"]
        if item["component_name"] == "settlement_account"
    )
    return {
        "cases": cases,
        "probes": probes,
        "nested_probe": {
            "component_name": "settlement_account",
            "left_case_id": definition["equality_contract"]["equal_probe"]["left_case_id"],
            "right_case_id": definition["equality_contract"]["equal_probe"]["right_case_id"],
            "variant_case_id": nested_variant["right_case_id"],
        },
    }


def build_proof(root: Path) -> dict[str, Any]:
    binding = validate_binding(root)
    definition = read_json(root, DEFINITION_PATH)
    payload = build_payload(definition)
    observer = root / OBSERVER_PATH
    source = root / SOURCE_PATH
    observation = run_pair(observer, source, payload)
    if observation.get("source_proof", {}).get("source_sha256") != binding["source_ref"]["sha256"]:
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_NATIVE_SOURCE_STALE")
    if observation.get("toolchain") != {
        "python_version": binding["python_version"],
        "executable_path": binding["python_executable_path"],
        "executable_sha256": binding["python_executable_sha256"],
    }:
        raise PythonValueObjectProofError("PY_VALUE_OBJECT_NATIVE_TOOLCHAIN_STALE")
    controls = execute_static_controls(
        observer,
        read_bytes(root, SOURCE_PATH).decode("utf8"),
        payload,
    )
    semantic = {key: value for key, value in observation.items() if key != "pid"}
    return {
        "schema_version": "PythonValueObjectNativeProof/v1",
        "target": {
            "target_id": binding["target_id"],
            "target_sha256": binding["source_ref"]["sha256"],
            "language": "python",
            "protocol_id": binding["protocol_id"],
        },
        "binding": {
            "binding_id": binding["binding_id"],
            "binding_sha256": binding["binding_sha256"],
        },
        "runtime_observation": semantic,
        "process_evidence": {
            "executions": 2,
            "distinct_pids": 2,
            "pids_redacted_from_semantic_proof": True,
            "semantic_replay_equal": True,
            "semantic_replay_sha256": sha256_bytes(canonical_json(semantic).encode("utf8")),
            "input_materialization": "json-inert-owner-cases",
        },
        "static_binding_controls": controls,
        "static_binding_accounting": {
            "declared": len(controls),
            "rejected": len(controls),
        },
        "claim_ceiling": (
            "one exact hash-locked candidate-local Python Settlement Value Object over "
            "owner JSON cases, two fresh processes, exact AST and bytecode admission, "
            "complete normalized tuple equality, owned congruent hash, recursive frozen "
            "owned components, exact bound validators and component protocols, and "
            "one-way additive validation-only extension; no arbitrary Python, reflection "
            "or mutable caller input, OS interception, business correctness beyond the "
            "owner fixture, collision freedom, cross-language hash bytes, parity, "
            "registration, promotion, publication, deployment, or production claim"
        ),
        "authority_effect": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        proof = build_proof(arguments.repository_root.resolve())
        arguments.output.write_text(
            canonical_json(proof) + "\n",
            encoding="utf8",
            newline="\n",
        )
        return 0
    except PythonValueObjectProofError as error:
        sys.stderr.write(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
