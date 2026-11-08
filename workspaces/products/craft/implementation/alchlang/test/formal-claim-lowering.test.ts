import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { FORMAL_IDENTITY_ALGORITHM_V2_BYTES, FORMAL_IDENTITY_ALGORITHM_V3_BYTES, lowerApplicationFormalClaims } from "../src/formal-claim-lowering.js";

const sha = (text: string | Buffer) => createHash("sha256").update(text).digest("hex");
const canonical = (value: any): string => Array.isArray(value) ? `[${value.map(canonical).join(",")}]` : value && typeof value === "object" ? `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(",")}}` : JSON.stringify(value);
import { source, formalLoweringFixture } from "./fixtures/formal-lowering-fixture.js";

function selectedMeaningFixture(version: "v1" | "v2") {
  const f = formalLoweringFixture(); const b = f.input.formal_claims.EligibleClaim;
  const originalRef = b.business_meaning_ref;
  const original = JSON.parse(f.sources.get(originalRef.path)!.toString());
  const meaning = version === "v1" ? original : {
    ...original, schema_version: "domainspec-v2.business-meaning/v2-candidate",
    supersedes: "Meaning:fixture@0", supersession_effect: "accepted-supersession",
    base_accepted_meaning_ref: originalRef, definition_source_ref: f.graph.definition_authority_ref,
    interpretation_model_ref: f.put("fixture/model.json", { model: "a" }),
    definition_policy: { canonical_location: "inline-in-this-business-meaning", normative_voice: "formal",
      explanatory_voices: ["plain_language", "domain_context"], conflict_rule: "formal-voice-prevails" },
    definitions: [f.definition]
  };
  if (version === "v2") b.identity_algorithm_ref = f.put("fixture/identity-v3.json", FORMAL_IDENTITY_ALGORITHM_V3_BYTES);
  b.business_acceptance_ref = f.acceptMeaning(meaning);
  b.business_meaning_ref = f.put("fixture/selected-meaning.json", meaning);
  return { f, b, meaning };
}

test("emits deterministic v4 sources with exact representation, semantic identity and source trace", () => {
  const f = formalLoweringFixture(); const result = lowerApplicationFormalClaims(source, f.input, f.sources);
  assert.deepEqual(result, lowerApplicationFormalClaims(source, structuredClone(f.input), f.sources));
  const claim = result.claims[0]!;
  assert.equal(claim.schema_version, "domainspec-v2.formal-claim-source/v4-candidate");
  assert.equal(claim.claim.claim_id, "FormalClaim:fixture");
  assert.equal(claim.canonical_proposition.representation_digest, sha(claim.canonical_proposition.representation));
  assert.equal(claim.canonical_proposition.semantic_identity_digest, sha(claim.canonical_proposition.semantic_identity));
  assert.equal(claim.tde_compatibility.status, "adapter-required");
  assert.equal(claim.interpretation_boundary.interpretation_model_is_part_of_claim, false);
  assert.equal(result.trace.declarations[0]!.target_sha256, sha(result.files["formalization/claims/EligibleClaim.json"]!));
});

test("whitespace and unrelated providers do not change claim identity; proposition and ceiling do", () => {
  const f = formalLoweringFixture();
  const identity = (text: string) => lowerApplicationFormalClaims(text, { ...f.input, source_sha256: sha(text) }, f.sources).claims[0]!.claim.identity_inputs_digest;
  const initial = identity(source);
  assert.equal(identity(source.replace("Eligible(o)", "Eligible( o )")), initial);
  f.put("unselected/runtime.json", { provider: "different-provider", bound: 100 });
  assert.equal(identity(source), initial);
  assert.notEqual(identity(source.replace("forall o", "exists o")), initial);
  assert.notEqual(identity(source.replace("Synthetic eligibility only.", "Another ceiling.")), initial);
});

