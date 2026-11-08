import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import test from "node:test";
import { digest, json } from "../src/domainspec-profile.js";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections, assertApplicationRuleProjectionCurrent } from "../src/application-rule-projection.js";
import { formalLoweringFixture } from "./fixtures/formal-lowering-fixture.js";
import { testTypeScript } from "./toolchain.js";

function fixture(proposition = "Eligible(current) and not Blocked(current)") {
  const f = formalLoweringFixture();
  const source = f.source.replace("  proposition forall o: Order: Eligible(o)",
    `  predicate Blocked(Order)\n  constant current: Order\n  proposition ${proposition}`) +
    "entity Order:\n  id UInt64\n  identity id\n  accepted Bool\n  blocked Bool\n";
  const bindings = { schema_version: "alchlang.application-bindings/v1", source_sha256: digest(source), owner: "fixture-owner",
    formal: { ...f.input, source_sha256: digest(source) }, declarations: {
      Order: { ontology: "FIXTURE-ORDER", meaning: "Synthetic order.", properties: {
        id: { ontology: "FIXTURE-ORDER#id", meaning: "Identity." }, accepted: { ontology: "FIXTURE-ORDER#accepted", meaning: "Eligibility." },
        blocked: { ontology: "FIXTURE-ORDER#blocked", meaning: "Block status." } } },
      EligibleOrder: { ontology: "FIXTURE-ELIGIBILITY", meaning: "Eligibility of the explicitly interpreted current order." },
    } };
  const formation = lowerApplicationDomain(source, bindings, f.sources);
  const interpretation = { schema_version: "alchlang.ground-rule-interpretation/v1-candidate", formation_sha256: digest(json(formation)), rules: {
    EligibleOrder: { claim_identity_inputs_digest: formation.trace.declarations.find(c => c.source_id === "EligibleClaim")!.identity_inputs_digest,
      context_id: "fixture-order-properties-v1", ceiling: "Ground current-order condition only; no universal proof.",
      sorts: { Order: "Order" }, constants: { current: "order" }, predicates: { Eligible: "accepted", Blocked: "blocked" } },
  } };
  return { source, bindings, sources: f.sources, interpretation, formation };
}

test("ground projection preserves exact claim identity and remains independent from formation", () => {
  const f = fixture(); const result = lowerApplicationRuleProjections(f.source, f.bindings, f.sources, f.interpretation);
  assert.deepEqual(result, lowerApplicationRuleProjections(f.source, f.bindings, f.sources, structuredClone(f.interpretation)));
  assert.deepEqual(result.formation, f.formation);
  const node = JSON.parse(result.projectFiles["specs/commerce/nodes/eligible-order.json"]!);
  assert.equal(node.body.typed_contract.schema_version, "domainspec.typed-rule/v2");
  assert.equal(node.body.typed_contract.expression.op, "all");
  assert.equal(result.trace.projections[0]!.proof, false);
  const other = structuredClone(f.interpretation); other.rules.EligibleOrder.context_id = "another-context";
  const changed = lowerApplicationRuleProjections(f.source, f.bindings, f.sources, other);
  assert.deepEqual(changed.formation, result.formation);
  assert.notEqual(changed.trace.interpretation_sha256, result.trace.interpretation_sha256);
  assertApplicationRuleProjectionCurrent(f.source, f.bindings, f.sources, f.interpretation, result);
  const mutant = structuredClone(result);
  const target = "specs/commerce/nodes/eligible-order.json";
  const wrong = JSON.parse(mutant.projectFiles[target]!); wrong.body.typed_contract.expression.op = "any";
  mutant.projectFiles[target] = json(wrong);
  mutant.trace.project_files[target] = digest(mutant.projectFiles[target]!);
  mutant.trace.projections[0]!.target_sha256 = mutant.trace.project_files[target];
  assert.throws(() => assertApplicationRuleProjectionCurrent(f.source, f.bindings, f.sources, f.interpretation, mutant), /RULE_PROJECTION_STALE/);
});

