import {createHash} from "node:crypto";

import {
  DECLARED_READ_LIFECYCLE_PATHS,
  EFFECT_CHANNELS,
  type DeclaredReadLifecycleDiagnostic,
  type DeclaredReadLifecycleEvaluationV1,
  type DeclaredReadLifecycleObservationV1,
  type DeclaredReadLifecyclePathV1,
  type DeclaredReadTargetV1,
  type EffectChannelV1,
  type EffectObservationDiagnostic,
  type EffectObservationEvaluationV1,
  type EffectObservationV1,
  type LockedEffectObserverRefV1,
} from "./contracts.js";

const SHA256 = /^[a-f0-9]{64}$/u;
const IDENTIFIER = /^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$/u;
const CHANNEL_SET = new Set<string>(EFFECT_CHANNELS);
const CHANNEL_ORDER = new Map<string, number>(
  EFFECT_CHANNELS.map((channel, index) => [channel, index]),
);
const LIFECYCLE_SET = new Set<string>(DECLARED_READ_LIFECYCLE_PATHS);
const LIFECYCLE_ORDER = new Map<string, number>(
  DECLARED_READ_LIFECYCLE_PATHS.map((path, index) => [path, index]),
);

const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const canonicalValue = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(canonicalValue);
  if (!isRecord(value)) return value;
  return Object.fromEntries(Object.entries(value)
    .sort(([left], [right]) => compareUtf8(left, right))
    .map(([key, child]) => [key, canonicalValue(child)]));
};
const deepFreeze = <Value>(value: Value): Readonly<Value> => {
  if (value === null || typeof value !== "object" || Object.isFrozen(value)) {
    return value;
  }
  Object.freeze(value);
  for (const child of Object.values(value)) deepFreeze(child);
  return value;
};
const exactKeys = (
  value: Record<string, unknown>,
  expectedKeys: readonly string[],
  label: string,
): void => {
  const observed = Object.keys(value).sort(compareUtf8);
  const expected = [...expectedKeys].sort(compareUtf8);
  if (JSON.stringify(observed) !== JSON.stringify(expected)) {
    throw new Error(`EFFECT_OBSERVATION_INVALID:${label}-shape`);
  }
};
const validIdentifier = (value: unknown): value is string =>
  typeof value === "string" && IDENTIFIER.test(value);
const validCount = (value: unknown): value is number =>
  Number.isSafeInteger(value) && Number(value) >= 0;

export const canonicalEffectObservationJson = (value: unknown): string =>
  JSON.stringify(canonicalValue(value));

export const sha256EffectObservationBytes = (
  value: string | Uint8Array,
): string => createHash("sha256").update(value).digest("hex");

type EffectObservationBodyV1 = Omit<EffectObservationV1, "observation_sha256">;

const validateObserverRef: (
  value: unknown,
) => asserts value is LockedEffectObserverRefV1 = (value) => {
  if (!isRecord(value)) throw new Error("EFFECT_OBSERVATION_INVALID:observer-ref");
  exactKeys(value, [
    "role",
    "observer_id",
    "observer_sha256",
    "owner_ref",
    "provider_id",
    "provider_sha256",
  ], "observer-ref");
  if (value.role !== "independent-effect-observer" ||
      !validIdentifier(value.observer_id) || !SHA256.test(String(value.observer_sha256)) ||
      !validIdentifier(value.owner_ref) || !validIdentifier(value.provider_id) ||
      !SHA256.test(String(value.provider_sha256))) {
    throw new Error("EFFECT_OBSERVATION_INVALID:observer-ref");
  }
};

