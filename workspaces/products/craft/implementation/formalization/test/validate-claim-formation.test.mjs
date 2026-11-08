import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { checkClaimFormation } from "../validate-claim-formation.mjs";

const sha = value => createHash("sha256").update(value).digest("hex");
const canonical = value => Array.isArray(value) ? `[${value.map(canonical).join(",")}]`
  : value && typeof value === "object" ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`
  : JSON.stringify(value);
const fixtures = JSON.parse(readFileSync(new URL("../fixtures/contract-fixtures.json", import.meta.url)));
const registryBytes = readFileSync(new URL("../profiles/formal-language-profiles.json", import.meta.url));
function materialize(value) {
  if (typeof value === "string" && Object.hasOwn(fixtures.macros, value)) return materialize(fixtures.macros[value]);
  if (Array.isArray(value)) return value.map(materialize);
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, materialize(item)]));
  return value;
}
function setup(t) {
  const root = mkdtempSync(join(tmpdir(), "dsf-formation-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, "fixture"));
  const profilePath = join(root, "fixture/profile.json");
  writeFileSync(profilePath, registryBytes);
  const claimPath = join(root, "fixture/claim.json");
  const claim = materialize(fixtures.bases["formal-claim-source-v4"]);
  const ref = (name, bytes) => ({ path: `fixture/${name}`, sha256: sha(bytes), size_bytes: bytes.length, current: true });
  claim.formal_language_profile_ref = ref("profile.json", registryBytes);
  const ast = { kind: "forall", variable: "x", sort: "Item", body: { kind: "predicate", name: "Holds", arguments: [{ kind: "variable", name: "x", sort: "Item" }] } };
  claim.canonical_proposition.representation_media_type = "text/x-alchlang-fol";
  claim.canonical_proposition.representation = "forall x: Item: Holds(x)";
  claim.canonical_proposition.representation_digest = sha(claim.canonical_proposition.representation);
  claim.canonical_proposition.semantic_identity = canonical(ast);
  claim.canonical_proposition.semantic_identity_digest = sha(claim.canonical_proposition.semantic_identity);
  const request = { schema_version: "domainspec-v2.formal-claim-formation-request/v1-candidate", root_directory: root,
    claim_ref: ref("claim.json", Buffer.from("placeholder")), selected_profile: "fol-core/1-candidate" };
  const write = () => { const bytes = Buffer.from(JSON.stringify(claim)); writeFileSync(claimPath, bytes); request.claim_ref = ref("claim.json", bytes); };
  write();
  return { root, claim, request, claimPath, profilePath, write };
}

test("schema-valid exact FOL source is checked with formation-only ceiling", t => {
  const { request } = setup(t);
  const output = checkClaimFormation(request);
  assert.equal(output.status, "checked", JSON.stringify(output));
  assert.equal(output.authority_effect, "none");
  assert.equal(output.formation.status, "checked");
  assert.match(output.claim_ceiling, /no BusinessMeaning acceptance/);
  assert.equal(output.claim_source.sha256, request.claim_ref.sha256);
  assert.match(output.schema_ref.sha256, /^[a-f0-9]{64}$/);
});

test("CLI preserves checked and rejected JSON exit contracts", t => {
  const { request } = setup(t);
  const entry = new URL("../validate-claim-formation.mjs", import.meta.url);
  const run = (input, args = []) => spawnSync(process.execPath, [entry.pathname, ...args], { input, encoding: "utf8" });
  const good = run(JSON.stringify(request));
  assert.equal(good.status, 0, good.stderr);
  assert.equal(JSON.parse(good.stdout).status, "checked");
  for (const bad of [run("{"), run(JSON.stringify(request), ["--unexpected"])]) {
    assert.equal(bad.status, 2, bad.stderr);
    assert.equal(JSON.parse(bad.stdout).status, "rejected");
  }
});

test("complete v4 schema is checked before formation", t => {
  const { claim, request, write } = setup(t);
  delete claim.business_acceptance_ref;
  write();
  const output = checkClaimFormation(request);
  assert.equal(output.status, "rejected");
  assert.equal(output.code, "CLAIM_SCHEMA");
  assert.match(output.schema_errors.join(" "), /business_acceptance_ref/);
  assert.equal(output.formation, undefined);
});

test("malformed FOL with recomputed source digest rejects", t => {
  const { claim, request, write } = setup(t);
  claim.canonical_proposition.representation = "not a formula at all";
  claim.canonical_proposition.representation_digest = sha(claim.canonical_proposition.representation);
  write();
  const output = checkClaimFormation(request);
  assert.equal(output.status, "rejected");
  assert.notEqual(output.code, "CLAIM_SCHEMA");
});

test("unsupported media is not treated as a checked formula", t => {
  const { claim, request, write } = setup(t);
  claim.canonical_proposition.representation_media_type = "text/vnd.domainspec.fol-core";
  write();
  const output = checkClaimFormation(request);
  assert.equal(output.status, "unsupported", JSON.stringify(output));
  assert.equal(output.formation.status, "unsupported");
});

test("stale claim, stale profile, and symlinked claim reject", t => {
  const { claim, request, claimPath, write } = setup(t);
  request.claim_ref.sha256 = "0".repeat(64);
  assert.equal(checkClaimFormation(request).code, "CLAIM_REF_STALE");
  write();
  claim.formal_language_profile_ref.sha256 = "0".repeat(64);
  write();
  assert.equal(checkClaimFormation(request).status, "rejected");
  rmSync(claimPath);
  symlinkSync("profile.json", claimPath);
  assert.equal(checkClaimFormation(request).status, "rejected");
});
