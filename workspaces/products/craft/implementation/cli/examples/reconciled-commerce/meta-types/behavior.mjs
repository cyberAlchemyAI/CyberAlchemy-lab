import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

// Pass the namespace imported from the exact installed AlchLang package.
export async function runLegacyPermission({ alchModule: alch }) {
  const source = `domain permission-witness "Permission witness"
owner permission-witness-owner
entity Order:
  orderId: identifier required
  approved: boolean required
actor OrderService
rule allowed:
  approved == true
boundary order-authority:
  owner permission-witness-owner
permission write-order:
  actor OrderService
  action CommitOrder
  when allowed
  boundary order-authority
action CommitOrder:
  actor OrderService
  subject Order
  input orderId, approved
  requires allowed
  permission write-order
  boundary order-authority
`;
  const model = alch.compileCarrier(alch.parseDomainSource(source).carrier).plan.model;
  const request = { action_id: "CommitOrder", actor_ref: "OrderService", facts: { orderId: "order-1", approved: true }, authority_grants: ["order-authority"] };
  const wrong = structuredClone(model);
  wrong.actions.push({ ...wrong.actions[0], id: "InspectOrder" });
  wrong.permissions[0].action_refs = ["InspectOrder"];
  let calls = 0;
  const effects = [];
  const adapters = { CommitOrder: { async execute() { calls++; effects.push("committed"); return { outcome: "committed" }; } } };
  await assert.rejects(() => alch.executeAction(wrong, request, adapters), error => error.issues?.[0]?.code === "PERMISSION_ACTION_DENIED");
  assert.equal(calls, 0); assert.deepEqual(effects, []);
  await assert.rejects(() => alch.executeAction(model, { ...request, facts: { ...request.facts, approved: false } }, adapters), error => error.issues?.[0]?.code === "RULE_DENIED");
  assert.equal(calls, 0);
  for (const [edit, code] of [
    [permission => { permission.actor_refs = ["OtherActor"]; }, "ACTOR_DENIED"],
    [permission => { permission.authority_boundary_ref = "other-authority"; }, "AUTHORITY_BOUNDARY_MISMATCH"],
    [permission => { permission.condition = { operator: "eq", operands: [{ node: "literal", value_type: "integer", value: 0 }, { node: "literal", value_type: "integer", value: 1 }] }; }, "PERMISSION_DENIED"],
  ]) {
    const denied = structuredClone(model); edit(denied.permissions[0]);
    await assert.rejects(() => alch.executeAction(denied, request, adapters), error => error.issues?.[0]?.code === code);
    assert.equal(calls, 0); assert.deepEqual(effects, []);
  }
  await assert.rejects(() => alch.executeAction(model, { ...request, authority_grants: [] }, adapters), error => error.issues?.[0]?.code === "AUTHORITY_DENIED");
  assert.equal(calls, 0);
  assert.equal((await alch.executeAction(model, request, adapters)).status, "executed");
  assert.equal(calls, 1); assert.deepEqual(effects, ["committed"]);
  return { id: "M12-installed-Alch-permission-and-guard", result: "pass", refused_calls: 0, authorized_calls: 1 };
}

// Supplied consumer provider: one in-memory atomic state/outbox boundary.
// Generated code prepares and validates the batch; this provider owns committing it.
function atomicStore(initial, { failAt = -1, mode = "reject", settlement = null } = {}) {
  let state = initial;
  const outbox = [], trace = [], batches = [];
  let begins = 0;
  const dependency = { store: { async begin() {
    const index = begins++;
    trace.push(`begin:${index}`);
    let closed = false;
    return {
      async read() { throw new Error("This fixture declares no reads"); },
      async rollback() { assert.equal(closed, false); closed = true; trace.push(`rollback:${index}`); },
      async commit(batch) {
        assert.equal(closed, false); closed = true; trace.push(`commit:${index}`);
        assert.ok(Object.isFrozen(batch));
        assert.equal(batch.writes.length, 1);
        assert.equal(batch.events.length, 1);
        batches.push(batch);
        if (index === failAt && mode === "reject") return { status: "rejected" };
        if (index === failAt && mode === "throw-before") throw new Error("before commit");
        const replacement = batch.writes[0].value;
        const messages = [...outbox, ...batch.events];
        if (index === failAt && mode === "between-state-and-outbox") throw new Error("atomic draft abandoned");
        // Both successors become visible together, after all preparation succeeds.
        state = replacement;
        outbox.splice(0, outbox.length, ...messages);
        if (index === failAt && mode === "throw-after") throw new Error("lost commit acknowledgement");
        if (index === failAt && mode === "indeterminate") return { status: "indeterminate" };
        if (settlement) await settlement;
        return { status: "committed" };
      },
    };
  } } };
  return { dependency, trace, batches, state: () => state, outbox, begins: () => begins };
}

