// Stage D (part 1) — obligation_key: content-addressed, byte-stable IDs.
// SWU-ENG-004 finalizes canonical_params normalization. The hash itself is
// deterministic and implemented here (no external deps; Node's crypto).

import { createHash } from "node:crypto";
import type {
  ObligationKey,
  RuleType,
  SourceAnchor,
  Value,
} from "../ir/types.js";

/** Stable JSON: object keys sorted so equal params always serialize identically. */
function canonicalJson(params: Readonly<Record<string, Value>>): string {
  const keys = Object.keys(params).sort();
  const parts = keys.map(
    (k) => `${JSON.stringify(k)}:${JSON.stringify(params[k] ?? null)}`,
  );
  return `{${parts.join(",")}}`;
}

export interface ObligationFreshness {
  readonly ruleSetVersion: string;
  readonly semanticSourceFingerprint: string;
}

/**
 * v2 derivation keys bind the rule-set and source semantics. The three-argument
 * form remains only for historical callers; it must not be used for current
 * derived/evidence identities.
 */
export function obligationKey(
  sourceAnchor: SourceAnchor,
  ruleType: RuleType,
  canonicalParams: Readonly<Record<string, Value>>,
  freshness?: ObligationFreshness,
): ObligationKey {
  const payload = freshness
    ? `v2|${JSON.stringify(freshness.ruleSetVersion)}|${freshness.semanticSourceFingerprint}|${sourceAnchor}|${ruleType}|${canonicalJson(canonicalParams)}`
    : `${sourceAnchor}|${ruleType}|${canonicalJson(canonicalParams)}`;
  return createHash("sha1").update(payload).digest("hex");
}