const validateBody: (
  value: unknown,
) => asserts value is EffectObservationBodyV1 = (value) => {
  if (!isRecord(value)) throw new Error("EFFECT_OBSERVATION_INVALID:observation");
  exactKeys(value, [
    "schema_version",
    "observation_id",
    "source_kind",
    "target_ref",
    "observer_ref",
    "channels",
    "result",
    "quiescence",
    "authority_effect",
  ], "observation");
  if (value.schema_version !== "EffectObservation/v1" ||
      !validIdentifier(value.observation_id) ||
      (value.source_kind !== "independent-owner-observation" &&
        value.source_kind !== "mutated-effect-observation") ||
      value.authority_effect !== "none") {
    throw new Error("EFFECT_OBSERVATION_INVALID:observation");
  }
  if (!isRecord(value.target_ref)) {
    throw new Error("EFFECT_OBSERVATION_INVALID:target-ref");
  }
  exactKeys(value.target_ref, ["target_id", "target_sha256"], "target-ref");
  if (!validIdentifier(value.target_ref.target_id) ||
      !SHA256.test(String(value.target_ref.target_sha256))) {
    throw new Error("EFFECT_OBSERVATION_INVALID:target-ref");
  }
  validateObserverRef(value.observer_ref);
  if (!Array.isArray(value.channels)) {
    throw new Error("EFFECT_OBSERVATION_INVALID:channels");
  }
  for (const channel of value.channels) {
    if (!isRecord(channel)) throw new Error("EFFECT_OBSERVATION_INVALID:channel");
    exactKeys(channel, [
      "channel",
      "coverage",
      "read_count",
      "write_count",
      "escape_count",
      "deferred_count",
    ], "channel");
    if (!CHANNEL_SET.has(String(channel.channel)) ||
        (channel.coverage !== "supported" && channel.coverage !== "unsupported") ||
        !validCount(channel.read_count) || !validCount(channel.write_count) ||
        !validCount(channel.escape_count) || !validCount(channel.deferred_count)) {
      throw new Error("EFFECT_OBSERVATION_INVALID:channel");
    }
  }
  if (!isRecord(value.result)) throw new Error("EFFECT_OBSERVATION_INVALID:result");
  exactKeys(value.result, ["consumption", "mutable_alias_observed"], "result");
  if ((value.result.consumption !== "complete" &&
      value.result.consumption !== "incomplete") ||
      typeof value.result.mutable_alias_observed !== "boolean") {
    throw new Error("EFFECT_OBSERVATION_INVALID:result");
  }
  if (!isRecord(value.quiescence)) {
    throw new Error("EFFECT_OBSERVATION_INVALID:quiescence");
  }
  exactKeys(value.quiescence, ["observed", "pending_count"], "quiescence");
  if (typeof value.quiescence.observed !== "boolean" ||
      !validCount(value.quiescence.pending_count)) {
    throw new Error("EFFECT_OBSERVATION_INVALID:quiescence");
  }
};

const observationBody = (
  observation: EffectObservationV1,
): EffectObservationBodyV1 => {
  const {observation_sha256: _digest, ...body} = observation;
  return body;
};

export const mintEffectObservationV1 = (
  input: EffectObservationBodyV1,
): EffectObservationV1 => {
  validateBody(input);
  const channels = [...input.channels].sort((left, right) =>
    (CHANNEL_ORDER.get(left.channel) ?? Number.MAX_SAFE_INTEGER) -
    (CHANNEL_ORDER.get(right.channel) ?? Number.MAX_SAFE_INTEGER));
  const body = {
    ...input,
    target_ref: {...input.target_ref},
    observer_ref: {...input.observer_ref},
    channels: channels.map((channel) => ({...channel})),
    result: {...input.result},
    quiescence: {...input.quiescence},
  } satisfies EffectObservationBodyV1;
  const observation = {
    ...body,
    observation_sha256: sha256EffectObservationBytes(
      canonicalEffectObservationJson(body),
    ),
  } satisfies EffectObservationV1;
  return deepFreeze(observation) as EffectObservationV1;
};

export const decodeEffectObservationV1 = (
  bytes: string,
): EffectObservationV1 => {
  let decoded: unknown;
  try {
    decoded = JSON.parse(bytes);
  } catch {
    throw new Error("EFFECT_OBSERVATION_INVALID:json");
  }
  if (!isRecord(decoded)) throw new Error("EFFECT_OBSERVATION_INVALID:observation");
  exactKeys(decoded, [
    "schema_version",
    "observation_id",
    "source_kind",
    "target_ref",
    "observer_ref",
    "channels",
    "result",
    "quiescence",
    "authority_effect",
    "observation_sha256",
  ], "observation");
  const {observation_sha256, ...body} = decoded;
  if (typeof observation_sha256 !== "string" || !SHA256.test(observation_sha256)) {
    throw new Error("EFFECT_OBSERVATION_INVALID:digest");
  }
  const minted = mintEffectObservationV1(body as EffectObservationBodyV1);
  if (minted.observation_sha256 !== observation_sha256) {
    throw new Error("EFFECT_OBSERVATION_DIGEST_STALE");
  }
  return minted;
};