export async function runBehavior({ generatedRoot, exampleRoot }) {
  const root = path.resolve(generatedRoot);
  const files = fs.readdirSync(root, { recursive: true }).map(String);
  const load = async suffix => {
    const matches = files.filter(file => file.split(path.sep).join("/").endsWith(`features/commerce/src/${suffix}`));
    assert.equal(matches.length, 1, `Expected exactly one generated ${suffix}`);
    return import(pathToFileURL(path.join(root, matches[0])).href);
  };
  const [api, mapping, posted, released, lifecycle, perform, undo, flow, material, inboundMapping, namedApi] = await Promise.all([
    load("application/interfaces/api.js"), load("application/mappings/summary.js"),
    load("domain/events/posted.js"), load("domain/events/released.js"),
    load("domain/state-machines/lifecycle.js"), load("application/operations/perform.js"),
    load("application/operations/undo.js"), load("application/workflows/flow.js"),
    load("application/workflows/flow.material.js"), load("application/mappings/inbound-request.js"),
    load("application/interfaces/named-boundary-api.js"),
  ]);
  const values = JSON.parse(fs.readFileSync(path.join(exampleRoot, "values.json"), "utf8"));
  const observations = [];
  async function check(id, execute) { await execute(); observations.push({ id, result: "pass" }); }

  await check("M09-contract-mapping-explicit-adapter", async () => {
    assert.deepEqual(Object.keys(api.endpointValues), ["find"]);
    assert.equal(api.endpointValues.find.result, api.publicContracts.response);
    assert.equal(api.acceptsVersion("1.0.0"), true);
    for (const version of ["1.0.1", "2.0.0", "bad"]) assert.equal(api.acceptsVersion(version), false);
    let calls = 0;
    const adapter = { async find(id) { calls++; assert.equal(id, 1n); return mapping.mappingSummary({ order: values.order, net: "93", fee: "5" }); } };
    // The consumer explicitly checks the requested version and both directions.
    const invoke = async (version, raw, supplied = adapter) => {
      if (!api.acceptsVersion(version)) throw new Error("UNSUPPORTED_INTERFACE_VERSION");
      const request = api.endpointValues.find.request.normalize(raw);
      return api.endpointValues.find.result.normalize(await supplied.find(request));
    };
    const result = await invoke("1.0.0", "1");
    assert.deepEqual(result, { id: 1n, net: 93n, fee: 5n });
    assert.equal(calls, 1);
    await assert.rejects(() => invoke("2.0.0", "1"), /UNSUPPORTED_INTERFACE_VERSION/);
    await assert.rejects(() => invoke("1.0.0", "bad"), /INTERFACE_VALUE/);
    assert.equal(calls, 1);
    await assert.rejects(() => invoke("1.0.0", "1", { async find() { return { id: "1", net: "93" }; } }), /INTERFACE_VALUE/);
    assert.equal(api.descriptor.transport_execution, "not-performed");
  });

  await check("M09-public-identity-value-object-enum-boundary", async () => {
    const input = { id: "9007199254740993", money: { quantity: "3" }, choice: { variant: "Some", payload: { quantity: "7" } } };
    const normalized = namedApi.endpointValues.find.request.normalize(input);
    assert.equal(normalized.id, 9007199254740993n);
    assert.equal(normalized.money.quantity, 3n);
    assert.equal(normalized.choice.payload.quantity, 7n);
    assert.deepEqual(Object.keys(namedApi.endpointValues), ["find"]);
    assert.equal(namedApi.acceptsVersion("1.0.0"), true); assert.equal(namedApi.acceptsVersion("1.0.1"), false);
    let calls = 0;
    const adapter = { async find(request) { calls++; return request; } };
    const output = namedApi.endpointValues.find.result.normalize(await adapter.find(normalized));
    assert.equal(calls, 1); assert.deepEqual(output, normalized);
    for (const edit of [v => v.id = "bad", v => v.money.quantity = "bad", v => v.choice.variant = "Unknown", v => delete v.choice.payload]) {
      const invalid = structuredClone(input); edit(invalid);
      assert.throws(() => namedApi.endpointValues.find.request.normalize(invalid), /INTERFACE_VALUE/);
      assert.throws(() => namedApi.endpointValues.find.result.normalize(invalid), /INTERFACE_VALUE/);
    }
    // Interface normalizers establish shape; they do not silently execute invariants.
    assert.equal(namedApi.endpointValues.find.request.normalize({ ...input, money: { quantity: "0" } }).money.quantity, 0n);
    assert.equal(namedApi.descriptor.invariant_execution, "not-performed");
  });

  await check("M10-occurrence-payload-clock-numeric-reference", () => {
    const input = structuredClone(values.events.post_first);
    input.payload["order-id"] = "9007199254740993";
    const event = posted.eventPosted(input);
    assert.equal(event.payload["order-id"], 9007199254740993n);
    assert.equal(event.payload.delta, -9223372036854775808n);
    assert.equal(event.occurredAt, input.occurredAt);
    assert.equal(event.occurrence["event-id"], input.occurrence["event-id"]);
    assert.ok(Object.isFrozen(event.payload));
    input.payload["order-id"] = "7";
    assert.equal(event.payload["order-id"], 9007199254740993n);
    assert.throws(() => posted.eventPosted({ ...values.events.post_first, payload: { "order-id": "bad" } }));
    assert.throws(() => posted.eventPosted({ ...values.events.post_first, occurrence: {} }));
    assert.throws(() => posted.eventPosted({ ...values.events.post_first, payload: { "order-id": "18446744073709551616" } }));
    assert.throws(() => posted.eventPosted({ occurrence: values.events.post_first.occurrence, payload: values.events.post_first.payload }));
    let clocks = 0;
    const generated = released.eventReleased(values.events.undo_first, () => { clocks++; return "2026-10-13T12:00:00Z"; });
    assert.equal(clocks, 1);
    assert.equal(generated.occurredAt, "2026-10-13T12:00:00Z");
    assert.throws(() => released.eventReleased(values.events.undo_first, () => 42));
    // A message identity belongs to the explicit delivery envelope, not Event construction.
    const envelopes = [{ messageId: "delivery-1", event }, { messageId: "delivery-2", event }];
    assert.notEqual(envelopes[0].messageId, envelopes[1].messageId);
    assert.equal(envelopes[0].event.occurrence, envelopes[1].event.occurrence);
    assert.equal(posted.eventPosted.descriptor.publication, false);
  });

  await check("M11-transition-guard-refusal-invalid-state-intents", () => {
    assert.equal(lifecycle.initialState, "draft");
    const outcome = lifecycle.transitionLifecycle("draft", "commerce:posted", { amount: "1" });
    assert.equal(outcome.status, "transitioned"); assert.equal(outcome.state, "posted");
    assert.deepEqual(outcome.output_intents, [{ slot: "confirmation", event_ref: "commerce:posted" }, { slot: "audit", event_ref: "commerce:posted" }]);
    assert.ok(Object.isFrozen(outcome.output_intents));
    assert.deepEqual(lifecycle.transitionLifecycle("draft", "commerce:posted", { amount: "0" }), { status: "rejected", state: "draft", reason: "guard", output_intents: [] });
    assert.equal(lifecycle.transitionLifecycle("draft", "commerce:released", { amount: "1" }).reason, "no-transition");
    assert.throws(() => lifecycle.transitionLifecycle("unknown", "commerce:posted", { amount: "1" }), /STATE_MACHINE_INPUT/);
    assert.throws(() => lifecycle.transitionLifecycle("draft", "commerce:posted", { amount: "bad" }), /STATE_MACHINE_INPUT/);
    assert.equal(lifecycle.transitionLifecycle("posted", "commerce:released", { amount: "1" }).state, "released");
  });

  const operationInput = () => ({ amount: structuredClone(values.order), notice_input: structuredClone(values.events.post_first) });
  await check("M12-operation-atomic-batch-owned-result", async () => {
    const store = atomicStore(values.before);
    const result = await perform.operationPerform(operationInput(), store.dependency);
    assert.equal(result.status, "committed"); assert.equal(result.value.id, 1n);
    assert.equal(store.state().money.quantity, 3n);
    assert.equal(store.outbox.length, 1); assert.equal(store.outbox[0].value.payload["order-id"], 1n);
    assert.deepEqual(store.trace, ["begin:0", "commit:0"]);
    assert.ok(Object.isFrozen(result.value));
    let settle;
    const settlement = new Promise(resolve => { settle = resolve; });
    const waitingStore = atomicStore(values.before, { settlement });
    const input = operationInput();
    let finished = false;
    const pending = perform.operationPerform(input, waitingStore.dependency).then(result => { finished = true; return result; });
    input.amount.money.quantity = "99";
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(finished, false, "Operation must await the supplied commit settlement");
    assert.equal(waitingStore.state().money.quantity, 3n, "Input is captured before suspension");
    settle();
    assert.equal((await pending).status, "committed");
  });
  await check("M12-input-guard-invariant-event-zero-commits", async () => {
    for (const [edit, status, stage] of [
      [v => v.amount.id = "bad", "failed", "input"],
      [v => v.amount.money.quantity = "100", "rejected", "guard"],
      [v => v.amount.money.quantity = "0", "failed", "write-validation"],
      [v => v.notice_input.payload["order-id"] = "bad", "failed", "event"],
    ]) {
      const input = operationInput(); edit(input);
      const store = atomicStore(values.before);
      const result = await perform.operationPerform(input, store.dependency);
      assert.equal(result.status, status); assert.equal(result.stage, stage);
      assert.equal(store.batches.length, 0); assert.equal(store.outbox.length, 0);
      assert.deepEqual(store.state(), values.before);
      if (stage === "input") assert.equal(store.begins(), 0);
      else assert.deepEqual(store.trace, ["begin:0", "rollback:0"]);
    }
  });
  await check("M12-rejection-failure-uncertainty-not-automatic-retry", async () => {
    for (const mode of ["reject", "throw-before", "between-state-and-outbox", "throw-after", "indeterminate"]) {
      const store = atomicStore(values.before, { failAt: 0, mode });
      const result = await perform.operationPerform(operationInput(), store.dependency);
      assert.equal(result.status, mode === "reject" ? "rejected" : "indeterminate");
      assert.equal(store.begins(), 1);
      assert.equal(store.trace.filter(v => v.startsWith("commit:")).length, 1);
      const committed = ["throw-after", "indeterminate"].includes(mode);
      assert.equal(store.outbox.length, committed ? 1 : 0);
      assert.equal(store.state().money.quantity, committed ? 3n : "1");
    }
  });

  const workflowInput = () => ({ ...structuredClone(values.workflow.inputs), ...structuredClone(values.workflow.event_inputs) });
  const identity = { workflow_execution_id: "meta-types-execution", failure_occurrence_id: "meta-types-failure" };
  await check("M13-distinct-previous-results-and-mapping-adaptation", () => {
    const input = workflowInput();
    input.amount = inboundMapping.mappingInboundRequest({ amount: input.amount });
    const captured = material.capture(input);
    const first = material.captureResult(captured, "first", { ...values.order, id: "61" });
    assert.equal(material.steps.second.arguments(captured, [first]).amount.id, 61n);
    const second = material.captureResult(captured, "second", { ...values.order, id: "62" });
    assert.equal(material.steps.third.arguments(captured, [first, second]).amount.id, 62n);
    assert.equal(captured.amount.id, 1n);
    assert.throws(() => material.steps.third.arguments(captured, [second, first]), /WORKFLOW_VALUE/);
    assert.throws(() => material.steps.second.arguments(captured, []), /WORKFLOW_VALUE/);
    assert.equal(material.compensations["undo-first"].arguments(captured, [first]).amount.money.quantity, 1n);
  });
  await check("M13-ordered-materialization-numeric-events", async () => {
    const store = atomicStore(values.before);
    const input = workflowInput();
    input.amount = inboundMapping.mappingInboundRequest({ amount: input.amount });
    const result = await flow.workflowFlow(input, identity, { "commerce:perform": store.dependency });
    assert.equal(result.status, "succeeded"); assert.equal(result.value.id, 1n);
    assert.deepEqual(store.trace, ["begin:0", "commit:0", "begin:1", "commit:1", "begin:2", "commit:2", "begin:3", "commit:3"]);
    assert.equal(store.outbox.length, 4);
    assert.deepEqual(store.outbox.map(e => e.value.payload["order-id"]), [1n, 1n, 1n, 1n]);
    assert.equal(new Set(store.outbox.map(e => e.value.occurrence["event-id"])).size, 4);
    assert.equal(result.recovery_bindings, null);
    assert.deepEqual(mapping.mappingSummary({ order: result.value, net: "93", fee: "5" }), { id: 1n, net: 93n, fee: 5n });
  });
  await check("M13-every-failure-prefix-selected-compensation", async () => {
    const expected = [[], ["undo-first"], ["undo-second", "undo-first"], ["undo-third", "undo-second", "undo-first"]];
    for (let failAt = 0; failAt < 4; failAt++) {
      const store = atomicStore(values.before, { failAt });
      const result = await flow.workflowFlow(workflowInput(), identity, { "commerce:perform": store.dependency });
      assert.equal(result.status, "forward-stopped"); assert.equal(store.begins(), failAt + 1); assert.equal(store.outbox.length, failAt);
      const bindings = result.recovery_bindings?.bindings ?? [];
      assert.deepEqual(bindings.map(b => b.compensation_id), expected[failAt]);
      // Generated Workflow returns intent; the consumer explicitly chooses to execute it.
      const compensation = atomicStore(store.state());
      const dependency = { ...compensation.dependency, clocks: { notice: () => "2026-10-13T12:00:00Z" } };
      for (const binding of bindings) {
        assert.equal(binding.arguments.amount.money.quantity, 1n);
        const undone = await undo.operationUndo(binding.arguments, dependency);
        assert.equal(undone.status, "committed");
      }
      assert.equal(compensation.begins(), failAt);
      if (failAt) assert.equal(compensation.state().money.quantity, 1n);
    }
  });
  await check("M13-uncertain-commit-requires-reconciliation", async () => {
    for (let failAt = 0; failAt < 4; failAt++) for (const mode of ["throw-before", "throw-after"]) {
      const store = atomicStore(values.before, { failAt, mode });
      const result = await flow.workflowFlow(workflowInput(), identity, { "commerce:perform": store.dependency });
      assert.equal(result.evaluation.recovery_status, "reconciliation-required");
      assert.equal(result.recovery_bindings, null);
      assert.equal(store.begins(), failAt + 1);
      assert.equal(store.outbox.length, failAt + (mode === "throw-after" ? 1 : 0));
    }
  });
  return { group: "behavior", result: "pass", observations, meta_types: ["Interface", "Event", "State Machine", "Operation", "Workflow"], provider: "explicit consumer in-memory atomic state/outbox", durable_runtime_claim: false };
}
