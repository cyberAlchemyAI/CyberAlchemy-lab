import { describe, expect, it } from "vitest";

import { admitMetaTypeDescriptorV2 } from "../codecs/decode-meta-type-descriptor-v2.js";
import { decodeProviderEnvelopeV2 } from "../codecs/decode-provider-envelope-v2.js";
import type { ExactRefResolver } from "./exact-ref.js";
import {
  activeAdmission,
  candidateAdmission,
  collapsedAxesDescriptor,
  contractBytes,
  maturityInflatedDescriptor,
  missingMappingAdmission,
  referenceBytes,
  staleProviderEnvelope,
  validDescriptor,
  validProviderEnvelope,
} from "./fixtures/descriptor-contract-fixtures.js";
import type {
  MetaTypeAdmissionV2,
  MetaTypeDescriptorV2,
} from "./meta-type-descriptor-v2.js";
import {
  readValidatedHandle,
  type ValidatedHandle,
} from "./validated-handle.js";

const resolveRef: ExactRefResolver = (ref) =>
  referenceBytes[ref.id as keyof typeof referenceBytes] ?? "";

describe("generic v2 descriptor and provider contracts", () => {
  it("validates exact descriptor bytes and every referenced byte", async () => {
    const handle = await admitMetaTypeDescriptorV2(
      contractBytes(validDescriptor),
      contractBytes(activeAdmission),
      resolveRef,
    );
    expect(readValidatedHandle(handle).descriptor_id).toBe(
      validDescriptor.descriptor_id,
    );
    expect(handle.validated_refs).toHaveLength(10);
  });

  it("validates provider output, envelope, and input reference digests", async () => {
    const handle = await decodeProviderEnvelopeV2(
      contractBytes(validProviderEnvelope),
      resolveRef,
    );
    expect(readValidatedHandle(handle).provider_id).toBe(
      validProviderEnvelope.provider_id,
    );
    expect(handle.validated_refs).toEqual([
      { id: "criterion", sha256: validProviderEnvelope.input_refs[0]!.sha256 },
    ]);
  });
  it("keeps family, target, and realization as independent axes", async () => {
    await expect(
      admitMetaTypeDescriptorV2(
        contractBytes(collapsedAxesDescriptor),
        contractBytes(activeAdmission),
        resolveRef,
      ),
    ).rejects.toThrow("FACTORY_DESCRIPTOR_AXIS_COLLAPSE");
  });

  it("rejects maturity inflation against the admitted authority snapshot", async () => {
    await expect(
      admitMetaTypeDescriptorV2(
        contractBytes(maturityInflatedDescriptor),
        contractBytes(candidateAdmission),
        resolveRef,
      ),
    ).rejects.toThrow("FACTORY_DESCRIPTOR_MATURITY_INFLATION");
  });

  it("rejects an absent architecture mapping before provider execution", async () => {
    await expect(
      admitMetaTypeDescriptorV2(
        contractBytes(validDescriptor),
        contractBytes(missingMappingAdmission),
        resolveRef,
      ),
    ).rejects.toThrow("FACTORY_DESCRIPTOR_MAPPING_MISSING");
  });

  it("rejects a provider envelope with a stale output digest", async () => {
    await expect(
      decodeProviderEnvelopeV2(
        contractBytes(staleProviderEnvelope),
        resolveRef,
      ),
    ).rejects.toThrow("FACTORY_PROVIDER_OUTPUT_DIGEST_STALE");
  });

  it("rejects a caller-asserted validated handle", () => {
    const asserted = {
      schema_version: "ValidatedHandle/v2",
      value: activeAdmission,
      source_sha256: activeAdmission.admission_sha256,
      validated_refs: [],
    } as unknown as ValidatedHandle<MetaTypeAdmissionV2>;
    expect(() => readValidatedHandle(asserted)).toThrow(
      "FACTORY_HANDLE_NOT_VALIDATED",
    );
  });

  it("rejects caller-asserted document and reference digests", async () => {
    const staleAdmission = {
      ...activeAdmission,
      admission_sha256: "0".repeat(64),
    };
    await expect(
      admitMetaTypeDescriptorV2(
        contractBytes(validDescriptor),
        contractBytes(staleAdmission),
        resolveRef,
      ),
    ).rejects.toThrow("FACTORY_ADMISSION_DIGEST_STALE");

    await expect(
      admitMetaTypeDescriptorV2(
        contractBytes(validDescriptor),
        contractBytes(activeAdmission),
        (ref) => ref.id === "family" ? "{}" : resolveRef(ref),
      ),
    ).rejects.toThrow("FACTORY_REF_DIGEST_STALE");
  });

  it("rejects incompatible schemas and stale envelope digests", async () => {
    await expect(
      admitMetaTypeDescriptorV2(
        contractBytes({
          ...validDescriptor,
          schema_version: "MetaTypeDescriptor/v3",
        }),
        contractBytes(activeAdmission),
        resolveRef,
      ),
    ).rejects.toThrow("FACTORY_DESCRIPTOR_SCHEMA_INVALID");

    await expect(
      decodeProviderEnvelopeV2(
        contractBytes({
          ...validProviderEnvelope,
          envelope_sha256: "0".repeat(64),
        }),
        resolveRef,
      ),
    ).rejects.toThrow("FACTORY_PROVIDER_ENVELOPE_DIGEST_STALE");
  });
});
