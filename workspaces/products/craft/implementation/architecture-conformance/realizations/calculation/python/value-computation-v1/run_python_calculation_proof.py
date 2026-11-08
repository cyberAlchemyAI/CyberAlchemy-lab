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
    "value-computation/fixtures/net-settlement/definition.json"
)
DENOMINATOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/"
    "value-computation/fixtures/net-settlement/denominator.json"
)
MUTATIONS_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/families/"
    "value-computation/fixtures/net-settlement/mutants.json"
)
DESCRIPTOR_PATH = (
    "projects/domainspec-v2/development/remaining-meta-types/admissions/"
    "calculation/cross-language-realization-descriptor.json"
)
SOURCE_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/"
    "remaining_types/calculation_v1.py"
)
OBSERVER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "calculation/python/value-computation-v1/observe_python_calculation_case.py"
)
SUPERVISOR_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "calculation/python/value-computation-v1/run_python_calculation_proof.py"
)
PROOF_BUILDER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "calculation/python/value-computation-v1/index.ts"
)
PROVIDER_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/"
    "providers/python-calculation-v1.ts"
)
BINDING_PATH = (
    "projects/domainspec-v2/impl/architecture-conformance/realizations/"
    "calculation/python/value-computation-v1/python-binding.json"
)
EFFECT_CHANNELS = (
    "clock",
    "random",
    "environment",
    "filesystem",
    "network",
    "process",
    "global-cache",
    "delayed-lazy",
    "callback",
    "iterator-future",
    "finalizer-drop",
    "mutable-output",
)


class PythonCalculationProofError(Exception):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_bytes(root: Path, relative: str) -> bytes:
    target = root / relative
    if not target.is_file() or target.is_symlink():
        raise PythonCalculationProofError("PY_CALC_INPUT_MISSING", relative)
    return target.read_bytes()


def document_digest(value: dict[str, Any], field: str) -> str:
    body = {key: child for key, child in value.items() if key != field}
    return sha256_bytes(canonical_json(body).encode("utf8"))


def expect_ref(
    root: Path,
    binding: dict[str, Any],
    field: str,
    expected_path: str,
) -> dict[str, str]:
    value = binding.get(field)
    if (
        not isinstance(value, dict)
        or set(value) != {"path", "sha256"}
        or value.get("path") != expected_path
        or not isinstance(value.get("sha256"), str)
    ):
        raise PythonCalculationProofError("PY_CALC_BINDING_REF_INVALID", field)
    observed = sha256_bytes(read_bytes(root, expected_path))
    if observed != value["sha256"]:
        raise PythonCalculationProofError("PY_CALC_BINDING_INPUT_STALE", field)
    return value


def encode_case(case_id: str, inputs: dict[str, Any]) -> str:
    value = {
        "case_id": case_id,
        "gross_amount_minor": inputs.get("gross_amount_minor"),
        "fee_amount_minor": inputs.get("fee_amount_minor"),
    }
    return base64.b64encode(canonical_json(value).encode("utf8")).decode("ascii")


def observer_command(
    observer: Path,
    source: Path,
    encoded_case: str,
) -> list[str]:
    return [
        sys.executable,
        "-I",
        "-B",
        str(observer),
        "--source",
        str(source),
        "--case-base64",
        encoded_case,
    ]


def run_pair(
    observer: Path,
    source: Path,
    case_id: str,
    inputs: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    encoded = encode_case(case_id, inputs)
    command = observer_command(observer, source, encoded)
    environment = {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}
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
    decoded: list[dict[str, Any]] = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=15)
        if process.returncode != 0 or stderr:
            raise PythonCalculationProofError(
                "PY_CALC_OBSERVER_FAILED",
                stderr.strip() or str(process.returncode),
            )
        try:
            value = json.loads(stdout)
        except json.JSONDecodeError as error:
            raise PythonCalculationProofError("PY_CALC_OBSERVER_OUTPUT_INVALID") from error
        if not isinstance(value, dict):
            raise PythonCalculationProofError("PY_CALC_OBSERVER_OUTPUT_INVALID")
        decoded.append(value)
    first, second = decoded
    if (
        type(first.get("pid")) is not int
        or type(second.get("pid")) is not int
        or first["pid"] == second["pid"]
    ):
        raise PythonCalculationProofError("PY_CALC_PROCESS_ISOLATION_FAILED")
    return first, second


