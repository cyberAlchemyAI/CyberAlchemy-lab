import { createHash } from "node:crypto";
import { joinApplicationEvfCaseClaims } from "./application-evf-case-claims.js";
import { assertApplicationNativeCasesCurrent, type NativeCaseObservationInput } from "./application-native-case-observation.js";
import { CompilationRejected } from "./model.js";

type JsonObject = Record<string, unknown>;

export interface NativeCaseClaimLinkInput {
  case_claim_input: unknown;
  native_input: NativeCaseObservationInput;
  native_receipt: unknown;
}

const fail = (code: string, path: string, message: string): never => {
  throw new CompilationRejected([{ code, path, message }]);
};
const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const item = value as JsonObject;
    return `{${Object.keys(item).sort().map(key => `${JSON.stringify(key)}:${canonical(item[key])}`).join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
};
const same = (left: unknown, right: unknown): boolean => canonical(left) === canonical(right);
const sha = (value: string): string => createHash("sha256").update(value).digest("hex");
const object = (value: unknown, path: string): JsonObject => {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("APPLICATION_NATIVE_LINK_INPUT", path, "expected object");
  return value as JsonObject;
};
const array = (value: unknown, path: string): unknown[] => {
  if (!Array.isArray(value)) fail("APPLICATION_NATIVE_LINK_INPUT", path, "expected array");
  return value as unknown[];
};
const ref = (value: unknown, path: string): JsonObject => {
  const item = object(value, path);
  if (!same(Object.keys(item).sort(), ["path", "sha256", "size_bytes", "current"].sort()) ||
      typeof item.path !== "string" || !item.path || typeof item.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/.test(item.sha256) || !Number.isSafeInteger(item.size_bytes) ||
      (item.size_bytes as number) < 1 || item.current !== true) {
    fail("APPLICATION_NATIVE_LINK_REF", path, "expected current exact reference");
  }
  return item;
};
const snapshot = (sources: ReadonlyMap<string, Buffer>): Map<string, Buffer> =>
  new Map([...sources].map(([key, bytes]) => [key, Buffer.from(bytes)]));
const assertUnchanged = (sources: ReadonlyMap<string, Buffer>, before: ReadonlyMap<string, Buffer>, input: unknown, inputBefore: string): void => {
  if (canonical(input) !== inputBefore) {
    fail("APPLICATION_NATIVE_LINK_INPUT_MUTATED", "$input", "caller input changed during replay");
  }
  if (sources.size !== before.size || [...before].some(([key, bytes]) => {
    const current = sources.get(key);
    return !current || !current.equals(bytes);
  })) fail("APPLICATION_NATIVE_LINK_SOURCE_MUTATED", "$sources", "source map or Buffer changed during replay");
};

/** Compares unverified v3 reports with replayed trusted-local outputs.
 * Agreement is not provider execution, oracle truth, or an EVF vote. */
export async function linkApplicationNativeCaseClaims(input: NativeCaseClaimLinkInput, sources: ReadonlyMap<string, Buffer>) {
  const root = object(input, "$input");
  if (!same(Object.keys(root).sort(), ["case_claim_input", "native_input", "native_receipt"].sort())) {
    fail("APPLICATION_NATIVE_LINK_INPUT", "$input", "unexpected or missing property");
  }
  const inputBefore = canonical(input);
  const before = snapshot(sources);
  try {
    const v3 = joinApplicationEvfCaseClaims(root.case_claim_input, sources);
    assertUnchanged(sources, before, input, inputBefore);
    await assertApplicationNativeCasesCurrent(root.native_input as NativeCaseObservationInput, sources, root.native_receipt);
    assertUnchanged(sources, before, input, inputBefore);

    const claimInput = object(root.case_claim_input, "$input/case_claim_input");
    const bindings = object(claimInput.bindings, "$input/case_claim_input/bindings");
    const receipt = object(root.native_receipt, "$input/native_receipt");
    const requestRef = ref(claimInput.evaluation_request_ref, "$input/case_claim_input/evaluation_request_ref");
    const nativeRequestRef = ref(receipt.finalized_request_ref, "$input/native_receipt/finalized_request_ref");
    const nativeInputRequestRef = ref(object(root.native_input, "$input/native_input").finalized_request_ref,
      "$input/native_input/finalized_request_ref");
    const obligationRef = ref(bindings.obligation_set_ref, "$input/case_claim_input/bindings/obligation_set_ref");
    const runtimeRef = ref(bindings.runtime_binding_ref, "$input/case_claim_input/bindings/runtime_binding_ref");
    const scope = object(object(v3.evf_join.bindings, "$v3/bindings").finalized_scope, "$v3/finalized_scope");
    if (!same(requestRef, nativeRequestRef) || !same(requestRef, nativeInputRequestRef) ||
        !same(obligationRef, receipt.obligation_set_ref) || !same(obligationRef, scope.obligation_set_ref) ||
        !same(runtimeRef, receipt.runtime_ref) ||
        receipt.case_domain_sha256 !== scope.case_domain_sha256 ||
        receipt.witness_input_set_sha256 !== scope.witness_input_set_sha256) {
      fail("APPLICATION_NATIVE_LINK_SCOPE", "$input", "request, obligation, runtime, case or witness scope differs");
    }
    if (receipt.evf_join !== "forbidden" || receipt.can_satisfy_obligation !== false ||
        receipt.runtime_guarantees_observed !== false || receipt.provider_equivalence !== "unverified" ||
        v3.causal_join.domain_join_status !== "BLOCKED" || v3.causal_join.can_satisfy_obligation !== false) {
      fail("APPLICATION_NATIVE_LINK_CEILING", "$input", "source attempted satisfaction or provider promotion");
    }
    const claims = array(claimInput.case_claims, "$input/case_claim_input/case_claims")
      .map((value, index) => object(value, `$input/case_claim_input/case_claims/${index}`));
    const observations = array(receipt.observations, "$input/native_receipt/observations")
      .map((value, index) => object(value, `$input/native_receipt/observations/${index}`));
    if (claims.length !== receipt.selected_case_count || observations.length !== receipt.observed_case_count ||
        observations.length > claims.length || !same(claims.map(row => row.case_id),
          claims.map(row => row.case_id).sort((left, right) => String(left).localeCompare(String(right))))) {
      fail("APPLICATION_NATIVE_LINK_DOMAIN", "$input", "case counts or sorted case domain differ");
    }
    const rows = observations.map((observed, index) => {
      const claimed = claims[index]!;
      if (observed.obligation_id !== claimed.obligation_id || observed.case_id !== claimed.case_id ||
          observed.witness_input_digest !== claimed.witness_input_digest) {
        fail("APPLICATION_NATIVE_LINK_DOMAIN", `$input/native_receipt/observations/${index}`,
          "obligation, case, order or witness identity differs");
      }
      const consistent = same(claimed.reported_native_output, observed.native_output);
      return { obligation_id: observed.obligation_id as string, case_id: observed.case_id as string,
        witness_input_digest: observed.witness_input_digest as string,
        case_claim_ref: ref(claimed.artifact_ref, `$input/case_claim_input/case_claims/${index}/artifact_ref`),
        local_input_sha256: observed.input_sha256 as string,
        local_stdout_sha256: observed.native_output_sha256 as string,
        reported_output_sha256: sha(canonical(claimed.reported_native_output)),
        local_output_sha256: sha(canonical(observed.native_output)), consistent };
    });
    const conflicts = rows.filter(row => !row.consistent).map(row => row.case_id);
    const complete = receipt.execution_status === "complete" && receipt.incomplete_case === null &&
      observations.length === claims.length && receipt.local_execution_observed === true;
    if (receipt.execution_status !== "complete" && receipt.execution_status !== "incomplete") {
      fail("APPLICATION_NATIVE_LINK_STATUS", "$input/native_receipt", "invalid replayed execution status");
    }
    const comparison_status = conflicts.length ? "contradicted" : !complete ? "incomplete" : "claim-vs-local-output-consistent";
    return { schema_version: "alchlang.native-case-claim-link/v1-candidate" as const,
      comparison_status, domain_join_status: "BLOCKED" as const, can_satisfy_obligation: false as const,
      evaluation_request_ref: requestRef, obligation_set_ref: obligationRef, runtime_ref: runtimeRef,
      local_adapter_ref: receipt.local_adapter_ref, local_executable_ref: receipt.local_executable_ref,
      case_domain_sha256: scope.case_domain_sha256, witness_input_set_sha256: scope.witness_input_set_sha256,
      selected_case_count: claims.length, observed_case_count: observations.length, rows,
      conflicting_case_ids: conflicts, incomplete_case: receipt.incomplete_case,
      case_evidence_verification: "unverified" as const, provider_equivalence: "unverified" as const,
      executable_oracle: "unverified" as const, network_enforcement: "unverified" as const,
      memory_enforcement: "unverified" as const, runtime_guarantees_observed: false as const,
      evf_artifact_emitted: false as const, provider_pass_established: false as const,
      authority_effect: "none" as const, release_admission: "not-granted" as const,
      residue: ["v3 case claims are caller-reported", "local adapter output is not provider-authenticated",
        "output agreement does not establish oracle truth", "network and memory enforcement unverified",
        "EVF satisfaction and runtime_guarantees_observed forbidden"],
      claim_ceiling: "Replayed trusted-local output compared with unverified case claims only; no provider, oracle, EVF or runtime-guarantee claim" };
  } finally {
    assertUnchanged(sources, before, input, inputBefore);
  }
}
