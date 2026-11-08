import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import test from "node:test";
import { assertApplicationEvfEvidenceCurrent, joinApplicationEvfEvidence, type ApplicationEvfCausalOutcome } from "../src/application-evf-evidence.js";
import { finalizeApplicationExecutionRequest } from "../src/application-execution-request.js";
import { assertApplicationRuntimeObservationsCurrent, joinApplicationRuntimeObservations, type ApplicationRuntimeStageKey } from "../src/application-runtime-observation.js";
import { assertApplicationVerificationProfilesCurrent, lowerApplicationVerificationProfiles } from "../src/application-verification-profile.js";
import { assertApplicationFormalClaimV2ProjectionCurrent, projectApplicationFormalClaimsToV2 } from "../src/formal-claim-v2-projection.js";
import { formalLoweringFixture, source as formalSource } from "./fixtures/formal-lowering-fixture.js";

const sha = (bytes: string | Buffer) => createHash("sha256").update(bytes).digest("hex");
const canonical = (value: any): string => Array.isArray(value) ? `[${value.map(canonical).join(",")}]` : value && typeof value === "object" ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}` : JSON.stringify(value);
const outcomes: ApplicationEvfCausalOutcome[] = ["pass", "fail", "unknown", "timeout", "malformed", "stale", "unavailable", "not-evaluable"];
const stageMap = { application_commit: "application-committed", provider_acceptance: "provider-accepted",
  transport_delivery: "transport-delivered", business_completion: "business-completed" } as const;
const stageKeys = Object.keys(stageMap) as ApplicationRuntimeStageKey[];

const profileBody = (provider: string) => `
verification-profile EligibleVerification:
  claim EligibleClaim
  context EvaluationContext:eligible-e05 version 1
  interpretation none
  route route:tde-execution
  provider ${provider}
  runtime runtime:e05
  timeout-ms 5000
  memory-ceiling-bytes 268435456
  max-output-bytes 1048576
  network forbidden
  working-directory sandbox/verification
  limit "Synthetic E05 request formation only."
  ceiling "Synthetic E05 evidence only."
