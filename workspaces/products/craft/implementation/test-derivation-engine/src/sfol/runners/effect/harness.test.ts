import { describe, expect, it } from "vitest";

import { integerValue, type SemanticValue } from "../../evaluator/index.js";
import {
  EFFECT_TRACE_CONTRACT_VERSION,
  type EffectTraceContract,
} from "./contracts.js";
import {
  EFFECT_HARNESS_ADAPTER_VERSION,
  runEffectHarness,
  type EffectHarnessAdapter,
  type EffectHarnessRuntime,
} from "./harness.js";

interface CounterResource {
  balance: string;
}

const policy = Object.freeze({
  timeout_ms: 30,
  max_open_resources: 1,
});

function contractFixture(): EffectTraceContract {
  return {
    schema_version: EFFECT_TRACE_CONTRACT_VERSION,
    contract_id: "framework.counter-effects",
    pre_record_declaration_id: "framework.State",
    post_record_declaration_id: "framework.State",
    effect_record_declaration_id: "framework.Effect",
    pre_fields: [{ name: "balance", value_tag: "integer" }],
    post_fields: [{ name: "balance", value_tag: "integer" }],
    effect_sequence: [
      { kind: "call", name: "authorize", payload_tag: "string" },
      { kind: "write", name: "balance", payload_tag: "integer" },
      { kind: "event", name: "incremented", payload_tag: "integer" },
      { kind: "error", name: "none", payload_tag: "string" },
    ],
    return_observation: { value_tag: "integer" },
    max_effects: 4,
  };
}

function referenceAdapter(
  changes: Partial<EffectHarnessAdapter<CounterResource>> = {},
): EffectHarnessAdapter<CounterResource> {
  return {
    schema_version: EFFECT_HARNESS_ADAPTER_VERSION,
    adapter_id: "framework.counter-reference",
    adapter_digest: "sha256:counter-reference-v1",
    contract_id: "framework.counter-effects",
    async setup(runtime) {
      runtime.openResource("counter-db");
      return { balance: "0" };
    },
    async capturePreState(resource) {
      return { balance: integerValue(resource.balance) };
    },
    async run(resource, runtime) {
      runtime.recordEffect("call", "authorize", stringValue("ok"));
      resource.balance = "1";
      runtime.recordEffect("write", "balance", integerValue("1"));
      runtime.recordEffect("event", "incremented", integerValue("1"));
      runtime.recordEffect("error", "none", stringValue("none"));
      return integerValue(resource.balance);
    },
    async capturePostState(resource) {
      return { balance: integerValue(resource.balance) };
    },
    async teardown(_resource, runtime) {
      runtime.closeResource("counter-db");
    },
    ...changes,
  };
}

