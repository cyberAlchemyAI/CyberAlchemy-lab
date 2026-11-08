from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


DEFINITION_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/"
    "read-model/fixtures/complete-settlement/definition.json"
)
DENOMINATOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/"
    "read-model/fixtures/complete-settlement/denominator.json"
)
MUTATIONS_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/"
    "read-model/fixtures/complete-settlement/mutants.json"
)
DESCRIPTOR_PATH = (
    "projects/domainspec-v2/development/remaining-meta-types/admissions/"
    "query/cross-language-realization-descriptor.json"
)
SOURCE_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/"
    "remaining_types/query_v1.py"
)
OBSERVER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "query/python/read-model-v1/observe_python_query_case.py"
)
SUPERVISOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "query/python/read-model-v1/run_python_query_proof.py"
)
PROOF_BUILDER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "query/python/read-model-v1/index.ts"
)
PROVIDER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/"
    "providers/python-query-v1.ts"
)
FAMILY_API_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/"
    "read-model/index.ts"
)
KERNEL_API_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/"
    "effect-observation/index.ts"
)
BINDING_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "query/python/read-model-v1/python-binding.json"
)
READ_TARGETS = (
    "settlement.read.settlement-by-id",
    "settlement.read.payout-by-settlement",
)
RESULT_FIELDS = (
    "settlement_id",
    "settlement_status",
    "gross_amount_minor",
    "payout_id",
    "payout_status",
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


class PythonQueryProofError(Exception):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_bytes(root: Path, relative: str) -> bytes:
    target = root / relative
    if not target.is_file() or target.is_symlink():
        raise PythonQueryProofError("PY_QUERY_INPUT_MISSING", relative)
    return target.read_bytes()


def read_json(root: Path, relative: str) -> dict[str, Any]:
    try:
        value = json.loads(read_bytes(root, relative))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PythonQueryProofError("PY_QUERY_JSON_INVALID", relative) from error
    if type(value) is not dict:
        raise PythonQueryProofError("PY_QUERY_JSON_INVALID", relative)
    return value


def document_digest(value: dict[str, Any], field: str) -> str:
    body = {key: child for key, child in value.items() if key != field}
    return sha256_bytes(canonical_json(body).encode("utf8"))


def validate_binding(root: Path) -> dict[str, Any]:
    binding = read_json(root, BINDING_PATH)
    expected_keys = {
        "schema_version",
        "binding_id",
        "target_id",
        "protocol_id",
        "output_concept_id",
        *EXPECTED_REFS.keys(),
        "observer_id",
        "observer_owner_ref",
        "symbol_name",
        "proof_mechanism",
        "authority_effect",
        "binding_sha256",
    }
    if set(binding) != expected_keys:
        raise PythonQueryProofError("PY_QUERY_BINDING_SHAPE_INVALID")
    if (
        binding["schema_version"] != "PythonQueryBinding/v1"
        or binding["binding_id"]
        != "python.complete-settlement.bound-query/v1"
        or binding["target_id"] != "query.python.complete-settlement/v1"
        or binding["protocol_id"] != "python.bound-query/v1"
        or binding["output_concept_id"]
        != "settlement.CompleteSettlementView"
        or binding["observer_id"]
        != "observer.python-query-closed-subset/v1"
        or binding["observer_owner_ref"] != "python-query-proof-harness"
        or binding["symbol_name"] != "read_complete_settlement"
        or binding["proof_mechanism"]
        != "exact-ast-bytecode-audit-plus-two-fresh-processes"
        or binding["authority_effect"] != "none"
        or type(binding["binding_sha256"]) is not str
        or document_digest(binding, "binding_sha256")
        != binding["binding_sha256"]
    ):
        raise PythonQueryProofError("PY_QUERY_BINDING_POLICY_INVALID")
    for field, expected_path in EXPECTED_REFS.items():
        reference = binding[field]
        if (
            type(reference) is not dict
            or set(reference) != {"path", "sha256"}
            or reference.get("path") != expected_path
            or type(reference.get("sha256")) is not str
            or sha256_bytes(read_bytes(root, expected_path))
            != reference["sha256"]
        ):
            raise PythonQueryProofError("PY_QUERY_BINDING_INPUT_STALE", field)
    return binding


def encode_payload(payload: dict[str, Any]) -> str:
    return base64.b64encode(
        canonical_json(payload).encode("utf8"),
    ).decode("ascii")


def observer_command(
    observer: Path,
    source: Path,
    payload: dict[str, Any],
) -> list[str]:
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


def run_pair(
    observer: Path,
    source: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    command = observer_command(observer, source, payload)
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
    }
    processes = [
        subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf8",
            env=environment,
        )
        for _ in range(2)
    ]
    observations: list[dict[str, Any]] = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=15)
        if process.returncode != 0 or stderr:
            raise PythonQueryProofError(
                "PY_QUERY_OBSERVER_FAILED",
                stderr.strip() or str(process.returncode),
            )
        try:
            value = json.loads(stdout)
        except json.JSONDecodeError as error:
            raise PythonQueryProofError(
                "PY_QUERY_OBSERVER_OUTPUT_INVALID",
            ) from error
        if type(value) is not dict:
            raise PythonQueryProofError("PY_QUERY_OBSERVER_OUTPUT_INVALID")
        observations.append(value)
    first, second = observations
    if (
        type(first.get("pid")) is not int
        or type(second.get("pid")) is not int
        or first["pid"] == second["pid"]
    ):
        raise PythonQueryProofError("PY_QUERY_PROCESS_ISOLATION_FAILED")
    first_semantic = {key: value for key, value in first.items() if key != "pid"}
    second_semantic = {key: value for key, value in second.items() if key != "pid"}
    if canonical_json(first_semantic) != canonical_json(second_semantic):
        raise PythonQueryProofError("PY_QUERY_PROCESS_REPLAY_MISMATCH")
    return first, second


