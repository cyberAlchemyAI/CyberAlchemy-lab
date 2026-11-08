import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  UiProfileValidationError,
  digestUiProfile,
  loadActiveMetaTypes,
  parseUiProfile,
  validateUiProfile,
  type UiProfile,
  type UiProfileViolationCode,
} from "../validate-ui-profile";

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const profilePath = resolve(implRoot, "spec/ui-profile/profile.yml");
const schemaPath = resolve(implRoot, "spec/ui-profile/profile.schema.json");
const designPath = resolve(
  implRoot,
  "../development/ui-profile-implementation/UI-PROFILE-DESIGN.json",
);
const metaTypesPath = resolve(implRoot, "../definitions/meta-types/meta-types.yml");
const activeMetaTypes = loadActiveMetaTypes(metaTypesPath);
const design = JSON.parse(readFileSync(designPath, "utf8")) as unknown;

function profile(): UiProfile {
  return parseUiProfile(readFileSync(profilePath, "utf8"), profilePath);
}

function expectCode(value: UiProfile, code: UiProfileViolationCode): void {
  assert.throws(
    () => validateUiProfile(value, { activeMetaTypes, design }),
    (error: unknown) => {
      assert.ok(error instanceof UiProfileValidationError);
      assert.equal(error.code, code);
      return true;
    },
  );
}

test("checked-in profile has an exact 11-concept census and stable digest", () => {
  const first = validateUiProfile(profile(), { activeMetaTypes, design });
  const reordered = profile();
  reordered.concepts.reverse();
  reordered.representation_vocabulary.reverse();
  const second = validateUiProfile(reordered, { activeMetaTypes, design });

  assert.equal(first.conceptCount, 11);
  assert.deepEqual(first.representationCounts, { node: 9, alias: 1, split: 1 });
  assert.equal(first.digest, second.digest);
  assert.match(first.digest, /^[a-f0-9]{64}$/);
});

test("current authority resolves Mapping and State Machine as active alias/branch targets", () => {
  assert.equal(activeMetaTypes.get("DS-D1.13"), "Mapping");
  assert.equal(activeMetaTypes.get("DS-D1.14"), "State Machine");
});

test("profile schema is parseable and declares the exact machine contract", () => {
  const schema = JSON.parse(readFileSync(schemaPath, "utf8")) as {
    $schema: string;
    properties: { concepts: { minItems: number; maxItems: number } };
  };
  assert.equal(schema.$schema, "https://json-schema.org/draft/2020-12/schema");
  assert.deepEqual(schema.properties.concepts, {
    type: "array",
    minItems: 11,
    maxItems: 11,
    items: { $ref: "#/$defs/concept" },
  });
});

test("missing and duplicate IDs fail with distinct codes", () => {
  const missing = profile();
  missing.concepts.pop();
  expectCode(missing, "PROFILE-ID-MISSING");

  const duplicate = profile();
  duplicate.concepts[10] = structuredClone(duplicate.concepts[0]);
  expectCode(duplicate, "PROFILE-ID-DUPLICATE");
});

test("unknown placement and confidence values fail independently", () => {
  const placement = profile();
  placement.concepts[0]!.representation = "widget";
  expectCode(placement, "PROFILE-REPRESENTATION-UNKNOWN");

  const confidence = profile();
  confidence.concepts[0]!.confidence = "trusted-because-required";
  expectCode(confidence, "PROFILE-CONFIDENCE-INVALID");
});

test("invalid alias target and alias cycle fail independently", () => {
  const invalid = profile();
  invalid.concepts[9]!.canonical_target = { id: "DS-D1.999", term: "Missing" };
  expectCode(invalid, "PROFILE-ALIAS-TARGET-INVALID");

  const cycle = profile();
  cycle.concepts[9]!.canonical_target = { id: "DS-D1.24", term: "Adapter" };
  expectCode(cycle, "PROFILE-ALIAS-CYCLE");
});

test("split branches require unique identities and resolvable targets", () => {
  const duplicate = profile();
  duplicate.concepts[10]!.branches![1]!.branch_id =
    duplicate.concepts[10]!.branches![0]!.branch_id;
  expectCode(duplicate, "PROFILE-SPLIT-BRANCH-INVALID");

  const unresolved = profile();
  unresolved.concepts[10]!.branches![0]!.target = { id: "DS-D1.999", term: "Missing" };
  expectCode(unresolved, "PROFILE-SPLIT-BRANCH-INVALID");
});

test("Binding cannot be presented as a node without its durable-record condition", () => {
  const value = profile();
  delete value.concepts[8]!.node_condition;
  expectCode(value, "PROFILE-BINDING-CONSTRAINT-INVALID");
});

test("confidence and unsupported fields cannot silently control representation", () => {
  const value = profile() as UiProfile & {
    concepts: Array<UiProfile["concepts"][number] & { confidence_controls?: string }>;
  };
  value.concepts[0]!.confidence_controls = "representation";
  expectCode(value, "PROFILE-CONCEPT-SHAPE-INVALID");
});

test("human design disagreement fails while non-authority semantic mutation changes digest", () => {
  const disagreement = profile();
  disagreement.concepts[0]!.confidence = "mechanically-supported";
  expectCode(disagreement, "PROFILE-DESIGN-MISMATCH");

  const original = profile();
  const mutation = profile();
  mutation.concepts[4]!.constraints = ["framework-neutral-reactive-contract", "typed-effects"];
  assert.notEqual(digestUiProfile(original), digestUiProfile(mutation));
});
