import {describe, expect, it} from "vitest";

import {
  DECLARED_READ_LIFECYCLE_PATHS,
  EFFECT_CHANNELS,
  canonicalEffectObservationJson,
  decodeDeclaredReadLifecycleObservationV1,
  decodeEffectObservationV1,
  evaluateDeclaredReadLifecycleObservationV1,
  evaluateEffectObservationV1,
  mintDeclaredReadLifecycleObservationV1,
  mintEffectObservationV1,
  sha256EffectObservationBytes,
  type DeclaredReadLifecycleObservationV1,
  type DeclaredReadTargetV1,
  type EffectChannelV1,
  type EffectObservationV1,
  type LockedEffectObserverRefV1,
} from "./index.js";

const digest = (value: string): string => value.repeat(64).slice(0, 64);
const locked: LockedEffectObserverRefV1 = Object.freeze({
  role: "independent-effect-observer",
  observer_id: "observer.effect-transport/v1",
  observer_sha256: digest("a"),
  owner_ref: "calculation-proof-owner",
  provider_id: "typescript.calculation-provider/v1",
  provider_sha256: digest("b"),
});
const zeroChannel = (channel: EffectChannelV1) => Object.freeze({
  channel,
  coverage: "supported" as const,
  read_count: 0,
  write_count: 0,
  escape_count: 0,
  deferred_count: 0,
});
const positive = (overrides: Partial<Omit<
  EffectObservationV1,
  "observation_sha256"
>> = {}): EffectObservationV1 => mintEffectObservationV1({
  schema_version: "EffectObservation/v1",
  observation_id: "observation.calculation-positive/v1",
  source_kind: "independent-owner-observation",
  target_ref: {
    target_id: "calculation.fixture-target/v1",
    target_sha256: digest("c"),
  },
  observer_ref: locked,
  channels: EFFECT_CHANNELS.map(zeroChannel),
  result: {consumption: "complete", mutable_alias_observed: false},
  quiescence: {observed: true, pending_count: 0},
  authority_effect: "none",
  ...overrides,
});
const findingCodes = (observation: EffectObservationV1, observer = locked) =>
  evaluateEffectObservationV1({
    locked_observer_ref: observer,
    observation,
  }).diagnostics;

const queryTarget = Object.freeze({
  target_id: "query.fixture-target/v1",
  target_sha256: digest("e"),
});
const declaredReadTargets: readonly DeclaredReadTargetV1[] = Object.freeze([
  Object.freeze({
    target_id: "read-target.settlement.by-player-id/v1",
    channel: "global-cache",
  }),
  Object.freeze({
    target_id: "read-target.payout.by-settlement-id/v1",
    channel: "global-cache",
  }),
]);
const declaredReadPositive = (overrides: Partial<Omit<
  DeclaredReadLifecycleObservationV1,
  "observation_sha256"
>> = {}): DeclaredReadLifecycleObservationV1 => {
  const effect = positive({
    observation_id: "observation.query-declared-read-effects/v1",
    target_ref: queryTarget,
    channels: EFFECT_CHANNELS.map((channel) => ({
      ...zeroChannel(channel),
      read_count: channel === "global-cache" ? declaredReadTargets.length : 0,
    })),
  });
  return mintDeclaredReadLifecycleObservationV1({
    schema_version: "DeclaredReadLifecycleObservation/v1",
    observation_id: "observation.query-declared-read-lifecycle/v1",
    source_kind: "independent-owner-observation",
    target_ref: queryTarget,
    observer_ref: locked,
    declared_read_attempts: declaredReadTargets.map((target, ordinal) => ({
      ordinal,
      ...target,
      lifecycle_path: ordinal === 0 ? "return" : "iterate-or-await",
      outcome: "success",
    })),
    lifecycle_paths: DECLARED_READ_LIFECYCLE_PATHS.map((lifecycle_path) => ({
      lifecycle_path,
      coverage: "supported",
    })),
    effect_observation: effect,
    source_support: "supported-static",
    write_then_restore_observed: false,
    authority_effect: "none",
    ...overrides,
  });
};
const declaredReadFindingCodes = (
  observation: DeclaredReadLifecycleObservationV1,
  observer = locked,
  target = queryTarget,
) => evaluateDeclaredReadLifecycleObservationV1({
  locked_observer_ref: observer,
  locked_target_ref: target,
  declared_read_targets: declaredReadTargets,
  observation,
}).diagnostics;

