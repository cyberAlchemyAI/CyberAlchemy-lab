import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  type EdgeMaps,
  type Schema,
  deriveFacts,
  evaluatePairs,
  findUnclassifiedRules,
  normalize,
  summarize,
} from "../lib/meta-type-noncollapse";

// --- helpers -----------------------------------------------------------------------------------
const NO_EDGES: EdgeMaps = { sourceEdges: new Map(), targetEdges: new Map() };
function edges(spec: Record<string, { source?: string[]; target?: string[] }>): EdgeMaps {
  const sourceEdges = new Map<string, Set<string>>();
  const targetEdges = new Map<string, Set<string>>();
  for (const [type, e] of Object.entries(spec)) {
    sourceEdges.set(normalize(type), new Set(e.source || []));
    targetEdges.set(normalize(type), new Set(e.target || []));
  }
  return { sourceEdges, targetEdges };
}
function schema(meta_type: string, criterion: Schema["criterion"]): Schema {
  return { meta_type, criterion };
}
function verdictFor(pairs: ReturnType<typeof evaluatePairs>, a: string, b: string) {
  return pairs.find(
    (p) =>
      (normalize(p.a) === normalize(a) && normalize(p.b) === normalize(b)) ||
      (normalize(p.a) === normalize(b) && normalize(p.b) === normalize(a)),
  );
}

// --- 1. a fresh, unknown duplicate collapses without a privileged named pair --------------------
test("fresh duplicate: two attestation-only types identical but for a declared value collapse", () => {
  const schemas = [
    schema("Widget", { kind: { rule: "attribute-equals", key: "kind", value: "widget" } }),
    schema("Gadget", { kind: { rule: "attribute-equals", key: "kind", value: "gadget" } }),
  ];
  const pairs = evaluatePairs(deriveFacts(schemas, NO_EDGES, new Set()));
  assert.equal(verdictFor(pairs, "Widget", "Gadget")?.verdict, "collapse");
});

// --- 2. structural separation is by a discriminating clause, never a shared byte-identical one ---
test("W-struct separates via identity/no_identity, and a shared typedness clause separates nothing", () => {
  const entity = schema("Entity", {
    identity: { rule: "at-least-one", column: "Identity" },
    typedness: { rule: "all-nonempty", column: "Type" },
  });
  const valueObject = schema("Value Object", {
    no_identity: { rule: "none", column: "Identity" },
    typedness: { rule: "all-nonempty", column: "Type" },
  });
  const distinct = evaluatePairs(deriveFacts([entity, valueObject], NO_EDGES, new Set()));
  assert.equal(verdictFor(distinct, "Entity", "Value Object")?.verdict, "distinct");
  assert.equal(verdictFor(distinct, "Entity", "Value Object")?.via, "W-struct");

  // Two types whose ONLY structural clause is the identical typedness → nothing separates → collapse.
  const a = schema("Aa", { typedness: { rule: "all-nonempty", column: "Type" } });
  const b = schema("Bb", { typedness: { rule: "all-nonempty", column: "Type" } });
  const shared = evaluatePairs(deriveFacts([a, b], NO_EDGES, new Set()));
  assert.equal(verdictFor(shared, "Aa", "Bb")?.verdict, "collapse");
});

// --- 3. the exception lane, not the tag, is what clears the members -----------------------------
test("exception lane: members clear WITH the owner allow-list, collapse WITHOUT it", () => {
  // three types identical except a declared attestation value, no distinguishing edges
  const schemas = [
    schema("Alpha", { d: { rule: "attribute-equals", key: "sort", value: "a" } }),
    schema("Beta", { d: { rule: "attribute-equals", key: "sort", value: "b" } }),
    schema("Gamma", { d: { rule: "attribute-equals", key: "sort", value: "c" } }),
  ];
  const withList = summarize(schemas, NO_EDGES, new Set(["alpha", "beta", "gamma"]));
  assert.deepEqual(withList.exceptionLane.map(normalize).sort(), ["alpha", "beta", "gamma"]);
  assert.equal(withList.collapses.length, 0);

  const withoutList = summarize(schemas, NO_EDGES, new Set());
  assert.equal(withoutList.collapses.length, 3); // Alpha~Beta, Alpha~Gamma, Beta~Gamma
});

