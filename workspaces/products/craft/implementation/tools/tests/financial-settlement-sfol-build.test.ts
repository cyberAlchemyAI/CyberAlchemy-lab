import assert from "node:assert/strict";
import {
  cpSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import {
  spawnSync,
  type SpawnSyncReturns,
} from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  NODE_PROJECTION_ADMISSION_VERSION,
  projectNodeLogic,
} from "../../test-derivation-engine/src/sfol/node-source/index";

type JsonObject = Record<string, any>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const featureRoot = resolve(
  implRoot,
  "spec/features/financial-settlement",
);
const registryPath = resolve(
  implRoot,
  "spec/sfol-profile/minted-project-profile.json",
);
const scriptPath = resolve(
  implRoot,
  "tools/build-financial-settlement-sfol.ts",
);

function run(
  project: string,
  extra: readonly string[] = [],
): SpawnSyncReturns<string> {
  return spawnSync(
    process.execPath,
    [
      "--import",
      "tsx",
      scriptPath,
      "--project",
      project,
      "--registry",
      registryPath,
      "--verify-only",
      ...extra,
    ],
    {
      cwd: implRoot,
      encoding: "utf8",
    },
  );
}

function projectFixture(): {
  readonly root: string;
  readonly cleanup: () => void;
} {
  const root = mkdtempSync(
    resolve(tmpdir(), "financial-settlement-sfol-build-"),
  );
  cpSync(featureRoot, root, {
    recursive: true,
    filter: (source) => !source.includes("/generated"),
  });
  return {
    root,
    cleanup: () => rmSync(root, { recursive: true, force: true }),
  };
}

function readJson(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}

function writeJson(path: string, value: unknown): void {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

test("Financial Settlement SFOL canonical build verifies twice identically", () => {
  const result = run(featureRoot);
  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(result.stdout) as JsonObject;
  assert.equal(receipt.status, "PASS");
  assert.equal(receipt.deterministic_double_build, true);
  assert.equal(receipt.projected_modules, 2);
  assert.equal(receipt.formal_owner_approval, false);
  assert.equal(receipt.release_admission, "not-granted");
});

test("Financial Settlement SFOL build rejects output path escape", () => {
  const result = run(featureRoot, ["--out", "../escape"]);
  assert.notEqual(result.status, 0);
  assert.match(
    result.stderr,
    /FINANCIAL_SETTLEMENT_SFOL_OUTPUT_INVALID/,
  );
});

test("Financial Settlement SFOL build rejects stale profile digest", () => {
  const fixture = projectFixture();
  try {
    const path = resolve(fixture.root, "project.json");
    const project = readJson(path);
    project.language.profile.digest = "0".repeat(64);
    writeJson(path, project);

    const result = run(fixture.root);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /PROFILE_DIGEST_MISMATCH/);
  } finally {
    fixture.cleanup();
  }
});

test("Financial Settlement SFOL build rejects malformed node logic", () => {
  const fixture = projectFixture();
  try {
    const path = resolve(
      fixture.root,
      "nodes/deal-split-calculation.json",
    );
    const node = readJson(path);
    delete node.body.logic.language_version;
    writeJson(path, node);

    const result = run(fixture.root);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /NODE_LOGIC_SCHEMA_INVALID/);
  } finally {
    fixture.cleanup();
  }
});

test("Financial Settlement SFOL projection rejects duplicate logic ownership", () => {
  const fixture = projectFixture();
  try {
    const calculation = readJson(
      resolve(
        fixture.root,
        "nodes/deal-split-calculation.json",
      ),
    );
    const operationPath = resolve(
      fixture.root,
      "nodes/generate-settlement.json",
    );
    const operation = readJson(operationPath);
    operation.body.logic = calculation.body.logic;
    operation.body.logic.source = {
      feature_id: "financial-settlement",
      node_id: "financial-settlement.GenerateSettlement",
      source_id: "financial-settlement.GenerateSettlement",
      source_path: "nodes/generate-settlement.json",
    };
    rewriteSpanSources(
      operation.body.logic,
      "financial-settlement.GenerateSettlement",
    );
    writeJson(operationPath, operation);

    const result = run(fixture.root);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /SFOL_SOURCE_DUPLICATE_ID/);
  } finally {
    fixture.cleanup();
  }
});

test("Financial Settlement SFOL projection rejects direct AST input", () => {
  const result = projectNodeLogic(
    {
      schema_version: "domainspec-node-logic/v1",
      module_id: "direct-input",
    },
    {
      schema_version: NODE_PROJECTION_ADMISSION_VERSION,
      profile_id: "sfol-development",
      profile_version: "0.1",
      logic_schema_versions: ["domainspec-node-logic/v1"],
      admitted_node_ids: [
        "financial-settlement.DealSplitCalculation",
      ],
    },
  );
  assert.equal(result.ok, false);
  assert.equal(
    result.ok ? "" : result.diagnostics[0]?.code,
    "SFOL_SOURCE_NONCANONICAL",
  );
});

function rewriteSpanSources(
  value: unknown,
  sourceId: string,
): void {
  if (Array.isArray(value)) {
    for (const item of value) rewriteSpanSources(item, sourceId);
    return;
  }
  if (typeof value !== "object" || value === null) return;
  const record = value as JsonObject;
  if (
    Object.hasOwn(record, "source_id") &&
    Object.hasOwn(record, "start") &&
    Object.hasOwn(record, "end")
  ) {
    record.source_id = sourceId;
  }
  for (const child of Object.values(record)) {
    rewriteSpanSources(child, sourceId);
  }
}
