import { deriveUnit, L1_CURRENT_PROJECTION } from "./derive.js";
import { canonicalJson, digestValue, exactRef, readJson } from "./exact-ref.js";
import { fail, R4_IDENTITY, type ExactRef, type GraphHandle } from "./types.js";
import { loadCurrentR4Binding, R4_CURRENT_BINDING } from "./verify-r4-current.js";

const ALGORITHM_PATH = "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l1/r4-case-projection.ts";
const CEILING = "candidate-local-r4-authored-pure-decision-cases-only-no-formal-claim-or-runtime-observation";

type DecisionInput = Readonly<{
  existingTransactions: readonly Readonly<{ type: string; date: string }>[];
  periodEnd: string;
  totalAppliedMakeup: number;
  totalPayout: number;
}>;
type FixtureCase = Readonly<{
  case_id: string;
  control_class: "truth-table" | "other-date" | "other-type";
  input: DecisionInput;
}>;
type Fixture = Readonly<{
  schema_version: string;
  fixture_id: string;
  cases: readonly FixtureCase[];
  expected_values_forbidden: boolean;
}>;
type TruthRow = Readonly<{
  case_id: string;
  same_date_makeup_applied_count: number;
  expected: boolean;
}>;

export type R4CaseProjection = Readonly<{
  schema_version: "tde.r4-authored-case-projection/v1-candidate";
  owner: "TDE";
  source_kind: "exact-authored-truth-table";
  graph_handle: GraphHandle;
  binding_ref: ExactRef;
  semantic_ref: ExactRef;
  fixture_ref: ExactRef;
  algorithm_ref: ExactRef;
  obligation_id: string;
  cases: readonly Readonly<{
    obligation_id: string;
    case_id: string;
    control_class: FixtureCase["control_class"];
    normalized_inputs: DecisionInput;
    expected_boolean: boolean;
  }>[];
  input_digest: string;
  output_digest: string;
  authority_effect: "none";
  claim_ceiling: typeof CEILING;
}>;

/** Exact projection of candidate-local authored R4 cases, not a FormalClaim
 * neutral obligation set or an observed provider result. */
