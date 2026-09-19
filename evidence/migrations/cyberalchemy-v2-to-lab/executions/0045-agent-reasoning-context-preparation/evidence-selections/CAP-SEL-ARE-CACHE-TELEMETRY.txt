import {freezeResult, isRecord, nonEmptyString} from "./canonical.mjs";

export const PROVIDER_CACHE_USAGE_SCHEMA = "are.provider-cache-usage/v1";
export const CACHE_TELEMETRY_EXTRACTION_SCHEMA = "are.cache-telemetry-extraction/v1";

function atPath(value, path) {
  let current = value;
  for (const segment of path.split(".")) {
    if (!isRecord(current) || !Object.hasOwn(current, segment)) return undefined;
    current = current[segment];
  }
  return current;
}

export function extractProviderCacheUsage(message, projection, profile = {}) {
  if (!isRecord(projection) || !nonEmptyString(projection.projection_digest) || !nonEmptyString(projection.exact_prefix_digest)) {
    return freezeResult({schema_version: CACHE_TELEMETRY_EXTRACTION_SCHEMA, ok: false, disposition: "block", reason_codes: ["cache-telemetry.projection-invalid"], authority_effect: "none"});
  }
  if (profile.enabled !== true) return freezeResult({schema_version: CACHE_TELEMETRY_EXTRACTION_SCHEMA, ok: true, disposition: "not-observed", reason_codes: ["cache-telemetry.extraction-disabled"], authority_effect: "none"});
  const paths = Array.isArray(profile.usage_paths) ? profile.usage_paths : [];
  const selectedPath = paths.find((path) => nonEmptyString(path) && isRecord(atPath(message, path)));
  if (!selectedPath) return freezeResult({schema_version: CACHE_TELEMETRY_EXTRACTION_SCHEMA, ok: true, disposition: "not-observed", reason_codes: ["cache-telemetry.provider-usage-unavailable"], authority_effect: "none"});
  const usage = atPath(message, selectedPath);
  const fields = profile.fields ?? {};
  const inputTokens = usage[fields.input_tokens ?? "input_tokens"];
  const cachedTokens = usage[fields.cached_input_tokens ?? "cached_input_tokens"];
  const latency = usage[fields.latency_ms ?? "latency_ms"];
  const baseline = usage[fields.baseline_latency_ms ?? "baseline_latency_ms"];
  if (!Number.isSafeInteger(inputTokens) || inputTokens < 0 || !Number.isSafeInteger(cachedTokens) || cachedTokens < 0 || cachedTokens > inputTokens) {
    return freezeResult({schema_version: CACHE_TELEMETRY_EXTRACTION_SCHEMA, ok: false, disposition: "block", reason_codes: ["cache-telemetry.provider-usage-invalid"], selected_path: selectedPath, authority_effect: "none"});
  }
  const providerUsage = freezeResult({
    schema_version: PROVIDER_CACHE_USAGE_SCHEMA,
    projection_digest: projection.projection_digest,
    exact_prefix_digest: projection.exact_prefix_digest,
    provider_ref: projection.stable_request_prefix?.provider_ref ?? null,
    model_ref: projection.stable_request_prefix?.model_ref ?? null,
    input_tokens: inputTokens,
    cached_input_tokens: cachedTokens,
    ...(typeof latency === "number" && Number.isFinite(latency) && latency >= 0 ? {latency_ms: latency} : {}),
    ...(typeof baseline === "number" && Number.isFinite(baseline) && baseline >= 0 ? {baseline_latency_ms: baseline} : {}),
  });
  return freezeResult({schema_version: CACHE_TELEMETRY_EXTRACTION_SCHEMA, ok: true, disposition: "observed", selected_path: selectedPath, provider_usage: providerUsage, authority_effect: "none"});
}

export function compareProviderCacheObservations(cold, warm) {
  const valid = [cold, warm].every((value) => isRecord(value) && ["observed-hit", "observed-miss"].includes(value.cache_hit_posture));
  if (!valid) return freezeResult({ok: false, disposition: "not-comparable", reason_codes: ["cache-telemetry.observations-required"], authority_effect: "none"});
  if (cold.projection_digest !== warm.projection_digest || cold.exact_prefix_digest !== warm.exact_prefix_digest) return freezeResult({ok: false, disposition: "not-comparable", reason_codes: ["cache-telemetry.prefix-identity-mismatch"], authority_effect: "none"});
  return freezeResult({ok: true, disposition: "compared", projection_digest: warm.projection_digest, exact_prefix_digest: warm.exact_prefix_digest, cached_input_token_delta: warm.observed_cached_input_tokens - cold.observed_cached_input_tokens, latency_delta_ms: typeof cold.observed_latency_ms === "number" && typeof warm.observed_latency_ms === "number" ? cold.observed_latency_ms - warm.observed_latency_ms : null, claim_ceiling: "Observed provider telemetry comparison only; no freshness, correctness, provenance, or authority claim.", authority_effect: "none"});
}
