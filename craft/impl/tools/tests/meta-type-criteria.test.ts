import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  type Criterion,
  type CriterionSubject,
  evaluateCriteria,
  loadMetaTypeSchemas,
  parseMetaTypeYaml,
  preflightCriteria,
} from "../lib/meta-type-criteria";

const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../");

test("the live backend inventory is exactly 13 schemas and 16 criteria across eight rules", () => {
  const loaded = loadMetaTypeSchemas(resolve(implRoot, "spec/meta-types"));
  const backend = loaded.filter((entry) => !entry.path.includes("/ui/"));
  const criteria = backend.flatMap((entry) => Object.values(entry.schema.criterion ?? {}));

  assert.equal(backend.length, 13);
  assert.equal(criteria.length, 16);
  assert.deepEqual(
    [...new Set(criteria.map((criterion) => criterion.rule))].sort(),
    [
      "all-nonempty",
      "at-least-one",
      "attribute-equals",
      "attribute-one-of",
      "attribute-present",
      "none",
      "section-contains",
      "table-has-column",
    ],
  );
  assert.equal(loaded.length, 22, "the shared loader must also preserve nine committed UI schemas");
});

test("the bounded YAML reader rejects every unsupported or ambiguous parser form", () => {
  const invalid: Array<[string, string]> = [
    ["meta_type:\tProbe\n", "tabs are not allowed"],
    ["meta_type: Probe\n criterion:\n", "two-space steps"],
    ["meta_type: Probe\n    rule: none\n", "malformed indentation"],
    ["meta_type: Probe\nitems:\n  - one\n", "block sequences"],
    ["meta_type: {name: Probe}\n", "flow maps"],
    ["meta_type: Probe\nvalues: [one, two\n", "malformed flow list"],
    ['meta_type: "Probe\n', "unmatched scalar quote"],
    ["meta_type: Probe\nmeta_type: Other\n", "DUPLICATE-KEY"],
  ];

  for (const [raw, message] of invalid) {
    assert.throws(() => parseMetaTypeYaml(raw, "fixture.yml"), new RegExp(message));
  }
});

test("criterion preflight requires fields and non-empty options before evaluation", () => {
  const invalid: Array<[Record<string, unknown>, string]> = [
    [{ probe: {} }, "UNKNOWN-RULE"],
    [{ probe: { rule: "attribute-maybe" } }, "UNKNOWN-RULE"],
    [{ probe: { rule: "at-least-one", truthy: ["yes"] } }, "non-empty 'column'"],
    [{ probe: { rule: "at-least-one", column: "Identity", truthy: [] } }, "non-empty 'truthy'"],
    [{ probe: { rule: "section-contains" } }, "non-empty 'pattern'"],
    [{ probe: { rule: "attribute-equals", key: "mode" } }, "non-empty 'value'"],
    [{ probe: { rule: "attribute-one-of", key: "mode", values: [] } }, "non-empty 'values'"],
  ];
  for (const [criteria, message] of invalid) {
    assert.throws(() => preflightCriteria(criteria, "fixture.yml"), new RegExp(message));
  }

  assert.throws(
    () =>
      preflightCriteria(
        {
          fixed: { rule: "attribute-equals", key: "mode", value: "external" },
          options: { rule: "attribute-one-of", key: "mode", values: ["local"] },
        },
        "fixture.yml",
      ),
    /CRITERIA-CONFLICT/,
  );
});

