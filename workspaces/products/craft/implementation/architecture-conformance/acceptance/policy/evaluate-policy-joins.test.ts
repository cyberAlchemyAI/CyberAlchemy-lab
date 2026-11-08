import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import type {FactoryUpstreamResultV1} from
  "../../factory/contracts/factory-node-provider-v1.js";
import {policyParityV1Provider} from
  "../../factory/registry/providers/policy-parity-v1.js";
import {policySelectsStrategyV1Provider} from
  "../../factory/registry/providers/policy-selects-strategy-v1.js";
import {pythonPolicyV1Provider} from
  "../../factory/registry/providers/python-policy-v1.js";
import {rustPolicyV1Provider} from
  "../../factory/registry/providers/rust-policy-v1.js";
import {typeScriptPolicyV1Provider} from
  "../../factory/registry/providers/typescript-policy-v1.js";
import {canonicalJson, sha256} from "../../factory/shared/canonical.js";
import {PYTHON_POLICY_RAW_PATHS} from
  "../../realizations/policy/python/strategy-selection-v1/index.js";
import {RUST_POLICY_RAW_PATHS} from
  "../../realizations/policy/rust/strategy-selection-v1/index.js";
import {TYPESCRIPT_POLICY_RAW_PATHS} from
  "../../realizations/policy/typescript/strategy-selection-v1/index.js";
import {
  evaluatePolicyParity,
  POLICY_DIRECT_HANDLES,
  POLICY_JOIN_RAW_PATHS,
  POLICY_PARITY_HANDLE,
  POLICY_RELATION_RAW_PATHS,
  provePolicyParity,
  provePolicySelectsStrategyRelation,
} from "./evaluate-policy-joins.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../..");
const readPaths = async (
  paths: Readonly<Record<string, string>>,
): Promise<Record<string, string>> => Object.fromEntries(await Promise.all(
  Object.entries(paths).map(async ([role, path]) =>
    [role, await readFile(resolve(repositoryRoot, path), "utf8")] as const),
));

let directUpstream: Record<string, FactoryUpstreamResultV1>;
let joinInputs: Record<string, string>;
let membershipInputs: Record<string, string>;
let relationUpstream: Record<string, FactoryUpstreamResultV1>;

beforeAll(async () => {
  joinInputs = await readPaths(POLICY_JOIN_RAW_PATHS);
  membershipInputs = await readPaths(POLICY_RELATION_RAW_PATHS);
  const results = await Promise.all([
    typeScriptPolicyV1Provider.execute({
      raw_inputs: await readPaths(TYPESCRIPT_POLICY_RAW_PATHS),
      upstream: {},
    }),
    pythonPolicyV1Provider.execute({
      raw_inputs: await readPaths(PYTHON_POLICY_RAW_PATHS),
      upstream: {},
    }),
    rustPolicyV1Provider.execute({
      raw_inputs: await readPaths(RUST_POLICY_RAW_PATHS),
      upstream: {},
    }),
  ]);
  directUpstream = Object.fromEntries(results.map((result, index) => {
    const handle = POLICY_DIRECT_HANDLES[index]!;
    return [handle.node_id, Object.freeze({
      node_id: handle.node_id,
      provider_id: result.provider_id,
      semantic_sha256: sha256(canonicalJson(result)),
      semantic_output: result.semantic_output,
    })];
  }));
  const parity = await policyParityV1Provider.execute({
    raw_inputs: joinInputs,
    upstream: directUpstream,
  });
  relationUpstream = {
    ...directUpstream,
    [POLICY_PARITY_HANDLE.node_id]: Object.freeze({
      node_id: POLICY_PARITY_HANDLE.node_id,
      provider_id: parity.provider_id,
      semantic_sha256: sha256(canonicalJson(parity)),
      semantic_output: parity.semantic_output,
    }),
  };
}, 60_000);

describe("Policy parity and selects_strategy joins", () => {
  it("proves exact three-language parity and kills all join hostiles", () => {
    const proof = provePolicyParity(directUpstream, joinInputs);
    expect(proof).toMatchObject({
      schema_version: "PolicyParityProof/v1",
      result: "pass",
      authority_effect: "none",
    });
    expect(proof.composed_from.map(({language}) => language))
      .toEqual(["typescript", "python", "rust"]);
    expect(proof.obligations).toHaveLength(14);
    expect(proof.obligations.every(({status}) => status === "passed")).toBe(true);
    expect(proof.hostile_mutations).toHaveLength(13);
    expect(proof.hostile_mutations.every(({status}) => status === "killed"))
      .toBe(true);
    expect(proof.non_execution_by_language).toEqual([
      {language: "typescript", attempt_count: 0, completion_count: 0},
      {language: "python", attempt_count: 0, completion_count: 0},
      {language: "rust", attempt_count: 0, completion_count: 0},
    ]);
    expect(JSON.stringify(proof)).not.toContain('"pid"');
  });

  it("proves every owner-case selection relates to a current data-only member", () => {
    const proof = provePolicySelectsStrategyRelation(
      relationUpstream,
      membershipInputs,
    );
    expect(proof).toMatchObject({
      schema_version: "PolicySelectsStrategyProof/v1",
      result: "pass",
      authority_effect: "none",
    });
    expect(proof.relation_rows).toHaveLength(5);
    expect(new Set(proof.relation_rows.map(({strategy_id: strategyId}) => strategyId)))
      .toEqual(new Set([
        "settlement.route.standard",
        "settlement.route.expedited",
        "settlement.route.manual-review",
      ]));
    expect(proof.relation_rows.every(({relation, member_executable: executable}) =>
      relation === "selects_strategy" && executable === false)).toBe(true);
    expect(proof.obligations).toHaveLength(8);
    expect(proof.membership_evaluations).toHaveLength(3);
    expect(proof.membership_evaluations.every(({evaluation}) =>
      evaluation.positive_decision_accounting.passed === 8)).toBe(true);
    expect(proof.membership_mutations).toHaveLength(10);
    expect(proof.hostile_mutations).toHaveLength(10);
  });

  it("exposes both joins as explicit factory providers", async () => {
    const parity = await policyParityV1Provider.execute({
      raw_inputs: joinInputs,
      upstream: directUpstream,
    });
    const relation = await policySelectsStrategyV1Provider.execute({
      raw_inputs: membershipInputs,
      upstream: relationUpstream,
    });
    expect(parity.accounting).toEqual({
      positives_declared: 14,
      positives_passed: 14,
      mutants_declared: 13,
      mutants_killed: 13,
    });
    expect(relation.accounting).toEqual({
      positives_declared: 32,
      positives_passed: 32,
      mutants_declared: 20,
      mutants_killed: 20,
    });
  });

  it("fails closed on direct-handle and parity-handle drift", () => {
    const missing = structuredClone(directUpstream);
    delete missing[POLICY_DIRECT_HANDLES[0].node_id];
    expect(() => evaluatePolicyParity(missing, joinInputs))
      .toThrowError("POLICY_PARITY_HANDLE_SET_MISMATCH");
    const foreign = structuredClone(relationUpstream) as any;
    foreign[POLICY_PARITY_HANDLE.node_id].provider_id = "foreign-provider";
    expect(() => provePolicySelectsStrategyRelation(foreign, membershipInputs))
      .toThrowError("POLICY_RELATION_PROVIDER_MISMATCH");
  });
});
