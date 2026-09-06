import {createHash} from "node:crypto";

import {
  EFFECT_CHANNELS,
  type EffectChannelV1,
} from "../../../../kernel/evidence/effect-observation/index.js";

export const RUST_CALCULATION_EXPECTED_SOURCE = `#[derive(Debug, Copy, Clone, PartialEq, Eq)]
pub struct NetSettlementInput {
    pub gross_amount_minor: i64,
    pub fee_amount_minor: i64,
}

pub type BoundCalculation<Input, Output> = fn(&Input) -> Output;

pub const NET_SETTLEMENT: BoundCalculation<NetSettlementInput, i64> =
    calculate_net_settlement;

fn calculate_net_settlement(input: &NetSettlementInput) -> i64 {
    input.gross_amount_minor - input.fee_amount_minor
}
`;

export type RustCalculationClosedSubsetProofV1 = Readonly<{
  schema_version: "RustCalculationClosedSubsetProof/v1";
  result: "pass";
  source_sha256: string;
  input_kind: "two-i64-fields";
  output_kind: "primitive-i64";
  callable_binding: "typed-function-item-constant";
  operation: "subtract";
  supported_effect_channels: readonly EffectChannelV1[];
  mechanism: "exact-source-byte-closed-subset";
  authority_effect: "none";
}>;

const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8")
  .digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};

export const inspectRustCalculationClosedSubset = (
  source: string,
): RustCalculationClosedSubsetProofV1 => {
  if (!/^[\x00-\x7F]*$/u.test(source)) {
    return fail("RUST_CALC_CLOSED_SUBSET_NON_ASCII");
  }
  if (source !== RUST_CALCULATION_EXPECTED_SOURCE) {
    return fail("RUST_CALC_CLOSED_SUBSET_SOURCE_MISMATCH");
  }
  return Object.freeze({
    schema_version: "RustCalculationClosedSubsetProof/v1" as const,
    result: "pass" as const,
    source_sha256: sha256(source),
    input_kind: "two-i64-fields" as const,
    output_kind: "primitive-i64" as const,
    callable_binding: "typed-function-item-constant" as const,
    operation: "subtract" as const,
    supported_effect_channels: EFFECT_CHANNELS,
    mechanism: "exact-source-byte-closed-subset" as const,
    authority_effect: "none" as const,
  });
};

export const rustCalculationHostileSource = (
  source: string,
  channel: EffectChannelV1,
): string => {
  inspectRustCalculationClosedSubset(source);
  const mutationByChannel: Readonly<Record<EffectChannelV1, string>> = Object.freeze({
    clock: "use std::time::SystemTime;\n",
    random: "use rand::random;\n",
    environment: "use std::env;\n",
    filesystem: "use std::fs;\n",
    network: "use std::net::TcpStream;\n",
    process: "use std::process::Command;\n",
    "global-cache": "static mut CACHED_FEE: i64 = 0;\n",
    "delayed-lazy": "const DEFERRED: Option<fn()> = None;\n",
    callback: "type Callback = fn(i64);\n",
    "iterator-future": "use std::future::Future;\n",
    "finalizer-drop": "struct DropProbe; impl Drop for DropProbe { fn drop(&mut self) {} }\n",
    "mutable-output": "type MutableOutput = Vec<i64>;\n",
  });
  return `${mutationByChannel[channel]}${source}`;
};
