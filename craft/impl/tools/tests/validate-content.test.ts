import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

// Black-box CLI test (build-from-owned: governance/tags/tools/tests/). Spawns the real validator
// over temp fixtures and asserts exit code + stdout. Schemas resolve from spec/meta-types (default).
const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../../");
const validator = "tools/validate-content.ts";

function runValidator(args: string[]) {
  return spawnSync(process.execPath, ["--import", "tsx", validator, ...args], {
    cwd: implRoot,
    encoding: "utf-8",
  });
}

function withFixture(body: string, run: (file: string) => void): void {
  const dir = mkdtempSync(join(tmpdir(), "dsv2-mt-"));
  try {
    const file = join(dir, "aspect.md");
    writeFileSync(file, body, "utf-8");
    run(file);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

function aspect(concept: string, type: string, rows: string[]): string {
  return [
    "# fixture",
    "",
    "## Concept Registry",
    "| Concept | Type |",
    "| --- | --- |",
    `| ${concept} | ${type} |`,
    "",
    `## ${concept}`,
    "| Field | Type | Required | Identity | Description |",
    "| --- | --- | --- | --- | --- |",
    ...rows,
    "",
  ].join("\n");
}

function attributeAspect(valueRows: string[]): string {
  return [
    "# fixture",
    "",
    "## Concept Registry",
    "| Concept | Type |",
    "| --- | --- |",
    "| Fulfillment | Scoped Workflow |",
    "",
    "## Fulfillment",
    "| Attribute | Value |",
    "| --- | --- |",
    ...valueRows,
    "",
  ].join("\n");
}

function withRuleFixture(
  schemaBody: string,
  aspectBody: string,
  run: (result: ReturnType<typeof runValidator>) => void,
): void {
  const dir = mkdtempSync(join(tmpdir(), "dsv2-rule-"));
  try {
    const schema = join(dir, "scoped-workflow.schema.yml");
    const file = join(dir, "aspect.md");
    writeFileSync(schema, schemaBody, "utf-8");
    writeFileSync(file, aspectBody, "utf-8");
    run(runValidator(["--schema-dir", dir, "--file", file]));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

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

const ENTITY_OK = aspect("PaymentTransaction", "Entity", [
  "| id | UUID | yes | yes | identity |",
  "| amount | Money | yes |  | amount |",
]);

const ENTITY_NO_IDENTITY = aspect("Money", "Entity", [
  "| amount | Decimal | yes |  | amount |",
  "| currency | Currency | yes |  | code |",
]);

const ENTITY_UNTYPED = aspect("Widget", "Entity", [
  "| id | UUID | yes | yes | identity |",
  "| label |  | yes |  | untyped field |",
]);

test("Entity positive fixture passes (exit 0)", () => {
  withFixture(ENTITY_OK, (file) => {
    const r = runValidator(["--file", file]);
    assert.equal(r.status, 0, r.stdout + r.stderr);
    assert.match(r.stdout, /PASS/);
  });
});

test("Entity without identity is rejected as Entity (exit 1, identity violation)", () => {
  withFixture(ENTITY_NO_IDENTITY, (file) => {
    const r = runValidator(["--file", file]);
    assert.equal(r.status, 1, r.stdout + r.stderr);
    assert.match(r.stdout, /identity/);
  });
});

test("Entity with an untyped field is rejected (exit 1, typedness violation)", () => {
  withFixture(ENTITY_UNTYPED, (file) => {
    const r = runValidator(["--file", file]);
    assert.equal(r.status, 1, r.stdout + r.stderr);
    assert.match(r.stdout, /typedness/);
  });
});

test("committed Entity fixtures behave (ok passes, bad rejected)", () => {
  const ok = runValidator(["--file", "spec/__fixtures__/mt/entity-ok.md"]);
  assert.equal(ok.status, 0, ok.stdout + ok.stderr);
  const bad = runValidator(["--file", "spec/__fixtures__/mt/entity-bad.md"]);
  assert.equal(bad.status, 1, bad.stdout + bad.stderr);
});

test("financial-settlement feature checks node criteria and valid relationship edges", () => {
  const r = runValidator(["--file", "spec/features/financial-settlement/SPEC.md"]);
  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /6 edge\(s\) checked/);
});

test("Value Object fixtures behave (ok passes, bad rejected as VO)", () => {
  const ok = runValidator(["--file", "spec/__fixtures__/mt/value-object-ok.md"]);
  assert.equal(ok.status, 0, ok.stdout + ok.stderr);
  const bad = runValidator(["--file", "spec/__fixtures__/mt/value-object-bad.md"]);
  assert.equal(bad.status, 1, bad.stdout + bad.stderr);
  assert.match(bad.stdout, /no_identity/);
});

test("Enum fixtures behave (ok passes, bad rejected as Enum)", () => {
  const ok = runValidator(["--file", "spec/__fixtures__/mt/enum-ok.md"]);
  assert.equal(ok.status, 0, ok.stdout + ok.stderr);
  const bad = runValidator(["--file", "spec/__fixtures__/mt/enum-bad.md"]);
  assert.equal(bad.status, 1, bad.stdout + bad.stderr);
  assert.match(bad.stdout, /value_table/);
});

test("cross-discrimination: identity-bearing concept rejected as Value Object", () => {
  const body =
    aspect("Thing", "Value Object", [
      "| id | UUID | yes | yes | identity |",
      "| name | String | yes |  | label |",
    ]) + "\n**Equality:** two Thing are equal by id.\n";
  withFixture(body, (file) => {
    const r = runValidator(["--file", file]);
    assert.equal(r.status, 1, r.stdout + r.stderr);
    assert.match(r.stdout, /no_identity/);
  });
});

for (const scope of ["intra-feature", "cross-feature"]) {
  test(`attribute-one-of accepts exact admitted scope '${scope}'`, () => {
    withRuleFixture(
      ATTRIBUTE_ONE_OF_SCHEMA,
      attributeAspect([`| SCOPE | ${scope.toUpperCase()} |`]),
      (result) => {
        assert.equal(result.status, 0, result.stdout + result.stderr);
        assert.match(result.stdout, /PASS/);
      },
    );
  });
}

test("attribute-one-of rejects an unknown value without partial matching", () => {
  withRuleFixture(
    ATTRIBUTE_ONE_OF_SCHEMA,
    attributeAspect(["| scope | cross |"]),
    (result) => {
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.stdout, /expected one of \[intra-feature, cross-feature\]/);
    },
  );
});

test("attribute-one-of rejects a missing attribute", () => {
  withRuleFixture(
    ATTRIBUTE_ONE_OF_SCHEMA,
    attributeAspect(["| owner | fulfillment |"]),
    (result) => {
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.stdout, /attribute 'scope' is not declared/);
    },
  );
});

test("attribute-one-of rejects an empty key", () => {
  const malformed = ATTRIBUTE_ONE_OF_SCHEMA.replace("key: scope", 'key: ""');
  withRuleFixture(malformed, attributeAspect(["| scope | intra-feature |"]), (result) => {
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /requires a non-empty 'key'/);
  });
});

