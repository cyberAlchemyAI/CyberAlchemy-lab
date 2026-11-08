import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { composeProviderApplicationV1 } from "../../src/generation/provider-application-v1.ts";
import {
  ProviderApplicationOutputError,
  publishProviderApplicationV1,
  verifyProviderApplicationV1,
} from "../../src/generation/provider-application-output-v1.ts";
import { planWholeApplicationV1 } from "../../src/generation/whole-application-v1.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const example = path.resolve(here, "../../examples/reconciled-commerce");
const source = JSON.parse(fs.readFileSync(path.join(example, "integrations/application.json"), "utf8"));
const selection = JSON.parse(fs.readFileSync(path.join(example, "selections/typescript.json"), "utf8"));
const providers = JSON.parse(fs.readFileSync(path.join(example, "providers/typescript.json"), "utf8"));

function fixture(t: test.TestContext): string {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-provider-output-"));
  t.after(() => fs.rmSync(parent, { recursive: true, force: true }));
  return parent;
}

function plan() {
  const whole = planWholeApplicationV1(path.join(example, "source"), structuredClone(selection), structuredClone(source));
  return composeProviderApplicationV1(whole, structuredClone(providers), structuredClone(source));
}

test("L2 publishes and verifies one exact provider application without mutation", t => {
  const parent = fixture(t);
  const target = path.join(parent, "application");
  const formed = plan();
  const publication = publishProviderApplicationV1(formed, target);
  assert.equal(publication.receipt.provider_application_plan_sha256, formed.plan_sha256);
  assert.equal(publication.receipt.provider_selection_sha256, formed.provider_selection_sha256);
  assert.equal(publication.receipt.artifacts.length, formed.artifacts.length);
  const before = fs.statSync(path.join(target, publication.receipt_path)).mtimeNs;
  const verification = verifyProviderApplicationV1(path.join(example, "source"), selection, source, providers, target);
  assert.equal(verification.result, "pass");
  assert.equal(verification.checks.every(item => item.result === "pass"), true);
  assert.equal(fs.statSync(path.join(target, publication.receipt_path)).mtimeNs, before);
  assert.equal(fs.readdirSync(parent).some(name => name.startsWith(".domainspec-provider-application-")), false);
});

test("L2 provider publication is new-target-only and snapshot-bound", t => {
  const parent = fixture(t);
  const formed = plan();
  const target = path.join(parent, "application");
  fs.mkdirSync(target);
  assert.throws(() => publishProviderApplicationV1(formed, target), (error: unknown) => error instanceof ProviderApplicationOutputError && error.code === "DS_PROVIDER_APPLICATION_OUTPUT_EXISTS");
  assert.deepEqual(fs.readdirSync(target), []);
  assert.throws(() => publishProviderApplicationV1({ ...formed } as never, path.join(parent, "changed")), /DS_PROVIDER_APPLICATION_SNAPSHOT/);
});

test("L2 verification reports provider selection, artifact, and inventory drift causally", t => {
  const parent = fixture(t);
  const target = path.join(parent, "application");
  const formed = plan();
  publishProviderApplicationV1(formed, target);
  const changedProviders = structuredClone(providers);
  changedProviders.selection_id = "provider-selection:reference-typescript-drift";
  const providerReport = verifyProviderApplicationV1(path.join(example, "source"), selection, source, changedProviders, target);
  assert.equal(providerReport.checks.find(item => item.id === "provider-selection-current")?.result, "fail");
  fs.appendFileSync(path.join(target, "migrations/0001_domainspec_reference.sql"), "-- drift\n");
  fs.writeFileSync(path.join(target, "extra.txt"), "extra");
  const artifactReport = verifyProviderApplicationV1(path.join(example, "source"), selection, source, providers, target);
  assert.equal(artifactReport.checks.find(item => item.id === "artifact:migrations/0001_domainspec_reference.sql")?.result, "fail");
  assert.equal(artifactReport.checks.find(item => item.id === "exact-path-inventory")?.result, "fail");
  assert.equal(artifactReport.checks.find(item => item.id === "receipt-current")?.result, "pass");
});
