import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";

import { runCli } from "../src/cli/main.ts";
import { createInstantiationReceipt, validateInstantiationReceipt } from "../src/conformance/receipt.ts";
import { observeTarget } from "../src/conformance/observe-target.ts";
import { planInstantiation } from "../src/generation/plan-instantiation.ts";
import { loadProjectNode } from "../src/input/project-model.ts";
import { canonicalJson, sha256 } from "../src/input/source-manifest.ts";
import { runInMemoryProject } from "../src/runtime/in-memory.ts";
import { decodeTypedCalculationContract } from "../src/typed-backend/contracts.ts";

const example = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../examples/capacity-classification");
const selector = "capacity-decision:classify-capacity";
const languages = ["typescript", "python", "rust"] as const;
const capacityCases = [
  { requested: 4, available: 5, variant: "Accept" },
  { requested: 5, available: 5, variant: "Reject" },
  { requested: 6, available: 5, variant: "Reject" },
] as const;

function fixture(): { parent: string; root: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-calculation-"));
  const root = path.join(parent, "source");
  fs.mkdirSync(root);
  fs.copyFileSync(path.join(example, "project.json"), path.join(root, "project.json"));
  fs.cpSync(path.join(example, "specs"), path.join(root, "specs"), { recursive: true });
  return { parent, root };
}

function mutate(root: string, name: string, action: (node: any) => void): void {
  const file = path.join(root, "specs/capacity-decision/nodes", `${name}.json`);
  const node = JSON.parse(fs.readFileSync(file, "utf8"));
  action(node);
  fs.writeFileSync(file, `${JSON.stringify(node, null, 2)}\n`);
}

function invocation(inputs: unknown, selected = selector): unknown {
  return { schema_version: "domainspec.runtime-invocation/v1", invocation_id: "calculation-verification", provider: "in-memory-v1", steps: [{ step_id: "calculation", selector: selected, input: { inputs } }] };
}

function snapshot(requested: number, available = 5): Record<string, unknown> {
  return { request_id: `R-${requested}`, requested_units: requested, available_units: available };
}

function output(root: string, inputs: unknown, selected = selector): unknown {
  return runInMemoryProject(root, invocation(inputs, selected)).outcomes[0]!.output;
}

function native(root: string, parent: string, name: string): Record<string, string> {
  const node = loadProjectNode(root, `capacity-decision:${name}`);
  return Object.fromEntries(languages.map((language) => {
    const file = path.join(parent, `${name}.${language === "typescript" ? "ts" : language === "python" ? "py" : "rs"}`);
    fs.writeFileSync(file, planInstantiation(node, language).artifacts[0]!.content);
    return [language, file];
  }));
}

function python(script: string): unknown {
  const result = spawnSync(process.env.PYTHON ?? "python3", ["-c", script], { encoding: "utf8" });
  assert.equal(result.status, 0, result.error?.message ?? result.stderr);
  return JSON.parse(result.stdout);
}

function rust(parent: string, script: string): string[] {
  const harness = path.join(parent, "main.rs"); const binary = path.join(parent, "calculation-bin");
  fs.writeFileSync(harness, script);
  const compiled = spawnSync(process.env.RUSTC ?? "rustc", ["--edition", "2024", harness, "-o", binary], { encoding: "utf8" });
  assert.equal(compiled.status, 0, compiled.error?.message ?? compiled.stderr);
  const result = spawnSync(binary, [], { encoding: "utf8" });
  assert.equal(result.status, 0, result.error?.message ?? result.stderr);
  return result.stdout.trim().split("\n");
}

for (const { requested, available, variant } of capacityCases) {
  test(`Calculation runtime classifies ${requested}/${available} as ${variant} without changing inputs`, () => {
    const inputs = { snapshot: Object.freeze(snapshot(requested, available)) };
    const before = structuredClone(inputs);
    const receipt = runInMemoryProject(example, invocation(Object.freeze(inputs)));
    assert.deepEqual(receipt.outcomes[0]!.output, { variant, payload: null });
    assert.equal(receipt.outcomes[0]!.kind, "Calculation");
    assert.equal(receipt.outcomes[0]!.meta_type_id, "DS-D1.6");
    assert.deepEqual(inputs, before);
    assert.equal(receipt.receipt_sha256, runInMemoryProject(example, invocation(inputs)).receipt_sha256);
  });
}

