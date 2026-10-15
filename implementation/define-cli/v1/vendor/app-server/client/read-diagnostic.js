const READ_RPC_FAILURES = new Map([
  ["rpc.response-error", "rpc-response-rejected"],
  ["rpc.request-timeout", "rpc-timeout"],
  ...["rpc.closed", "rpc.transport-exited", "rpc.transport-spawn-failed", "rpc.transport-failed"]
    .map(code => [code, "transport-unavailable"]),
  ["rpc.invalid-json", "invalid-response"],
]);
const READ_REASON_CODES = new Set([
  "gateway.turn-history-stale", "gateway.turn-history-unsettled",
  "gateway.history-audit-not-durable", "gateway.history-audit-completion-not-durable",
  "gateway.turn-history-not-durable", "gateway.turn-history-status-conflict",
  "gateway.turn-marker-history-conflict", "gateway.turn-completion-status-conflict",
  "gateway.turn-marker-not-durable", "gateway.session-faulted", "gateway.history-audit-incomplete",
]);
const INVALID_READ_MESSAGES = new Set(["windows-client.runtime-response-invalid",
  "windows-client.history-response-invalid", "windows-client.history-turn-invalid"]);

// Pure, shared contract: no host APIs, storage, network, Node imports or effects.
// These labels describe a failed read, never permission to retry a model turn.
export function classifyHostedReadFailure(error) {
  const rpcCode = READ_RPC_FAILURES.has(error?.code) ? error.code : null;
  const reasons = error?.details?.data?.reason_codes;
  const reasonCodes = rpcCode === "rpc.response-error" && Array.isArray(reasons) && reasons.length <= 8
    ? [...new Set(reasons.filter(code => READ_REASON_CODES.has(code)))] : [];
  return Object.freeze({schema_version: "are.hosted-read-diagnostic/v1",
    classification: READ_RPC_FAILURES.get(rpcCode)
      ?? (INVALID_READ_MESSAGES.has(error?.message) ? "invalid-response" : "internal-failure"),
    rpc_code: rpcCode, reason_codes: Object.freeze(reasonCodes), authority_effect: "none"});
}

export function isHostedReadFailureDiagnostic(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)
    || Object.keys(value).sort().join(",") !== "authority_effect,classification,reason_codes,rpc_code,schema_version"
    || value.schema_version !== "are.hosted-read-diagnostic/v1" || value.authority_effect !== "none"
    || !Array.isArray(value.reason_codes) || value.reason_codes.length > 8
    || new Set(value.reason_codes).size !== value.reason_codes.length
    || [...value.reason_codes].some(code => !READ_REASON_CODES.has(code))) return false;
  return (value.rpc_code === null
    ? ["invalid-response", "internal-failure"].includes(value.classification)
    : READ_RPC_FAILURES.has(value.rpc_code) && READ_RPC_FAILURES.get(value.rpc_code) === value.classification)
    && (value.rpc_code === "rpc.response-error" || value.reason_codes.length === 0);
}

const EXPLANATIONS = Object.freeze({
  "rpc-timeout": "the ARE host read timed out. Check the host connection",
  "transport-unavailable": "the ARE host connection was lost. Restore the connection",
  "rpc-response-rejected": "ARE refused the host read. See Diagnostics",
  "invalid-response": "the host response could not be verified. See Diagnostics",
  "internal-failure": "the host read failed. See Diagnostics",
});

export function hostedReadFailureView(value, kind = "runtime") {
  if (!["runtime", "history"].includes(kind)) throw new TypeError("Unsupported hosted read kind.");
  const valid = isHostedReadFailureDiagnostic(value);
  const diagnostic = valid ? Object.freeze({schema_version: value.schema_version,
    classification: value.classification, rpc_code: value.rpc_code,
    reason_codes: Object.freeze([...value.reason_codes]), authority_effect: "none"}) : null;
  return Object.freeze({
    message: `${kind === "runtime" ? "Turn state" : "Stored history"} unavailable: ${valid
      ? EXPLANATIONS[value.classification] : "the read failure could not be verified. See Diagnostics"}; no turn was resent.`,
    diagnostic,
  });
}
