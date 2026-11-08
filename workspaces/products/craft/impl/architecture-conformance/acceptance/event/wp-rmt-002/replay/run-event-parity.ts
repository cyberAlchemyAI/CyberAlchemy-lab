import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import type {FactoryNodeProviderV1} from "../../../../factory/contracts/factory-node-provider-v1.js";
import {eventPythonV1Provider} from "../../../../factory/registry/providers/event-python-v1.js";
import {eventRustV1Provider} from "../../../../factory/registry/providers/event-rust-v1.js";
import {eventTypeScriptV1Provider} from "../../../../factory/registry/providers/event-typescript-v1.js";
import {makeSettlementEventCase, makeSettlementEventS1Case} from "../../../../targets/typescript/event-v1.js";

const parityReceiptPath = "projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-EVENT-006.json";
const parityReceiptSha256 = "17fbbf95a213973cdd08d30f44f37124696f7634aaa049d28af912b5201d6053";
const hostileRoot = "projects/domainspec-v2/impl/architecture-conformance/families/past-tense-event/hostiles";
const providers = [eventTypeScriptV1Provider, eventPythonV1Provider, eventRustV1Provider] as const;
const canonical = (value: unknown): unknown => Array.isArray(value) ? value.map(canonical) : value && typeof value === "object" ? Object.fromEntries(Object.entries(value).sort(([left], [right]) => left.localeCompare(right)).map(([key, item]) => [key, canonical(item)])) : value;
const load = (name: string) => JSON.parse(readFileSync(`${hostileRoot}/${name}.json`, "utf8"));
const execute = (provider: FactoryNodeProviderV1, eventCase: unknown) => provider.execute({raw_inputs: {event_case: JSON.stringify(eventCase)}} as never);

const runAll = async (eventCase: unknown) => {
  const results = [];
  for (const provider of providers) results.push(await execute(provider, eventCase));
  return results;
};

const assertPortableParity = (results: readonly any[]): readonly any[] => {
  const outputs = results.map(result => result.semantic_output);
  const portable = outputs.map(({portable}: any) => JSON.stringify(canonical(portable)));
  if (results.some(({result}) => result !== "pass") || portable[1] !== portable[0] || portable[2] !== portable[0]) throw new Error("RMT_EVENT_REPLAY_PARITY_DRIFT");
  return outputs;
};

const assertRejectedByAll = async (eventCase: unknown, errorCode: string): Promise<void> => {
  const messages = await Promise.all(providers.map(async provider => {
    try { await execute(provider, eventCase); return "accepted"; }
    catch (error) { return error instanceof Error ? error.message : String(error); }
  }));
  if (!messages.every(message => message.includes(errorCode))) throw new Error("RMT_EVENT_REPLAY_INCOHERENT_INPUT_ACCEPTED");
};

