import {readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {evaluateRuleParity} from "../../parity/evaluate-rule-parity.js";
import type {RuleHostileFixtureV1} from
  "../../../../families/pure-boolean-rule/contracts/pure-boolean-rule-contracts.js";
import {
  evaluatePureBooleanRuleProfile,
  PURE_BOOLEAN_RULE_BASELINE,
} from
  "../../../../families/pure-boolean-rule/evaluator/evaluate-pure-boolean-rule.js";
import {applyRuleHostile} from
  "../../../../families/pure-boolean-rule/mutations/apply-rule-hostile.js";
import {rulePythonV1Provider} from
  "../../../../factory/registry/providers/rule-python-v1.js";
import {ruleRustV1Provider} from
  "../../../../factory/registry/providers/rule-rust-v1.js";
import {ruleTypeScriptV1Provider} from
  "../../../../factory/registry/providers/rule-typescript-v1.js";
import {canonicalJson, sha256} from "../../../../factory/shared/canonical.js";
import {PYTHON_RULE_ADAPTER_PATHS} from
  "../../../../realizations/rule/python/pure-boolean-v1/index.js";
import {RUST_RULE_ADAPTER_PATHS} from
  "../../../../realizations/rule/rust/pure-boolean-v1/index.js";
import {TYPESCRIPT_RULE_ADAPTER_PATHS} from
  "../../../../realizations/rule/typescript/pure-boolean-v1/index.js";

const semanticHostiles = Object.freeze([
  ["non-boolean-return.json", "rule/non-boolean-return",
    "RMT_RULE_NON_BOOLEAN_RETURN"],
  ["hidden-mutation.json", "rule/hidden-mutation",
    "RMT_RULE_HIDDEN_MUTATION"],
  ["external-effect.json", "rule/external-effect",
    "RMT_RULE_EXTERNAL_EFFECT"],
  ["missing-enforces-edge.json", "rule/missing-enforces-edge",
    "RMT_RULE_MISSING_ENFORCES_EDGE"],
  ["inverse-enforces-edge.json", "rule/inverse-enforces-edge",
    "RMT_RULE_INVERSE_ENFORCES_EDGE"],
  ["undeclared-dependency.json", "rule/undeclared-dependency",
    "RMT_RULE_UNDECLARED_DEPENDENCY"],
  ["rule-calls-operation.json", "rule/rule-calls-operation",
    "RMT_RULE_RULE_CALLS_OPERATION"],
  ["evaluation-order-dependence.json", "rule/evaluation-order-dependence",
    "RMT_RULE_EVALUATION_ORDER_DEPENDENCE"],
  ["unstable-input-binding.json", "rule/unstable-input-binding",
    "RMT_RULE_UNSTABLE_INPUT_BINDING"],
  ["exception-as-false.json", "rule/exception-as-false",
    "RMT_RULE_EXCEPTION_AS_FALSE"],
] as const);
const hostileRoot =
  "projects/domainspec-v2/impl/architecture-conformance/families/pure-boolean-rule/hostiles";

const loadRaw = async (
  root: string,
  paths: Readonly<Record<string, string>>,
): Promise<Record<string, string>> => Object.fromEntries(await Promise.all(
  Object.entries(paths).map(async ([role, path]) =>
    [role, await readFile(resolve(root, path), "utf8")]),
));

const semanticSource = (result: Awaited<ReturnType<
  typeof ruleTypeScriptV1Provider.execute
>>) => {
  const output = result.semantic_output as Readonly<{
    summary: Record<string, unknown>;
    observations: unknown;
    native_evidence: unknown;
  }>;
  return Object.freeze({
    summary: output.summary,
    observations: output.observations,
    semantic_sha256: sha256(canonicalJson({
      summary: output.summary,
      observations: output.observations,
    })),
    native_evidence: output.native_evidence,
  });
};

export const evaluateWpRmt002RuleParity = async (
  root = process.cwd(),
) => {
  const [typescript, python, rust] = await Promise.all([
    loadRaw(root, TYPESCRIPT_RULE_ADAPTER_PATHS).then((raw_inputs) =>
      ruleTypeScriptV1Provider.execute({raw_inputs, upstream: {}})),
    loadRaw(root, PYTHON_RULE_ADAPTER_PATHS).then((raw_inputs) =>
      rulePythonV1Provider.execute({raw_inputs, upstream: {}})),
    loadRaw(root, RUST_RULE_ADAPTER_PATHS).then((raw_inputs) =>
      ruleRustV1Provider.execute({raw_inputs, upstream: {}})),
  ]);
  const sources = {
    typescript: semanticSource(typescript),
    python: semanticSource(python),
    rust: semanticSource(rust),
  };
  const parity = await evaluateRuleParity({
    typescript: sources.typescript,
    python: sources.python,
    rust: sources.rust,
  });
  if (parity.result !== "pass") {
    throw Object.assign(new Error("RMT_RULE_PARITY_BLOCKED"), {
      code: "RMT_RULE_PARITY_BLOCKED",
    });
  }
  const semanticControls = await Promise.all(semanticHostiles.map(
    async ([name, hostileId, expectedCode]) => {
      const fixture = JSON.parse(await readFile(
        resolve(root, hostileRoot, name), "utf8")) as RuleHostileFixtureV1;
      if (fixture.hostile_id !== hostileId ||
          fixture.hostile_class !== "type-semantic") {
        throw Object.assign(new Error("RMT_RULE_HOSTILE_CATALOGUE_DRIFT"), {
          code: "RMT_RULE_HOSTILE_CATALOGUE_DRIFT",
        });
      }
      const mutated = applyRuleHostile(PURE_BOOLEAN_RULE_BASELINE, fixture);
      const evaluation = evaluatePureBooleanRuleProfile(mutated);
      if (evaluation.findings.length !== 1 ||
          evaluation.findings[0]?.code !== expectedCode) {
        throw Object.assign(new Error("RMT_RULE_HOSTILE_NOT_KILLED"), {
          code: "RMT_RULE_HOSTILE_NOT_KILLED",
        });
      }
      return Object.freeze({
        hostile_id: hostileId,
        expected_code: expectedCode,
        observed_code: evaluation.findings[0].code,
        status: "killed" as const,
      });
    },
  ));
  return Object.freeze({
    schema_version: "RuleWpRmt002ParityReceipt/v1" as const,
    result: "pass" as const,
    provider_ids: Object.freeze([
      "rule-typescript-v1", "rule-python-v1", "rule-rust-v1",
    ]),
    portable_parity: parity,
    semantic_controls: Object.freeze({
      declared: semanticControls.length,
      killed: semanticControls.filter(({status}) =>
        status === "killed").length,
      controls: Object.freeze(semanticControls),
    }),
    native_evidence: Object.freeze({
      separated: true,
      native_hash_byte_comparison: false,
      records: Object.freeze(Object.entries(sources).map(([target, source]) =>
        Object.freeze({
          target,
          semantic_sha256: source.semantic_sha256,
          evidence: source.native_evidence,
        }))),
    }),
    claim_ceiling: "portable semantic parity for one candidate-local Rule over three hash-bound native adapters; native evidence remains separate and no native bytes are compared; no admission, registration, promotion, publication, deployment, or production claim",
    authority_effect: "none" as const,
  });
};