test("BusinessMeaning v2 interpretation change requires a fresh decision but preserves claim identity", () => {
  const f = formalLoweringFixture();
  const originalRef = f.input.formal_claims.EligibleClaim.business_meaning_ref;
  const original = JSON.parse(f.sources.get(originalRef.path)!.toString());
  const meaning = {
    ...original,
    schema_version: "domainspec-v2.business-meaning/v2-candidate",
    supersedes: "Meaning:fixture@0",
    supersession_effect: "accepted-supersession",
    base_accepted_meaning_ref: originalRef,
    definition_source_ref: f.graph.definition_authority_ref,
    interpretation_model_ref: f.put("fixture/model-a.json", { model: "a" }),
    definition_policy: { canonical_location: "inline-in-this-business-meaning", normative_voice: "formal", explanatory_voices: ["plain_language", "domain_context"], conflict_rule: "formal-voice-prevails" },
    definitions: [f.definition]
  };
  f.input.formal_claims.EligibleClaim.identity_algorithm_ref = f.put("fixture/identity-v3.json", FORMAL_IDENTITY_ALGORITHM_V3_BYTES);
  const lower = () => {
    f.input.formal_claims.EligibleClaim.business_acceptance_ref = f.acceptMeaning(meaning);
    f.input.formal_claims.EligibleClaim.business_meaning_ref = f.put("fixture/meaning-v2.json", meaning);
    return lowerApplicationFormalClaims(source, f.input, f.sources).claims[0]!;
  };
  const first = lower();
  meaning.interpretation_model_ref = f.put("fixture/model-b.json", { model: "b" });
  f.input.formal_claims.EligibleClaim.business_meaning_ref = f.put("fixture/meaning-v2.json", meaning);
  assert.throws(() => lowerApplicationFormalClaims(source, f.input, f.sources), /FORMAL_MEANING_ACCEPTANCE/);
  const changedContext = lower();
  assert.equal(changedContext.claim.identity_inputs_digest, first.claim.identity_inputs_digest);
  assert.notEqual(changedContext.business_meaning_ref.sha256, first.business_meaning_ref.sha256);
  meaning.rule = "A changed business rule";
  assert.notEqual(lower().claim.identity_inputs_digest, first.claim.identity_inputs_digest);
});

test("BusinessMeaning v2 rejects a coordinated detached definition authority", () => {
  for (const mode of ["changed-body", "extra-body"]) {
    const f = formalLoweringFixture(); const b = f.input.formal_claims.EligibleClaim;
    const originalRef = b.business_meaning_ref;
    const original = JSON.parse(f.sources.get(originalRef.path)!.toString());
    const meaning = { ...original, schema_version: "domainspec-v2.business-meaning/v2-candidate",
      supersedes: "Meaning:fixture@0", supersession_effect: "accepted-supersession",
      base_accepted_meaning_ref: originalRef, definition_source_ref: f.graph.definition_authority_ref,
      interpretation_model_ref: f.put("fixture/model.json", { model: "a" }),
      definition_policy: { canonical_location: "inline-in-this-business-meaning", normative_voice: "formal",
        explanatory_voices: ["plain_language", "domain_context"], conflict_rule: "formal-voice-prevails" },
      definitions: [f.definition] };
    b.business_acceptance_ref = f.acceptMeaning(meaning);
    b.business_meaning_ref = f.put("fixture/meaning-v2.json", meaning);
    b.identity_algorithm_ref = f.put("fixture/identity-v3.json", FORMAL_IDENTITY_ALGORITHM_V3_BYTES);
    assert.equal(lowerApplicationFormalClaims(source, f.input, f.sources).claims.length, 1);
    const changed = { ...f.definition, formal: { ...f.definition.formal,
      expression: "A different, still accepted definition" } };
    const mirror = mode === "changed-body" ? [changed] : [f.definition, changed];
    f.graph.definition_authority_ref = f.put("fixture/detached-definitions.json", { definitions: mirror });
    if (mode === "changed-body") {
      f.graph.definition_nodes[0]!.definition_digest = sha(canonical(changed));
      f.graph.definition_closure.digest = sha(canonical([changed]));
    }
    b.definition_binding_ref = f.put("fixture/detached-binding.json", f.graph);
    assert.throws(() => lowerApplicationFormalClaims(source, f.input, f.sources),
      /FORMAL_DEFINITION_AUTHORITY/, mode);
  }
});

