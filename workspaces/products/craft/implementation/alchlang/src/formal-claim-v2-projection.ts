import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import { FORMAL_IDENTITY_ALGORITHM_BYTES, FORMAL_IDENTITY_ALGORITHM_V3_BYTES, lowerApplicationFormalClaims, type ExactFormalSourceRef } from "./formal-claim-lowering.js";

type JsonObject = Record<string, unknown>;
const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical((value as JsonObject)[key])}`).join(",")}}`;
  return JSON.stringify(value);
};
const fail = (code: string, path: string, message: string): never => { throw new CompilationRejected([{ code, path, message }]); };
const currentRef = (path: string, bytes: string): ExactFormalSourceRef => ({ path, sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes), current: true });
const preservationRef = (ref: ExactFormalSourceRef) => ({ path: ref.path, sha256: ref.sha256, size_bytes: ref.size_bytes });

function signatureStrings(signature: {
  sorts: Array<{ name: string }>;
  functions: Array<{ name: string; parameter_sorts: string[]; result_sort: string }>;
  predicates: Array<{ name: string; parameter_sorts: string[] }>;
  constants: Array<{ name: string; sort: string }>;
}): string[] {
  return [
    ...signature.sorts.map(item => `sort ${item.name}`),
    ...signature.functions.map(item => `function ${item.name}(${item.parameter_sorts.join(",")}) -> ${item.result_sort}`),
    ...signature.predicates.map(item => `predicate ${item.name}(${item.parameter_sorts.join(",")})`),
    ...signature.constants.map(item => `constant ${item.name}: ${item.sort}`),
  ];
}

/**
 * Projects the current AlchLang v4 FormalClaim subset into the current v2 TDE
 * intake. The target is an immutable compatibility view, never a second claim.
 */
