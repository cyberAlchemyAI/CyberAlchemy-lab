import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

import { compareIndependentRuntimeTarget } from "../src/runtime/conformance.ts";
import { runInMemoryProject } from "../src/runtime/in-memory.ts";
import { RuntimeContractError } from "../src/runtime/contracts.ts";
import { validateRuntimeReceiptBinding } from "../src/runtime/receipt.ts";
import { canonicalJson, sha256 } from "../src/input/source-manifest.ts";
import { completeL2Invocation, createCompleteL1Project } from "./helpers/l1-project.ts";
import { independentRuntimeTarget } from "./fixtures/independent-runtime-target.ts";

const capacityFixture = path.resolve("test/fixtures/capacity-decision");

test("in-memory runtime executes all 13 backend types and observes all 17 relationships", () => {
  const fixture = createCompleteL1Project();
  try {
    const receipt = runInMemoryProject(fixture.root, completeL2Invocation());
    assert.equal(receipt.outcomes.length, 16);
    assert.equal(receipt.coverage.meta_type_ids.length, 13);
    assert.equal(receipt.coverage.relationship_ids.length, 17);
    assert.equal(receipt.coverage.complete_backend_types, true);
    assert.equal(receipt.coverage.complete_backend_relationships, true);
    assert.equal(compareIndependentRuntimeTarget(receipt, independentRuntimeTarget).result, "pass");
    const mutant = { ...independentRuntimeTarget, expected_outputs: { ...independentRuntimeTarget.expected_outputs, calculation: 7 } };
    assert.deepEqual(compareIndependentRuntimeTarget(receipt, mutant).mismatches, ["calculation"]);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("domainspec-v2 run executes in a fresh process and writes a distinct deterministic receipt", () => {
  const fixture = createCompleteL1Project();
  const output = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-l2-run-"));
  const requestPath = path.join(output, "request.json"); const receiptPath = path.join(output, "runtime-receipt.json");
  try {
    fs.writeFileSync(requestPath, `${JSON.stringify(completeL2Invocation(), null, 2)}\n`);
    const cli = path.resolve("src/cli/main.ts");
    const result = spawnSync(process.execPath, ["--disable-warning=DEP0205", "--import", "tsx", cli, "run", fixture.root, "--request", requestPath, "--receipt", receiptPath], { cwd: path.resolve("."), encoding: "utf8" });
    assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
    const command = JSON.parse(result.stdout); const receipt = JSON.parse(fs.readFileSync(receiptPath, "utf8"));
    assert.equal(command.result, "pass");
    assert.equal(receipt.schema_version, "domainspec.runtime-receipt/v1");
    assert.equal(receipt.coverage.complete_backend_types, true);
    assert.equal(receipt.coverage.complete_backend_relationships, true);
    assert.match(receipt.compiled_certificate_sha256, /^[a-f0-9]{64}$/);
    assert.match(receipt.checked_interchange_sha256, /^[a-f0-9]{64}$/);
    assert.equal(validateRuntimeReceiptBinding(fixture.root, receipt), receipt);
    const foreignBinding = structuredClone(receipt);
    foreignBinding.checked_interchange_sha256 = "0".repeat(64);
    const { receipt_sha256: ignored, ...foreignBody } = foreignBinding;
    foreignBinding.receipt_sha256 = sha256(canonicalJson(foreignBody));
    assert.throws(() => validateRuntimeReceiptBinding(fixture.root, foreignBinding), (error: unknown) => (error as { code?: string }).code === "MTCLI_RUNTIME_RECEIPT_INTERCHANGE");
    const missingOutcomes = structuredClone(receipt) as Record<string, unknown>;
    delete missingOutcomes.outcomes;
    const { receipt_sha256: missingDigest, ...missingBody } = missingOutcomes;
    missingOutcomes.receipt_sha256 = sha256(canonicalJson(missingBody));
    assert.throws(() => validateRuntimeReceiptBinding(fixture.root, missingOutcomes), (error: unknown) => (error as { code?: string }).code === "MTCLI_RUNTIME_RECEIPT_SCHEMA");
    const forgedOutput = structuredClone(receipt);
    forgedOutput.outcomes[0]!.output_sha256 = "0".repeat(64);
    const { receipt_sha256: forgedDigest, ...forgedBody } = forgedOutput;
    forgedOutput.receipt_sha256 = sha256(canonicalJson(forgedBody));
    assert.throws(() => validateRuntimeReceiptBinding(fixture.root, forgedOutput), (error: unknown) => (error as { code?: string }).code === "MTCLI_RUNTIME_RECEIPT_OUTPUT");
    const repeat = runInMemoryProject(fixture.root, completeL2Invocation());
    assert.equal(repeat.receipt_sha256, receipt.receipt_sha256);
    const originalBytes = fs.readFileSync(receiptPath, "utf8");
    const overwrite = spawnSync(process.execPath, ["--disable-warning=DEP0205", "--import", "tsx", cli, "run", fixture.root, "--request", requestPath, "--receipt", receiptPath], { cwd: path.resolve("."), encoding: "utf8" });
    assert.equal(overwrite.status, 22);
    assert.equal(JSON.parse(overwrite.stderr).code, "MTCLI_RUNTIME_RECEIPT_EXISTS");
    assert.equal(fs.readFileSync(receiptPath, "utf8"), originalBytes);
    const schemas = path.resolve("contracts");
    const schemaCheck = spawnSync("python3", ["-c", "import json,sys\nfrom jsonschema import Draft202012Validator\nfor schema,value in ((json.load(open(sys.argv[1])),json.load(open(sys.argv[3]))),(json.load(open(sys.argv[2])),json.load(open(sys.argv[4])))):Draft202012Validator(schema).validate(value)", path.join(schemas, "runtime-invocation.schema.json"), path.join(schemas, "runtime-receipt.schema.json"), requestPath, receiptPath], { encoding: "utf8" });
    assert.equal(schemaCheck.status, 0, schemaCheck.stderr);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(output, { recursive: true, force: true }); }
});

test("runtime request, entry, semantic failures, and receipt overwrite fail closed", () => {
  const fixture = createCompleteL1Project();
  try {
    const duplicate = structuredClone(completeL2Invocation()) as { steps: Array<{ step_id: string }> };
    duplicate.steps[1]!.step_id = duplicate.steps[0]!.step_id;
    assert.throws(() => runInMemoryProject(fixture.root, duplicate), (error: unknown) => error instanceof RuntimeContractError && error.code === "MTCLI_RUNTIME_DUPLICATE");
    const unknown = structuredClone(completeL2Invocation()) as { steps: Array<{ selector: string }> };
    unknown.steps[0]!.selector = "alpha:missing";
    assert.throws(() => runInMemoryProject(fixture.root, unknown), (error: unknown) => error instanceof RuntimeContractError && error.code === "MTCLI_RUNTIME_ENTRY");
    const invalid = structuredClone(completeL2Invocation()) as { steps: Array<{ step_id: string; input: Record<string, unknown> }> };
    invalid.steps.find(({ step_id }) => step_id === "calculation")!.input = { inputs: { subtotal: 10, fee: 1, divisor: 0 } };
    assert.throws(() => runInMemoryProject(fixture.root, invalid), (error: unknown) => error instanceof RuntimeContractError && error.code === "MTCLI_RUNTIME_CALCULATION");
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("runtime receipt is causally bound to authored source", () => {
  const fixture = createCompleteL1Project();
  try {
    const before = runInMemoryProject(fixture.root, completeL2Invocation());
    const file = path.join(fixture.root, "specs/alpha/nodes/find-customer.json"); const node = JSON.parse(fs.readFileSync(file, "utf8"));
    node.body.typed_contract.projection = ["customer_id"]; fs.writeFileSync(file, `${JSON.stringify(node, null, 2)}\n`);
    const after = runInMemoryProject(fixture.root, completeL2Invocation());
    assert.notEqual(after.source_manifest_sha256, before.source_manifest_sha256);
    assert.notEqual(after.compiled_certificate_sha256, before.compiled_certificate_sha256);
    assert.notEqual(after.checked_interchange_sha256, before.checked_interchange_sha256);
    assert.notEqual(after.receipt_sha256, before.receipt_sha256);
    assert.notEqual(after.outcomes.find(({ step_id }) => step_id === "query")!.output_sha256, before.outcomes.find(({ step_id }) => step_id === "query")!.output_sha256);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("typed Entity and Operation execute their compiled contracts and reject hostile values", () => {
  const invocation = (requestedUnits: number, availableUnits: number) => ({
    schema_version: "domainspec.runtime-invocation/v1", invocation_id: "typed-capacity", provider: "in-memory-v1",
    steps: [
      { step_id: "snapshot", selector: "capacity-decision:capacity-snapshot", input: { record: { request_id: "request-1", requested_units: requestedUnits, available_units: availableUnits } } },
      { step_id: "decision", selector: "capacity-decision:decide-capacity", input: { parameters: { snapshot: { request_id: "request-1", requested_units: requestedUnits, available_units: availableUnits } } } },
    ],
  });
  const accepted = runInMemoryProject(capacityFixture, invocation(4, 5));
  assert.deepEqual(accepted.outcomes[0]!.output, { identity: "request-1", record: { request_id: "request-1", requested_units: 4, available_units: 5 } });
  assert.deepEqual(accepted.outcomes[1]!.output, { ok: true, result: { variant: "Accept", payload: null }, continuation: null });
  const rejected = runInMemoryProject(capacityFixture, invocation(5, 5));
  assert.deepEqual(rejected.outcomes[1]!.output, { ok: false, result: { variant: "Reject", payload: null }, continuation: "return-reject-without-state-change" });
  const hostile = invocation(-1, 5);
  assert.throws(() => runInMemoryProject(capacityFixture, hostile), (error: unknown) => error instanceof RuntimeContractError && error.code === "MTCLI_RUNTIME_TYPE");
});

test("typed Value Object uses the compiled record contract for structural equality", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-l2-typed-vo-")); const root = path.join(parent, "source");
  try {
    fs.cpSync(capacityFixture, root, { recursive: true });
    const featurePath = path.join(root, "specs/capacity-decision/feature.json"); const feature = JSON.parse(fs.readFileSync(featurePath, "utf8"));
    feature.nodes.push("capacity-amount"); fs.writeFileSync(featurePath, `${JSON.stringify(feature, null, 2)}\n`);
    fs.writeFileSync(path.join(root, "specs/capacity-decision/nodes/capacity-amount.json"), `${JSON.stringify({
      schema_version: "domainspec.node/v1", node_id: "capacity-amount", feature_id: "capacity-decision", kind: "Value Object",
      body: { description: "Typed amount.", fields: ["currency", "units"], typed_contract: { schema_version: "domainspec.typed-record/v1", ontology_node: "CAPACITY-AMOUNT", properties: [
        { ontology_property: "CAPACITY-AMOUNT#currency", name: "currency", type: { kind: "scalar", name: "String" }, cardinality: "one", identity: false, meaning: "Currency code." },
        { ontology_property: "CAPACITY-AMOUNT#units", name: "units", type: { kind: "scalar", name: "UInt64" }, cardinality: "one", identity: false, meaning: "Unsigned units." },
      ] } },
    }, null, 2)}\n`);
    const request = { schema_version: "domainspec.runtime-invocation/v1", invocation_id: "typed-value-object", provider: "in-memory-v1", steps: [{ step_id: "amount", selector: "capacity-decision:capacity-amount", input: { left: { currency: "GBP", units: 2 }, right: { currency: "GBP", units: 2 } } }] };
    assert.deepEqual(runInMemoryProject(root, request).outcomes[0]!.output, { equal: true });
    const hostile = structuredClone(request) as { steps: Array<{ input: { right: Record<string, unknown> } }> }; hostile.steps[0]!.input.right.extra = true;
    assert.throws(() => runInMemoryProject(root, hostile), (error: unknown) => error instanceof RuntimeContractError && error.code === "MTCLI_RUNTIME_INPUT");
  } finally { fs.rmSync(parent, { recursive: true, force: true }); }
});
