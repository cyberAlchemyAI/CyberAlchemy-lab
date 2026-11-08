import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../src/application-executable.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { digest, json } from "../src/domainspec-profile.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { testTypeScript } from "./toolchain.js";

function fixture(authored = false) {
  const f = executableFixture();
  const source = f.source.replace("  requires EligibleOrder", "  requires EligibleOrder\n  produces OrderSubmitted") + `event OrderSubmitted:
  event-type order-submitted
  version 1
  occurrence-id eventId String
  occurred-at generated
  orderId -> Order.id
` + (authored ? `realization SubmitOrderExecution:
  operation SubmitOrder
  input request
  event-input submitted OrderSubmitted
  read current <- Order key request.id
  guard EligibleOrder(order <- current)
  write Order replace <- request
  event OrderSubmitted <- submitted
  result <- request
  atomicity state-and-outbox
  continuation awaited-settlement
` : "");
  const bindings = { ...f.bindings, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) },
    declarations: { ...f.bindings.declarations, OrderSubmitted: { ontology: "FIXTURE-SUBMITTED", meaning: "Explicit synthetic submission occurrence." } } };
  const formation = lowerApplicationDomain(source, bindings, f.sources);
  const interpretation = { ...f.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(source, bindings, f.sources, interpretation);
  const execution = { ...f.execution, projection_sha256: digest(json(projection)), selection: { ...f.execution.selection,
    operations: f.execution.selection.operations.map(op => ({ ...op, events: [{ slot: "commerce:order-submitted", target: "commerce:order-submitted", parameter: "submitted" }] })) } };
  const { operations, ...selection } = execution.selection;
  return { ...f, source, bindings, formation, interpretation, expectedOperations: operations,
    execution: authored ? { ...execution, schema_version: "alchlang.application-execution/v2-candidate", selection } : execution };
}

test("authored produces edges and effect slots require exact realization coverage", async () => {
  const f = fixture(); const compiler = await loadDomainSpecCompiler();
  const node = JSON.parse(f.formation.projectFiles["specs/commerce/nodes/submit-order.json"]!);
  assert.deepEqual(node.body.effects, ["commerce:order-submitted"]);
  assert.equal(JSON.parse(f.formation.projectFiles["specs/commerce/edges/submit-order-produces-order-submitted.json"]!).relationship, "produces");
  const prepare = (execution: unknown) => prepareApplicationExecutable(f.source, f.bindings, f.sources, f.interpretation, execution, compiler);
  assert.ok(prepare(f.execution));
  for (const mutate of [
    (e: any) => { e.selection.operations[0].events = []; },
    (e: any) => { e.selection.operations[0].events[0].target = "commerce:order"; },
    (e: any) => { e.selection.operations[0].events[0].slot = "hidden-event"; },
    (e: any) => { e.selection.operations[0].events.push({ slot: "extra", target: "commerce:other", parameter: "extra" }); },
  ]) { const bad = structuredClone(f.execution); mutate(bad); assert.throws(() => prepare(bad), /APPLICATION_EXECUTION_/); }
});

for (const authored of [false, true]) test(`native ${authored ? "source-derived realization" : "explicit legacy Operation"} commits writes and Event intents without claiming delivery`, async t => {
  const f = fixture(authored); const compiler = await loadDomainSpecCompiler();
  const candidate = prepareApplicationExecutable(f.source, f.bindings, f.sources, f.interpretation, f.execution, compiler);
  assert.deepEqual(candidate.selection.operations, f.expectedOperations);
  const temp = mkdtempSync(path.join(tmpdir(), "alch-effects-")); t.after(() => rmSync(temp, { recursive: true, force: true }));
  const write = (dir: string, files: Record<string, string>) => { for (const [relative, bytes] of Object.entries(files)) {
    const target = path.join(dir, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
  } };
  const sourceRoot = path.join(temp, "source"); write(sourceRoot, candidate.projectFiles);
  const result = compileApplicationExecutable(candidate, compiler.compileProject(sourceRoot).graph, compiler);
  const generated = path.join(temp, "generated"); write(generated, Object.fromEntries(result.view.artifacts.map(a => [a.relative_path, a.content])));
  execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs",
    "--rootDir", generated, "--outDir", path.join(temp, "js"), ...result.view.artifacts.map(a => path.join(generated, a.relative_path))], { encoding: "utf8" });
  const module = result.view.artifacts.find(a => a.relative_path.endsWith("/operations/submit-order.ts")); assert.ok(module);
  const run = createRequire(import.meta.url)(path.join(temp, "js", module.relative_path.replace(/\.ts$/, ".js"))).operationSubmitOrder;
  for (const scenario of ["success", "guard-rejection", "invalid-event", "invalid-occurrence", "commit-rejection", "commit-uncertain"]) {
    const calls: string[] = []; let batch: any;
    const outcome = await run({ request: { id: "1", accepted: true }, submitted: { occurrence: { "event-id": scenario === "invalid-occurrence" ? 42 : "event-1" }, payload: { "order-id": scenario === "invalid-event" ? -1n : "1" } } }, {
      clocks: { "commerce:order-submitted": () => { calls.push("clock"); return "explicit-time"; } },
      store: { begin: async () => { calls.push("begin"); return {
        read: async () => { calls.push("read"); return { id: "1", accepted: scenario !== "guard-rejection" }; },
        commit: async (value: unknown) => { calls.push("commit"); batch = value;
          if (scenario === "commit-uncertain") throw Error("connection lost");
          return { status: scenario === "commit-rejection" ? "rejected" : "committed" }; },
        rollback: async () => { calls.push("rollback"); },
      }; } },
    });
    if (scenario === "guard-rejection" || scenario === "invalid-event" || scenario === "invalid-occurrence") {
      assert.equal(batch, undefined); assert.deepEqual(calls, ["begin", "read", "rollback"]);
      assert.equal(outcome.stage, scenario === "guard-rejection" ? "guard" : "event");
      assert.equal(outcome.status, scenario === "guard-rejection" ? "rejected" : "failed");
    } else {
      assert.deepEqual(calls, ["begin", "read", "clock", "commit"]);
      assert.equal(batch.writes.length, 1); assert.equal(batch.events.length, 1);
      assert.deepEqual(batch.events[0], { slot: "commerce:order-submitted", target: "commerce:order-submitted", value: {
        type: "order-submitted", version: "1", occurrence: { "event-id": "event-1" }, occurredAt: "explicit-time", payload: { "order-id": 1n },
      } });
      assert.ok(Object.isFrozen(batch)); assert.ok(Object.isFrozen(batch.events));
      assert.equal(outcome.status, scenario === "success" ? "committed" : scenario === "commit-rejection" ? "rejected" : "indeterminate");
      if (scenario === "commit-uncertain") assert.equal(outcome.code, "COMMIT_UNCERTAIN");
    }
    assert.equal(Object.hasOwn(outcome, "delivered"), false);
    assert.equal(Object.hasOwn(outcome, "published"), false);
  }
});
