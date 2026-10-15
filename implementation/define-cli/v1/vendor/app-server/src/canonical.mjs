import {createHash} from "node:crypto";

import {
  canonicalJson,
  canonicalizeJson,
  deepFreeze,
  sha256HexText,
} from "./json.mjs";

export {canonicalJson, canonicalizeJson, deepFreeze, sha256HexText};

export function digestValue(value) {
  return createHash("sha256").update(canonicalJson(value)).digest("hex");
}

export function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function nonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

export function uniqueStrings(value) {
  if (!Array.isArray(value)) return [];
  return [...new Set(value.filter(nonEmptyString).map((item) => item.trim()))].sort();
}

export function freezeResult(value) {
  return deepFreeze(canonicalizeJson(value));
}

export function fail(stage, reasonCodes, residue = []) {
  return freezeResult({
    schema_version: "are.codex-wrapper-failure/v1",
    ok: false,
    stage,
    reason_codes: [...new Set(reasonCodes)].sort(),
    residue,
    authority_effect: "none",
  });
}
