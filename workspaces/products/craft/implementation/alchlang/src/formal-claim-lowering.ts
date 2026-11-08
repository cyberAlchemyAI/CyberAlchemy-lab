import { createHash } from "node:crypto";
import { CompilationRejected } from "./model.js";
import { parseDomainSource } from "./parser.js";
import type { ApplicationFormalSource } from "./formal-claim.js";

type JsonObject = Record<string, unknown>;
export interface ExactFormalSourceRef { path: string; sha256: string; size_bytes: number; current: true }
const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical((value as JsonObject)[key])}`).join(",")}}`;
  return JSON.stringify(value);
};
const sha = (value: string | Buffer) => createHash("sha256").update(value).digest("hex");
const json = (value: unknown) => JSON.stringify(value, null, 2) + "\n";
/** The decision subject excludes the whole acceptance envelope to avoid a circular digest. */
export function businessAcceptanceSubjectDigest(meaning: JsonObject): string {
  return sha(canonical(Object.fromEntries(Object.entries(meaning).filter(([key]) => key !== "acceptance"))));
}
// Exact selected record from DomainSpec formalization/profiles/formal-language-profiles.json.
// Changing that semantic record requires reviewing this parser/profile binding.
export const FOL_CORE_PROFILE_SHA256 = "bc6b15bbe27641b6e5dd7a88774f8c587a52d64359e24a9d2a1bf198c706f856";

export const FORMAL_IDENTITY_ALGORITHM_BYTES = json({
  schema_version: "alchlang.formal-identity-algorithm/v1",
  proposition: "SHA-256 of key-sorted JSON typed fol-core AST; no logical-equivalence or alpha-equivalence claim",
  claim: "SHA-256 of key-sorted JSON {business_meaning_sha256,definition_binding_sha256,formal_profile_sha256,signature,proposition_semantic_identity,claim_ceiling}",
  signature: "Sort declaration arrays by symbol name; preserve callable parameter order",
  definition_closure: "SHA-256 of key-sorted JSON array of exact definition bodies sorted by definition_id",
  excluded_inputs: ["provider", "runtime", "interpretation_model", "execution_bound", "observed_result", "source_whitespace"],
  authority_effect: "none",
});

// BusinessMeaning/v2 carries an InterpretationModel reference for lineage even
// though FormalClaim/v4 assigns that model to an external EvaluationContext.
// Version the algorithm rather than silently changing v1 claim identities.
export const FORMAL_IDENTITY_ALGORITHM_V2_BYTES = json({
  schema_version: "alchlang.formal-identity-algorithm/v2",
  proposition: "SHA-256 of key-sorted JSON typed fol-core AST; no logical-equivalence or alpha-equivalence claim",
  claim: "SHA-256 of key-sorted JSON {business_meaning_semantic_sha256,definition_binding_sha256,formal_profile_sha256,signature,proposition_semantic_identity,claim_ceiling}",
  business_meaning_semantic_sha256: "SHA-256 of key-sorted BusinessMeaning/v2 JSON excluding only interpretation_model_ref",
  signature: "Sort declaration arrays by symbol name; preserve callable parameter order",
  definition_closure: "SHA-256 of key-sorted JSON array of exact definition bodies sorted by definition_id",
  excluded_inputs: ["provider", "runtime", "interpretation_model_ref", "execution_bound", "observed_result", "source_whitespace"],
  authority_effect: "none",
});

// Acceptance decisions bind exact subjects, but their changing envelopes do
// not redefine a FormalClaim proposition. V3 is explicit so persisted V2
// identities are never silently reinterpreted.
export const FORMAL_IDENTITY_ALGORITHM_V3_BYTES = json({
  schema_version: "alchlang.formal-identity-algorithm/v3",
  proposition: "SHA-256 of key-sorted JSON typed fol-core AST; no logical-equivalence or alpha-equivalence claim",
  claim: "SHA-256 of key-sorted JSON {business_meaning_semantic_sha256,definition_binding_sha256,formal_profile_sha256,signature,proposition_semantic_identity,claim_ceiling}",
  business_meaning_semantic_sha256: "SHA-256 of key-sorted BusinessMeaning/v2 JSON excluding acceptance and interpretation_model_ref",
  signature: "Sort declaration arrays by symbol name; preserve callable parameter order",
  definition_closure: "SHA-256 of key-sorted JSON array of exact definition bodies sorted by definition_id",
  excluded_inputs: ["provider", "runtime", "acceptance", "interpretation_model_ref", "execution_bound", "observed_result", "source_whitespace"],
  authority_effect: "none",
});

