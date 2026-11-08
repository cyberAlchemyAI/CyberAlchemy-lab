import type { CompiledProjectGraph } from "../input/project-model.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { validateApplicationIntegrationBinding } from "./application-binding-v1.js";
import type { IntegrationGenerationSourceV2 } from "./generation-v2.js";
import { REQUIRED_PROVIDER_CAPABILITIES, validateProviderPackSelectionV1, providerPackSelectionSha256, ProviderPackSelectionError } from "./provider-pack-v1.js";

const kinds = { persistence: "postgresql", messaging: "managed-broker", outbound_http: "http-client", inbound_http: "http-server" } as const;
type Role = keyof typeof kinds;
function fail(pointer: string, message: string): never {
  throw new ProviderPackSelectionError("DS_APPLICATION_RUNTIME_PROVIDER", pointer, message);
}
function freeze<T>(value: T): T {
  if (value && typeof value === "object" && !Object.isFrozen(value)) { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
}

/** Joins every actual kernel binding, not merely a compatible unused profile. */
export function compileApplicationRuntimeBindingV1(graph: CompiledProjectGraph, source: IntegrationGenerationSourceV2, providerInput: unknown) {
  const providers = validateProviderPackSelectionV1(providerInput);
  const binding = validateApplicationIntegrationBinding(graph, source);
  const rows = [];
  for (const lane of ["persistence", "messaging", "external_api"] as const) {
    const kernel = source[lane].integration_kernel;
    for (const item of kernel.integration_bindings) {
      const pointer = `/${lane}/integration_kernel/integration_bindings/${item.binding_id}`;
      const role: Role = lane === "persistence" ? "persistence" : lane === "messaging" ? "messaging"
        : item.direction === "inbound" ? "inbound_http" : item.direction === "outbound" ? "outbound_http"
        : fail(pointer, "HTTP runtime binding requires an explicit direction");
      const expectedConcern = lane === "external_api" ? "external-api" : lane;
      const realization = kernel.provider_realizations.find(r => r.realization_id === item.provider_realization_ref);
      const profile = kernel.provider_profiles.find(p => p.profile_id === realization?.provider_profile_ref);
      if (!realization || !profile || item.concern !== expectedConcern || profile.concern !== expectedConcern
        || profile.provider_kind !== kinds[role] || !REQUIRED_PROVIDER_CAPABILITIES[role].every(c => profile.capability_set.includes(c))) {
        fail(pointer, "the selected realization must resolve to the runtime pack's exact provider kind and required capabilities");
      }
      rows.push({ partition: lane, binding_ref: item.binding_id, logical_boundary_ref: item.logical_boundary_ref,
        provider_realization_ref: realization.realization_id, provider_profile_ref: profile.profile_id,
        role, provider: providers.providers[role] });
    }
  }
  rows.sort((a, b) => a.partition.localeCompare(b.partition) || a.binding_ref.localeCompare(b.binding_ref));
  const body = { schema_version: "domainspec.application-runtime-binding/v1-candidate",
    binding, provider_selection_sha256: providerPackSelectionSha256(providers), language: providers.language,
    providers: rows, runtime_guarantees_observed: false, authority_effect: "none" };
  return freeze({ ...body, runtime_binding_sha256: sha256(canonicalJson(body)) });
}
