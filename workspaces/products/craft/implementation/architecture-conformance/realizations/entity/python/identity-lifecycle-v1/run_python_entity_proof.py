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
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/"
    "fixtures/settlement-entity/definition.json"
)
DENOMINATOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/"
    "fixtures/settlement-entity/denominator.json"
)
MUTATIONS_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/"
    "fixtures/settlement-entity/mutants.json"
)
DESCRIPTOR_PATH = (
    "projects/domainspec-v2/development/remaining-meta-types/admissions/entity/"
    "cross-language-realization-descriptor.json"
)
SOURCE_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/"
    "remaining_types/entity_v1.py"
)
OBSERVER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/"
    "python/identity-lifecycle-v1/observe_python_entity.py"
)
SUPERVISOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/"
    "python/identity-lifecycle-v1/run_python_entity_proof.py"
)
PROOF_BUILDER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/"
    "python/identity-lifecycle-v1/index.ts"
)
PROVIDER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/"
    "python-entity-v1.ts"
)
FAMILY_API_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/"
    "identity-lifecycle/index.ts"
)
FAMILY_DECODER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/"
    "providers/decode-identity-lifecycle.ts"
)
FAMILY_EVALUATOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/"
    "evaluator/evaluate-identity-lifecycle.ts"
)
FAMILY_MUTATOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/"
    "mutations/apply-identity-lifecycle-mutant.ts"
)
KERNEL_API_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/"
    "construction-observation/index.ts"
)
KERNEL_CONTRACTS_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/"
    "construction-observation/entity-lifecycle-contracts.ts"
)
KERNEL_EVALUATOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/"
    "construction-observation/entity-lifecycle-construction-observation.ts"
)
BINDING_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/"
    "python/identity-lifecycle-v1/python-binding.json"
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
    "family_decoder_ref": FAMILY_DECODER_PATH,
    "family_evaluator_ref": FAMILY_EVALUATOR_PATH,
    "family_mutator_ref": FAMILY_MUTATOR_PATH,
    "kernel_api_ref": KERNEL_API_PATH,
    "kernel_contracts_ref": KERNEL_CONTRACTS_PATH,
    "kernel_evaluator_ref": KERNEL_EVALUATOR_PATH,
}


class PythonEntityProofError(Exception):
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
        raise PythonEntityProofError("PY_ENTITY_INPUT_MISSING", relative)
    return target.read_bytes()


