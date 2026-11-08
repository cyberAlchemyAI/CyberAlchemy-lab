import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { planWholeApplicationV1 } from "../../src/generation/whole-application-v1.ts";
import { publishWholeApplicationV1, verifyWholeApplicationV1, WholeApplicationOutputError } from "../../src/generation/whole-application-output-v1.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const example = path.resolve(here, "../../examples/reconciled-commerce");
const source = JSON.parse(fs.readFileSync(path.join(example, "integrations/application.json"), "utf8"));
const selection = JSON.parse(fs.readFileSync(path.join(example, "selections/typescript.json"), "utf8"));

function fixture(t: test.TestContext): string {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-whole-output-"));
  t.after(() => fs.rmSync(parent, { recursive: true, force: true }));
  return parent;
}

test("L1 publishes one new exact whole-application target and verifies it without mutation", t => {
  const parent = fixture(t);
  const target = path.join(parent, "application");
  const plan = planWholeApplicationV1(path.join(example, "source"), selection, source);
  const publication = publishWholeApplicationV1(plan, target);
  assert.equal(publication.receipt.whole_application_plan_sha256, plan.plan_sha256);
  assert.equal(publication.receipt.artifacts.length, plan.artifacts.length);
  const before = fs.statSync(path.join(target, publication.receipt_path)).mtimeNs;
  const verification = verifyWholeApplicationV1(path.join(example, "source"), selection, source, target);
  assert.equal(verification.result, "pass");
  assert.equal(verification.checks.every(item => item.result === "pass"), true);
  assert.equal(fs.statSync(path.join(target, publication.receipt_path)).mtimeNs, before);
  assert.equal(fs.readdirSync(parent).some(name => name.startsWith(".domainspec-whole-application-")), false);
});

test("L1 publication rejects existing, non-normalized, and changed plans without merging", t => {
  const parent = fixture(t);
  const plan = planWholeApplicationV1(path.join(example, "source"), selection, source);
  const target = path.join(parent, "application");
  fs.mkdirSync(target);
  assert.throws(() => publishWholeApplicationV1(plan, target), (error: unknown) => error instanceof WholeApplicationOutputError && error.code === "DS_WHOLE_APPLICATION_OUTPUT_EXISTS");
  assert.deepEqual(fs.readdirSync(target), []);
  assert.throws(() => publishWholeApplicationV1(plan, `${parent}/application/../other`), WholeApplicationOutputError);
  const changed = { ...plan, plan_sha256: "0".repeat(64) };
  assert.throws(() => publishWholeApplicationV1(changed as never, path.join(parent, "changed")), { code: "DS_WHOLE_APPLICATION_SNAPSHOT" });
});

test("L1 verification reports artifact, receipt, and extra-path drift independently", t => {
  const parent = fixture(t);
  const target = path.join(parent, "application");
  const plan = planWholeApplicationV1(path.join(example, "source"), selection, source);
  publishWholeApplicationV1(plan, target);
  fs.appendFileSync(path.join(target, plan.artifacts[0]!.relative_path), "drift");
  fs.writeFileSync(path.join(target, "extra.txt"), "extra");
  const verification = verifyWholeApplicationV1(path.join(example, "source"), selection, source, target);
  assert.equal(verification.result, "fail");
  assert.equal(verification.checks.find(item => item.id === `artifact:${plan.artifacts[0]!.relative_path}`)?.result, "fail");
  assert.equal(verification.checks.find(item => item.id === "exact-path-inventory")?.result, "fail");
  assert.equal(verification.checks.find(item => item.id === "receipt-current")?.result, "pass");
});

test("L1 verification distinguishes domain, integration, and selection currentness", t => {
  const parent = fixture(t);
  const target = path.join(parent, "application");
  publishWholeApplicationV1(planWholeApplicationV1(path.join(example, "source"), selection, source), target);
  const changedIntegration = structuredClone(source);
  changedIntegration.source_id = "integration-source:reconciled-commerce-l1-drift";
  const integrationReport = verifyWholeApplicationV1(path.join(example, "source"), selection, changedIntegration, target);
  assert.equal(integrationReport.checks.find(item => item.id === "integration-source-current")?.result, "fail");
  assert.equal(integrationReport.checks.find(item => item.id === "domain-source-current")?.result, "pass");
  const changedSelection = structuredClone(selection);
  changedSelection.module_root = "commerce-corpus-drift";
  const selectionReport = verifyWholeApplicationV1(path.join(example, "source"), changedSelection, source, target);
  assert.equal(selectionReport.checks.find(item => item.id === "selection-current")?.result, "fail");
  assert.equal(selectionReport.checks.find(item => item.id === "integration-source-current")?.result, "pass");
  const changedSource = path.join(parent, "changed-source");
  fs.cpSync(path.join(example, "source"), changedSource, { recursive: true });
  const nodePath = path.join(changedSource, "specs/commerce/nodes/integration-inbound.json");
  const node = JSON.parse(fs.readFileSync(nodePath, "utf8"));
  node.body.description += " Drift fixture.";
  fs.writeFileSync(nodePath, `${JSON.stringify(node, null, 2)}\n`);
  const domainReport = verifyWholeApplicationV1(changedSource, selection, source, target);
  assert.equal(domainReport.checks.find(item => item.id === "domain-source-current")?.result, "fail");
  assert.equal(domainReport.checks.find(item => item.id === "integration-source-current")?.result, "pass");
});
