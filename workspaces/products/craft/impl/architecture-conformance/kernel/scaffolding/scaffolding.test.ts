import { createHash } from "node:crypto";

import { describe, expect, it } from "vitest";

import type { MetaTypeAdmissionV2 } from "../contracts/meta-type-descriptor-v2.js";
import {
  createValidatedHandle,
  type ValidatedHandle,
} from "../contracts/validated-handle.js";
import {
  activeAdmission,
  validDescriptor,
} from "../contracts/fixtures/descriptor-contract-fixtures.js";
import { classifyFactoryReadiness } from "./readiness-classifier.js";
import { scaffoldExpectedRedKit } from "./scaffold-realization-kit.js";

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const admission = (
  overrides: Partial<Omit<MetaTypeAdmissionV2, "admission_sha256">> = {},
): MetaTypeAdmissionV2 => {
  const { admission_sha256: _ignored, ...base } = activeAdmission;
  const body = { ...base, mapping_status: "mapped" as const, ...overrides };
  return Object.freeze({ ...body, admission_sha256: sha256(JSON.stringify(body)) });
};
const handle = () => createValidatedHandle({
  value: validDescriptor,
  source_sha256: validDescriptor.descriptor_sha256,
  validated_refs: [],
});

describe("fail-closed expected-red kit scaffolder", () => {
  it("creates the same empty skeleton for the same admitted descriptor", () => {
    const descriptor = handle();
    const readiness = classifyFactoryReadiness({ admission: admission(), descriptor });
    expect(readiness.code).toBe("READY");
    const first = scaffoldExpectedRedKit({ readiness, descriptor });
    const second = scaffoldExpectedRedKit({ readiness, descriptor });
    expect(first).toEqual(second);
    expect(first.files).toHaveLength(6);
    expect(first.files.map(({ path }) => path)).toEqual([
      "binding/empty.json", "definition/empty.json", "expected-red/manifest.json",
      "kit.json", "mutations/empty.json", "obligations/empty.json",
    ]);
    const content = first.files.map(({ content }) => content).join("\n");
    expect(content).not.toMatch(/payout|paid|return true|business rule body/iu);
    expect(content).toContain('"business_outcomes": "absent"');
  });

  it.each([
    ["unmapped", { mapping_status: "profiled-unmapped", architecture_type_ref: null }, "REFUSED_UNMAPPED"],
    ["candidate mapping", { mapping_status: "candidate-mapped" }, "REFUSED_CANDIDATE_MAPPING"],
    ["candidate", { maturity: "candidate" }, "REFUSED_CANDIDATE"],
    ["deferred", { maturity: "deferred" }, "REFUSED_DEFERRED"],
    ["superseded", { maturity: "superseded" }, "REFUSED_SUPERSEDED"],
  ] as const)("refuses %s admission", (_name, overrides, code) => {
    const descriptor = handle();
    const readiness = classifyFactoryReadiness({
      admission: admission(overrides as Partial<Omit<MetaTypeAdmissionV2, "admission_sha256">>),
      descriptor,
    });
    expect(readiness.code).toBe(code);
    expect(() => scaffoldExpectedRedKit({ readiness, descriptor }))
      .toThrow("FACTORY_SCAFFOLD_NOT_READY");
  });

  it("refuses stale admission, stale descriptor, and forged handles", () => {
    const descriptor = handle();
    const staleAdmission = { ...admission(), admission_sha256: "0".repeat(64) };
    expect(classifyFactoryReadiness({
      admission: staleAdmission, descriptor,
    }).code).toBe("REFUSED_STALE");
    const staleDescriptor = createValidatedHandle({
      value: { ...validDescriptor, claim_ceiling: "changed without digest" },
      source_sha256: validDescriptor.descriptor_sha256,
      validated_refs: [],
    });
    expect(classifyFactoryReadiness({
      admission: admission(), descriptor: staleDescriptor,
    }).code).toBe("REFUSED_STALE");
    const forged = { ...descriptor } as ValidatedHandle<typeof validDescriptor>;
    expect(() => classifyFactoryReadiness({
      admission: admission(), descriptor: forged,
    })).toThrow("FACTORY_HANDLE_NOT_VALIDATED");
  });
});
