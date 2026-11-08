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


SOURCE_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/"
    "remaining_types/operation_v1.py"
)
OBSERVER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "operation/python/state-changing-v1/observe_python_operation_case.py"
)
SUPERVISOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "operation/python/state-changing-v1/run_python_operation_proof.py"
)
PROOF_BUILDER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "operation/python/state-changing-v1/index.ts"
)
PROVIDER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/"
    "providers/operation-python-v1.ts"
)
BINDING_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "operation/python/state-changing-v1/python-binding.json"
)

BOUND_PATHS = {
    "admission": (
        "projects/domainspec-v2/development/remaining-meta-types/active-types/"
        "operation/admission/admission.json"
    ),
    "definition": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/fixtures/complete-settlement/"
        "operation-contract.json"
    ),
    "denominator": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/fixtures/complete-settlement/denominator.json"
    ),
    "positive_observations": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/fixtures/complete-settlement/"
        "positive-observation.json"
    ),
    "family_contracts": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/contracts/state-changing-action-contracts.ts"
    ),
    "family_decoder": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/providers/decode-state-changing-action.ts"
    ),
    "family_evaluator": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/evaluator/evaluate-state-changing-action.ts"
    ),
    "family_mutator": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/mutations/apply-operation-hostile.ts"
    ),
    "hostile_catalogue": (
        "projects/domainspec-v2/development/refinement-runs/"
        "20260814T193343Z-active-meta-type-implementations/refreshes/"
        "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/"
        "HOSTILE-CATALOGUE.json"
    ),
    "relation_contracts": (
        "projects/domainspec-v2/development/refinement-runs/"
        "20260814T193343Z-active-meta-type-implementations/refreshes/"
        "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/"
        "RELATION-CONTRACTS.json"
    ),
    "source": SOURCE_PATH,
    "observer": OBSERVER_PATH,
    "supervisor": SUPERVISOR_PATH,
    "proof_builder": PROOF_BUILDER_PATH,
    "provider": PROVIDER_PATH,
    "provider_contract": (
        "projects/domainspec-v2/impl/architecture-conformance/factory/"
        "contracts/factory-node-provider-v1.ts"
    ),
    "hostile_01_undeclared_write": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/undeclared-write.json"
    ),
    "hostile_02_undeclared_effect": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/undeclared-effect.json"
    ),
    "hostile_03_guard_bypass": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/guard-bypass.json"
    ),
    "hostile_04_order_swap": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/order-swap.json"
    ),
    "hostile_05_atomicity_removed": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/atomicity-removed.json"
    ),
    "hostile_06_success_failure_collapse": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/success-failure-collapse.json"
    ),
    "hostile_07_emitted_before_commit": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/emitted-before-commit.json"
    ),
    "hostile_08_continuation_mismatch": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/continuation-mismatch.json"
    ),
    "hostile_09_read_set_drift": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/read-set-drift.json"
    ),
    "hostile_10_output_contract_overclaim": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/output-contract-overclaim.json"
    ),
    "hostile_11_relation_owner_evidence_stale": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/relation-owner-evidence-stale.json"
    ),
    "hostile_12_relation_source_endpoint_mismatch": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/relation-source-endpoint-mismatch.json"
    ),
    "hostile_13_relation_target_endpoint_mismatch": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/relation-target-endpoint-mismatch.json"
    ),
    "hostile_14_materialized_without_exact_assertion": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/"
        "materialized-without-exact-assertion.json"
    ),
    "hostile_15_before_state_write_failure": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/before-state-write-failure.json"
    ),
    "hostile_16_between_state_and_outbox_failure": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/"
        "between-state-and-outbox-failure.json"
    ),
    "hostile_17_missing_member": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/missing-member.json"
    ),
    "hostile_18_mixed_commit": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/mixed-commit.json"
    ),
    "hostile_19_rollback_after_commit": (
        "projects/domainspec-v2/impl/architecture-conformance/families/"
        "state-changing-action/hostiles/rollback-after-commit.json"
    ),
}

