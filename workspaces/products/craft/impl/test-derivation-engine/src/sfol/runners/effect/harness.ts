import {
  EFFECT_TRACE_VERSION,
  validateEffectTrace,
  type EffectKind,
  type EffectTraceContract,
  type EffectTraceDiagnostic,
  type ValidatedEffectTrace,
} from "./contracts.js";
import type { SemanticValue } from "../../evaluator/index.js";

export const EFFECT_HARNESS_ADAPTER_VERSION =
  "domainspec-sfol-effect-harness-adapter/v1" as const;

export interface EffectHarnessPolicy {
  readonly timeout_ms: number;
  readonly max_open_resources: number;
}

export interface EffectHarnessRuntime {
  readonly signal: AbortSignal;
  openResource(resourceId: string): void;
  closeResource(resourceId: string): void;
  recordEffect(
    kind: EffectKind,
    name: string,
    payload: SemanticValue,
  ): void;
}

export interface EffectHarnessAdapter<Resource> {
  readonly schema_version: typeof EFFECT_HARNESS_ADAPTER_VERSION;
  readonly adapter_id: string;
  readonly adapter_digest: string;
  readonly contract_id: string;
  setup(runtime: EffectHarnessRuntime): Promise<Resource>;
  capturePreState(resource: Resource): Promise<unknown>;
  run(
    resource: Resource,
    runtime: EffectHarnessRuntime,
  ): Promise<unknown>;
  capturePostState(resource: Resource): Promise<unknown>;
  teardown(
    resource: Resource,
    runtime: EffectHarnessRuntime,
  ): Promise<void>;
}

export type EffectHarnessDiagnosticCode =
  | "SFOL_HARNESS_ADAPTER_INVALID"
  | "SFOL_HARNESS_SETUP_FAILED"
  | "SFOL_HARNESS_CAPTURE_FAILED"
  | "SFOL_HARNESS_RUN_FAILED"
  | "SFOL_HARNESS_PARTIAL_TRACE"
  | "SFOL_HARNESS_TIMEOUT"
  | "SFOL_HARNESS_UNDECLARED_EFFECT"
  | "SFOL_HARNESS_RESOURCE_LIMIT"
  | "SFOL_HARNESS_TEARDOWN_FAILED"
  | "SFOL_HARNESS_RESOURCE_LEAK"
  | "SFOL_HARNESS_TRACE_INVALID";

export interface EffectHarnessDiagnostic {
  readonly code: EffectHarnessDiagnosticCode;
  readonly stage: "effect-harness";
  readonly phase: HarnessPhase;
  readonly detail: string;
  readonly trace_diagnostics?: readonly EffectTraceDiagnostic[];
}

export interface EffectHarnessContainment {
  readonly setup_completed: boolean;
  readonly teardown_attempted: boolean;
  readonly teardown_completed: boolean;
  readonly open_resources: readonly string[];
  readonly recorded_effects: number;
  readonly timed_out: boolean;
}

export type EffectHarnessRunResult =
  | {
      readonly ok: true;
      readonly trace: ValidatedEffectTrace;
      readonly containment: EffectHarnessContainment;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly EffectHarnessDiagnostic[];
      readonly containment: EffectHarnessContainment;
    };

type HarnessPhase =
  | "preflight"
  | "setup"
  | "capture-pre"
  | "run"
  | "capture-post"
  | "teardown"
  | "closed";

class HarnessAbort extends Error {
  readonly diagnostic: EffectHarnessDiagnostic;

  constructor(diagnostic: EffectHarnessDiagnostic) {
    super(`${diagnostic.code}: ${diagnostic.detail}`);
    this.name = "HarnessAbort";
    this.diagnostic = diagnostic;
  }
}