function fail(code: string, path: string, message: string): never { throw new CompilationRejected([{ code, path, message }]); }
function object(value: unknown, path: string): JsonObject {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("FORMAL_BINDING_SCHEMA", path, "expected object");
  return value as JsonObject;
}
function exact(value: unknown, keys: string[], path: string): JsonObject {
  const result = object(value, path);
  if (canonical(Object.keys(result).sort()) !== canonical(keys.sort())) fail("FORMAL_BINDING_SCHEMA", path, "unexpected or missing property");
  return result;
}
function text(value: unknown, path: string): string {
  if (typeof value !== "string" || !value.trim()) fail("FORMAL_BINDING_SCHEMA", path, "expected nonempty text");
  return value as string;
}
function list(value: unknown, path: string): unknown[] {
  if (!Array.isArray(value)) fail("FORMAL_BINDING_SCHEMA", path, "expected array");
  return value as unknown[];
}
function unique(values: string[], path: string): void {
  if (new Set(values).size !== values.length) fail("FORMAL_BINDING_DUPLICATE", path, "duplicate identity");
}
function digest(value: unknown, path: string): string {
  const result = text(value, path); if (!/^[a-f0-9]{64}$/.test(result)) fail("FORMAL_BINDING_SCHEMA", path, "expected SHA-256"); return result;
}

/** Validate reference metadata before any filesystem access. */
export function validateExactFormalSourceRef(value: unknown, path: string): ExactFormalSourceRef {
  const ref = exact(value, ["path", "sha256", "size_bytes", "current"], path);
  const relative = text(ref.path, path);
  if (relative.startsWith("/") || relative.includes("\\") || relative.includes(":") || relative.split("/").some(p => !p || p === "." || p === "..")) fail("FORMAL_BINDING_PATH", path, "expected bounded relative path");
  const expected = digest(ref.sha256, path);
  if (ref.current !== true || !Number.isSafeInteger(ref.size_bytes) || (ref.size_bytes as number) < 1) fail("FORMAL_BINDING_CURRENTNESS", path, "reference must be current with an exact byte size");
  if (relative.includes("\u0000")) fail("FORMAL_BINDING_PATH", path, "path contains a null byte");
  return { path: relative, sha256: expected, size_bytes: ref.size_bytes as number, current: true };
}

/** Resolves caller-selected immutable inputs. It never fetches files or authorizes acceptance. */
export function resolveExactFormalSource(value: unknown, sources: ReadonlyMap<string, Buffer>, path: string): { ref: ExactFormalSourceRef; bytes: Buffer } {
  const ref = validateExactFormalSourceRef(value, path);
  const relative = ref.path, expected = ref.sha256;
  const bytes = sources.get(relative);
  if (!bytes) fail("FORMAL_BINDING_MISSING", path, `missing ${relative}`);
  if (bytes!.length !== ref.size_bytes || sha(bytes!) !== expected) fail("FORMAL_BINDING_STALE", path, `changed ${relative}`);
  return { ref: { path: relative, sha256: expected, size_bytes: ref.size_bytes as number, current: true }, bytes: Buffer.from(bytes!) };
}
function decode(bytes: Buffer, path: string): JsonObject {
  let value: unknown;
  try { value = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes)); }
  catch { fail("FORMAL_BINDING_JSON", path, "expected UTF-8 JSON"); }
  return object(value, path);
}

