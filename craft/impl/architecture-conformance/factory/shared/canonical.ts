import { createHash } from "node:crypto";

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

export const canonicalValue = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(canonicalValue);
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(Object.entries(value as Record<string, unknown>)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonicalValue(child)]));
  }
  return value;
};

export const canonicalJson = (value: unknown): string =>
  JSON.stringify(canonicalValue(value));

export const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");

export const json = (value: unknown): string =>
  `${JSON.stringify(value, null, 2)}\n`;

export const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail === undefined ? code : `${code}:${detail}`), {
    code,
    detail: detail ?? null,
  });
};

export const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

export const exactKeys = (
  value: Record<string, unknown>,
  keys: readonly string[],
  code = "FACTORY_REQUEST_INVALID",
): void => {
  const expected = [...keys].sort(compareUtf8);
  const observed = Object.keys(value).sort(compareUtf8);
  if (JSON.stringify(expected) !== JSON.stringify(observed)) fail(code, "closed-shape");
};

export const safeRelativePath = (value: string): boolean =>
  value.length > 0 && !value.startsWith("/") && !value.includes("\\") &&
  !value.split("/").some((part) => part === "" || part === "." || part === "..");
