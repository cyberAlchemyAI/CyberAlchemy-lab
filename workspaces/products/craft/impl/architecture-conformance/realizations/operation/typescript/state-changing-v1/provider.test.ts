import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {getFactoryNodeProviderV1, listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {operationTypeScriptV1Provider} from
  "../../../../factory/registry/providers/operation-typescript-v1.js";
import {typeScriptOperationV1Provider as legacyTypeScriptOperationV1Provider}
  from "../../../../factory/registry/providers/typescript-operation-v1.js";
import {
  canonicalOperationJson,
  sha256OperationBytes,
} from "../../../../families/state-changing-action/providers/decode-state-changing-action.js";
import {
  inspectTypeScriptOperationClosedSubset,
  TYPESCRIPT_OPERATION_SOURCE_CONTROLS,
} from "./closed-subset.js";
import {
  TYPESCRIPT_OPERATION_RAW_PATHS,
  type TypeScriptOperationRawInputs,
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
      // The OP003 staged tree intentionally falls back to live OP002 inputs.
    }
  }
  return readFile(resolve(repositoryRoot, path), "utf8");
};

const readRawInputs = async (): Promise<TypeScriptOperationRawInputs> =>
  Object.freeze(Object.fromEntries(await Promise.all(
    Object.entries(TYPESCRIPT_OPERATION_RAW_PATHS).map(
      async ([role, path]) => [
        role,
        await readCandidateOrLive(path),
      ] as const,
    ),
  ))) as TypeScriptOperationRawInputs;

const rebindRole = (
  raw: TypeScriptOperationRawInputs,
  role: Exclude<keyof TypeScriptOperationRawInputs, "binding">,
  bytes: string,
): TypeScriptOperationRawInputs => {
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
  raw: TypeScriptOperationRawInputs,
  source: string,
): TypeScriptOperationRawInputs => rebindRole(raw, "source", source);

