import type { CompiledProjectGraph } from "../input/project-model.js";
import { assertCompiledProjectSnapshot } from "../input/project-model.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";

export const CONDITION_BINDING_VERSION = "domainspec.formal-condition-bindings/v1-candidate";
export const CONDITION_RELATIONSHIP = Object.freeze({
  relationship: "condition-bound-to", source_partition: "domain", source_kind: "Rule",
  target_partition: "formalization", target_kind: "FormalClaim",
  conditions_per_selected_rule: 1, rules_per_claim: "many", authority_effect: "none",
});

export class ConditionBindingError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(`${code} at ${pointer}: ${message}`);
    this.name = "ConditionBindingError";
  }
}
const fail = (code: string, path: string, message: string): never => { throw new ConditionBindingError(code, path, message); };
function object(value: unknown, path: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("CONDITION_SCHEMA", path, "expected object");
  return value as Record<string, unknown>;
}
function exact(value: unknown, keys: readonly string[], path: string): Record<string, unknown> {
  const result = object(value, path);
  if (canonicalJson(Object.keys(result).sort()) !== canonicalJson([...keys].sort())) fail("CONDITION_SCHEMA", path, "unexpected or missing member");
  return result;
}
function text(value: unknown, path: string): string {
  if (typeof value !== "string" || !value.trim()) fail("CONDITION_SCHEMA", path, "expected nonempty text");
  return value as string;
}
function digest(value: unknown, path: string): string {
  const result = text(value, path);
  if (!/^[a-f0-9]{64}$/.test(result)) fail("CONDITION_SCHEMA", path, "expected SHA-256");
  return result;
}

/** Joins exact source identities only. It does not validate a proposition or its executable projection. */
export function compileFormalConditionBindings(
  graph: CompiledProjectGraph,
  input: unknown,
  sources: ReadonlyMap<string, Buffer>,
) {
  assertCompiledProjectSnapshot(graph);
  const root = exact(input, ["schema_version", "rules", "bindings", "authority_effect"], "$");
  if (root.schema_version !== CONDITION_BINDING_VERSION || root.authority_effect !== "none") fail("CONDITION_SCHEMA", "$", "invalid version or authority effect");
  if (!Array.isArray(root.rules) || !Array.isArray(root.bindings)) fail("CONDITION_SCHEMA", "$", "rules and bindings must be arrays");
  const ruleList = root.rules as unknown[];
  const selected = new Set(ruleList.map((rule, i) => text(rule, `$/rules/${i}`)));
  if (selected.size !== ruleList.length) fail("CONDITION_MULTIPLICITY", "$/rules", "duplicate selected Rule");
  for (const rule of selected) {
    if (graph.nodes.find(node => node.selector === rule)?.kind !== "Rule") fail("CONDITION_SOURCE_KIND", rule, "expected an exact qualified Rule in this graph");
  }
  const seenRules = new Set<string>();
  const seenIds = new Set<string>();
  const identities = new Map<string, string>();
  const bindings = (root.bindings as unknown[]).map((raw, index) => {
    const path = `$/bindings/${index}`;
    const b = exact(raw, ["binding_id", "relationship", "rule_ref", "claim_ref", "source_pointer"], path);
    const id = text(b.binding_id, `${path}/binding_id`);
    if (seenIds.has(id)) fail("CONDITION_MULTIPLICITY", path, "duplicate binding identity");
    seenIds.add(id);
    if (b.relationship !== CONDITION_RELATIONSHIP.relationship) fail("CONDITION_RELATIONSHIP", path, "expected condition-bound-to");
    const rule = text(b.rule_ref, `${path}/rule_ref`);
    if (!selected.has(rule)) fail("CONDITION_SOURCE_KIND", path, "Rule not selected in this binding scope");
    if (seenRules.has(rule)) fail("CONDITION_MULTIPLICITY", path, "Rule has more than one condition");
    seenRules.add(rule);
    const ref = exact(b.claim_ref, ["path", "sha256", "size_bytes", "claim_id", "claim_version", "identity_inputs_digest"], `${path}/claim_ref`);
    const sourcePath = text(ref.path, `${path}/claim_ref/path`);
    if (sourcePath.startsWith("/") || sourcePath.includes("\\") || sourcePath.includes(":") || sourcePath.split("/").some(part => !part || part === "." || part === "..")) fail("CONDITION_SOURCE_PATH", path, "expected a bounded relative source path");
    const sourceDigest = digest(ref.sha256, `${path}/claim_ref/sha256`);
    if (!Number.isSafeInteger(ref.size_bytes) || (ref.size_bytes as number) < 1) fail("CONDITION_SCHEMA", path, "invalid byte count");
    const bytes = sources.get(sourcePath);
    if (!bytes) fail("CONDITION_SOURCE_MISSING", path, "claim bytes unavailable");
    const sourceBytes = bytes as Buffer;
    if (sourceBytes.length !== ref.size_bytes || sha256(sourceBytes) !== sourceDigest) fail("CONDITION_SOURCE_STALE", path, "claim bytes differ from exact reference");
    let payload: unknown;
    try { payload = JSON.parse(sourceBytes.toString("utf8")); }
    catch { fail("CONDITION_SOURCE_JSON", path, "claim source is not JSON"); }
    const claimSource = object(payload, path);
    if (claimSource.schema_version !== "domainspec-v2.formal-claim-source/v4-candidate" || claimSource.authority_effect !== "none") fail("CONDITION_TARGET_KIND", path, "expected non-authorizing FormalClaim v4 source");
    const claim = object(claimSource.claim, `${path}/claim`);
    const claimId = text(ref.claim_id, `${path}/claim_ref/claim_id`);
    const version = text(ref.claim_version, `${path}/claim_ref/claim_version`);
    const identity = digest(ref.identity_inputs_digest, `${path}/claim_ref/identity_inputs_digest`);
    if (claim.claim_id !== claimId || claim.claim_version !== version || claim.identity_inputs_digest !== identity || claim.currentness !== "current") fail("CONDITION_CLAIM_IDENTITY", path, "claim identity, version or currentness differs");
    const identityKey = canonicalJson([claimId, version]);
    if (identities.has(identityKey) && identities.get(identityKey) !== sourceDigest) fail("CONDITION_CLAIM_COLLISION", path, "one claim identity resolves to competing source bytes");
    identities.set(identityKey, sourceDigest);
    return Object.freeze({ binding_id: id, relationship: "condition-bound-to" as const,
      rule_ref: rule, claim_ref: Object.freeze({ path: sourcePath, sha256: sourceDigest,
        size_bytes: sourceBytes.length, claim_id: claimId, claim_version: version,
        identity_inputs_digest: identity }), source_pointer: text(b.source_pointer, `${path}/source_pointer`) });
  });
  for (const rule of selected) if (!seenRules.has(rule)) fail("CONDITION_MISSING", rule, "selected Rule has no FormalClaim condition");
  bindings.sort((a, b) => a.binding_id < b.binding_id ? -1 : a.binding_id > b.binding_id ? 1 : 0);
  const result = { schema_version: CONDITION_BINDING_VERSION, project_id: graph.project_id,
    domain_source_manifest_sha256: graph.source_manifest.manifest_sha256,
    relationship_signature_sha256: sha256(canonicalJson(CONDITION_RELATIONSHIP)),
    rules: Object.freeze([...selected].sort()), bindings: Object.freeze(bindings),
    authority_effect: "none" as const,
    claim_ceiling: "Exact endpoint and source-byte join only; no proposition validation, executable equivalence, proof or admission." };
  return Object.freeze({ ...result, join_sha256: sha256(canonicalJson(result)) });
}
