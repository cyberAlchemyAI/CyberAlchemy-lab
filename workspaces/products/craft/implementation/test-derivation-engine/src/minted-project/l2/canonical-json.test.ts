import { describe, expect, it } from "vitest";

import { canonicalJson, digestValue } from "./canonical-json.js";
import { L2Error } from "./types.js";

describe("EVF L2 canonical JSON", () => {
  it("sorts object keys by UTF-16 code units while preserving arrays and strings", () => {
    const value = { z: 1, a: { b: 2, a: 3 }, ordered: [" b ", "A", "é"] };
    expect(canonicalJson(value)).toBe('{"a":{"a":3,"b":2},"ordered":[" b ","A","é"],"z":1}');
    expect(digestValue(value)).toBe(digestValue({ ordered: [" b ", "A", "é"], a: { a: 3, b: 2 }, z: 1 }));
  });

  it.each([Number.NaN, Number.POSITIVE_INFINITY, Number.MAX_SAFE_INTEGER + 1, undefined])(
    "rejects unsupported digest material %s",
    (value) => {
      expect(() => canonicalJson({ value })).toThrowError(
        expect.objectContaining({ code: "CANONICALIZATION_UNSUPPORTED" }),
      );
    },
  );

  it("rejects cyclic objects", () => {
    const value: Record<string, unknown> = {};
    value.self = value;
    expect(() => canonicalJson(value)).toThrow(L2Error);
  });
});