const sameObserverRef = (
  left: LockedEffectObserverRefV1,
  right: LockedEffectObserverRefV1,
): boolean => canonicalEffectObservationJson(left) ===
  canonicalEffectObservationJson(right);

export const evaluateEffectObservationV1 = (input: Readonly<{
  locked_observer_ref: LockedEffectObserverRefV1;
  observation: EffectObservationV1;
}>): EffectObservationEvaluationV1 => {
  const {locked_observer_ref: locked, observation} = input;
  const diagnostics: EffectObservationDiagnostic[] = [];
  const expectedDigest = sha256EffectObservationBytes(
    canonicalEffectObservationJson(observationBody(observation)),
  );
  if (expectedDigest !== observation.observation_sha256) {
    throw new Error("EFFECT_OBSERVATION_DIGEST_STALE");
  }
  if (!sameObserverRef(locked, observation.observer_ref)) {
    diagnostics.push("EFFECT_OBSERVER_BINDING_MISMATCH");
  }
  if (locked.owner_ref === locked.provider_id ||
      observation.observer_ref.owner_ref === observation.observer_ref.provider_id) {
    diagnostics.push("EFFECT_OBSERVER_SELF_ISSUED");
  }

  const byChannel = new Map<EffectChannelV1, EffectObservationV1["channels"]>();
  for (const channel of EFFECT_CHANNELS) byChannel.set(channel, []);
  for (const entry of observation.channels as readonly Readonly<{
    channel: string;
    coverage: "supported" | "unsupported";
    read_count: number;
    write_count: number;
    escape_count: number;
    deferred_count: number;
  }>[]) {
    if (!CHANNEL_SET.has(entry.channel)) {
      diagnostics.push("EFFECT_CHANNEL_UNEXPECTED");
      continue;
    }
    const channel = entry.channel as EffectChannelV1;
    byChannel.set(channel, [...(byChannel.get(channel) ?? []), entry as EffectObservationV1["channels"][number]]);
  }
  for (const channel of EFFECT_CHANNELS) {
    const entries = byChannel.get(channel) ?? [];
    if (entries.length === 0) {
      diagnostics.push("EFFECT_CHANNEL_MISSING");
      continue;
    }
    if (entries.length > 1) {
      diagnostics.push("EFFECT_CHANNEL_DUPLICATE");
    }
    for (const entry of entries) {
      if (entry.coverage === "unsupported") {
        diagnostics.push("EFFECT_CHANNEL_UNSUPPORTED");
      }
      if (entry.read_count !== 0) {
        diagnostics.push("EFFECT_READ_OBSERVED");
      }
      if (entry.write_count !== 0) {
        diagnostics.push("EFFECT_WRITE_OBSERVED");
      }
      if (entry.escape_count !== 0) {
        diagnostics.push("EFFECT_ESCAPE_OBSERVED");
      }
      if (entry.deferred_count !== 0) {
        diagnostics.push("EFFECT_DEFERRED_OBSERVED");
      }
    }
  }
  if (observation.result.consumption !== "complete") {
    diagnostics.push("EFFECT_RESULT_INCOMPLETE");
  }
  if (observation.result.mutable_alias_observed) {
    diagnostics.push("EFFECT_MUTABLE_ALIAS_OBSERVED");
  }
  if (!observation.quiescence.observed) {
    diagnostics.push("EFFECT_QUIESCENCE_UNSUPPORTED");
  }
  if (observation.quiescence.pending_count !== 0) {
    diagnostics.push("EFFECT_QUIESCENCE_VIOLATION");
  }

  const normalized = [...new Set(diagnostics)].sort(compareUtf8);
  const supportedChannels = new Set(observation.channels
    .filter(({coverage}) => coverage === "supported")
    .map(({channel}) => channel));
  const unsupportedChannels = new Set(observation.channels
    .filter(({coverage}) => coverage === "unsupported")
    .map(({channel}) => channel));
  const totals = observation.channels.reduce((sum, entry) => ({
    reads: sum.reads + entry.read_count,
    writes: sum.writes + entry.write_count,
    escapes: sum.escapes + entry.escape_count,
    deferred: sum.deferred + entry.deferred_count,
  }), {reads: 0, writes: 0, escapes: 0, deferred: 0});
  const evaluationCore = {
    schema_version: "EffectObservationEvaluation/v1" as const,
    observation_ref: {
      observation_id: observation.observation_id,
      observation_sha256: observation.observation_sha256,
    },
    observer_ref: {...locked},
    result: normalized.length === 0 ? "pass" as const : "fail" as const,
    diagnostics: normalized,
    coverage: {
      required: EFFECT_CHANNELS.length,
      supported: supportedChannels.size,
      unsupported: unsupportedChannels.size,
    },
    zero_effect_accounting: totals,
    claim: "transport-evaluation-only-no-runtime-interception" as const,
    authority_effect: "none" as const,
  };
  return deepFreeze({
    ...evaluationCore,
    evaluation_id: `evaluation.effect-observation.${sha256EffectObservationBytes(
      canonicalEffectObservationJson(evaluationCore),
    )}`,
  }) as EffectObservationEvaluationV1;
};