describe("DS-SFOL contained effect harness", () => {
  it("completes setup, capture, run, capture, validation, and teardown deterministically", async () => {
    const left = await runEffectHarness(
      "case-counter-001",
      contractFixture(),
      referenceAdapter(),
      policy,
    );
    const right = await runEffectHarness(
      "case-counter-001",
      contractFixture(),
      referenceAdapter(),
      policy,
    );

    expect(left).toMatchObject({
      ok: true,
      containment: {
        setup_completed: true,
        teardown_attempted: true,
        teardown_completed: true,
        open_resources: [],
        recorded_effects: 4,
        timed_out: false,
      },
    });
    expect(right.ok && left.ok && right.trace.trace_digest).toBe(
      left.ok ? left.trace.trace_digest : "",
    );
  });

  it("reports setup failure without pretending teardown was possible", async () => {
    const result = await runEffectHarness(
      "case-counter-setup",
      contractFixture(),
      referenceAdapter({
        async setup() {
          throw new Error("setup unavailable");
        },
      }),
      policy,
    );

    expect(result).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_HARNESS_SETUP_FAILED", phase: "setup" }],
      containment: {
        setup_completed: false,
        teardown_attempted: false,
      },
    });
  });

  it("always attempts teardown after a partial run failure", async () => {
    let tornDown = false;
    const result = await runEffectHarness(
      "case-counter-partial",
      contractFixture(),
      referenceAdapter({
        async run(_resource, runtime) {
          runtime.recordEffect("call", "authorize", stringValue("ok"));
          throw new Error("target crashed");
        },
        async teardown(_resource, runtime) {
          tornDown = true;
          runtime.closeResource("counter-db");
        },
      }),
      policy,
    );

    expect(tornDown).toBe(true);
    expect(result).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_HARNESS_PARTIAL_TRACE", phase: "run" }],
      containment: {
        teardown_attempted: true,
        teardown_completed: true,
        recorded_effects: 1,
      },
    });
  });

  it("reports incomplete teardown independently", async () => {
    const result = await runEffectHarness(
      "case-counter-teardown",
      contractFixture(),
      referenceAdapter({
        async teardown(_resource, runtime) {
          runtime.closeResource("counter-db");
          throw new Error("teardown receipt missing");
        },
      }),
      policy,
    );

    expect(result).toMatchObject({
      ok: false,
      diagnostics: [
        { code: "SFOL_HARNESS_TEARDOWN_FAILED", phase: "teardown" },
      ],
      containment: {
        teardown_attempted: true,
        teardown_completed: false,
        open_resources: [],
      },
    });
  });

  it("detects resources left open after teardown", async () => {
    const result = await runEffectHarness(
      "case-counter-leak",
      contractFixture(),
      referenceAdapter({
        async teardown() {},
      }),
      policy,
    );

    expect(result).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_HARNESS_RESOURCE_LEAK" }],
      containment: {
        teardown_attempted: true,
        teardown_completed: true,
        open_resources: ["counter-db"],
      },
    });
  });

  it("rejects an undeclared effect before a trace can be accepted", async () => {
    const result = await runEffectHarness(
      "case-counter-undeclared",
      contractFixture(),
      referenceAdapter({
        async run(_resource, runtime) {
          runtime.recordEffect("event", "surprise", stringValue("bad"));
          return integerValue("0");
        },
      }),
      policy,
    );

    expect(result).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_HARNESS_UNDECLARED_EFFECT" }],
      containment: { teardown_completed: true, recorded_effects: 0 },
    });
  });

  it("aborts a cooperative run at the finite timeout and tears down", async () => {
    const result = await runEffectHarness(
      "case-counter-timeout",
      contractFixture(),
      referenceAdapter({
        async run(_resource, runtime) {
          await waitForAbort(runtime);
          return integerValue("0");
        },
      }),
      { ...policy, timeout_ms: 5 },
    );

    expect(result).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_HARNESS_TIMEOUT", phase: "run" }],
      containment: {
        timed_out: true,
        teardown_attempted: true,
        teardown_completed: true,
      },
    });
  });

  it("rejects an incomplete captured trace after successful containment", async () => {
    const result = await runEffectHarness(
      "case-counter-incomplete",
      contractFixture(),
      referenceAdapter({
        async run(resource, runtime) {
          runtime.recordEffect("call", "authorize", stringValue("ok"));
          resource.balance = "1";
          return integerValue("1");
        },
      }),
      policy,
    );

    expect(result).toMatchObject({
      ok: false,
      diagnostics: [
        {
          code: "SFOL_HARNESS_TRACE_INVALID",
          trace_diagnostics: [
            { code: "SFOL_EFFECT_MISSING_OBSERVATION" },
          ],
        },
      ],
      containment: {
        teardown_completed: true,
        recorded_effects: 1,
      },
    });
  });

  it("enforces the harness-owned finite resource ceiling", async () => {
    const result = await runEffectHarness(
      "case-counter-resource-limit",
      contractFixture(),
      referenceAdapter({
        async setup(runtime) {
          runtime.openResource("counter-db");
          runtime.openResource("network");
          return { balance: "0" };
        },
      }),
      policy,
    );

    expect(result).toMatchObject({
      ok: false,
      diagnostics: [
        { code: "SFOL_HARNESS_RESOURCE_LIMIT" },
        { code: "SFOL_HARNESS_RESOURCE_LEAK" },
      ],
      containment: {
        setup_completed: false,
        teardown_attempted: false,
        open_resources: ["counter-db"],
      },
    });
  });

  it("keeps raw harness adapters free of evaluator callbacks and expected values", () => {
    const adapter = referenceAdapter();
    expect(Object.keys(adapter).sort()).toEqual([
      "adapter_digest",
      "adapter_id",
      "capturePostState",
      "capturePreState",
      "contract_id",
      "run",
      "schema_version",
      "setup",
      "teardown",
    ]);
  });
});

function stringValue(value: string): SemanticValue {
  return Object.freeze({ tag: "string", value });
}

function waitForAbort(runtime: EffectHarnessRuntime): Promise<void> {
  return new Promise((resolve) => {
    if (runtime.signal.aborted) {
      resolve();
      return;
    }
    runtime.signal.addEventListener("abort", () => resolve(), {
      once: true,
    });
  });
}
