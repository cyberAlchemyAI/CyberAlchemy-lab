import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { pathToFileURL, fileURLToPath } from "node:url";

import { runCli } from "../src/cli/main.ts";
import { planInstantiation } from "../src/generation/plan-instantiation.ts";
import { loadProjectNode } from "../src/input/project-model.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const canonical = path.resolve(testDir, "../fixtures/input-roots/canonical-project");

const query = {
  schema_version: "domainspec.typed-query/v1", ontology_query: "BACKEND-QUERY-CUSTOMER", source: "alpha:customer",
  inputs: [{ name: "customer_id", type: { kind: "scalar", name: "String" } }],
  filter: { op: "eq", left: { kind: "field", name: "customer_id" }, right: { kind: "parameter", name: "customer_id" } },
  projection: ["customer_id", "settlement_details"], order_by: { field: "customer_id", direction: "asc" }, limit: 1,
};
const calculation = {
  schema_version: "domainspec.typed-calculation/v1", ontology_calculation: "BACKEND-CALCULATION-TOTAL",
  inputs: ["subtotal", "fee", "divisor"].map((name) => ({ name, type: { kind: "scalar", name: "UInt64" } })),
  result: { kind: "scalar", name: "UInt64" }, division_rounding: "ceil",
  expression: { op: "divide", left: { op: "add", left: { op: "input", name: "subtotal" }, right: { op: "input", name: "fee" } }, right: { op: "input", name: "divisor" } },
};
const mapping = {
  schema_version: "domainspec.typed-mapping/v1", ontology_mapping: "BACKEND-MAPPING-CUSTOMER", source: "alpha:customer", target: "alpha:customer", total: true,
  fields: [
    { target: "customer_id", source: "customer_id", default: null },
    { target: "settlement_details", source: "settlement_details", default: null },
    { target: "preferred_method", source: "preferred_method", default: { type: "String", value: "standard" } },
  ],
};
const policy = {
  schema_version: "domainspec.typed-policy/v1", ontology_policy: "BACKEND-POLICY-SETTLEMENT",
  inputs: [{ name: "amount", type: { kind: "scalar", name: "UInt64" } }],
  cases: [{ target: "alpha:total-cost", when: { op: "gt", left: { kind: "parameter", name: "amount" }, right: { kind: "literal", type: "UInt64", value: 100 } } }],
  default_target: "alpha:settle",
};

function fixture(): { root: string; parent: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-thin-"));
  const root = path.join(parent, "source");
  fs.cpSync(canonical, root, { recursive: true });
  return { root, parent };
}

function add(root: string, kind: string, name: string, contract: unknown): Record<string, unknown> {
  const out: string[] = []; const errors: string[] = [];
  const code = runCli(["add", kind, root, "--feature", "alpha", "--name", name, "--description", `Typed ${kind} fixture.`, "--contract-json", JSON.stringify(contract)], { stdout: (value) => out.push(value), stderr: (value) => errors.push(value) });
  assert.equal(code, 0, errors.at(-1));
  return JSON.parse(out.at(-1)!);
}

function complete(root: string): void {
  add(root, "query", "find-customer", query);
  add(root, "calculation", "total-cost", calculation);
  add(root, "mapping", "normalize-customer", mapping);
  add(root, "policy", "settlement-policy", policy);
}