type DeclaredReadLifecycleBodyV1 = Omit<
  DeclaredReadLifecycleObservationV1,
  "observation_sha256"
>;

const validateDeclaredReadLifecycleBody: (
  value: unknown,
) => asserts value is DeclaredReadLifecycleBodyV1 = (value) => {
  if (!isRecord(value)) {
    throw new Error("DECLARED_READ_OBSERVATION_INVALID:observation");
  }
  exactKeys(value, [
    "schema_version",
    "observation_id",
    "source_kind",
    "target_ref",
    "observer_ref",
    "declared_read_attempts",
    "lifecycle_paths",
    "effect_observation",
    "source_support",
    "write_then_restore_observed",
    "authority_effect",
  ], "declared-read-observation");
  if (value.schema_version !== "DeclaredReadLifecycleObservation/v1" ||
      !validIdentifier(value.observation_id) ||
      (value.source_kind !== "independent-owner-observation" &&
        value.source_kind !== "mutated-declared-read-observation") ||
      (value.source_support !== "supported-static" &&
        value.source_support !== "unsupported-dynamic-or-generated") ||
      typeof value.write_then_restore_observed !== "boolean" ||
      value.authority_effect !== "none") {
    throw new Error("DECLARED_READ_OBSERVATION_INVALID:observation");
  }
  if (!isRecord(value.target_ref)) {
    throw new Error("DECLARED_READ_OBSERVATION_INVALID:target-ref");
  }
  exactKeys(value.target_ref, ["target_id", "target_sha256"],
    "declared-read-target-ref");
  if (!validIdentifier(value.target_ref.target_id) ||
      !SHA256.test(String(value.target_ref.target_sha256))) {
    throw new Error("DECLARED_READ_OBSERVATION_INVALID:target-ref");
  }
  validateObserverRef(value.observer_ref);
  if (!Array.isArray(value.declared_read_attempts)) {
    throw new Error("DECLARED_READ_OBSERVATION_INVALID:read-attempts");
  }
  for (const attempt of value.declared_read_attempts) {
    if (!isRecord(attempt)) {
      throw new Error("DECLARED_READ_OBSERVATION_INVALID:read-attempt");
    }
    exactKeys(attempt, [
      "ordinal",
      "target_id",
      "channel",
      "lifecycle_path",
      "outcome",
    ], "declared-read-attempt");
    if (!validCount(attempt.ordinal) || !validIdentifier(attempt.target_id) ||
        !CHANNEL_SET.has(String(attempt.channel)) ||
        !LIFECYCLE_SET.has(String(attempt.lifecycle_path)) ||
        (attempt.outcome !== "success" &&
          attempt.outcome !== "declared-failure")) {
      throw new Error("DECLARED_READ_OBSERVATION_INVALID:read-attempt");
    }
  }
  if (!Array.isArray(value.lifecycle_paths)) {
    throw new Error("DECLARED_READ_OBSERVATION_INVALID:lifecycle-paths");
  }
  for (const lifecycle of value.lifecycle_paths) {
    if (!isRecord(lifecycle)) {
      throw new Error("DECLARED_READ_OBSERVATION_INVALID:lifecycle-path");
    }
    exactKeys(lifecycle, ["lifecycle_path", "coverage"],
      "declared-read-lifecycle-path");
    if (!LIFECYCLE_SET.has(String(lifecycle.lifecycle_path)) ||
        (lifecycle.coverage !== "supported" &&
          lifecycle.coverage !== "unsupported")) {
      throw new Error("DECLARED_READ_OBSERVATION_INVALID:lifecycle-path");
    }
  }
  decodeEffectObservationV1(canonicalEffectObservationJson(
    value.effect_observation,
  ));
};

