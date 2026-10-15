import {createHash} from "node:crypto";

export {classifyHostedReadFailure, isHostedReadFailureDiagnostic} from "../client/read-diagnostic.js";

const SECRET_PATTERNS = [
  /\b(?:api[-_]?key|access[-_]?token|refresh[-_]?token|client[-_]?secret|password)\s*[:=]\s*[^\s,;]+/giu,
  /\bBearer\s+[A-Za-z0-9._~+\/-]+=*/giu,
  /\b(?:sk|rk|pk)-[A-Za-z0-9_-]{8,}\b/gu,
];

function redact(text) {
  let value = String(text ?? "");
  for (const pattern of SECRET_PATTERNS) value = value.replace(pattern, "[REDACTED]");
  return value;
}

export function classifyBackendDiagnostic(input, options = {}) {
  const raw = String(input ?? "");
  const maximumBytes = options.maximum_bytes ?? 2048;
  if (!Number.isSafeInteger(maximumBytes) || maximumBytes < 64) throw new TypeError("diagnostic.maximum-bytes-invalid");
  const clean = redact(raw).replaceAll(/\p{C}+/gu, " ").trim();
  const preview = Buffer.from(clean, "utf8").subarray(0, maximumBytes).toString("utf8");
  return Object.freeze({
    schema_version: "are.backend-diagnostic/v1",
    classification: options.classification ?? "backend-stderr",
    preview,
    truncated: Buffer.byteLength(clean) > Buffer.byteLength(preview),
    source_bytes: Buffer.byteLength(raw),
    source_digest: createHash("sha256").update(raw).digest("hex"),
    secret_values_emitted: false,
    authority_effect: "none",
  });
}