test("Query, Calculation, Mapping, and Policy author atomically with exact relationships", () => {
  const value = fixture();
  try {
    complete(value.root);
    const queryNode = loadProjectNode(value.root, "alpha:find-customer");
    assert.deepEqual(queryNode.relationships.filter(({ relationship }) => relationship === "reads").map(({ target }) => target.node_id), ["customer"]);
    const mappingNode = loadProjectNode(value.root, "alpha:normalize-customer");
    assert.deepEqual(mappingNode.relationships.filter(({ relationship }) => relationship === "maps").map(({ target }) => target.node_id), ["customer"]);
    const policyNode = loadProjectNode(value.root, "alpha:settlement-policy");
    assert.deepEqual(policyNode.relationships.filter(({ relationship }) => relationship === "applies").map(({ target }) => target.node_id).sort(), ["settle", "total-cost"]);
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
});

test("thin semantic failures are causal and leave source bytes unchanged", () => {
  const value = fixture();
  try {
    const before = fs.readFileSync(path.join(value.root, "specs/alpha/feature.json"), "utf8");
    const hostile = { ...query, projection: ["missing_field"] };
    const errors: string[] = [];
    assert.equal(runCli(["add", "query", value.root, "--feature", "alpha", "--name", "bad-query", "--description", "Bad query.", "--contract-json", JSON.stringify(hostile)], { stdout: () => undefined, stderr: (entry) => errors.push(entry) }), 22);
    assert.equal(JSON.parse(errors.at(-1)!).code, "MTCLI_BACKEND_FIELD");
    assert.equal(fs.existsSync(path.join(value.root, "specs/alpha/nodes/bad-query.json")), false);
    assert.equal(fs.readFileSync(path.join(value.root, "specs/alpha/feature.json"), "utf8"), before);
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
});

test("thin source semantics causally determine every language binding", () => {
  const value = fixture();
  try {
    complete(value.root);
    const selected = loadProjectNode(value.root, "alpha:total-cost");
    const before = (["typescript", "python", "rust"] as const).map((language) => planInstantiation(selected, language).artifacts[0]!.sha256);
    const nodePath = path.join(value.root, "specs/alpha/nodes/total-cost.json");
    const node = JSON.parse(fs.readFileSync(nodePath, "utf8"));
    node.body.typed_contract.division_rounding = "floor";
    fs.writeFileSync(nodePath, `${JSON.stringify(node, null, 2)}\n`);
    const changed = loadProjectNode(value.root, "alpha:total-cost");
    const after = (["typescript", "python", "rust"] as const).map((language) => planInstantiation(changed, language).artifacts[0]!.sha256);
    assert.equal(after.every((digest, index) => digest !== before[index]), true);
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); }
});

test("Query, Calculation, Mapping, and Policy agree across TypeScript, Python, and Rust", async () => {
  const value = fixture();
  const output = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-thin-native-"));
  try {
    complete(value.root);
    const names = ["find-customer", "total-cost", "normalize-customer", "settlement-policy"] as const;
    for (const name of names) {
      const node = loadProjectNode(value.root, `alpha:${name}`);
      for (const language of ["typescript", "python", "rust"] as const) fs.writeFileSync(path.join(output, `${name}.${language === "typescript" ? "ts" : language === "python" ? "py" : "rs"}`), planInstantiation(node, language).artifacts[0]!.content);
    }
    const queryModule = await import(`${pathToFileURL(path.join(output, "find-customer.ts")).href}?l1`);
    assert.deepEqual(queryModule.findCustomer([{ customer_id: "b", settlement_details: "B" }, { customer_id: "a", settlement_details: "A" }], { customer_id: "a" }), [{ customer_id: "a", settlement_details: "A" }]);
    const calcModule = await import(`${pathToFileURL(path.join(output, "total-cost.ts")).href}?l1`);
    assert.equal(calcModule.totalCost({ subtotal: 10, fee: 1, divisor: 2 }), 6);
    const mappingModule = await import(`${pathToFileURL(path.join(output, "normalize-customer.ts")).href}?l1`);
    assert.deepEqual(mappingModule.normalizeCustomer({ customer_id: "a", settlement_details: "A" }), { customer_id: "a", settlement_details: "A", preferred_method: "standard" });
    const policyModule = await import(`${pathToFileURL(path.join(output, "settlement-policy.ts")).href}?l1`);
    assert.deepEqual([policyModule.settlementPolicy({ amount: 101 }), policyModule.settlementPolicy({ amount: 100 })], ["alpha:total-cost", "alpha:settle"]);

    const python = spawnSync("python3", ["-c", `import importlib.util\ndef load(n):\n s=importlib.util.spec_from_file_location(n,${JSON.stringify(output)}+'/'+n.replace('_','-')+'.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m\nq=load('find_customer');c=load('total_cost');m=load('normalize_customer');p=load('settlement_policy')\nprint(q.find_customer([{'customer_id':'b','settlement_details':'B'},{'customer_id':'a','settlement_details':'A'}],{'customer_id':'a'}))\nprint(c.total_cost({'subtotal':10,'fee':1,'divisor':2}))\nprint(m.normalize_customer({'customer_id':'a','settlement_details':'A'}))\nprint([p.settlement_policy({'amount':101}),p.settlement_policy({'amount':100})])`], { encoding: "utf8" });
    assert.equal(python.status, 0, python.stderr);
    assert.match(python.stdout, /6/);
    assert.match(python.stdout, /alpha:total-cost/);

    const harness = path.join(output, "main.rs");
    fs.writeFileSync(harness, `mod q { include!(${JSON.stringify(path.join(output, "find-customer.rs"))}); }\nmod c { include!(${JSON.stringify(path.join(output, "total-cost.rs"))}); }\nmod m { include!(${JSON.stringify(path.join(output, "normalize-customer.rs"))}); }\nmod p { include!(${JSON.stringify(path.join(output, "settlement-policy.rs"))}); }\nuse std::collections::BTreeMap; fn main(){let mut a=BTreeMap::new();a.insert("customer_id".to_owned(),"a".to_owned());a.insert("settlement_details".to_owned(),"A".to_owned());let mut params=BTreeMap::new();params.insert("customer_id".to_owned(),"a".to_owned());println!("{}",q::find_customer(&[a.clone()],&params).unwrap().len());let nums=BTreeMap::from([("subtotal".to_owned(),10),("fee".to_owned(),1),("divisor".to_owned(),2)]);println!("{}",c::total_cost(&nums).unwrap());println!("{}",m::normalize_customer(&a).unwrap().get("preferred_method").unwrap());let policy=BTreeMap::from([("amount".to_owned(),"101".to_owned())]);println!("{}",p::settlement_policy(&policy).unwrap());}`);
    const binary = path.join(output, "thin-bin");
    const compiled = spawnSync("/home/vrondelli/.cargo/bin/rustc", ["--edition", "2024", harness, "-o", binary], { encoding: "utf8" });
    assert.equal(compiled.status, 0, compiled.stderr);
    const rust = spawnSync(binary, [], { encoding: "utf8" });
    assert.equal(rust.status, 0, rust.stderr);
    assert.deepEqual(rust.stdout.trim().split("\n"), ["1", "6", "standard", "alpha:total-cost"]);
  } finally { fs.rmSync(value.parent, { recursive: true, force: true }); fs.rmSync(output, { recursive: true, force: true }); }
});