SOURCE_CONTROL_ORDER = (
    ("py-op/undeclared-write", "RMT_OP_UNDECLARED_WRITE", "committed-success"),
    ("py-op/undeclared-effect", "RMT_OP_UNDECLARED_EFFECT", "committed-success"),
    ("py-op/guard-bypass", "RMT_OP_GUARD_BYPASS", "guard-rejected"),
    ("py-op/order-swap", "RMT_OP_ORDER_SWAP", "committed-success"),
    ("py-op/atomicity-removed", "RMT_OP_ATOMICITY_REMOVED", "committed-success"),
    (
        "py-op/success-failure-collapse",
        "RMT_OP_SUCCESS_FAILURE_COLLAPSE",
        "guard-rejected",
    ),
    (
        "py-op/emitted-before-commit",
        "RMT_OP_EMITTED_BEFORE_COMMIT",
        "committed-success",
    ),
    (
        "py-op/continuation-mismatch",
        "RMT_OP_CONTINUATION_MISMATCH",
        "committed-success",
    ),
    ("py-op/read-set-drift", "RMT_OP_READ_SET_DRIFT", "committed-success"),
    (
        "py-op/output-contract-overclaim",
        "RMT_OP_OUTPUT_CONTRACT_OVERCLAIM",
        "committed-success",
    ),
)


class PythonOperationProofError(Exception):
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
        raise PythonOperationProofError("PY_OP_INPUT_MISSING", relative)
    return target.read_bytes()


def read_json(root: Path, relative: str) -> dict[str, Any]:
    try:
        value = json.loads(read_bytes(root, relative))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PythonOperationProofError("PY_OP_JSON_INVALID", relative) from error
    if type(value) is not dict:
        raise PythonOperationProofError("PY_OP_JSON_INVALID", relative)
    return value


def document_digest(value: dict[str, Any], field: str) -> str:
    body = {key: child for key, child in value.items() if key != field}
    return sha256_bytes(canonical_json(body).encode("utf8"))


def validate_binding(root: Path) -> dict[str, Any]:
    binding = read_json(root, BINDING_PATH)
    if set(binding) != {
        "schema_version",
        "binding_id",
        "target_id",
        "protocol_id",
        "symbol_name",
        "observer_id",
        "observer_owner_ref",
        "proof_mechanism",
        "refs",
        "authority_effect",
        "binding_sha256",
    }:
        raise PythonOperationProofError("PY_OP_BINDING_SHAPE_INVALID")
    if (
        binding["schema_version"] != "PythonOperationBinding/v1"
        or binding["binding_id"]
        != "python.complete-settlement.bound-operation/v1"
        or binding["target_id"]
        != "operation.python.complete-settlement/v1"
        or binding["protocol_id"] != "python.bound-operation/v1"
        or binding["symbol_name"] != "complete_settlement_operation"
        or binding["observer_id"]
        != "observer.python-operation-ports/v1"
        or binding["observer_owner_ref"]
        != "python-operation-proof-harness"
        or binding["proof_mechanism"]
        != "ast-bytecode-audit-plus-two-fresh-processes-per-owner-case"
        or binding["authority_effect"] != "none"
        or type(binding["binding_sha256"]) is not str
        or document_digest(binding, "binding_sha256")
        != binding["binding_sha256"]
        or type(binding["refs"]) is not dict
        or set(binding["refs"]) != set(BOUND_PATHS)
    ):
        raise PythonOperationProofError("PY_OP_BINDING_POLICY_INVALID")
    for role, expected_path in BOUND_PATHS.items():
        reference = binding["refs"][role]
        if (
            type(reference) is not dict
            or set(reference) != {"path", "sha256"}
            or reference.get("path") != expected_path
            or type(reference.get("sha256")) is not str
            or sha256_bytes(read_bytes(root, expected_path))
            != reference["sha256"]
        ):
            raise PythonOperationProofError(
                "PY_OP_BINDING_INPUT_STALE",
                role,
            )
    return binding


def encode_payload(payload: dict[str, Any]) -> str:
    return base64.b64encode(
        canonical_json(payload).encode("utf8"),
    ).decode("ascii")


def payload_for(case_id: str) -> dict[str, Any]:
    committed = case_id == "committed-success"
    return {
        "case_id": case_id,
        "input": {
            "settlement_id": "settlement-001",
            "expected_state_version": 7 if committed else 6,
        },
        "current_state_version": 7,
        "fixtures": {
            "settlement.read.settlement-by-id": {
                "settlement_id": "settlement-001",
            },
            "settlement.read.payout-account": {
                "account_id": "account-001",
            },
        },
    }


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


