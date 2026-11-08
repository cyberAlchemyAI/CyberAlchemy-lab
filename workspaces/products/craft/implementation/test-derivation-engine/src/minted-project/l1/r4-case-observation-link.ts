import { canonicalJson, digestValue, readJson } from "./exact-ref.js";
import { deriveR4CaseProjection, type R4CaseProjection } from "./r4-case-projection.js";
import { fail, type ExactRef } from "./types.js";
import { replayStoredCurrentR4Receipt, type CurrentR4Receipt } from "./verify-r4-current.js";

const CEILING = "candidate-local-r4-authored-cases-matched-to-replayed-standalone-pure-decision-only";

type Observation = Readonly<{
  case_id: string;
  control_class: "truth-table" | "other-date" | "other-type";
  input_digest: string;
  expected: boolean;
  actual: boolean;
}>;

type Execution = Readonly<{
  schema_version: string;
  fixture_ref: ExactRef;
  observations: readonly Observation[];
  observations_digest: string;
  status: string;
  side_effect_observation: string;
}>;

export type R4CaseObservationLink = Readonly<{
  schema_version: "tde.r4-case-observation-link/v1-candidate";
  owner: "TDE";
  projection_input_digest: string;
  projection_output_digest: string;
  terminal_receipt_ref: ExactRef;
  execution_ref: ExactRef;
  obligation_id: string;
  cases: readonly Readonly<{
    obligation_id: string;
    case_id: string;
    input_digest: string;
    expected_boolean: boolean;
    observed_boolean: boolean;
  }>[];
  matched_cases: 5;
  authority_effect: "none";
  claim_ceiling: typeof CEILING;
  link_digest: string;
}>;

/** Structural join only. Call through deriveR4CaseObservationLink for current replay. */
export function compareR4CaseObservations(projection: R4CaseProjection, execution: Execution):
  R4CaseObservationLink["cases"] {
  if (execution.schema_version !== "evf.financial-settlement-r4-observed-decision/v2" ||
      execution.status !== "pass" || execution.side_effect_observation !== "none-pure-decision-only" ||
      canonicalJson(execution.fixture_ref) !== canonicalJson(projection.fixture_ref) ||
      execution.observations_digest !== digestValue(execution.observations) ||
      execution.observations.length !== projection.cases.length || projection.cases.length !== 5) {
    fail("OBSERVATION_TAMPERED", "execution", "R4 observed decision envelope or case denominator differs");
  }
  return projection.cases.map((item, index) => {
    const observed = execution.observations[index];
    if (!observed || item.obligation_id !== projection.obligation_id ||
        observed.case_id !== item.case_id || observed.control_class !== item.control_class ||
        observed.input_digest !== digestValue(item.normalized_inputs) ||
        observed.expected !== item.expected_boolean || observed.actual !== observed.expected) {
      fail("OBSERVATION_TAMPERED", "execution", `R4 projected case does not match observation at index ${index}`);
    }
    return { obligation_id: item.obligation_id, case_id: item.case_id,
      input_digest: observed.input_digest, expected_boolean: item.expected_boolean,
      observed_boolean: observed.actual };
  });
}

/** Replays the exact stored R4 receipt, then joins its runner-owned observations to current authored cases. */
export async function deriveR4CaseObservationLink(repoRoot: string, terminalReceiptRef: ExactRef):
  Promise<R4CaseObservationLink> {
  const projection = deriveR4CaseProjection(repoRoot);
  await replayStoredCurrentR4Receipt(repoRoot, terminalReceiptRef);
  const receipt = readJson<CurrentR4Receipt>(repoRoot, terminalReceiptRef.path);
  if (canonicalJson(receipt.graph_handle) !== canonicalJson(projection.graph_handle))
    fail("SOURCE_GRAPH_DIGEST_STALE", "receipt", "R4 projection and replayed receipt graph differ");
  const execution = readJson<Execution>(repoRoot, receipt.evidence.execution_ref.path);
  const cases = compareR4CaseObservations(projection, execution);
  const unsigned = {
    schema_version: "tde.r4-case-observation-link/v1-candidate" as const,
    owner: "TDE" as const,
    projection_input_digest: projection.input_digest,
    projection_output_digest: projection.output_digest,
    terminal_receipt_ref: terminalReceiptRef,
    execution_ref: receipt.evidence.execution_ref,
    obligation_id: projection.obligation_id,
    cases,
    matched_cases: 5 as const,
    authority_effect: "none" as const,
    claim_ceiling: CEILING as typeof CEILING,
  };
  return { ...unsigned, link_digest: digestValue(unsigned) };
}

/** Caller-held links cannot attest themselves; replay recomputes current source and execution. */
export async function replayR4CaseObservationLink(repoRoot: string, candidate: unknown,
  terminalReceiptRef: ExactRef): Promise<R4CaseObservationLink> {
  const current = await deriveR4CaseObservationLink(repoRoot, terminalReceiptRef);
  if (canonicalJson(candidate) !== canonicalJson(current))
    fail("RECEIPT_TAMPERED", "receipt", "R4 case-observation link differs from exact current replay");
  return current;
}

