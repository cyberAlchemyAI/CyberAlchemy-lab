import { createHash } from "node:crypto";
import { mkdtemp, readFile, readdir, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import {
  activeAdmission,
  referenceBytes,
  validDescriptor,
} from "../../kernel/contracts/fixtures/descriptor-contract-fixtures.js";
import { inspectFactoryKitPackage } from "../kit/inspect-kit-package.js";
import { publishExpectedRedKit } from "../kit/publish-expected-red-kit.js";

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const packageValue = (mapping: "mapped" | "candidate-mapped") => {
  const { admission_sha256: _ignored, ...base } = activeAdmission;
  const admissionBody = { ...base, mapping_status: mapping };
  return {
    schema_version: "FactoryKitPackage/v1",
    admission: { ...admissionBody, admission_sha256: sha256(JSON.stringify(admissionBody)) },
    descriptor: validDescriptor,
    reference_documents: referenceBytes,
    authority_effect: "none",
  };
};

describe("factory inspect/init", () => {
  it("publishes exactly six deterministic empty expected-red files", async () => {
    const root = await mkdtemp(resolve(tmpdir(), "domainspec-factory-init-"));
    try {
      const inspection = await inspectFactoryKitPackage(packageValue("mapped"));
      expect(inspection.readiness.code).toBe("READY");
      const output = resolve(root, "kit");
      const publication = await publishExpectedRedKit({ inspection, outputPath: output });
      expect(publication.file_count).toBe(6);
      const top = await readdir(output);
      expect(top.sort()).toEqual(["binding", "definition", "expected-red", "kit.json", "mutations", "obligations"]);
      const manifest = await readFile(resolve(output, "expected-red/manifest.json"), "utf8");
      expect(manifest).toContain('"business_outcomes": "absent"');
      expect(manifest).not.toMatch(/payout|return true|business rule body/iu);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });

  it("refuses candidate mapping without an escape flag", async () => {
    const root = await mkdtemp(resolve(tmpdir(), "domainspec-factory-candidate-init-"));
    try {
      const candidatePackage = packageValue("candidate-mapped");
      expect(candidatePackage.admission.maturity).toBe("active");
      const inspection = await inspectFactoryKitPackage(candidatePackage);
      expect(inspection).toMatchObject({
        result: "refused",
        readiness: {
          schema_version: "FactoryReadiness/v1",
          result: "refused",
          code: "REFUSED_CANDIDATE_MAPPING",
          descriptor_id: null,
          authority_effect: "none",
        },
        authority_effect: "none",
      });
      await expect(publishExpectedRedKit({ inspection, outputPath: resolve(root, "kit") }))
        .rejects.toThrow("REFUSED_CANDIDATE_MAPPING");
      expect(await readdir(root)).toEqual([]);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });
});
