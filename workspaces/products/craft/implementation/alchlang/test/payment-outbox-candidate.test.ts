import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import { parseDomainSource } from "../src/parser.js";
import type { ApplicationFormalSource } from "../src/formal-claim.js";

const sourcePath = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../review/whole-application-v1/candidate/payment-outbox.alch");
const source = readFileSync(sourcePath, "utf8");

test("candidate payment model uses first-class Money, states, and Event triggers", () => {
  const model = parseDomainSource(source).carrier as unknown as ApplicationFormalSource;
  const declaration = (id: string) => model.declarations.find(item => item.id === id);
  const money = declaration("Money");
  assert.ok(money && money.kind === "value-object");
  assert.deepEqual(money.fields.map(field => field.name), ["amountMinor", "currency"]);
  const intent = declaration("PaymentIntent");
  assert.ok(intent && intent.kind === "entity");
  assert.equal(intent.identity, "submissionId");
  assert.deepEqual(intent.fields.map(field => field.name), ["submissionId", "orderId", "amount", "status"]);
  const requested = declaration("PaymentAuthorizationRequested");
  assert.ok(requested && requested.kind === "event");
  assert.equal(requested.occurred_at_policy, "generated");
  const lifecycle = declaration("PaymentLifecycle");
  assert.ok(lifecycle && lifecycle.kind === "state-machine");
  assert.equal(lifecycle.subject, "PaymentIntent");
  assert.equal(lifecycle.initial, "Pending");
  assert.deepEqual(lifecycle.transitions.map(({ from, to, trigger_event }) => [from, to, trigger_event]), [
    ["Pending", "Authorized", "PaymentAuthorized"],
    ["Pending", "Declined", "PaymentDeclined"],
    ["Pending", "Unresolved", "PaymentOutcomeUnknown"],
    ["Unresolved", "Authorized", "PaymentAuthorized"],
    ["Unresolved", "Declined", "PaymentDeclined"],
  ]);
});

test("candidate lifecycle rejects an undeclared authorization outcome Event", () => {
  assert.throws(() => parseDomainSource(source.replace("on PaymentAuthorized", "on MissingPaymentEvent")),
    /MissingPaymentEvent is not an Event/);
});
