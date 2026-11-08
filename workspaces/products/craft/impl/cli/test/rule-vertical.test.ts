import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { pathToFileURL, fileURLToPath } from "node:url";

import { runCli } from "../src/cli/main.ts";
import { planInstantiation } from "../src/generation/plan-instantiation.ts";
import { loadCompiledProjectGraph, loadProjectNode, validateCompiledProjectGraphObligations } from "../src/input/project-model.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const capacityFixture = path.resolve(testDir, "fixtures/capacity-decision");
const canonicalFixture = path.resolve(testDir, "../fixtures/input-roots/canonical-project");

function copyFixture(source: string): { parent: string; root: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-rule-"));
  const root = path.join(parent, "source");
  fs.cpSync(source, root, { recursive: true });
  return { parent, root };
}

function snapshot(root: string): string {
  const rows: string[] = [];
  const visit = (relative: string): void => {
    for (const entry of fs.readdirSync(path.join(root, relative), { withFileTypes: true }).sort((left, right) => left.name.localeCompare(right.name))) {
      const child = relative ? `${relative}/${entry.name}` : entry.name;
      if (entry.isDirectory()) visit(child);
      else rows.push(`${child}\0${fs.readFileSync(path.join(root, child), "hex")}`);
    }
  };
  visit("");
  return rows.join("\n");
}

const parameters = JSON.stringify([{ name: "candidate", type: { kind: "scalar", name: "Bool" } }]);
const expression = JSON.stringify({ op: "eq", left: { op: "path", root: "candidate", properties: [] }, right: { op: "literal", type: "Bool", value: true } });
const addRuleArgs = (root: string): string[] => [
  "add", "rule", root,
  "--feature", "alpha",
  "--name", "candidate-is-true",
  "--description", "The candidate must be exactly true.",
  "--ontology-rule", "ALPHA-RULE-CANDIDATE-TRUE",
  "--parameters-json", parameters,
  "--expression-json", expression,
];

test("add rule atomically authors deterministic typed semantics", () => {
  const left = copyFixture(canonicalFixture);
  const right = copyFixture(canonicalFixture);
  try {
    const manifests: string[] = [];
    for (const root of [left.root, right.root]) {
      const out: string[] = [];
      const errors: string[] = [];
      assert.equal(runCli(addRuleArgs(root), { stdout: (value) => out.push(value), stderr: (value) => errors.push(value) }), 0);
      const receipt = JSON.parse(out.pop()!);
      assert.equal(receipt.schema_version, "domainspec.add-rule-command-result/v1");
      assert.equal(receipt.selector, "alpha:candidate-is-true");
      manifests.push(receipt.source_manifest_sha256);
      assert.deepEqual(errors, []);
      const node = JSON.parse(fs.readFileSync(path.join(root, receipt.node_path), "utf8"));
      assert.equal(node.kind, "Rule");
      assert.equal(node.body.predicate, "structured:domainspec.typed-rule/v1");
      assert.deepEqual(node.body.typed_contract.expression, JSON.parse(expression));
    }
    assert.equal(manifests[0], manifests[1]);
    assert.equal(
      fs.readFileSync(path.join(left.root, "specs/alpha/nodes/candidate-is-true.json"), "utf8"),
      fs.readFileSync(path.join(right.root, "specs/alpha/nodes/candidate-is-true.json"), "utf8"),
    );
  } finally {
    fs.rmSync(left.parent, { recursive: true, force: true });
    fs.rmSync(right.parent, { recursive: true, force: true });
  }
});

test("hostile add rule input leaves the project byte-identical", () => {
  const fixture = copyFixture(canonicalFixture);
  try {
    const before = snapshot(fixture.root);
    const args = addRuleArgs(fixture.root);
    args[args.indexOf(expression)] = JSON.stringify({ op: "eq", left: { op: "path", root: "candidate", properties: ["MISSING-PROPERTY#value"] }, right: { op: "literal", type: "Bool", value: true } });
    const errors: string[] = [];
    assert.equal(runCli(args, { stdout: () => undefined, stderr: (value) => errors.push(value) }), 22);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_TYPED_CLOSURE_PROPERTY");
    assert.equal(snapshot(fixture.root), before);

    const invalid = addRuleArgs(fixture.root);
    invalid[invalid.indexOf(parameters)] = "not-json";
    assert.equal(runCli(invalid, { stdout: () => undefined, stderr: (value) => errors.push(value) }), 22);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_USAGE");
    assert.equal(snapshot(fixture.root), before);
  } finally {
    fs.rmSync(fixture.parent, { recursive: true, force: true });
  }
});

