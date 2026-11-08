import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { FORMAL_IDENTITY_ALGORITHM_V3_BYTES } from "../src/formal-claim-lowering.js";
import { assertApplicationFormalClaimV2ProjectionCurrent, projectApplicationFormalClaimsToV2 } from "../src/formal-claim-v2-projection.js";
import { formalLoweringFixture, source } from "./fixtures/formal-lowering-fixture.js";

const sha = (bytes: string | Buffer) => createHash("sha256").update(bytes).digest("hex");

test("projects current v4 FormalClaim bytes into deterministic current v2 intake without a second claim", () => {
  const fixture = formalLoweringFixture(); const result = projectApplicationFormalClaimsToV2(source, fixture.input, fixture.sources);
  assert.deepEqual(result, projectApplicationFormalClaimsToV2(source, structuredClone(fixture.input), fixture.sources));
  const v4 = result.formal.claims[0]!; const v2 = result.payloads[0]! as any; const projection = result.projections[0]! as any;
  assert.equal(v2.schema_version, "domainspec-v2.formal-claim-source-payload/v2");
  assert.deepEqual([v2.claim.claim_id, v2.claim.claim_version, v2.claim.owner], [v4.claim.claim_id, v4.claim.claim_version, v4.claim.owner]);
  assert.equal(v2.claim.source_digest, sha(result.formal.files["formalization/claims/EligibleClaim.json"]!));
  assert.deepEqual(v2.business_binding, { business_meaning_ref: v4.business_meaning_ref.path,
    business_meaning_digest: v4.business_meaning_ref.sha256, relation: "formalizes",
    acceptance_ref: v4.business_acceptance_ref.path, acceptance_digest: v4.business_acceptance_ref.sha256 });
  assert.equal(v2.canonical_proposition.representation, v4.canonical_proposition.representation);
  assert.equal(v2.canonical_proposition.semantic_identity, v4.canonical_proposition.semantic_identity);
  assert.deepEqual(v2.canonical_proposition.identity_algorithm, { id: "alchlang.formal-identity-algorithm", version: "1",
    digest: v4.canonical_proposition.identity_algorithm_ref.sha256 });
  assert.equal(v2.claim_ceiling, v4.claim_ceiling);
  assert.deepEqual(v2.interpretation_environment.signature, ["sort Order", "predicate Eligible(Order)"]);
  assert.match(v2.interpretation_environment.imports[0], new RegExp(v4.definition_binding_ref.sha256));
  assert.equal(projection.source_identity_inputs_digest, v4.claim.identity_inputs_digest);
  assert.equal(projection.semantic_loss_count, 0); assert.equal(projection.known_losses.length, 5);
  assert.equal(result.trace.meaning_repaired_or_invented, false);
  assert.equal((result.attached_sources[0]! as any).tde_compatibility.status, "v2-projection-attached");
  assertApplicationFormalClaimV2ProjectionCurrent(source, fixture.input, fixture.sources, result);
});

test("v2 compatibility payload preserves the exact v3 identity algorithm version", () => {
  const fixture = formalLoweringFixture();
  const originalRef = fixture.input.formal_claims.EligibleClaim.business_meaning_ref;
  const original = JSON.parse(fixture.sources.get(originalRef.path)!.toString());
  const meaning = { ...original, schema_version: "domainspec-v2.business-meaning/v2-candidate", supersedes: "Meaning:fixture@0", supersession_effect: "accepted-supersession",
    base_accepted_meaning_ref: originalRef, definition_source_ref: fixture.graph.definition_authority_ref,
    interpretation_model_ref: fixture.put("fixture/model.json", { model: "a" }),
    definition_policy: { canonical_location: "inline-in-this-business-meaning", normative_voice: "formal", explanatory_voices: ["plain_language", "domain_context"], conflict_rule: "formal-voice-prevails" },
    definitions: [fixture.definition] };
  fixture.input.formal_claims.EligibleClaim.business_acceptance_ref = fixture.acceptMeaning(meaning);
  fixture.input.formal_claims.EligibleClaim.business_meaning_ref = fixture.put("fixture/meaning-v2.json", meaning);
  fixture.input.formal_claims.EligibleClaim.identity_algorithm_ref = fixture.put("fixture/identity-v3.json", FORMAL_IDENTITY_ALGORITHM_V3_BYTES);
  const result = projectApplicationFormalClaimsToV2(source, fixture.input, fixture.sources);
  assert.deepEqual((result.payloads[0] as any).canonical_proposition.identity_algorithm,
    { id: "alchlang.formal-identity-algorithm", version: "3", digest: fixture.input.formal_claims.EligibleClaim.identity_algorithm_ref.sha256 });
  const targetSchema = fileURLToPath(new URL("../../../../../../../craft/projects/domainspec-v2/development/spec-ontology-branch-decision/contracts/formal-claim-source-payload.v2.schema.json", import.meta.url));
  const validate = spawnSync("python3", ["-c", "import json,sys,jsonschema; jsonschema.Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(sys.stdin))", targetSchema],
    { input: JSON.stringify(result.payloads[0]), encoding: "utf8", timeout: 10000 });
  assert.equal(validate.status, 0, validate.stderr || String(validate.error));
  fixture.input.formal_claims.EligibleClaim.business_acceptance_ref = fixture.acceptMeaning(meaning, "fixture/acceptance-reissued.json");
  fixture.input.formal_claims.EligibleClaim.business_meaning_ref = fixture.put("fixture/meaning-v2.json", meaning);
  assert.throws(() => assertApplicationFormalClaimV2ProjectionCurrent(source, fixture.input, fixture.sources, result), /FORMAL_V2_PROJECTION_STALE/);
  const reissued = projectApplicationFormalClaimsToV2(source, fixture.input, fixture.sources);
  assert.equal(reissued.formal.claims[0]!.claim.identity_inputs_digest, result.formal.claims[0]!.claim.identity_inputs_digest);
  assert.notEqual((reissued.projections[0] as any).target_ref.sha256, (result.projections[0] as any).target_ref.sha256);
  meaning.interpretation_model_ref = fixture.put("fixture/model-b.json", { model: "b" });
  fixture.input.formal_claims.EligibleClaim.business_acceptance_ref = fixture.acceptMeaning(meaning);
  fixture.input.formal_claims.EligibleClaim.business_meaning_ref = fixture.put("fixture/meaning-v2.json", meaning);
  assert.throws(() => assertApplicationFormalClaimV2ProjectionCurrent(source, fixture.input, fixture.sources, reissued), /FORMAL_V2_PROJECTION_STALE/);
  const changed = projectApplicationFormalClaimsToV2(source, fixture.input, fixture.sources);
  assert.equal(changed.formal.claims[0]!.claim.identity_inputs_digest, result.formal.claims[0]!.claim.identity_inputs_digest);
  assert.notEqual((changed.projections[0] as any).target_ref.sha256, (result.projections[0] as any).target_ref.sha256);
});