def read_json(root: Path, relative: str) -> dict[str, Any]:
    try:
        value = json.loads(read_bytes(root, relative))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PythonEntityProofError("PY_ENTITY_JSON_INVALID", relative) from error
    if type(value) is not dict:
        raise PythonEntityProofError("PY_ENTITY_JSON_INVALID", relative)
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
        raise PythonEntityProofError("PY_ENTITY_BINDING_SHAPE_INVALID")
    if document_digest(binding, "binding_sha256") != binding["binding_sha256"]:
        raise PythonEntityProofError("PY_ENTITY_BINDING_DIGEST_STALE")
    if (
        binding["schema_version"] != "PythonEntityBinding/v1"
        or binding["binding_id"] != "python.settlement-entity.identity-lifecycle/v1"
        or binding["target_id"] != "entity.python.settlement/v1"
        or binding["protocol_id"] != "python.validated-extensible-entity-factory/v1"
        or binding["observer_id"] != "observer.python-entity-closed-subset/v1"
        or binding["observer_owner_ref"] != "python-entity-proof-harness"
        or binding["proof_mechanism"]
            != "hash-locked-source-ast-bytecode-runtime-plus-two-fresh-processes"
        or binding["authority_effect"] != "none"
    ):
        raise PythonEntityProofError("PY_ENTITY_BINDING_POLICY_INVALID")
    for field, expected_path in EXPECTED_REFS.items():
        reference = binding[field]
        if (
            type(reference) is not dict
            or set(reference) != {"path", "sha256"}
            or reference.get("path") != expected_path
            or sha256_bytes(read_bytes(root, expected_path)) != reference.get("sha256")
        ):
            role = {
                "mutation_catalogue_ref": "mutations",
                "proof_builder_ref": "proof_builder",
                "family_api_ref": "family_api",
                "family_decoder_ref": "family_decoder",
                "family_evaluator_ref": "family_evaluator",
                "family_mutator_ref": "family_mutator",
                "kernel_api_ref": "kernel_api",
                "kernel_contracts_ref": "kernel_contracts",
                "kernel_evaluator_ref": "kernel_evaluator",
            }.get(field, field.removesuffix("_ref"))
            raise PythonEntityProofError("PY_ENTITY_BINDING_INPUT_STALE", role)
    executable = Path(os.path.realpath(sys.executable))
    if (
        binding["python_version"] != sys.version.split()[0]
        or binding["python_executable_path"] != str(executable)
        or binding["python_executable_sha256"] != sha256_bytes(executable.read_bytes())
    ):
        raise PythonEntityProofError("PY_ENTITY_TOOLCHAIN_STALE")
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
    try:
        for process in processes:
            stdout, stderr = process.communicate(timeout=20)
            if process.returncode != 0 or stderr:
                raise PythonEntityProofError(
                    "PY_ENTITY_OBSERVER_FAILED",
                    stderr.strip() or str(process.returncode),
                )
            value = json.loads(stdout)
            if type(value) is not dict:
                raise PythonEntityProofError("PY_ENTITY_OBSERVER_OUTPUT_INVALID")
            observations.append(value)
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.wait()
    first, second = observations
    if type(first.get("pid")) is not int or type(second.get("pid")) is not int:
        raise PythonEntityProofError("PY_ENTITY_PROCESS_ISOLATION_FAILED")
    if first["pid"] == second["pid"]:
        raise PythonEntityProofError("PY_ENTITY_PROCESS_ISOLATION_FAILED")
    first_semantic = {key: value for key, value in first.items() if key != "pid"}
    second_semantic = {key: value for key, value in second.items() if key != "pid"}
    if canonical_json(first_semantic) != canonical_json(second_semantic):
        raise PythonEntityProofError("PY_ENTITY_PROCESS_REPLAY_MISMATCH")
    return first


def source_controls(source: str) -> dict[str, str]:
    controls = {
        "per-call-validator-bypass": source.replace(
            "def create(\n        self,\n        input_data: SettlementEntityInput,\n    )",
            "def create(\n        self,\n        input_data: SettlementEntityInput,\n        per_call_validator=None,\n    )",
            1,
        ),
        "remove-base-validator": source.replace(
            "return BASE_VALIDATORS\n",
            "return BASE_VALIDATORS[1:]\n",
            1,
        ),
        "replace-identity-resolver": source.replace(
            "return IDENTITY_RESOLVER_REF",
            "return IdentityResolverRef(\"replacement\", \"e\" * 64)",
            1,
        ),
        "allow-extension-cycle": source.replace(
            "if self.mode != \"base\":\n            return None",
            "if self.mode != \"base\":\n            return SettlementEntityFactory(\"duplicate-blocked\")",
            1,
        ),
        "invalid-input-forms-snapshot": source.replace(
            "False,\n                    None,\n                    (failure_code,)",
            "True,\n                    _construct_snapshot(),\n                    ()",
            1,
        ),
        "mutable-snapshot": source.replace(
            "@dataclass(frozen=True, slots=True, eq=False, init=False)\n"
            "    class SettlementEntitySnapshot:",
            "@dataclass(frozen=False, slots=True, eq=False, init=False)\n"
            "    class SettlementEntitySnapshot:",
            1,
        ),
        "complete-field-equality": source.replace(
            "return self.identity == other.identity",
            "return (self.identity, self.state_sha256) == "
            "(other.identity, other.state_sha256)",
            1,
        ),
        "reconstruction-bypass": source.replace(
            "return self._execute(\"deserialization-reconstruction\", input_data)",
            "return self._execute(\"factory\", input_data)",
            1,
        ),
        "transition-identity-replacement": source.replace(
            "predecessor.identity.settlement_id.normalized_value_sha256",
            "predecessor.identity.organization_id.normalized_value_sha256",
            1,
        ),
        "constructor-exposure": source.replace(
            "if observed is not construction_token:",
            "if False:",
            1,
        ),
        "route-whitelist-bypass": source.replace(
            "if route_id not in (\n"
            "            \"factory\",\n"
            "            \"deserialization-reconstruction\",\n"
            "            \"lifecycle-transition\",\n"
            "        ):",
            "if False:",
            1,
        ),
    }
    if any(mutated == source for mutated in controls.values()):
        raise PythonEntityProofError("PY_ENTITY_SOURCE_CONTROL_NOOP")
    return controls


