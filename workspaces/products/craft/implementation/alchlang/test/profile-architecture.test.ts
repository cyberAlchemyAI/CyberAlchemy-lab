import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { ALCH_SOURCE_PROFILE_ARCHITECTURE, selectAlchSourceProfile } from "../src/profile-architecture.js";
import { parseDomainSource } from "../src/parser.js";
import { testTsx } from "./toolchain.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const application = 'domain sample "Sample"\nprofile application-v1\nowner sample-owner\n';
const legacy = 'domain sample "Sample"\nowner sample-owner\n';

test("one closed profile selector distinguishes the product grammar from bounded adapters", () => {
  assert.ok(Object.isFrozen(ALCH_SOURCE_PROFILE_ARCHITECTURE));
  assert.equal(new Set(ALCH_SOURCE_PROFILE_ARCHITECTURE.map(row => row.id)).size, ALCH_SOURCE_PROFILE_ARCHITECTURE.length);
  const product = ALCH_SOURCE_PROFILE_ARCHITECTURE.filter(row => row.product_language);
  assert.deepEqual(product.map(row => row.id), ["application-v1"]);
  assert.equal(product[0]!.parser_owner, "shared-domain-parser");
  assert.equal(product[0]!.normalized_model, "application-v1");
  assert.ok(product[0]!.commands.includes("qualify"));
  for (const row of ALCH_SOURCE_PROFILE_ARCHITECTURE) {
    assert.ok(Object.isFrozen(row)); assert.ok(Object.isFrozen(row.commands)); assert.ok(Object.isFrozen(row.capabilities));
    if (row.parser_owner === "package-local-adapter") assert.equal(row.product_language, false);
  }
  assert.deepEqual(ALCH_SOURCE_PROFILE_ARCHITECTURE.filter(row => row.optional_feature === "rust").map(row => row.id).sort(), ["event-execution-v1", "semantic-host-v1"]);
  assert.deepEqual(ALCH_SOURCE_PROFILE_ARCHITECTURE.filter(row => row.optional_feature === "local-host").map(row => row.id).sort(), ["local-host-migration-v1", "local-host-v1", "ontology-host-v1"]);
  for (const id of ["http-contract-v1", "outbound-invocation-v2"]) {
    const extensionOwned = ALCH_SOURCE_PROFILE_ARCHITECTURE.find(row => row.id === id)!;
    assert.equal(extensionOwned.product_language, false);
    assert.deepEqual(extensionOwned.commands, []);
  }
});

test("CLI selection and semantic parsing share exact application and compatibility identities", () => {
  const selected = selectAlchSourceProfile(application);
  assert.equal(selected.profile.id, "application-v1"); assert.equal(selected.selection, "explicit");
  assert.equal(parseDomainSource(application).source_profile, selected.profile.normalized_model);
  const historical = selectAlchSourceProfile(legacy);
  assert.equal(historical.profile.id, "legacy-sfol-v1"); assert.equal(historical.selection, "historical-default");
  assert.equal(parseDomainSource(legacy).source_profile, historical.profile.id);
  const explicitLegacy = selectAlchSourceProfile(legacy.replace("owner sample-owner", "profile legacy-sfol-v1\nowner sample-owner"));
  assert.equal(explicitLegacy.selection, "explicit");
});

test("profile selection rejects alternate, duplicate and malformed root language claims", () => {
  assert.throws(() => selectAlchSourceProfile(application.replace("application-v1", "unregistered-v1")), /ALCH_PROFILE_UNSUPPORTED/);
  assert.throws(() => selectAlchSourceProfile(application + "profile legacy-sfol-v1\n"), /ALCH_PROFILE_CONFLICT/);
  assert.throws(() => selectAlchSourceProfile(application.replace("profile application-v1", "profile application-v1 extra")), /ALCH_PROFILE_SYNTAX/);
  const adapter = selectAlchSourceProfile(application.replace("application-v1", "function-v1"));
  assert.equal(adapter.profile.role, "capability-adapter"); assert.equal(adapter.profile.product_language, false);
  assert.deepEqual(selectAlchSourceProfile(application.replace("application-v1", "outbound-invocation-v2")).profile.commands, []);
  assert.throws(() => parseDomainSource(application.replace("application-v1", "function-v1")), /TEXT_SYNTAX/);
});

test("CLI rejects commands outside the selected profile contract before another adapter can claim the source", t => {
  const directory = mkdtempSync(path.join(tmpdir(), "alchlang-profile-command-"));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const source = path.join(directory, "application.alch");
  writeFileSync(source, application);
  const result = spawnSync(testTsx(), [path.join(root, "src/cli.ts"), "ontology", source], {
    cwd: root,
    encoding: "utf8",
    env: process.env,
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /ALCH_PROFILE_COMMAND_UNSUPPORTED:application-v1:ontology/);
});