export function deriveR4CaseProjection(repoRoot: string): R4CaseProjection {
  const derivation = deriveUnit(repoRoot, "R4", { projection: L1_CURRENT_PROJECTION });
  const binding = loadCurrentR4Binding(repoRoot);
  const bindingRef = exactRef(repoRoot, R4_CURRENT_BINDING);
  const semanticRef = exactRef(repoRoot, binding.semantic_ref.path);
  const fixtureRef = exactRef(repoRoot, binding.fixture_ref.path);
  const algorithmRef = exactRef(repoRoot, ALGORITHM_PATH);
  const fixture = readJson<Fixture>(repoRoot, binding.fixture_ref.path);
  if (fixture.schema_version !== "evf.financial-settlement-r4-input/v1" ||
      fixture.fixture_id !== "evf.l1.financial-settlement.r4.fixture.v1" ||
      fixture.expected_values_forbidden !== true || fixture.cases.length !== 5 ||
      new Set(fixture.cases.map(row => row.case_id)).size !== 5) {
    fail("FIXTURE_DIGEST_STALE", "derivation", "R4 fixture identity or case denominator differs");
  }
  const semantic = derivation.O_gen.semantic_contract as { readonly fixed_premise?: unknown;
    readonly decision_field?: unknown; readonly truth_table?: readonly TruthRow[] };
  if (derivation.identity.obligation_id !== R4_IDENTITY.obligation_id ||
      derivation.O_gen.obligation_id !== R4_IDENTITY.obligation_id ||
      derivation.O_gen.rule_id !== R4_IDENTITY.rule_id ||
      derivation.O_gen.edge_id !== R4_IDENTITY.edge_id ||
      derivation.O_gen.relationship !== "enforces" ||
      derivation.O_gen.target_id !== "financial-settlement.GenerateSettlement" ||
      derivation.O_gen.contract_kind !== "pure-decision-truth-table" ||
      semantic.decision_field !== "shouldCreateMakeupAppliedEvent" ||
      canonicalJson(semantic.fixed_premise) !== canonicalJson({ totalAppliedMakeup: { operator: "gt", right: 0 } }) ||
      canonicalJson(derivation.O_gen.excluded_claims) !== canonicalJson([
        "database-write", "event-emission", "P3", "full-settlement-preconditions",
      ]) ||
      !semantic.truth_table || semantic.truth_table.length !== 5) {
    fail("OBLIGATION_MISMATCH", "derivation", "R4 authored decision obligation differs");
  }
  const truth = new Map<string, TruthRow>();
  for (const row of semantic.truth_table) {
    if (typeof row.case_id !== "string" || !Number.isSafeInteger(row.same_date_makeup_applied_count) ||
        typeof row.expected !== "boolean" || truth.has(row.case_id)) {
      fail("OBLIGATION_MISMATCH", "derivation", "R4 authored truth-table row is invalid");
    }
    truth.set(row.case_id, row);
  }
  const cases = fixture.cases.map(row => {
    if (!row || typeof row !== "object" || !row.input || typeof row.input !== "object" ||
        Object.keys(row).sort().join(",") !== "case_id,control_class,input" ||
        Object.keys(row.input).sort().join(",") !== "existingTransactions,periodEnd,totalAppliedMakeup,totalPayout" ||
        !Number.isSafeInteger(row.input.totalAppliedMakeup) || row.input.totalAppliedMakeup <= 0 ||
        !Number.isSafeInteger(row.input.totalPayout) || typeof row.input.periodEnd !== "string" ||
        !Array.isArray(row.input.existingTransactions)) {
      fail("FIXTURE_DIGEST_STALE", "derivation", `R4 fixture case shape or premise differs: ${row.case_id}`);
    }
    for (const transaction of row.input.existingTransactions) {
      if (Object.keys(transaction).sort().join(",") !== "date,type" ||
          typeof transaction.date !== "string" || typeof transaction.type !== "string") {
        fail("FIXTURE_DIGEST_STALE", "derivation", `R4 fixture transaction shape differs: ${row.case_id}`);
      }
    }
    const authored = truth.get(row.case_id);
    if (!authored) fail("OBLIGATION_MISMATCH", "derivation", `R4 fixture case missing from authored table: ${row.case_id}`);
    const sameDateCount = row.input.existingTransactions.filter(item =>
      item.type === "MAKEUP_APPLIED" && item.date === row.input.periodEnd).length;
    if (sameDateCount !== authored.same_date_makeup_applied_count) {
      fail("FIXTURE_DIGEST_STALE", "derivation", `R4 same-date count differs: ${row.case_id}`);
    }
    return { obligation_id: R4_IDENTITY.obligation_id, case_id: row.case_id,
      control_class: row.control_class, normalized_inputs: row.input, expected_boolean: authored.expected };
  });
  if (cases.length !== truth.size ||
      canonicalJson(cases.map(row => row.case_id)) !== canonicalJson([
        "r4-zero-same-date", "r4-one-same-date", "r4-two-same-date", "r4-other-date-control", "r4-other-type-control",
      ]) ||
      canonicalJson(cases.map(row => row.control_class)) !== canonicalJson([
        "truth-table", "truth-table", "truth-table", "other-date", "other-type",
      ]) ||
      canonicalJson(cases.map(row => row.expected_boolean)) !== canonicalJson([true, false, false, true, true])) {
    fail("OBLIGATION_MISMATCH", "derivation", "R4 authored case identity, class or expected denominator differs");
  }
  const [zero, one, two, otherDate, otherType] = fixture.cases;
  const date = zero!.input.periodEnd;
  const matching = { type: "MAKEUP_APPLIED", date };
  if (fixture.cases.some(row => row.input.periodEnd !== date || row.input.totalAppliedMakeup !== 100 || row.input.totalPayout !== 0) ||
      zero!.input.existingTransactions.length !== 0 ||
      canonicalJson(one!.input.existingTransactions) !== canonicalJson([matching]) ||
      canonicalJson(two!.input.existingTransactions) !== canonicalJson([matching, matching]) ||
      otherDate!.input.existingTransactions.length !== 1 ||
      otherDate!.input.existingTransactions[0]!.type !== "MAKEUP_APPLIED" ||
      otherDate!.input.existingTransactions[0]!.date === date ||
      otherType!.input.existingTransactions.length !== 1 ||
      otherType!.input.existingTransactions[0]!.type === "MAKEUP_APPLIED" ||
      otherType!.input.existingTransactions[0]!.date !== date) {
    fail("FIXTURE_DIGEST_STALE", "derivation", "R4 fixture control roles or otherwise-eligible premise differ");
  }
  const inputDigest = digestValue({ graph_handle: derivation.graph_handle, binding_ref: bindingRef,
    semantic_ref: semanticRef, fixture_ref: fixtureRef, algorithm_ref: algorithmRef,
    selected_case_ids: cases.map(row => row.case_id) });
  const outputDigest = digestValue({ obligation_id: R4_IDENTITY.obligation_id, cases,
    authority_effect: "none", claim_ceiling: CEILING });
  return { schema_version: "tde.r4-authored-case-projection/v1-candidate", owner: "TDE",
    source_kind: "exact-authored-truth-table", graph_handle: derivation.graph_handle,
    binding_ref: bindingRef, semantic_ref: semanticRef, fixture_ref: fixtureRef,
    algorithm_ref: algorithmRef, obligation_id: R4_IDENTITY.obligation_id,
    cases, input_digest: inputDigest, output_digest: outputDigest,
    authority_effect: "none", claim_ceiling: CEILING };
}

/** Recompute from selected current source; caller-held digests cannot self-attest. */
export function replayR4CaseProjection(repoRoot: string, candidate: unknown): R4CaseProjection {
  const current = deriveR4CaseProjection(repoRoot);
  if (canonicalJson(candidate) !== canonicalJson(current)) {
    fail("RECEIPT_TAMPERED", "derivation", "R4 candidate projection differs from exact current source replay");
  }
  return current;
}
