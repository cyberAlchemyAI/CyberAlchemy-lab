// Deterministic Test-Derivation Engine — public entrypoint.
// Pipeline: parse -> G -> derive (δ) -> obligation_key -> emit.
// See SPEC.md / ARCHITECTURE.md. No LLM, no network: determinism by construction.

import { parse } from "./grammar/index.js";
import { derive, DEFAULT_RULE_SET, type RuleSet } from "./rules/index.js";
import { emitSpec } from "./emit/spec.js";
import { emitTests } from "./emit/tests.js";
import type { Obligation } from "./ir/types.js";

export interface DeriveOptions {
  readonly rules?: RuleSet;
  readonly emitTests?: boolean;
}

export interface DeriveResult {
  readonly obligations: readonly Obligation[];
  readonly spec: string;
  readonly tests?: string;
}

/** Compile a feature's canonical docs into deterministic test obligations. */
export function deriveFeature(
  featureDir: string,
  opts: DeriveOptions = {},
): DeriveResult {
  const { graph } = parse(featureDir);
  const obligations = derive(graph, opts.rules ?? DEFAULT_RULE_SET);
  return {
    obligations,
    spec: emitSpec(obligations),
    ...(opts.emitTests ? { tests: emitTests(obligations) } : {}),
  };
}

export { parse } from "./grammar/index.js";
export { derive, classifyFormal } from "./rules/index.js";
export type { Obligation } from "./ir/types.js";
export { obligationKey } from "./keys/index.js";
export {
  buildResidueReceipt,
  renderResidueReceipt,
} from "./residue/receipt.js";
export type { ResidueReceipt } from "./residue/receipt.js";
export {
  compareRoundTrip,
  deriveDescriptor,
  engineSemanticId,
  engineSemanticSet,
  isIrreducibleMiss,
  parseCommittedSemantic,
  parseCommittedSpec2,
  semanticRoundTrip,
} from "./roundtrip/index.js";
export type {
  ClassifiedMiss,
  CommittedDialect,
  CommittedSpec,
  DialectDescriptor,
  SemanticOptions,
} from "./roundtrip/index.js";
export {
  ExactBindingResolutionError,
  resolveExactBinding,
} from "./bindings/index.js";
export { emitEvfS1StrictTests } from "./emit/tests.js";
export * from "./minted-project/types.js";
export * from "./minted-project/derive.js";
export * from "./minted-project/typed-predicate.js";
export * from "./minted-project/enforces-execution.js";
export * from "./minted-project/evolvable-validation-receipt.js";
export * from "./bte/development-engine.js";
export * from "./bte/proof-engine.js";
export * from "./bte/consumer-engine.js";
export {
  runCompleteDevelopmentBte,
  runDevelopmentBte,
} from "./bte/development-pipeline.js";
export type {
  DevelopmentBteRun,
  DevelopmentBteSummary,
} from "./bte/development-pipeline.js";
