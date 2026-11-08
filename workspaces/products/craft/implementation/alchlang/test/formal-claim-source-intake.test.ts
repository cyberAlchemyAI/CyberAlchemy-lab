import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { lowerApplicationFormalClaims } from "../src/formal-claim-lowering.js";
import { checkFormalClaimSourceIntake } from "../src/formal-claim-source-intake.js";
import { formalLoweringFixture, source } from "./fixtures/formal-lowering-fixture.js";

const packageRoot = fileURLToPath(new URL("..", import.meta.url));
const registryBytes = readFileSync(new URL("../../../../../../../craft/projects/domainspec-v2/formalization/profiles/formal-language-profiles.json", import.meta.url));
const sha = (bytes: Buffer | string) => createHash("sha256").update(bytes).digest("hex");
const ref = (name: string, bytes: Buffer | string) => ({ path: `fixture/${name}`, sha256: sha(bytes), size_bytes: Buffer.byteLength(bytes), current: true as const });

function setup(t: { after: (callback: () => void) => void }) {
  const root = mkdtempSync(path.join(tmpdir(), "alch-fol-intake-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(path.join(root, "fixture"));
  const fixture = formalLoweringFixture();
  const claim = structuredClone(lowerApplicationFormalClaims(source, fixture.input, fixture.sources).claims[0]!);
  const profileFile = path.join(root, "fixture", "profile.json");
  writeFileSync(profileFile, registryBytes);
  claim.formal_language_profile_ref = ref("profile.json", registryBytes);
  const claimFile = path.join(root, "fixture", "claim.json");
  const request = { schema_version: "alchlang.formal-claim-formation-request/v1", root_directory: root,
    claim_ref: ref("claim.json", "placeholder"), selected_profile: "fol-core/1-candidate" };
  const writeClaim = (value: unknown) => {
    const bytes = Buffer.isBuffer(value) ? value : typeof value === "string" ? value : JSON.stringify(value);
    writeFileSync(claimFile, bytes);
    request.claim_ref = ref("claim.json", bytes);
  };
  writeClaim(claim);
  return { root, claim, request, claimFile, profileFile, writeClaim };
}

const cli = (input: string, extraArgs: string[] = []) => spawnSync(process.execPath,
  ["scripts/run-toolchain.mjs", "tsx", "src/core-cli.ts", "check-formal-claim", ...extraArgs],
  { cwd: packageRoot, input, encoding: "utf8", timeout: 20000 });

test("exact claim and profile bytes yield formation-only checked result", t => {
  const { request } = setup(t);
  const result = checkFormalClaimSourceIntake(request);
  assert.equal(result.status, "checked");
  assert.equal(result.authority_effect, "none");
  assert.deepEqual(result.claim_source, { path: request.claim_ref.path, sha256: request.claim_ref.sha256,
    size_bytes: request.claim_ref.size_bytes });
  assert.match(result.claim_ceiling, /no BusinessMeaning acceptance/);
  const command = cli(JSON.stringify(request));
  assert.equal(command.status, 0, command.stderr);
  assert.deepEqual(JSON.parse(command.stdout), result);
});

test("stale, unsafe and symlink claim references fail closed", t => {
  const { request, claimFile } = setup(t);
  request.claim_ref.sha256 = "0".repeat(64);
  assert.equal(checkFormalClaimSourceIntake(request).status, "rejected");
  request.claim_ref.path = "../claim.json";
  assert.equal(checkFormalClaimSourceIntake(request).status, "rejected");
  request.claim_ref.path = "fixture/claim.json";
  rmSync(claimFile);
  symlinkSync("elsewhere.json", claimFile);
  assert.equal(checkFormalClaimSourceIntake(request).status, "rejected");
});

test("malformed claim bytes or shape reject, not unsupported", t => {
  const { request, writeClaim } = setup(t);
  writeClaim(Buffer.from([0xff]));
  assert.equal(checkFormalClaimSourceIntake(request).code, "CLAIM_SOURCE_JSON");
  writeClaim("{");
  assert.equal(checkFormalClaimSourceIntake(request).code, "CLAIM_SOURCE_JSON");
  writeClaim({schema_version:"historical-v3"});
  assert.equal(checkFormalClaimSourceIntake(request).code, "CLAIM_SOURCE_SHAPE");
});

test("source mutation, profile tampering and unsupported media retain distinct outcomes", t => {
  const { request, claim, profileFile, writeClaim } = setup(t);
  claim.canonical_proposition.representation = "This is malformed";
  claim.canonical_proposition.representation_digest = sha(claim.canonical_proposition.representation);
  writeClaim(claim);
  assert.equal(checkFormalClaimSourceIntake(request).status, "rejected");
  claim.canonical_proposition.representation_media_type = "text/vnd.domainspec.fol-core";
  writeClaim(claim);
  assert.equal(checkFormalClaimSourceIntake(request).status, "unsupported");
  const unsupported = cli(JSON.stringify(request));
  assert.equal(unsupported.status, 3, unsupported.stderr);
  assert.equal(JSON.parse(unsupported.stdout).status, "unsupported");
  writeFileSync(profileFile, Buffer.concat([registryBytes, Buffer.from(" ")]));
  assert.equal(checkFormalClaimSourceIntake(request).status, "rejected");
});

test("CLI rejects malformed and oversized or multiple requests with JSON output", t => {
  const { request } = setup(t);
  for (const input of ["{", `${JSON.stringify(request)}${JSON.stringify(request)}`, "x".repeat(1048577)]) {
    const command = cli(input);
    assert.equal(command.status, 2, command.stderr);
    const result = JSON.parse(command.stdout);
    assert.equal(result.status, "rejected");
    assert.equal(result.authority_effect, "none");
  }
  const extraArgument = cli(JSON.stringify(request), ["--unexpected"]);
  assert.equal(extraArgument.status, 2, extraArgument.stderr);
  assert.deepEqual(JSON.parse(extraArgument.stdout), {
    schema_version: "alchlang.formal-claim-formation-result/v1", status: "rejected",
    authority_effect: "none", claim_ceiling: checkFormalClaimSourceIntake(request).claim_ceiling,
    code: "FORMATION_REQUEST_ARGUMENT",
  });
});
