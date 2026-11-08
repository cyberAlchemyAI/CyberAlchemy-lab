import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { digest } from "../src/domainspec-profile.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { lowerApplicationDomain, assertApplicationDomainCurrent } from "../src/application-domain-lowering.js";
import { formalLoweringFixture } from "./fixtures/formal-lowering-fixture.js";

export function applicationFixture() {
  const f = formalLoweringFixture();
  const source = f.source + `entity Order:
  id UInt64
  identity id
  accepted Bool
operation SubmitOrder:
  input Order
  output Order
  reads Order
  writes Order
  requires EligibleOrder
`;
  const formal = { ...f.input, source_sha256: digest(source) };
  const input = { schema_version: "alchlang.application-bindings/v1", source_sha256: digest(source), owner: "fixture-owner", formal,
    declarations: {
      Order: { ontology: "FIXTURE-ORDER", meaning: "A synthetic order with an explicit identity and acceptance flag.", properties: {
        id: { ontology: "FIXTURE-ORDER#id", meaning: "Synthetic order identity." },
        accepted: { ontology: "FIXTURE-ORDER#accepted", meaning: "Synthetic acceptance flag." },
      } },
      EligibleOrder: { ontology: "FIXTURE-ELIGIBILITY", meaning: "The explicit claim gates submission." },
      SubmitOrder: { ontology: "FIXTURE-SUBMIT", meaning: "Submit the selected order.", failure_continuation: "return-submission-error" },
    } };
  return { source, input, sources: f.sources };
}

test("one source forms exact domain and formal partitions without losing operation shape", () => {
  const f = applicationFixture(); const lower = lowerApplicationDomain(f.source, f.input, f.sources);
  assert.deepEqual(lower, lowerApplicationDomain(f.source, structuredClone(f.input), f.sources));
  const node = JSON.parse(lower.projectFiles["specs/commerce/nodes/order.json"]!);
  assert.equal(node.kind, "Entity"); assert.equal(node.body.typed_contract.properties[0].identity, true);
  const operation = JSON.parse(lower.projectFiles["specs/commerce/nodes/submit-order.json"]!);
  assert.equal(operation.body.guard, "commerce:eligible-order");
  assert.equal(operation.body.failure_continuation, "return-submission-error");
  assert.deepEqual(lower.operationShapes.operations[0]!.input, { kind: "named", selector: "commerce:order" });
  assert.deepEqual(lower.operationShapes.operations[0]!.output, { kind: "named", selector: "commerce:order" });
  assert.equal(lower.trace.declarations.length, 4);
  assert.equal(lower.trace.formation_only, true);
  assert.equal((lower.conditions.bindings[0]!.claim_ref as any).claim_id, "FormalClaim:fixture");
});

test("current DomainSpec compiler validates the generated graph and exact cross-partition join", async t => {
  const f = applicationFixture(); const lower = lowerApplicationDomain(f.source, f.input, f.sources);
  const compiler = await loadDomainSpecCompiler();
  const temp = mkdtempSync(path.join(os.tmpdir(), "alch-application-domain-"));
  t.after(() => rmSync(temp, { recursive: true, force: true }));
  for (const [relative, bytes] of Object.entries(lower.projectFiles)) {
    const file = path.join(temp, relative); mkdirSync(path.dirname(file), { recursive: true }); writeFileSync(file, bytes, { flag: "wx" });
  }
  const compiled = compiler.compileProject(temp);
  assert.equal(compiled.graph.nodes.length, 3);
  assert.equal(compiled.graph.relationships.filter(r => r.relationship === "enforces").length, 1);
  assert.equal(compiled.graph.nodes.some(n => n.kind === "FormalClaim"), false);
  const bytes = new Map(Object.entries(lower.files).map(([name, content]) => [name, Buffer.from(content)]));
  const joined: any = compiler.compileFormalConditionBindings(compiled.graph, lower.conditions, bytes);
  assert.equal(joined.bindings[0].rule_ref, "commerce:eligible-order");
  assert.equal(joined.domain_source_manifest_sha256, compiled.graph.source_manifest.manifest_sha256);
  bytes.set("formalization/claims/EligibleClaim.json", Buffer.from("{}"));
  assert.throws(() => compiler.compileFormalConditionBindings(compiled.graph, lower.conditions, bytes), /CONDITION_SOURCE_STALE/);
});

