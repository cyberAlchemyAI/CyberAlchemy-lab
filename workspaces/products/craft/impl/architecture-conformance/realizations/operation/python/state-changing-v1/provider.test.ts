import {readFile, readdir} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {getFactoryNodeProviderV1, listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {operationPythonV1Provider} from
  "../../../../factory/registry/providers/operation-python-v1.js";
import {
  canonicalOperationJson,
  sha256OperationBytes,
} from "../../../../families/state-changing-action/providers/decode-state-changing-action.js";
import {
  PYTHON_OPERATION_RAW_PATHS,
  PYTHON_OPERATION_SOURCE_CONTROLS,
  type PythonOperationRawInputs,
} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = process.cwd();
const candidateImplRoot = resolve(here, "../../../../..");

const readCandidateOrLive = async (path: string): Promise<string> => {
  if (path.startsWith("projects/domainspec-v2/impl/")) {
    const suffix = path.slice("projects/domainspec-v2/impl/".length);
    try {
      return await readFile(resolve(candidateImplRoot, suffix), "utf8");
    } catch {
      // The OP004 staged tree intentionally falls back to live OP002 inputs.
    }
  }
  return readFile(resolve(repositoryRoot, path), "utf8");
};

const readRawInputs = async (): Promise<PythonOperationRawInputs> =>
  Object.freeze(Object.fromEntries(await Promise.all(
    Object.entries(PYTHON_OPERATION_RAW_PATHS).map(
      async ([role, path]) => [
        role,
        await readCandidateOrLive(path),
      ] as const,
    ),
  ))) as PythonOperationRawInputs;

const rebindRole = (
  raw: PythonOperationRawInputs,
  role: Exclude<keyof PythonOperationRawInputs, "binding">,
  bytes: string,
): PythonOperationRawInputs => {
  const binding = JSON.parse(raw.binding) as {
    refs: Record<string, {sha256: string}>;
    binding_sha256: string;
  } & Record<string, unknown>;
  binding.refs[role]!.sha256 = sha256OperationBytes(bytes);
  const {binding_sha256: _digest, ...body} = binding;
  binding.binding_sha256 = sha256OperationBytes(
    canonicalOperationJson(body),
  );
  return Object.freeze({...raw, [role]: bytes,
    binding: JSON.stringify(binding)});
};

const rebindSource = (
  raw: PythonOperationRawInputs,
  source: string,
): PythonOperationRawInputs => rebindRole(raw, "source", source);

describe("Python Operation direct provider", () => {
  it("proves two owner cases, 10 native controls, and 19 family controls", async () => {
    const result = await operationPythonV1Provider.execute({
      raw_inputs: await readRawInputs(),
      upstream: {},
    });
    expect(result).toMatchObject({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "operation-python-v1",
      accounting: {
        positives_declared: 2,
        positives_passed: 2,
        mutants_declared: 29,
        mutants_killed: 29,
      },
      semantic_output: {
        workspace: {isolated: true, cleaned: true, symlinks: false},
        proof: {
          schema_version: "PythonOperationComposedProof/v1",
          target: {
            target_id: "operation.python.complete-settlement/v1",
            language: "python",
            protocol_id: "python.bound-operation/v1",
            symbol_name: "complete_settlement_operation",
          },
          native_process_evidence: {
            owner_cases: 2,
            fresh_processes: 4,
            distinct_pid_pairs: 2,
            pids_redacted_from_semantic_observations: true,
          },
          accounting: {
            positives: {declared: 2, passed: 2},
            native_source_controls: {declared: 10, killed: 10},
            family_controls: {declared: 19, killed: 19},
            mutants: {declared: 29, killed: 29},
          },
        },
      },
      authority_effect: "none",
    });
    const proof = (result.semantic_output as {
      proof: {
        source_controls: {
          control_id: string;
          source_sha256: string;
          finding_codes: string[];
        }[];
        family_controls: {finding_codes: string[]}[];
      };
    }).proof;
    expect(proof.source_controls.map(({control_id}) => control_id)).toEqual(
      PYTHON_OPERATION_SOURCE_CONTROLS.map(({control_id}) => control_id),
    );
    expect(new Set(proof.source_controls.map(({source_sha256}) =>
      source_sha256)).size).toBe(10);
    expect(proof.source_controls.every(({finding_codes}, index) =>
      finding_codes.includes(
        PYTHON_OPERATION_SOURCE_CONTROLS[index]!.expected_code,
      ))).toBe(true);
    expect(proof.family_controls).toHaveLength(19);
    expect(proof.family_controls.every(({finding_codes}) =>
      finding_codes.length === 1)).toBe(true);
    expect(result.claim_ceiling).toContain("not arbitrary Python");
    expect(result.claim_ceiling).toContain(
      "exactly-once distributed delivery",
    );
  }, 60_000);

  it("rejects an incoherent S1 residue through provider evaluation", async () => {
    const raw = await readRawInputs();
    const role = "hostile_15_before_state_write_failure" as const;
    const fixture = JSON.parse(raw[role]) as {
      mutation: Record<string, unknown>;
    };
    fixture.mutation.transaction_aborted = false;
    await expect(operationPythonV1Provider.execute({
      raw_inputs: rebindRole(raw, role, JSON.stringify(fixture)),
      upstream: {},
    })).rejects.toMatchObject({code: "RMT_OP_S1_RESIDUE_INCOHERENT"});
  });

  it("hash-closes every declared raw role and the binding body", async () => {
    const baseline = await readRawInputs();
    for (const role of Object.keys(PYTHON_OPERATION_RAW_PATHS).filter(
      (candidate) => candidate !== "binding",
    )) {
      await expect(operationPythonV1Provider.execute({
        raw_inputs: {
          ...baseline,
          [role]: `${baseline[
            role as keyof PythonOperationRawInputs
          ]}\n`,
        },
        upstream: {},
      })).rejects.toMatchObject({code: "PY_OP_BINDING_INPUT_STALE"});
    }
    const changedBinding = JSON.parse(baseline.binding) as {
      protocol_id: string;
    };
    changedBinding.protocol_id = "python.changed-operation/v1";
    await expect(operationPythonV1Provider.execute({
      raw_inputs: {...baseline, binding: JSON.stringify(changedBinding)},
      upstream: {},
    })).rejects.toMatchObject({code: "PY_OP_BINDING_POLICY_INVALID"});
  });

  it("rejects nested binding extras and exact-role drift", async () => {
    const raw = await readRawInputs();
    const nested = JSON.parse(raw.binding) as {
      refs: {source: Record<string, unknown>};
    };
    nested.refs.source.oracle_hint = "forbidden";
    await expect(operationPythonV1Provider.execute({
      raw_inputs: {...raw, binding: JSON.stringify(nested)},
      upstream: {},
    })).rejects.toMatchObject({code: "PY_OP_BINDING_REF_INVALID"});
    await expect(operationPythonV1Provider.execute({
      raw_inputs: {...raw, oracle_hint: "forbidden"},
      upstream: {},
    })).rejects.toMatchObject({code: "PY_OP_PROVIDER_INPUT_ROLES_INVALID"});
    const {source: _source, ...missing} = raw;
    await expect(operationPythonV1Provider.execute({
      raw_inputs: missing,
      upstream: {},
    })).rejects.toMatchObject({code: "PY_OP_PROVIDER_INPUT_ROLES_INVALID"});
  });

  it("derives guard-version evidence from the actual Python call", async () => {
    const raw = await readRawInputs();
    for (const replacement of [
      `{
        "settlement_id": input_data["settlement_id"],
        "expected_state_version": -1,
      }`,
      `{
        "settlement_id": input_data["settlement_id"],
      }`,
    ]) {
      const source = raw.source.replace(
        'ports["guard"]("rule.can-settle-payout", input_data)',
        `ports["guard"]("rule.can-settle-payout", ${replacement})`,
      );
      expect(source).not.toBe(raw.source);
      const error: unknown = await operationPythonV1Provider.execute({
        raw_inputs: rebindSource(raw, source),
        upstream: {},
      }).catch((failure: unknown) => failure);
      expect(error).toMatchObject({code: "PY_OP_TARGET_POSITIVE_BLOCKED"});
      expect(String(error)).toContain("RMT_OP_GUARD_BYPASS");
    }
  }, 60_000);

  it("rejects ignored guards and target input mutation", async () => {
    const raw = await readRawInputs();
    const ignored = raw.source.replace(
      '    if not guard["allowed"]:\n',
      "    if False:\n",
    );
    const ignoredError: unknown = await operationPythonV1Provider.execute({
      raw_inputs: rebindSource(raw, ignored),
      upstream: {},
    }).catch((error: unknown) => error);
    expect(ignoredError).toMatchObject({
      code: "PY_OP_TARGET_POSITIVE_BLOCKED",
    });
    expect(String(ignoredError)).toContain("RMT_OP_GUARD_BYPASS");

    const mutatesInput = raw.source.replace(
      '    guard = ports["guard"]("rule.can-settle-payout", input_data)\n',
      '    input_data["expected_state_version"] = -1\n' +
      '    guard = ports["guard"]("rule.can-settle-payout", input_data)\n',
    );
    await expect(operationPythonV1Provider.execute({
      raw_inputs: rebindSource(raw, mutatesInput),
      upstream: {},
    })).rejects.toMatchObject({
      code: "FACTORY_PYTHON_OPERATION_PROVIDER_FAILED",
    });

    const dynamicPort = raw.source.replace(
      'ports["guard"]',
      'ports["gu" + "ard"]',
    );
    await expect(operationPythonV1Provider.execute({
      raw_inputs: rebindSource(raw, dynamicPort),
      upstream: {},
    })).rejects.toMatchObject({
      code: "FACTORY_PYTHON_OPERATION_PROVIDER_FAILED",
    });
  }, 60_000);

  it("snapshots all raw inputs before the first asynchronous edge", async () => {
    const baseline = await readRawInputs();
    const mutable = {...baseline};
    const pending = operationPythonV1Provider.execute({
      raw_inputs: mutable,
      upstream: {},
    });
    mutable.source = `${mutable.source}\n`;
    await expect(pending).resolves.toMatchObject({
      result: "pass",
      provider_id: "operation-python-v1",
    });
  }, 60_000);

  it("remains unregistered", () => {
    const ids = listFactoryNodeProvidersV1().map(
      ({provider_id: providerId}) => providerId,
    );
    expect(ids).not.toContain("operation-python-v1");
    expect(() => getFactoryNodeProviderV1(
      "operation-python-v1",
    )).toThrow("FACTORY_PROVIDER_UNKNOWN:operation-python-v1");
  });

  it("leaves no Python bytecode in the candidate material paths", async () => {
    const realizationEntries = await readdir(here, {
      recursive: true,
      withFileTypes: true,
    });
    expect(realizationEntries.some((entry) =>
      entry.name === "__pycache__" || /\.py[co]$/u.test(entry.name),
    )).toBe(false);
    const targetDirectory = resolve(
      candidateImplRoot,
      "architecture-conformance/targets/python/remaining_types",
    );
    const targetEntries = await readdir(targetDirectory, {
      withFileTypes: true,
    });
    expect(targetEntries.some((entry) =>
      /^operation_v1.*\.py[co]$/u.test(entry.name),
    )).toBe(false);
  });
});
