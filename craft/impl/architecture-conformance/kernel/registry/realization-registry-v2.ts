import type { MetaTypeDescriptorV2 } from "../contracts/meta-type-descriptor-v2.js";
import {
  readValidatedHandle,
  type ValidatedHandle,
} from "../contracts/validated-handle.js";

const PROVIDER_IMPLEMENTATION_KEYS = [
  "projector",
  "definition_or_binding",
  "obligations",
  "evaluator",
  "mutations",
  "family",
  "target",
  "realization",
] as const;

export type ProviderImplementationKey =
  (typeof PROVIDER_IMPLEMENTATION_KEYS)[number];

export type ProviderImplementationsV2 = Readonly<
  Record<ProviderImplementationKey, object>
>;

export type RealizationRegistrationV2<
  TProviders extends ProviderImplementationsV2 = ProviderImplementationsV2,
> = Readonly<{
  descriptor: ValidatedHandle<MetaTypeDescriptorV2>;
  providers: TProviders;
}>;

export type RealizationRegistryV2 = Readonly<{
  schema_version: "RealizationRegistry/v2";
  entries: ReadonlyMap<string, RealizationRegistrationV2>;
  axis_keys: ReadonlySet<string>;
  authority_effect: "none";
}>;

const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};

const exactProviderKeys = (providers: ProviderImplementationsV2): boolean => {
  const actual = Object.keys(providers).sort();
  const expected = [...PROVIDER_IMPLEMENTATION_KEYS].sort();
  return actual.length === expected.length &&
    actual.every((key, index) => key === expected[index]) &&
    Object.values(providers).every((provider) =>
      provider !== null && typeof provider === "object");
};

const axisKey = (descriptor: MetaTypeDescriptorV2): string => [
  descriptor.meta_type_ref,
  descriptor.family_ref.id,
  descriptor.target_ref.id,
  descriptor.realization_ref.id,
].join("\u0000");

export const createRealizationRegistryV2 = (): RealizationRegistryV2 =>
  Object.freeze({
    schema_version: "RealizationRegistry/v2" as const,
    entries: new Map<string, RealizationRegistrationV2>(),
    axis_keys: new Set<string>(),
    authority_effect: "none" as const,
  });

export const registerRealizationV2 = <
  TProviders extends ProviderImplementationsV2,
>(
  registry: RealizationRegistryV2,
  registration: RealizationRegistrationV2<TProviders>,
): RealizationRegistryV2 => {
  const descriptor = readValidatedHandle(registration.descriptor);
  if (!exactProviderKeys(registration.providers)) {
    return fail("FACTORY_REGISTRY_PROVIDER_SET_INVALID");
  }
  const key = axisKey(descriptor);
  if (registry.entries.has(descriptor.descriptor_id)) {
    return fail("FACTORY_REGISTRY_DESCRIPTOR_DUPLICATE");
  }
  if (registry.axis_keys.has(key)) return fail("FACTORY_REGISTRY_AXIS_DUPLICATE");
  const entries = new Map(registry.entries);
  entries.set(descriptor.descriptor_id, Object.freeze(registration));
  return Object.freeze({
    ...registry,
    entries,
    axis_keys: new Set([...registry.axis_keys, key]),
  });
};

export const resolveRealizationV2 = <
  TProviders extends ProviderImplementationsV2,
>(
  registry: RealizationRegistryV2,
  descriptorId: string,
): RealizationRegistrationV2<TProviders> => {
  const registration = registry.entries.get(descriptorId);
  return registration === undefined
    ? fail("FACTORY_REGISTRY_DESCRIPTOR_MISSING")
    : registration as RealizationRegistrationV2<TProviders>;
};
