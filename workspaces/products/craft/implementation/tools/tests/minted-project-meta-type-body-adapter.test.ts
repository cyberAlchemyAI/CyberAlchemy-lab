import assert from "node:assert/strict";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  MINTED_NODE_BODY_ADAPTER_VERSION,
  mintedNodeBodyToCriterionSubject,
  resolveMintedNodeFormationSchema,
  validateMintedNodeFormation,
} from "../minted-project/meta-type-body-adapter";

const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

test("minted node bodies normalize fields, values, scalar attributes, and named prose", () => {
  const subject = mintedNodeBodyToCriterionSubject(
    {
      fields: [
        { name: "id", type: "string", identity: true },
        { name: "label", type: "", identity: false },
      ],
      values: ["draft", 0, false],
      equality: "Values are equal by fields.",
      enabled: false,
      count: 0,
      ignored_projection: { state_change: "yes" },
    },
    "nodes/probe.json",
  );

  assert.equal(subject.kind, "normalized");
  assert.equal(subject.path, "nodes/probe.json#$.body");
  assert.equal(subject.text, "Values are equal by fields.");
  assert.deepEqual(subject.columns?.Identity, [true, false]);
  assert.deepEqual(subject.columns?.Type, ["string", ""]);
  assert.deepEqual(subject.table, {
    columns: ["Value"],
    rows: [["draft"], [0], [false]],
  });
  assert.deepEqual(subject.attributes, [
    { key: "equality", value: "Values are equal by fields." },
    { key: "enabled", value: false },
    { key: "count", value: 0 },
  ]);
});

test("the adapter passes and fails all eight backend rule forms through live YAML schemas", () => {
  const cases = [
    {
      metaType: "Entity",
      good: { fields: [{ name: "id", type: "string", identity: true }] },
      bad: { fields: [{ name: "id", type: "string", identity: false }] },
      criterionId: "identity",
      rule: "at-least-one",
      code: "AT-LEAST-ONE-UNSATISFIED",
    },
    {
      metaType: "Entity",
      good: { fields: [{ name: "id", type: "string", identity: true }] },
      bad: { fields: [{ name: "id", type: "  ", identity: true }] },
      criterionId: "typedness",
      rule: "all-nonempty",
      code: "ALL-NONEMPTY-VIOLATED",
    },
    {
      metaType: "Value Object",
      good: {
        fields: [{ name: "amount", type: "number", identity: false }],
        equality: "Two values are equal by fields.",
      },
      bad: {
        fields: [{ name: "amount", type: "number", identity: true }],
        equality: "Two values are equal by fields.",
      },
      criterionId: "no_identity",
      rule: "none",
      code: "NONE-VIOLATED",
    },
    {
      metaType: "Value Object",
      good: {
        fields: [{ name: "amount", type: "number", identity: false }],
        equality: "Two values are equal by fields.",
      },
      bad: {
        fields: [{ name: "amount", type: "number", identity: false }],
        equality: "Two values share the same fields.",
        note: "equal must not leak from an unrelated scalar",
      },
      criterionId: "equality",
      rule: "section-contains",
      code: "SECTION-PATTERN-MISSING",
    },
    {
      metaType: "Enum",
      good: { values: ["draft"] },
      bad: { values: [] },
      criterionId: "value_table",
      rule: "table-has-column",
      code: "TABLE-EMPTY",
    },
    {
      metaType: "Operation",
      good: { state_change: "yes" },
      bad: { state_change: "no", ignored_projection: { state_change: "yes" } },
      criterionId: "writes_state",
      rule: "attribute-equals",
      code: "ATTRIBUTE-VALUE-MISMATCH",
    },
    {
      metaType: "Interface",
      good: { interface_kind: "external" },
      bad: {},
      criterionId: "declares_boundary",
      rule: "attribute-present",
      code: "ATTRIBUTE-MISSING",
    },
    {
      metaType: "Workflow",
      good: { scope: "intra-feature" },
      bad: { scope: "global" },
      criterionId: "admitted_scope",
      rule: "attribute-one-of",
      code: "ATTRIBUTE-VALUE-NOT-ALLOWED",
    },
  ] as const;

  for (const entry of cases) {
    assert.deepEqual(
      validateMintedNodeFormation(entry.metaType, entry.good, `nodes/${entry.metaType}.json`),
      [],
      entry.metaType,
    );
    const violations = validateMintedNodeFormation(
      entry.metaType,
      entry.bad,
      `nodes/${entry.metaType}.json`,
    );
    assert.equal(violations.length, 1, entry.metaType);
    assert.equal(violations[0]?.adapterVersion, MINTED_NODE_BODY_ADAPTER_VERSION);
    assert.equal(violations[0]?.criterionId, entry.criterionId);
    assert.equal(violations[0]?.rule, entry.rule);
    assert.equal(violations[0]?.code, entry.code);
    assert.match(violations[0]?.keyword ?? "", new RegExp(`^criterion:${entry.criterionId}:`));
  }
  assert.deepEqual(
    [...new Set(cases.map((entry) => entry.rule))].sort(),
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
});

test("schema selection is canonical, explicit bindings are checked, and digest drift fails closed", () => {
  const operation = resolveMintedNodeFormationSchema("Operation");
  assert.ok(operation);
  assert.match(operation.path, /meta-types\/behavioral\/operation\.schema\.yml$/);

  assert.deepEqual(
    validateMintedNodeFormation(
      "Operation",
      { state_change: "yes" },
      "nodes/operation.json",
      { expectedSchemaSha256: operation.sha256 },
    ),
    [],
  );
  assert.equal(
    validateMintedNodeFormation(
      "Operation",
      { state_change: "yes" },
      "nodes/operation.json",
      { expectedSchemaSha256: "0".repeat(64) },
    )[0]?.code,
    "SCHEMA-DIGEST-MISMATCH",
  );
  assert.equal(
    validateMintedNodeFormation(
      "Operation",
      { state_change: "yes" },
      "nodes/operation.json",
      { schemaPath: resolve(implRoot, "spec/meta-types/connective/interface.schema.yml") },
    )[0]?.code,
    "SCHEMA-META-TYPE-MISMATCH",
  );
  assert.equal(
    validateMintedNodeFormation("Unknown Kind", {}, "nodes/unknown.json")[0]?.code,
    "SCHEMA-MISSING",
  );
});
