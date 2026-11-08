import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { pathToFileURL } from "node:url";

import { runCli } from "../src/cli/main.ts";
import { createMetaTypeFormalizationProjection } from "../src/formalization/projection.ts";
import { validateGraphBoundCertificate } from "../src/formalization/refinement.ts";
import { decodeBody, evaluateCompiledObligationWitness, loadCompiledProjectGraph, validateCompiledProjectGraphObligations, type CompiledProjectGraph, type CompiledRelationshipObligationWitness, type DecodedProjectNode, type DecodedRelationship } from "../src/input/project-model.ts";
import { planInstantiation } from "../src/generation/plan-instantiation.ts";
import { planProjectInstantiation } from "../src/generation/project-instantiation.ts";
import { publishProjectInstantiation, publishProjectInstantiationForTest } from "../src/generation/publish-project.ts";
import type { SourceManifestV1 } from "../src/input/source-manifest.ts";
import { relationshipSignature } from "../src/relationships/authority.ts";
import { checkoutRoot } from "./helpers/local-toolchain.ts";

const canonicalProject = path.resolve(import.meta.dirname, "../fixtures/input-roots/canonical-project");
const authOperationSource = path.join(checkoutRoot, "auth-foundation/implementation/operation-source");

const manifest = Object.freeze({
  schema_version: "domainspec.stable-foundation-cli.source-manifest/v1", project_id: "static-backend",
  source_count: 1, total_size_bytes: 1, sources: [], aggregate_sha256: "0".repeat(64),
  authority_effect: "none", manifest_sha256: "1".repeat(64),
}) as unknown as SourceManifestV1;

const calculationBody = {
  description: "Compute a deterministic adjusted amount.",
  inputs: ["base", "surcharge", "rate"],
  semantics: {
    schema_version: "domainspec.calculation-semantics/v1", result: "number",
    expression: { op: "add", terms: [{ op: "input", name: "base" }, { op: "multiply", terms: [{ op: "input", name: "surcharge" }, { op: "input", name: "rate" }] }] },
    rounding: { mode: "half-away-from-zero", scale: 2 },
  },
};
const policyBody = {
  description: "Select the first admitted strategy.", strategies: ["fast-path", "safe-path"],
  decisions: [{ rule_ref: "alpha:is-fast", strategy: "fast-path" }, { rule_ref: "alpha:is-safe", strategy: "safe-path" }], default_strategy: "safe-path",
};
const mappingBody = {
  description: "Map an input shape to a customer shape.", source: "alpha:source", target: "alpha:customer", direction: "inbound",
  totality: "partial",
  fields: [
    { target_field: "customer-id", source_field: "id", default_value: null, required: true, conversion: "identity" },
    { target_field: "currency", source_field: null, default_value: "USD", required: true, conversion: "string" },
    { target_field: "note", source_field: "note", default_value: null, required: false, conversion: "identity" },
  ],
};

function edge(kind: "Calculation" | "Policy" | "Mapping", nodeId: string, relationship: "calculates" | "applies" | "maps", targetId: string, targetKind: "Operation" | "Calculation" | "Entity"): DecodedRelationship {
  return Object.freeze({ edge_id: `${nodeId}-${relationship}-${targetId}`, relationship, scope: "feature", source: Object.freeze({ feature_id: "alpha", node_id: nodeId, kind }), target: Object.freeze({ feature_id: "alpha", node_id: targetId, kind: targetKind }) });
}

function semanticNode(kind: "Calculation" | "Policy" | "Mapping", nodeId: string, body: Record<string, unknown>): DecodedProjectNode {
  const relation = kind === "Calculation" ? edge(kind, nodeId, "calculates", "operate", "Operation") : kind === "Policy" ? edge(kind, nodeId, "applies", "fee", "Calculation") : edge(kind, nodeId, "maps", "customer", "Entity");
  return Object.freeze({ project_root: "/tmp/static-backend", project_id: "static-backend", feature_id: "alpha", node_id: nodeId, kind, meta_type_id: kind === "Calculation" ? "DS-D1.6" : kind === "Policy" ? "DS-D1.8" : "DS-D1.13", body: decodeBody(kind, body), relationships: Object.freeze([relation]), source_manifest: manifest, typed_closure: null });
}

test("Calculation, Policy, and Mapping semantic bodies are closed and hostile inputs fail causally", () => {
  assert.equal(decodeBody("Calculation", calculationBody).semantics !== undefined, true);
  assert.equal((decodeBody("Policy", policyBody).decisions as readonly unknown[]).length, 2);
  assert.equal((decodeBody("Mapping", mappingBody).fields as readonly unknown[]).length, 3);
  assert.throws(() => decodeBody("Calculation", { ...calculationBody, semantics: { ...calculationBody.semantics, expression: { op: "input", name: "ambient" } } }), (error: unknown) => (error as { code?: string }).code === "MTCLI_CALCULATION_INPUT");
  assert.throws(() => decodeBody("Calculation", { ...calculationBody, semantics: { ...calculationBody.semantics, rounding: { mode: "bankers", scale: 2 } } }), (error: unknown) => (error as { code?: string }).code === "MTCLI_CALCULATION_ROUNDING");
  assert.throws(() => decodeBody("Policy", { ...policyBody, default_strategy: "undeclared" }), (error: unknown) => (error as { code?: string }).code === "MTCLI_POLICY_STRATEGY");
  assert.throws(() => decodeBody("Mapping", { ...mappingBody, fields: [{ target_field: "x", source_field: null, default_value: null, required: true, conversion: "identity" }] }), (error: unknown) => (error as { code?: string }).code === "MTCLI_MAPPING_FIELDS");
  assert.throws(() => decodeBody("Mapping", { ...mappingBody, totality: "total", fields: [mappingBody.fields[0]] }), (error: unknown) => (error as { code?: string }).code === "MTCLI_MAPPING_TOTALITY");
});