const declaredReadLifecycleBody = (
  observation: DeclaredReadLifecycleObservationV1,
): DeclaredReadLifecycleBodyV1 => {
  const {observation_sha256: _digest, ...body} = observation;
  return body;
};

export const mintDeclaredReadLifecycleObservationV1 = (
  input: DeclaredReadLifecycleBodyV1,
): DeclaredReadLifecycleObservationV1 => {
  validateDeclaredReadLifecycleBody(input);
  const body = {
    ...input,
    target_ref: {...input.target_ref},
    observer_ref: {...input.observer_ref},
    declared_read_attempts: [...input.declared_read_attempts]
      .sort((left, right) => left.ordinal - right.ordinal)
      .map((attempt) => ({...attempt})),
    lifecycle_paths: [...input.lifecycle_paths]
      .sort((left, right) =>
        (LIFECYCLE_ORDER.get(left.lifecycle_path) ?? Number.MAX_SAFE_INTEGER) -
        (LIFECYCLE_ORDER.get(right.lifecycle_path) ?? Number.MAX_SAFE_INTEGER))
      .map((lifecycle) => ({...lifecycle})),
    effect_observation: input.effect_observation,
  } satisfies DeclaredReadLifecycleBodyV1;
  return deepFreeze({
    ...body,
    observation_sha256: sha256EffectObservationBytes(
      canonicalEffectObservationJson(body),
    ),
  }) as DeclaredReadLifecycleObservationV1;
};

export const decodeDeclaredReadLifecycleObservationV1 = (
  bytes: string,
): DeclaredReadLifecycleObservationV1 => {
  let decoded: unknown;
  try {
    decoded = JSON.parse(bytes);
  } catch {
    throw new Error("DECLARED_READ_OBSERVATION_INVALID:json");
  }
  if (!isRecord(decoded)) {
    throw new Error("DECLARED_READ_OBSERVATION_INVALID:observation");
  }
  exactKeys(decoded, [
    "schema_version",
    "observation_id",
    "source_kind",
    "target_ref",
    "observer_ref",
    "declared_read_attempts",
    "lifecycle_paths",
    "effect_observation",
    "source_support",
    "write_then_restore_observed",
    "authority_effect",
    "observation_sha256",
  ], "declared-read-observation");
  const {observation_sha256, ...body} = decoded;
  if (typeof observation_sha256 !== "string" ||
      !SHA256.test(observation_sha256)) {
    throw new Error("DECLARED_READ_OBSERVATION_INVALID:digest");
  }
  const minted = mintDeclaredReadLifecycleObservationV1(
    body as DeclaredReadLifecycleBodyV1,
  );
  if (minted.observation_sha256 !== observation_sha256) {
    throw new Error("DECLARED_READ_OBSERVATION_DIGEST_STALE");
  }
  return minted;
};

const sameTargetRef = (
  left: Readonly<{target_id: string; target_sha256: string}>,
  right: Readonly<{target_id: string; target_sha256: string}>,
): boolean => canonicalEffectObservationJson(left) ===
  canonicalEffectObservationJson(right);