function validateMeaning(document: JsonObject, path: string): void {
  const common = ["schema_version", "meaning_id", "version", "owner", "status", "domain_context", "rule", "applies_when", "actors", "inputs", "outcomes", "examples", "counterexamples", "boundaries", "acceptance", "claim_ceiling", "authority_effect"];
  const version = document.schema_version;
  const v2 = version === "domainspec-v2.business-meaning/v2-candidate";
  if (!v2 && version !== "domainspec-v2.business-meaning/v1-candidate") fail("FORMAL_MEANING_SCHEMA", path, "unsupported BusinessMeaning schema");
  const extra = v2 ? ["supersedes", "supersession_effect", "base_accepted_meaning_ref", "definition_source_ref", "interpretation_model_ref", "definition_policy", "definitions"] : Object.hasOwn(document, "supersedes") ? ["supersedes"] : [];
  exact(document, [...common, ...extra], path);
  for (const key of ["meaning_id", "version", "owner", "domain_context", "rule", "claim_ceiling"]) text(document[key], `${path}/${key}`);
  for (const key of ["applies_when", "actors", "inputs", "outcomes", "boundaries"]) {
    const values = list(document[key], path).map(v => text(v, path)); unique(values, path);
  }
  for (const key of ["examples", "counterexamples"]) {
    const cases = list(document[key], path);
    if (!cases.length) fail("FORMAL_MEANING_SCHEMA", path, `${key} cannot be empty`);
    for (const entry of cases) {
      const item = exact(entry, ["case_id", "given", "when", "then", "why"], path);
      Object.values(item).forEach(v => text(v, path));
    }
  }
  exact(document.acceptance, ["status", "owner_ref", "acceptance_ref", "acceptance_digest"], path);
  if (v2) {
    text(document.supersedes, path);
    if (document.supersession_effect !== "accepted-supersession") fail("FORMAL_MEANING_SCHEMA", path, "accepted meaning requires accepted supersession");
    const policy = { canonical_location: "inline-in-this-business-meaning", normative_voice: "formal", explanatory_voices: ["plain_language", "domain_context"], conflict_rule: "formal-voice-prevails" };
    if (canonical(document.definition_policy) !== canonical(policy)) fail("FORMAL_MEANING_SCHEMA", path, "definition policy differs");
    // These lineage/model references remain opaque metadata, not claim-owned interpretation.
    for (const key of ["base_accepted_meaning_ref", "definition_source_ref", "interpretation_model_ref"]) {
      const ref = exact(document[key], ["path", "sha256", "size_bytes", "current"], path);
      text(ref.path, path); digest(ref.sha256, path);
      if (ref.current !== true || !Number.isSafeInteger(ref.size_bytes) || (ref.size_bytes as number) < 1) fail("FORMAL_MEANING_SCHEMA", path, "invalid lineage reference");
    }
    if (!list(document.definitions, path).length) fail("FORMAL_MEANING_SCHEMA", path, "empty inline definitions");
    for (const definition of document.definitions as unknown[]) validateDefinition(object(definition, path), path);
  } else if (Object.hasOwn(document, "supersedes") && document.supersedes !== null) text(document.supersedes, path);
}

function validateDefinition(definition: JsonObject, path: string): void {
  exact(definition, ["definition_id", "term", "definition_kind", "formal", "plain_language", "domain_context", "depends_on", "business_fact_refs", "interpretation_refs", "source_concept_refs", "forbidden_collapses", "status"], path);
  if (!/^[A-Z][A-Z0-9-]+$/.test(text(definition.definition_id, path)) || definition.status !== "accepted") fail("FORMAL_DEFINITION_SCHEMA", path, "expected accepted definition identity");
  for (const key of ["term", "plain_language", "domain_context"]) text(definition[key], path);
  if (!["entity", "value-object", "relation", "predicate", "decision-value", "function", "temporal-value", "revision-value"].includes(String(definition.definition_kind))) fail("FORMAL_DEFINITION_SCHEMA", path, "unsupported definition kind");
  const formal = exact(definition.formal, ["definition", "expression", "notation", "operational_interpretation"], path);
  for (const key of ["definition", "expression", "operational_interpretation"]) text(formal[key], path);
  const notation = list(formal.notation, path);
  if (!notation.length) fail("FORMAL_DEFINITION_SCHEMA", path, "empty formal notation");
  for (const entry of notation) { const n = exact(entry, ["symbol", "meaning"], path); text(n.symbol, path); text(n.meaning, path); }
  for (const key of ["depends_on", "business_fact_refs", "interpretation_refs", "source_concept_refs", "forbidden_collapses"]) {
    const values = list(definition[key], path).map(v => text(v, path)); unique(values, path);
    if (["business_fact_refs", "interpretation_refs", "forbidden_collapses"].includes(key) && !values.length) fail("FORMAL_DEFINITION_SCHEMA", path, `empty ${key}`);
    if (["business_fact_refs", "interpretation_refs"].includes(key) && values.some(v => !v.startsWith("#/"))) fail("FORMAL_DEFINITION_SCHEMA", path, "expected JSON pointer");
  }
}