def execute_source_controls(
    observer: Path,
    source: str,
    payload: dict[str, Any],
) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="domainspec-python-entity-controls-") as raw:
        root = Path(raw)
        try:
            for index, (control_id, mutated) in enumerate(source_controls(source).items()):
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
                    raise PythonEntityProofError(
                        "PY_ENTITY_SOURCE_CONTROL_SURVIVED",
                        control_id,
                    )
                code = completed.stderr.strip().split(":", 1)[0]
                if not code.startswith("PY_ENTITY_"):
                    raise PythonEntityProofError(
                        "PY_ENTITY_SOURCE_CONTROL_EVIDENCE_INVALID",
                        control_id,
                    )
                results.append({
                    "control_id": control_id,
                    "evidence_kind": "python-target-source-control",
                    "status": "rejected",
                    "error_code": code,
                })
        finally:
            for residue in root.rglob("__pycache__"):
                raise PythonEntityProofError("PY_ENTITY_CACHE_RESIDUE", str(residue))
    return results


def build_payload(definition: dict[str, Any]) -> dict[str, Any]:
    return {
        "snapshots": definition["snapshots"],
        "validation_failure": definition["validation_failure"],
    }


def build_proof(root: Path) -> dict[str, Any]:
    binding = validate_binding(root)
    definition = read_json(root, DEFINITION_PATH)
    payload = build_payload(definition)
    observer = root / OBSERVER_PATH
    source = root / SOURCE_PATH
    observation = run_pair(observer, source, payload)
    if observation.get("source_proof", {}).get("source_sha256") != binding["source_ref"]["sha256"]:
        raise PythonEntityProofError("PY_ENTITY_NATIVE_SOURCE_STALE")
    if observation.get("toolchain") != {
        "python_version": binding["python_version"],
        "executable_path": binding["python_executable_path"],
        "executable_sha256": binding["python_executable_sha256"],
    }:
        raise PythonEntityProofError("PY_ENTITY_NATIVE_TOOLCHAIN_STALE")
    controls = execute_source_controls(
        observer,
        read_bytes(root, SOURCE_PATH).decode("utf8"),
        payload,
    )
    semantic = {key: value for key, value in observation.items() if key != "pid"}
    return {
        "schema_version": "PythonEntityNativeProof/v1",
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
        "target_source_controls": controls,
        "target_source_accounting": {
            "declared": len(controls),
            "rejected": len(controls),
        },
        "claim_ceiling": (
            "one exact hash-locked candidate-local Python Settlement Entity target "
            "over inert owner JSON cases, two fresh Python processes, frozen dataclass "
            "snapshots, typed composite stable identity, identity-only equality and "
            "owned deterministic hash, exact base-before-extension validators, "
            "structured no-snapshot failure, factory reconstruction and transition "
            "pipeline convergence, inaccessible direct constructor, additive acyclic "
            "extension, and eleven actual target-source controls; no arbitrary Python, "
            "OS interception, hash collision freedom, cross-language hash bytes or "
            "parity, registration, candidate projection, promotion, publication, "
            "release, deployment, or production claim"
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
    except PythonEntityProofError as error:
        sys.stderr.write(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
