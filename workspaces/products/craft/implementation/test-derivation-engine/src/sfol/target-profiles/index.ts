export const SFOL_TARGET_PROFILE_REGISTRY_VERSION = "domainspec-sfol-target-profile-registry/v1" as const;

export interface SfolTargetProfile {
  readonly profile_id: string;
  readonly profile_version: "1.0.0";
  readonly adapter_kind: "pure-function" | "effect-operation";
  readonly runner_boundary: "in-process-pure" | "contained-effect";
  readonly semantic_observation: "typed-return" | "validated-effect-trace";
  readonly effect_authority: "none" | "separately-required";
}

export const SFOL_TARGET_PROFILES: readonly SfolTargetProfile[] = Object.freeze([
  Object.freeze({ profile_id: "domainspec.sfol.target.pure-function", profile_version: "1.0.0", adapter_kind: "pure-function", runner_boundary: "in-process-pure", semantic_observation: "typed-return", effect_authority: "none" }),
  Object.freeze({ profile_id: "domainspec.sfol.target.effect-operation", profile_version: "1.0.0", adapter_kind: "effect-operation", runner_boundary: "contained-effect", semantic_observation: "validated-effect-trace", effect_authority: "separately-required" }),
]);

export function resolveSfolTargetProfile(profileId: string, profileVersion: string): SfolTargetProfile | null {
  return SFOL_TARGET_PROFILES.find((profile) => profile.profile_id === profileId && profile.profile_version === profileVersion) ?? null;
}