test("meaning, metadata coverage, identity, and source drift fail before output", () => {
  const f = applicationFixture();
  assert.throws(() => lowerApplicationDomain(f.source + "\n", f.input, f.sources), /APPLICATION_BINDING_SOURCE/);
  const missing: any = structuredClone(f.input); delete missing.declarations.Order.properties.accepted;
  assert.throws(() => lowerApplicationDomain(f.source, missing, f.sources), /APPLICATION_BINDING_COVERAGE/);
  const invented: any = structuredClone(f.input); invented.declarations.SubmitOrder.failure_continuation = "";
  assert.throws(() => lowerApplicationDomain(f.source, invented, f.sources), /APPLICATION_BINDING/);
  const newSource = f.source.replace("  identity id\n", "");
  assert.throws(() => lowerApplicationDomain(newSource, { ...f.input, source_sha256: digest(newSource), formal: { ...f.input.formal, source_sha256: digest(newSource) } }, f.sources), /APPLICATION_IDENTITY/);
  const property = structuredClone(f.input); property.declarations.Order.properties.id.ontology = "OTHER-OWNER#id";
  assert.throws(() => lowerApplicationDomain(f.source, property, f.sources), /APPLICATION_ONTOLOGY/);
});

test("every formed artifact is bound and edits cannot be hidden by rehashing its trace", () => {
  const f = applicationFixture(); const formed = lowerApplicationDomain(f.source, f.input, f.sources);
  assertApplicationDomainCurrent(f.source, f.input, f.sources, formed);
  assert.deepEqual(Object.keys(formed.trace.formed_files).sort(), Object.keys(formed.files).sort());
  for (const [file, bytes] of Object.entries(formed.files)) {
    assert.deepEqual(formed.trace.formed_files[file], { sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes) });
    const changed = structuredClone(formed);
    (changed.files as Record<string, string>)[file] = bytes + " ";
    changed.trace.formed_files[file] = { sha256: digest(bytes + " "), size_bytes: Buffer.byteLength(bytes + " ") };
    assert.throws(() => assertApplicationDomainCurrent(f.source, f.input, f.sources, changed), /APPLICATION_FORMATION_STALE/);
    const missing = structuredClone(formed);
    delete (missing.files as Record<string, string>)[file];
    delete missing.trace.formed_files[file];
    assert.throws(() => assertApplicationDomainCurrent(f.source, f.input, f.sources, missing), /APPLICATION_FORMATION_STALE/);
  }
  for (const file of Object.keys(formed.projectFiles)) {
    const changed = structuredClone(formed); changed.projectFiles[file] += " ";
    changed.trace.project_files[file] = digest(changed.projectFiles[file]!);
    assert.throws(() => assertApplicationDomainCurrent(f.source, f.input, f.sources, changed), /APPLICATION_FORMATION_STALE/);
  }
  const extra = structuredClone(formed); (extra.files as Record<string, string>)["unbound.json"] = "{}";
  assert.throws(() => assertApplicationDomainCurrent(f.source, f.input, f.sources, extra), /APPLICATION_FORMATION_STALE/);
});

test("authored enum variant meaning survives lowering without extending backend semantics", () => {
  const f = applicationFixture();
  const source = f.source + 'enum Status:\n  value Pending "Awaiting the customer’s confirmation."\n  value Submitted\n';
  const input = { ...f.input, source_sha256: digest(source), formal: { ...f.input.formal, source_sha256: digest(source) },
    declarations: { ...f.input.declarations, Status: { ontology: "FIXTURE-STATUS", meaning: "Order status.",
      variants: { Pending: "FIXTURE-STATUS#Pending", Submitted: "FIXTURE-STATUS#Submitted" } } } };
  const formed = lowerApplicationDomain(source, input, f.sources);
  const variants = (formed.trace.declarations.find(d => d.source_id === "Status") as any).variants;
  assert.equal(variants[0].meaning, "Awaiting the customer’s confirmation.");
  assert.equal(variants[1].meaning, null);
  assert.equal(variants[0].target, "Pending");
  assertApplicationDomainCurrent(source, input, f.sources, formed);
  const changed = structuredClone(formed);
  (changed.trace.declarations.find(d => d.source_id === "Status") as any).variants[0].meaning = "Different meaning";
  assert.throws(() => assertApplicationDomainCurrent(source, input, f.sources, changed), /APPLICATION_FORMATION_STALE/);
});
