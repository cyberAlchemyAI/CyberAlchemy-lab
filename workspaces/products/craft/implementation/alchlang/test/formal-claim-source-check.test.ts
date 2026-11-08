import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { lowerApplicationFormalClaims } from "../src/formal-claim-lowering.js";
import { checkFormalClaimSourceProposition } from "../src/formal-claim-source-check.js";
import { formalLoweringFixture, source } from "./fixtures/formal-lowering-fixture.js";

const sha = (value: string) => createHash("sha256").update(value).digest("hex");
const registry = JSON.parse(readFileSync(new URL("../../../../../../../craft/projects/domainspec-v2/formalization/profiles/formal-language-profiles.json", import.meta.url), "utf8"));
const profile = registry.profiles.find((item: { profile_id: string }) => item.profile_id === "fol-core");
const claim = () => {
  const fixture = formalLoweringFixture();
  return structuredClone(lowerApplicationFormalClaims(source, fixture.input, fixture.sources).claims[0]!);
};

test("checks emitted AlchLang v4 proposition against exact profile and signature", () => {
  const current = claim();
  assert.deepEqual(checkFormalClaimSourceProposition(current, profile), {
    status: "checked", checker: "alchlang-fol/1",
    representation_digest: current.canonical_proposition.representation_digest,
    ast_digest: current.canonical_proposition.semantic_identity_digest,
  });
});

test("rejects stale and recomputed malformed source, not just a bad digest", () => {
  const current = claim();
  current.canonical_proposition.representation = "This is malformed";
  assert.throws(() => checkFormalClaimSourceProposition(current, profile), /FOL_SOURCE_STALE/);
  current.canonical_proposition.representation_digest = sha(current.canonical_proposition.representation);
  assert.throws(() => checkFormalClaimSourceProposition(current, profile), /FOL_/);
});

test("rejects malformed, unbound, unknown, wrong arity and wrong-sort propositions", () => {
  const mutations = [
    "forall o: Order: Eligible(o) garbage",
    "forall o: Missing: Eligible(o)",
    "Eligible(o)",
    "forall o: Order: Missing(o)",
    "forall o: Order: Eligible()",
    "forall o: Order: Eligible(o,o)",
  ];
  for (const representation of mutations) {
    const current = claim();
    current.canonical_proposition.representation = representation;
    current.canonical_proposition.representation_digest = sha(representation);
    assert.throws(() => checkFormalClaimSourceProposition(current, profile), /FOL_/, representation);
  }
  const wrongSort = claim();
  wrongSort.formal_signature.sorts.push({ name: "Other" });
  wrongSort.formal_signature.constants.push({ name: "other", sort: "Other" });
  wrongSort.canonical_proposition.representation = "Eligible(other)";
  wrongSort.canonical_proposition.representation_digest = sha(wrongSort.canonical_proposition.representation);
  assert.throws(() => checkFormalClaimSourceProposition(wrongSort, profile), /FOL_SORT_MISMATCH/);
});

test("rejects a source whose checked AST differs from the supplied identity", () => {
  const current = claim();
  current.canonical_proposition.representation = "exists o: Order: Eligible(o)";
  current.canonical_proposition.representation_digest = sha(current.canonical_proposition.representation);
  assert.throws(() => checkFormalClaimSourceProposition(current, profile), /FOL_SOURCE_IDENTITY/);
});

test("historical Auth media, changed profile and arbitrary media remain explicitly unsupported", () => {
  for (const media of ["text/vnd.domainspec.fol-core", "text/plain"]) {
    const current = claim(); current.canonical_proposition.representation_media_type = media;
    assert.deepEqual(checkFormalClaimSourceProposition(current, profile), { status: "unsupported", reason: "profile-or-media-type" });
  }
  assert.deepEqual(checkFormalClaimSourceProposition(claim(), { ...profile, result_semantics: "changed" }),
    { status: "unsupported", reason: "profile-or-media-type" });
});

test("unsupported media cannot conceal malformed source shape or stale identity", () => {
  const missing = claim();
  missing.canonical_proposition.representation_media_type = "text/plain";
  delete (missing.canonical_proposition as { representation?: string }).representation;
  assert.throws(() => checkFormalClaimSourceProposition(missing, profile), /FOL_SOURCE_SHAPE/);
  const stale = claim();
  stale.canonical_proposition.representation_media_type = "text/plain";
  stale.canonical_proposition.semantic_identity_digest = "0".repeat(64);
  assert.throws(() => checkFormalClaimSourceProposition(stale, profile), /FOL_SOURCE_IDENTITY/);
  const malformedSignature = claim();
  malformedSignature.canonical_proposition.representation_media_type = "text/plain";
  malformedSignature.formal_signature.sorts = null as never;
  assert.throws(() => checkFormalClaimSourceProposition(malformedSignature, profile), /FOL_SOURCE_SHAPE/);
});
