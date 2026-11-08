import assert from "node:assert/strict";
import {
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

type JsonObject = Record<string, any>;

const here = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(here, "../..");
const adoptionRoot = resolve(
  implRoot,
  "spec/features/financial-settlement/sfol/adoption",
);
const runnerPath = resolve(
  implRoot,
  "tools/run-financial-settlement-sfol.ts",
);
const validatorPath = resolve(
  implRoot,
  "tools/validate-financial-settlement-sfol.ts",
);

test("Financial Settlement executes four DS-SFOL cases and detects eight mutations", () => {
  const run = spawn(runnerPath, ["--skip-bte"]);
  assert.equal(run.status, 0, run.stderr);
  const validate = spawn(validatorPath);
  assert.equal(validate.status, 0, validate.stderr);
  const report = readJson(resolve(adoptionRoot, "adoption-report.json"));
  assert.equal(report.status, "pass");
  assert.equal(report.case_count, 4);
  assert.equal(Object.keys(report.mutations).length, 8);
  assert.deepEqual(
    [...new Set(report.stage_sets.map(({ case_ids }: JsonObject) =>
      JSON.stringify(case_ids),
    ))],
    [JSON.stringify(report.stage_sets[0].case_ids)],
  );
  assert.equal(report.core_path_audit.status, "pass");
});

test("adoption fixtures and bindings contain no expected-value oracle", () => {
  const pure = readJson(resolve(adoptionRoot, "pure-evidence.json"));
  const effect = readJson(resolve(adoptionRoot, "effect-evidence.json"));
  const executionInputs = JSON.stringify({
    pure: {
      fixtures: pure.fixtures,
      bindings: pure.bindings,
    },
    effect: {
      fixture: effect.fixture,
      bindings: effect.bindings,
    },
  });
  assert.doesNotMatch(
    executionInputs,
    /expected(?:_|")|oracle|acceptance|verdict/i,
  );
});

test("adoption validator rejects an inflated full-coverage claim", () => {
  const temporary = mkdtempSync(
    resolve(tmpdir(), "financial-settlement-sfol-adoption-"),
  );
  try {
    const report = readJson(
      resolve(adoptionRoot, "adoption-report.json"),
    );
    report.claims.full_financial_settlement_coverage = true;
    const path = resolve(temporary, "inflated-report.json");
    writeFileSync(path, `${JSON.stringify(report, null, 2)}\n`);
    const validation = spawn(validatorPath, ["--report", path]);
    assert.notEqual(validation.status, 0);
    assert.match(
      validation.stdout,
      /claim full_financial_settlement_coverage|report digest/,
    );
  } finally {
    rmSync(temporary, { recursive: true, force: true });
  }
});

test("adoption report keeps BTE structural evidence separate from behavior", () => {
  const report = readJson(resolve(adoptionRoot, "adoption-report.json"));
  assert.deepEqual(report.bte, {
    verifier_status: "pass",
    structural_result: "expected-red",
    behavioral_authority: false,
  });
  assert.equal(report.formal_owner_approval, false);
  assert.equal(report.release_admission, "not-granted");
});

function spawn(
  script: string,
  extra: readonly string[] = [],
): SpawnSyncReturns<string> {
  return spawnSync(
    process.execPath,
    ["--import", "tsx", script, ...extra],
    {
      cwd: implRoot,
      encoding: "utf8",
      maxBuffer: 16 * 1024 * 1024,
    },
  );
}

function readJson(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}