test("changed decision bytes reject under an unchanged exact acceptance reference", () => {
  const f = formalLoweringFixture();
  const decisionRef = f.input.formal_claims.EligibleClaim.business_acceptance_ref;
  const decision = JSON.parse(f.sources.get(decisionRef.path)!.toString());
  f.sources.set(decisionRef.path, Buffer.from(JSON.stringify({ ...decision, outcome: "rejected" })));
  assert.throws(() => lowerApplicationFormalClaims(source, f.input, f.sources), /FORMAL_BINDING_STALE/);
});

test("BusinessMeaning v2 refuses the legacy exact-meaning identity algorithm", () => {
  const f = formalLoweringFixture();
  const originalRef = f.input.formal_claims.EligibleClaim.business_meaning_ref;
  const original = JSON.parse(f.sources.get(originalRef.path)!.toString());
  const meaning = { ...original, schema_version: "domainspec-v2.business-meaning/v2-candidate", supersedes: "Meaning:fixture@0", supersession_effect: "accepted-supersession",
    base_accepted_meaning_ref: originalRef, definition_source_ref: f.graph.definition_authority_ref,
    interpretation_model_ref: f.put("fixture/model.json", { model: "a" }),
    definition_policy: { canonical_location: "inline-in-this-business-meaning", normative_voice: "formal", explanatory_voices: ["plain_language", "domain_context"], conflict_rule: "formal-voice-prevails" },
    definitions: [f.definition] };
  f.input.formal_claims.EligibleClaim.business_meaning_ref = f.put("fixture/meaning-v2.json", meaning);
  assert.throws(() => lowerApplicationFormalClaims(source, f.input, f.sources), /FORMAL_IDENTITY_ALGORITHM/);
});

test("BusinessMeaning v2 refuses the predecessor algorithm that includes acceptance in claim identity", () => {
  const f = formalLoweringFixture();
  const originalRef = f.input.formal_claims.EligibleClaim.business_meaning_ref;
  const original = JSON.parse(f.sources.get(originalRef.path)!.toString());
  const meaning = { ...original, schema_version: "domainspec-v2.business-meaning/v2-candidate", supersedes: "Meaning:fixture@0", supersession_effect: "accepted-supersession",
    base_accepted_meaning_ref: originalRef, definition_source_ref: f.graph.definition_authority_ref,
    interpretation_model_ref: f.put("fixture/model.json", { model: "a" }),
    definition_policy: { canonical_location: "inline-in-this-business-meaning", normative_voice: "formal", explanatory_voices: ["plain_language", "domain_context"], conflict_rule: "formal-voice-prevails" },
    definitions: [f.definition] };
  f.input.formal_claims.EligibleClaim.business_acceptance_ref = f.acceptMeaning(meaning);
  f.input.formal_claims.EligibleClaim.business_meaning_ref = f.put("fixture/meaning-v2.json", meaning);
  f.input.formal_claims.EligibleClaim.identity_algorithm_ref = f.put("fixture/identity-v2.json", FORMAL_IDENTITY_ALGORITHM_V2_BYTES);
  assert.throws(() => lowerApplicationFormalClaims(source, f.input, f.sources), /FORMAL_IDENTITY_ALGORITHM/);
});

test("missing stale and wrong-owner bindings reject before producing a result", () => {
  for (const mode of ["missing", "stale", "owner", "acceptance", "algorithm", "coverage"]) {
    const f = formalLoweringFixture(); const b = f.input.formal_claims.EligibleClaim;
    if (mode === "missing") f.sources.delete(b.business_meaning_ref.path);
    if (mode === "stale") f.sources.set(b.business_meaning_ref.path, Buffer.from("{}"));
    if (mode === "owner") f.input.owner = "different";
    if (mode === "acceptance") b.business_acceptance_ref = f.put("fixture/other-decision.json", {});
    if (mode === "algorithm") b.identity_algorithm_ref = f.put("fixture/identity.json", "invented");
    if (mode === "coverage") Object.assign(f.input.formal_claims, { Unknown: structuredClone(b) });
    assert.throws(() => lowerApplicationFormalClaims(source, f.input, f.sources), /FORMAL_/);
  }
});