test("all eight BTE rule forms produce stable ordered structured violations", () => {
  const criteria: Record<string, Criterion> = {
    identity: { rule: "at-least-one", column: "Identity", truthy: ["yes"] },
    no_secret: { rule: "none", column: "Secret", truthy: ["yes"] },
    typedness: { rule: "all-nonempty", column: "Type" },
    equality: { rule: "section-contains", pattern: "equal by value" },
    value_table: { rule: "table-has-column", column: "Value" },
    fixed_mode: { rule: "attribute-equals", key: "mode", value: "strict" },
    owner: { rule: "attribute-present", key: "owner" },
    scope: { rule: "attribute-one-of", key: "scope", values: ["local", "global"] },
  };
  const subject: CriterionSubject = {
    kind: "normalized",
    path: "fixture#Probe",
    text: "different prose",
    table: { columns: ["Other"], rows: [["x"]] },
    columns: {
      Identity: ["no"],
      Secret: ["yes"],
      Type: ["String", "  "],
    },
    attributes: [
      { key: "mode", value: "relaxed" },
      { key: "scope", value: "external" },
    ],
  };

  const violations = evaluateCriteria("schemas/probe.schema.yml", criteria, subject);
  assert.deepEqual(
    violations.map((violation) => violation.code),
    [
      "AT-LEAST-ONE-UNSATISFIED",
      "NONE-VIOLATED",
      "ALL-NONEMPTY-VIOLATED",
      "SECTION-PATTERN-MISSING",
      "TABLE-COLUMN-MISSING",
      "ATTRIBUTE-VALUE-MISMATCH",
      "ATTRIBUTE-MISSING",
      "ATTRIBUTE-VALUE-NOT-ALLOWED",
    ],
  );
  assert.deepEqual(
    violations.map(({ schemaPath, criterionId, rule, subjectPath }) => ({
      schemaPath,
      criterionId,
      rule,
      subjectPath,
    })),
    Object.entries(criteria).map(([criterionId, criterion]) => ({
      schemaPath: "schemas/probe.schema.yml",
      criterionId,
      rule: criterion.rule,
      subjectPath: "fixture#Probe",
    })),
  );
});

test("all eight BTE rule forms pass through one normalized subject", () => {
  const criteria: Record<string, Criterion> = {
    identity: { rule: "at-least-one", column: "Identity", truthy: ["yes"] },
    no_secret: { rule: "none", column: "Secret", truthy: ["yes"] },
    typedness: { rule: "all-nonempty", column: "Type" },
    equality: { rule: "section-contains", pattern: "equal by value" },
    value_table: { rule: "table-has-column", column: "Value" },
    fixed_mode: { rule: "attribute-equals", key: "mode", value: "strict" },
    owner: { rule: "attribute-present", key: "owner" },
    scope: { rule: "attribute-one-of", key: "scope", values: ["local", "global"] },
  };
  const subject: CriterionSubject = {
    kind: "normalized",
    path: "fixture#Probe",
    text: "Two probes are equal by value.",
    table: { columns: ["Value"], rows: [["A"]] },
    columns: {
      Identity: ["yes"],
      Secret: ["no"],
      Type: ["String", "Uuid"],
    },
    attributes: [
      { key: "mode", value: "STRICT" },
      { key: "owner", value: 0 },
      { key: "scope", value: "GLOBAL" },
    ],
  };
  assert.deepEqual(evaluateCriteria("schemas/probe.schema.yml", criteria, subject), []);
});

test("normalization keeps missing, empty, whitespace, false, and zero distinct", () => {
  const scalarCriteria: Record<string, Criterion> = {
    false_fixed: { rule: "attribute-equals", key: "enabled", value: false },
    zero_fixed: { rule: "attribute-equals", key: "count", value: 0 },
    false_present: { rule: "attribute-present", key: "enabled" },
    zero_present: { rule: "attribute-present", key: "count" },
    nonempty_values: { rule: "all-nonempty", column: "Value" },
  };
  const passSubject: CriterionSubject = {
    kind: "normalized",
    path: "fixture#scalars",
    attributes: [
      { key: "enabled", value: false },
      { key: "count", value: 0 },
    ],
    columns: { Value: [false, 0] },
  };
  assert.deepEqual(evaluateCriteria("schema.yml", scalarCriteria, passSubject), []);

  const missing = evaluateCriteria(
    "schema.yml",
    { probe: { rule: "attribute-present", key: "value" } },
    { kind: "normalized", path: "missing", attributes: [] },
  );
  const empty = evaluateCriteria(
    "schema.yml",
    { probe: { rule: "attribute-equals", key: "value", value: "x" } },
    { kind: "normalized", path: "empty", attributes: [{ key: "value", value: "" }] },
  );
  const whitespace = evaluateCriteria(
    "schema.yml",
    { probe: { rule: "attribute-equals", key: "value", value: "x" } },
    { kind: "normalized", path: "whitespace", attributes: [{ key: "value", value: "  " }] },
  );
  assert.equal(missing[0]?.code, "ATTRIBUTE-MISSING");
  assert.equal(empty[0]?.code, "ATTRIBUTE-EMPTY");
  assert.equal(whitespace[0]?.code, "ATTRIBUTE-WHITESPACE");
});