test("conditional Calculation agrees across generated TypeScript, Python and Rust at all capacity boundaries", async () => {
  const value = fixture();
  try {
    const files = native(value.root, value.parent, "classify-capacity");
    const ts = await import(pathToFileURL(files.typescript!).href);
    for (const { requested, available, variant } of capacityCases) {
      const inputs = Object.freeze({ snapshot: Object.freeze(snapshot(requested, available)) });
      const before = structuredClone(inputs);
      assert.deepEqual(ts.classifyCapacity(inputs), { variant, payload: null });
      assert.deepEqual(inputs, before);
    }
    const expected = capacityCases.map(({ variant }) => ({ variant, payload: null }));
    assert.deepEqual(python(`import copy,importlib.util,json\ns=importlib.util.spec_from_file_location('c',${JSON.stringify(files.python)});m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\noutputs=[]\nfor requested in [4,5,6]:\n inputs={'snapshot':{'request_id':f'R-{requested}','requested_units':requested,'available_units':5}}\n before=copy.deepcopy(inputs);outputs.append(m.classify_capacity(inputs));assert inputs==before\nprint(json.dumps(outputs))`), expected);
    assert.deepEqual(rust(value.parent, `mod c { include!(${JSON.stringify(files.rust)}); }\nfn main(){for requested in [4,5,6]{let s=c::CapacitySnapshot{request_id:format!("R-{requested}"),requested_units:requested,available_units:5};let before=s.clone();println!("{:?}",c::classify_capacity(&s));assert_eq!(s,before);}}`), ["Accept", "Reject", "Reject"]);
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
});

test("conditional Calculation rejects invalid inputs consistently in runtime and dynamic language bindings", async () => {
  const value = fixture();
  try {
    const files = native(value.root, value.parent, "classify-capacity");
    const ts = await import(pathToFileURL(files.typescript!).href);
    const bad = [
      { snapshot: { ...snapshot(4), requested_units: -1 } },
      { snapshot: { ...snapshot(4), requested_units: 4.5 } },
      { snapshot: { ...snapshot(4), requested_units: true } },
      { snapshot: { ...snapshot(4), available_units: "5" } },
      { snapshot: { ...snapshot(4), extra: 1 } },
      { snapshot: { requested_units: 4, available_units: 5 } },
      { snapshot: snapshot(4), extra: 1 },
      {},
    ];
    for (const inputs of bad) {
      assert.throws(() => output(value.root, inputs));
      assert.throws(() => ts.classifyCapacity(inputs));
    }
    assert.deepEqual(python(`import importlib.util,json\ns=importlib.util.spec_from_file_location('c',${JSON.stringify(files.python)});m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\nresults=[]\nfor inputs in json.loads(${JSON.stringify(JSON.stringify(bad))}):\n try:m.classify_capacity(inputs);results.append(False)\n except (ValueError,TypeError,KeyError):results.append(True)\nprint(json.dumps(results))`), bad.map(() => true));
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
});

test("Calculation authoring retains its role and typed references without inventing graph edges", () => {
  const value = fixture();
  try {
    const contract = loadProjectNode(value.root, selector).body.typed_contract;
    const feature = path.join(value.root, "specs/capacity-decision/feature.json");
    const edges = JSON.parse(fs.readFileSync(feature, "utf8")).relationships;
    const out: string[] = []; const errors: string[] = [];
    assert.equal(runCli(["add", "calculation", value.root, "--feature", "capacity-decision", "--name", "classify-again", "--description", "Pure classification.", "--contract-json", JSON.stringify(contract)], { stdout: (entry) => out.push(entry), stderr: (entry) => errors.push(entry) }), 0, errors.at(-1));
    const node = loadProjectNode(value.root, "capacity-decision:classify-again");
    assert.equal(node.kind, "Calculation");
    assert.deepEqual(JSON.parse(fs.readFileSync(feature, "utf8")).relationships, edges);
    assert.deepEqual(node.relationships, []);
    assert.equal(node.typed_closure?.schema_version, "domainspec.typed-calculation-closure/v1");
    assert.deepEqual(output(value.root, { snapshot: snapshot(4) }, "capacity-decision:classify-again"), { variant: "Accept", payload: null });
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
});

test("Calculation closure and receipt round trip in all three languages", () => {
  const node = loadProjectNode(example, selector);
  assert.equal(node.typed_closure?.nodes.length, 4);
  for (const language of languages) {
    const plan = planInstantiation(node, language);
    const receipt = createInstantiationReceipt(plan);
    assert.deepEqual(validateInstantiationReceipt(JSON.parse(JSON.stringify(receipt))), receipt);
    assert.equal(plan.plan_sha256, planInstantiation(node, language).plan_sha256);
    const forged = structuredClone(receipt) as any;
    forged.semantic_contract.typed_closure.calculation.expression.then.variant = "Reject";
    const { receipt_sha256: ignored, ...body } = forged;
    forged.receipt_sha256 = sha256(canonicalJson(body));
    assert.throws(() => validateInstantiationReceipt(forged));
  }
});

test("Calculation targets pass exact observation and JSON Schema validation in every language", () => {
  const value = fixture();
  try {
    const receipts = [];
    for (const language of languages) {
      const target = path.join(value.parent, language);
      const errors: string[] = [];
      assert.equal(runCli(["instantiate", value.root, "--node", selector, "--language", language, "--target-root", target], { stdout: () => undefined, stderr: (entry) => errors.push(entry) }), 0, errors.at(-1));
      assert.equal(observeTarget(target).result, "pass");
      receipts.push(JSON.parse(fs.readFileSync(path.join(target, ".domainspec/instantiations/capacity-decision.classify-capacity.json"), "utf8")));
    }
    const schema = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../contracts/instantiation-receipt.schema.json");
    const file = path.join(value.parent, "receipts.json"); fs.writeFileSync(file, JSON.stringify(receipts));
    assert.deepEqual(python(`import json\nfrom jsonschema import Draft202012Validator\nv=Draft202012Validator(json.load(open(${JSON.stringify(schema)})))\nfor receipt in json.load(open(${JSON.stringify(file)})):v.validate(receipt)\nprint('true')`), true);
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
});

test("Rule changes causally change the Calculation closure, generated sources and runtime output", () => {
  const value = fixture();
  try {
    const before = loadProjectNode(value.root, selector);
    const digests = languages.map((language) => planInstantiation(before, language).artifacts[0]!.sha256);
    assert.deepEqual(output(value.root, { snapshot: snapshot(5) }), { variant: "Reject", payload: null });
    mutate(value.root, "within-capacity", (node) => { node.body.typed_contract.expression.op = "eq"; });
    const after = loadProjectNode(value.root, selector);
    assert.notEqual(after.typed_closure?.closure_sha256, before.typed_closure?.closure_sha256);
    assert.deepEqual(output(value.root, { snapshot: snapshot(5) }), { variant: "Accept", payload: null });
    for (const [index, language] of languages.entries()) assert.notEqual(planInstantiation(after, language).artifacts[0]!.sha256, digests[index]);
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
});

const invalidContracts: Array<[string, (node: any) => void]> = [
  ["state write", (node) => { node.body.typed_contract.writes = ["capacity-decision:capacity-snapshot"]; }],
  ["unknown variant", (node) => { node.body.typed_contract.expression.then.variant = "Missing"; }],
  ["payload", (node) => { node.body.typed_contract.expression.then.payload = 1; }],
  ["missing Rule", (node) => { node.body.typed_contract.expression.condition.selector = "capacity-decision:missing"; }],
  ["missing Rule argument", (node) => { node.body.typed_contract.expression.condition.arguments = []; }],
  ["wrong Rule argument type", (node) => { node.body.typed_contract.expression.condition.arguments[0].value = { op: "literal", type: "UInt64", value: 4 }; }],
  ["wrong result role", (node) => { node.body.typed_contract.result.selector = "capacity-decision:capacity-snapshot"; }],
];
for (const [label, action] of invalidContracts) {
  test(`conditional Calculation rejects ${label} before generation or execution`, () => {
    const value = fixture();
    try {
      mutate(value.root, "classify-capacity", action);
      assert.throws(() => loadProjectNode(value.root, selector));
      assert.throws(() => output(value.root, { snapshot: snapshot(4) }));
    } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
  });
}

const input = (name: string) => ({ op: "input", name });
const numericCases = [
  { name: "sum", expression: { op: "add", left: input("a"), right: input("b") }, rounding: "reject", a: 10, b: 3, expected: 13 },
  { name: "difference", expression: { op: "subtract", left: input("a"), right: input("b") }, rounding: "reject", a: 10, b: 3, expected: 7 },
  { name: "product", expression: { op: "multiply", left: input("a"), right: input("b") }, rounding: "reject", a: 10, b: 3, expected: 30 },
  { name: "floor-quotient", expression: { op: "divide", left: input("a"), right: input("b") }, rounding: "floor", a: 11, b: 2, expected: 5 },
  { name: "ceil-quotient", expression: { op: "divide", left: input("a"), right: input("b") }, rounding: "ceil", a: 11, b: 2, expected: 6 },
  { name: "exact-quotient", expression: { op: "divide", left: input("a"), right: input("b") }, rounding: "reject", a: 12, b: 2, expected: 6 },
  { name: "literal-sum", expression: { op: "add", left: input("a"), right: { op: "literal", value: 5 } }, rounding: "reject", a: 10, b: 3, expected: 15 },
];

function addNumeric(root: string): void {
  for (const row of numericCases) {
    const contract = {
      schema_version: "domainspec.typed-calculation/v1", ontology_calculation: "TEST-CALC-NUMERIC",
      inputs: ["a", "b"].map((name) => ({ name, type: { kind: "scalar", name: "UInt64" } })),
      result: { kind: "scalar", name: "UInt64" }, division_rounding: row.rounding, expression: row.expression,
    };
    assert.equal(decodeTypedCalculationContract(contract).schema_version, "domainspec.typed-calculation/v1");
    const errors: string[] = [];
    assert.equal(runCli(["add", "calculation", root, "--feature", "capacity-decision", "--name", row.name, "--description", "Numeric compatibility regression.", "--contract-json", JSON.stringify(contract)], { stdout: () => undefined, stderr: (entry) => errors.push(entry) }), 0, errors.at(-1));
  }
}

test("existing numeric Calculation v1 arithmetic and rounding agree in runtime, TypeScript, Python and Rust", async () => {
  const value = fixture();
  try {
    addNumeric(value.root);
    const expected = numericCases.map((row) => row.expected);
    const files = numericCases.map((row) => native(value.root, value.parent, row.name));
    for (const [index, row] of numericCases.entries()) {
      const selected = `capacity-decision:${row.name}`;
      assert.equal(loadProjectNode(value.root, selected).typed_closure, null);
      const inputs = Object.freeze({ a: row.a, b: row.b });
      assert.equal(output(value.root, inputs, selected), row.expected);
      const module = await import(pathToFileURL(files[index]!.typescript!).href);
      const fn = row.name.replace(/-([a-z])/g, (_, char: string) => char.toUpperCase());
      assert.equal(module[fn](inputs), row.expected);
      assert.deepEqual(inputs, { a: row.a, b: row.b });
    }
    assert.deepEqual(python(`import importlib.util,json\noutputs=[]\nfor file,name,a,b in json.loads(${JSON.stringify(JSON.stringify(numericCases.map((row, i) => [files[i]!.python, row.name.replaceAll("-", "_"), row.a, row.b])))}):\n s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);inputs={'a':a,'b':b};outputs.append(getattr(m,name)(inputs));assert inputs=={'a':a,'b':b}\nprint(json.dumps(outputs))`), expected);
    assert.deepEqual(rust(value.parent, `${files.map((file, i) => `mod c${i} { include!(${JSON.stringify(file.rust)}); }`).join("\n")}\nuse std::collections::BTreeMap;fn main(){${numericCases.map((row, i) => `let inputs=BTreeMap::from([("a".to_owned(),${row.a}),("b".to_owned(),${row.b})]);let before=inputs.clone();println!("{}",c${i}::${row.name.replaceAll("-", "_")}(&inputs).unwrap());assert_eq!(inputs,before);`).join("")}}`), expected.map(String));
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
});

test("existing numeric Calculations still reject division by zero, inexact division and underflow", async () => {
  const value = fixture();
  try {
    addNumeric(value.root);
    const cases = [
      { name: "exact-quotient", a: 12, b: 0 },
      { name: "exact-quotient", a: 11, b: 2 },
      { name: "difference", a: 2, b: 3 },
    ];
    const files = cases.map((row, i) => {
      const directory = path.join(value.parent, `case-${i}`); fs.mkdirSync(directory);
      return native(value.root, directory, row.name);
    });
    for (const [index, row] of cases.entries()) {
      assert.throws(() => output(value.root, { a: row.a, b: row.b }, `capacity-decision:${row.name}`));
      const module = await import(pathToFileURL(files[index]!.typescript!).href);
      const fn = row.name.replace(/-([a-z])/g, (_, char: string) => char.toUpperCase());
      assert.throws(() => module[fn]({ a: row.a, b: row.b }));
    }
    assert.deepEqual(python(`import importlib.util,json\noutputs=[]\nfor file,name,a,b in json.loads(${JSON.stringify(JSON.stringify(cases.map((row, i) => [files[i]!.python, row.name.replaceAll("-", "_"), row.a, row.b])))}):\n s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n try:getattr(m,name)({'a':a,'b':b});outputs.append(False)\n except (ValueError,ZeroDivisionError):outputs.append(True)\nprint(json.dumps(outputs))`), cases.map(() => true));
    assert.deepEqual(rust(value.parent, `${files.map((file, i) => `mod c${i} { include!(${JSON.stringify(file.rust)}); }`).join("\n")}\nuse std::collections::BTreeMap;fn main(){${cases.map((row, i) => `println!("{}",c${i}::${row.name.replaceAll("-", "_")}(&BTreeMap::from([("a".to_owned(),${row.a}),("b".to_owned(),${row.b})])).is_err());`).join("")}}`), cases.map(() => "true"));
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
});
