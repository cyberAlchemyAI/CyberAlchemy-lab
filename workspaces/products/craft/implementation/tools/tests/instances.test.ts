import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

// Round-trip: generate canonical example instances from the schemas, then validate them (DEF-D3 source B).
const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../../");
const tool = "tools/instances.ts";

function run(args: string[]) {
  return spawnSync(process.execPath, ["--import", "tsx", tool, ...args], {
    cwd: implRoot,
    encoding: "utf-8",
  });
}

test("generate emits an example instance per schema; every generated instance validates", () => {
  const dir = mkdtempSync(join(tmpdir(), "dsv2-inst-"));
  try {
    const gen = run(["generate", "--out-dir", dir]);
    assert.equal(gen.status, 0, gen.stdout + gen.stderr);
    assert.match(gen.stdout, /generated \d+ example/);
    const val = run(["validate", "--dir", dir]);
    assert.equal(val.status, 0, val.stdout + val.stderr);
    assert.match(val.stdout, /PASS/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("a malformed instance is rejected (Entity example with the identity flag dropped)", () => {
  const dir = mkdtempSync(join(tmpdir(), "dsv2-inst-"));
  try {
    run(["generate", "--out-dir", dir]);
    const entity = readFileSync(join(dir, "entity.example.instance.yml"), "utf-8");
    const mutant = entity.replace(/field_identity: \[[^\]]*\]/, "field_identity: [no, no]");
    assert.notEqual(mutant, entity, "mutation should have changed the instance");
    const mfile = join(dir, "entity-mutant.instance.yml");
    writeFileSync(mfile, mutant, "utf-8");
    const val = run(["validate", "--file", mfile]);
    assert.equal(val.status, 1, val.stdout + val.stderr);
    assert.match(val.stdout, /identity/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

const ATTRIBUTE_ONE_OF_SCHEMA = [
  "meta_type: Scoped Workflow",
  "required_structure:",
  "  attributes_table_columns: [Attribute, Value]",
  "criterion:",
  "  admitted_scope:",
  "    rule: attribute-one-of",
  "    key: scope",
  "    values: [intra-feature, cross-feature]",
  "",
].join("\n");

function scopedWorkflowInstance(scopeLine?: string): string {
  return [
    "meta_type: Scoped Workflow",
    "concept: ExampleScopedWorkflow",
    ...(scopeLine === undefined ? [] : ["attributes:", `  ${scopeLine}`]),
    "",
  ].join("\n");
}

test("attribute-one-of generation is deterministic and chooses the first allowed value", () => {
  const schemaDir = mkdtempSync(join(tmpdir(), "dsv2-schema-"));
  const outDir = mkdtempSync(join(tmpdir(), "dsv2-inst-"));
  try {
    writeFileSync(join(schemaDir, "scoped-workflow.schema.yml"), ATTRIBUTE_ONE_OF_SCHEMA, "utf-8");
    const first = run(["generate", "--schema-dir", schemaDir, "--out-dir", outDir]);
    assert.equal(first.status, 0, first.stdout + first.stderr);
    const file = join(outDir, "scoped-workflow.example.instance.yml");
    const firstBody = readFileSync(file, "utf-8");
    assert.match(firstBody, /scope: intra-feature/);

    const second = run(["generate", "--schema-dir", schemaDir, "--out-dir", outDir]);
    assert.equal(second.status, 0, second.stdout + second.stderr);
    assert.equal(readFileSync(file, "utf-8"), firstBody);

    const validate = run(["validate", "--schema-dir", schemaDir, "--file", file]);
    assert.equal(validate.status, 0, validate.stdout + validate.stderr);
  } finally {
    rmSync(schemaDir, { recursive: true, force: true });
    rmSync(outDir, { recursive: true, force: true });
  }
});

test("attribute-one-of instance validation accepts normalized membership and rejects unknown or missing values", () => {
  const dir = mkdtempSync(join(tmpdir(), "dsv2-inst-rule-"));
  try {
    const schema = join(dir, "scoped-workflow.schema.yml");
    writeFileSync(schema, ATTRIBUTE_ONE_OF_SCHEMA, "utf-8");

    const valid = join(dir, "valid.instance.yml");
    writeFileSync(valid, scopedWorkflowInstance("SCOPE: CROSS-FEATURE"), "utf-8");
    const validResult = run(["validate", "--schema-dir", dir, "--file", valid]);
    assert.equal(validResult.status, 0, validResult.stdout + validResult.stderr);

    const unknown = join(dir, "unknown.instance.yml");
    writeFileSync(unknown, scopedWorkflowInstance("scope: cross"), "utf-8");
    const unknownResult = run(["validate", "--schema-dir", dir, "--file", unknown]);
    assert.equal(unknownResult.status, 1, unknownResult.stdout + unknownResult.stderr);
    assert.match(unknownResult.stdout, /expected one of \[intra-feature, cross-feature\]/);

    const missing = join(dir, "missing.instance.yml");
    writeFileSync(missing, scopedWorkflowInstance(), "utf-8");
    const missingResult = run(["validate", "--schema-dir", dir, "--file", missing]);
    assert.equal(missingResult.status, 1, missingResult.stdout + missingResult.stderr);
    assert.match(missingResult.stdout, /attribute 'scope' is not declared/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("attribute-one-of generation rejects an empty allowed-values list", () => {
  const schemaDir = mkdtempSync(join(tmpdir(), "dsv2-schema-bad-"));
  const outDir = mkdtempSync(join(tmpdir(), "dsv2-inst-bad-"));
  try {
    writeFileSync(
      join(schemaDir, "scoped-workflow.schema.yml"),
      ATTRIBUTE_ONE_OF_SCHEMA.replace("values: [intra-feature, cross-feature]", "values: []"),
      "utf-8",
    );
    const result = run(["generate", "--schema-dir", schemaDir, "--out-dir", outDir]);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stderr, /requires a non-empty 'values' string array/);
  } finally {
    rmSync(schemaDir, { recursive: true, force: true });
    rmSync(outDir, { recursive: true, force: true });
  }
});

test("instance validation rejects an unsupported criterion rule", () => {
  const dir = mkdtempSync(join(tmpdir(), "dsv2-inst-unsupported-"));
  try {
    writeFileSync(
      join(dir, "scoped-workflow.schema.yml"),
      ATTRIBUTE_ONE_OF_SCHEMA.replace("attribute-one-of", "attribute-maybe"),
      "utf-8",
    );
    const file = join(dir, "scoped-workflow.instance.yml");
    writeFileSync(file, scopedWorkflowInstance("scope: intra-feature"), "utf-8");
    const result = run(["validate", "--schema-dir", dir, "--file", file]);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout + result.stderr, /ui-repair-violations\/v1:UNKNOWN-RULE/);
    assert.match(result.stdout + result.stderr, /unsupported rule 'attribute-maybe'/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("instance generation rejects a duplicate schema key before overwrite", () => {
  const schemaDir = mkdtempSync(join(tmpdir(), "dsv2-schema-duplicate-"));
  const outDir = mkdtempSync(join(tmpdir(), "dsv2-inst-duplicate-"));
  try {
    for (const duplicateRules of [
      "    rule: attribute-one-of\n    rule: attribute-present",
      "    rule: attribute-present\n    rule: attribute-one-of",
    ]) {
      const duplicate = ATTRIBUTE_ONE_OF_SCHEMA.replace("    rule: attribute-one-of", duplicateRules);
      writeFileSync(join(schemaDir, "scoped-workflow.schema.yml"), duplicate, "utf-8");
      const result = run(["generate", "--schema-dir", schemaDir, "--out-dir", outDir]);
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.stdout + result.stderr, /ui-repair-violations\/v1:DUPLICATE-KEY/);
    }
  } finally {
    rmSync(schemaDir, { recursive: true, force: true });
    rmSync(outDir, { recursive: true, force: true });
  }
});

test("instance generation rejects contradictory schema criteria", () => {
  const schemaDir = mkdtempSync(join(tmpdir(), "dsv2-schema-conflict-"));
  const outDir = mkdtempSync(join(tmpdir(), "dsv2-inst-conflict-"));
  try {
    const conflict = [
      "meta_type: Scoped Workflow",
      "required_structure:",
      "  attributes_table_columns: [Attribute, Value]",
      "criterion:",
      "  fixed_scope:",
      "    rule: attribute-equals",
      "    key: scope",
      "    value: external",
      "  admitted_scope:",
      "    rule: attribute-one-of",
      "    key: scope",
      "    values: [intra-feature, cross-feature]",
      "",
    ].join("\n");
    writeFileSync(join(schemaDir, "scoped-workflow.schema.yml"), conflict, "utf-8");
    const result = run(["generate", "--schema-dir", schemaDir, "--out-dir", outDir]);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout + result.stderr, /ui-repair-violations\/v1:CRITERIA-CONFLICT/);
  } finally {
    rmSync(schemaDir, { recursive: true, force: true });
    rmSync(outDir, { recursive: true, force: true });
  }
});