export async function runEffectHarness<Resource>(
  caseId: string,
  contract: EffectTraceContract,
  adapter: EffectHarnessAdapter<Resource>,
  policy: EffectHarnessPolicy,
): Promise<EffectHarnessRunResult> {
  const controller = new AbortController();
  const state = {
    phase: "preflight" as HarnessPhase,
    setupCompleted: false,
    teardownAttempted: false,
    teardownCompleted: false,
    timedOut: false,
    resources: new Set<string>(),
    effects: [] as Array<{
      sequence: number;
      kind: EffectKind;
      name: string;
      payload: SemanticValue;
    }>,
  };
  const diagnostics: EffectHarnessDiagnostic[] = [];
  let resource!: Resource;
  let preState: unknown;
  let postState: unknown;
  let returnValue: unknown;

  const runtime: EffectHarnessRuntime = Object.freeze({
    signal: controller.signal,
    openResource(resourceId: string): void {
      requireRuntimeResourceId(resourceId, state.phase);
      if (state.phase === "teardown" || state.phase === "closed") {
        harnessFail(
          "SFOL_HARNESS_RESOURCE_LIMIT",
          state.phase,
          "resources cannot be opened during or after teardown",
        );
      }
      if (state.resources.has(resourceId)) {
        harnessFail(
          "SFOL_HARNESS_RESOURCE_LIMIT",
          state.phase,
          `resource ${resourceId} is already open`,
        );
      }
      if (state.resources.size >= policy.max_open_resources) {
        harnessFail(
          "SFOL_HARNESS_RESOURCE_LIMIT",
          state.phase,
          `maximum open resources is ${policy.max_open_resources}`,
        );
      }
      state.resources.add(resourceId);
    },
    closeResource(resourceId: string): void {
      requireRuntimeResourceId(resourceId, state.phase);
      if (!state.resources.delete(resourceId)) {
        harnessFail(
          "SFOL_HARNESS_RESOURCE_LIMIT",
          state.phase,
          `resource ${resourceId} is not open`,
        );
      }
    },
    recordEffect(
      kind: EffectKind,
      name: string,
      payload: SemanticValue,
    ): void {
      if (state.phase !== "run") {
        harnessFail(
          "SFOL_HARNESS_UNDECLARED_EFFECT",
          state.phase,
          "effects may be recorded only during run",
        );
      }
      const sequence = state.effects.length;
      const slot = contract.effect_sequence[sequence];
      if (
        slot === undefined ||
        slot.kind !== kind ||
        slot.name !== name ||
        slot.payload_tag !== payload.tag
      ) {
        harnessFail(
          "SFOL_HARNESS_UNDECLARED_EFFECT",
          state.phase,
          `effect ${sequence} is not the declared ${slot?.kind ?? "<none>"}:${slot?.name ?? "<none>"}:${slot?.payload_tag ?? "<none>"}`,
        );
      }
      state.effects.push(
        Object.freeze({ sequence, kind, name, payload }),
      );
    },
  });

  try {
    validatePreflight(caseId, contract, adapter, policy);
    state.phase = "setup";
    resource = await adapter.setup(runtime);
    state.setupCompleted = true;

    state.phase = "capture-pre";
    preState = await adapter.capturePreState(resource);

    state.phase = "run";
    returnValue = await runWithTimeout(
      adapter.run(resource, runtime),
      policy.timeout_ms,
      controller,
      () => {
        state.timedOut = true;
      },
    );

    state.phase = "capture-post";
    postState = await adapter.capturePostState(resource);
  } catch (error: unknown) {
    diagnostics.push(
      normalizePrimaryFailure(error, state.phase, state.effects.length),
    );
  } finally {
    if (state.setupCompleted) {
      state.phase = "teardown";
      state.teardownAttempted = true;
      try {
        await adapter.teardown(resource, runtime);
        state.teardownCompleted = true;
      } catch (error: unknown) {
        diagnostics.push(
          diagnostic(
            "SFOL_HARNESS_TEARDOWN_FAILED",
            "teardown",
            errorDetail(error, "teardown failed"),
          ),
        );
      }
    }
    state.phase = "closed";
  }

  if (state.resources.size > 0) {
    diagnostics.push(
      diagnostic(
        "SFOL_HARNESS_RESOURCE_LEAK",
        "closed",
        `open resource(s): ${[...state.resources].sort().join(", ")}`,
      ),
    );
  }

  const containment = freezeContainment(state);
  if (diagnostics.length > 0) {
    return failedResult(diagnostics, containment);
  }

  const traceResult = validateEffectTrace(contract, {
    schema_version: EFFECT_TRACE_VERSION,
    trace_id: `${caseId}:${adapter.adapter_id}`,
    contract_id: contract.contract_id,
    pre_state: preState,
    post_state: postState,
    effects: state.effects,
    return_value: returnValue,
  });
  if (!traceResult.ok) {
    return failedResult(
      [
        diagnostic(
          "SFOL_HARNESS_TRACE_INVALID",
          "closed",
          "captured trace does not satisfy its declared observation contract",
          traceResult.diagnostics,
        ),
      ],
      containment,
    );
  }

  return Object.freeze({
    ok: true,
    trace: traceResult.value,
    containment,
  });
}

