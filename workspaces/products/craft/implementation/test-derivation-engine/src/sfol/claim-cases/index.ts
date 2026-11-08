import { createHash } from "node:crypto";
import { lstatSync, readFileSync, realpathSync, statSync } from "node:fs";
import { isAbsolute, join, relative } from "node:path";

import { canonicalSfolJson, derivePureCases, digestSfolValue, type DerivedPureCase } from "../cases/index.js";
import { buildClauseDenominator } from "../denominator/index.js";
import { evaluateTerm, type SemanticValue } from "../evaluator/index.js";
import { decodeNodeLogicModule } from "../language/decoder.js";
import { typecheckLogicModule } from "../language/typecheck.js";
import { derivePureFixtures, EXHAUSTIVE_FINITE_RULESET, type PartitionDomain } from "../partitions/index.js";

const SHA256 = /^[a-f0-9]{64}$/;
const MAX_SOURCE_BYTES = 2 * 1024 * 1024;
const CEILING = "selected admitted SFOL source to complete Boolean cases only; no upstream graph or build proof; no DomainSpec v4 neutral set; no provider observation; no F5 satisfaction" as const;
const BOOLEAN_DOMAIN = [{ tag: "boolean", value: false }, { tag: "boolean", value: true }] as const;

export type SelectedSfolRef = Readonly<{ path: string; sha256: string; size_bytes: number }>;
export type SelectedSfolClaimSources = Readonly<{
  decision: SelectedSfolRef;
  claim: SelectedSfolRef;
  module: SelectedSfolRef;
  clause_manifest: SelectedSfolRef;
  domain: PartitionDomain;
  max_cases: number;
}>;

export type SelectedSfolCaseSet = Readonly<{
  schema_version: "tde.selected-sfol-claim-cases/v1-candidate";
  selection: SelectedSfolClaimSources;
  claim_id: string;
  clause_id: string;
  denominator_digest: string;
  ruleset_digest: string;
  domain_digest: string;
  domain_scope: "full-boolean-valuation-of-selected-clause-inputs";
  proof_context_verification: "not-performed";
  oracle_provenance: "same-typed-sfol-evaluator";
  f5_eligibility: "blocked-missing-domainspec-v4-chain";
  cases: readonly DerivedPureCase[];
  oracles: readonly Readonly<{
    case_id: string;
    witness_input_digest: string;
    expected_value: SemanticValue;
    expected_digest: string;
  }> [];
  case_set_digest: string;
  authority_effect: "none";
  claim_ceiling: typeof CEILING;
}>;

export class SelectedSfolCaseError extends Error {
  constructor(readonly code: "SOURCE_DRIFT" | "ADMISSION_MISMATCH" | "DERIVATION_FAILED" | "REPLAY_MISMATCH", detail: string) {
    super(`${code}:${detail}`);
    this.name = "SelectedSfolCaseError";
  }
}

function fail(code: SelectedSfolCaseError["code"], detail: string): never {
  throw new SelectedSfolCaseError(code, detail);
}

function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("ADMISSION_MISMATCH", "expected an object");
  return value as Record<string, unknown>;
}

function readSelected(root: string, ref: SelectedSfolRef): unknown {
  if (!ref || Object.keys(ref).sort().join(",") !== "path,sha256,size_bytes" ||
      typeof ref.path !== "string" || !ref.path || isAbsolute(ref.path) || ref.path.includes("\\") ||
      ref.path.split("/").some(part => !part || part === "." || part === "..") ||
      !SHA256.test(ref.sha256) || !Number.isSafeInteger(ref.size_bytes) ||
      ref.size_bytes < 1 || ref.size_bytes > MAX_SOURCE_BYTES)
    fail("SOURCE_DRIFT", "invalid exact source reference");
  const base = realpathSync(root);
  let path = base;
  for (const part of ref.path.split("/")) {
    path = join(path, part);
    if (lstatSync(path).isSymbolicLink()) fail("SOURCE_DRIFT", `symlink in ${ref.path}`);
  }
  const rel = relative(base, path);
  if (rel === ".." || rel.startsWith("../") || isAbsolute(rel) || realpathSync(path) !== path)
    fail("SOURCE_DRIFT", `source escapes selected root: ${ref.path}`);
  const before = statSync(path);
  if (!before.isFile() || before.size !== ref.size_bytes) fail("SOURCE_DRIFT", `source size changed: ${ref.path}`);
  const bytes = readFileSync(path);
  const after = statSync(path);
  if (before.ino !== after.ino || before.dev !== after.dev || before.mtimeMs !== after.mtimeMs ||
      bytes.length !== ref.size_bytes || digestSfolBytes(bytes) !== ref.sha256)
    fail("SOURCE_DRIFT", `source bytes changed: ${ref.path}`);
  try { return JSON.parse(bytes.toString("utf8")); }
  catch { return fail("SOURCE_DRIFT", `source is not JSON: ${ref.path}`); }
}