def hostile_sources(source: str) -> dict[str, str]:
    swapped = source.replace(READ_TARGETS[0], "__QUERY_TARGET_SWAP__", 1)
    swapped = swapped.replace(READ_TARGETS[1], READ_TARGETS[0], 1)
    swapped = swapped.replace("__QUERY_TARGET_SWAP__", READ_TARGETS[1], 1)
    duplicate = source.replace(READ_TARGETS[1], READ_TARGETS[0], 1)
    hidden_write = source.replace(
        "def read_complete_settlement(input_data, read):\n",
        "def read_complete_settlement(input_data, read):\n"
        "    open('/tmp/domainspec-query-hostile', 'w').write('x')\n",
        1,
    )
    write_restore = source.replace(
        "def read_complete_settlement(input_data, read):\n",
        "def read_complete_settlement(input_data, read):\n"
        "    scratch = {}\n"
        "    scratch['value'] = 1\n"
        "    scratch.clear()\n",
        1,
    )
    deferred = source.replace(
        "def read_complete_settlement(input_data, read):",
        "async def read_complete_settlement(input_data, read):",
        1,
    )
    dynamic_import = source.replace(
        "def read_complete_settlement(input_data, read):\n",
        "def read_complete_settlement(input_data, read):\n"
        "    __import__('os')\n",
        1,
    )
    computed_read = source.replace(
        f'        "{READ_TARGETS[0]}",',
        '        "settlement.read." + "settlement-by-id",',
        1,
    )
    extra_output = source.replace(
        '        "payout_status": payout["payout_status"],\n',
        '        "payout_status": payout["payout_status"],\n'
        '        "extra": "not-declared",\n',
        1,
    )
    values = {
        "swapped-read-order": swapped,
        "duplicate-read": duplicate,
        "hidden-write": hidden_write,
        "write-then-restore": write_restore,
        "deferred-lazy": deferred,
        "dynamic-import": dynamic_import,
        "computed-read-target": computed_read,
        "extra-output-field": extra_output,
    }
    if any(value == source for value in values.values()):
        raise PythonQueryProofError("PY_QUERY_HOSTILE_SOURCE_UNCHANGED")
    return values


def execute_hostiles(
    observer: Path,
    canonical_source: str,
    payload: dict[str, Any],
) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="domainspec-python-query-hostiles-") as raw:
        root = Path(raw)
        for index, (hostile_id, source) in enumerate(
            hostile_sources(canonical_source).items(),
        ):
            path = root / f"{index:02d}-{hostile_id}.py"
            path.write_text(source, encoding="utf8", newline="\n")
            completed = subprocess.run(
                observer_command(observer, path, payload),
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf8",
                env={
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONHASHSEED": "0",
                },
                timeout=15,
                check=False,
            )
            if completed.returncode == 0:
                raise PythonQueryProofError(
                    "PY_QUERY_SOURCE_HOSTILE_SURVIVED",
                    hostile_id,
                )
            error_code = completed.stderr.strip().split(":", 1)[0]
            if not error_code.startswith("PY_QUERY_"):
                raise PythonQueryProofError(
                    "PY_QUERY_SOURCE_HOSTILE_EVIDENCE_INVALID",
                    hostile_id,
                )
            results.append({
                "hostile_id": hostile_id,
                "evidence_kind": "python-source-hostile",
                "status": "killed",
                "error_code": error_code,
            })
    return results


