import assert from "node:assert/strict";
import test from "node:test";
import { parseDomainSource } from "../src/parser.js";
import { deriveApplicationExternalWriteBindings } from "../src/application-external-write.js";
import { digest } from "../src/domainspec-profile.js";

const source = `domain commerce "Commerce"
owner fixture
profile application-v1
entity Order:
  id UInt64
  identity id
  accepted Bool
operation SubmitOrder:
  input Order
  output Order
interface PaymentApi:
  kind external
  version 1.0.0
  compatibility exact
  contract CaptureRequest:
    id UInt64
    accepted Bool
  contract CaptureResult:
    id UInt64
    accepted Bool
  exposes Capture:
    request CaptureRequest
    result CaptureResult
  exposes Inspect:
    request CaptureRequest
    result CaptureResult
mapping ToCapture:
  input order Order
  target PaymentApi.CaptureRequest
  total true
  field id <- order.id
  field accepted <- order.accepted
mapping ToInspect:
  input order Order
  target PaymentApi.CaptureRequest
  total true
  field id <- order.id
  field accepted <- order.accepted
mapping FromCapture:
  input observed PaymentApi.CaptureResult
  target Order
  total true
  field id <- observed.id
  field accepted <- observed.accepted
outbound-write CapturePayment:
  operation SubmitOrder
    -> interface PaymentApi
    -> write Capture
    -> inspect Inspect
    -> request-map ToCapture
    -> inspect-request-map ToInspect
    -> response-map FromCapture
  on-unknown inspect
  on-unresolved pending
  on-conflict reject
`;

test("external write source derives one exact typed write/inspect pair without claims or runtime authority", () => {
  const model = parseDomainSource(source).carrier as any;
  assert.deepEqual(model.formal_claims, []);
  assert.equal(model.integrations[0].kind, "outbound-write");
  const result = deriveApplicationExternalWriteBindings(source);
  assert.equal(result.artifact.source_sha256, digest(source));
  assert.equal(result.artifact.native_binding_status, "unbound");
  assert.equal(result.artifact.runtime_calls_observed, false);
  assert.deepEqual(result.artifact.bindings[0]!.ambiguous_outcome, { unknown: "inspect", unresolved: "pending", conflict: "reject" });
  assert.equal(result.artifact.bindings[0]!.write_member_ref, "commerce:payment-api#capture");
  assert.equal(result.artifact.bindings[0]!.inspect_member_ref, "commerce:payment-api#inspect");
  assert.deepEqual(result.artifact.bindings[0]!.wire_request_type, { kind: "public-contract", interface: "PaymentApi", contract: "CaptureRequest" });
  assert.deepEqual(JSON.parse(result.files["external-write-source-bindings.json"]!), result.artifact);
});

test("external write rejects type drift, non-paired exposures, and missing uncertainty disposition", () => {
  assert.throws(() => deriveApplicationExternalWriteBindings(source.replace("input order Order\n  target PaymentApi.CaptureRequest", "input order PaymentApi.CaptureRequest\n  target PaymentApi.CaptureRequest")), /APPLICATION_WRITE_MAPPING/);
  assert.throws(() => deriveApplicationExternalWriteBindings(source.replace("request CaptureRequest\n    result CaptureResult\nmapping ToCapture", "request CaptureResult\n    result CaptureResult\nmapping ToCapture")), /APPLICATION_WRITE_PAIR/);
  assert.throws(() => parseDomainSource(source.replace("  on-unresolved pending\n", "")), /INTEGRATION_PATH/);
  assert.throws(() => parseDomainSource(source.replace("on-unknown inspect", "on-unknown retry")), /INTEGRATION_WRITE_OUTCOME/);
});