function definitionClosure(binding: JsonObject, claimId: string, version: string, sources: ReadonlyMap<string, Buffer>, path: string, inlineDefinitions?: unknown[]): void {
  exact(binding, ["schema_version", "binding_id", "claim_identity", "definition_authority_ref", "definition_nodes", "relations", "definition_closure", "resolution_policy", "authority_effect", "claim_ceiling"], path);
  if (binding.schema_version !== "domainspec-v2.formal-claim-definition-binding/v1-candidate" || binding.authority_effect !== "none") fail("FORMAL_DEFINITION_BINDING", path, "invalid definition binding kind");
  const identity = exact(binding.claim_identity, ["claim_id", "claim_version"], path);
  if (identity.claim_id !== claimId || identity.claim_version !== version) fail("FORMAL_DEFINITION_BINDING", path, "claim identity differs");
  const policy = { edge_source: "explicit-author-declaration", name_inference: "forbidden", missing_definition: "block", transitive_dependencies: "required", definition_body_authority: "definition_authority_ref" };
  if (canonical(binding.resolution_policy) !== canonical(policy)) fail("FORMAL_DEFINITION_BINDING", path, "definition resolution policy differs");
  const authority = resolveExactFormalSource(binding.definition_authority_ref, sources, `${path}/authority`);
  const document = decode(authority.bytes, path);
  // A v2 meaning owns its definitions inline. A separate source may be used
  // as an exact projection, but it cannot introduce different canonical bodies.
  if (inlineDefinitions && canonical(document.definitions) !== canonical(inlineDefinitions))
    fail("FORMAL_DEFINITION_AUTHORITY", path, "definition authority differs from accepted inline definitions");
  const definitions = list(document.definitions, `${path}/definitions`).map((d, i) => object(d, `${path}/definitions/${i}`));
  unique(definitions.map(d => text(d.definition_id, path)), path);
  const nodes = list(binding.definition_nodes, path).map(n => exact(n, ["definition_id", "definition_pointer", "status", "definition_digest"], path));
  if (!nodes.length) fail("FORMAL_DEFINITION_BINDING", path, "empty definition closure");
  unique(nodes.map(n => text(n.definition_id, path)), path);
  const resolved = nodes.map(n => {
    const pointer = text(n.definition_pointer, path); const match = /^#\/definitions\/(0|[1-9][0-9]*)$/.exec(pointer);
    if (!match) fail("FORMAL_DEFINITION_POINTER", path, "invalid definition pointer");
    const definition = definitions[Number(match![1])];
    if (!definition || definition.definition_id !== n.definition_id || definition.status !== "accepted" || n.status !== "accepted") fail("FORMAL_DEFINITION_POINTER", path, "definition identity or acceptance differs");
    validateDefinition(definition!, path);
    if (sha(canonical(definition)) !== n.definition_digest) fail("FORMAL_DEFINITION_STALE", path, "definition body changed");
    return definition!;
  });
  const selected = new Set(nodes.map(n => n.definition_id));
  for (const definition of resolved) for (const dependency of list(definition.depends_on, path)) {
    if (!selected.has(text(dependency, path))) fail("FORMAL_DEFINITION_CLOSURE", path, `missing transitive definition ${dependency}`);
  }
  const edges = list(binding.relations, path).map(e => exact(e, ["relation_id", "relation_type", "source_claim_id", "target_definition_id", "definition_pointer", "binding_effect", "inference"], path));
  unique(edges.map(e => text(e.relation_id, path)), path);
  unique(edges.map(e => text(e.target_definition_id, path)), path);
  if (edges.length !== nodes.length) fail("FORMAL_DEFINITION_CLOSURE", path, "every definition requires one explicit edge");
  for (const edge of edges) {
    const node = nodes.find(n => n.definition_id === edge.target_definition_id);
    if (!node || edge.source_claim_id !== claimId || edge.relation_type !== "uses_definition" || edge.definition_pointer !== node.definition_pointer || edge.binding_effect !== "semantic-dependency" || edge.inference !== "explicit") fail("FORMAL_DEFINITION_CLOSURE", path, "invalid or inferred definition edge");
  }
  const closure = exact(binding.definition_closure, ["definition_ids", "canonicalization", "digest_algorithm", "digest"], path);
  const ids = list(closure.definition_ids, path).map(id => text(id, path)); unique(ids, path);
  if (canonical([...ids].sort()) !== canonical([...selected].sort()) || closure.canonicalization !== "domainspec-json-keysort-v1" || closure.digest_algorithm !== "sha256") fail("FORMAL_DEFINITION_CLOSURE", path, "declared closure differs");
  resolved.sort((a, b) => String(a.definition_id) < String(b.definition_id) ? -1 : String(a.definition_id) > String(b.definition_id) ? 1 : 0);
  if (sha(canonical(resolved)) !== closure.digest) fail("FORMAL_DEFINITION_STALE", path, "closure digest differs");
}