test("missing, stale, wrong-sort and nonboolean interpretations reject; quantifiers are never narrowed", () => {
  const f = fixture();
  for (const mutate of [
    (x: any) => { x.formation_sha256 = "0".repeat(64); },
    (x: any) => { x.rules.EligibleOrder.claim_identity_inputs_digest = "0".repeat(64); },
    (x: any) => { delete x.rules.EligibleOrder.predicates.Blocked; },
    (x: any) => { x.rules.EligibleOrder.predicates.Blocked = "id"; },
    (x: any) => { x.rules.EligibleOrder.sorts.Order = "Missing"; },
    (x: any) => { x.rules.EligibleOrder.constants.current = "invalid parameter"; },
  ]) {
    const bad = structuredClone(f.interpretation); mutate(bad);
    assert.throws(() => lowerApplicationRuleProjections(f.source, f.bindings, f.sources, bad), /RULE_PROJECTION_/);
  }
  const q = fixture("forall o: Order: Eligible(o) and Blocked(current)");
  assert.throws(() => lowerApplicationRuleProjections(q.source, q.bindings, q.sources, q.interpretation), /RULE_PROJECTION_UNSUPPORTED/);
  let large = "Eligible(current) and Blocked(current)";
  for (let i = 0; i < 11; i++) large = `(${large}) iff Eligible(current)`;
  const bounded = fixture(large);
  assert.throws(() => lowerApplicationRuleProjections(bounded.source, bounded.bindings, bounded.sources, bounded.interpretation), /RULE_PROJECTION_LIMIT/);
});

test("current DomainSpec emits native TypeScript with the ground proposition truth table", async t => {
  const temp = mkdtempSync(path.join(tmpdir(), "alch-rule-projection-"));
  t.after(() => rmSync(temp, { recursive: true, force: true }));
  const ds = defaultDomainSpecPackageRoot();
  // Test-only imports of the actual backend. Product CLI integration is I07.
  const load = (relative: string) => import(pathToFileURL(path.join(ds, "src", relative)).href);
  const { loadCompiledProjectGraph } = await load("input/project-model.ts");
  const { planConfiguredRules, STRUCTURED_RULE_VERSION } = await load("generation/configured-rules.ts");
  const { getReconciledSource: src } = await load("generation/reconciled-sources.ts");
  const ruleSources = Object.fromEntries(Object.entries({ configuration: "configuration", base: "base", typescript: "typescript",
    rule_contract: "rule", collection_contract: "rule_collection", predicate_contract: "rule_predicate", numeric_contract: "rule_numeric",
    exact_contract: "rule_exact", literal_contract: "rule_literal", structured_contract: "rule_structured", field_contract: "field" }).map(([k, v]) => [k, src(v)]));
  const cases: Array<[string, (a: boolean, b: boolean) => boolean]> = [
    ["Eligible(current) and not Blocked(current)", (a, b) => a && !b],
    ["Eligible(current) or Blocked(current)", (a, b) => a || b],
    ["Eligible(current) implies Blocked(current)", (a, b) => !a || b],
    ["Eligible(current) iff Blocked(current)", (a, b) => a === b],
  ];
  for (const [i, [proposition, expected]] of cases.entries()) {
    const f = fixture(proposition); const projected = lowerApplicationRuleProjections(f.source, f.bindings, f.sources, f.interpretation);
    const root = path.join(temp, String(i));
    for (const [name, bytes] of Object.entries(projected.projectFiles)) {
      const target = path.join(root, "source", name); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
    }
    const graph = loadCompiledProjectGraph(path.join(root, "source"));
    const selection = { schema_version: STRUCTURED_RULE_VERSION, language: "typescript", module_root: "application",
      value_profile: "domainspec.typescript-exact-uint64/v1", roots: ["commerce:eligible-order"] };
    const plan = planConfiguredRules(graph, selection, ruleSources);
    assert.deepEqual(plan, planConfiguredRules(graph, selection, ruleSources));
    for (const artifact of plan.artifacts) {
      const target = path.join(root, artifact.relative_path); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, artifact.content);
    }
    execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs",
      "--rootDir", root, "--outDir", path.join(root, "js"), ...plan.artifacts.map((a: any) => path.join(root, a.relative_path))], { encoding: "utf8" });
    const module = plan.modules[0];
    const run = createRequire(import.meta.url)(path.join(root, "js", module.relative_path.replace(/\.ts$/, ".js")))[module.callable];
    for (const accepted of [false, true]) for (const blocked of [false, true]) {
      assert.equal(run({ order: { id: "1", accepted, blocked } }), expected(accepted, blocked), proposition);
    }
    assert.throws(() => run({ order: { id: "1", accepted: "true", blocked: false } }));
  }
});