test("Calculation rounding is explicit and agrees on positive and negative ties in all languages", async () => {
  const body = { ...calculationBody, semantics: { ...calculationBody.semantics, expression: { op: "divide", left: { op: "input", name: "base" }, right: { op: "input", name: "rate" } }, rounding: { mode: "half-away-from-zero", scale: 0 } } };
  const node = semanticNode("Calculation", "fee", body);
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-calculation-rounding-"));
  try {
    const tsPath = path.join(root, "fee.ts"); fs.writeFileSync(tsPath, planInstantiation(node, "typescript").artifacts[0]!.content);
    const ts = await import(`${pathToFileURL(tsPath).href}?rounding`);
    assert.deepEqual([ts.fee({ base: 5, surcharge: 0, rate: 2 }), ts.fee({ base: -5, surcharge: 0, rate: 2 })], [3, -3]);
    const pyPath = path.join(root, "fee.py"); fs.writeFileSync(pyPath, planInstantiation(node, "python").artifacts[0]!.content);
    const py = spawnSync("python3", ["-c", `import importlib.util\ns=importlib.util.spec_from_file_location('m',${JSON.stringify(pyPath)})\nm=importlib.util.module_from_spec(s);s.loader.exec_module(m)\nprint(m.fee({'base':5,'surcharge':0,'rate':2}),m.fee({'base':-5,'surcharge':0,'rate':2}))`], { encoding: "utf8" });
    assert.equal(py.status, 0, py.stderr); assert.equal(py.stdout.trim(), "3.0 -3.0");
    const rustPath = path.join(root, "fee.rs"); fs.writeFileSync(rustPath, planInstantiation(node, "rust").artifacts[0]!.content);
    const harness = path.join(root, "main.rs"); fs.writeFileSync(harness, `mod generated { include!(${JSON.stringify(rustPath)}); }\nuse generated::*;\nfn main(){for base in [5.0,-5.0]{println!("{}",fee(&FeeInputs{base,surcharge:0.0,rate:2.0}).unwrap());}}\n`);
    const binary = path.join(root, "rounding"); const compile = spawnSync(process.env.DOMAINSPEC_RUSTC ?? "rustc", ["--edition", "2024", harness, "-o", binary], { encoding: "utf8" });
    assert.equal(compile.status, 0, compile.stderr); assert.deepEqual(spawnSync(binary, [], { encoding: "utf8" }).stdout.trim().split("\n"), ["3", "-3"]);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test("all three static semantic bindings are source-sensitive in all languages", () => {
  const bodies = [calculationBody, policyBody, mappingBody] as const;
  const kinds = ["Calculation", "Policy", "Mapping"] as const;
  const ids = ["fee", "routing-policy", "customer-mapping"] as const;
  for (let index = 0; index < kinds.length; index += 1) {
    const before = semanticNode(kinds[index]!, ids[index]!, bodies[index]! as unknown as Record<string, unknown>);
    const changed = structuredClone(bodies[index]) as Record<string, unknown>;
    changed.description = `${changed.description} Changed.`;
    const after = semanticNode(kinds[index]!, ids[index]!, changed);
    for (const language of ["typescript", "python", "rust"] as const) {
      const left = planInstantiation(before, language).artifacts[0]!;
      const right = planInstantiation(after, language).artifacts[0]!;
      assert.notEqual(left.sha256, right.sha256, `${kinds[index]}/${language}`);
    }
  }
});

test("typed Value Object equality is recursively structural in TypeScript", async () => {
  const body = decodeBody("Value Object", {
    description: "Nested value", fields: ["items", "labels", "choice"], invariant_refs: ["alpha:nested-value-valid"], typed_contract: {
      schema_version: "domainspec.typed-record/v1", ontology_node: "TEST-NESTED-VALUE",
      properties: [
        { ontology_property: "TEST-NESTED-VALUE#items", name: "items", type: { kind: "list", element: { kind: "scalar", name: "String" } }, cardinality: "many", identity: false, meaning: "Ordered values." },
        { ontology_property: "TEST-NESTED-VALUE#labels", name: "labels", type: { kind: "set", element: { kind: "sum", variants: [{ ontology_variant: "TEST-LABEL#Some", name: "Some", payload: { kind: "scalar", name: "String" } }] } }, cardinality: "many-unique", identity: false, meaning: "Unique structural labels." },
        { ontology_property: "TEST-NESTED-VALUE#choice", name: "choice", type: { kind: "sum", variants: [{ ontology_variant: "TEST-CHOICE#Some", name: "Some", payload: { kind: "scalar", name: "String" } }, { ontology_variant: "TEST-CHOICE#None", name: "None", payload: null }] }, cardinality: "one", identity: false, meaning: "Value-defining tagged choice." },
      ],
    },
  });
  const node = Object.freeze({ project_root: "/tmp/static-backend", project_id: "static-backend", feature_id: "alpha", node_id: "nested-value", kind: "Value Object", meta_type_id: "DS-D1.2", body, relationships: Object.freeze([]), source_manifest: manifest, typed_closure: null }) as DecodedProjectNode;
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-value-equality-"));
  try {
    const target = path.join(root, "nested-value.ts"); fs.writeFileSync(target, planInstantiation(node, "typescript").artifacts[0]!.content);
    const generated = await import(`${pathToFileURL(target).href}?value-equality`);
    const mutable = { items: ["a", "b"], labels: new Set([{ variant: "Some", payload: "x" }, { variant: "Some", payload: "y" }]), choice: { variant: "Some", payload: "v" } };
    const left = new generated.NestedValue(mutable);
    const equal = new generated.NestedValue({ items: ["a", "b"], labels: new Set([{ variant: "Some", payload: "y" }, { variant: "Some", payload: "x" }]), choice: { variant: "Some", payload: "v" } });
    const changed = new generated.NestedValue({ items: ["a", "c"], labels: new Set([{ variant: "Some", payload: "x" }, { variant: "Some", payload: "y" }]), choice: { variant: "Some", payload: "v" } });
    const nonBijective = new generated.NestedValue({ items: ["a", "b"], labels: new Set([{ variant: "Some", payload: "x" }, { variant: "Some", payload: "x" }]), choice: { variant: "Some", payload: "v" } });
    assert.equal(left.equals(equal), true); assert.equal(left.equals(changed), false); assert.equal(nonBijective.equals(left), false);
    mutable.items.push("caller-mutation"); mutable.labels.add({ variant: "Some", payload: "caller-mutation" }); mutable.choice.payload = "caller-mutation";
    assert.equal(left.equals(equal), true);
    const exposed = left.snapshot() as { items: string[]; labels: Set<{ variant: string; payload: string }>; choice: { payload: string } };
    assert.throws(() => { exposed.items.push("snapshot-mutation"); }, TypeError);
    exposed.labels.add({ variant: "Some", payload: "snapshot-mutation" });
    assert.throws(() => { exposed.choice.payload = "snapshot-mutation"; }, TypeError);
    assert.equal(left.equals(equal), true);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test("Calculation executes one deterministic corpus in TypeScript, Python, and Rust", async () => {
  const node = semanticNode("Calculation", "fee", calculationBody);
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-calculation-"));
  try {
    const tsPath = path.join(root, "fee.ts");
    fs.writeFileSync(tsPath, planInstantiation(node, "typescript").artifacts[0]!.content);
    const ts = await import(`${pathToFileURL(tsPath).href}?calculation`);
    assert.equal(ts.fee({ base: 10, surcharge: 4, rate: 0.5 }), 12);

    const pyPath = path.join(root, "fee.py");
    fs.writeFileSync(pyPath, planInstantiation(node, "python").artifacts[0]!.content);
    const py = spawnSync("python3", ["-c", `import importlib.util\ns=importlib.util.spec_from_file_location('m',${JSON.stringify(pyPath)})\nm=importlib.util.module_from_spec(s);s.loader.exec_module(m)\nprint(m.fee({'base':10,'surcharge':4,'rate':0.5}))`], { encoding: "utf8" });
    assert.equal(py.status, 0, py.stderr);
    assert.equal(py.stdout.trim(), "12.0");

    const rustPath = path.join(root, "fee.rs");
    fs.writeFileSync(rustPath, planInstantiation(node, "rust").artifacts[0]!.content);
    const harness = path.join(root, "main.rs");
    fs.writeFileSync(harness, `mod generated { include!(${JSON.stringify(rustPath)}); }\nuse generated::*;\nfn main(){let i=FeeInputs{base:10.0,surcharge:4.0,rate:0.5};println!("{}",fee(&i).unwrap());let hostile=FeeInputs{base:f64::NAN,surcharge:4.0,rate:0.5};println!("{}",fee(&hostile).unwrap_err());}\n`);
    const binary = path.join(root, "calc");
    const compile = spawnSync(process.env.DOMAINSPEC_RUSTC ?? "rustc", ["--edition", "2024", harness, "-o", binary], { encoding: "utf8" });
    assert.equal(compile.status, 0, compile.stderr);
    assert.deepEqual(spawnSync(binary, [], { encoding: "utf8" }).stdout.trim().split("\n"), ["12", "missing or non-finite Calculation input:base"]);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test("Calculation division by zero fails causally in every native binding", async () => {
  const body = { ...calculationBody, semantics: { ...calculationBody.semantics, expression: { op: "divide", left: { op: "input", name: "base" }, right: { op: "input", name: "rate" } } } };
  const node = semanticNode("Calculation", "fee", body);
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-calculation-zero-"));
  try {
    const tsPath = path.join(root, "fee.ts");
    fs.writeFileSync(tsPath, planInstantiation(node, "typescript").artifacts[0]!.content);
    const ts = await import(`${pathToFileURL(tsPath).href}?calculation-zero`);
    assert.throws(() => ts.fee({ base: 10, surcharge: 0, rate: 0 }), /Calculation division by zero/);

    const pyPath = path.join(root, "fee.py");
    fs.writeFileSync(pyPath, planInstantiation(node, "python").artifacts[0]!.content);
    const py = spawnSync("python3", ["-c", `import importlib.util\ns=importlib.util.spec_from_file_location('m',${JSON.stringify(pyPath)})\nm=importlib.util.module_from_spec(s);s.loader.exec_module(m)\nm.fee({'base':10,'surcharge':0,'rate':0})`], { encoding: "utf8" });
    assert.notEqual(py.status, 0); assert.match(py.stderr, /Calculation division by zero/);

    const rustPath = path.join(root, "fee.rs");
    fs.writeFileSync(rustPath, planInstantiation(node, "rust").artifacts[0]!.content);
    const harness = path.join(root, "main.rs");
    fs.writeFileSync(harness, `mod generated { include!(${JSON.stringify(rustPath)}); }\nuse generated::*;\nfn main(){let i=FeeInputs{base:10.0,surcharge:0.0,rate:0.0};println!("{}",fee(&i).unwrap_err());}\n`);
    const binary = path.join(root, "calc-zero");
    const compile = spawnSync(process.env.DOMAINSPEC_RUSTC ?? "rustc", ["--edition", "2024", harness, "-o", binary], { encoding: "utf8" });
    assert.equal(compile.status, 0, compile.stderr);
    assert.equal(spawnSync(binary, [], { encoding: "utf8" }).stdout.trim(), "Calculation division by zero");
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test("Policy selection and Mapping transformation agree across native bindings", async () => {
  const policy = semanticNode("Policy", "routing-policy", policyBody);
  const mapping = semanticNode("Mapping", "customer-mapping", mappingBody);
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-static-bindings-"));
  try {
    const policyTs = path.join(root, "policy.ts");
    const mappingTs = path.join(root, "mapping.ts");
    fs.writeFileSync(policyTs, planInstantiation(policy, "typescript").artifacts[0]!.content);
    fs.writeFileSync(mappingTs, planInstantiation(mapping, "typescript").artifacts[0]!.content);
    const pts = await import(`${pathToFileURL(policyTs).href}?policy`);
    const mts = await import(`${pathToFileURL(mappingTs).href}?mapping`);
    assert.equal(pts.routingPolicy((rule: string) => rule === "alpha:is-fast"), "fast-path");
    assert.equal(pts.routingPolicy(() => false), "safe-path");
    assert.throws(() => pts.routingPolicy(() => true), /ambiguous Policy selection/);
    assert.deepEqual(mts.customerMapping({ id: "c-1" }), { "customer-id": "c-1", currency: "USD" });
    assert.throws(() => mts.customerMapping({}), /missing Mapping source field:id/);

    const policyPy = path.join(root, "policy.py");
    const mappingPy = path.join(root, "mapping.py");
    fs.writeFileSync(policyPy, planInstantiation(policy, "python").artifacts[0]!.content);
    fs.writeFileSync(mappingPy, planInstantiation(mapping, "python").artifacts[0]!.content);
    const py = spawnSync("python3", ["-c", `import importlib.util,json\ndef load(n,p):\n s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m\np=load('p',${JSON.stringify(policyPy)});m=load('m',${JSON.stringify(mappingPy)})\nprint(p.routing_policy(lambda r:r=='alpha:is-fast'));print(p.routing_policy(lambda r:False));\ntry:p.routing_policy(lambda r:True)\nexcept ValueError as e:print(str(e))\nprint(json.dumps(m.customer_mapping({'id':'c-1'}),sort_keys=True,separators=(',',':')))`], { encoding: "utf8" });
    assert.equal(py.status, 0, py.stderr);
    assert.deepEqual(py.stdout.trim().split("\n"), ["fast-path", "safe-path", "ambiguous Policy selection", '{"currency":"USD","customer-id":"c-1"}']);

    const policyRs = path.join(root, "policy.rs");
    const mappingRs = path.join(root, "mapping.rs");
    fs.writeFileSync(policyRs, planInstantiation(policy, "rust").artifacts[0]!.content);
    fs.writeFileSync(mappingRs, planInstantiation(mapping, "rust").artifacts[0]!.content);
    const harness = path.join(root, "main.rs");
    fs.writeFileSync(harness, `mod p { include!(${JSON.stringify(policyRs)}); }\nmod m { include!(${JSON.stringify(mappingRs)}); }\nuse std::collections::BTreeMap;\nfn main(){println!("{}",p::routing_policy(|r|r=="alpha:is-fast").unwrap());println!("{}",p::routing_policy(|_|false).unwrap());assert!(p::routing_policy(|_|true).is_err());let mut s=BTreeMap::new();s.insert("id".to_owned(),m::DomainspecMappingValue::String("c-1".to_owned()));let out=m::customer_mapping(&s).unwrap();println!("{}|{}",out.get("customer-id").unwrap().display(),out.get("currency").unwrap().display());}\n`);
    const binary = path.join(root, "static");
    const compile = spawnSync(process.env.DOMAINSPEC_RUSTC ?? "rustc", ["--edition", "2024", harness, "-o", binary], { encoding: "utf8" });
    assert.equal(compile.status, 0, compile.stderr);
    assert.deepEqual(spawnSync(binary, [], { encoding: "utf8" }).stdout.trim().split("\n"), ["fast-path", "safe-path", "c-1|USD"]);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test("Rust Mapping rejects source text that cannot be preserved byte-faithfully", () => {
  const hostile = { ...mappingBody, fields: [{ target_field: "value", source_field: null, default_value: "\ud800", required: true, conversion: "string" }] };
  assert.throws(() => planInstantiation(semanticNode("Mapping", "customer-mapping", hostile), "rust"), /unpaired UTF-16 surrogate/);
});

function writeJson(file: string, value: unknown): void { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`); }
function projectFixture(): { readonly parent: string; readonly root: string } { const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-l1-complete-")); const root = path.join(parent, "source"); fs.cpSync(canonicalProject, root, { recursive: true }); return { parent, root }; }
function updateJson(file: string, mutate: (value: Record<string, any>) => void): void { const value = JSON.parse(fs.readFileSync(file, "utf8")); mutate(value); writeJson(file, value); }
function featurePath(root: string, feature: string): string { return path.join(root, "specs", feature, "feature.json"); }
function addDirectNode(root: string, feature: string, id: string, kind: string, body: unknown): void {
  writeJson(path.join(root, "specs", feature, "nodes", `${id}.json`), { schema_version: "domainspec.node/v1", node_id: id, feature_id: feature, kind, body });
  updateJson(featurePath(root, feature), (value) => { value.nodes = [...value.nodes, id].sort(); });
}
function addFeatureEdge(root: string, feature: string, id: string, relationship: string, source: string, target: string): void {
  writeJson(path.join(root, "specs", feature, "edges", `${id}.json`), { schema_version: "domainspec.edge/v1", edge_id: id, feature_id: feature, relationship, source_node_id: source, target_node_id: target, scope: "feature" });
  updateJson(featurePath(root, feature), (value) => { value.edges = [...value.edges, id].sort(); });
}
function addProjectEdge(root: string, id: string, relationship: string, sourceFeature: string, source: string, targetFeature: string, target: string): void {
  writeJson(path.join(root, "edges", `${id}.json`), { schema_version: "domainspec.edge/v1", edge_id: id, source_feature_id: sourceFeature, source_node_id: source, target_feature_id: targetFeature, target_node_id: target, relationship, scope: "project" });
  updateJson(path.join(root, "project.json"), (value) => { value.cross_feature_edges = [...value.cross_feature_edges, id].sort(); });
}
function completeProject(): { readonly parent: string; readonly root: string } {
  const fixture = projectFixture();
  addDirectNode(fixture.root, "alpha", "query-record", "Entity", {
    description: "Typed Query read model", fields: ["record_id"], typed_contract: {
      schema_version: "domainspec.typed-record/v1", ontology_node: "TEST-CUSTOMER",
      properties: [{ ontology_property: "TEST-CUSTOMER#record_id", name: "record_id", type: { kind: "scalar", name: "String" }, cardinality: "one", identity: true, meaning: "Stable record identity." }],
    },
  });
  addDirectNode(fixture.root, "alpha", "mapping-source", "Entity", { description: "Mapping input", identity_field: "id", fields: [{ field_id: "id", type_ref: { kind: "primitive", name: "uuid" }, required: true }] });
  updateJson(path.join(fixture.root, "specs", "beta", "nodes", "settlement-method.json"), (value) => {
    value.body.values = ["Resolved", "Deny"];
    value.body.typed_contract = {
      schema_version: "domainspec.typed-sum/v1", ontology_node: "TEST-QUERY-RESULT",
      variants: [
        { ontology_variant: "TEST-QUERY-RESULT#Resolved", name: "Resolved", payload: { kind: "scalar", name: "String" } },
        { ontology_variant: "TEST-QUERY-RESULT#Deny", name: "Deny", payload: null },
      ],
    };
  });
  updateJson(path.join(fixture.root, "specs", "beta", "nodes", "can-complete-settlement.json"), (value) => {
    value.body.predicate = "structured:domainspec.typed-rule/v1";
    value.body.typed_contract = {
      schema_version: "domainspec.typed-rule/v1", ontology_rule: "TEST-RULE-CAN-COMPLETE",
      parameters: [{ name: "candidate", type: { kind: "scalar", name: "String" } }],
      expression: { op: "not", term: { op: "eq", left: { op: "path", root: "candidate", properties: [] }, right: { op: "literal", type: "String", value: "" } } },
    };
  });
  const calculationArgs = ["calculation", fixture.root, "--feature", "alpha", "--name", "fee", "--description", calculationBody.description, "--inputs", calculationBody.inputs.join(","), "--semantics-json", JSON.stringify(calculationBody.semantics), "--calculates", "settle"];
  const policyArgs = ["policy", fixture.root, "--feature", "alpha", "--name", "routing-policy", "--description", policyBody.description, "--strategies", policyBody.strategies.join(","), "--decisions-json", JSON.stringify([{ rule_ref: "beta:can-complete-settlement", strategy: "fast-path" }]), "--default-strategy", policyBody.default_strategy, "--applies", "fee"];
  const mappingArgs = ["mapping", fixture.root, "--feature", "alpha", "--name", "customer-mapping", "--description", mappingBody.description, "--source", "mapping-source", "--target", "customer", "--direction", "inbound", "--totality", "partial", "--fields-json", JSON.stringify([mappingBody.fields[0]])];
  for (const args of [calculationArgs, policyArgs, mappingArgs]) {
    const out: string[] = []; const errors: string[] = [];
    assert.equal(runCli(["add", ...args], { stdout: (value) => out.push(value), stderr: (value) => errors.push(value) }), 0, errors.at(-1));
    assert.equal(JSON.parse(out.at(-1)!).result, "pass");
  }
  addDirectNode(fixture.root, "alpha", "find-customer", "Query", {
    description: "Read one customer.", reads: ["query-record"],
    typed_contract: {
      schema_version: "domainspec.typed-operation/v1", ontology_operation: "TEST-QUERY-FIND-CUSTOMER",
      inputs: [{ name: "candidate", type: { kind: "scalar", name: "String" } }],
      output: { kind: "named", selector: "beta:settlement-method" }, guard: "beta:can-complete-settlement",
      reads: ["alpha:query-record"], writes: [], effects: [], failure_continuation: "return-deny",
      success_result: { variant: "Resolved", payload: { op: "path", root: "candidate", properties: [] } },
      failure_result: { variant: "Deny", payload: null },
    },
  });
  addFeatureEdge(fixture.root, "alpha", "find-customer-reads-query-record", "reads", "find-customer", "query-record");
  addDirectNode(fixture.root, "alpha", "settlement-workflow", "Workflow", { description: "Run settlement.", steps: ["settle"], compensations: [] });
  addFeatureEdge(fixture.root, "alpha", "settlement-workflow-orchestrates-settle", "orchestrates", "settlement-workflow", "settle");
  addDirectNode(fixture.root, "alpha", "settlement-recorded", "Event", { description: "Settlement was recorded.", event_type: "settlement-recorded", version: "1", occurrence_id: { field_id: "occurrence-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }, occurred_at_policy: "required", payload: [] });
  addFeatureEdge(fixture.root, "alpha", "settle-produces-settlement-recorded", "produces", "settle", "settlement-recorded");
  addFeatureEdge(fixture.root, "beta", "settled-contains-details", "contains", "settled", "settlement-details");
  addFeatureEdge(fixture.root, "beta", "settled-emits-completed", "emits", "settled", "settlement-completed");
  addProjectEdge(fixture.root, "settle-produces-for-settled", "produces-for", "alpha", "settle", "beta", "settled");
  addProjectEdge(fixture.root, "can-complete-enforces-settle", "enforces", "beta", "can-complete-settlement", "alpha", "settle");
  return fixture;
}
function snapshot(root: string): string { const rows: string[] = []; const visit = (dir: string): void => { for (const entry of fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) { const child = path.join(dir, entry.name); if (entry.isDirectory()) visit(child); else rows.push(`${path.relative(root, child)}\0${fs.readFileSync(child, "hex")}`); } }; visit(root); return rows.join("\n"); }

function hostileObligationCase(graph: CompiledProjectGraph, original: CompiledRelationshipObligationWitness): { readonly graph: Pick<CompiledProjectGraph, "nodes" | "relationships">; readonly witness: CompiledRelationshipObligationWitness } {
  const nodes = structuredClone(graph.nodes) as any[];
  const relationships = structuredClone(graph.relationships) as any[];
  const witness = structuredClone(original) as any;
  const edge = relationships.find(({ edge_id }) => edge_id === original.edge_id)!;
  if (original.family === "endpoint") {
    const endpoint = original.obligation_id.endsWith("_source") ? "source" : "target";
    const selector = `${edge[endpoint].feature_id}:${edge[endpoint].node_id}`;
    edge[endpoint].kind = "__invalid_meta_type__";
    nodes.find((node) => node.selector === selector)!.kind = "__invalid_meta_type__";
    witness.witness[`${endpoint}_type`] = "__invalid_meta_type__";
  } else if (original.family === "scope") {
    if (original.obligation_id === "reject_enforces_cross_label") {
      const selector = `${edge.target.feature_id}:${edge.target.node_id}`;
      edge.target.kind = edge.source.kind; nodes.find((node) => node.selector === selector)!.kind = edge.source.kind; witness.witness.target_type = edge.source.kind;
    } else {
      edge.scope = edge.scope === "feature" ? "project" : "feature"; witness.witness.scope = edge.scope;
    }
  } else if (original.family === "multiplicity") {
    const duplicate = structuredClone(edge); duplicate.edge_id = `${edge.edge_id}-hostile-duplicate`;
    relationships.push(duplicate);
  } else if (original.family === "generated-projection") {
    const source = nodes.find((node) => node.selector === original.witness.source_selector)!;
    const attribute = original.predicate.generated_projection_attribute!;
    if (original.obligation_id === "reject_authored_generated_projection") source.authored_forbidden_projection_attributes = [attribute];
    else source.generated_relationship_projections[attribute] = ["hostile:omission"];
  } else if (original.family === "inverse-collapse") {
    relationships.push({ edge_id: `${edge.edge_id}-hostile-inverse`, relationship: "owns", scope: edge.scope, source: structuredClone(edge.target), target: structuredClone(edge.source) });
  } else {
    edge.relationship = "queries";
  }
  return { graph: { nodes, relationships }, witness };
}

test("authored Calculation, Policy, and Mapping close exact DS-D8 relationships", () => {
  const fixture = completeProject();
  try {
    const graph = loadCompiledProjectGraph(fixture.root);
    for (const [selector, relationship] of [["alpha:fee", "calculates"], ["alpha:routing-policy", "applies"], ["alpha:customer-mapping", "maps"]] as const) {
      const node = graph.nodes.find((candidate) => candidate.selector === selector)!;
      const signature = relationshipSignature(relationship)!;
      for (const obligation of signature.validation_obligations) assert.equal(node.applicable_obligation_ids.includes(obligation), true, `${selector}:${obligation}`);
    }
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("Mapping rejects incompatible endpoint fields before generation", () => {
  const fixture = completeProject();
  try {
    updateJson(path.join(fixture.root, "specs/alpha/nodes/mapping-source.json"), (value) => {
      value.body.fields[0].type_ref = { kind: "primitive", name: "string" };
    });
    assert.throws(() => loadCompiledProjectGraph(fixture.root), (error: unknown) => (error as { code?: string }).code === "MTCLI_MAPPING_TYPE");
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("authoring rollback removes only the inode it published", () => {
  const fixture = projectFixture();
  const nodePath = path.join(fixture.root, "specs/alpha/nodes/raced-fee.json");
  const feature = featurePath(fixture.root, "alpha");
  const originalRename = fs.renameSync;
  try {
    (fs as unknown as { renameSync: typeof fs.renameSync }).renameSync = ((source: fs.PathLike, destination: fs.PathLike) => {
      if (String(destination) === feature) {
        fs.unlinkSync(nodePath);
        fs.writeFileSync(nodePath, "competing writer\n", { flag: "wx" });
        const error = new Error("injected feature publication failure") as NodeJS.ErrnoException; error.code = "EIO"; throw error;
      }
      return originalRename(source, destination);
    }) as typeof fs.renameSync;
    const errors: string[] = [];
    const status = runCli(["add", "calculation", fixture.root, "--feature", "alpha", "--name", "raced-fee", "--description", "Raced fee", "--inputs", "base", "--semantics-json", JSON.stringify({ schema_version: "domainspec.calculation-semantics/v1", result: "number", expression: { op: "input", name: "base" }, rounding: { mode: "none", scale: 0 } }), "--calculates", "settle"], { stdout: () => undefined, stderr: (value) => errors.push(value) });
    assert.notEqual(status, 0); assert.match(errors.at(-1) ?? "", /injected feature publication failure/);
    assert.equal(fs.readFileSync(nodePath, "utf8"), "competing writer\n");
    assert.equal(fs.existsSync(path.join(fixture.root, "specs/alpha/edges/raced-fee-calculates-settle.json")), false);
  } finally {
    (fs as unknown as { renameSync: typeof fs.renameSync }).renameSync = originalRename;
    fs.rmSync(fixture.parent, { recursive: true, force: true });
  }
});

test("whole-backend corpus reaches all 13 types and 17 relationships with exhaustive applicable-obligation mutants", () => {
  const fixture = completeProject();
  try {
    const graph = loadCompiledProjectGraph(fixture.root);
    assert.equal(new Set(graph.nodes.map(({ kind }) => kind)).size, 13);
    assert.deepEqual([...new Set(graph.relationships.map(({ relationship }) => relationship))].sort(), ["applies", "belongs-to", "calculates", "contains", "creates", "emits", "enforces", "exposes", "maps", "orchestrates", "owns", "performs", "produces", "produces-for", "reads", "transitions", "triggers-cross"]);
    const expectedApplicable = [...new Set(graph.relationships.flatMap(({ relationship }) => relationshipSignature(relationship)!.validation_obligations))].sort();
    assert.deepEqual([...new Set(graph.obligation_witnesses.map(({ obligation_id }) => obligation_id))].sort(), expectedApplicable);
    assert.equal(graph.obligation_applicability.length, 28);
    assert.deepEqual(graph.obligation_applicability.map(({ classification }) => classification), Array(28).fill("applicable"));
    assert.equal(graph.obligation_outcomes.length, graph.obligation_witnesses.length);
    const representativeByObligation = new Map(graph.obligation_witnesses.map((witness) => [witness.obligation_id, witness]));
    assert.equal(representativeByObligation.size, 28);
    for (const [obligationId, witness] of representativeByObligation) {
      const hostile = hostileObligationCase(graph, witness);
      assert.throws(() => evaluateCompiledObligationWitness(hostile.graph, hostile.witness), (error: unknown) => {
        const typed = error as { code?: string; message?: string };
        return typed.code === "MTCLI_COMPILED_OBLIGATION_ENFORCEMENT" && (witness.family !== "deprecation" || typed.message?.includes("deprecated relationship alias entered") === true);
      }, obligationId);
    }
    const sparse = loadCompiledProjectGraph(canonicalProject);
    assert.equal(sparse.obligation_applicability.some(({ classification }) => classification === "applicable"), true);
    assert.equal(sparse.obligation_applicability.some(({ classification }) => classification === "inapplicable"), true);
    for (const row of sparse.obligation_applicability) { assert.notEqual(row.reason, ""); if (row.classification === "applicable") assert.notEqual(row.source_selector, null); }
    const projection = createMetaTypeFormalizationProjection(graph);
    assert.equal(projection.render_payload.graph_certificate.graph_sha256, projection.project_graph.graph_sha256);
    assert.equal(projection.render_payload.graph_certificate.source_identity.source_manifest_sha256, graph.source_manifest.manifest_sha256);
    assert.deepEqual(projection.render_payload.graph_certificate.denominators, { node_count: 18, edge_count: graph.relationships.length, backend_meta_type_count: 13, backend_relationship_count: 17, applicable_obligation_count: 28, witness_count: graph.obligation_witnesses.length });
    const projected = { nodes: projection.render_payload.project_graph.nodes, edges: projection.render_payload.project_graph.edges };
    validateGraphBoundCertificate(graph, projected, projection.render_payload.graph_certificate);
    const certificate = projection.render_payload.graph_certificate;
    for (const mutant of [
      { ...certificate, witness_outcomes: certificate.witness_outcomes.slice(1) },
      { ...certificate, applicable_obligation_ids: certificate.applicable_obligation_ids.slice(1) },
      { ...certificate, denominators: { ...certificate.denominators, node_count: certificate.denominators.node_count - 1 } },
      { ...certificate, source_identity: { ...certificate.source_identity, source_bytes_sha256: "0".repeat(64) } },
    ]) assert.throws(() => validateGraphBoundCertificate(graph, projected, mutant as typeof certificate), (error: unknown) => (error as { code?: string }).code === "MTCLI_GRAPH_CERTIFICATE");
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("whole-project generation publishes every node-language plan atomically and reproducibly", () => {
  const fixture = completeProject(); const targets = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-project-targets-"));
  try {
    const sourceBefore = snapshot(fixture.root);
    const plan = planProjectInstantiation(fixture.root, ["typescript", "python", "rust"]);
    assert.equal(plan.node_count, 18); assert.equal(plan.plan_count, 54); assert.equal(plan.artifacts.length, 56);
    const left = path.join(targets, "left"); const right = path.join(targets, "right");
    const l = publishProjectInstantiation(plan, left); const r = publishProjectInstantiation(planProjectInstantiation(fixture.root, ["rust", "python", "typescript"]), right);
    assert.equal(l.receipt.receipt_sha256, r.receipt.receipt_sha256); assert.equal(snapshot(left), snapshot(right)); assert.equal(snapshot(fixture.root), sourceBefore);
    assert.equal(l.receipt.graph_certificate.graph_sha256, plan.graph_certificate.graph_sha256);
    const cliTarget = path.join(targets, "cli"); const out: string[] = []; const errors: string[] = [];
    assert.equal(runCli(["instantiate-project", fixture.root, "--languages", "typescript,python,rust", "--target-root", cliTarget], { stdout: (value) => out.push(value), stderr: (value) => errors.push(value) }), 0, errors.at(-1));
    const cliReceipt = JSON.parse(out.at(-1)!); assert.equal(cliReceipt.artifact_count, 56); assert.equal(cliReceipt.graph_certificate.graph_sha256, plan.graph_certificate.graph_sha256); assert.equal(snapshot(cliTarget), snapshot(left));
    const typescriptPlan = planProjectInstantiation(fixture.root, ["typescript"]); const typescriptTarget = path.join(targets, "typescript-only");
    assert.equal(typescriptPlan.plan_count, 18); assert.equal(typescriptPlan.artifacts.length, 18);
    const typescriptPublication = publishProjectInstantiation(typescriptPlan, typescriptTarget);
    assert.deepEqual(typescriptPublication.receipt.languages, ["typescript"]); assert.equal(fs.existsSync(path.join(typescriptTarget, ".domainspec/project-publication.json")), true);
    const typescriptCliTarget = path.join(targets, "typescript-cli"); const typescriptOut: string[] = []; const typescriptErrors: string[] = [];
    assert.equal(runCli(["instantiate-project", fixture.root, "--languages", "typescript", "--target-root", typescriptCliTarget], { stdout: (value) => typescriptOut.push(value), stderr: (value) => typescriptErrors.push(value) }), 0, typescriptErrors.at(-1));
    assert.equal(JSON.parse(typescriptOut.at(-1)!).artifact_count, 18); assert.equal(snapshot(typescriptCliTarget), snapshot(typescriptTarget));
    const driftTarget = path.join(targets, "drift");
    const drifted = { ...plan, artifacts: Object.freeze(plan.artifacts.map((artifact, index) => index === 0 ? Object.freeze({ ...artifact, content: `${artifact.content}\n` }) : artifact)) };
    assert.throws(() => publishProjectInstantiation(drifted, driftTarget), (error: unknown) => (error as { code?: string }).code === "MTCLI_PROJECT_PLAN_DRIFT");
    assert.equal(fs.existsSync(driftTarget), false);
    const occupied = path.join(targets, "occupied"); fs.mkdirSync(occupied); fs.writeFileSync(path.join(occupied, "sentinel"), "keep");
    assert.throws(() => publishProjectInstantiation(plan, occupied), (error: unknown) => (error as { code?: string }).code === "MTCLI_PROJECT_PUBLISH_EXISTS");
    assert.equal(fs.readFileSync(path.join(occupied, "sentinel"), "utf8"), "keep");
    const raced = path.join(targets, "raced");
    assert.throws(() => publishProjectInstantiationForTest(plan, raced, { before_claim: (_stage, target) => fs.mkdirSync(target) }), (error: unknown) => (error as { code?: string }).code === "MTCLI_PROJECT_PUBLISH_EXISTS");
    assert.deepEqual(fs.readdirSync(raced), []);
    const replaced = path.join(targets, "replaced");
    assert.throws(() => publishProjectInstantiationForTest(plan, replaced, { after_receipt: () => { fs.rmSync(replaced, { recursive: true }); fs.mkdirSync(replaced); fs.writeFileSync(path.join(replaced, "competitor"), "keep"); } }), (error: unknown) => (error as { code?: string }).code === "MTCLI_PROJECT_PUBLISH_RACE");
    assert.equal(fs.readFileSync(path.join(replaced, "competitor"), "utf8"), "keep");
    const replacedReceipt = path.join(targets, "replaced-receipt");
    assert.throws(() => publishProjectInstantiationForTest(plan, replacedReceipt, { after_receipt: (receipt) => { fs.unlinkSync(receipt); fs.writeFileSync(receipt, "competing receipt\n", { flag: "wx" }); } }), (error: unknown) => (error as { code?: string }).code === "MTCLI_PROJECT_PUBLISH_RACE");
    assert.equal(fs.readFileSync(path.join(replacedReceipt, ".domainspec/project-publication.json"), "utf8"), "competing receipt\n");
    assert.deepEqual(fs.readdirSync(targets).filter((entry) => entry.startsWith(".domainspec-project-staging-")), []);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(targets, { recursive: true, force: true }); }
});

test("compiled typed references reject target-name collisions before generation", () => {
  const fixture = projectFixture();
  try {
    addDirectNode(fixture.root, "alpha", "foo-bar", "Entity", { description: "First", identity_field: "id", fields: [{ field_id: "id", type_ref: { kind: "primitive", name: "uuid" }, required: true }] });
    writeJson(path.join(fixture.root, "specs/alpha-foo/feature.json"), { schema_version: "domainspec.feature/v1", feature_id: "alpha-foo", nodes: ["bar"], edges: [] });
    writeJson(path.join(fixture.root, "specs/alpha-foo/nodes/bar.json"), { schema_version: "domainspec.node/v1", node_id: "bar", feature_id: "alpha-foo", kind: "Entity", body: { description: "Second", identity_field: "id", fields: [{ field_id: "id", type_ref: { kind: "primitive", name: "uuid" }, required: true }] } });
    updateJson(path.join(fixture.root, "project.json"), (value) => { value.features = [...value.features, "alpha-foo"].sort(); });
    addDirectNode(fixture.root, "alpha", "collision-value", "Value Object", { description: "Collision carrier", fields: ["left", "right"], invariant_refs: ["beta:can-complete-settlement"], typed_contract: { schema_version: "domainspec.typed-record/v1", ontology_node: "TEST-COLLISION-VALUE", properties: [
      { ontology_property: "TEST-COLLISION-VALUE#left", name: "left", type: { kind: "named", selector: "alpha:foo-bar" }, cardinality: "one", identity: false, meaning: "First reference." },
      { ontology_property: "TEST-COLLISION-VALUE#right", name: "right", type: { kind: "named", selector: "alpha-foo:bar" }, cardinality: "one", identity: false, meaning: "Second reference." },
    ] } });
    assert.throws(() => loadCompiledProjectGraph(fixture.root), (error: unknown) => (error as { code?: string }).code === "MTCLI_TYPE_IDENTIFIER_COLLISION");
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("typed Value Object admission requires no identity and a resolved Rule invariant", () => {
  const fixture = projectFixture();
  try {
    const body = { description: "Strict value", fields: ["value"], typed_contract: { schema_version: "domainspec.typed-record/v1", ontology_node: "TEST-STRICT-VALUE", properties: [
      { ontology_property: "TEST-STRICT-VALUE#value", name: "value", type: { kind: "scalar", name: "String" }, cardinality: "one", identity: true, meaning: "Value." },
    ] } };
    addDirectNode(fixture.root, "alpha", "strict-value", "Value Object", body);
    assert.throws(() => loadCompiledProjectGraph(fixture.root), (error: unknown) => (error as { code?: string }).code === "MTCLI_TYPED_IDENTITY");
    body.typed_contract.properties[0]!.identity = false;
    writeJson(path.join(fixture.root, "specs/alpha/nodes/strict-value.json"), { schema_version: "domainspec.node/v1", node_id: "strict-value", feature_id: "alpha", kind: "Value Object", body });
    assert.throws(() => loadCompiledProjectGraph(fixture.root), (error: unknown) => (error as { code?: string }).code === "MTCLI_VALUE_OBJECT_COMPLETE");
    (body as typeof body & { invariant_refs: string[] }).invariant_refs = ["beta:can-complete-settlement"];
    writeJson(path.join(fixture.root, "specs/alpha/nodes/strict-value.json"), { schema_version: "domainspec.node/v1", node_id: "strict-value", feature_id: "alpha", kind: "Value Object", body });
    assert.equal(loadCompiledProjectGraph(fixture.root).nodes.some(({ node_id }) => node_id === "strict-value"), true);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("legacy typed Value Object compatibility is exact-source-byte bound", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-legacy-value-object-")); const root = path.join(parent, "source");
  try {
    fs.cpSync(authOperationSource, root, { recursive: true });
    assert.equal(loadCompiledProjectGraph(root).nodes.some(({ node_id }) => node_id === "authorization-request"), true);
    const requestPath = path.join(root, "specs/auth-exact-permission/nodes/authorization-request.json");
    updateJson(requestPath, (value) => { value.body.description = `${value.body.description} Drift.`; });
    assert.throws(() => loadCompiledProjectGraph(root), (error: unknown) => (error as { code?: string }).code === "MTCLI_TYPED_IDENTITY");
  } finally { fs.rmSync(parent, { recursive: true, force: true }); }
});

test("B15 generated corpus has no hidden runtime skips", () => {
  const fixture = completeProject(); const targetParent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-b15-"));
  try {
    const plan = planProjectInstantiation(fixture.root, ["typescript", "python", "rust"]); const target = path.join(targetParent, "target"); publishProjectInstantiation(plan, target);
    const ts = plan.artifacts.filter(({ relative_path }) => relative_path.endsWith(".ts")).map(({ relative_path }) => path.join(target, relative_path));
    const py = plan.artifacts.filter(({ relative_path }) => relative_path.endsWith(".py")).map(({ relative_path }) => path.join(target, relative_path));
    const rs = plan.artifacts.filter(({ relative_path }) => relative_path.endsWith(".rs")).map(({ relative_path }) => path.join(target, relative_path));
    const tsc = spawnSync(path.resolve(import.meta.dirname, "../../node_modules/.bin/tsc"), ["--noEmit", "--target", "ES2022", "--module", "NodeNext", "--moduleResolution", "NodeNext", "--skipLibCheck", ...ts], { encoding: "utf8", cwd: target });
    assert.equal(tsc.status, 0, tsc.stderr || tsc.stdout); assert.equal(spawnSync("python3", ["-m", "py_compile", ...py], { encoding: "utf8" }).status, 0);
    for (const file of rs) { const result = spawnSync(process.env.DOMAINSPEC_RUSTC ?? "rustc", ["--edition", "2024", "--crate-type", "lib", file, "-o", `${file}.rlib`], { encoding: "utf8" }); assert.equal(result.status, 0, `${file}\n${result.stderr}`); }
    assert.deepEqual([ts.length, py.length, rs.length], [18, 18, 18]);
    const verifiedTarget = path.join(targetParent, "verified"); const out: string[] = []; const errors: string[] = [];
    const priorTsc = process.env.DOMAINSPEC_TSC;
    process.env.DOMAINSPEC_TSC = path.resolve(import.meta.dirname, "../../node_modules/.bin/tsc");
    try {
      assert.equal(runCli(["verify-project", fixture.root, "--target-root", verifiedTarget], { stdout: (value) => out.push(value), stderr: (value) => errors.push(value) }), 0, errors.at(-1));
    } finally {
      if (priorTsc === undefined) delete process.env.DOMAINSPEC_TSC; else process.env.DOMAINSPEC_TSC = priorTsc;
    }
    const verification = JSON.parse(out.at(-1)!);
    assert.equal(verification.result, "pass"); assert.equal(verification.checks.length, 8); assert.equal(verification.skipped_check_count, 0); assert.equal(verification.inferred_evidence_count, 0);
    assert.deepEqual(verification.checks.map(({ id, result }: { id: string; result: string }) => [id, result]), [
      ["source", "pass"], ["compiled-graph", "pass"], ["ds-d8-obligations", "pass"], ["artifacts", "pass"], ["receipts", "pass"], ["formalization-currentness", "pass"], ["isolated-clean-replay", "pass"], ["no-skips-or-inference", "pass"],
    ]);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(targetParent, { recursive: true, force: true }); }
});