describe("TypeScript Operation direct provider", () => {
  it("proves both owner cases, 10 source controls, and 19 family controls", async () => {
    const result = await operationTypeScriptV1Provider.execute({
      raw_inputs: await readRawInputs(),
      upstream: {},
    });
    expect(result).toMatchObject({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "operation-typescript-v1",
      accounting: {
        positives_declared: 2,
        positives_passed: 2,
        mutants_declared: 29,
        mutants_killed: 29,
      },
      semantic_output: {
        proof: {
          schema_version: "TypeScriptOperationComposedProof/v1",
          result: "pass",
          target: {
            target_id: "operation.typescript.complete-settlement/v1",
            protocol_id: "typescript.bound-operation/v1",
            language: "typescript",
            symbol_name: "completeSettlementOperation",
          },
          runtime_proof: {
            owner_cases: 2,
            fresh_processes: 4,
            distinct_pid_pairs: 2,
            observer_origin: "independent-injected-port-harness",
          },
          accounting: {
            positives: {declared: 2, passed: 2},
            target_source_controls: {declared: 10, killed: 10},
            family_controls: {declared: 19, killed: 19},
            mutants: {declared: 29, killed: 29},
          },
        },
      },
      authority_effect: "none",
    });
    const proof = (result.semantic_output as {
      proof: {
        source_controls: {control_id: string; source_sha256: string}[];
        family_controls: {hostile_id: string; finding_codes: string[]}[];
        observations: {case_id: string}[];
      };
    }).proof;
    expect(proof.source_controls.map(({control_id}) => control_id)).toEqual(
      TYPESCRIPT_OPERATION_SOURCE_CONTROLS.map(({control_id}) => control_id),
    );
    expect(new Set(proof.source_controls.map(({source_sha256}) =>
      source_sha256)).size).toBe(10);
    expect(proof.family_controls).toHaveLength(19);
    expect(proof.family_controls.every(({finding_codes}) =>
      finding_codes.length === 1)).toBe(true);
    expect(proof.observations.map(({case_id}) => case_id)).toEqual([
      "committed-success",
      "guard-rejected",
    ]);
    expect(result.claim_ceiling).toContain(
      "not arbitrary TypeScript",
    );
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
    await expect(operationTypeScriptV1Provider.execute({
      raw_inputs: rebindRole(raw, role, JSON.stringify(fixture)),
      upstream: {},
    })).rejects.toMatchObject({code: "RMT_OP_S1_RESIDUE_INCOHERENT"});
  });

  it("hash-closes every declared raw input and the binding body", async () => {
    const baseline = await readRawInputs();
    for (const role of Object.keys(TYPESCRIPT_OPERATION_RAW_PATHS).filter(
      (candidate) => candidate !== "binding",
    )) {
      const mutated = {...baseline, [role]: `${baseline[
        role as keyof TypeScriptOperationRawInputs
      ]}\n`};
      await expect(operationTypeScriptV1Provider.execute({
        raw_inputs: mutated,
        upstream: {},
      })).rejects.toMatchObject({
        code: "TS_OP_BINDING_INPUT_STALE",
      });
    }

    const changedBinding = JSON.parse(baseline.binding) as {
      binding_id: string;
    };
    changedBinding.binding_id = "typescript.changed.bound-operation/v1";
    await expect(operationTypeScriptV1Provider.execute({
      raw_inputs: {...baseline, binding: JSON.stringify(changedBinding)},
      upstream: {},
    })).rejects.toMatchObject({code: "TS_OP_BINDING_POLICY_INVALID"});
  });

  it("rejects nested binding extras and wrong observer identity", async () => {
    const raw = await readRawInputs();
    const nested = JSON.parse(raw.binding) as {
      refs: {source: Record<string, unknown>};
    };
    nested.refs.source.oracle_hint = "forbidden";
    await expect(operationTypeScriptV1Provider.execute({
      raw_inputs: {...raw, binding: JSON.stringify(nested)},
      upstream: {},
    })).rejects.toMatchObject({code: "TS_OP_BINDING_REF_INVALID"});

    const wrongObserver = JSON.parse(raw.binding) as {
      observer_id: string;
    };
    wrongObserver.observer_id = "observer.untrusted/v1";
    await expect(operationTypeScriptV1Provider.execute({
      raw_inputs: {...raw, binding: JSON.stringify(wrongObserver)},
      upstream: {},
    })).rejects.toMatchObject({code: "TS_OP_BINDING_POLICY_INVALID"});
  });

  it("derives guard-version evidence from the target's actual call", async () => {
    const raw = await readRawInputs();
    const source = raw.source.replace(
      'await ports.guard("rule.can-settle-payout", input)',
      `await ports.guard("rule.can-settle-payout", {
    settlement_id: input.settlement_id,
    expected_state_version: -1,
  })`,
    );
    expect(source).not.toBe(raw.source);
    await expect(operationTypeScriptV1Provider.execute({
      raw_inputs: rebindSource(raw, source),
      upstream: {},
    })).rejects.toMatchObject({code: "TS_OP_TARGET_POSITIVE_BLOCKED"});
  }, 60_000);

  it("rejects surplus raw input roles", async () => {
    const raw = await readRawInputs();
    await expect(operationTypeScriptV1Provider.execute({
      raw_inputs: {...raw, oracle_hint: "forbidden"},
      upstream: {},
    })).rejects.toMatchObject({code: "TS_OP_PROVIDER_INPUT_ROLES_INVALID"});
  });

  it("snapshots raw inputs before the first asynchronous proof edge", async () => {
    const baseline = await readRawInputs();
    const mutable = {...baseline};
    const pending = operationTypeScriptV1Provider.execute({
      raw_inputs: mutable,
      upstream: {},
    });
    mutable.source = `${mutable.source}\n`;
    await expect(pending).resolves.toMatchObject({
      result: "pass",
      provider_id: "operation-typescript-v1",
    });
  }, 60_000);

  it("remains unregistered without disturbing the legacy provider identity", () => {
    const ids = listFactoryNodeProvidersV1().map(
      ({provider_id: providerId}) => providerId,
    );
    expect(ids).not.toContain("operation-typescript-v1");
    expect(ids).toContain("typescript-operation-v1");
    expect(() => getFactoryNodeProviderV1(
      "operation-typescript-v1",
    )).toThrow("FACTORY_PROVIDER_UNKNOWN:operation-typescript-v1");
    expect(getFactoryNodeProviderV1("typescript-operation-v1")).toBe(
      legacyTypeScriptOperationV1Provider,
    );
    expect(operationTypeScriptV1Provider.provider_id).not.toBe(
      legacyTypeScriptOperationV1Provider.provider_id,
    );
  });

  it("rejects ambient target dependencies before native execution", async () => {
    const source = (await readRawInputs()).source;
    for (const prefix of [
      "const ambient = Date.now();\n",
      "const ambient = process.env.HOME;\n",
      "const ambient = fetch(\"https://example.invalid\");\n",
    ]) {
      expect(() => inspectTypeScriptOperationClosedSubset(
        `${prefix}${source}`,
      )).toThrow("TS_OP_CLOSED_SUBSET_AMBIENT_DEPENDENCY");
    }
  });
});