test("compiled Rule graph carries complete applicable DS-D8 predicates and witnesses", () => {
  const graph = loadCompiledProjectGraph(capacityFixture);
  const rule = graph.nodes.find(({ selector }) => selector === "capacity-decision:within-capacity")!;
  const expected = [
    "admit_same_and_cross_feature_scope",
    "reject_enforces_cross_label",
    "reject_non_operation_target",
    "reject_non_rule_source",
  ];
  assert.deepEqual(rule.applicable_obligation_ids, expected);
  const witnesses = graph.obligation_witnesses.filter(({ edge_id }) => edge_id === "within-capacity-enforces-decide-capacity");
  assert.deepEqual(witnesses.map(({ obligation_id }) => obligation_id), expected);
  assert.deepEqual(new Set(witnesses.map(({ family }) => family)), new Set(["endpoint", "scope"]));
  for (const witness of witnesses) {
    assert.equal(witness.predicate.relationship_id, "enforces");
    assert.deepEqual(witness.predicate.allowed_source_types, ["Rule"]);
    assert.deepEqual(witness.predicate.allowed_target_types, ["Operation"]);
    assert.equal(witness.witness.source_selector, rule.selector);
  }
  assert.throws(
    () => validateCompiledProjectGraphObligations({ ...graph, obligation_witnesses: graph.obligation_witnesses.slice(1) }),
    (error: unknown) => (error as { code?: string }).code === "MTCLI_COMPILED_OBLIGATION",
  );
});

test("Rule source changes alter closure and generated bindings while unrelated bytes do not", () => {
  const fixture = copyFixture(capacityFixture);
  try {
    const original = loadProjectNode(fixture.root, "capacity-decision:within-capacity");
    const before = (["typescript", "python", "rust"] as const).map((language) => planInstantiation(original, language));
    const projectPath = path.join(fixture.root, "project.json");
    fs.writeFileSync(projectPath, `${JSON.stringify(JSON.parse(fs.readFileSync(projectPath, "utf8")), null, 4)}\n`);
    const unrelated = loadProjectNode(fixture.root, "capacity-decision:within-capacity");
    const afterUnrelated = (["typescript", "python", "rust"] as const).map((language) => planInstantiation(unrelated, language));
    assert.deepEqual(afterUnrelated.map(({ artifacts }) => artifacts[0]!.sha256), before.map(({ artifacts }) => artifacts[0]!.sha256));

    const rulePath = path.join(fixture.root, "specs/capacity-decision/nodes/within-capacity.json");
    const rule = JSON.parse(fs.readFileSync(rulePath, "utf8"));
    rule.body.typed_contract.expression.op = "eq";
    fs.writeFileSync(rulePath, `${JSON.stringify(rule, null, 2)}\n`);
    const changed = loadProjectNode(fixture.root, "capacity-decision:within-capacity");
    const afterChanged = (["typescript", "python", "rust"] as const).map((language) => planInstantiation(changed, language));
    assert.notEqual(changed.typed_closure?.closure_sha256, original.typed_closure?.closure_sha256);
    for (let index = 0; index < before.length; index += 1) assert.notEqual(afterChanged[index]!.artifacts[0]!.sha256, before[index]!.artifacts[0]!.sha256);

    rule.body.typed_contract.expression.left.properties = ["CAPACITY-SNAPSHOT#missing"];
    fs.writeFileSync(rulePath, `${JSON.stringify(rule, null, 2)}\n`);
    assert.throws(() => loadProjectNode(fixture.root, "capacity-decision:within-capacity"), (error: unknown) => (error as { code?: string }).code === "MTCLI_TYPED_CLOSURE_PROPERTY");
  } finally {
    fs.rmSync(fixture.parent, { recursive: true, force: true });
  }
});