describe("independent effect-observation transport", () => {
  it("accounts for the complete perimeter without claiming runtime interception", () => {
    const observation = positive({
      channels: [...EFFECT_CHANNELS].reverse().map(zeroChannel),
    });
    const evaluation = evaluateEffectObservationV1({
      locked_observer_ref: locked,
      observation,
    });
    expect(observation.channels.map(({channel}) => channel)).toEqual(EFFECT_CHANNELS);
    expect(evaluation.result).toBe("pass");
    expect(evaluation.diagnostics).toEqual([]);
    expect(evaluation.coverage).toEqual({
      required: 12,
      supported: 12,
      unsupported: 0,
    });
    expect(evaluation.zero_effect_accounting).toEqual({
      reads: 0,
      writes: 0,
      escapes: 0,
      deferred: 0,
    });
    expect(evaluation.claim).toBe("transport-evaluation-only-no-runtime-interception");
    expect(Object.isFrozen(observation)).toBe(true);
    expect(Object.isFrozen(evaluation)).toBe(true);
  });

  it("rejects provider-self-issued zero counts", () => {
    const selfIssued = Object.freeze({
      ...locked,
      owner_ref: locked.provider_id,
    });
    expect(findingCodes(positive({observer_ref: selfIssued}), selfIssued))
      .toContain("EFFECT_OBSERVER_SELF_ISSUED");
  });

  it("rejects a stale observer or provider binding", () => {
    const stale = Object.freeze({...locked, provider_sha256: digest("d")});
    expect(findingCodes(positive(), stale))
      .toContain("EFFECT_OBSERVER_BINDING_MISMATCH");
  });

  it("distinguishes a missing channel from unsupported coverage", () => {
    const missing = positive({
      channels: EFFECT_CHANNELS.filter((channel) => channel !== "network")
        .map(zeroChannel),
    });
    const unsupported = positive({
      channels: EFFECT_CHANNELS.map((channel) => channel === "filesystem"
        ? {...zeroChannel(channel), coverage: "unsupported" as const}
        : zeroChannel(channel)),
    });
    expect(findingCodes(missing)).toContain("EFFECT_CHANNEL_MISSING");
    expect(findingCodes(unsupported)).toContain("EFFECT_CHANNEL_UNSUPPORTED");
  });

  it.each([
    ["read_count", "EFFECT_READ_OBSERVED"],
    ["write_count", "EFFECT_WRITE_OBSERVED"],
    ["escape_count", "EFFECT_ESCAPE_OBSERVED"],
    ["deferred_count", "EFFECT_DEFERRED_OBSERVED"],
  ] as const)("rejects nonzero %s", (field, code) => {
    const observation = positive({
      channels: EFFECT_CHANNELS.map((channel) => channel === "global-cache"
        ? {...zeroChannel(channel), [field]: 1}
        : zeroChannel(channel)),
    });
    expect(findingCodes(observation)).toContain(code);
  });

  it("rejects incomplete consumption and a mutable result alias", () => {
    const observation = positive({
      result: {consumption: "incomplete", mutable_alias_observed: true},
    });
    expect(findingCodes(observation)).toEqual([
      "EFFECT_MUTABLE_ALIAS_OBSERVED",
      "EFFECT_RESULT_INCOMPLETE",
    ]);
  });

  it("rejects non-quiescence and pending work", () => {
    expect(findingCodes(positive({
      quiescence: {observed: false, pending_count: 2},
    }))).toEqual([
      "EFFECT_QUIESCENCE_UNSUPPORTED",
      "EFFECT_QUIESCENCE_VIOLATION",
    ]);
  });

  it("fails closed on a stale observation digest", () => {
    const observation = positive();
    const stale = canonicalEffectObservationJson({
      ...observation,
      observation_sha256: digest("0"),
    });
    expect(() => decodeEffectObservationV1(stale))
      .toThrow("EFFECT_OBSERVATION_DIGEST_STALE");
    expect(decodeEffectObservationV1(
      canonicalEffectObservationJson(observation),
    )).toEqual(observation);
  });
});