def decode_observer_output(stdout: str, stderr: str, code: int) -> dict[str, Any]:
    if code != 0 or stderr:
        raise PythonOperationProofError(
            "PY_OP_OBSERVER_FAILED",
            stderr.strip() or str(code),
        )
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise PythonOperationProofError(
            "PY_OP_OBSERVER_OUTPUT_INVALID",
        ) from error
    if type(value) is not dict or type(value.get("pid")) is not int:
        raise PythonOperationProofError("PY_OP_OBSERVER_OUTPUT_INVALID")
    return value


def run_once(
    observer: Path,
    source: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    completed = subprocess.run(
        observer_command(observer, source, payload),
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
    return decode_observer_output(
        completed.stdout,
        completed.stderr,
        completed.returncode,
    )


def semantic_observation(value: dict[str, Any]) -> dict[str, Any]:
    return {key: child for key, child in value.items() if key != "pid"}


def run_pair(
    observer: Path,
    source: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    command = observer_command(observer, source, payload)
    processes = [
        subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf8",
            env={
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
        )
        for _ in range(2)
    ]
    observations: list[dict[str, Any]] = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=15)
        observations.append(decode_observer_output(
            stdout,
            stderr,
            process.returncode,
        ))
    first, second = observations
    if first["pid"] == second["pid"]:
        raise PythonOperationProofError("PY_OP_PROCESS_ISOLATION_FAILED")
    if canonical_json(semantic_observation(first)) != canonical_json(
        semantic_observation(second),
    ):
        raise PythonOperationProofError("PY_OP_PROCESS_REPLAY_MISMATCH")
    return first, second


def replace_exact(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise PythonOperationProofError("PY_OP_CONTROL_PATTERN_INVALID")
    return source.replace(old, new, 1)


def replace_last(source: str, old: str, new: str) -> str:
    index = source.rfind(old)
    if index < 0:
        raise PythonOperationProofError("PY_OP_CONTROL_PATTERN_INVALID")
    return source[:index] + new + source[index + len(old):]


def source_controls(source: str) -> dict[str, str]:
    second_write = '''        transaction["write"](
            "settlement.write.settlement-status",
            {
                "settlement_id": input_data["settlement_id"],
                "status": "committed",
            },
        )
'''
    extra_write = second_write + '''        transaction["write"](
            "settlement.write.audit-record",
            {"settlement_id": input_data["settlement_id"]},
        )
'''
    declared_effect = '''        ports["external_effect"](
            "event-store.append.PayoutCreated",
            {
                "event_type": "PayoutCreated",
                "settlement_id": input_data["settlement_id"],
                "payout_id": payout_id,
            },
        )
'''
    extra_effect = declared_effect + '''        ports["external_effect"](
            "event-store.append.AuditRecorded",
            {
                "event_type": "AuditRecorded",
                "settlement_id": input_data["settlement_id"],
                "payout_id": payout_id,
            },
        )
'''
    first_read = '''        settlement = ports["read"](
            "settlement.read.settlement-by-id",
            input_data["settlement_id"],
        )
'''
    second_read = '''        payout_account = ports["read"](
            "settlement.read.payout-account",
            input_data["settlement_id"],
        )
'''
    swapped = replace_exact(source, first_read, "__PY_OP_FIRST_READ__\n")
    swapped = replace_exact(swapped, second_read, first_read)
    swapped = replace_exact(swapped, "__PY_OP_FIRST_READ__\n", second_read)
    read_drift = replace_exact(
        source,
        second_read,
        second_read + '''        ports["read"](
            "settlement.read.audit-record",
            input_data["settlement_id"],
        )
''',
    )
    precommit_effect = '''        ports["external_effect"](
            "event-store.append.PayoutCreated",
            {
                "event_type": "PayoutCreated",
                "settlement_id": input_data["settlement_id"],
                "payout_id": payout_id,
            },
        )
        transaction["commit"]("all-or-nothing")
'''
    if '    if not guard["allowed"]:\n' in source:
        guard_bypass = replace_exact(
            source,
            '    if not guard["allowed"]:\n',
            "    if False:\n",
        )
    elif "    if False:\n" in source:
        guard_bypass = replace_exact(
            source,
            "    if False:\n",
            "    if 0:\n",
        )
    else:
        raise PythonOperationProofError("PY_OP_CONTROL_PATTERN_INVALID")
    values = {
        "py-op/undeclared-write": replace_exact(
            source,
            second_write,
            extra_write,
        ),
        "py-op/undeclared-effect": replace_exact(
            source,
            declared_effect,
            extra_effect,
        ),
        "py-op/guard-bypass": guard_bypass,
        "py-op/order-swap": swapped,
        "py-op/atomicity-removed": replace_exact(
            source,
            '        transaction["commit"]("all-or-nothing")\n',
            '        transaction["commit"]("best-effort")\n',
        ),
        "py-op/success-failure-collapse": replace_exact(
            source,
            '''            "value": None,
            "failure_code": "guard-rejected",
''',
            '''            "value": {
                "settlement_id": input_data["settlement_id"],
            },
            "failure_code": "guard-rejected",
''',
        ),
        "py-op/emitted-before-commit": replace_exact(
            source,
            '        transaction["commit"]("all-or-nothing")\n',
            precommit_effect,
        ),
        "py-op/continuation-mismatch": replace_last(
            source,
            '        "return-await-cancel-close-dispose-finalizer-quiescence",\n',
            '        "return-with-pending-effect",\n',
        ),
        "py-op/read-set-drift": read_drift,
        "py-op/output-contract-overclaim": replace_last(
            source,
            '        "exactly_once_distributed_delivery_claimed": False,\n',
            '        "exactly_once_distributed_delivery_claimed": True,\n',
        ),
    }
    if set(values) != {item[0] for item in SOURCE_CONTROL_ORDER}:
        raise PythonOperationProofError("PY_OP_CONTROL_CATALOGUE_INVALID")
    if any(value == source for value in values.values()):
        raise PythonOperationProofError("PY_OP_CONTROL_SOURCE_UNCHANGED")
    return values


def run_source_controls(
    observer: Path,
    source: str,
) -> list[dict[str, Any]]:
    mutants = source_controls(source)
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="domainspec-python-operation-") as tmp:
        root = Path(tmp)
        for index, (control_id, expected_code, case_id) in enumerate(
            SOURCE_CONTROL_ORDER,
            start=1,
        ):
            mutant = mutants[control_id]
            path = root / f"{index:02d}-{control_id.split('/')[-1]}.py"
            path.write_text(mutant, encoding="utf8", newline="\n")
            observed = semantic_observation(run_once(
                observer,
                path,
                payload_for(case_id),
            ))
            results.append({
                "control_id": control_id,
                "expected_code": expected_code,
                "case_id": case_id,
                "source_sha256": sha256_bytes(mutant.encode("utf8")),
                "observation": observed,
            })
    return results


def build_proof(root: Path) -> dict[str, Any]:
    binding = validate_binding(root)
    source_path = root / SOURCE_PATH
    observer = root / OBSERVER_PATH
    source = source_path.read_text(encoding="utf8")
    owner_cases: list[dict[str, Any]] = []
    process_pairs: list[dict[str, Any]] = []
    for case_id in ("committed-success", "guard-rejected"):
        first, second = run_pair(observer, source_path, payload_for(case_id))
        semantic = semantic_observation(first)
        owner_cases.append(semantic)
        process_pairs.append({
            "case_id": case_id,
            "first_pid": first["pid"],
            "second_pid": second["pid"],
            "semantic_sha256": sha256_bytes(
                canonical_json(semantic).encode("utf8"),
            ),
        })
    controls = run_source_controls(observer, source)
    return {
        "schema_version": "PythonOperationNativeProof/v1",
        "binding": {
            "binding_id": binding["binding_id"],
            "binding_sha256": binding["binding_sha256"],
        },
        "source_proof": owner_cases[0]["source_proof"],
        "owner_cases": owner_cases,
        "source_controls": controls,
        "process_evidence": {
            "owner_cases": 2,
            "fresh_processes": 4,
            "distinct_pid_pairs": 2,
            "process_pairs": process_pairs,
            "pids_redacted_from_semantic_observations": True,
        },
        "accounting": {
            "positives": {"declared": 2, "passed": 2},
            "source_controls": {"declared": 10, "executed": 10},
        },
        "claim_ceiling": (
            "one candidate-local Python bound Operation observed through an "
            "AST and bytecode audited injected-port harness in two fresh "
            "processes per owner case; not arbitrary Python, exactly-once "
            "delivery, cross-language parity, registry admission, publication, "
            "deployment, or production"
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
    except PythonOperationProofError as error:
        sys.stderr.write(str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
