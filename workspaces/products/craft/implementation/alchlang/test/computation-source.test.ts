import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { COMPUTATION_CAPABILITY, lowerComputationSource, parseComputationSource, parseComputationCompanion, computationDigest } from "../src/computation-source.js";
import { parseDomainSource } from "../src/parser.js";

const folder = fileURLToPath(new URL("../examples/computation/", import.meta.url));
const options = { capability: COMPUTATION_CAPABILITY };
const source = readFileSync(folder + "summary.alch", "utf8");
const companion = readFileSync(folder + "summary.alch.computation.json", "utf8");
const changed = readFileSync(folder + "summary-count-two.alch", "utf8");
const rejects = (action: () => unknown, code: string) => assert.throws(action, new RegExp(code));

test("every complete readable chapter source lowers with its exact reviewed companion", () => {
  for (const file of readdirSync(folder).filter(name => name.endsWith(".alch"))) {
    const text = readFileSync(folder + file, "utf8");
    const lowered = lowerComputationSource(text, readFileSync(folder + file + ".computation.json", "utf8"), options);
    assert.equal(lowered.source_profile, "application-v1");
    assert.equal(lowered.contract.stage, "full-computation");
    assert.ok(Object.keys(lowered.source_map).length > 0);
  }
});

test("record reducer lowers the actual declared Rule, Mapping and Calculation references", () => {
  const lowered = lowerComputationSource(source, companion, options);
  const contract = lowered.contract;
  assert.equal(lowered.source_binding.owner_ref, "delivery_team");
  assert.equal(lowered.source_binding.meaning, JSON.parse(companion).declarations.main.meaning);
  assert.deepEqual(Object.keys(lowered.source_binding.declaration_meanings), ["$.records[0]", "$.records[1]", "$.functions[0]", "$.functions[1]", "$.functions[2]"]);
  assert.equal(lowered.source_binding.declaration_meanings["$.records[0]"], JSON.parse(companion).declarations.order.meaning);
  assert.equal(lowered.source_binding.declaration_meanings["$.functions[2]"], JSON.parse(companion).declarations.summary_step.meaning);
  assert.deepEqual(contract.functions.map((f: any) => [f.name, f.kind]), [["eligible", "Rule"], ["amount", "Mapping"], ["summary_step", "Calculation"]]);
  assert.equal(contract.expression.op, "fold");
  assert.equal(contract.expression.source.source.predicate.declaration, "eligible");
  assert.equal(contract.expression.body.declaration, "summary_step");
  assert.equal(contract.expression.initial.fields.count.value, "0");
  assert.equal(contract.functions[2].body.fields.count.right.value, "1");
});

test("a meaningful authored count 1 to 2 edit requires the updated exact companion", () => {
  rejects(() => lowerComputationSource(changed, companion, options), "COMPUTATION_BINDING_SOURCE");
  const updatedHashOnly = JSON.parse(companion); updatedHashOnly.source_sha256 = computationDigest(changed);
  rejects(() => lowerComputationSource(changed, updatedHashOnly, options), "COMPUTATION_BINDING_DECLARATION");
  const fresh = lowerComputationSource(changed, readFileSync(folder + "summary-count-two.alch.computation.json", "utf8"), options);
  assert.equal(fresh.contract.functions[2].body.fields.count.right.value, "2");
  assert.notEqual(fresh.source_sha256, computationDigest(source));
});

test("capability command selection and source successor are both explicit", () => {
  rejects(() => parseComputationSource(source, undefined as any), "COMPUTATION_CAPABILITY_REQUIRED");
  rejects(() => parseComputationSource(source.replace(`capability ${COMPUTATION_CAPABILITY}\n`, ""), options), "COMPUTATION_REQUIRED");
  rejects(() => parseComputationSource(source.replace("profile application-v1", "profile legacy-sfol-v1"), options), "COMPUTATION_PROFILE");
  assert.throws(() => parseDomainSource(source), /TEXT_SYNTAX/);
});

test("exact companion rejects missing extra duplicated stale and wrong-kind members", () => {
  const binding = JSON.parse(companion);
  const missing = structuredClone(binding); delete missing.declarations.amount;
  rejects(() => lowerComputationSource(source, missing, options), "COMPUTATION_BINDING_SHAPE");
  const extra = structuredClone(binding); extra.declarations.phantom = binding.declarations.amount;
  rejects(() => lowerComputationSource(source, extra, options), "COMPUTATION_BINDING_SHAPE");
  const kind = structuredClone(binding); kind.declarations.eligible.kind = "Calculation";
  rejects(() => lowerComputationSource(source, kind, options), "COMPUTATION_BINDING_DECLARATION");
  rejects(() => parseComputationCompanion('{"owner":"one","owner":"two"}'), "duplicate companion key owner");
  rejects(() => parseComputationCompanion('{"declarations":{"x":{},"\\u0078":{}}}'), "duplicate companion key x");
});

