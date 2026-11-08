import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { compileMessagingCompositionV2, MessagingCompositionError, projectLegacyMessagingV1, validateMessagingCompositionV2 } from "../../src/system-integration/messaging-v2.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixtureRoot = path.resolve(here, "../../../system-integration/fixtures/messaging-composition-v2");
const schemaPath = path.resolve(here, "../../../system-integration/contracts/messaging-composition-v2.schema.json");
const fixture = JSON.parse(fs.readFileSync(path.join(fixtureRoot, "order-submitted-topic.json"), "utf8"));
const legacy = JSON.parse(fs.readFileSync(path.join(fixtureRoot, "legacy-publish-subscribe.json"), "utf8"));
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

test("R4 messaging composition is a deterministic orthogonal graph", () => {
  const left = compileMessagingCompositionV2(fixture);
  const right = compileMessagingCompositionV2(clone(fixture));
  assert.deepEqual(left, right);
  assert.match(left.composition_digest, /^[a-f0-9]{64}$/);
  assert.deepEqual(left.channels.map(item => item.channel_kind), ["dead-letter", "queue", "stream", "topic"]);
  assert.equal(left.publication_bindings[0]!.logical_source_ref, "commerce:order-submitted");
  assert.equal(left.publication_bindings[0]!.message_type_ref, "message-type:order-submitted-v1");
  assert.equal(left.runtime_delivery_observed, false);
});

test("R4 schema closes each graph node and binding", () => {
  const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
  assert.equal(schema.additionalProperties, false);
  for (const name of ["messageType", "messageMapping", "queue", "topic", "stream", "deadLetter", "deliveryPolicy", "producerBoundary", "acknowledgementBoundary", "orderingPolicy", "deduplicationPolicy", "publicationBinding", "subscriptionBinding"]) {
    assert.equal(schema.$defs[name].additionalProperties, false, name);
  }
});

test("Event cannot bind directly to transport without a distinct Message mapping", () => {
  const direct = clone(fixture);
  direct.publication_bindings[0].message_type_ref = "commerce:order-submitted";
  assert.throws(() => validateMessagingCompositionV2(direct), (error) => error instanceof MessagingCompositionError && error.code === "MESSAGING_GRAPH_COLLAPSE");
  const missingMapping = clone(fixture);
  missingMapping.message_mappings = missingMapping.message_mappings.filter((item: { direction: string }) => item.direction !== "logical-to-message");
  assert.throws(() => validateMessagingCompositionV2(missingMapping), (error) => error instanceof MessagingCompositionError && error.code === "MESSAGING_GRAPH_COLLAPSE");
});

test("queue, topic, stream, and dead-letter semantics cannot be relabeled", () => {
  const queue = clone(fixture);
  queue.channels.find((item: { channel_kind: string }) => item.channel_kind === "queue").consumption_model = "fan-out-subscriptions";
  assert.throws(() => validateMessagingCompositionV2(queue), (error) => error instanceof MessagingCompositionError && error.code === "MESSAGING_CHANNEL_COLLAPSE");
  const deadLetter = clone(fixture);
  deadLetter.channels.find((item: { channel_kind: string }) => item.channel_kind === "dead-letter").source_channel_ref = "channel:order-events-dead-letter";
  assert.throws(() => validateMessagingCompositionV2(deadLetter), (error) => error instanceof MessagingCompositionError && error.code === "MESSAGING_CHANNEL_COLLAPSE");
});

test("producer acceptance cannot claim transport delivery or application completion", () => {
  const inflated = clone(fixture);
  inflated.producer_acceptance_boundaries[0].claim_ceiling = "application-committed";
  assert.throws(() => validateMessagingCompositionV2(inflated), (error) => error instanceof MessagingCompositionError && error.code === "MESSAGING_ACCEPTANCE_CLAIM");
});

test("acknowledgement, delivery, ordering, and deduplication remain independent selections", () => {
  const missingOrdering = clone(fixture);
  missingOrdering.subscription_bindings[0].ordering_policy_ref = "ordering:missing";
  assert.throws(() => validateMessagingCompositionV2(missingOrdering), (error) => error instanceof MessagingCompositionError && error.code === "MESSAGING_REFERENCE_UNRESOLVED");
  const wrongAckOwner = clone(fixture);
  wrongAckOwner.acknowledgement_boundaries[0].subscription_binding_ref = "subscription:missing";
  assert.throws(() => validateMessagingCompositionV2(wrongAckOwner), (error) => error instanceof MessagingCompositionError && error.code === "MESSAGING_REFERENCE_UNRESOLVED");
});

test("legacy v1 projection retains facts without inventing v2 semantics", () => {
  const projection = projectLegacyMessagingV1(legacy);
  assert.deepEqual(projection.retained_event_refs, ["commerce:order-submitted"]);
  assert.deepEqual(projection.retained_operation_refs, ["commerce:submit-order"]);
  assert.equal(projection.channel_classification, "legacy-undifferentiated");
  assert.equal(projection.producer_acceptance, "provider-accepted-unclassified");
  assert.equal(projection.message_types_inferred, false);
  assert.equal(projection.subscriptions_inferred, false);
  assert.equal(projection.consumer_acknowledgement_inferred, false);
  assert.equal(projection.application_commit_inferred, false);
  assert.equal(projection.exactly_once_inferred, false);
});
