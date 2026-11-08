import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import {
  buildTypeScriptPolicyProof,
  TYPESCRIPT_POLICY_RAW_PATHS,
  type TypeScriptPolicyRawInputs,
} from "./index.js";
import {typeScriptPolicyV1Provider} from
  "../../../../factory/registry/providers/typescript-policy-v1.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");
let raw: TypeScriptPolicyRawInputs;

beforeAll(async () => {
  raw = Object.freeze(Object.fromEntries(await Promise.all(
    Object.entries(TYPESCRIPT_POLICY_RAW_PATHS).map(async ([role, path]) => [
      role,
      await readFile(resolve(repositoryRoot, path), "utf8"),
    ]),
  )) as TypeScriptPolicyRawInputs);
});

describe("TypeScript Policy realization and provider", () => {
  it("executes all owner cases twice and proves zero strategy calls", async () => {
    const proof = await buildTypeScriptPolicyProof(raw);
    expect(proof).toMatchObject({
      schema_version: "TypeScriptPolicyComposedProof/v1",
      result: "pass",
      target: {
        target_id: "policy.typescript.settlement-routing/v1",
        language: "typescript",
        protocol_id: "typescript.bound-policy/v1",
      },
      runtime_proof: {
        cases_executed: 5,
        fresh_processes_executed: 10,
        distinct_pid_pairs: 5,
        result_kind: "primitive-strategy-identity",
        strategy_execution_attempts: 0,
      },
      accounting: {
        positives: {declared: 14, passed: 14},
        mutants: {declared: 16, killed: 16},
      },
      authority_effect: "none",
    });
    expect(proof.family_evaluation.verdict).toBe("pass");
    expect(proof.observation.strategy_execution_observation.attempt_count).toBe(0);
    expect(proof.closed_subset_proof.target_call_expressions).toBe(0);
  });

  it("exposes an explicit unregistered factory provider", async () => {
    expect(typeScriptPolicyV1Provider).toMatchObject({
      provider_id: "typescript-policy-v1",
      compatible_kinds: ["direct-proof"],
    });
    const result = await typeScriptPolicyV1Provider.execute({
      raw_inputs: raw,
      upstream: Object.freeze({}),
    });
    expect(result).toMatchObject({
      result: "pass",
      provider_id: "typescript-policy-v1",
      accounting: {
        positives_declared: 14,
        positives_passed: 14,
        mutants_declared: 16,
        mutants_killed: 16,
      },
    });
  });

  it("rejects stale source and proof-builder bytes", async () => {
    await expect(buildTypeScriptPolicyProof({
      ...raw,
      source: raw.source.replace(
        "settlement.route.expedited",
        "settlement.route.standard",
      ),
    })).rejects.toThrow("TS_POLICY_BINDING_INPUT_STALE:source");
    await expect(buildTypeScriptPolicyProof({
      ...raw,
      proof_builder: `${raw.proof_builder}\n`,
    })).rejects.toThrow("TS_POLICY_BINDING_INPUT_STALE:proof_builder");
  });
});