function validatePreflight<Resource>(
  caseId: string,
  contract: EffectTraceContract,
  adapter: EffectHarnessAdapter<Resource>,
  policy: EffectHarnessPolicy,
): void {
  for (const [name, value] of [
    ["caseId", caseId],
    ["adapter.adapter_id", adapter.adapter_id],
    ["adapter.adapter_digest", adapter.adapter_digest],
  ] as const) {
    if (typeof value !== "string" || value.length === 0) {
      harnessFail(
        "SFOL_HARNESS_ADAPTER_INVALID",
        "preflight",
        `${name} must be a non-empty string`,
      );
    }
  }
  if (adapter.schema_version !== EFFECT_HARNESS_ADAPTER_VERSION) {
    harnessFail(
      "SFOL_HARNESS_ADAPTER_INVALID",
      "preflight",
      `unsupported adapter version ${String(adapter.schema_version)}`,
    );
  }
  if (adapter.contract_id !== contract.contract_id) {
    harnessFail(
      "SFOL_HARNESS_ADAPTER_INVALID",
      "preflight",
      `adapter contract ${adapter.contract_id} does not match ${contract.contract_id}`,
    );
  }
  if (!Number.isSafeInteger(policy.timeout_ms) || policy.timeout_ms <= 0) {
    harnessFail(
      "SFOL_HARNESS_ADAPTER_INVALID",
      "preflight",
      "timeout_ms must be a positive safe integer",
    );
  }
  if (
    !Number.isSafeInteger(policy.max_open_resources) ||
    policy.max_open_resources < 0
  ) {
    harnessFail(
      "SFOL_HARNESS_ADAPTER_INVALID",
      "preflight",
      "max_open_resources must be a non-negative safe integer",
    );
  }
}

async function runWithTimeout<T>(
  operation: Promise<T>,
  timeoutMs: number,
  controller: AbortController,
  onTimeout: () => void,
): Promise<T> {
  let timer: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<never>((_resolve, reject) => {
    timer = setTimeout(() => {
      onTimeout();
      controller.abort();
      reject(
        new HarnessAbort(
          diagnostic(
            "SFOL_HARNESS_TIMEOUT",
            "run",
            `run exceeded ${timeoutMs}ms`,
          ),
        ),
      );
    }, timeoutMs);
  });
  try {
    return await Promise.race([operation, timeout]);
  } finally {
    if (timer !== undefined) {
      clearTimeout(timer);
    }
  }
}

function normalizePrimaryFailure(
  error: unknown,
  phase: HarnessPhase,
  effectCount: number,
): EffectHarnessDiagnostic {
  if (error instanceof HarnessAbort) {
    return error.diagnostic;
  }
  if (phase === "setup") {
    return diagnostic(
      "SFOL_HARNESS_SETUP_FAILED",
      phase,
      errorDetail(error, "setup failed"),
    );
  }
  if (phase === "capture-pre" || phase === "capture-post") {
    return diagnostic(
      "SFOL_HARNESS_CAPTURE_FAILED",
      phase,
      errorDetail(error, "state capture failed"),
    );
  }
  if (phase === "run") {
    return diagnostic(
      effectCount > 0
        ? "SFOL_HARNESS_PARTIAL_TRACE"
        : "SFOL_HARNESS_RUN_FAILED",
      phase,
      errorDetail(error, "run failed"),
    );
  }
  return diagnostic(
    "SFOL_HARNESS_ADAPTER_INVALID",
    phase,
    errorDetail(error, "harness failed"),
  );
}

function freezeContainment(state: {
  readonly setupCompleted: boolean;
  readonly teardownAttempted: boolean;
  readonly teardownCompleted: boolean;
  readonly resources: ReadonlySet<string>;
  readonly effects: readonly unknown[];
  readonly timedOut: boolean;
}): EffectHarnessContainment {
  return Object.freeze({
    setup_completed: state.setupCompleted,
    teardown_attempted: state.teardownAttempted,
    teardown_completed: state.teardownCompleted,
    open_resources: Object.freeze([...state.resources].sort()),
    recorded_effects: state.effects.length,
    timed_out: state.timedOut,
  });
}

function failedResult(
  diagnostics: readonly EffectHarnessDiagnostic[],
  containment: EffectHarnessContainment,
): EffectHarnessRunResult {
  return Object.freeze({
    ok: false,
    diagnostics: Object.freeze(
      diagnostics.map((item) => Object.freeze(item)),
    ),
    containment,
  });
}

function requireRuntimeResourceId(
  resourceId: string,
  phase: HarnessPhase,
): void {
  if (typeof resourceId !== "string" || resourceId.length === 0) {
    harnessFail(
      "SFOL_HARNESS_RESOURCE_LIMIT",
      phase,
      "resource ID must be a non-empty string",
    );
  }
}

function errorDetail(error: unknown, fallback: string): string {
  return error instanceof Error && error.message.length > 0
    ? error.message
    : fallback;
}

function diagnostic(
  code: EffectHarnessDiagnosticCode,
  phase: HarnessPhase,
  detail: string,
  traceDiagnostics?: readonly EffectTraceDiagnostic[],
): EffectHarnessDiagnostic {
  return traceDiagnostics === undefined
    ? { code, stage: "effect-harness", phase, detail }
    : {
        code,
        stage: "effect-harness",
        phase,
        detail,
        trace_diagnostics: Object.freeze([...traceDiagnostics]),
      };
}

function harnessFail(
  code: EffectHarnessDiagnosticCode,
  phase: HarnessPhase,
  detail: string,
): never {
  throw new HarnessAbort(diagnostic(code, phase, detail));
}