function digestSfolBytes(bytes: Buffer): string {
  // Exact file refs hash bytes, while SFOL semantic digests use canonical JSON.
  return createHash("sha256").update(bytes).digest("hex");
}

/** This validates selected Auth SFOL admission content, not the historical
 * authenticity of the decision or any DomainSpec v4 FormalClaim projection. */
export function deriveSelectedSfolClaimCases(root: string, selection: SelectedSfolClaimSources): SelectedSfolCaseSet {
  if (!selection || Object.keys(selection).sort().join(",") !== "claim,clause_manifest,decision,domain,max_cases,module" ||
      !Number.isSafeInteger(selection.max_cases) || selection.max_cases < 1 || selection.max_cases > 64 ||
      !selection.domain || !selection.domain.inputs || Object.keys(selection.domain.inputs).length === 0)
    fail("DERIVATION_FAILED", "explicit finite input domain and bounded case budget required");
  const decision = object(readSelected(root, selection.decision));
  const claim = object(readSelected(root, selection.claim));
  const module = object(readSelected(root, selection.module));
  const manifest = readSelected(root, selection.clause_manifest);
  const artifacts = object(decision.admitted_artifacts);
  const admittedClaim = object(artifacts.formal_claim);
  const admittedModule = object(artifacts.sfol_module);
  const formalism = object(claim.formalism);
  const admissionMeaning = object(decision.meaning_predecessor);
  const claimMeaning = object(claim.meaning_predecessor);
  if (decision.schema_version !== "auth-foundation.sfol-formal-claim-admission/v1" ||
      decision.authority_effect !== "admits one exact SFOL FormalClaim and module for bounded local EVF/TDE consumption" ||
      !Array.isArray(decision.consumer_authorization) ||
      !decision.consumer_authorization.includes("DomainSpec TDE local derivation") ||
      claim.schema_version !== "auth-foundation.formal-claim-sfol/v1" ||
      claim.lifecycle_status !== "authored-candidate-admitted-by-separate-owner-decision" ||
      claimMeaning.decision_path !== admissionMeaning.decision_path ||
      claim.formal_claim_id !== admittedClaim.formal_claim_id ||
      selection.claim.path !== admittedClaim.path || selection.claim.sha256 !== admittedClaim.sha256 ||
      selection.module.path !== admittedModule.path || selection.module.sha256 !== admittedModule.sha256 ||
      formalism.module_path !== selection.module.path || formalism.clause_id !== admittedModule.clause_id ||
      formalism.language_version !== "domainspec-sfol/v1" ||
      module.module_id === undefined)
    fail("ADMISSION_MISMATCH", "selected admission, claim and module identity differ");
  const decoded = decodeNodeLogicModule(module);
  if (!decoded.ok) fail("DERIVATION_FAILED", `module decode: ${decoded.diagnostics[0]?.code}`);
  const typedResult = typecheckLogicModule(decoded.value);
  if (!typedResult.ok) fail("DERIVATION_FAILED", `module typecheck: ${typedResult.diagnostics[0]?.code}`);
  const typed = typedResult.value;
  const clause = typed.source.clauses.find(item => item.clause_id === formalism.clause_id);
  if (!clause || clause.kind !== "predicate" || clause.status !== "admitted" ||
      typed.source.clauses.length !== 1 || typed.source.module_id !== module.module_id)
    fail("ADMISSION_MISMATCH", "selected single admitted predicate clause is unavailable");
  const selectedDomainInputs = selection.domain.inputs;
  if (!selectedDomainInputs) fail("DERIVATION_FAILED", "explicit finite input domain required");
  const declaredInputs = clause.inputs.map(item => item.name).sort();
  const selectedInputs = Object.keys(selectedDomainInputs).sort();
  if (Object.keys(selection.domain).sort().join(",") !== "inputs" ||
      canonicalSfolJson(declaredInputs) !== canonicalSfolJson(selectedInputs) ||
      clause.inputs.some(item => item.sort.tag !== "primitive" || item.sort.name !== "boolean" ||
        canonicalSfolJson(selectedDomainInputs[item.name]) !== canonicalSfolJson(BOOLEAN_DOMAIN)))
    fail("DERIVATION_FAILED", "finite domain must explicitly cover exactly the clause inputs");
  const denominator = buildClauseDenominator(manifest);
  if (denominator.members.length !== 1 || denominator.members[0]?.clause_id !== clause.clause_id ||
      denominator.members[0].module_digest !== digestSfolValue(typed.source) ||
      denominator.members[0].clause_digest !== digestSfolValue(clause) ||
      denominator.members[0].node_digest !== selection.module.sha256)
    fail("ADMISSION_MISMATCH", "clause denominator differs from selected module");
  const ruleset = { ...EXHAUSTIVE_FINITE_RULESET, max_cases: selection.max_cases };
  const args = { typed, typed_module_digest: digestSfolValue(typed.source),
    typed_clause_digests: { [clause.clause_id]: digestSfolValue(clause) }, denominator };
  // The selected domain above must name the complete Boolean values, while
  // SFOL's canonical Boolean default preserves the existing case identities.
  const partitioned = derivePureFixtures({ ...args, ruleset });
  if (!partitioned.ok) fail("DERIVATION_FAILED", `finite partitions: ${partitioned.diagnostics[0]?.code}`);
  const derived = derivePureCases({ ...args, fixtures: partitioned.value });
  if (!derived.ok) fail("DERIVATION_FAILED", `pure cases: ${derived.diagnostics[0]?.code}`);
  const oracles = derived.value.map(item => {
    const evaluation = evaluateTerm(typed, clause.expression, { variables: item.inputs, universes: item.universes });
    if (evaluation.status !== "value" || evaluation.value.tag !== "boolean" ||
        digestSfolValue(evaluation.value) !== item.expected_digest)
      fail("DERIVATION_FAILED", `typed Boolean oracle disagrees for ${item.case_id}`);
    return { case_id: item.case_id, witness_input_digest: digestSfolValue({ inputs: item.inputs, universes: item.universes }),
      expected_value: evaluation.value, expected_digest: item.expected_digest };
  });
  const unsigned = { schema_version: "tde.selected-sfol-claim-cases/v1-candidate" as const,
    selection, claim_id: claim.formal_claim_id as string, clause_id: clause.clause_id,
    denominator_digest: denominator.digest, ruleset_digest: partitioned.ruleset_digest,
    domain_digest: partitioned.domain_digest,
    domain_scope: "full-boolean-valuation-of-selected-clause-inputs" as const,
    proof_context_verification: "not-performed" as const,
    oracle_provenance: "same-typed-sfol-evaluator" as const,
    f5_eligibility: "blocked-missing-domainspec-v4-chain" as const,
    cases: derived.value, oracles,
    authority_effect: "none" as const, claim_ceiling: CEILING };
  return { ...unsigned, case_set_digest: digestSfolValue(unsigned) };
}

/** Replay requires independently selected sources; a self-selected receipt is
 * not evidence of admission origin, provider execution or F5 satisfaction. */
export function replaySelectedSfolClaimCases(root: string, selection: SelectedSfolClaimSources,
  candidate: SelectedSfolCaseSet): SelectedSfolCaseSet {
  const current = deriveSelectedSfolClaimCases(root, selection);
  if (canonicalSfolJson(current) !== canonicalSfolJson(candidate))
    fail("REPLAY_MISMATCH", "case set differs from current selected sources and derivation");
  return current;
}