export function projectApplicationFormalClaimsToV2(
  source: string,
  formalInput: unknown,
  sources: ReadonlyMap<string, Buffer>,
) {
  const formal = lowerApplicationFormalClaims(source, formalInput, sources);
  const files: Record<string, string> = {}; const payloads: JsonObject[] = []; const projections: JsonObject[] = [];
  const preservationBindings: JsonObject[] = []; const attachedSources: JsonObject[] = []; const declarations: JsonObject[] = [];
  for (const [index, claim] of formal.claims.entries()) {
    const declaration = formal.model.formal_claims[index];
    if (!declaration) fail("FORMAL_V2_PROJECTION_COVERAGE", "$formal", "lowered claim has no source declaration");
    if (claim.schema_version !== "domainspec-v2.formal-claim-source/v4-candidate" ||
        claim.tde_compatibility.current_intake_contract !== "FormalClaimSourcePayload/v2" ||
        claim.tde_compatibility.status !== "adapter-required" || claim.tde_compatibility.v2_projection_ref !== null ||
        claim.interpretation_boundary.interpretation_model_is_part_of_claim !== false ||
        claim.interpretation_boundary.join_stage !== "external-evaluation-context") {
      fail("FORMAL_V2_PROJECTION_SOURCE", `$claim:${declaration.id}`, "source is not the current unprojected v4 boundary");
    }
    const sourcePath = `formalization/claims/${declaration.id}.json`; const sourceBytes = formal.files[sourcePath];
    if (!sourceBytes) fail("FORMAL_V2_PROJECTION_COVERAGE", `$claim:${declaration.id}`, "missing exact v4 source bytes");
    const sourceRef = currentRef(sourcePath, sourceBytes);
    const algorithmDigest = claim.canonical_proposition.identity_algorithm_ref.sha256;
    const algorithmVersion = algorithmDigest === digest(FORMAL_IDENTITY_ALGORITHM_V3_BYTES) ? "3"
      : algorithmDigest === digest(FORMAL_IDENTITY_ALGORITHM_BYTES) ? "1"
      : fail("FORMAL_V2_PROJECTION_ALGORITHM", `$claim:${declaration.id}`, "unsupported exact identity algorithm");
    const signature = signatureStrings(claim.formal_signature);
    if (!signature.length || new Set(signature).size !== signature.length) fail("FORMAL_V2_PROJECTION_SIGNATURE", `$claim:${declaration.id}`, "formal signature encoding is empty or ambiguous");
    const theory = `formal-language-profile ${claim.formal_language_profile_ref.path} sha256:${claim.formal_language_profile_ref.sha256}`;
    const definitionImport = `definition-binding ${claim.definition_binding_ref.path} sha256:${claim.definition_binding_ref.sha256}`;
    const environmentWithoutDigest = {
      environment_id: `V4ProjectionEnvironment:${claim.claim.claim_id}@${claim.claim.claim_version}`,
      signature,
      theories: [theory], imports: [definitionImport], assumptions: [] as string[], universe_bindings: {},
      configuration_bindings: {
        "formal-claim-identity-inputs-sha256": claim.claim.identity_inputs_digest,
        "interpretation-model-is-part-of-claim": "false",
        "interpretation-model-join-stage": "external-evaluation-context",
        "source-authority-count": String(claim.source_authority_count),
      },
      model_profile_bindings: [] as Array<{ id: string; version: string; digest: string }>,
    };
    const interpretationEnvironment = { environment_id: environmentWithoutDigest.environment_id,
      environment_digest: digest(canonical(environmentWithoutDigest)), signature: environmentWithoutDigest.signature,
      theories: environmentWithoutDigest.theories, imports: environmentWithoutDigest.imports,
      assumptions: environmentWithoutDigest.assumptions, universe_bindings: environmentWithoutDigest.universe_bindings,
      configuration_bindings: environmentWithoutDigest.configuration_bindings, model_profile_bindings: environmentWithoutDigest.model_profile_bindings };
    const payload = { schema_version: "domainspec-v2.formal-claim-source-payload/v2",
      claim: { claim_id: claim.claim.claim_id, claim_version: claim.claim.claim_version, owner: claim.claim.owner,
        currentness: claim.claim.currentness, supersedes: claim.claim.supersedes, source_digest: sourceRef.sha256 },
      business_binding: { business_meaning_ref: claim.business_meaning_ref.path,
        business_meaning_digest: claim.business_meaning_ref.sha256, relation: "formalizes",
        acceptance_ref: claim.business_acceptance_ref.path, acceptance_digest: claim.business_acceptance_ref.sha256 },
      formal_language_profile: { formal_language_profile_ref: claim.formal_language_profile_ref.path,
        profile_digest: claim.formal_language_profile_ref.sha256 },
      canonical_proposition: { representation_media_type: claim.canonical_proposition.representation_media_type,
        representation: claim.canonical_proposition.representation, representation_digest: claim.canonical_proposition.representation_digest,
        semantic_identity: claim.canonical_proposition.semantic_identity, semantic_identity_digest: claim.canonical_proposition.semantic_identity_digest,
        identity_algorithm: { id: "alchlang.formal-identity-algorithm",
          version: algorithmVersion, digest: algorithmDigest } },
      interpretation_environment: interpretationEnvironment, claim_ceiling: claim.claim_ceiling, authority_effect: "none" };
    const prefix = `formalization/v2-projections/${symbol(declaration.id)}`;
    const payloadPath = `${prefix}/formal-claim-source-payload.v2.json`; const payloadBytes = json(payload); files[payloadPath] = payloadBytes;
    const targetRef = currentRef(payloadPath, payloadBytes);
    const knownLosses = [
      "v2 has no first-class definition_binding_ref field; its exact path and digest remain in interpretation_environment.imports and the projection record",
      "v2 flattens the structured v4 formal_signature into a deterministic reversible string set",
      "v2 has no first-class interpretation_boundary field; its exact values remain in configuration_bindings and the projection record",
      "v2 exact leaf references omit v4 size/current fields; the projection record retains the exact current source references",
      "v2 omits the v4 tde_compatibility wrapper because the target artifact is that compatibility view",
    ];
    const projection = { schema_version: "alchlang.formal-claim-v4-v2-projection/v1-candidate",
      projection_id: `FormalClaimV2Projection:${claim.claim.claim_id}@${claim.claim.claim_version}`,
      source_ref: sourceRef, target_ref: targetRef, source_identity_inputs_digest: claim.claim.identity_inputs_digest,
      mapping: { claim_identity: "copied-exactly; source_digest binds exact v4 bytes",
        business_binding: "v4 exact meaning/acceptance paths and digests copied without dereference or rewrite",
        formal_language_profile: "v4 exact profile path and digest copied",
        canonical_proposition: "representation and semantic identity copied byte-for-byte with exact digests",
        formal_signature: "deterministic reversible declaration strings in v2 interpretation_environment.signature",
        definition_binding: "exact v4 path and digest encoded as one v2 interpretation_environment import",
        interpretation_boundary: "external-evaluation-context separation retained as exact configuration bindings",
        claim_ceiling: "copied exactly" },
      preserved_semantics: ["claim identity", "accepted business binding", "definition dependency binding", "formal-language profile",
        "formal signature", "canonical proposition representation and semantic identity", "external interpretation boundary", "claim ceiling"],
      known_losses: knownLosses, semantic_loss_count: 0, representation_change_count: knownLosses.length,
      currentness: "current", authority_effect: "none",
      claim_ceiling: "v4-to-v2 compatibility projection only; no evaluation, proof, admission, execution or authority" };
    const projectionPath = `${prefix}/projection.json`; const projectionBytes = json(projection); files[projectionPath] = projectionBytes;
    const projectionRef = currentRef(projectionPath, projectionBytes);
    const preservation = { schema_version: "domainspec-v2.preservation-binding/v1-candidate",
      binding_id: `PreservationBinding:${claim.claim.claim_id}@${claim.claim.claim_version}:v4-to-v2`,
      owner: "projects/domainspec-v2/formalization", projection_ref: preservationRef(projectionRef), direction: "source-to-projection",
      kind: "syntactic-by-construction", preserved_semantics: projection.preserved_semantics, known_losses: knownLosses,
      unsupported_constructs: [] as string[], validation_method: "deterministic field mapping plus exact source/target currentness and semantic mutation rejection",
      certificate_ref: null, status: "preserved", authority_effect: "none",
      claim_ceiling: "compatibility-shape preservation only; no proof, evaluation, provider admission or authority" };
    const preservationPath = `${prefix}/preservation-binding.json`; const preservationBytes = json(preservation); files[preservationPath] = preservationBytes;
    const preservationBindingRef = currentRef(preservationPath, preservationBytes);
    const attached: any = structuredClone(claim);
    attached.tde_compatibility = { current_intake_contract: "FormalClaimSourcePayload/v2", status: "v2-projection-attached", v2_projection_ref: targetRef };
    const attachedPath = `${prefix}/formal-claim-source.v4-with-projection.json`; const attachedBytes = json(attached); files[attachedPath] = attachedBytes;
    const attachedRef = currentRef(attachedPath, attachedBytes);
    payloads.push(payload); projections.push(projection); preservationBindings.push(preservation); attachedSources.push(attached);
    declarations.push({ source_id: declaration.id, source_line: declaration.source_line, source_ref: sourceRef, target_ref: targetRef,
      projection_ref: projectionRef, preservation_binding_ref: preservationBindingRef, attached_source_ref: attachedRef,
      source_identity_inputs_digest: claim.claim.identity_inputs_digest, semantic_loss_count: 0,
      representation_change_count: knownLosses.length });
  }
  const trace = { schema_version: "alchlang.formal-claim-v4-v2-projection-trace/v1-candidate",
    source_sha256: digest(source), formal_claim_trace_sha256: digest(json(formal.trace)), declarations,
    meaning_repaired_or_invented: false, provider_execution_observed: false, authority_effect: "none" };
  files["formalization/v2-projections/trace.json"] = json(trace);
  return { formal, payloads, projections, preservation_bindings: preservationBindings, attached_sources: attachedSources, files, trace };
}

export function assertApplicationFormalClaimV2ProjectionCurrent(
  source: string,
  formalInput: unknown,
  sources: ReadonlyMap<string, Buffer>,
  candidate: unknown,
): void {
  if (json(candidate) !== json(projectApplicationFormalClaimsToV2(source, formalInput, sources))) {
    fail("FORMAL_V2_PROJECTION_STALE", "$candidate", "projection differs from exact current v4 source, mapping contract, or referenced inputs");
  }
}
