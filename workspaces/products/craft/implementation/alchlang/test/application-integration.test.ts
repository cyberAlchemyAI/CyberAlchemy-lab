import assert from "node:assert/strict";
import test from "node:test";
import { parseDomainSource } from "../src/parser.js";
import type { ApplicationFormalSource } from "../src/formal-claim.js";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { digest } from "../src/domainspec-profile.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";

const header = 'domain commerce "Commerce"\nprofile application-v1\nowner commerce-team\n';
const subscription = `subscription StartBilling:
  topic OrderEvents
    -> message OrderSubmittedMessage
    -> map MessageToAuthorizePayment
    -> operation AuthorizePayment
  acknowledge after application-commit
  deduplicate by messageId
  failure -> dead-letter OrderEventsDeadLetter
`;
const publication = `publication PublishOrderSubmitted:
  event OrderSubmitted
    -> map OrderSubmittedToMessage
    -> message OrderSubmittedMessage
    -> topic OrderEvents
`;
const inbound = `inbound-endpoint SubmitOrderHttp:
  HTTP POST "/orders"
    -> request SubmitOrderRequest
    -> operation SubmitOrder
    -> response OrderSummary
`;
const outbound = `outbound-call AuthorizePaymentCall:
  operation AuthorizePayment
    -> request PaymentAuthorizationRequest
    -> external-api PaymentGateway
    -> response PaymentAuthorization
`;
const persistence = `persistence Orders:
  stores Order
  serves FindOrder
  accepts-writes-from SubmitOrder
  transaction local
`;
const parse = (source: string) => parseDomainSource(header + source).carrier as unknown as ApplicationFormalSource;

test("existing scanner preserves all five closed integration paths and source locations", () => {
  const body = subscription + publication + inbound + outbound + persistence;
  const model = parse(body);
  assert.deepEqual(model, parse(body));
  assert.deepEqual(model.integrations.map(i => i.kind), ["subscription", "publication", "inbound-endpoint", "outbound-call", "persistence"]);
  assert.deepEqual(model.declarations, []);
  const [sub, pub, http, api, db] = model.integrations;
  assert.equal(sub!.kind, "subscription");
  if (sub!.kind !== "subscription" || pub!.kind !== "publication" || http!.kind !== "inbound-endpoint" || api!.kind !== "outbound-call" || db!.kind !== "persistence") assert.fail("lost typed integration kinds");
  assert.deepEqual(sub.channel, { kind: "topic", ref: "OrderEvents", source_line: 5 });
  assert.equal(sub.mapping.ref, "MessageToAuthorizePayment");
  assert.equal(sub.operation.ref, "AuthorizePayment");
  assert.equal(sub.acknowledge.condition, "application-committed");
  assert.deepEqual(sub.deduplicate.key_path, ["messageId"]);
  assert.equal(sub.dead_letter.ref, "OrderEventsDeadLetter");
  assert.equal(pub.event.ref, "OrderSubmitted");
  assert.equal(pub.message.ref, "OrderSubmittedMessage");
  assert.equal(http.protocol.method, "POST"); assert.equal(http.protocol.path, "/orders");
  assert.equal(http.request.ref, "SubmitOrderRequest"); assert.equal(http.response.ref, "OrderSummary");
  assert.equal(api.external_api.ref, "PaymentGateway");
  assert.equal(db.entity.ref, "Order"); assert.equal(db.queries[0]!.ref, "FindOrder");
  assert.equal(db.operations[0]!.ref, "SubmitOrder"); assert.equal(db.transaction.scope, "single-resource-local");
});

test("channel and acknowledgement variants stay distinct without inferred delivery guarantees", () => {
  for (const kind of ["queue", "topic", "stream"]) {
    const model = parse(subscription.replace("topic OrderEvents", `${kind} OrderEvents`).replace("application-commit", "handler-return"));
    const sub = model.integrations[0]!;
    if (sub.kind !== "subscription") assert.fail("wrong kind");
    assert.equal(sub.channel.kind, kind); assert.equal(sub.acknowledge.condition, "consumer-handler-returned");
    assert.equal("provider" in sub, false); assert.equal("exactly_once" in sub, false);
  }
});