test("v4 proposition and ceiling mutations create new identity and projection bytes instead of being repaired", () => {
  const fixture = formalLoweringFixture(); const initial = projectApplicationFormalClaimsToV2(source, fixture.input, fixture.sources);
  for (const changedSource of [source.replace("forall o", "exists o"), source.replace("Synthetic eligibility only.", "Changed synthetic ceiling.")]) {
    const input = structuredClone(fixture.input); input.source_sha256 = sha(changedSource);
    const changed = projectApplicationFormalClaimsToV2(changedSource, input, fixture.sources);
    assert.notEqual(changed.formal.claims[0]!.claim.identity_inputs_digest, initial.formal.claims[0]!.claim.identity_inputs_digest);
    assert.notEqual((changed.projections[0]! as any).target_ref.sha256, (initial.projections[0]! as any).target_ref.sha256);
    assert.equal(changed.trace.meaning_repaired_or_invented, false);
  }
});

test("currentness rejects mutations to every meaning-bearing v2 projection surface", () => {
  const mutate = [
    (value: any) => { value.payloads[0].business_binding.business_meaning_digest = "0".repeat(64); },
    (value: any) => { value.payloads[0].canonical_proposition.representation = "invented"; },
    (value: any) => { value.payloads[0].interpretation_environment.signature[0] = "sort Invented"; },
    (value: any) => { value.payloads[0].interpretation_environment.imports = []; },
    (value: any) => { value.payloads[0].claim_ceiling = "widened"; },
    (value: any) => { value.projections[0].semantic_loss_count = 1; },
    (value: any) => { value.preservation_bindings[0].status = "partially-preserved"; },
    (value: any) => { value.attached_sources[0].tde_compatibility.v2_projection_ref.sha256 = "f".repeat(64); },
  ];
  for (const change of mutate) {
    const fixture = formalLoweringFixture(); const result = projectApplicationFormalClaimsToV2(source, fixture.input, fixture.sources);
    const changed = structuredClone(result); change(changed);
    assert.throws(() => assertApplicationFormalClaimV2ProjectionCurrent(source, fixture.input, fixture.sources, changed), /FORMAL_V2_PROJECTION_STALE/);
  }
});

test("stale v4 inputs reject before any projection is returned", () => {
  const fixture = formalLoweringFixture();
  fixture.sources.set(fixture.input.formal_claims.EligibleClaim.business_meaning_ref.path, Buffer.from("{}"));
  assert.throws(() => projectApplicationFormalClaimsToV2(source, fixture.input, fixture.sources), /FORMAL_BINDING_STALE/);
});

test("v2 payload, projection, preservation binding and attached v4 source satisfy closed schemas", () => {
  const fixture = formalLoweringFixture(); const result = projectApplicationFormalClaimsToV2(source, fixture.input, fixture.sources);
  const roots = [
    new URL("../../../../../../../craft/projects/domainspec-v2/development/spec-ontology-branch-decision/contracts/formal-claim-source-payload.v2.schema.json", import.meta.url),
    new URL("../../../../../../../craft/projects/domainspec-v2/development/authoring-to-runtime-v1/formal-claim-v4-v2-projection.schema.json", import.meta.url),
    new URL("../../../../../../../craft/projects/domainspec-v2/formalization/schemas/preservation-binding.schema.json", import.meta.url),
    new URL("../../../../../../../craft/projects/domainspec-v2/formalization/schemas/formal-claim-source-v4-candidate.schema.json", import.meta.url),
  ].map(value => fileURLToPath(value));
  const script = "import json,sys,jsonschema; p=json.load(sys.stdin); [(jsonschema.Draft202012Validator(json.load(open(s))).validate(v)) for v,s in zip(p,sys.argv[1:])]";
  const values = [result.payloads[0], result.projections[0], result.preservation_bindings[0], result.attached_sources[0]];
  const validation = spawnSync("python3", ["-c", script, ...roots], { input: JSON.stringify(values), encoding: "utf8", timeout: 10000 });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
});
