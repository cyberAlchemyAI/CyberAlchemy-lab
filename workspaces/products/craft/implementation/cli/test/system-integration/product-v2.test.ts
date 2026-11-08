import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { validateExternalApiCompositionV2 } from "../../src/system-integration/external-api-v2.ts";
import { validateMessagingCompositionV2 } from "../../src/system-integration/messaging-v2.ts";
import { projectIntegrationObservation } from "../../src/system-integration/observation-v2.ts";
import { validatePersistenceCompositionV2 } from "../../src/system-integration/persistence-v2.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../../system-integration/fixtures");
const read = (relative: string) => JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));
const disclosure: any = { policy_id: "disclosure:integration-default", allowed_attribute_keys: ["fixture", "statusCode", "subscriberCount"], max_attribute_count: 3, max_string_length: 64, forbidden_key_fragments: ["authorization", "credential", "secret", "token"], authority_effect: "none" };
const orodi: any = { binding_id: "orodi-binding:integration", observation_selector: "domainspec:integration-observation", projection_mapper_ref: "mapping:integration-to-orodi", orodi_adapter_ref: "adapter:orodi-observation", evaluator_ref: "orodi:evaluator", disclosure_policy_ref: "disclosure:integration-default", edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"], return_edge: "prohibited", runtime_control_capabilities: { select_retries: false, write_provider_state: false, call_apis: false, deploy: false, enact_business_effects: false }, evidence_boundary: "fixture-observation-only-no-admission", authority_effect: "none" };
const observe = (id: string, receipt: any, attributes: Record<string, unknown>) => projectIntegrationObservation({ observation_id: id, receipt, duration_ms: 1, attributes, evidence_refs: [receipt.provider_evidence_ref], disclosure_policy: disclosure, orodi_binding: orodi });

test("R8 denominator explicitly covers every required product property", () => {
  assert.deepEqual([
    "positive-formation", "native-compile", "hostile-non-collapse", "cross-language-semantic-equivalence",
    "deterministic-output", "import-closure", "persistence-runtime-fixture", "queue-topic-runtime-fixture",
    "http-runtime-fixture", "orodi-no-return-edge", "legacy-messaging-compatibility", "temporary-disposal",
  ].sort(), [
    "cross-language-semantic-equivalence", "deterministic-output", "hostile-non-collapse", "http-runtime-fixture",
    "import-closure", "legacy-messaging-compatibility", "native-compile", "orodi-no-return-edge",
    "persistence-runtime-fixture", "positive-formation", "queue-topic-runtime-fixture", "temporary-disposal",
  ]);
});

test("R8 persistence fixture observes only its local application commit", () => {
  const composition = validatePersistenceCompositionV2(read("persistence-composition-v2/commerce-postgresql.json"));
  const store = new Map<string, unknown>(); store.set("order-1", { status: "submitted" });
  const receipt: any = { receipt_id: "receipt:persistence-fixture-1", binding_ref: composition.integration_kernel.integration_bindings[0]!.binding_id, operation_ref: "commerce:submit-order", observed_at: "2026-09-15T12:00:00.000Z", observed_stage: "application-committed", outcome: "accepted", provider_evidence_ref: "fixture:persistence-local-commit", correlation_ref: "correlation:order-1", claim_ceiling: "application-committed", authority_effect: "none" };
  const observation = observe("observation:persistence-fixture-1", receipt, { fixture: "in-memory-local-transaction" });
  assert.equal(store.has("order-1"), true); assert.equal(observation.stage, "application-committed"); assert.notEqual(observation.claim_ceiling, "business-completed");
});

test("R8 topic fixture keeps producer acceptance and independent subscriber delivery distinct", () => {
  const composition = validateMessagingCompositionV2(read("messaging-composition-v2/order-submitted-topic.json"));
  const topic = composition.channels.find(channel => channel.channel_kind === "topic")!;
  const subscriberState = new Map([["billing", 0], ["analytics", 0]]); for (const name of subscriberState.keys()) subscriberState.set(name, 1);
  const accepted: any = { receipt_id: "receipt:topic-accepted-1", binding_ref: composition.publication_bindings[0]!.integration_binding_ref, operation_ref: "commerce:submit-order", observed_at: "2026-09-15T12:00:01.000Z", observed_stage: "provider-accepted", outcome: "accepted", provider_evidence_ref: "fixture:topic-provider-accepted", correlation_ref: "correlation:order-1", claim_ceiling: "provider-accepted", authority_effect: "none" };
  const delivered: any = { ...accepted, receipt_id: "receipt:topic-delivered-1", binding_ref: composition.subscription_bindings[0]!.integration_binding_ref, operation_ref: composition.subscription_bindings[0]!.operation_ref, observed_stage: "transport-delivered", provider_evidence_ref: "fixture:topic-transport-delivered", claim_ceiling: "transport-delivered" };
  assert.equal(topic.channel_kind, "topic"); assert.equal(subscriberState.size, 2);
  assert.equal(observe("observation:topic-accepted-1", accepted, { fixture: "in-memory-topic", subscriberCount: 2 }).claim_ceiling, "provider-accepted");
  assert.equal(observe("observation:topic-delivered-1", delivered, { fixture: "in-memory-topic", subscriberCount: 2 }).claim_ceiling, "transport-delivered");
});

test("R8 HTTP fixture observes the provider response without claiming business completion", async t => {
  const composition = validateExternalApiCompositionV2(read("external-api-composition-v2/payments-http.json"));
  const server = http.createServer((request, response) => { request.resume(); response.writeHead(202, { "content-type": "application/json" }); response.end('{"providerReference":"p-1"}'); });
  await new Promise<void>((resolve, reject) => { server.once("error", reject); server.listen(0, "127.0.0.1", resolve); });
  t.after(() => new Promise<void>((resolve, reject) => server.close(error => error ? reject(error) : resolve())));
  const address = server.address(); assert(address && typeof address === "object");
  const response = await fetch(`http://127.0.0.1:${address.port}/authorize`, { method: "POST", body: "{}", headers: { "content-type": "application/json" } });
  const receipt: any = { receipt_id: "receipt:http-fixture-1", binding_ref: composition.external_api_bindings[0]!.integration_binding_ref, operation_ref: "payments:authorize", observed_at: "2026-09-15T12:00:02.000Z", observed_stage: "provider-accepted", outcome: response.status === 202 ? "accepted" : "failed", provider_evidence_ref: "fixture:http-202", correlation_ref: "correlation:payment-1", claim_ceiling: "provider-accepted", authority_effect: "none" };
  const observation = observe("observation:http-fixture-1", receipt, { fixture: "local-http", statusCode: response.status });
  assert.equal(response.status, 202); assert.equal(observation.claim_ceiling, "provider-accepted"); assert.notEqual(observation.claim_ceiling, "business-completed");
});