test("lowering admits safe snapshots before validation and identifies raw and object bytes explicitly", () => {
  const binding = JSON.parse(companion);
  const object = lowerComputationSource(source, binding, options);
  const text = lowerComputationSource(source, companion, options);
  const nullPrototype = Object.assign(Object.create(null), binding);
  assert.deepEqual(lowerComputationSource(source, nullPrototype, options), object);
  assert.deepEqual(text.contract, object.contract);
  assert.deepEqual(text.source_binding, object.source_binding);
  assert.equal(text.companion_sha256, computationDigest(companion));
  assert.equal(text.companion_text, companion);
  assert.equal(text.companion_identity_kind, "raw-utf8");
  assert.equal(object.companion_sha256, computationDigest(object.companion_text));
  assert.equal(object.companion_identity_kind, "canonical-json");
  let calls = 0;
  Object.defineProperty(binding, "owner", { get() { calls++; return "delivery_team"; }, enumerable: true });
  rejects(() => lowerComputationSource(source, binding, options), "COMPUTATION_BINDING_DATA");
  const nested = JSON.parse(companion);
  Object.defineProperty(nested.declarations.main, "meaning", { get() { calls++; return "meaning"; }, enumerable: true });
  rejects(() => lowerComputationSource(source, nested, options), "COMPUTATION_BINDING_DATA");
  assert.equal(calls, 0);
  const caller = JSON.parse(companion);
  const lowered = lowerComputationSource(source, caller, options);
  caller.declarations.main.meaning = "mutated after admission";
  assert.equal(lowered.source_binding.meaning, object.source_binding.meaning);
  assert.equal(lowered.companion_sha256, object.companion_sha256);
});

test("duplicate source fields declarations inputs and missing root declaration reject", () => {
  rejects(() => parseComputationSource(source.replace("field amount:UInt64", "field amount:UInt64\n  field amount:UInt64"), options), "COMPUTATION_DUPLICATE");
  rejects(() => parseComputationSource(source.replace("input item:UInt64", "input item:UInt64\n  input item:UInt64"), options), "COMPUTATION_DUPLICATE");
  rejects(() => parseComputationSource(source + "\nrecord order:\n  meaning \"dup\"\n  field a:Bool\n", options), "COMPUTATION_DUPLICATE");
  rejects(() => parseComputationSource(source.replace("compute main", "compute phantom"), options), "COMPUTATION_ROOT");
  rejects(() => parseComputationSource(source.replace("compute main", "compute eligible"), options), "COMPUTATION_ROOT");
});

test("syntax errors and normalized expression paths retain actual source locations", () => {
  const parsed = parseComputationSource(source, options);
  const line = source.split("\n").findIndex(value => value.includes("fold(map(")) + 1;
  assert.deepEqual(parsed.source_map["$.expression"], { line, column: 5 });
  const malformed = source.replace("summary_step(state,item)", "summary_step(state,@)");
  assert.throws(() => parseComputationSource(malformed, options), new RegExp(`COMPUTATION_SYNTAX at \\$line:${line + 1}:column:`));
});

test("source and expression nesting caps reject before unbounded parsing", () => {
  rejects(() => parseComputationSource(" ".repeat(262145), options), "COMPUTATION_SOURCE_BOUND");
  const expression = "(".repeat(33) + "0" + ")".repeat(33);
  const single = readFileSync(folder + "map.alch", "utf8").replace(/expression .+/, "expression " + expression);
  rejects(() => parseComputationSource(single, options), "COMPUTATION_SOURCE_BOUND");
});

test("finite for sugar shares indexed fold normalization and tightly adjoining type delimiters parse", () => {
  const finite = readFileSync(folder + "finite-loop.alch", "utf8");
  const ordinary = parseComputationSource(finite, options);
  const sugar = parseComputationSource(finite.replace("indexed-fold(", "for(").replace("List<UInt64,10> =", "List<UInt64,10>="), options);
  assert.deepEqual(sugar.contract, ordinary.contract);
  const matched = parseComputationSource(readFileSync(folder + "state-machine-match.alch", "utf8"), options);
  assert.equal(matched.contract.expression.op, "match");
  assert.equal(matched.contract.expression.binding.type.kind, "outcome");
});
