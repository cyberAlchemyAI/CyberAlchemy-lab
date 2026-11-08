import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  computeEnumDefinitionSha256,
  validateEnumDefinitionSnapshot,
} from "../../../realization/contracts/enum-definition-snapshot.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const fixturePath = resolve(
  repositoryRoot,
  "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
);

const loadFixture = async (): Promise<Record<string, unknown>> =>
  JSON.parse(await readFile(fixturePath, "utf8")) as Record<string, unknown>;

const withDigest = (value: Record<string, unknown>): Record<string, unknown> => {
  const copy = structuredClone(value);
  delete copy.definition_sha256;
  return {
    ...copy,
    definition_sha256: computeEnumDefinitionSha256(copy as never),
  };
};

const codeOf = (operation: () => unknown): string => {
  try {
    operation();
    return "NO_ERROR";
  } catch (error) {
    return String((error as { code?: string }).code);
  }
};

describe("EnumDefinitionSnapshot/v1", () => {
  it("validates, canonicalizes, and recursively freezes the OrderStatus snapshot", async () => {
    const snapshot = validateEnumDefinitionSnapshot(await loadFixture());
    expect(snapshot.members).toEqual([
      { member_id: "status.paid", semantic_value: "paid" },
      { member_id: "status.pending", semantic_value: "pending" },
    ]);
    const { definition_sha256: _, ...withoutDigest } = snapshot;
    expect(snapshot.definition_sha256).toBe(computeEnumDefinitionSha256(withoutDigest));
    expect(Object.isFrozen(snapshot)).toBe(true);
    expect(Object.isFrozen(snapshot.members)).toBe(true);
    expect(Object.isFrozen(snapshot.members[0])).toBe(true);
  });

  it("normalizes member order without changing the semantic digest", async () => {
    const fixture = await loadFixture();
    fixture.members = [...fixture.members as unknown[]].reverse();
    const permuted = validateEnumDefinitionSnapshot(withDigest(fixture));
    const positive = validateEnumDefinitionSnapshot(await loadFixture());
    expect(permuted).toEqual(positive);
  });

  it("kills the closed hostile matrix with exact codes", async () => {
    const positive = await loadFixture();
    const members = () => structuredClone(positive.members) as Array<Record<string, unknown>>;
    const cases: Array<readonly [string, Record<string, unknown>]> = [
      ["ARCH_ENUM_DEFINITION_SHAPE_INVALID", withDigest({ ...positive, language: "typescript" })],
      ["ARCH_ENUM_DEFINITION_IDENTITY_INVALID", withDigest({ ...positive, definition_id: "" })],
      ["ARCH_ENUM_DEFINITION_MEMBERS_EMPTY", withDigest({ ...positive, members: [] })],
      ["ARCH_ENUM_DEFINITION_MEMBER_ID_INVALID", withDigest({
        ...positive,
        members: [{ ...members()[0], member_id: "" }, members()[1]],
      })],
      ["ARCH_ENUM_DEFINITION_MEMBER_VALUE_INVALID", withDigest({
        ...positive,
        members: [{ ...members()[0], semantic_value: "" }, members()[1]],
      })],
      ["ARCH_ENUM_DEFINITION_MEMBER_ID_DUPLICATE", withDigest({
        ...positive,
        members: [members()[0], { ...members()[1], member_id: members()[0]?.member_id }],
      })],
      ["ARCH_ENUM_DEFINITION_MEMBER_VALUE_DUPLICATE", withDigest({
        ...positive,
        members: [members()[0], {
          ...members()[1],
          semantic_value: members()[0]?.semantic_value,
        }],
      })],
      ["ARCH_ENUM_DEFINITION_AUTHORITY_REF_INVALID", withDigest({ ...positive, authority_ref: "" })],
      ["ARCH_ENUM_DEFINITION_AUTHORITY_STATUS_INVALID", withDigest({
        ...positive,
        authority_status: "unknown",
      })],
      ["ARCH_ENUM_DEFINITION_AUTHORITY_INFLATION", withDigest({
        ...positive,
        authority_status: "canonical-promoted",
      })],
    ];
    for (const [expected, candidate] of cases) {
      expect(codeOf(() => validateEnumDefinitionSnapshot(candidate))).toBe(expected);
    }
    expect(codeOf(() => validateEnumDefinitionSnapshot({
      ...positive,
      definition_sha256: "not-a-digest",
    }))).toBe("ARCH_ENUM_DEFINITION_DIGEST_INVALID");
    expect(codeOf(() => validateEnumDefinitionSnapshot({
      ...positive,
      definition_sha256: "0".repeat(64),
    }))).toBe("ARCH_ENUM_DEFINITION_DIGEST_STALE");
  });
});