def hostile_sources() -> dict[str, str]:
    prefix = ""
    return {
        "clock": prefix + "import time\n\ndef calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> int:\n    return gross_amount_minor - int(time.time())\n",
        "random": prefix + "import random\n\ndef calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> int:\n    return gross_amount_minor - random.randint(0, fee_amount_minor)\n",
        "environment": prefix + "import os\n\ndef calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> int:\n    return gross_amount_minor - int(os.environ.get('FEE', fee_amount_minor))\n",
        "filesystem": prefix + "def calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> int:\n    open('/tmp/domainspec-calculation', 'w').write('x')\n    return gross_amount_minor - fee_amount_minor\n",
        "network": prefix + "import socket\n\ndef calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> int:\n    socket.socket()\n    return gross_amount_minor - fee_amount_minor\n",
        "process": prefix + "import subprocess\n\ndef calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> int:\n    subprocess.run(['true'])\n    return gross_amount_minor - fee_amount_minor\n",
        "global-cache": prefix + "CACHE = 0\n\ndef calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> int:\n    global CACHE\n    CACHE += 1\n    return gross_amount_minor - fee_amount_minor\n",
        "delayed-lazy": prefix + "async def calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> int:\n    return gross_amount_minor - fee_amount_minor\n",
        "callback": prefix + "def calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int, callback) -> int:\n    callback(gross_amount_minor)\n    return gross_amount_minor - fee_amount_minor\n",
        "iterator-future": prefix + "def calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> int:\n    yield gross_amount_minor - fee_amount_minor\n",
        "finalizer-drop": prefix + "class Dropper:\n    def __del__(self):\n        pass\n\ndef calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> int:\n    return gross_amount_minor - fee_amount_minor\n",
        "mutable-output": prefix + "def calculate_net_settlement(gross_amount_minor: int, fee_amount_minor: int) -> list[int]:\n    return [gross_amount_minor - fee_amount_minor]\n",
    }


def execute_hostile_probes(observer: Path) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    encoded = encode_case(
        "native-hostile",
        {"gross_amount_minor": 10, "fee_amount_minor": 1},
    )
    with tempfile.TemporaryDirectory(prefix="domainspec-python-calc-hostiles-") as raw:
        root = Path(raw)
        for index, channel in enumerate(EFFECT_CHANNELS):
            source = root / f"{index:02d}-{channel}.py"
            source.write_text(hostile_sources()[channel], encoding="utf8", newline="\n")
            completed = subprocess.run(
                observer_command(observer, source, encoded),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf8",
                env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"},
                timeout=15,
                check=False,
            )
            error_code = completed.stderr.strip().split(":", 1)[0]
            if (
                completed.returncode != 2
                or completed.stdout
                or not error_code.startswith("PY_CALC_CLOSED_SUBSET_")
            ):
                raise PythonCalculationProofError(
                    "PY_CALC_HOSTILE_SURVIVED",
                    channel,
                )
            results.append({
                "channel": channel,
                "status": "killed",
                "error_code": error_code,
            })
    return results


