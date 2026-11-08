import {createHash} from "node:crypto";

import {
  EFFECT_CHANNELS,
  type EffectChannelV1,
} from "../../../../kernel/evidence/effect-observation/index.js";

export const RUST_POLICY_EXPECTED_SOURCE = `#[derive(Debug, Copy, Clone, PartialEq, Eq, Hash)]
pub enum SettlementRoutingStrategyId {
    Standard,
    Expedited,
    ManualReview,
}

impl SettlementRoutingStrategyId {
    pub const fn as_wire(self) -> &'static str {
        match self {
            Self::Standard => "settlement.route.standard",
            Self::Expedited => "settlement.route.expedited",
            Self::ManualReview => "settlement.route.manual-review",
        }
    }
}

#[derive(Debug, Copy, Clone, PartialEq, Eq)]
pub struct SettlementRoutingInput {
    pub amount_minor: i64,
    pub expedite_limit_minor: i64,
    pub expedite_requested: bool,
    pub manual_review_required: bool,
}

pub type BoundPolicy<Input, Strategy> = fn(&Input) -> Strategy;

pub const SETTLEMENT_ROUTING_POLICY: BoundPolicy<
    SettlementRoutingInput,
    SettlementRoutingStrategyId,
> = select_settlement_route;

fn select_settlement_route(
    input: &SettlementRoutingInput,
) -> SettlementRoutingStrategyId {
    if input.manual_review_required {
        SettlementRoutingStrategyId::ManualReview
    } else if input.expedite_requested
        && input.amount_minor <= input.expedite_limit_minor
    {
        SettlementRoutingStrategyId::Expedited
    } else {
        SettlementRoutingStrategyId::Standard
    }
}
`;

export type RustPolicyClosedSubsetProofV1 = Readonly<{
  schema_version: "RustPolicyClosedSubsetProof/v1";
  result: "pass";
  source_sha256: string;
  input_kind: "four-explicit-fields";
  output_kind: "typed-unit-variant-strategy-identity";
  callable_binding: "typed-function-item-constant";
  strategy_call_sites: 0;
  supported_effect_channels: readonly EffectChannelV1[];
  mechanism: "exact-source-byte-closed-subset-plus-native-compile";
  authority_effect: "none";
}>;

const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8")
  .digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};

export const inspectRustPolicyClosedSubset = (
  source: string,
): RustPolicyClosedSubsetProofV1 => {
  if (!/^[\x00-\x7F]*$/u.test(source)) {
    return fail("RUST_POLICY_CLOSED_SUBSET_NON_ASCII");
  }
  if (source !== RUST_POLICY_EXPECTED_SOURCE) {
    return fail("RUST_POLICY_CLOSED_SUBSET_SOURCE_MISMATCH");
  }
  return Object.freeze({
    schema_version: "RustPolicyClosedSubsetProof/v1" as const,
    result: "pass" as const,
    source_sha256: sha256(source),
    input_kind: "four-explicit-fields" as const,
    output_kind: "typed-unit-variant-strategy-identity" as const,
    callable_binding: "typed-function-item-constant" as const,
    strategy_call_sites: 0 as const,
    supported_effect_channels: EFFECT_CHANNELS,
    mechanism: "exact-source-byte-closed-subset-plus-native-compile" as const,
    authority_effect: "none" as const,
  });
};

export const rustPolicyHostileSource = (
  source: string,
  channel: EffectChannelV1,
): string => {
  inspectRustPolicyClosedSubset(source);
  const mutationByChannel: Readonly<Record<EffectChannelV1, string>> = Object.freeze({
    clock: "use std::time::SystemTime;\n",
    random: "use rand::random;\n",
    environment: "use std::env;\n",
    filesystem: "use std::fs;\n",
    network: "use std::net::TcpStream;\n",
    process: "use std::process::Command;\n",
    "global-cache": "static mut CACHED_ROUTE: usize = 0;\n",
    "delayed-lazy": "const DEFERRED: Option<fn()> = None;\n",
    callback: "type StrategyCallback = fn(&str);\n",
    "iterator-future": "use std::future::Future;\n",
    "finalizer-drop":
      "struct DropProbe; impl Drop for DropProbe { fn drop(&mut self) {} }\n",
    "mutable-output": "type MutableStrategy = Vec<String>;\n",
  });
  return `${mutationByChannel[channel]}${source}`;
};