test("reordered paths, invented roles, expressions and imperative statements reject at their source", () => {
  const mutations = [
    subscription.replace("-> message OrderSubmittedMessage", "-> operation OrderSubmittedMessage"),
    subscription.replace("-> map MessageToAuthorizePayment", "-> transformed-by MessageToAuthorizePayment"),
    subscription.replace("-> operation AuthorizePayment", "-> operation AuthorizePayment()"),
    subscription.replace("    -> map", "  -> map"),
    subscription.replace("    -> operation", "      -> operation"),
    subscription.replace("  acknowledge", "    acknowledge"),
    subscription.replace("application-commit", "provider-accepted"),
    subscription.replace("deduplicate by messageId", "deduplicate by hash(messageId)"),
    subscription.replace("failure -> dead-letter", "failure -> topic"),
    subscription.replace("  acknowledge after application-commit\n", ""),
    publication.replace("event OrderSubmitted", "message OrderSubmitted"),
    publication + "  save Order\n",
    inbound.replace("-> operation SubmitOrder", "-> invokes SubmitOrder"),
    outbound.replace("-> external-api PaymentGateway", "-> external-api https://example.invalid"),
    persistence.replace("transaction local", "transaction distributed"),
    persistence + "  serves FindOrder\n",
    persistence + '  provider "postgresql"\n',
  ];
  for (const source of mutations) assert.throws(() => parse(source), e => {
    assert.match(String(e), /INTEGRATION_/); assert.match(String(e), /\$line:/); return true;
  });
});

test("HTTP routes reject remote URLs, secrets in queries and ambiguous path forms", () => {
  for (const path of ["https://host/orders", "//host/orders", "/orders?token=secret", "/orders#fragment", "/or ders", "/orders\n", "/orders\\x"]) {
    assert.throws(() => parse(inbound.replace('"/orders"', JSON.stringify(path))), /INTEGRATION_HTTP/);
  }
});

test("persistence retains multiple consumers without inventing reads or writes", () => {
  const readOnly = parse(persistence.replace("  accepts-writes-from SubmitOrder\n", "")).integrations[0]!;
  const writeOnly = parse(persistence.replace("  serves FindOrder\n", "")).integrations[0]!;
  const multiple = parse(persistence + "  serves FindOtherOrder\n  accepts-writes-from CancelOrder\n").integrations[0]!;
  if (readOnly.kind !== "persistence" || writeOnly.kind !== "persistence" || multiple.kind !== "persistence") assert.fail("wrong kind");
  assert.deepEqual(readOnly.operations, []); assert.deepEqual(writeOnly.queries, []);
  assert.deepEqual(multiple.queries.map(r => r.ref), ["FindOrder", "FindOtherOrder"]);
  assert.deepEqual(multiple.operations.map(r => r.ref), ["SubmitOrder", "CancelOrder"]);
  assert.throws(() => parse("persistence Orders:\n  stores Order\n  transaction local\n"), /INTEGRATION_PERSISTENCE/);
});

test("integration declarations cannot disappear into the legacy profile or duplicate domain identity", () => {
  for (const body of [subscription, publication, inbound, outbound, persistence]) {
    assert.throws(() => parseDomainSource((header + body).replace("profile application-v1\n", "")), /ALCH_PROFILE_REQUIRED/);
    assert.throws(() => parseDomainSource((header + body).replace("application-v1", "legacy-sfol-v1")), /ALCH_PROFILE_REQUIRED/);
  }
  assert.throws(() => parse(subscription + "entity StartBilling:\n  id UInt64\n  identity id\n"), /DUPLICATE_IDENTIFIER/);
});

test("domain-only formation cannot silently discard newly parsed integration intent", () => {
  const f = executableFixture(); const source = f.source + publication;
  const bindings = { ...f.bindings, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) } };
  assert.throws(() => lowerApplicationDomain(source, bindings, f.sources), /APPLICATION_INTEGRATION_LOWERING_REQUIRED/);
});