export const runEventParity = async () => {
  const bytes = readFileSync(parityReceiptPath);
  const observedHash = createHash("sha256").update(bytes).digest("hex");
  if (observedHash !== parityReceiptSha256) throw new Error("RMT_EVENT_REPLAY_PARITY_RECEIPT_STALE");
  const receipt = JSON.parse(bytes.toString("utf8"));
  if (receipt.result !== "pass" || receipt.authority_effect !== "none" || receipt.semantic_plan_epoch_id !== "WP-RMT-002/S1/2026-08-16" || receipt.proof_closure?.s1_cross_boundary_count !== 7) throw new Error("RMT_EVENT_REPLAY_PARITY_RECEIPT_INVALID");

  const first = await runAll(makeSettlementEventCase("publish:req-1:1"));
  const retry = await runAll(makeSettlementEventCase("publish:req-1:2"));
  const firstOutputs = assertPortableParity(first);
  const retryOutputs = assertPortableParity(retry);
  const attempts = [];
  for (let index = 0; index < providers.length; index++) {
    const initial = firstOutputs[index].portable;
    const repeated = retryOutputs[index].portable;
    if (initial.occurrence_id !== repeated.occurrence_id || initial.durable_occurrence.publication_attempt_id === repeated.durable_occurrence.publication_attempt_id || initial.durable_occurrence.acknowledgement_state !== "unknown" || repeated.distributed_exactly_once_claim !== false) throw new Error("RMT_EVENT_REPLAY_DURABLE_FACT_DRIFT");
    attempts.push(Object.freeze({provider_id: first[index]!.provider_id, occurrence_id: initial.occurrence_id, publication_attempt_ids: Object.freeze([initial.durable_occurrence.publication_attempt_id, repeated.durable_occurrence.publication_attempt_id])}));
  }

  const s1Controls = [];
  for (const [name, expectedCode] of [["recovery-replay", "RMT_S1_RECOVERY_REPLAY_MISMATCH"], ["non-idempotent-retry", "RMT_S1_NON_IDEMPOTENT_RETRY"]] as const) {
    const hostile = load(name);
    if (hostile.hostile_id !== `s1/${name}` || hostile.proof_owner_swu !== "RMT-EVENT-007" || hostile.expected_code !== expectedCode) throw new Error("RMT_EVENT_REPLAY_S1_FIXTURE_INVALID");
    const results = await runAll(makeSettlementEventS1Case(hostile));
    const outputs = assertPortableParity(results);
    const portable = outputs[0].portable;
    if (portable.result !== "reject" || portable.diagnostic_code !== expectedCode || portable.scenario !== name || portable.occurrence_id !== "settlement:req-1" || portable.distributed_exactly_once_claim !== false) throw new Error("RMT_EVENT_REPLAY_S1_SEMANTIC_DRIFT");
    s1Controls.push(Object.freeze({hostile_id: hostile.hostile_id, diagnostic_code: portable.diagnostic_code, required_residue: portable.required_residue, provider_ids: Object.freeze(results.map(({provider_id}) => provider_id))}));
  }

  const recovery = makeSettlementEventS1Case(load("recovery-replay"));
  await assertRejectedByAll({...recovery, observation: {...recovery.observation, s1_observation: {...recovery.observation.s1_observation!, recovered_occurrence_id: "settlement:req-2"}}}, "RMT_EVENT_S1_OBSERVATION_INVALID");
  const nonIdempotent = makeSettlementEventS1Case(load("non-idempotent-retry"));
  await assertRejectedByAll({...nonIdempotent, observation: {...nonIdempotent.observation, s1_observation: {...nonIdempotent.observation.s1_observation!, retry_occurrence_id: "settlement:req-1", consumer_effect_count: 1}}}, "RMT_EVENT_S1_OBSERVATION_INVALID");

  return Object.freeze({
    schema_version: "domainspec.event-semantic-replay-receipt/v1", result: "pass", work_pack_id: "WP-RMT-002", swu_id: "RMT-EVENT-007",
    semantic_plan_epoch_id: "WP-RMT-002/S1/2026-08-16", semantic_contract_digest: "75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7",
    parity_receipt: Object.freeze({path: parityReceiptPath, sha256: observedHash, size_bytes: bytes.length}),
    provider_ids: Object.freeze(first.map(({provider_id}) => provider_id)), portable: firstOutputs[0].portable, retry_attempts: Object.freeze(attempts),
    s1_replay_controls: Object.freeze(s1Controls), native_evidence: Object.freeze(firstOutputs.map(({native_evidence}: any) => native_evidence)),
    fresh_process_count_declared: 2, provider_attempt_count: 12, recovery_replay_stable: true, recovery_same_occurrence_and_outcome: true,
    recovery_mismatch_rejected_by_all_providers: true, non_idempotent_retry_rejected_by_all_providers: true,
    acknowledgement_ambiguity_preserves_durable_facts: true, native_hash_byte_comparison: false, authority_effect: "none",
  });
};

if (process.argv[1]?.endsWith("run-event-parity.ts")) {
  const mode = process.argv[2] ?? "--emit";
  if (mode === "--fail") { process.stderr.write("RMT_EVENT_REPLAY_PROBE_FAILURE\n"); process.exitCode = 23; }
  else if (mode === "--malformed-output") process.stdout.write("{}\n{}\n");
  else if (mode === "--emit") {
    try { process.stdout.write(`${JSON.stringify(await runEventParity())}\n`); }
    catch (error) { process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`); process.exitCode = 1; }
  } else { process.stderr.write("RMT_EVENT_REPLAY_MODE_INVALID\n"); process.exitCode = 24; }
}