describe("declared-read lifecycle observation transport", () => {
  it("accounts for exact declared reads without weakening zero-read evaluation", () => {
    const observation = declaredReadPositive();
    const evaluation = evaluateDeclaredReadLifecycleObservationV1({
      locked_observer_ref: locked,
      locked_target_ref: queryTarget,
      declared_read_targets: declaredReadTargets,
      observation,
    });
    expect(evaluation.result).toBe("pass");
    expect(evaluation.diagnostics).toEqual([]);
    expect(evaluation.coverage).toEqual({
      effect_channels_required: 12,
      effect_channels_supported: 12,
      effect_channels_unsupported: 0,
      lifecycle_paths_required: 7,
      lifecycle_paths_supported: 7,
      lifecycle_paths_unsupported: 0,
    });
    expect(evaluation.read_accounting).toEqual({declared: 2, observed: 2});
    expect(evaluation.forbidden_accounting).toEqual({
      writes: 0,
      escapes: 0,
      deferred: 0,
    });
    expect(evaluateEffectObservationV1({
      locked_observer_ref: locked,
      observation: observation.effect_observation,
    }).diagnostics).toContain("EFFECT_READ_OBSERVED");
  });

  it("rejects wrong read order and channel accounting", () => {
    const wrongLedger = declaredReadPositive({
      declared_read_attempts: [...declaredReadPositive().declared_read_attempts]
        .reverse()
        .map((attempt, ordinal) => ({...attempt, ordinal})),
    });
    const wrongCount = declaredReadPositive({
      effect_observation: positive({
        observation_id: "observation.query-wrong-read-count/v1",
        target_ref: queryTarget,
      }),
    });
    expect(declaredReadFindingCodes(wrongLedger))
      .toContain("DECLARED_READ_LEDGER_MISMATCH");
    expect(declaredReadFindingCodes(wrongCount))
      .toContain("DECLARED_READ_COUNT_MISMATCH");
  });

  it("fails closed on writes, escapes, deferred work, and write-restore", () => {
    const effect = declaredReadPositive().effect_observation;
    const hostileEffect = positive({
      observation_id: "observation.query-forbidden-effects/v1",
      target_ref: queryTarget,
      channels: effect.channels.map((entry) => entry.channel === "global-cache"
        ? {...entry, write_count: 1, escape_count: 1, deferred_count: 1}
        : entry),
    });
    expect(declaredReadFindingCodes(declaredReadPositive({
      effect_observation: hostileEffect,
      write_then_restore_observed: true,
    }))).toEqual(expect.arrayContaining([
      "DECLARED_READ_WRITE_OBSERVED",
      "DECLARED_READ_ESCAPE_OBSERVED",
      "DECLARED_READ_DEFERRED_OBSERVED",
      "DECLARED_READ_WRITE_THEN_RESTORE_OBSERVED",
    ]));
  });

  it("distinguishes missing and unsupported lifecycle/source coverage", () => {
    const missing = declaredReadPositive({
      lifecycle_paths: DECLARED_READ_LIFECYCLE_PATHS
        .filter((path) => path !== "finalizer")
        .map((lifecycle_path) => ({lifecycle_path, coverage: "supported"})),
    });
    const unsupported = declaredReadPositive({
      lifecycle_paths: DECLARED_READ_LIFECYCLE_PATHS.map((lifecycle_path) => ({
        lifecycle_path,
        coverage: lifecycle_path === "dispose" ? "unsupported" : "supported",
      })),
      source_support: "unsupported-dynamic-or-generated",
    });
    expect(declaredReadFindingCodes(missing))
      .toContain("DECLARED_READ_LIFECYCLE_MISSING");
    expect(declaredReadFindingCodes(unsupported)).toEqual(expect.arrayContaining([
      "DECLARED_READ_LIFECYCLE_UNSUPPORTED",
      "DECLARED_READ_SOURCE_UNSUPPORTED",
    ]));
  });

  it("rejects stale bindings, self-issued evidence, and stale digests", () => {
    const staleTarget = {...queryTarget, target_sha256: digest("f")};
    expect(declaredReadFindingCodes(declaredReadPositive(), locked, staleTarget))
      .toContain("DECLARED_READ_TARGET_BINDING_MISMATCH");
    const selfIssued = Object.freeze({...locked, owner_ref: locked.provider_id});
    expect(declaredReadFindingCodes(declaredReadPositive({
      observer_ref: selfIssued,
      effect_observation: positive({
        observation_id: "observation.query-self-issued/v1",
        target_ref: queryTarget,
        observer_ref: selfIssued,
        channels: EFFECT_CHANNELS.map((channel) => ({
          ...zeroChannel(channel),
          read_count: channel === "global-cache" ? 2 : 0,
        })),
      }),
    }), selfIssued)).toContain("DECLARED_READ_OBSERVER_SELF_ISSUED");
    const observation = declaredReadPositive();
    expect(() => decodeDeclaredReadLifecycleObservationV1(
      canonicalEffectObservationJson({...observation, observation_sha256: digest("0")}),
    )).toThrow("DECLARED_READ_OBSERVATION_DIGEST_STALE");
    expect(decodeDeclaredReadLifecycleObservationV1(
      canonicalEffectObservationJson(observation),
    )).toEqual(observation);
    const {observation_sha256: _outerDigest, ...outerBody} = observation;
    const forgedBody = {
      ...outerBody,
      effect_observation: {
        ...observation.effect_observation,
        observation_sha256: digest("0"),
      },
    };
    const forged = {
      ...forgedBody,
      observation_sha256: sha256EffectObservationBytes(
        canonicalEffectObservationJson(forgedBody),
      ),
    } as DeclaredReadLifecycleObservationV1;
    expect(() => evaluateDeclaredReadLifecycleObservationV1({
      locked_observer_ref: locked,
      locked_target_ref: queryTarget,
      declared_read_targets: declaredReadTargets,
      observation: forged,
    })).toThrow("EFFECT_OBSERVATION_DIGEST_STALE");
  });
});