test("v1 and v2 selected acceptance decisions require exact structured subjects", () => {
  for (const version of ["v1", "v2"] as const) {
    for (const mode of ["rejected", "owner", "subject", "version", "legacy", "numeric-id", "numeric-subject-id", "extra-decision", "extra-subject", "historical-bundled"]) {
      const { f, b, meaning } = selectedMeaningFixture(version);
      let decision = JSON.parse(f.sources.get(b.business_acceptance_ref.path)!.toString());
      if (mode === "rejected") decision.outcome = "rejected";
      if (mode === "owner") decision.owner = "different-owner";
      if (mode === "subject") decision.subject.digest = "a".repeat(64);
      if (mode === "version") decision.subject.version = "different-version";
      if (mode === "numeric-id") decision.decision_id = 42;
      if (mode === "numeric-subject-id") decision.subject.meaning_id = 42;
      if (mode === "legacy") { delete decision.schema_version; delete decision.subject; }
      if (mode === "extra-decision") decision.unreviewed_claim = true;
      if (mode === "extra-subject") decision.subject.unreviewed_claim = true;
      if (mode === "historical-bundled") decision = JSON.parse(readFileSync(new URL(
        "../../../../../../../auth-foundation/formalization/decisions/AF-EXACT-SESSION-ROLE-PERMISSION-001/owner-semantic-decision.json",
        import.meta.url), "utf8"));
      b.business_acceptance_ref = f.put("fixture/acceptance.json", decision);
      meaning.acceptance.acceptance_digest = b.business_acceptance_ref.sha256;
      b.business_meaning_ref = f.put("fixture/selected-meaning.json", meaning);
      assert.throws(() => lowerApplicationFormalClaims(source, f.input, f.sources),
        mode === "historical-bundled" ? /FORMAL_BINDING_SCHEMA/ : /FORMAL_/, `${version}: ${mode}`);
    }
  }
});

test("valid decision reissue preserves each version's documented claim identity rule", () => {
  for (const version of ["v1", "v2"] as const) {
    const { f, b, meaning } = selectedMeaningFixture(version);
    const first = lowerApplicationFormalClaims(source, f.input, f.sources).claims[0]!;
    b.business_acceptance_ref = f.acceptMeaning(meaning, "fixture/acceptance-reissued.json");
    b.business_meaning_ref = f.put("fixture/selected-meaning.json", meaning);
    const reissued = lowerApplicationFormalClaims(source, f.input, f.sources).claims[0]!;
    assert.notEqual(reissued.business_acceptance_ref.path, first.business_acceptance_ref.path, version);
    assert.notEqual(reissued.business_meaning_ref.sha256, first.business_meaning_ref.sha256, version);
    assert.equal(reissued.schema_version, "domainspec-v2.formal-claim-source/v4-candidate");
    if (version === "v1") assert.notEqual(reissued.claim.identity_inputs_digest, first.claim.identity_inputs_digest);
    else assert.equal(reissued.claim.identity_inputs_digest, first.claim.identity_inputs_digest);
    const schemaRoot = fileURLToPath(new URL("../../../../../../../craft/projects/domainspec-v2/formalization/schemas/", import.meta.url));
    const payload = { claim: reissued, meaning, decision: JSON.parse(f.sources.get(b.business_acceptance_ref.path)!.toString()),
      meaning_schema: version === "v1" ? "business-meaning.schema.json" : "business-meaning.v2-candidate.schema.json" };
    const validation = spawnSync("python3", ["-c", "import json,sys,pathlib,jsonschema; p=json.load(sys.stdin); root=pathlib.Path(sys.argv[1]); pairs=[(p['claim'],'formal-claim-source-v4-candidate.schema.json'),(p['meaning'],p['meaning_schema']),(p['decision'],'business-acceptance-decision.v1-candidate.schema.json')]; [(jsonschema.Draft202012Validator(json.loads((root/s).read_text())).validate(v)) for v,s in pairs]", schemaRoot],
      { input: JSON.stringify(payload), encoding: "utf8", timeout: 10000 });
    assert.equal(validation.status, 0, `${version}: ${validation.stderr || String(validation.error)}`);
  }
});

