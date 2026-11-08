import { CompilationRejected, type NormalizedDomain, type NormalizedEffect } from "./model.js";
import type { ActionAdapter, AdapterRequest, AdapterResult } from "./runtime.js";
import { DurableSqliteTransactionalOutbox, type DurableCommitRequest } from "./durable-outbox-runtime.js";

function reject(code: string, path: string, message: string): never {
  throw new CompilationRejected([{ code, path, message }]);
}

export function resolveSqliteTransactionalOutboxEffect(model: NormalizedDomain, actionId: string, bindingId: string): NormalizedEffect {
  const action = model.actions.find((item) => item.id === actionId);
  if (!action) reject("ACTION_NOT_FOUND", "$.action_id", `${actionId} is not declared`);
  const matching = action.performs.filter((item) => item.integration_binding_ref === bindingId);
  if (matching.length === 0) reject("EFFECT_BINDING_NOT_DECLARED", `$.actions.${actionId}.performs`, `${bindingId} is not declared by ${actionId}`);
  if (matching.length > 1) reject("EFFECT_BINDING_AMBIGUOUS", `$.actions.${actionId}.performs`, `${bindingId} resolves to more than one effect`);
  const performs = matching[0];
  const effect = model.effects.find((item) => item.id === performs.effect_ref);
  if (!effect) reject("EFFECT_NOT_FOUND", `$.actions.${actionId}.performs`, `${performs.effect_ref} is not declared`);
  if (effect.integration_binding_ref !== bindingId) reject("EFFECT_BINDING_MISMATCH", `$.effects.${effect.id}`, `${effect.integration_binding_ref} does not match ${bindingId}`);
  if (effect.pattern_ref !== "transactional-outbox") reject("EFFECT_PATTERN_MISMATCH", `$.effects.${effect.id}`, `${effect.pattern_ref} is not transactional-outbox`);
  if (bindingId !== "sqlite-transactional-outbox") reject("EFFECT_PROVIDER_UNSUPPORTED", `$.effects.${effect.id}`, `${bindingId} has no local runtime provider`);
  if (effect.guarantee !== "atomic-state-and-outbox") reject("EFFECT_GUARANTEE_MISMATCH", `$.effects.${effect.id}`, `${effect.guarantee} is not supported`);
  if (effect.failure_continuation !== "rollback") reject("EFFECT_FAILURE_CONTINUATION_MISMATCH", `$.effects.${effect.id}`, `${effect.failure_continuation} is not supported`);
  if (effect.authority_boundary_ref !== action.authority_boundary_ref) reject("EFFECT_AUTHORITY_BOUNDARY_MISMATCH", `$.effects.${effect.id}`, "action and effect authority boundaries differ");
  return effect;
}

export class SqliteTransactionalOutboxActionAdapter implements ActionAdapter, Disposable {
  private constructor(
    private readonly effect: NormalizedEffect,
    private readonly request: DurableCommitRequest,
    readonly outbox: DurableSqliteTransactionalOutbox,
    private readonly failpoint?: "after-state-write"
  ) {}

  static open(input: { model: NormalizedDomain; actionId: string; bindingId: string; databasePath: string; effectRequest: DurableCommitRequest; failpoint?: "after-state-write" }): SqliteTransactionalOutboxActionAdapter {
    const effect = resolveSqliteTransactionalOutboxEffect(input.model, input.actionId, input.bindingId);
    if (!effect.write_refs.includes(input.effectRequest.aggregateType)) reject("EFFECT_AGGREGATE_NOT_DECLARED", `$.effects.${effect.id}.writes`, `${input.effectRequest.aggregateType} is not a declared write`);
    for (const message of input.effectRequest.messages) {
      if (!effect.event_refs.includes(message.eventType)) reject("EFFECT_EVENT_NOT_DECLARED", `$.effects.${effect.id}.emits`, `${message.eventType} is not a declared effect event`);
    }
    return new SqliteTransactionalOutboxActionAdapter(effect, structuredClone(input.effectRequest), new DurableSqliteTransactionalOutbox(input.databasePath), input.failpoint);
  }

  async execute(request: AdapterRequest): Promise<AdapterResult> {
    if (request.authority_boundary_ref !== this.effect.authority_boundary_ref) reject("EFFECT_AUTHORITY_BOUNDARY_MISMATCH", "$.adapter", "runtime request and effect authority boundaries differ");
    const commit = this.outbox.commit(this.request, this.failpoint);
    return {
      outcome: "committed-with-outbox",
      emitted_events: this.request.messages.map((message) => message.eventType),
      data: {
        effect_id: this.effect.id,
        integration_binding_ref: this.effect.integration_binding_ref,
        aggregate_type: this.request.aggregateType,
        aggregate_id: this.request.aggregateId,
        version: this.request.expectedVersion + 1,
        commit_status: commit.status,
        message_ids: this.request.messages.map((message) => message.messageId)
      }
    };
  }

  close(): void { this.outbox.close(); }
  [Symbol.dispose](): void { this.close(); }
}