def build_proof(repository_root: Path) -> dict[str, Any]:
    try:
        binding = json.loads(read_bytes(repository_root, BINDING_PATH))
    except json.JSONDecodeError as error:
        raise PythonCalculationProofError("PY_CALC_BINDING_JSON_INVALID") from error
    if (
        not isinstance(binding, dict)
        or binding.get("schema_version") != "PythonCalculationBinding/v1"
        or binding.get("binding_id") != "python.net-settlement.bound-calculation/v1"
        or binding.get("target_id") != "calculation.python.net-settlement/v1"
        or binding.get("protocol_id") != "python.bound-calculation/v1"
        or binding.get("observer_id") != "observer.python-calculation-closed-subset/v1"
        or binding.get("observer_owner_ref") != "python-calculation-proof-harness"
        or binding.get("symbol_name") != "calculate_net_settlement"
        or binding.get("authority_effect") != "none"
        or document_digest(binding, "binding_sha256") != binding.get("binding_sha256")
    ):
        raise PythonCalculationProofError("PY_CALC_BINDING_INVALID")
    refs = {
        "definition_ref": DEFINITION_PATH,
        "denominator_ref": DENOMINATOR_PATH,
        "mutation_catalogue_ref": MUTATIONS_PATH,
        "descriptor_ref": DESCRIPTOR_PATH,
        "source_ref": SOURCE_PATH,
        "observer_ref": OBSERVER_PATH,
        "supervisor_ref": SUPERVISOR_PATH,
        "proof_builder_ref": PROOF_BUILDER_PATH,
        "provider_ref": PROVIDER_PATH,
    }
    resolved = {
        field: expect_ref(repository_root, binding, field, path)
        for field, path in refs.items()
    }
    try:
        definition = json.loads(read_bytes(repository_root, DEFINITION_PATH))
    except json.JSONDecodeError as error:
        raise PythonCalculationProofError("PY_CALC_DEFINITION_JSON_INVALID") from error
    cases = definition.get("cases") if isinstance(definition, dict) else None
    if not isinstance(cases, list) or len(cases) != 4:
        raise PythonCalculationProofError("PY_CALC_DEFINITION_CASES_INVALID")
    observer = repository_root / OBSERVER_PATH
    source = repository_root / SOURCE_PATH
    observations: list[dict[str, Any]] = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("inputs"), dict):
            raise PythonCalculationProofError("PY_CALC_DEFINITION_CASES_INVALID")
        case_id = case.get("case_id")
        if not isinstance(case_id, str):
            raise PythonCalculationProofError("PY_CALC_DEFINITION_CASES_INVALID")
        first, second = run_pair(observer, source, case_id, case["inputs"])
        if (
            first.get("case_id") != case_id
            or second.get("case_id") != case_id
            or first.get("source_sha256") != resolved["source_ref"]["sha256"]
            or second.get("source_sha256") != resolved["source_ref"]["sha256"]
            or first.get("result_value") != second.get("result_value")
            or first.get("result_sha256") != second.get("result_sha256")
            or first.get("audit_events") != []
            or second.get("audit_events") != []
        ):
            raise PythonCalculationProofError("PY_CALC_CASE_PROOF_INVALID", case_id)
        observations.append({
            "case_id": case_id,
            "inputs": case["inputs"],
            "first": first,
            "second": second,
        })
    hostiles = execute_hostile_probes(observer)
    return {
        "schema_version": "PythonCalculationNativeProof/v1",
        "result": "pass",
        "target": {
            "target_id": binding["target_id"],
            "language": "python",
            "protocol_id": binding["protocol_id"],
        },
        "binding": {
            "binding_id": binding["binding_id"],
            "binding_sha256": binding["binding_sha256"],
            "descriptor_sha256": resolved["descriptor_ref"]["sha256"],
            "provider_sha256": resolved["provider_ref"]["sha256"],
            "observer_sha256": resolved["observer_ref"]["sha256"],
            "supervisor_sha256": resolved["supervisor_ref"]["sha256"],
            "proof_builder_sha256": resolved["proof_builder_ref"]["sha256"],
        },
        "source_ref": resolved["source_ref"],
        "closed_subset": {
            "ast": "exact-two-int-parameters-one-subtraction",
            "bytecode": "RESUME-LOAD_FAST-LOAD_FAST-BINARY_OP_SUBTRACT-RETURN_VALUE",
            "runtime_guard": "exact-int-not-bool-plus-python-audit-hook",
            "supported_effect_channels": list(EFFECT_CHANNELS),
        },
        "cases": observations,
        "runtime_proof": {
            "cases_executed": len(observations),
            "fresh_processes_executed": len(observations) * 2,
            "distinct_pid_pairs": len(observations),
            "result_kind": "primitive-number",
            "quiescence_basis": "closed-subset-plus-successful-child-exit",
        },
        "hostile_probes": hostiles,
        "hostile_accounting": {
            "declared": len(EFFECT_CHANNELS),
            "killed": len(hostiles),
        },
        "authority_effect": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    sys.dont_write_bytecode = True
    try:
        proof = build_proof(Path(arguments.repository_root).resolve())
        Path(arguments.output).write_text(
            f"{json.dumps(proof, indent=2, sort_keys=True)}\n",
            encoding="utf8",
            newline="\n",
        )
        return 0
    except PythonCalculationProofError as error:
        sys.stderr.write(f"{error}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