`;

function verificationFixture(provider = "provider:e05-a", sourceBase = formalSource) {
  const fixture = formalLoweringFixture(); const source = sourceBase + profileBody(provider);
  const routeRef = fixture.put("fixture/e05-route.json", { route_id: "route:tde-execution" });
  const providerRef = fixture.put(`fixture/${provider.replaceAll(":", "-")}.json`, {
    provider_owner: "fixture-provider-owner", provider_id: provider, provider_version: "1",
  });
  const runtimeRef = fixture.put("fixture/e05-runtime.json", {
    schema_version: "domainspec-v2.provider-runtime-binding/v1-candidate", runtime_binding_id: "runtime:e05",
    provider_owner: "fixture-provider-owner", provider_id: provider, provider_version: "1",
    provider_digest: sha(provider), profile_ref: providerRef, input_artifact_ref: routeRef,
    command: ["fixture-provider"], working_directory: "sandbox/verification", environment_allowlist: [], fixture_refs: [],
    limits: { timeout_ms: 5000, memory_ceiling_bytes: 268435456, max_output_bytes: 1048576 },
    network: "forbidden", supported_outcomes: ["passed", "failed"], currentness: "current",
    authority_effect: "none", claim_ceiling: "runtime-binding-only-no-execution-claim",
  });
  const formal = { ...fixture.input, source_sha256: sha(source) };
  const input: any = { schema_version: "alchlang.verification-profile-bindings/v1", source_sha256: sha(source), owner: "fixture-owner", formal,
    verification_profiles: { EligibleVerification: { interpretation: null,
      route: { selector: "route:tde-execution", ref: routeRef }, provider: { selector: provider, ref: providerRef },
      runtime: { selector: "runtime:e05", ref: runtimeRef } } } };
  return { ...fixture, source, input, formal, providerRef, runtimeRef, routeRef };
}

function evfFixture(outcome: ApplicationEvfCausalOutcome, provider = "provider:e05-a") {
  const fixture = verificationFixture(provider);
  const verification = lowerApplicationVerificationProfiles(fixture.source, fixture.input, fixture.sources);
  const projection = projectApplicationFormalClaimsToV2(fixture.source, fixture.formal, fixture.sources);
  for (const [path, bytes] of Object.entries({ ...verification.formal.files, ...verification.files, ...projection.files })) fixture.sources.set(path, Buffer.from(bytes));
  const verificationTrace = verification.trace.declarations[0]! as any;
  const projectionTrace = projection.trace.declarations[0]! as any;
  const capabilityPolicyRef = fixture.put("fixture/e05-capability-policy.json", { policy_id: "synthetic-e05-policy" });
  const capabilityRef = fixture.put("fixture/e05-capability.json", {
    schema_version: "domainspec-v2.formal-claim-capability-assessment/v1-candidate", assessment_id: "e05-assessment",
    owner: "validation-governance", formal_claim_ref: verificationTrace.claim_ref, policy_ref: capabilityPolicyRef,
    classification: "executable-bounded", needs_formal_reasons: [], admitted_for_tde_execution: true,
    provider_route: "tde", currentness: "current", authority_effect: "none",
    claim_ceiling: "classification-and-routing-only-no-execution-claim",
  });
  const environmentRef = fixture.put("fixture/e05-environment.json", { environment_id: "e05-loopback" });
  let obligationSetRef: any = fixture.put("fixture/e05-obligation-set.json", { obligations: ["e05-obligation"] });
  let projectionRef: any = projectionTrace.target_ref;
  let preservationRef: any = projectionTrace.preservation_binding_ref;
  let evaluationRequestRef: any = verificationTrace.request_ref;
  let finalizedScope: Record<string, unknown> | undefined;
  if (outcome === "pass") {
    const acceptedContextRef = fixture.put("fixture/e05-accepted-context.json", { ...verification.contexts[0], status: "accepted" });
    const baseRequestRef = fixture.put("fixture/e05-accepted-base-request.json", {
      ...verification.requests[0], evaluation_context_ref: acceptedContextRef,
    });
    const derivationProfileRef = fixture.put("fixture/e05-derivation-profile.json", { profile_id: "e05-synthetic-TDE" });
    obligationSetRef = fixture.put("fixture/e05-finalized-obligation-set.json", {
      schema_version: "domainspec-v2.neutral-obligation-set/v1-candidate", obligation_set_id: "e05-set", owner: "TDE",
      formal_claim_ref: verificationTrace.claim_ref,
      capability_assessment_ref: { path: capabilityRef.path, sha256: capabilityRef.sha256, size_bytes: capabilityRef.size_bytes },
      projection_ref: null, derivation_profile_ref: derivationProfileRef, derivation_status: "derived",
      obligations: [{ obligation_id: "e05-obligation", case_id: "e05-case", kind: "property",
        normalized_inputs: { value: "synthetic" }, expected_relation_or_oracle: "holds", source_basis: ["FormalClaim:e05"],
        case_class: "positive", status: "ready", claim_ceiling: "Synthetic E05 evidence only." }],
      residue: [], determinism: { algorithm_ref: derivationProfileRef, input_digest: sha("input"), output_digest: sha("output") },
      authority_effect: "none", claim_ceiling: "Synthetic E05 evidence only.",
    });
    projectionRef = fixture.put("fixture/e05-finalized-projection.json", {
      schema_version: "domainspec-v2.formalization-projection/v1-candidate", projection_id: "e05-projection",
      owner: "projects/domainspec-v2/formalization", formal_claim_ref: verificationTrace.claim_ref,
      capability_assessment_ref: capabilityRef, obligation_set_ref: obligationSetRef,
      purpose: "tde-executable-slice", target_profile_ref: derivationProfileRef,
      source_semantics_digest: sha("source"), projected_semantics_digest: sha("projected"),
      domain_and_bound: "one finite synthetic E05 case", preservation_kind: "exact-equivalent",
      currentness: "current", authority_effect: "none", claim_ceiling: "Synthetic E05 evidence only.",
    });
    preservationRef = fixture.put("fixture/e05-finalized-preservation.json", {
      schema_version: "domainspec-v2.preservation-binding/v1-candidate", binding_id: "e05-preservation",
      owner: "projects/domainspec-v2/formalization",
      projection_ref: { path: projectionRef.path, sha256: projectionRef.sha256, size_bytes: projectionRef.size_bytes },
      direction: "bidirectional", kind: "review-backed", preserved_semantics: ["synthetic finite case"],
      known_losses: [], unsupported_constructs: [], validation_method: "synthetic fixture", certificate_ref: null,
      status: "preserved", authority_effect: "none", claim_ceiling: "Synthetic E05 evidence only.",
    });
    const finalized = finalizeApplicationExecutionRequest({ base_request_ref: baseRequestRef,
      obligation_set_ref: obligationSetRef, projection_ref: projectionRef, preservation_binding_ref: preservationRef }, fixture.sources);
    evaluationRequestRef = fixture.put("fixture/e05-finalized-execution-request.json", finalized);
    finalizedScope = { formal_claim_ref: verificationTrace.claim_ref, evaluation_context_ref: finalized.evaluation_context_ref,
      interpretation_model_ref: finalized.interpretation_model_ref, obligation_set_ref: obligationSetRef,
      projection_ref: projectionRef, preservation_binding_ref: preservationRef,
      case_domain_sha256: finalized.case_domain_sha256, witness_input_set_sha256: finalized.witness_input_set_sha256,
      domain_and_bound_sha256: finalized.domain_and_bound_sha256 };
  }
  const input: any = { schema_version: "alchlang.evf-evidence-input/v1", join_id: `e05-${provider.replaceAll(":", "-")}-${outcome}`,
    route_kind: "execution-evidence", provider: { owner: "fixture-provider-owner", id: provider, version: "1" }, causal_outcome: outcome,
    cause: `synthetic ${outcome} observation`, evaluation_request_ref: evaluationRequestRef,
    comparability: { same_claim: true, same_evaluation_request: true, same_domain: true, same_result_semantics: true },
    result_semantics: "synthetic provider result", claim_ceiling: "Synthetic E05 evidence only.",
    bindings: { formal_claim_ref: verificationTrace.claim_ref, capability_assessment_ref: capabilityRef,
      obligation_ref: fixture.put("fixture/e05-obligation.json", { obligation_id: "e05-obligation" }),
      obligation_set_ref: obligationSetRef,
      projection_ref: projectionRef, preservation_binding_ref: preservationRef,
      native_source_bundle_ref: fixture.put("fixture/e05-native-source.json", { files: ["fixture.native"] }),
      runtime_binding_ref: fixture.runtimeRef, profile_ref: fixture.providerRef, environment_refs: [environmentRef] } };
  const receiptRef: any = fixture.put(`fixture/e05-${provider.replaceAll(":", "-")}-${outcome}.json`, {
    schema_version: finalizedScope ? "alchlang.evf-provider-outcome/v2-candidate" : "alchlang.evf-provider-outcome/v1-candidate", route_kind: input.route_kind,
    provider: input.provider, causal_outcome: outcome, cause: input.cause,
    evaluation_request_ref: input.evaluation_request_ref, comparability: input.comparability,
    result_semantics: input.result_semantics,
    ...(finalizedScope ? { finalized_scope: finalizedScope,
      case_results: [{ obligation_id: "e05-obligation", case_id: "e05-case", normalized_outcome: "passed" }] } : {}),
  });
  if (outcome === "stale") receiptRef.current = false;
  input.provider_receipt_ref = receiptRef;
  return { ...fixture, verification, projection, evfInput: input };
}

function replaceEvfReceipt(fixture: ReturnType<typeof evfFixture>, mutate: (value: any) => void): void {
  const ref = fixture.evfInput.provider_receipt_ref;
  const value = JSON.parse((fixture.sources.get(ref.path) as Buffer).toString("utf8"));
  mutate(value);
  const bytes = Buffer.from(JSON.stringify(value));
  fixture.sources.set(ref.path, bytes);
  ref.sha256 = sha(bytes); ref.size_bytes = bytes.length;
}

function runtimeFixture(observed = new Set<ApplicationRuntimeStageKey>(stageKeys)) {
  const sources = new Map<string, Buffer>();
  const put = (path: string, value: unknown) => { const bytes = Buffer.from(JSON.stringify(value)); sources.set(path, bytes);
    return { path, sha256: sha(bytes), size_bytes: bytes.length, current: true as boolean }; };
  const sourceRef = put("fixture/e05-application.alch", "synthetic application source");
  const graphRef = put("fixture/e05-graph.json", { graph_id: "e05-graph" });
  const providerRef = put("fixture/e05-provider-selection.json", { provider_id: "provider:e05-a" });
  const generatedRefs = [put("fixture/e05-generated.ts", "export const e05 = true;")];
  const environmentRef = put("fixture/e05-runtime-environment.json", { environment_id: "e05-loopback" });
  const orodi = { binding_id: "orodi-binding:e05", observation_selector: "domainspec:integration-observation",
    projection_mapper_ref: "mapping:integration-to-orodi", orodi_adapter_ref: "adapter:orodi-observation", evaluator_ref: "orodi:evaluator",
    disclosure_policy_ref: "disclosure:e05", edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"],
    return_edge: "prohibited", runtime_control_capabilities: { select_retries: false, write_provider_state: false, call_apis: false,
      deploy: false, enact_business_effects: false }, evidence_boundary: "synthetic observation only", authority_effect: "none" };
  const orodiRef = put("fixture/e05-orodi.json", orodi);
  const cleanup = { schema_version: "alchlang.runtime-cleanup-report/v1-candidate", run_id: "e05-run", cleanup_observed: true,
    temporary_resources_removed: true, owned_residue: [], authority_effect: "none", claim_ceiling: "Synthetic resources only." };
  const cleanupRef = put("fixture/e05-cleanup.json", cleanup);
  const stages: any = {};
  for (const key of stageKeys) {
    if (!observed.has(key)) { stages[key] = { runtime_receipt_ref: null, observation_ref: null }; continue; }
    const stage = stageMap[key];
    const receipt = { receipt_id: `receipt:${key}`, binding_ref: "binding:e05", operation_ref: "operation:e05",
      observed_at: "2026-09-20T12:00:00.000Z", observed_stage: stage, outcome: "accepted", provider_evidence_ref: `evidence:${key}`,
      correlation_ref: cleanup.run_id, claim_ceiling: stage, authority_effect: "none" };
    const receiptRef = put(`fixture/e05-receipts/${key}.json`, receipt);
    const observation = { schema_version: "domainspec.integration-observation/v1-candidate", observation_id: `observation:${key}`,
      source_receipt_digest: sha(canonical(receipt)), binding_ref: receipt.binding_ref, operation_ref: receipt.operation_ref, stage,
      outcome: receipt.outcome, observed_at: receipt.observed_at, duration_ms: 1, correlation_ref: receipt.correlation_ref,
      sanitized_attributes: { fixture: true }, evidence_refs: [receipt.provider_evidence_ref], claim_ceiling: stage,
      orodi_binding_ref: orodi.binding_id, immutable: true, authority_effect: "none" };
    stages[key] = { runtime_receipt_ref: receiptRef, observation_ref: put(`fixture/e05-observations/${key}.json`, observation) };
  }
  const input: any = { schema_version: "alchlang.runtime-observation-bindings/v1", join_id: "e05-runtime-join",
    source_ref: sourceRef, compiled_graph_ref: graphRef, provider_selection_ref: providerRef, generated_artifact_refs: generatedRefs,
    runtime_environment_ref: environmentRef, orodi_binding_ref: orodiRef, cleanup_report_ref: cleanupRef, stages,
    claim_ceiling: "Synthetic E05 runtime evidence only." };
  return { input, sources, orodi };
}

test("E05 non-collapse keeps provider selection outside FormalClaim identity while proposition meaning remains identity-bearing", () => {
  const a = verificationFixture("provider:e05-a"); const b = verificationFixture("provider:e05-b");
  const ar = lowerApplicationVerificationProfiles(a.source, a.input, a.sources);
  const br = lowerApplicationVerificationProfiles(b.source, b.input, b.sources);
  assert.equal(ar.formal.claims[0]!.claim.identity_inputs_digest, br.formal.claims[0]!.claim.identity_inputs_digest);
  assert.notEqual((ar.trace.declarations[0]! as any).request_ref.sha256, (br.trace.declarations[0]! as any).request_ref.sha256);
  const changedSource = formalSource.replace("forall o", "exists o"); const changed = verificationFixture("provider:e05-a", changedSource);
  const changedProjection = projectApplicationFormalClaimsToV2(changed.source, changed.formal, changed.sources);
  assert.notEqual(changedProjection.formal.claims[0]!.claim.identity_inputs_digest, ar.formal.claims[0]!.claim.identity_inputs_digest);
});

test("E05 semantic oracle rejects synthetic execution pass and preserves non-pass outcomes", () => {
  for (const outcome of outcomes) {
    const fixture = evfFixture(outcome);
    if (outcome === "pass") {
      assert.throws(() => joinApplicationEvfEvidence(fixture.evfInput, fixture.sources), /APPLICATION_EVF_CASE_OBSERVATION_REQUIRED/);
      continue;
    }
    const result = joinApplicationEvfEvidence(fixture.evfInput, fixture.sources);
    assert.equal((result.causal_join as any).can_satisfy_obligation, false, outcome);
    assert.equal((result.evf_join as any).residue.length, 3, outcome);
  }
  const incomparable = evfFixture("pass"); incomparable.evfInput.comparability.same_result_semantics = false;
  replaceEvfReceipt(incomparable, receipt => { receipt.comparability.same_result_semantics = false; });
  assert.throws(() => joinApplicationEvfEvidence(incomparable.evfInput, incomparable.sources), /APPLICATION_EVF_PASS_GUARD/);
});

test("E05 orthogonality keeps every runtime-stage subset independent from all other stages", () => {
  for (let mask = 0; mask < 16; mask += 1) {
    const selected = new Set(stageKeys.filter((_, index) => (mask & (1 << index)) !== 0));
    const fixture = runtimeFixture(selected); const result = joinApplicationRuntimeObservations(fixture.input, fixture.sources);
    assert.equal((result.join as any).observed_stage_count, selected.size, `mask=${mask}`);
    assert.equal((result.join as any).stage_inference_used, false, `mask=${mask}`);
    for (const key of stageKeys) assert.equal((result.join as any).stages[key].status, selected.has(key) ? "observed" : "not-observed", `${mask}/${key}`);
  }
});

test("E05 property oracle preserves claim identity across the provider-by-causal-outcome product", () => {
  let claimIdentity: string | undefined;
  const requestRefs = new Set<string>();
  for (const provider of ["provider:e05-a", "provider:e05-b"]) for (const outcome of outcomes) {
    const fixture = evfFixture(outcome, provider);
    if (outcome === "pass") {
      assert.throws(() => joinApplicationEvfEvidence(fixture.evfInput, fixture.sources), /APPLICATION_EVF_CASE_OBSERVATION_REQUIRED/);
    }
    const result = outcome === "pass" ? undefined : joinApplicationEvfEvidence(fixture.evfInput, fixture.sources);
    const identity = fixture.verification.formal.claims[0]!.claim.identity_inputs_digest;
    claimIdentity ??= identity; assert.equal(identity, claimIdentity, `${provider}/${outcome}`);
    requestRefs.add((fixture.verification.trace.declarations[0]! as any).request_ref.sha256);
    if (result) assert.equal((result.causal_join as any).causal_outcome, outcome);
  }
  assert.equal(requestRefs.size, 2);
});

test("E05 hostile mutations fail at the layer whose semantic boundary they violate", () => {
  const verification = verificationFixture(); verification.sources.set(verification.providerRef.path, Buffer.from("changed"));
  assert.throws(() => lowerApplicationVerificationProfiles(verification.source, verification.input, verification.sources), /APPLICATION_VERIFICATION_|FORMAL_BINDING_/);
  const projection = verificationFixture(); const projected = projectApplicationFormalClaimsToV2(projection.source, projection.formal, projection.sources);
  const changedProjection = structuredClone(projected); (changedProjection.payloads[0]! as any).claim_ceiling = "widened";
  assert.throws(() => assertApplicationFormalClaimV2ProjectionCurrent(projection.source, projection.formal, projection.sources, changedProjection), /FORMAL_V2_PROJECTION_STALE/);
  const evf = evfFixture("pass"); evf.evfInput.comparability.same_claim = false;
  replaceEvfReceipt(evf, receipt => { receipt.comparability.same_claim = false; });
  assert.throws(() => joinApplicationEvfEvidence(evf.evfInput, evf.sources), /APPLICATION_EVF_PASS_GUARD/);
  const runtime = runtimeFixture(); runtime.input.stages.business_completion = runtime.input.stages.application_commit;
  assert.throws(() => joinApplicationRuntimeObservations(runtime.input, runtime.sources), /APPLICATION_RUNTIME_OBSERVATION_STAGE/);
});

test("E05 determinism is byte-stable across verification, projection, EVF and runtime joins", () => {
  const fixture = evfFixture("unknown"); const runtime = runtimeFixture(new Set(["application_commit", "transport_delivery"]));
  const once = { verification: lowerApplicationVerificationProfiles(fixture.source, fixture.input, fixture.sources),
    projection: projectApplicationFormalClaimsToV2(fixture.source, fixture.formal, fixture.sources),
    evf: joinApplicationEvfEvidence(fixture.evfInput, fixture.sources),
    runtime: joinApplicationRuntimeObservations(runtime.input, runtime.sources) };
  const twice = { verification: lowerApplicationVerificationProfiles(fixture.source, structuredClone(fixture.input), fixture.sources),
    projection: projectApplicationFormalClaimsToV2(fixture.source, structuredClone(fixture.formal), fixture.sources),
    evf: joinApplicationEvfEvidence(structuredClone(fixture.evfInput), fixture.sources),
    runtime: joinApplicationRuntimeObservations(structuredClone(runtime.input), runtime.sources) };
  assert.equal(JSON.stringify(once), JSON.stringify(twice));
});

test("E05 currentness rejects stale exact inputs and semantically changed outputs at every layer", () => {
  const verification = verificationFixture(); const currentVerification = lowerApplicationVerificationProfiles(verification.source, verification.input, verification.sources);
  const changedVerification = structuredClone(currentVerification); (changedVerification.requests[0]! as any).release_admission = "granted";
  assert.throws(() => assertApplicationVerificationProfilesCurrent(verification.source, verification.input, verification.sources, changedVerification), /APPLICATION_VERIFICATION_STALE/);
  const projection = projectApplicationFormalClaimsToV2(verification.source, verification.formal, verification.sources);
  const changedProjection = structuredClone(projection); (changedProjection.projections[0]! as any).semantic_loss_count = 1;
  assert.throws(() => assertApplicationFormalClaimV2ProjectionCurrent(verification.source, verification.formal, verification.sources, changedProjection), /FORMAL_V2_PROJECTION_STALE/);
  const evf = evfFixture("unknown"); const currentEvf = joinApplicationEvfEvidence(evf.evfInput, evf.sources);
  const changedEvf = structuredClone(currentEvf); (changedEvf.causal_join as any).can_satisfy_obligation = true;
  assert.throws(() => assertApplicationEvfEvidenceCurrent(evf.evfInput, evf.sources, changedEvf), /APPLICATION_EVF_STALE/);
  const runtime = runtimeFixture(); const currentRuntime = joinApplicationRuntimeObservations(runtime.input, runtime.sources);
  const changedRuntime = structuredClone(currentRuntime); (changedRuntime.join as any).stage_inference_used = true;
  assert.throws(() => assertApplicationRuntimeObservationsCurrent(runtime.input, runtime.sources, changedRuntime), /APPLICATION_RUNTIME_OBSERVATION_STALE/);
});
