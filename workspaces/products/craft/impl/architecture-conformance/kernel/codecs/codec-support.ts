import { createHash } from "node:crypto";

import type {
  ExactRef,
  ExactRefResolver,
} from "../contracts/exact-ref.js";
import type { ExactRefIdentity } from "../contracts/validated-handle.js";

export const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");

export const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};

export const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

export const exactKeys = (
  value: Record<string, unknown>,
  expected: readonly string[],
): boolean => {
  const actual = Object.keys(value).sort();
  const required = [...expected].sort();
  return actual.length === required.length &&
    actual.every((key, index) => key === required[index]);
};

export const parseRecord = (bytes: string, code: string): Record<string, unknown> => {
  let value: unknown;
  try {
    value = JSON.parse(bytes);
  } catch {
    return fail(code);
  }
  return isRecord(value) ? value : fail(code);
};

export const recomputeDocumentDigest = (
  value: Record<string, unknown>,
  digestField: string,
): string => {
  const body = Object.fromEntries(
    Object.entries(value).filter(([key]) => key !== digestField),
  );
  return sha256(JSON.stringify(body));
};

const SHA256 = /^[a-f0-9]{64}$/u;

export const decodeExactRef = (value: unknown): ExactRef => {
  if (!isRecord(value) ||
      !exactKeys(value, ["id", "schema_version", "sha256"]) ||
      typeof value.id !== "string" || value.id.length === 0 ||
      typeof value.schema_version !== "string" ||
      value.schema_version.length === 0 ||
      typeof value.sha256 !== "string" || !SHA256.test(value.sha256)) {
    return fail("FACTORY_REF_INVALID");
  }
  return Object.freeze({
    id: value.id,
    schema_version: value.schema_version,
    sha256: value.sha256,
  });
};

export const validateExactRef = async (
  value: unknown,
  resolveRef: ExactRefResolver,
): Promise<ExactRefIdentity> => {
  const ref = decodeExactRef(value);
  let bytes: string;
  try {
    bytes = await resolveRef(ref);
  } catch {
    return fail("FACTORY_REF_UNRESOLVED");
  }
  if (typeof bytes !== "string" || bytes.length === 0) {
    return fail("FACTORY_REF_UNRESOLVED");
  }
  if (sha256(bytes) !== ref.sha256) return fail("FACTORY_REF_DIGEST_STALE");
  const referenced = parseRecord(bytes, "FACTORY_REF_SCHEMA_INVALID");
  if (referenced.schema_version !== ref.schema_version) {
    return fail("FACTORY_REF_SCHEMA_INVALID");
  }
  return Object.freeze({ id: ref.id, sha256: ref.sha256 });
};

export const unique = (values: readonly string[]): boolean =>
  new Set(values).size === values.length;