test("Markdown and instance adapters report the same result for equivalent subjects", () => {
  const dir = mkdtempSync(join(tmpdir(), "dsv2-kernel-parity-"));
  try {
    const schema = [
      "meta_type: Parity Probe",
      "criterion:",
      "  identity:",
      "    rule: at-least-one",
      "    column: Identity",
      "    truthy: [yes]",
      "  typedness:",
      "    rule: all-nonempty",
      "    column: Type",
      "  marker:",
      "    rule: section-contains",
      "    pattern: parity-marker",
      "  mode:",
      "    rule: attribute-equals",
      "    key: mode",
      "    value: strict",
      "",
    ].join("\n");
    const markdown = [
      "# fixture",
      "",
      "## Concept Registry",
      "| Concept | Type |",
      "| --- | --- |",
      "| Probe | Parity Probe |",
      "",
      "## Probe",
      "parity-marker",
      "",
      "| Attribute | Value | Identity | Type |",
      "| --- | --- | --- | --- |",
      "| mode | strict | yes | String |",
      "",
    ].join("\n");
    const instance = [
      "meta_type: Parity Probe",
      "concept: Probe",
      "marker: parity-marker",
      "field_identity: [yes]",
      "field_type: [String]",
      "attributes:",
      "  mode: strict",
      "",
    ].join("\n");
    const schemaPath = join(dir, "parity.schema.yml");
    const markdownPath = join(dir, "aspect.md");
    const instancePath = join(dir, "probe.instance.yml");
    writeFileSync(schemaPath, schema, "utf8");
    writeFileSync(markdownPath, markdown, "utf8");
    writeFileSync(instancePath, instance, "utf8");

    const contentResult = run("tools/validate-content.ts", [
      "--schema-dir",
      dir,
      "--file",
      markdownPath,
    ]);
    const instanceResult = run("tools/instances.ts", [
      "validate",
      "--schema-dir",
      dir,
      "--file",
      instancePath,
    ]);
    assert.equal(contentResult.status, 0, contentResult.stdout + contentResult.stderr);
    assert.equal(instanceResult.status, 0, instanceResult.stdout + instanceResult.stderr);

    writeFileSync(markdownPath, markdown.replace("| mode | strict | yes |", "| mode | strict | no |"), "utf8");
    writeFileSync(instancePath, instance.replace("field_identity: [yes]", "field_identity: [no]"), "utf8");
    const badContent = run("tools/validate-content.ts", ["--schema-dir", dir, "--file", markdownPath]);
    const badInstance = run("tools/instances.ts", ["validate", "--schema-dir", dir, "--file", instancePath]);
    assert.equal(badContent.status, 1, badContent.stdout + badContent.stderr);
    assert.equal(badInstance.status, 1, badInstance.stdout + badInstance.stderr);
    assert.match(badContent.stdout, /criterion 'identity'/);
    assert.match(badInstance.stdout, /criterion 'identity'/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

function run(tool: string, args: string[]) {
  return spawnSync(process.execPath, ["--import", "tsx", tool, ...args], {
    cwd: implRoot,
    encoding: "utf8",
  });
}