export const evaluateDeclaredReadLifecycleObservationV1 = (input: Readonly<{
  locked_observer_ref: LockedEffectObserverRefV1;
  locked_target_ref: Readonly<{target_id: string; target_sha256: string}>;
  declared_read_targets: readonly DeclaredReadTargetV1[];
  observation: DeclaredReadLifecycleObservationV1;
}>): DeclaredReadLifecycleEvaluationV1 => {
  const {locked_observer_ref: lockedObserver, locked_target_ref: lockedTarget,
    declared_read_targets: declaredTargets, observation} = input;
  const diagnostics: DeclaredReadLifecycleDiagnostic[] = [];
  const expectedDigest = sha256EffectObservationBytes(
    canonicalEffectObservationJson(declaredReadLifecycleBody(observation)),
  );
  if (expectedDigest !== observation.observation_sha256) {
    throw new Error("DECLARED_READ_OBSERVATION_DIGEST_STALE");
  }
  const nestedEffectDigest = sha256EffectObservationBytes(
    canonicalEffectObservationJson(observationBody(
      observation.effect_observation,
    )),
  );
  if (nestedEffectDigest !==
      observation.effect_observation.observation_sha256) {
    throw new Error("EFFECT_OBSERVATION_DIGEST_STALE");
  }
  if (!sameObserverRef(lockedObserver, observation.observer_ref) ||
      !sameObserverRef(observation.observer_ref,
        observation.effect_observation.observer_ref)) {
    diagnostics.push("DECLARED_READ_OBSERVER_BINDING_MISMATCH");
  }
  if (lockedObserver.owner_ref === lockedObserver.provider_id ||
      observation.observer_ref.owner_ref ===
        observation.observer_ref.provider_id) {
    diagnostics.push("DECLARED_READ_OBSERVER_SELF_ISSUED");
  }
  if (!sameTargetRef(lockedTarget, observation.target_ref) ||
      !sameTargetRef(observation.target_ref,
        observation.effect_observation.target_ref)) {
    diagnostics.push("DECLARED_READ_TARGET_BINDING_MISMATCH");
  }

  const observedLedger = observation.declared_read_attempts.map((attempt) => ({
    target_id: attempt.target_id,
    channel: attempt.channel,
  }));
  const ordinalComplete = observation.declared_read_attempts.every(
    ({ordinal}, index) => ordinal === index,
  );
  if (!ordinalComplete ||
      canonicalEffectObservationJson(observedLedger) !==
        canonicalEffectObservationJson(declaredTargets)) {
    diagnostics.push("DECLARED_READ_LEDGER_MISMATCH");
  }

  const effectEntries = observation.effect_observation.channels;
  const effectByChannel = new Map<EffectChannelV1,
    typeof effectEntries>();
  for (const channel of EFFECT_CHANNELS) effectByChannel.set(channel, []);
  for (const entry of effectEntries) {
    effectByChannel.set(entry.channel, [
      ...(effectByChannel.get(entry.channel) ?? []),
      entry,
    ]);
  }
  for (const channel of EFFECT_CHANNELS) {
    const entries = effectByChannel.get(channel) ?? [];
    if (entries.length === 0) {
      diagnostics.push("DECLARED_READ_CHANNEL_MISSING");
      continue;
    }
    if (entries.length > 1) {
      diagnostics.push("DECLARED_READ_CHANNEL_DUPLICATE");
    }
    const expectedReads = observation.declared_read_attempts.filter(
      (attempt) => attempt.channel === channel,
    ).length;
    for (const entry of entries) {
      if (entry.coverage !== "supported") {
        diagnostics.push("DECLARED_READ_CHANNEL_UNSUPPORTED");
      }
      if (entry.read_count !== expectedReads) {
        diagnostics.push("DECLARED_READ_COUNT_MISMATCH");
      }
      if (entry.write_count !== 0) {
        diagnostics.push("DECLARED_READ_WRITE_OBSERVED");
      }
      if (entry.escape_count !== 0) {
        diagnostics.push("DECLARED_READ_ESCAPE_OBSERVED");
      }
      if (entry.deferred_count !== 0) {
        diagnostics.push("DECLARED_READ_DEFERRED_OBSERVED");
      }
    }
  }

  const lifecycleByPath = new Map<DeclaredReadLifecyclePathV1,
    DeclaredReadLifecycleObservationV1["lifecycle_paths"]>();
  for (const path of DECLARED_READ_LIFECYCLE_PATHS) {
    lifecycleByPath.set(path, []);
  }
  for (const lifecycle of observation.lifecycle_paths) {
    lifecycleByPath.set(lifecycle.lifecycle_path, [
      ...(lifecycleByPath.get(lifecycle.lifecycle_path) ?? []),
      lifecycle,
    ]);
  }
  for (const path of DECLARED_READ_LIFECYCLE_PATHS) {
    const entries = lifecycleByPath.get(path) ?? [];
    if (entries.length === 0) {
      diagnostics.push("DECLARED_READ_LIFECYCLE_MISSING");
      continue;
    }
    if (entries.length > 1) {
      diagnostics.push("DECLARED_READ_LIFECYCLE_DUPLICATE");
    }
    if (entries.some(({coverage}) => coverage !== "supported")) {
      diagnostics.push("DECLARED_READ_LIFECYCLE_UNSUPPORTED");
    }
  }

  if (observation.effect_observation.result.consumption !== "complete") {
    diagnostics.push("DECLARED_READ_RESULT_INCOMPLETE");
  }
  if (observation.effect_observation.result.mutable_alias_observed) {
    diagnostics.push("DECLARED_READ_MUTABLE_ALIAS_OBSERVED");
  }
  if (!observation.effect_observation.quiescence.observed) {
    diagnostics.push("DECLARED_READ_QUIESCENCE_UNSUPPORTED");
  }
  if (observation.effect_observation.quiescence.pending_count !== 0) {
    diagnostics.push("DECLARED_READ_QUIESCENCE_VIOLATION");
  }
  if (observation.write_then_restore_observed) {
    diagnostics.push("DECLARED_READ_WRITE_THEN_RESTORE_OBSERVED");
  }
  if (observation.source_support !== "supported-static") {
    diagnostics.push("DECLARED_READ_SOURCE_UNSUPPORTED");
  }

  const normalized = [...new Set(diagnostics)].sort(compareUtf8);
  const supportedChannels = new Set(effectEntries
    .filter(({coverage}) => coverage === "supported")
    .map(({channel}) => channel));
  const unsupportedChannels = new Set(effectEntries
    .filter(({coverage}) => coverage === "unsupported")
    .map(({channel}) => channel));
  const supportedLifecycle = new Set(observation.lifecycle_paths
    .filter(({coverage}) => coverage === "supported")
    .map(({lifecycle_path: path}) => path));
  const unsupportedLifecycle = new Set(observation.lifecycle_paths
    .filter(({coverage}) => coverage === "unsupported")
    .map(({lifecycle_path: path}) => path));
  const totals = effectEntries.reduce((sum, entry) => ({
    writes: sum.writes + entry.write_count,
    escapes: sum.escapes + entry.escape_count,
    deferred: sum.deferred + entry.deferred_count,
  }), {writes: 0, escapes: 0, deferred: 0});
  const evaluationCore = {
    schema_version: "DeclaredReadLifecycleEvaluation/v1" as const,
    observation_ref: {
      observation_id: observation.observation_id,
      observation_sha256: observation.observation_sha256,
    },
    target_ref: {...lockedTarget},
    observer_ref: {...lockedObserver},
    result: normalized.length === 0 ? "pass" as const : "fail" as const,
    diagnostics: normalized,
    coverage: {
      effect_channels_required: EFFECT_CHANNELS.length,
      effect_channels_supported: supportedChannels.size,
      effect_channels_unsupported: unsupportedChannels.size,
      lifecycle_paths_required: DECLARED_READ_LIFECYCLE_PATHS.length,
      lifecycle_paths_supported: supportedLifecycle.size,
      lifecycle_paths_unsupported: unsupportedLifecycle.size,
    },
    read_accounting: {
      declared: declaredTargets.length,
      observed: observation.declared_read_attempts.length,
    },
    forbidden_accounting: totals,
    claim: "declared-read-transport-evaluation-no-runtime-interception" as const,
    authority_effect: "none" as const,
  };
  return deepFreeze({
    ...evaluationCore,
    evaluation_id: `evaluation.declared-read.${sha256EffectObservationBytes(
      canonicalEffectObservationJson(evaluationCore),
    )}`,
  }) as DeclaredReadLifecycleEvaluationV1;
};