def build_proof(root: Path) -> dict[str, Any]:
    binding = validate_binding(root)
    definition = read_json(root, DEFINITION_PATH)
    cases = definition.get("cases")
    read_targets = definition.get("read_targets")
    output_concept = definition.get("output_concept")
    if (
        type(cases) is not list
        or len(cases) != 1
        or type(cases[0]) is not dict
        or type(read_targets) is not list
        or tuple(item.get("target_id") for item in read_targets) != READ_TARGETS
        or type(output_concept) is not dict
        or output_concept.get("concept_id")
        != binding["output_concept_id"]
        or tuple(item.get("name") for item in output_concept.get("fields", []))
        != RESULT_FIELDS
    ):
        raise PythonQueryProofError("PY_QUERY_OWNER_DEFINITION_INVALID")
    owner_case = cases[0]
    inputs = owner_case.get("inputs")
    expected_result = owner_case.get("expected_result")
    if type(inputs) is not dict or type(expected_result) is not dict:
        raise PythonQueryProofError("PY_QUERY_OWNER_CASE_INVALID")
    fixtures = {
        READ_TARGETS[0]: {
            "settlement_status": expected_result["settlement_status"],
            "gross_amount_minor": expected_result["gross_amount_minor"],
        },
        READ_TARGETS[1]: {
            "payout_id": expected_result["payout_id"],
            "payout_status": expected_result["payout_status"],
        },
    }
    payload = {
        "case_id": owner_case["case_id"],
        "input": inputs,
        "fixtures": fixtures,
    }
    observer = root / OBSERVER_PATH
    source = root / SOURCE_PATH
    first, second = run_pair(observer, source, payload)
    if (
        first.get("result") != expected_result
        or tuple(item.get("target_id") for item in first.get("trace", []))
        != READ_TARGETS
        or first.get("runtime_audit_events") != []
        or first.get("mutable_alias_observed") is not False
        or first.get("quiescence", {}).get("observed") is not True
        or first.get("quiescence", {}).get("pending_count") != 0
        or first.get("source_proof", {}).get("source_sha256")
        != binding["source_ref"]["sha256"]
    ):
        raise PythonQueryProofError("PY_QUERY_NATIVE_OBSERVATION_INVALID")
    source_text = read_bytes(root, SOURCE_PATH).decode("utf8")
    hostiles = execute_hostiles(observer, source_text, payload)
    semantic_observation = {
        key: value for key, value in first.items() if key != "pid"
    }
    return {
        "schema_version": "PythonQueryNativeProof/v1",
        "target": {
            "target_id": binding["target_id"],
            "target_sha256": binding["source_ref"]["sha256"],
            "language": "python",
            "protocol_id": binding["protocol_id"],
            "output_concept_id": binding["output_concept_id"],
        },
        "binding": {
            "binding_id": binding["binding_id"],
            "binding_sha256": binding["binding_sha256"],
        },
        "owner_case": {
            "case_id": owner_case["case_id"],
            "input": inputs,
            "input_sha256": sha256_bytes(
                canonical_json(inputs).encode("utf8"),
            ),
            "expected_result": expected_result,
        },
        "observation": semantic_observation,
        "process_evidence": {
            "executions": 2,
            "distinct_pids": 2,
            "pids_redacted_from_semantic_proof": True,
            "semantic_replay_equal": True,
            "trace_sha256": sha256_bytes(
                canonical_json(first["trace"]).encode("utf8"),
            ),
            "result_sha256": sha256_bytes(
                canonical_json(first["result"]).encode("utf8"),
            ),
            "input_materialization": "json-inert-mapping-proxy",
            "read_fixtures": "json-inert-mapping-proxy",
            "lifecycle_basis": first["source_proof"]["lifecycle_basis"],
        },
        "source_hostiles": hostiles,
        "source_hostile_accounting": {
            "declared": len(hostiles),
            "killed": len(hostiles),
        },
        "claim_ceiling": (
            "owner-fixture Python exact-source Query observation over JSON-"
            "materialized inert mapping inputs and fixtures, two fresh child "
            "processes, an actual ordered harness read trace, a closed plain "
            "scalar result, AST and bytecode source rejection, runtime audit "
            "silence, and static exclusion of unsupported lifecycle surfaces; "
            "no arbitrary Python or generated source, getter Proxy or mutable "
            "caller input, universal runtime or OS interception, failure-path "
            "behavior, business correctness, parity, registration, promotion, "
            "release, deployment, or production claim"
        ),
        "authority_effect": "none",
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        root = arguments.repository_root.resolve()
        proof = build_proof(root)
        arguments.output.write_text(
            canonical_json(proof) + "\n",
            encoding="utf8",
            newline="\n",
        )
        return 0
    except PythonQueryProofError as error:
        sys.stderr.write(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
