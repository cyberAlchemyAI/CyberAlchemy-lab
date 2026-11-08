import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { deriveAvailability, listOperationPatterns, requireGeneratablePattern } from "../src/index.js";

const inventoryPath = path.resolve(import.meta.dirname, "../../extensions/generatable-operation-patterns-v1/generated/operation-patterns.generated.json");

test("operation pattern availability is derived from explicit prerequisites", () => {
  const patterns = listOperationPatterns();
  assert.equal(patterns.length, 2);
  for (const pattern of patterns) assert.equal(pattern.availability, deriveAvailability(pattern));
  assert.equal(requireGeneratablePattern("operation-port").generated_artifacts[0], "domain.tools.ts");
});

test("executable registry stays byte-semantically aligned with the ontology inventory", () => {
  const inventory = JSON.parse(readFileSync(inventoryPath, "utf8"));
  assert.equal(inventory.authority_effect, "none");
  assert.deepEqual(inventory.patterns, listOperationPatterns());
});

test("closed effectful patterns can be selected and unknown patterns still fail closed", () => {
  const outbox = listOperationPatterns().find((pattern) => pattern.pattern_id === "transactional-outbox");
  assert.equal(outbox?.availability, "available");
  assert.equal(requireGeneratablePattern("transactional-outbox").pattern_id, "transactional-outbox");
  assert.throws(() => requireGeneratablePattern("unknown-pattern"), /PATTERN_NOT_REGISTERED/);
});
