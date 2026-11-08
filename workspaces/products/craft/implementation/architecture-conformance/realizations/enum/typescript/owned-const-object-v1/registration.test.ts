import { describe, expect, it } from "vitest";

import { readValidatedHandle } from "../../../../kernel/contracts/validated-handle.js";
import {
  registerRealizationV2,
  resolveRealizationV2,
} from "../../../../kernel/registry/realization-registry-v2.js";
import { createEnumTypeScriptRegistrationV2 } from "./registration.js";

const repositoryRoot = process.cwd().endsWith("projects/domainspec-v2/impl")
  ? process.cwd().slice(0, -"projects/domainspec-v2/impl".length - 1)
  : process.cwd();

describe("finite-vocabulary TypeScript owned-const-object v2 registration", () => {
  it("registers three distinct axes with exact provider documents", async () => {
    const first = await createEnumTypeScriptRegistrationV2(repositoryRoot);
    const second = await createEnumTypeScriptRegistrationV2(repositoryRoot);
    const descriptor = readValidatedHandle(first.descriptor);
    expect([
      descriptor.family_ref.id,
      descriptor.target_ref.id,
      descriptor.realization_ref.id,
    ]).toEqual(["family", "target", "realization"]);
    expect(new Set([
      descriptor.family_ref.sha256,
      descriptor.target_ref.sha256,
      descriptor.realization_ref.sha256,
    ]).size).toBe(3);
    expect(first.descriptor.source_sha256).toBe(second.descriptor.source_sha256);
    expect(first.descriptor.validated_refs).toHaveLength(10);
    expect(Object.keys(first.reference_documents)).toHaveLength(10);
    expect(resolveRealizationV2(
      first.registry,
      descriptor.descriptor_id,
    ).providers).toBe(first.providers);
  });

  it("keeps profile projection and generated-source observation separate", async () => {
    const registration = await createEnumTypeScriptRegistrationV2(repositoryRoot);
    expect(registration.providers.projector).not.toBe(
      registration.providers.realization,
    );
    expect(registration.providers.projector).toHaveProperty("derive");
    expect(registration.providers.projector).not.toHaveProperty("observe");
    expect(registration.providers.realization).toHaveProperty("observe");
    expect(registration.providers.realization).not.toHaveProperty("derive");
  });

  it("rejects duplicate descriptors and axis registrations", async () => {
    const registration = await createEnumTypeScriptRegistrationV2(repositoryRoot);
    await expect(Promise.resolve().then(() => registerRealizationV2(
      registration.registry,
      { descriptor: registration.descriptor, providers: registration.providers },
    ))).rejects.toMatchObject({ code: "FACTORY_REGISTRY_DESCRIPTOR_DUPLICATE" });
  });
});