/** Emits only the formalization partition; domain/application generation is a separate join. */
export function lowerApplicationFormalClaims(source: string, input: unknown, sources: ReadonlyMap<string, Buffer>) {
  const parsed = parseDomainSource(source);
  if (parsed.carrier.schema_version !== "alchlang.application-source/v1-candidate") fail("FORMAL_SOURCE_PROFILE", "$", "expected application-v1 source");
  const model = parsed.carrier as unknown as ApplicationFormalSource;
  const root = exact(input, ["schema_version", "source_sha256", "owner", "formal_claims"], "$bindings");
  if (root.schema_version !== "alchlang.formal-claim-bindings/v1" || root.source_sha256 !== sha(source) || root.owner !== model.owner) fail("FORMAL_SOURCE_BINDING", "$bindings", "source, owner or binding version differs");
  const bindings = object(root.formal_claims, "$bindings/formal_claims");
  if (canonical(Object.keys(bindings).sort()) !== canonical(model.formal_claims.map(c => c.id).sort())) fail("FORMAL_SOURCE_BINDING", "$bindings", "claim binding coverage differs");
  const files: Record<string, string> = {}; const trace: JsonObject[] = []; const identities = new Set<string>();
  const claims = model.formal_claims.map(declaration => {
    const path = `$bindings/formal_claims/${declaration.id}`;
    const b = exact(bindings[declaration.id], ["claim_id", "claim_version", "supersedes", "business_meaning_ref", "business_acceptance_ref", "definition_binding_ref", "formal_language_profile_ref", "identity_algorithm_ref"], path);
    const claimId = text(b.claim_id, path); const version = text(b.claim_version, path);
    const identity = canonical([claimId, version]); if (identities.has(identity)) fail("FORMAL_BINDING_DUPLICATE", path, "duplicate external claim identity"); identities.add(identity);
    if (b.supersedes !== null) text(b.supersedes, path);
    const meaning = resolveExactFormalSource(b.business_meaning_ref, sources, `${path}/business_meaning_ref`);
    const acceptance = resolveExactFormalSource(b.business_acceptance_ref, sources, `${path}/business_acceptance_ref`);
    const definitions = resolveExactFormalSource(b.definition_binding_ref, sources, `${path}/definition_binding_ref`);
    const profile = resolveExactFormalSource(b.formal_language_profile_ref, sources, `${path}/formal_language_profile_ref`);
    const algorithm = resolveExactFormalSource(b.identity_algorithm_ref, sources, `${path}/identity_algorithm_ref`);
    const business = decode(meaning.bytes, path); validateMeaning(business, path); const decision = object(business.acceptance, path);
    const v2Meaning = business.schema_version === "domainspec-v2.business-meaning/v2-candidate";
    const expectedAlgorithm = v2Meaning ? FORMAL_IDENTITY_ALGORITHM_V3_BYTES : FORMAL_IDENTITY_ALGORITHM_BYTES;
    if (algorithm.bytes.toString("utf8") !== expectedAlgorithm) fail("FORMAL_IDENTITY_ALGORITHM", path, "unsupported identity algorithm bytes for BusinessMeaning version");
    if (!["domainspec-v2.business-meaning/v1-candidate", "domainspec-v2.business-meaning/v2-candidate"].includes(String(business.schema_version)) || business.status !== "accepted" || business.authority_effect !== "none" || decision.status !== "accepted" || decision.acceptance_ref !== acceptance.ref.path || decision.acceptance_digest !== acceptance.ref.sha256 || decision.owner_ref !== business.owner) fail("FORMAL_MEANING_ACCEPTANCE", path, "meaning does not bind the selected acceptance bytes and owner");
    const selectedDecision = decode(acceptance.bytes, `${path}/business_acceptance_ref`);
    exact(selectedDecision, ["schema_version", "decision_id", "owner", "outcome", "subject", "authority_effect"], `${path}/business_acceptance_ref`);
    text(selectedDecision.decision_id, `${path}/business_acceptance_ref/decision_id`);
    text(selectedDecision.owner, `${path}/business_acceptance_ref/owner`);
    const subject = exact(selectedDecision.subject, ["meaning_id", "version", "canonicalization", "digest_algorithm", "digest"], `${path}/business_acceptance_ref/subject`);
    text(subject.meaning_id, `${path}/business_acceptance_ref/subject/meaning_id`);
    text(subject.version, `${path}/business_acceptance_ref/subject/version`);
    digest(subject.digest, `${path}/business_acceptance_ref/subject/digest`);
    if (selectedDecision.schema_version !== "domainspec-v2.business-acceptance-decision/v1-candidate"
      || selectedDecision.owner !== business.owner || selectedDecision.owner !== decision.owner_ref
      || selectedDecision.outcome !== "accepted" || selectedDecision.authority_effect !== "none"
      || subject.meaning_id !== business.meaning_id || subject.version !== business.version
      || subject.canonicalization !== "domainspec-json-keysort-excluding-acceptance-v1"
      || subject.digest_algorithm !== "sha256" || subject.digest !== businessAcceptanceSubjectDigest(business))
      fail("FORMAL_MEANING_ACCEPTANCE", `${path}/business_acceptance_ref`, "selected owner decision does not accept this exact BusinessMeaning subject");
    definitionClosure(decode(definitions.bytes, path), claimId, version, sources,
      `${path}/definitions`, v2Meaning ? list(business.definitions, path) : undefined);
    const profileDocument = decode(profile.bytes, path);
    const profiles = Array.isArray(profileDocument.profiles) ? profileDocument.profiles.map(p => object(p, path)) : [profileDocument];
    const selectedProfiles = profiles.filter(p => `${p.profile_id}/${p.version}` === declaration.profile);
    if (selectedProfiles.length !== 1 || selectedProfiles[0]!.logic_family !== "many-sorted-first-order-logic" || selectedProfiles[0]!.formal_claim_role !== "canonical-source") fail("FORMAL_LANGUAGE_PROFILE", path, "source profile does not resolve to exactly one sorted-FOL canonical profile");
    if (sha(canonical(selectedProfiles[0])) !== FOL_CORE_PROFILE_SHA256) fail("FORMAL_LANGUAGE_PROFILE", path, "profile semantics differ from the implemented fol-core binding");
    const sorted = <T extends { name: string }>(items: T[]): T[] => [...items].sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
    const signature = { sorts: sorted(declaration.signature.sorts), functions: sorted(declaration.signature.functions), predicates: sorted(declaration.signature.predicates), constants: sorted(declaration.signature.constants) };
    const semanticIdentity = canonical(declaration.proposition);
    const meaningIdentity = v2Meaning ? sha(canonical(Object.fromEntries(Object.entries(business).filter(([key]) => key !== "acceptance" && key !== "interpretation_model_ref")))) : meaning.ref.sha256;
    const identityInputs = { ...(v2Meaning ? { business_meaning_semantic_sha256: meaningIdentity } : { business_meaning_sha256: meaningIdentity }), definition_binding_sha256: definitions.ref.sha256,
      formal_profile_sha256: sha(canonical(selectedProfiles[0])), signature, proposition_semantic_identity: semanticIdentity, claim_ceiling: declaration.ceiling };
    const claim = { schema_version: "domainspec-v2.formal-claim-source/v4-candidate",
      claim: { claim_id: claimId, claim_version: version, owner: model.owner, currentness: "current", supersedes: b.supersedes,
        identity_algorithm_ref: algorithm.ref, identity_inputs_digest: sha(canonical(identityInputs)) },
      business_meaning_ref: meaning.ref, business_acceptance_ref: acceptance.ref, definition_binding_ref: definitions.ref,
      formal_language_profile_ref: profile.ref, formal_signature: signature,
      canonical_proposition: { representation_media_type: "text/x-alchlang-fol", representation: declaration.proposition_source,
        representation_digest: sha(declaration.proposition_source), semantic_identity: semanticIdentity,
        semantic_identity_digest: sha(semanticIdentity), identity_algorithm_ref: algorithm.ref },
      interpretation_boundary: { interpretation_model_is_part_of_claim: false, join_stage: "external-evaluation-context" },
      source_authority_count: 1, tde_compatibility: { current_intake_contract: "FormalClaimSourcePayload/v2", status: "adapter-required", v2_projection_ref: null },
      claim_ceiling: declaration.ceiling, authority_effect: "none" };
    const output = `formalization/claims/${declaration.id}.json`;
    files[output] = json(claim);
    trace.push({ source_id: declaration.id, source_line: declaration.source_line, target: output, target_sha256: sha(files[output]!), claim_id: claimId, claim_version: version, identity_inputs_digest: claim.claim.identity_inputs_digest });
    return claim;
  });
  return { model, claims, files, trace: { schema_version: "alchlang.formal-claim-trace/v1", source_sha256: sha(source), bindings_sha256: sha(canonical(input)), declarations: trace, authority_effect: "none" } };
}
