import {readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {beforeAll, describe, expect, it} from "vitest";

import {operationPythonV1Provider} from
  "../../../../factory/registry/providers/operation-python-v1.js";
import {operationRustV1Provider} from
  "../../../../factory/registry/providers/operation-rust-v1.js";
import {operationTypeScriptV1Provider} from
  "../../../../factory/registry/providers/operation-typescript-v1.js";
import {PYTHON_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/python/state-changing-v1/index.js";
import {RUST_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/rust/state-changing-v1/index.js";
import {TYPESCRIPT_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/typescript/state-changing-v1/index.js";
import {sha256OperationValue} from
  "../../../../families/state-changing-action/providers/decode-state-changing-action.js";
import {evaluateOperationParity} from "./evaluate-operation-parity.js";

type JsonObject = Record<string, any>;
const repositoryRoot = process.cwd();

const readRaw = async (
  paths: Readonly<Record<string, string>>,
): Promise<Readonly<Record<string, string>>> => Object.freeze(
  Object.fromEntries(await Promise.all(Object.entries(paths).map(
    async ([role, path]) => [
      role,
      await readFile(resolve(repositoryRoot, path), "utf8"),
    ],
  ))),
);
const clone = <T>(value: T): T => structuredClone(value);
let exactInput: JsonObject;

beforeAll(async () => {
  const typescript = await operationTypeScriptV1Provider.execute({
    raw_inputs: await readRaw(TYPESCRIPT_OPERATION_RAW_PATHS),
    upstream: {},
  });
  const python = await operationPythonV1Provider.execute({
    raw_inputs: await readRaw(PYTHON_OPERATION_RAW_PATHS),
    upstream: {},
  });
  const rust = await operationRustV1Provider.execute({
    raw_inputs: await readRaw(RUST_OPERATION_RAW_PATHS),
    upstream: {},
  });
  exactInput = {
    typescript: {
      provider_id: operationTypeScriptV1Provider.provider_id,
      result: typescript,
    },
    python: {
      provider_id: operationPythonV1Provider.provider_id,
      result: python,
    },
    rust: {
      provider_id: operationRustV1Provider.provider_id,
      result: rust,
    },
  };
}, 120_000);

describe("Operation TypeScript, Python, and Rust semantic parity", () => {
  it("joins portable obligations from the three exact direct providers", () => {
    const result = evaluateOperationParity(exactInput);
    expect(result).toMatchObject({
      schema_version: "OperationSemanticParity/v1",
      result: "pass",
      providers: [
        "operation-typescript-v1",
        "operation-python-v1",
        "operation-rust-v1",
      ],
      native_hash_byte_comparison: false,
      native_source_hashes_all_distinct: true,
      authority_effect: "none",
    });
    expect(result.diagnostics).toEqual([]);
    expect(result.portable_projection.observations).toHaveLength(2);
    expect(result.portable_projection.source_obligations).toHaveLength(10);
    expect(result.portable_projection.family_controls).toHaveLength(19);
    expect(result.parity_sha256).toMatch(/^[a-f0-9]{64}$/u);
  });

  it("does not require cross-language native source hashes to match", () => {
    const result = evaluateOperationParity(exactInput);
    expect(result.result).toBe("pass");
    expect(result.native_hash_byte_comparison).toBe(false);
    expect(result.native_source_hashes_all_distinct).toBe(true);
    expect(new Set(Object.values(result.native_evidence).map((native) =>
      (native.target as JsonObject).source_sha256)).size).toBe(3);
  });

  it.each(["typescript", "python", "rust"] as const)(
    "blocks rehashed %s portable observation drift",
    (language) => {
      const changed = clone(exactInput);
      const observation = changed[language].result.semantic_output.proof
        .observations[0];
      observation.read_attempts = [...observation.read_attempts].reverse();
      const {observation_sha256: _digest, ...body} = observation;
      observation.observation_sha256 = sha256OperationValue(body);
      const result = evaluateOperationParity(changed);
      expect(result.result).toBe("block");
      const expectedMismatches = language === "typescript"
        ? ["python", "rust"] : [language];
      for (const mismatch of expectedMismatches) {
        expect(result.diagnostics).toContain(
          `RMT_OP_PARITY_OBSERVATION_MISMATCH:${mismatch}`,
        );
      }
    },
  );

  it("rejects provider substitution, omission, and surplus", () => {
    const substituted = clone(exactInput);
    substituted.python.provider_id = "operation-rust-v1";
    expect(() => evaluateOperationParity(substituted))
      .toThrow("RMT_OP_PARITY_PROVIDER_ID_INVALID:python");

    const missing = clone(exactInput);
    delete missing.rust;
    expect(() => evaluateOperationParity(missing))
      .toThrow("RMT_OP_PARITY_PROVIDER_SET_INVALID");

    expect(() => evaluateOperationParity({
      ...exactInput,
      synthetic: exactInput.rust,
    })).toThrow("RMT_OP_PARITY_PROVIDER_SET_INVALID");
  });

  it("rejects fabricated or stale provider evidence", () => {
    const fabricated = clone(exactInput);
    fabricated.python.result.result = "block";
    expect(() => evaluateOperationParity(fabricated))
      .toThrow("RMT_OP_PARITY_PROVIDER_RESULT_INVALID:python");

    const stale = clone(exactInput);
    stale.typescript.result.semantic_output.proof.observations[0]
      .operation_id = "fabricated-operation";
    expect(() => evaluateOperationParity(stale))
      .toThrow("RMT_OP_PARITY_OBSERVATION_DIGEST_STALE");
  });

  it("rejects rehashed native fields inside the portable projection", () => {
    const changed = clone(exactInput);
    const observation = changed.typescript.result.semantic_output.proof
      .observations[0];
    observation.inputs.native_pid = 42;
    const {observation_sha256: _digest, ...body} = observation;
    observation.observation_sha256 = sha256OperationValue(body);
    expect(() => evaluateOperationParity(changed))
      .toThrow("RMT_OP_PARITY_OBSERVATION_INVALID");
  });

  it("rejects proof identity, binding, accounting, and authority inflation", () => {
    const proofIdentity = clone(exactInput);
    proofIdentity.python.result.semantic_output.proof.schema_version =
      "FabricatedProof/v1";
    expect(() => evaluateOperationParity(proofIdentity))
      .toThrow("RMT_OP_PARITY_PROVIDER_PROOF_INVALID:python");

    const binding = clone(exactInput);
    binding.rust.result.semantic_output.proof.binding.bound_role_count = 28;
    expect(() => evaluateOperationParity(binding))
      .toThrow("RMT_OP_PARITY_TARGET_INVALID:rust");

    const accounting = clone(exactInput);
    accounting.typescript.result.accounting.mutants_killed = 30;
    expect(() => evaluateOperationParity(accounting))
      .toThrow("RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID:typescript");

    const authority = clone(exactInput);
    authority.python.result.authority_effect = "promote";
    expect(() => evaluateOperationParity(authority))
      .toThrow("RMT_OP_PARITY_PROVIDER_RESULT_INVALID:python");
  });

  it("rejects missing relations and non-singleton family findings", () => {
    const relation = clone(exactInput);
    const observation = relation.rust.result.semantic_output.proof
      .observations[0];
    observation.relation_assertions.pop();
    const {observation_sha256: _digest, ...body} = observation;
    observation.observation_sha256 = sha256OperationValue(body);
    expect(() => evaluateOperationParity(relation))
      .toThrow("RMT_OP_PARITY_OBSERVATION_INVALID");

    const family = clone(exactInput);
    family.typescript.result.semantic_output.proof.family_controls[0]
      .finding_codes.push("RMT_OP_GUARD_BYPASS");
    expect(() => evaluateOperationParity(family))
      .toThrow("RMT_OP_PARITY_FAMILY_CONTROLS_INVALID:typescript");
  });

  it("rejects stale native, binding, process, and source-control evidence", () => {
    const pythonBinding = clone(exactInput);
    pythonBinding.python.result.semantic_output.proof.binding.binding_sha256 =
      "e".repeat(64);
    expect(() => evaluateOperationParity(pythonBinding))
      .toThrow("RMT_OP_PARITY_PROVIDER_EVIDENCE_STALE:python");

    const rustProvider = clone(exactInput);
    rustProvider.rust.result.semantic_output.proof.binding.provider_sha256 =
      "e".repeat(64);
    expect(() => evaluateOperationParity(rustProvider))
      .toThrow("RMT_OP_PARITY_PROVIDER_EVIDENCE_STALE:rust");

    const target = clone(exactInput);
    target.typescript.result.semantic_output.proof.target.source_sha256 =
      "e".repeat(64);
    target.typescript.result.semantic_output.proof.closed_subset_proof
      .source_sha256 = "e".repeat(64);
    expect(() => evaluateOperationParity(target))
      .toThrow("RMT_OP_PARITY_PROVIDER_EVIDENCE_STALE:typescript");

    const process = clone(exactInput);
    process.python.result.semantic_output.proof.native_process_evidence
      .process_pairs[0].semantic_sha256 = "e".repeat(64);
    expect(() => evaluateOperationParity(process))
      .toThrow("RMT_OP_PARITY_PROVIDER_EVIDENCE_STALE:python");

    const sourceControl = clone(exactInput);
    sourceControl.rust.result.semantic_output.proof.source_controls[0]
      .source_sha256 = "e".repeat(64);
    expect(() => evaluateOperationParity(sourceControl))
      .toThrow("RMT_OP_PARITY_PROVIDER_EVIDENCE_STALE:rust");
  });

  it("rejects invalid PIDs and Rust cross-pair PID reuse", () => {
    const invalid = clone(exactInput);
    invalid.python.result.semantic_output.proof.native_process_evidence
      .process_pairs[0].first_pid = -1;
    expect(() => evaluateOperationParity(invalid))
      .toThrow("RMT_OP_PARITY_NATIVE_PROOF_INVALID:python");

    const reused = clone(exactInput);
    const pairs = reused.rust.result.semantic_output.proof.runtime_proof
      .process_pairs;
    pairs[1].first_pid = pairs[0].first_pid;
    expect(() => evaluateOperationParity(reused))
      .toThrow("RMT_OP_PARITY_NATIVE_PROOF_INVALID:rust");
  });

  it("binds native observer and observation identities per language", () => {
    const observer = clone(exactInput);
    const observerObservation = observer.python.result.semantic_output.proof
      .observations[0];
    observerObservation.observer.observer_id = "observer.fabricated/v1";
    const {observation_sha256: _observerDigest, ...observerBody} =
      observerObservation;
    observerObservation.observation_sha256 = sha256OperationValue(observerBody);
    expect(() => evaluateOperationParity(observer))
      .toThrow("RMT_OP_PARITY_OBSERVATION_INVALID");

    const identity = clone(exactInput);
    const identityObservation = identity.rust.result.semantic_output.proof
      .observations[0];
    identityObservation.observation_id = "";
    const {observation_sha256: _identityDigest, ...identityBody} =
      identityObservation;
    identityObservation.observation_sha256 = sha256OperationValue(identityBody);
    expect(() => evaluateOperationParity(identity))
      .toThrow("RMT_OP_PARITY_OBSERVATION_INVALID");
  });

  it("rejects family-control and source-obligation inflation", () => {
    const family = clone(exactInput);
    family.python.result.semantic_output.proof.family_controls.pop();
    expect(() => evaluateOperationParity(family))
      .toThrow("RMT_OP_PARITY_FAMILY_CONTROLS_INVALID:python");

    const source = clone(exactInput);
    source.rust.result.semantic_output.proof.source_controls[0]
      .finding_codes = [];
    expect(() => evaluateOperationParity(source))
      .toThrow("RMT_OP_PARITY_SOURCE_CONTROLS_INVALID:rust");
  });

  it("keeps native evidence out of the portable projection", () => {
    const result = evaluateOperationParity(exactInput);
    const portable = JSON.stringify(result.portable_projection);
    for (const nativeField of [
      "source_sha256", "binding_sha256", "observer_id", "observation_id",
      "first_pid",
      "workspace", "control_id", "native_process_evidence",
      "fresh_processes",
    ]) {
      expect(portable).not.toContain(nativeField);
    }
    expect(JSON.stringify(result.native_evidence)).toContain("source_sha256");
    expect(result.native_evidence.typescript.runtime_proof).not.toBeNull();
    expect(result.native_evidence.typescript.observation_identities)
      .toHaveLength(2);
    expect((result.native_evidence.typescript
      .observation_identities as JsonObject[]).every((identity) =>
      /^[a-f0-9]{64}$/u.test(String(identity.observation_sha256)))).toBe(true);
    expect(result.native_evidence.python.native_process_evidence)
      .toMatchObject({
        owner_cases: 2,
        fresh_processes: 4,
        distinct_pid_pairs: 2,
      });
    expect(result.native_evidence.rust.runtime_proof).not.toBeNull();
    expect(result.claim_ceiling).toContain("native evidence remains separate");
  });
});
