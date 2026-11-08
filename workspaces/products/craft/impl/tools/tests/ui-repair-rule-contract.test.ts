import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  assertCriterionPreflight,
  assertNoDuplicateSchemaKey,
  UI_REPAIR_VIOLATION_CODES,
  UI_REPAIR_VIOLATION_REGISTRY,
} from "../lib/ui-repair-rule-contract";

const thisDir = dirname(fileURLToPath(import.meta.url));
const repairRoot = resolve(thisDir, "../../../development/ui-meta-type-repair");

test("v1 registry exposes the ratified repair codes", () => {
  assert.equal(UI_REPAIR_VIOLATION_REGISTRY, "ui-repair-violations/v1");
  assert.deepEqual(UI_REPAIR_VIOLATION_CODES, [
    "ATTRIBUTE-MISSING",
    "ATTRIBUTE-EMPTY",
    "ATTRIBUTE-WHITESPACE",
    "DUPLICATE-KEY",
    "CRITERIA-CONFLICT",
    "FIXED-VALUE-MISMATCH",
    "NONSTRING-VALUE",
    "UNKNOWN-RULE",
  ]);

  const registry = JSON.parse(
    readFileSync(resolve(repairRoot, "contracts/ui-repair-violations-v1.yml"), "utf8"),
  ) as { registry_id: string; codes: Record<string, string> };
  assert.equal(registry.registry_id, UI_REPAIR_VIOLATION_REGISTRY);
  assert.deepEqual(Object.keys(registry.codes), [...UI_REPAIR_VIOLATION_CODES]);
});

test("duplicate/conflict extension manifest is finite and unique", () => {
  const manifest = JSON.parse(
    readFileSync(resolve(repairRoot, "fixtures/contracts/duplicate-conflict-manifest.json"), "utf8"),
  ) as { cases: Array<{ id: string; kind: string }> };
  assert.equal(manifest.cases.length, 8);
  assert.equal(new Set(manifest.cases.map((entry) => entry.id)).size, manifest.cases.length);
  assert.deepEqual(
    Object.fromEntries(["duplicate", "conflict", "non-conflict"].map((kind) => [kind, manifest.cases.filter((entry) => entry.kind === kind).length])),
    { duplicate: 3, conflict: 3, "non-conflict": 2 },
  );
});

test("duplicate keys fail closed with no precedence", () => {
  assert.throws(
    () => assertNoDuplicateSchemaKey({ rule: "attribute-present" }, "rule", "fixture.yml", 4),
    /ui-repair-violations\/v1:DUPLICATE-KEY.*no precedence/,
  );
});

test("unknown rules fail schema preflight", () => {
  assert.throws(
    () => assertCriterionPreflight({ probe: { rule: "attribute-maybe" } }, "fixture.yml"),
    /ui-repair-violations\/v1:UNKNOWN-RULE.*attribute-maybe/,
  );
});

test("finite contradictory criterion forms fail preflight", () => {
  const cases = [
    {
      first: { rule: "attribute-equals", key: "scope", value: "local" },
      second: { rule: "attribute-equals", key: "scope", value: "global" },
    },
    {
      first: { rule: "attribute-equals", key: "scope", value: "external" },
      second: { rule: "attribute-one-of", key: "scope", values: ["local", "global"] },
    },
    {
      first: { rule: "attribute-one-of", key: "scope", values: ["local"] },
      second: { rule: "attribute-one-of", key: "scope", values: ["global"] },
    },
  ];
  for (const criteria of cases) {
    assert.throws(
      () => assertCriterionPreflight(criteria, "fixture.yml"),
      /ui-repair-violations\/v1:CRITERIA-CONFLICT/,
    );
  }
});

test("compatible presence, equality, and overlapping sets pass preflight", () => {
  assert.doesNotThrow(() =>
    assertCriterionPreflight(
      {
        present: { rule: "attribute-present", key: "scope" },
        fixed: { rule: "attribute-equals", key: "scope", value: "local" },
        admitted: { rule: "attribute-one-of", key: "scope", values: ["local", "global"] },
        overlapping: { rule: "attribute-one-of", key: "scope", values: ["local", "other"] },
      },
      "fixture.yml",
    ),
  );
});
