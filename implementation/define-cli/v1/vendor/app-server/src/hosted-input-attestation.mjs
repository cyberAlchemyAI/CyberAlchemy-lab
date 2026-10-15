import {createHmac, timingSafeEqual} from "node:crypto";

import {canonicalJson, isRecord, nonEmptyString} from "./canonical.mjs";

export const HOSTED_INPUT_ATTESTATION_SCHEMA = "are.hosted-input-attestation/v1";
const HOSTED_INPUT_METHODS = new Set(["turn/start", "turn/steer", "cyberalchemy/learning/submitFeedback",
  "cyberalchemy/learning/applyPendingFeedback", "cyberalchemy/learning/dismissPendingFeedback"]);

export function validHostedInputAttestationKey(key) {
  return typeof key === "string" && /^[0-9a-f]{64}$/.test(key);
}

function payload({consumer_id, method, params, request_key = null}) {
  if (!nonEmptyString(consumer_id) || !HOSTED_INPUT_METHODS.has(method)
    || !isRecord(params) || (request_key !== null && !nonEmptyString(request_key))) {
    throw new TypeError("Hosted input attestation requires a supported request and consumer.");
  }
  return canonicalJson({schema_version: HOSTED_INPUT_ATTESTATION_SCHEMA,
    consumer_id, method, params, request_key});
}

export function signHostedInput({key, ...request}) {
  if (!validHostedInputAttestationKey(key)) throw new TypeError("Hosted input attestation key must be 32 hex bytes.");
  return createHmac("sha256", Buffer.from(key, "hex")).update(payload(request)).digest("hex");
}

export function verifyHostedInput({key, signature, ...request}) {
  if (!validHostedInputAttestationKey(key) || typeof signature !== "string"
    || !/^[0-9a-f]{64}$/.test(signature)) return false;
  let expected;
  try { expected = signHostedInput({key, ...request}); } catch { return false; }
  return timingSafeEqual(Buffer.from(signature, "hex"), Buffer.from(expected, "hex"));
}