test("TypeScript, Python, and Rust Rule bindings execute the same corpus", async () => {
  const node = loadProjectNode(capacityFixture, "capacity-decision:within-capacity");
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-rule-native-"));
  try {
    const expected = [true, false, false];
    const samples = [[2, 3], [3, 3], [4, 3]];
    const tsPath = path.join(parent, "within-capacity.ts");
    fs.writeFileSync(tsPath, planInstantiation(node, "typescript").artifacts[0]!.content);
    const ts = await import(`${pathToFileURL(tsPath).href}?rule-native`);
    assert.deepEqual(samples.map(([requested_units, available_units]) => ts.withinCapacity({ snapshot: { request_id: "r", requested_units, available_units } })), expected);

    const pyPath = path.join(parent, "within_capacity.py");
    fs.writeFileSync(pyPath, planInstantiation(node, "python").artifacts[0]!.content);
    const pythonProgram = `import importlib.util\ns=importlib.util.spec_from_file_location('rule',${JSON.stringify(pyPath)})\nm=importlib.util.module_from_spec(s)\ns.loader.exec_module(m)\nprint([m.within_capacity({'snapshot':{'request_id':'r','requested_units':a,'available_units':b}}) for a,b in [(2,3),(3,3),(4,3)]])`;
    const python = spawnSync("python3", ["-c", pythonProgram], { encoding: "utf8" });
    assert.equal(python.status, 0, python.stderr);
    assert.equal(python.stdout.trim(), "[True, False, False]");

    const rustPath = path.join(parent, "within_capacity.rs");
    fs.writeFileSync(rustPath, planInstantiation(node, "rust").artifacts[0]!.content);
    const harness = path.join(parent, "main.rs");
    fs.writeFileSync(harness, `mod generated { include!(${JSON.stringify(rustPath)}); }\nfn main(){for (a,b) in [(2,3),(3,3),(4,3)] { let value=generated::CapacitySnapshot{request_id:"r".to_owned(),requested_units:a,available_units:b}; println!("{}",generated::within_capacity(&value)); }}\n`);
    const binary = path.join(parent, "rule-bin");
    const compiled = spawnSync(process.env.RUSTC ?? "rustc", ["--edition", "2024", harness, "-o", binary], { encoding: "utf8" });
    assert.equal(compiled.status, 0, compiled.stderr ?? compiled.error?.message);
    const rust = spawnSync(binary, [], { encoding: "utf8" });
    assert.equal(rust.status, 0, rust.stderr);
    assert.deepEqual(rust.stdout.trim().split("\n"), ["true", "false", "false"]);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("CLI replays Rule instantiation deterministically with valid receipts", () => {
  const leftParent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-rule-cli-left-"));
  const rightParent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-rule-cli-right-"));
  const left = path.join(leftParent, "target");
  const right = path.join(rightParent, "target");
  try {
    const receipts: string[] = [];
    for (const target of [left, right]) {
      const out: string[] = [];
      const errors: string[] = [];
      const io = { stdout: (value: string) => out.push(value), stderr: (value: string) => errors.push(value) };
      const exitCode = runCli(["instantiate", capacityFixture, "--node", "capacity-decision:within-capacity", "--language", "rust", "--target-root", target], io);
      assert.equal(exitCode, 0, errors.at(-1));
      assert.equal(JSON.parse(out.pop()!).result, "pass");
      assert.equal(runCli(["receipt", target], io), 0);
      const receipt = JSON.parse(out.pop()!).receipt;
      assert.equal(receipt.semantic_contract.typed_closure.schema_version, "domainspec.typed-rule-closure/v1");
      receipts.push(receipt.receipt_sha256);
      assert.deepEqual(errors, []);
    }
    assert.equal(receipts[0], receipts[1]);
  } finally {
    fs.rmSync(leftParent, { recursive: true, force: true });
    fs.rmSync(rightParent, { recursive: true, force: true });
  }
});