test("attribute-one-of rejects an empty values array", () => {
  const malformed = ATTRIBUTE_ONE_OF_SCHEMA.replace(
    "values: [intra-feature, cross-feature]",
    "values: []",
  );
  withRuleFixture(malformed, attributeAspect(["| scope | intra-feature |"]), (result) => {
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /requires a non-empty 'values' string array/);
  });
});

test("content validation rejects an unsupported criterion rule", () => {
  const unsupported = ATTRIBUTE_ONE_OF_SCHEMA.replace("attribute-one-of", "attribute-maybe");
  withRuleFixture(unsupported, attributeAspect(["| scope | intra-feature |"]), (result) => {
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout + result.stderr, /ui-repair-violations\/v1:UNKNOWN-RULE/);
    assert.match(result.stdout + result.stderr, /unsupported rule 'attribute-maybe'/);
  });
});

test("content schema preflight rejects a duplicate key before overwrite", () => {
  for (const duplicateRules of [
    "    rule: attribute-one-of\n    rule: attribute-present",
    "    rule: attribute-present\n    rule: attribute-one-of",
  ]) {
    const duplicate = ATTRIBUTE_ONE_OF_SCHEMA.replace("    rule: attribute-one-of", duplicateRules);
    withRuleFixture(duplicate, attributeAspect(["| scope | intra-feature |"]), (result) => {
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.stdout + result.stderr, /ui-repair-violations\/v1:DUPLICATE-KEY/);
      assert.match(result.stdout + result.stderr, /no precedence is defined/);
    });
  }
});

test("content schema preflight rejects contradictory criteria", () => {
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
  withRuleFixture(conflict, attributeAspect(["| scope | external |"]), (result) => {
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout + result.stderr, /ui-repair-violations\/v1:CRITERIA-CONFLICT/);
    assert.match(result.stdout + result.stderr, /fixed value 'external' is outside/);
  });
});

// MT2 — Behavioral: each type's positive fixture passes, its neighbor-valued negative is rejected.
for (const t of [
  "operation",
  "query",
  "calculation",
  "rule",
  "policy",
  "workflow",
]) {
  test(`Behavioral ${t} fixtures behave (ok passes, bad rejected)`, () => {
    const ok = runValidator(["--file", `spec/__fixtures__/mt/${t}-ok.md`]);
    assert.equal(ok.status, 0, ok.stdout + ok.stderr);
    const bad = runValidator(["--file", `spec/__fixtures__/mt/${t}-bad.md`]);
    assert.equal(bad.status, 1, bad.stdout + bad.stderr);
  });
}

// MT3 (node half) — Connective + Lifecycle. Edge signatures deferred to batch-1 R3.
for (const t of ["interface", "event", "mapping", "state-machine"]) {
  test(`Connective/Lifecycle ${t} fixtures behave (ok passes, bad rejected)`, () => {
    const ok = runValidator(["--file", `spec/__fixtures__/mt/${t}-ok.md`]);
    assert.equal(ok.status, 0, ok.stdout + ok.stderr);
    const bad = runValidator(["--file", `spec/__fixtures__/mt/${t}-bad.md`]);
    assert.equal(bad.status, 1, bad.stdout + bad.stderr);
  });
}