// --- 4. anti-cheat: witnesses are invariant under permuting ALL attestation values (closes d1) --
test("anti-tautology: permuting every attestation value never changes any verdict", () => {
  const build = (v1: string, v2: string, v3: string): Schema[] => [
    schema("Entity", {
      identity: { rule: "at-least-one", column: "Identity" },
      note: { rule: "attribute-equals", key: "note", value: v1 },
    }),
    schema("Coordinator Alpha", { scope: { rule: "attribute-equals", key: "scope", value: v2 } }),
    schema("Coordinator Beta", { scope: { rule: "attribute-equals", key: "scope", value: v3 } }),
  ];
  const e = edges({
    Entity: { source: ["owns"] },
    "Coordinator Alpha": { source: ["orchestrates"] },
    "Coordinator Beta": { source: ["orchestrates"] },
  });
  const before = evaluatePairs(deriveFacts(build("x", "cross-feature", "intra-feature"), e, new Set()));
  // flip/permute every attestation value; witnesses must not move
  const after = evaluatePairs(deriveFacts(build("TOTALLY-DIFFERENT", "intra-feature", "cross-feature"), e, new Set()));
  assert.deepEqual(after, before);
  // and the collapse that legitimately rests on no-witness is still there, unmoved
  assert.equal(verdictFor(after, "Coordinator Alpha", "Coordinator Beta")?.verdict, "collapse");
  assert.equal(verdictFor(after, "Entity", "Coordinator Alpha")?.verdict, "distinct");
});

test("attribute-one-of is attestation-only and invariant under allowed-value permutation", () => {
  const build = (values: string[]): Schema[] => [
    schema("Scoped Workflow", {
      scope: { rule: "attribute-one-of", key: "scope", values },
    }),
    schema("Tagged Process", {
      scope: { rule: "attribute-equals", key: "scope", value: "tagged" },
    }),
  ];
  const beforeSchemas = build(["intra-feature", "cross-feature"]);
  const afterSchemas = build(["cross-feature", "intra-feature"]);
  assert.deepEqual(findUnclassifiedRules(beforeSchemas), []);

  const beforeFacts = deriveFacts(beforeSchemas, NO_EDGES, new Set());
  assert.equal(beforeFacts[0]?.attestationOnly, true);
  assert.equal(beforeFacts[0]?.structKeys.size, 0);

  const before = evaluatePairs(beforeFacts);
  const after = evaluatePairs(deriveFacts(afterSchemas, NO_EDGES, new Set()));
  assert.deepEqual(after, before);
  assert.equal(verdictFor(after, "Scoped Workflow", "Tagged Process")?.verdict, "collapse");
});

test("attribute-nonempty/v1 is totally classified as attestation-only", () => {
  const schemas = [
    schema("Nonempty Probe", {
      label: { rule: "attribute-nonempty/v1", key: "label" },
    }),
  ];
  assert.deepEqual(findUnclassifiedRules(schemas), []);
  const facts = deriveFacts(schemas, NO_EDGES, new Set());
  assert.equal(facts[0]?.attestationOnly, true);
  assert.equal(facts[0]?.structKeys.size, 0);
});

// --- 5. the classification is total: an unknown rule keyword is caught ---------------------------
test("classification guard: an unclassified rule keyword is reported", () => {
  const ok = [schema("Enum", { value_table: { rule: "table-has-column", column: "Value" } })];
  assert.equal(findUnclassifiedRules(ok).length, 0);
  const bad = [schema("Weird", { x: { rule: "semantic-parse", column: "Body" } })];
  assert.equal(findUnclassifiedRules(bad).length, 1);
});

// --- 6. W-edge distinguishes on authority-resolved participation, collapses when identical -------
test("W-edge: differing authority participation is distinct; identical participation collapses", () => {
  const op = schema("Operation", { s: { rule: "attribute-equals", key: "state_change", value: "yes" } });
  const query = schema("Query", { s: { rule: "attribute-equals", key: "state_change", value: "no" } });
  const distinct = evaluatePairs(deriveFacts([op, query], edges({ Operation: { source: ["mutates"] }, Query: { source: ["fetches"] } }), new Set()));
  assert.equal(verdictFor(distinct, "Operation", "Query")?.verdict, "distinct");
  assert.equal(verdictFor(distinct, "Operation", "Query")?.via, "W-edge");

  const same = evaluatePairs(deriveFacts([op, query], edges({ Operation: { source: ["mutates"] }, Query: { source: ["mutates"] } }), new Set()));
  assert.equal(verdictFor(same, "Operation", "Query")?.verdict, "collapse");
});

// --- 7. black-box: the current registry passes all acceptance criteria ---------------------------
test("real registry: CLI exits 0 with zero collapse candidates and all checks PASS", () => {
  const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../");
  const run = spawnSync(process.execPath, ["--import", "tsx", "tools/validate-meta-types-noncollapse.ts"], {
    cwd: implRoot,
    encoding: "utf-8",
  });
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.match(run.stdout, /collapse-candidate\(s\): none/);
  assert.match(run.stdout, /all 9 supported keywords mapped/);
  assert.match(run.stdout, /Current registry baseline has no collapse candidates/);
  assert.equal((run.stdout.match(/\[PASS\]/g) || []).length, 5);
  assert.equal((run.stdout.match(/\[FAIL\]/g) || []).length, 0);
});
