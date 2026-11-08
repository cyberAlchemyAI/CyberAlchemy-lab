import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { lowerApplicationFormalClaims } from "../src/formal-claim-lowering.js";
import { checkFormalClaimSourceBoundary } from "../src/formal-claim-source-boundary.js";
import { formalLoweringFixture, source } from "./fixtures/formal-lowering-fixture.js";

const sha = (bytes: Buffer | string) => createHash("sha256").update(bytes).digest("hex");
const registryBytes = readFileSync(new URL("../../../../../../../craft/projects/domainspec-v2/formalization/profiles/formal-language-profiles.json", import.meta.url));
const profileKey = "fol-core/1-candidate";
const claim = () => {
  const fixture = formalLoweringFixture();
  return structuredClone(lowerApplicationFormalClaims(source, fixture.input, fixture.sources).claims[0]!);
};

function setup(t: { after: (callback: () => void) => void }) {
  const root = mkdtempSync(path.join(tmpdir(), "alch-fol-boundary-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(path.join(root, "fixture"));
  const file = path.join(root, "fixture", "profile.json");
  const current = claim();
  const write = (bytes: Buffer | string) => {
    writeFileSync(file, bytes);
    current.formal_language_profile_ref = {
      path: "fixture/profile.json", sha256: sha(bytes), size_bytes: Buffer.byteLength(bytes), current: true,
    };
  };
  write(registryBytes);
  return { root, file, current, write };
}

test("checks v4 FOL formation only after the exact registry file and selected record match", t => {
  const { root, current } = setup(t);
  assert.deepEqual(checkFormalClaimSourceBoundary(root, current, profileKey), {
    status: "checked", checker: "alchlang-fol/1", selected_profile: profileKey,
    profile_ref_digest: sha(registryBytes),
    representation_digest: current.canonical_proposition.representation_digest,
    ast_digest: current.canonical_proposition.semantic_identity_digest,
  });
});

test("rejects stale, incomplete, unsafe and substituted profile references", t => {
  const { root, file, current } = setup(t);
  writeFileSync(file, Buffer.concat([registryBytes, Buffer.from(" ")]));
  assert.equal(checkFormalClaimSourceBoundary(root, current, profileKey).status, "rejected");
  writeFileSync(file, registryBytes);
  current.formal_language_profile_ref.sha256 = "0".repeat(64);
  assert.equal(checkFormalClaimSourceBoundary(root, current, profileKey).status, "rejected");
  current.formal_language_profile_ref.sha256 = sha(registryBytes);
  (current.formal_language_profile_ref as { current: boolean }).current = false;
  assert.equal(checkFormalClaimSourceBoundary(root, current, profileKey).status, "rejected");
  current.formal_language_profile_ref.current = true;
  current.formal_language_profile_ref.path = "../profile.json";
  assert.equal(checkFormalClaimSourceBoundary(root, current, profileKey).status, "rejected");
  current.formal_language_profile_ref.path = "fixture/profile.json";
  rmSync(file);
  symlinkSync(path.join(root, "elsewhere.json"), file);
  assert.equal(checkFormalClaimSourceBoundary(root, current, profileKey).status, "rejected");
});

test("rejects malformed registry and missing or duplicate selected records", t => {
  const { root, current, write } = setup(t);
  write("{");
  assert.deepEqual(checkFormalClaimSourceBoundary(root, current, profileKey), { status: "rejected", code: "PROFILE_SOURCE_JSON" });
  write("{}");
  assert.deepEqual(checkFormalClaimSourceBoundary(root, current, profileKey), { status: "rejected", code: "PROFILE_REGISTRY_SHAPE" });
  const registry = JSON.parse(registryBytes.toString("utf8"));
  write(JSON.stringify({ ...registry, profiles: registry.profiles.filter((p: { profile_id: string }) => p.profile_id !== "fol-core") }));
  assert.deepEqual(checkFormalClaimSourceBoundary(root, current, profileKey), { status: "rejected", code: "PROFILE_SELECTION_CARDINALITY" });
  const selected = registry.profiles.find((p: { profile_id: string }) => p.profile_id === "fol-core");
  write(JSON.stringify({ ...registry, profiles: [...registry.profiles, selected] }));
  assert.deepEqual(checkFormalClaimSourceBoundary(root, current, profileKey), { status: "rejected", code: "PROFILE_SELECTION_CARDINALITY" });
});

test("rejects missing files and malformed selection keys", t => {
  const { root, file, current } = setup(t);
  assert.deepEqual(checkFormalClaimSourceBoundary(root, current, "../fol-core"), { status: "rejected", code: "PROFILE_SELECTION" });
  rmSync(file);
  assert.deepEqual(checkFormalClaimSourceBoundary(root, current, profileKey), { status: "rejected", code: "PROFILE_SOURCE_IO" });
});

test("a fresh registry digest cannot hide changed selected-profile semantics", t => {
  const { root, current, write } = setup(t);
  const registry = JSON.parse(registryBytes.toString("utf8"));
  const selected = registry.profiles.find((p: { profile_id: string }) => p.profile_id === "fol-core");
  selected.result_semantics = "changed";
  write(JSON.stringify(registry));
  assert.deepEqual(checkFormalClaimSourceBoundary(root, current, profileKey), { status: "unsupported", reason: "profile-or-media-type" });
});

test("unsupported media and selected non-FOL profiles do not pass formation", t => {
  const { root, current } = setup(t);
  for (const media of ["text/vnd.domainspec.fol-core", "text/plain"]) {
    current.canonical_proposition.representation_media_type = media;
    assert.deepEqual(checkFormalClaimSourceBoundary(root, current, profileKey), { status: "unsupported", reason: "profile-or-media-type" });
  }
  current.canonical_proposition.representation_media_type = "text/x-alchlang-fol";
  assert.deepEqual(checkFormalClaimSourceBoundary(root, current, "lean-dtt/1-candidate"), { status: "unsupported", reason: "profile-or-media-type" });
});

test("malformed source and changed AST identity reject even with recomputed source digest", t => {
  const { root, current } = setup(t);
  current.canonical_proposition.representation = "This is malformed";
  current.canonical_proposition.representation_digest = sha(current.canonical_proposition.representation);
  assert.equal(checkFormalClaimSourceBoundary(root, current, profileKey).status, "rejected");
  current.canonical_proposition.representation = "exists o: Order: Eligible(o)";
  current.canonical_proposition.representation_digest = sha(current.canonical_proposition.representation);
  assert.deepEqual(checkFormalClaimSourceBoundary(root, current, profileKey), { status: "rejected", code: "FOL_SOURCE_IDENTITY" });
});
