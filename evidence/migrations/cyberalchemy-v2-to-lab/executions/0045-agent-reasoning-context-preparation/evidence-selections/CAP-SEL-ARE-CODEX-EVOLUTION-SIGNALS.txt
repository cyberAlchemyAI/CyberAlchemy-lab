import {createImprovementSignal} from "../../evolution-runtime/index.mjs";
import {freezeResult, isRecord, nonEmptyString} from "./canonical.mjs";

export const CODEX_EVOLUTION_SIGNAL_EMISSION_SCHEMA = "are.codex-evolution-signal-emission/v1";

function summary(fields) {
  return freezeResult({schema_version: CODEX_EVOLUTION_SIGNAL_EMISSION_SCHEMA, ...fields, authority_effect: "none"});
}
export async function emitCompletionImprovementSignals(input) {
  const configuration = isRecord(input?.configuration) ? input.configuration : {enabled: false, trigger: "turn/completed"};
  if (configuration.enabled !== true) return summary({disposition: "disabled", provider_calls: 0, sink_calls: 0, signal_count: 0, signal_refs: [], reason_codes: []});
  if (configuration.trigger !== "turn/completed") return summary({disposition: "blocked", provider_calls: 0, sink_calls: 0, signal_count: 0, signal_refs: [], reason_codes: ["evolution.signal-trigger-unsupported"]});
  if (!nonEmptyString(input.completion_digest)) return summary({disposition: "blocked", provider_calls: 0, sink_calls: 0, signal_count: 0, signal_refs: [], reason_codes: ["evolution.completion-digest-required"]});
  if (typeof input.signal_provider !== "function") return summary({disposition: "no-provider", provider_calls: 0, sink_calls: 0, signal_count: 0, signal_refs: [], reason_codes: []});

  let candidates;
  try {
    candidates = await input.signal_provider(freezeResult({
      completion_message: input.completion_message,
      completion_digest: input.completion_digest,
      turn_state: input.turn_state ?? null,
      semantic_completion: input.semantic_completion ?? null,
      continuation_result: input.continuation_result ?? null,
      authority_effect: "none",
    }));
  } catch {
    return summary({disposition: "provider-failed", provider_calls: 1, sink_calls: 0, signal_count: 0, signal_refs: [], reason_codes: ["evolution.signal-provider-failed"]});
  }
  if (!Array.isArray(candidates)) return summary({disposition: "provider-failed", provider_calls: 1, sink_calls: 0, signal_count: 0, signal_refs: [], reason_codes: ["evolution.signal-provider-result-invalid"]});
  const provenance = [
    `codex-completion:${input.completion_digest}`,
    input.turn_state?.context_envelope_digest ? `context-envelope:${input.turn_state.context_envelope_digest}` : null,
    input.semantic_completion?.reasoning_receipt_digest ? `reasoning-receipt:${input.semantic_completion.reasoning_receipt_digest}` : null,
    input.continuation_result?.value?.decision_digest ? `continuation-decision:${input.continuation_result.value.decision_digest}` : null,
  ].filter(Boolean);
  let signals;
  try {
    signals = candidates.map((candidate) => createImprovementSignal({
      ...candidate,
      source_result_ref: `codex-turn-completed:${input.completion_digest}`,
      provenance_refs: [...(candidate.provenance_refs ?? []), ...provenance],
    }));
  } catch {
    return summary({disposition: "provider-failed", provider_calls: 1, sink_calls: 0, signal_count: 0, signal_refs: [], reason_codes: ["evolution.signal-candidate-invalid"]});
  }
  signals = [...new Map(signals.map((signal) => [signal.record_id, signal])).values()].sort((a, b) => a.record_id.localeCompare(b.record_id));
  if (signals.length === 0) return summary({disposition: "no-signals", provider_calls: 1, sink_calls: 0, signal_count: 0, signal_refs: [], reason_codes: []});
  if (typeof input.signal_sink !== "function") return summary({disposition: "no-sink", provider_calls: 1, sink_calls: 0, signal_count: signals.length, signal_refs: signals.map((signal) => signal.record_id), reason_codes: ["evolution.signal-sink-missing"]});
  let sinkCalls = 0;
  try {
    for (const signal of signals) {
      sinkCalls += 1;
      const result = await input.signal_sink(signal);
      if (result?.ok === false) throw new Error("signal sink rejected record");
    }
  } catch {
    return summary({disposition: "sink-failed", provider_calls: 1, sink_calls: sinkCalls, signal_count: signals.length, signal_refs: signals.map((signal) => signal.record_id), reason_codes: ["evolution.signal-sink-failed"]});
  }
  return summary({disposition: "emitted", provider_calls: 1, sink_calls: sinkCalls, signal_count: signals.length, signal_refs: signals.map((signal) => signal.record_id), reason_codes: []});
}
