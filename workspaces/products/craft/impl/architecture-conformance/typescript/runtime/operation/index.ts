import { createHash } from "node:crypto";

import ts from "typescript";

import type { OperationObservationV1 } from "../../../families/state-change/contracts/operation-contracts.js";

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");

export const observeTypeScriptOperation = async (input: Readonly<{
  source: string;
  bindingId: string;
  bindingSourceSha256: string;
  symbolName: string;
  mutationId: string | null;
  requestId: string;
  amount: number;
}>): Promise<OperationObservationV1> => {
  const compiled = ts.transpileModule(input.source, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ES2022,
      strict: true,
    },
    reportDiagnostics: true,
  });
  if ((compiled.diagnostics ?? []).length > 0) {
    throw Object.assign(new Error("TS_OPERATION_COMPILE_FAILED"), {
      code: "TS_OPERATION_COMPILE_FAILED",
    });
  }
  const module = await import(`data:text/javascript;base64,${Buffer.from(
    compiled.outputText, "utf8",
  ).toString("base64")}`) as Record<string, unknown>;
  const callable = module[input.symbolName];
  if (typeof callable !== "function") {
    throw Object.assign(new Error("TS_OPERATION_EXPORT_MISSING"), {
      code: "TS_OPERATION_EXPORT_MISSING",
    });
  }
  const trace: string[] = [];
  const payouts: string[] = [];
  const events: string[] = [];
  const state = {
    payouts: new Proxy(payouts, {
      get(target, property, receiver) {
        if (property === "push") return (...items: string[]) => {
          trace.push("payout-write");
          return target.push(...items);
        };
        return Reflect.get(target, property, receiver);
      },
    }),
    events: new Proxy(events, {
      get(target, property, receiver) {
        if (property === "push") return (...items: string[]) => {
          trace.push("payout-created-event");
          return target.push(...items);
        };
        return Reflect.get(target, property, receiver);
      },
    }),
  };
  callable(state, { requestId: input.requestId, amount: input.amount });
  return Object.freeze({
    schema_version: "OperationObservation/v1" as const,
    binding_id: input.bindingId,
    binding_source_sha256: input.bindingSourceSha256,
    execution_source_sha256: sha256(input.source),
    mutation_id: input.mutationId,
    payout_ids: Object.freeze([...payouts]),
    events: Object.freeze([...events]),
    trace: Object.freeze(trace),
    authority_effect: "none" as const,
  });
};