test("definition pointer, edge, closure and transitive dependency mutations reject", () => {
  for (const mode of ["pointer", "edge", "closure", "transitive", "accepted"]) {
    const f = formalLoweringFixture();
    if (mode === "pointer") f.graph.definition_nodes[0]!.definition_pointer = "#/definitions/1";
    if (mode === "edge") f.graph.relations[0]!.inference = "inferred";
    if (mode === "closure") f.graph.definition_closure.digest = "b".repeat(64);
    if (mode === "transitive" || mode === "accepted") {
      const definition = { ...f.definition, depends_on: mode === "transitive" ? ["MISSING-DEFINITION"] : [], status: mode === "accepted" ? "candidate" : "accepted" };
      f.graph.definition_authority_ref = f.put("fixture/definitions.json", { definitions: [definition] });
      f.graph.definition_nodes[0]!.definition_digest = sha(canonical(definition));
      f.graph.definition_closure.digest = sha(canonical([definition]));
    }
    f.input.formal_claims.EligibleClaim.definition_binding_ref = f.put("fixture/definition-binding.json", f.graph);
    assert.throws(() => lowerApplicationFormalClaims(source, f.input, f.sources), /FORMAL_DEFINITION_/);
  }
});

test("source digest, exact reference shape and paths cannot be bypassed", () => {
  const f = formalLoweringFixture();
  assert.throws(() => lowerApplicationFormalClaims(source + "\n", f.input, f.sources), /FORMAL_SOURCE_BINDING/);
  const changed = structuredClone(f.input); changed.formal_claims.EligibleClaim.business_meaning_ref.path = "../meaning.json";
  assert.throws(() => lowerApplicationFormalClaims(source, changed, f.sources), /FORMAL_BINDING_PATH/);
  Object.assign(f.input.formal_claims.EligibleClaim, { provider: "smt" });
  assert.throws(() => lowerApplicationFormalClaims(source, f.input, f.sources), /FORMAL_BINDING_SCHEMA/);
});

test("emitted claims and synthetic inputs conform to DomainSpec's authoritative JSON schemas", () => {
  const f = formalLoweringFixture(); const claims = lowerApplicationFormalClaims(source, f.input, f.sources).claims;
  const schemaRoot = fileURLToPath(new URL("../../../../../../../craft/projects/domainspec-v2/formalization/schemas/", import.meta.url));
  const payload = { claims, business: JSON.parse(f.sources.get("fixture/meaning.json")!.toString()), decision: JSON.parse(f.sources.get("fixture/acceptance.json")!.toString()), definitions: f.graph };
  const result = spawnSync("python3", ["-c", "import json,sys,pathlib,jsonschema; p=json.load(sys.stdin); root=pathlib.Path(sys.argv[1]); pairs=[(c,'formal-claim-source-v4-candidate.schema.json') for c in p['claims']]+[(p['business'],'business-meaning.schema.json'),(p['decision'],'business-acceptance-decision.v1-candidate.schema.json'),(p['definitions'],'formal-claim-definition-binding.schema.json')]; [(jsonschema.Draft202012Validator(json.loads((root/s).read_text())).validate(v)) for v,s in pairs]", schemaRoot], { input: JSON.stringify(payload), encoding: "utf8", timeout: 10000 });
  assert.equal(result.status, 0, result.stderr || String(result.error));
});

test("a familiar profile identifier cannot conceal changed profile semantics", () => {
  const f = formalLoweringFixture();
  const registry = JSON.parse(f.sources.get("fixture/profile.json")!.toString());
  registry.profiles.find((p: any) => p.profile_id === "fol-core").supported_constructs = ["arbitrary code"];
  f.input.formal_claims.EligibleClaim.formal_language_profile_ref = f.put("fixture/profile.json", registry);
  assert.throws(() => lowerApplicationFormalClaims(source, f.input, f.sources), /FORMAL_LANGUAGE_PROFILE/);
});
