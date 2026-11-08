import { pathToFileURL } from "node:url";

import type {
  RuleCaseV1,
  RuleObservationV1,
} from "../../../families/outcome-function/contracts/rule-contracts.js";
import { canonicalRuleJson } from "../../../families/outcome-function/providers/decode-rule-contracts.js";
import { createHash } from "node:crypto";

type EffectGlobal = typeof globalThis & { __domainspecRuleEffectCount?: number };
const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");

export const observeCompiledTypeScriptRule = async (input: Readonly<{
  outputPath: string;
  symbolName: string;
  bindingId: string;
  bindingSourceSha256: string;
  cases: readonly RuleCaseV1[];
}>): Promise<RuleObservationV1> => {
  const loaded = await import(
    `${pathToFileURL(input.outputPath).href}?proof=${Date.now()}`,
  ) as Record<string, unknown>;
  const callable = loaded[input.symbolName];
  if (typeof callable !== "function") {
    throw Object.assign(new Error("TS_RULE_RUNTIME_EXPORT_MISSING"), {
      code: "TS_RULE_RUNTIME_EXPORT_MISSING",
    });
  }
  const host = globalThis as EffectGlobal;
  const caseObservations = [];
  try {
    for (const item of input.cases) {
      host.__domainspecRuleEffectCount = 0;
      let outcome: unknown;
      try {
        outcome = callable(item.input);
      } catch {
        outcome = null;
      }
      caseObservations.push(Object.freeze({
        case_id: item.case_id,
        outcome: typeof outcome === "boolean" || typeof outcome === "string" ||
            typeof outcome === "number" || outcome === null
          ? outcome
          : null,
        observed_effect_count: host.__domainspecRuleEffectCount ?? 0,
      }));
    }
  } finally {
    delete host.__domainspecRuleEffectCount;
  }
  const body: Omit<RuleObservationV1, "observation_sha256"> = Object.freeze({
    schema_version: "RuleObservation/v1" as const,
    binding_id: input.bindingId,
    source_sha256: input.bindingSourceSha256,
    symbol_name: input.symbolName,
    case_observations: Object.freeze(caseObservations),
    unsupported: Object.freeze([]),
    authority_effect: "none" as const,
  });
  return Object.freeze({
    ...body,
    observation_sha256: sha256(canonicalRuleJson(body)),
  });
};
