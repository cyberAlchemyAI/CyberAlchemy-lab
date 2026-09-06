export const EFFECT_CHANNELS = Object.freeze([
  "clock",
  "random",
  "environment",
  "filesystem",
  "network",
  "process",
  "global-cache",
  "delayed-lazy",
  "callback",
  "iterator-future",
  "finalizer-drop",
  "mutable-output",
] as const);

export type EffectChannelV1 = (typeof EFFECT_CHANNELS)[number];

export type LockedEffectObserverRefV1 = Readonly<{
  role: "independent-effect-observer";
  observer_id: string;
  observer_sha256: string;
  owner_ref: string;
  provider_id: string;
  provider_sha256: string;
}>;

export type EffectObservationV1 = Readonly<{
  schema_version: "EffectObservation/v1";
  observation_id: string;
  source_kind: "independent-owner-observation" | "mutated-effect-observation";
  target_ref: Readonly<{
    target_id: string;
    target_sha256: string;
  }>;
  observer_ref: LockedEffectObserverRefV1;
  channels: readonly Readonly<{
    channel: EffectChannelV1;
    coverage: "supported" | "unsupported";
    read_count: number;
    write_count: number;
    escape_count: number;
    deferred_count: number;
  }>[];
  result: Readonly<{
    consumption: "complete" | "incomplete";
    mutable_alias_observed: boolean;
  }>;
  quiescence: Readonly<{
    observed: boolean;
    pending_count: number;
  }>;
  authority_effect: "none";
  observation_sha256: string;
}>;

export type EffectObservationDiagnostic =
  | "EFFECT_OBSERVER_BINDING_MISMATCH"
  | "EFFECT_OBSERVER_SELF_ISSUED"
  | "EFFECT_CHANNEL_MISSING"
  | "EFFECT_CHANNEL_UNEXPECTED"
  | "EFFECT_CHANNEL_DUPLICATE"
  | "EFFECT_CHANNEL_UNSUPPORTED"
  | "EFFECT_READ_OBSERVED"
  | "EFFECT_WRITE_OBSERVED"
  | "EFFECT_ESCAPE_OBSERVED"
  | "EFFECT_DEFERRED_OBSERVED"
  | "EFFECT_RESULT_INCOMPLETE"
  | "EFFECT_MUTABLE_ALIAS_OBSERVED"
  | "EFFECT_QUIESCENCE_UNSUPPORTED"
  | "EFFECT_QUIESCENCE_VIOLATION";

export type EffectObservationEvaluationV1 = Readonly<{
  schema_version: "EffectObservationEvaluation/v1";
  evaluation_id: string;
  observation_ref: Readonly<{
    observation_id: string;
    observation_sha256: string;
  }>;
  observer_ref: LockedEffectObserverRefV1;
  result: "pass" | "fail";
  diagnostics: readonly EffectObservationDiagnostic[];
  coverage: Readonly<{
    required: number;
    supported: number;
    unsupported: number;
  }>;
  zero_effect_accounting: Readonly<{
    reads: number;
    writes: number;
    escapes: number;
    deferred: number;
  }>;
  claim: "transport-evaluation-only-no-runtime-interception";
  authority_effect: "none";
}>;

export const DECLARED_READ_LIFECYCLE_PATHS = Object.freeze([
  "return",
  "iterate-or-await",
  "cancel",
  "close",
  "dispose",
  "finalizer",
  "quiescence",
] as const);

export type DeclaredReadLifecyclePathV1 =
  (typeof DECLARED_READ_LIFECYCLE_PATHS)[number];

export type DeclaredReadTargetV1 = Readonly<{
  target_id: string;
  channel: EffectChannelV1;
}>;

export type DeclaredReadLifecycleObservationV1 = Readonly<{
  schema_version: "DeclaredReadLifecycleObservation/v1";
  observation_id: string;
  source_kind:
    | "independent-owner-observation"
    | "mutated-declared-read-observation";
  target_ref: Readonly<{
    target_id: string;
    target_sha256: string;
  }>;
  observer_ref: LockedEffectObserverRefV1;
  declared_read_attempts: readonly Readonly<{
    ordinal: number;
    target_id: string;
    channel: EffectChannelV1;
    lifecycle_path: DeclaredReadLifecyclePathV1;
    outcome: "success" | "declared-failure";
  }>[];
  lifecycle_paths: readonly Readonly<{
    lifecycle_path: DeclaredReadLifecyclePathV1;
    coverage: "supported" | "unsupported";
  }>[];
  effect_observation: EffectObservationV1;
  source_support: "supported-static" | "unsupported-dynamic-or-generated";
  write_then_restore_observed: boolean;
  authority_effect: "none";
  observation_sha256: string;
}>;

export type DeclaredReadLifecycleDiagnostic =
  | "DECLARED_READ_OBSERVER_BINDING_MISMATCH"
  | "DECLARED_READ_OBSERVER_SELF_ISSUED"
  | "DECLARED_READ_TARGET_BINDING_MISMATCH"
  | "DECLARED_READ_LEDGER_MISMATCH"
  | "DECLARED_READ_CHANNEL_MISSING"
  | "DECLARED_READ_CHANNEL_DUPLICATE"
  | "DECLARED_READ_CHANNEL_UNSUPPORTED"
  | "DECLARED_READ_COUNT_MISMATCH"
  | "DECLARED_READ_WRITE_OBSERVED"
  | "DECLARED_READ_ESCAPE_OBSERVED"
  | "DECLARED_READ_DEFERRED_OBSERVED"
  | "DECLARED_READ_RESULT_INCOMPLETE"
  | "DECLARED_READ_MUTABLE_ALIAS_OBSERVED"
  | "DECLARED_READ_LIFECYCLE_MISSING"
  | "DECLARED_READ_LIFECYCLE_DUPLICATE"
  | "DECLARED_READ_LIFECYCLE_UNSUPPORTED"
  | "DECLARED_READ_QUIESCENCE_UNSUPPORTED"
  | "DECLARED_READ_QUIESCENCE_VIOLATION"
  | "DECLARED_READ_WRITE_THEN_RESTORE_OBSERVED"
  | "DECLARED_READ_SOURCE_UNSUPPORTED";

export type DeclaredReadLifecycleEvaluationV1 = Readonly<{
  schema_version: "DeclaredReadLifecycleEvaluation/v1";
  evaluation_id: string;
  observation_ref: Readonly<{
    observation_id: string;
    observation_sha256: string;
  }>;
  target_ref: Readonly<{
    target_id: string;
    target_sha256: string;
  }>;
  observer_ref: LockedEffectObserverRefV1;
  result: "pass" | "fail";
  diagnostics: readonly DeclaredReadLifecycleDiagnostic[];
  coverage: Readonly<{
    effect_channels_required: number;
    effect_channels_supported: number;
    effect_channels_unsupported: number;
    lifecycle_paths_required: number;
    lifecycle_paths_supported: number;
    lifecycle_paths_unsupported: number;
  }>;
  read_accounting: Readonly<{
    declared: number;
    observed: number;
  }>;
  forbidden_accounting: Readonly<{
    writes: number;
    escapes: number;
    deferred: number;
  }>;
  claim: "declared-read-transport-evaluation-no-runtime-interception";
  authority_effect: "none";
}>;
