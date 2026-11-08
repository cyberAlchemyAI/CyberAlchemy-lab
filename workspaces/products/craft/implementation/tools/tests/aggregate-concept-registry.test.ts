import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { aggregateConceptRegistry } from "../aggregate-concept-registry";

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const schemaRoot = resolve(implRoot, "spec/meta-types");
const relationshipsPath = resolve(
  implRoot,
  "../definitions/relationships/relationships.yml",
);

test("live project aggregation retains all DS-D1 concepts and validated edges", () => {
  const result = aggregateConceptRegistry({
    featuresRoot: resolve(implRoot, "spec/features"),
    metaTypeSchemaRoot: schemaRoot,
    relationshipsPath,
  });

  assert.equal(result.report.concept_count, 38);
  assert.equal(result.report.edge_count, 35);
  assert.deepEqual(result.report.duplicate_ids, []);
  assert.deepEqual(result.report.type_drift, []);
  assert.deepEqual(result.report.relationship_violations, []);
  assert.deepEqual(
    result.report.excluded_concepts.map((entry) => [entry.concept, entry.type]),
    [["SampleValidationFixture", "Fixture"]],
  );
});

test("aggregation flags a shared authored ID and cross-feature type drift without merging", () => {
  const root = mkdtempSync(resolve(tmpdir(), "domainspec-concept-aggregation-"));
  try {
    for (const [feature, type] of [
      ["feature-a", "Entity"],
      ["feature-b", "Operation"],
    ] as const) {
      const featureRoot = resolve(root, feature);
      mkdirSync(featureRoot, { recursive: true });
      writeFileSync(
        resolve(featureRoot, "SPEC.md"),
        [
          `# ${feature}`,
          "",
          "## Concept Registry",
          "",
          "| Concept | ID | Type |",
          "| --- | --- | --- |",
          `| SharedConcept | shared.concept | ${type} |`,
          "",
          "## Feature Concept Graph",
          "",
          "| From | Edge | To |",
          "| --- | --- | --- |",
          "",
        ].join("\n"),
      );
    }

    const result = aggregateConceptRegistry({
      featuresRoot: root,
      metaTypeSchemaRoot: schemaRoot,
      relationshipsPath,
    });
    assert.equal(result.report.duplicate_ids.length, 1);
    assert.equal(result.report.duplicate_ids[0]?.declarations.length, 2);
    assert.equal(result.report.type_drift.length, 1);
    assert.deepEqual(result.report.type_drift[0]?.types, ["Entity", "Operation"]);
    assert.equal(result.registry["shared.concept"]?.length, 2);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
