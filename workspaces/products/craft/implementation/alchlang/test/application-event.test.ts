import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { parseDomainSource } from "../src/parser.js";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../src/application-executable.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { digest, json } from "../src/domainspec-profile.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { testTypeScript } from "./toolchain.js";

const event = `event OrderSubmitted:
  event-type order-submitted
  version 1
  occurrence-id eventId String
  occurred-at required
  orderId -> Order.id
  accepted optional<Bool>
`;
function fixture(suffix = event) {
  const f = executableFixture(); const source = f.source + suffix;
  const bindings = { ...f.bindings, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) },
    declarations: { ...f.bindings.declarations, OrderSubmitted: { ontology: "FIXTURE-SUBMITTED", meaning: "Synthetic order submission occurrence." } } };
  return { ...f, source, bindings };
}

test("Event metadata and occurrence identity lower distinctly from payload and transport", () => {
  const f = fixture(); const formed = lowerApplicationDomain(f.source, f.bindings, f.sources);
  const body = JSON.parse(formed.projectFiles["specs/commerce/nodes/order-submitted.json"]!).body;
  assert.deepEqual(body, { description: "Synthetic order submission occurrence.", event_type: "order-submitted", version: "1",
    occurrence_id: { field_id: "event-id", type_ref: { kind: "primitive", name: "string" }, required: true },
    occurred_at_policy: "required", payload: [
      { field_id: "order-id", type_ref: { kind: "reference", selector: "commerce:order" }, required: true },
      { field_id: "accepted", type_ref: { kind: "primitive", name: "boolean" }, required: false },
    ] });
  const trace = formed.trace.declarations.find(d => d.source_id === "OrderSubmitted")!;
  assert.equal(trace.ontology_event, "FIXTURE-SUBMITTED");
  assert.equal(trace.publication, false); assert.equal(trace.occurrence_registration, false);
  assert.equal(Object.hasOwn(body, "typed_contract"), false, "Event is not recast as a record");
});

test("Event decoding rejects malformed metadata and lowering never infers missing or lossy representation", () => {
  for (const [before, after] of [
    ["version 1", "version 0"], ["event-type order-submitted", "event-type OrderSubmitted"],
    ["occurred-at required", "occurred-at automatic"], ["occurrence-id eventId String", "occurrence-id eventId optional<String>"],
    ["version 1", "version 1\n  version 2"], ["occurrence-id eventId String", "occurrence-id eventId String\n  occurrence-id other String"],
  ]) assert.throws(() => parseDomainSource(fixture(event.replace(before!, after!)).source), /APPLICATION_EVENT/);
  for (const clause of ["  event-type order-submitted\n", "  version 1\n", "  occurrence-id eventId String\n", "  occurred-at required\n"]) {
    const f = fixture(event.replace(clause, ""));
    assert.throws(() => lowerApplicationDomain(f.source, f.bindings, f.sources), /APPLICATION_EVENT_REALIZATION/);
  }
  for (const field of ["amount UInt64", "orders list<String>", "order Order", "accepted optional<optional<Bool>>"]) {
    const f = fixture(event.replace("accepted optional<Bool>", field));
    assert.throws(() => lowerApplicationDomain(f.source, f.bindings, f.sources), /APPLICATION_EVENT_FIELD_UNSUPPORTED/);
  }
  const f = fixture(event + "  order-id String\n");
  assert.throws(() => lowerApplicationDomain(f.source, f.bindings, f.sources), /APPLICATION_SYMBOL_COLLISION/);
});

test("public compiler emits native Event constructors with exact identity bounds and explicit clock policy", async t => {
  const compiler = await loadDomainSpecCompiler();
  const temp = mkdtempSync(path.join(tmpdir(), "alch-event-")); t.after(() => rmSync(temp, { recursive: true, force: true }));
  for (const policy of ["required", "generated"] as const) {
    const f = fixture(event.replace("occurred-at required", `occurred-at ${policy}`));
    const formed = lowerApplicationDomain(f.source, f.bindings, f.sources);
    const interpretation = { ...f.interpretation, formation_sha256: digest(json(formed)) };
    const projection = lowerApplicationRuleProjections(f.source, f.bindings, f.sources, interpretation);
    const execution = { ...f.execution, projection_sha256: digest(json(projection)) };
    const candidate = prepareApplicationExecutable(f.source, f.bindings, f.sources, interpretation, execution, compiler);
    const root = path.join(temp, policy);
    const write = (dir: string, files: Record<string, string>) => { for (const [relative, bytes] of Object.entries(files)) {
      const target = path.join(dir, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
    } };
    const sourceRoot = path.join(root, "source"); write(sourceRoot, candidate.projectFiles);
    const result = compileApplicationExecutable(candidate, compiler.compileProject(sourceRoot).graph, compiler);
    const generated = path.join(root, "generated");
    write(generated, Object.fromEntries(result.view.artifacts.map(a => [a.relative_path, a.content])));
    execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs",
      "--rootDir", generated, "--outDir", path.join(root, "js"), ...result.view.artifacts.map(a => path.join(generated, a.relative_path))], { encoding: "utf8" });
    const module = result.view.artifacts.find(a => a.relative_path.endsWith("/events/order-submitted.ts")); assert.ok(module);
    const make = createRequire(import.meta.url)(path.join(root, "js", module.relative_path.replace(/\.ts$/, ".js"))).eventOrderSubmitted;
    let clockCalls = 0; const clock = () => { clockCalls++; return "supplied-clock-time"; };
    const input = (id: unknown) => ({ occurrence: { "event-id": "event-1" }, payload: { "order-id": id }, ...(policy === "required" ? { occurredAt: "source-time" } : {}) });
    const value = make(input("18446744073709551615"), ...(policy === "generated" ? [clock] : []));
    assert.equal(value.payload["order-id"], 18446744073709551615n);
    assert.equal(value.type, "order-submitted"); assert.equal(value.version, "1");
    assert.equal(value.occurredAt, policy === "required" ? "source-time" : "supplied-clock-time");
    assert.equal(clockCalls, policy === "generated" ? 1 : 0);
    assert.ok(Object.isFrozen(value)); assert.ok(Object.isFrozen(value.payload));
    assert.equal(Object.hasOwn(value.payload, "accepted"), false);
    for (const bad of [-1n, -1, "-1", 18446744073709551616n, "18446744073709551616", "1.5"]) {
      assert.throws(() => make(input(bad), ...(policy === "generated" ? [clock] : [])), /EVENT_INPUT/);
    }
    assert.equal(clockCalls, policy === "generated" ? 1 : 0, "invalid payload cannot trigger a clock effect");
    assert.throws(() => make({ ...input("1"), payload: { "order-id": "1", accepted: "true" } }, clock), /EVENT_INPUT/);
    if (policy === "generated") assert.throws(() => make(input("1")), /EVENT_INPUT/);
    assert.equal(make.descriptor.publication, false); assert.equal(make.descriptor.occurrence_registration, false);
  }
});
