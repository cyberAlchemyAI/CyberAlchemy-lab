import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {EFFECT_CHANNELS} from
  "../../../../kernel/evidence/effect-observation/index.js";
import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {typeScriptCalculationV1Provider} from
  "../../../../factory/registry/providers/typescript-calculation-v1.js";
import {inspectTypeScriptCalculationClosedSubset} from "./closed-subset.js";
import {TYPESCRIPT_CALCULATION_RAW_PATHS} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");

const readRawInputs = async (): Promise<Record<string, string>> =>
  Object.fromEntries(await Promise.all(
    Object.entries(TYPESCRIPT_CALCULATION_RAW_PATHS).map(async ([role, path]) =>
      [role, await readFile(resolve(repositoryRoot, path), "utf8")] as const),
  ));

const closedTarget = (body: string, prefix = ""): string => `${prefix}export const calculateNetSettlement = (
  input: Readonly<{
    gross_amount_minor: number;
    fee_amount_minor: number;
  }>,
): number => ${body};
`;

describe("TypeScript Calculation direct provider", () => {
  it("proves the owner cases in distinct fresh processes and kills every family mutant", async () => {
    const result = await typeScriptCalculationV1Provider.execute({
      raw_inputs: await readRawInputs(),
      upstream: {},
    });
    expect(result).toMatchObject({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "typescript-calculation-v1",
      accounting: {
        positives_declared: 11,
        positives_passed: 11,
        mutants_declared: 13,
        mutants_killed: 13,
      },
      semantic_output: {
        proof: {
          schema_version: "TypeScriptCalculationComposedProof/v1",
          result: "pass",
          runtime_proof: {
            cases_executed: 4,
            fresh_processes_executed: 8,
            distinct_pid_pairs: 4,
            result_kind: "primitive-number",
          },
          family_evaluation: {
            verdict: "pass",
            portable_claim:
              "owner-bound-deterministic-zero-effect-value-under-declared-perimeter",
          },
          accounting: {
            positives: {declared: 11, passed: 11},
            mutants: {declared: 13, killed: 13},
          },
        },
      },
      authority_effect: "none",
    });
    expect(result.claim_ceiling).toContain("four owner-authored JSON-materialized");
    expect(result.claim_ceiling).toContain("not arbitrary callers, getter or Proxy inputs");
  }, 30_000);

  it("binds every proof-producing source and rejects stale bytes", async () => {
    const boundRoles = [
      "definition",
      "denominator",
      "mutations",
      "descriptor",
      "source",
      "observer",
      "proof_builder",
      "provider",
    ] as const;
    for (const role of boundRoles) {
      const inputs = await readRawInputs();
      inputs[role] = `${inputs[role]}\n`;
      await expect(typeScriptCalculationV1Provider.execute({
        raw_inputs: inputs,
        upstream: {},
      })).rejects.toMatchObject({code: "TS_CALC_BINDING_INPUT_STALE"});
    }
    const bindingInputs = await readRawInputs();
    bindingInputs.binding = bindingInputs.binding.replace(
      "typescript.net-settlement.bound-calculation/v1",
      "typescript.net-settlement.tampered/v1",
    );
    await expect(typeScriptCalculationV1Provider.execute({
      raw_inputs: bindingInputs,
      upstream: {},
    })).rejects.toMatchObject({code: "TS_CALC_BINDING_POLICY_INVALID"});
  });

  it.each([
    ["clock", closedTarget("Date.now()")],
    ["random", closedTarget("Math.random()")],
    ["environment", closedTarget("input.gross_amount_minor - process.env.FEE")],
    ["filesystem", closedTarget(
      "input.gross_amount_minor - input.fee_amount_minor",
      "import {readFileSync} from \"node:fs\";\n",
    )],
    ["network", closedTarget("fetch(\"https://example.invalid\")")],
    ["process", closedTarget("input.gross_amount_minor - process.pid")],
    ["global-cache", closedTarget("input.gross_amount_minor - globalThis.cachedFee")],
    ["delayed-lazy", closedTarget("setTimeout(() => 0, 0)")],
    ["callback", `export const calculateNetSettlement = (
  input: Readonly<{gross_amount_minor: number; fee_amount_minor: number}>,
  callback: (value: number) => void,
): number => input.gross_amount_minor - input.fee_amount_minor;
`],
    ["iterator-future", `export const calculateNetSettlement = async (
  input: Readonly<{gross_amount_minor: number; fee_amount_minor: number}>,
): Promise<number> => input.gross_amount_minor - input.fee_amount_minor;
`],
    ["finalizer-drop", closedTarget("new WeakRef(input)")],
    ["mutable-output", `export const calculateNetSettlement = (
  input: Readonly<{gross_amount_minor: number; fee_amount_minor: number}>,
): {value: number} => ({value: input.gross_amount_minor - input.fee_amount_minor});
`],
  ])("rejects the %s channel before execution", (_channel, source) => {
    expect(() => inspectTypeScriptCalculationClosedSubset(source)).toThrow();
  });

  it.each([
    ["any input", `export const calculateNetSettlement = (
  input: any,
): number => input.gross_amount_minor - input.fee_amount_minor;
`],
    ["ambient input type", `export const calculateNetSettlement = (
  input: typeof globalThis,
): number => input.gross_amount_minor - input.fee_amount_minor;
`],
    ["optional input read", `export const calculateNetSettlement = (
  input: Readonly<{gross_amount_minor: number; fee_amount_minor: number}>,
): number => input?.gross_amount_minor - input.fee_amount_minor;
`],
  ])("rejects the non-exact %s signature", (_name, source) => {
    expect(() => inspectTypeScriptCalculationClosedSubset(source)).toThrow();
  });

  it("covers all twelve channels and remains unregistered until RMT-CALC-006", async () => {
    const source = await readFile(resolve(
      repositoryRoot,
      TYPESCRIPT_CALCULATION_RAW_PATHS.source,
    ), "utf8");
    expect(inspectTypeScriptCalculationClosedSubset(source)
      .supported_effect_channels).toEqual(EFFECT_CHANNELS);
    expect(typeScriptCalculationV1Provider.required_input_roles)
      .toEqual(Object.keys(TYPESCRIPT_CALCULATION_RAW_PATHS));
    expect(listFactoryNodeProvidersV1()
      .some(({provider_id: providerId}) =>
        providerId === typeScriptCalculationV1Provider.provider_id)).toBe(false);
  });
});
