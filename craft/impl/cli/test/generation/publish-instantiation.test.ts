import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import type { InstantiationPlanV1 } from "../../src/generation/contracts.ts";
import { planInstantiation } from "../../src/generation/plan-instantiation.ts";
import { PublicationError, publishInstantiation } from "../../src/generation/publish-instantiation.ts";
import { loadProjectNode } from "../../src/input/project-model.ts";
import { sha256 } from "../../src/input/source-manifest.ts";
import { testPlan } from "../helpers/plans.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const sourceFixtureRoot = path.resolve(testDir, "../../fixtures/input-roots/canonical-project");

function sandbox(): string {
  return fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-publish-"));
}

function clean(root: string): void {
  assert.equal(root.startsWith(path.join(os.tmpdir(), "mtcli-publish-")), true);
  fs.rmSync(root, { recursive: true, force: true });
}

function expectCode(action: () => unknown, code: string): void {
  assert.throws(action, (error) => error instanceof PublicationError && error.code === code);
}

function inventory(root: string): readonly Readonly<{ relative_path: string; sha256: string }>[] {
  const visit = (relative = ""): Array<Readonly<{ relative_path: string; sha256: string }>> => fs.readdirSync(path.join(root, relative), { withFileTypes: true })
    .sort((left, right) => left.name.localeCompare(right.name))
    .flatMap((entry) => {
      const child = relative ? `${relative}/${entry.name}` : entry.name;
      return entry.isDirectory() ? visit(child) : [{ relative_path: child, sha256: sha256(fs.readFileSync(path.join(root, child))) }];
    });
  return Object.freeze(visit());
}

test("publication atomically creates the declared target and receipt", () => {
  const root = sandbox();
  const target = path.join(root, "target");
  try {
    const result = publishInstantiation(testPlan("Entity"), target);
    assert.equal(result.target_root, target);
    assert.equal(fs.existsSync(path.join(target, result.receipt_path)), true);
    assert.equal(fs.readFileSync(path.join(target, result.receipt.artifacts[0]!.relative_path), "utf8").includes("export class Account"), true);
    assert.deepEqual(fs.readdirSync(root), ["target"]);
  } finally {
    clean(root);
  }
});

test("State Machine materialization and receipt are byte-identical across two targets", () => {
  const root = sandbox();
  const left = path.join(root, "left");
  const right = path.join(root, "right");
  try {
    const leftResult = publishInstantiation(testPlan("State Machine"), left);
    const rightResult = publishInstantiation(testPlan("State Machine"), right);
    assert.deepEqual(inventory(left), inventory(right));
    assert.equal(leftResult.receipt.receipt_sha256, rightResult.receipt.receipt_sha256);
    assert.equal(leftResult.receipt.generator_id, "domainspec.generator/DS-D1.14/typescript/v2");
    assert.deepEqual(leftResult.receipt.semantic_contract.body, rightResult.receipt.semantic_contract.body);
    assert.deepEqual(leftResult.receipt.semantic_contract.relationships, rightResult.receipt.semantic_contract.relationships);
  } finally {
    clean(root);
  }
});

test("all connected L1 contracts materialize byte-identically in three languages", () => {
  const selectors = ["alpha:customer", "beta:settlement-details", "beta:settlement-method", "beta:settlement-completed", "alpha:settlement-api"];
  const root = sandbox();
  try {
    for (const selector of selectors) for (const language of ["typescript", "python", "rust"] as const) {
      const node = loadProjectNode(sourceFixtureRoot, selector);
      const suffix = `${selector.replace(":", "-")}-${language}`;
      const left = path.join(root, `${suffix}-left`);
      const right = path.join(root, `${suffix}-right`);
      const leftResult = publishInstantiation(planInstantiation(node, language), left);
      const rightResult = publishInstantiation(planInstantiation(node, language), right);
      assert.deepEqual(inventory(left), inventory(right));
      assert.equal(leftResult.receipt.receipt_sha256, rightResult.receipt.receipt_sha256);
      assert.deepEqual(leftResult.receipt.semantic_contract.body, rightResult.receipt.semantic_contract.body);
    }
  } finally {
    clean(root);
  }
});

test("traversal, overwrite, and symlinked parents fail closed", () => {
  const root = sandbox();
  try {
    const plan = testPlan("Entity");
    const artifact = plan.artifacts[0]!;
    const traversal = { ...plan, artifacts: [{ ...artifact, relative_path: "../escape.ts" }] } as InstantiationPlanV1;
    expectCode(() => publishInstantiation(traversal, path.join(root, "traversal")), "MTCLI_PUBLISH_PATH");
    assert.equal(fs.existsSync(path.join(root, "escape.ts")), false);

    const existing = path.join(root, "existing");
    fs.mkdirSync(existing);
    fs.writeFileSync(path.join(existing, "sentinel"), "preserve");
    expectCode(() => publishInstantiation(plan, existing), "MTCLI_PUBLISH_EXISTS");
    assert.equal(fs.readFileSync(path.join(existing, "sentinel"), "utf8"), "preserve");

    const realParent = path.join(root, "real-parent");
    const aliasParent = path.join(root, "alias-parent");
    fs.mkdirSync(realParent);
    fs.symlinkSync(realParent, aliasParent, "dir");
    expectCode(() => publishInstantiation(plan, path.join(aliasParent, "target")), "MTCLI_PUBLISH_SYMLINK");
  } finally {
    clean(root);
  }
});

test("a staging failure leaves no target or staging residue", () => {
  const root = sandbox();
  const target = path.join(root, "target");
  try {
    const plan = testPlan("Entity");
    const first = { relative_path: "collision", content: "file", size_bytes: 4, sha256: sha256("file") };
    const second = { relative_path: "collision/child", content: "child", size_bytes: 5, sha256: sha256("child") };
    const hostile = { ...plan, artifacts: [first, second] } as InstantiationPlanV1;
    expectCode(() => publishInstantiation(hostile, target), "MTCLI_PUBLISH_ATOMIC");
    assert.equal(fs.existsSync(target), false);
    assert.deepEqual(fs.readdirSync(root), []);
  } finally {
    clean(root);
  }
});
