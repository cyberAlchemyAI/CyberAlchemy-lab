import {createHash} from "node:crypto";

export const RUST_QUERY_EXPECTED_SOURCE = `pub const SETTLEMENT_BY_ID_TARGET: &str =
    "settlement.read.settlement-by-id";
pub const PAYOUT_BY_SETTLEMENT_TARGET: &str =
    "settlement.read.payout-by-settlement";

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CompleteSettlementInput<'a> {
    pub settlement_id: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SettlementRecord {
    pub settlement_id: String,
    pub settlement_status: String,
    pub gross_amount_minor: i64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PayoutRecord {
    pub payout_id: String,
    pub payout_status: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CompleteSettlementView {
    pub settlement_id: String,
    pub settlement_status: String,
    pub gross_amount_minor: i64,
    pub payout_id: String,
    pub payout_status: String,
}

pub trait CompleteSettlementReadPort {
    fn read_settlement_by_id(
        &mut self,
        target_id: &'static str,
        settlement_id: &str,
    ) -> SettlementRecord;

    fn read_payout_by_settlement(
        &mut self,
        target_id: &'static str,
        settlement_id: &str,
    ) -> PayoutRecord;
}

pub type BoundQuery = for<'a> fn(
    &CompleteSettlementInput<'a>,
    &mut dyn CompleteSettlementReadPort,
) -> CompleteSettlementView;

pub const COMPLETE_SETTLEMENT_QUERY: BoundQuery = read_complete_settlement;

fn read_complete_settlement(
    input: &CompleteSettlementInput<'_>,
    reads: &mut dyn CompleteSettlementReadPort,
) -> CompleteSettlementView {
    let settlement = reads.read_settlement_by_id(
        SETTLEMENT_BY_ID_TARGET,
        input.settlement_id,
    );
    let payout = reads.read_payout_by_settlement(
        PAYOUT_BY_SETTLEMENT_TARGET,
        input.settlement_id,
    );
    CompleteSettlementView {
        settlement_id: settlement.settlement_id,
        settlement_status: settlement.settlement_status,
        gross_amount_minor: settlement.gross_amount_minor,
        payout_id: payout.payout_id,
        payout_status: payout.payout_status,
    }
}
`;

export const RUST_QUERY_HOSTILE_IDS = Object.freeze([
  "swapped-read-order",
  "duplicate-read",
  "hidden-write",
  "write-then-restore",
  "deferred-lazy",
  "dynamic-source",
  "computed-read-target",
  "extra-output-field",
] as const);

export type RustQueryHostileId = (typeof RUST_QUERY_HOSTILE_IDS)[number];

export type RustQueryClosedSubsetProofV1 = Readonly<{
  schema_version: "RustQueryClosedSubsetProof/v1";
  result: "pass";
  source_sha256: string;
  symbol_name: "COMPLETE_SETTLEMENT_QUERY";
  callable_binding: "typed-function-item-constant";
  declared_read_targets: readonly [
    "settlement.read.settlement-by-id",
    "settlement.read.payout-by-settlement",
  ];
  result_fields: readonly [
    "settlement_id",
    "settlement_status",
    "gross_amount_minor",
    "payout_id",
    "payout_status",
  ];
  lifecycle_basis: "synchronous-return-plus-owned-plain-data-static-exclusion";
  mechanism: "exact-source-byte-closed-subset";
  authority_effect: "none";
}>;

const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8")
  .digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};

export const inspectRustQueryClosedSubset = (
  source: string,
): RustQueryClosedSubsetProofV1 => {
  if (!/^[\x00-\x7F]*$/u.test(source)) {
    return fail("RUST_QUERY_CLOSED_SUBSET_NON_ASCII");
  }
  if (source !== RUST_QUERY_EXPECTED_SOURCE) {
    return fail("RUST_QUERY_CLOSED_SUBSET_SOURCE_MISMATCH");
  }
  return Object.freeze({
    schema_version: "RustQueryClosedSubsetProof/v1" as const,
    result: "pass" as const,
    source_sha256: sha256(source),
    symbol_name: "COMPLETE_SETTLEMENT_QUERY" as const,
    callable_binding: "typed-function-item-constant" as const,
    declared_read_targets: Object.freeze([
      "settlement.read.settlement-by-id",
      "settlement.read.payout-by-settlement",
    ] as const),
    result_fields: Object.freeze([
      "settlement_id",
      "settlement_status",
      "gross_amount_minor",
      "payout_id",
      "payout_status",
    ] as const),
    lifecycle_basis:
      "synchronous-return-plus-owned-plain-data-static-exclusion" as const,
    mechanism: "exact-source-byte-closed-subset" as const,
    authority_effect: "none" as const,
  });
};

export const rustQueryHostileSource = (
  source: string,
  hostileId: RustQueryHostileId,
): string => {
  inspectRustQueryClosedSubset(source);
  const settlementTarget = "settlement.read.settlement-by-id";
  const payoutTarget = "settlement.read.payout-by-settlement";
  const swapSentinel = "__DOMAINSPEC_QUERY_SWAP__";
  const sources: Readonly<Record<RustQueryHostileId, string>> = Object.freeze({
    "swapped-read-order": source
      .replace(settlementTarget, swapSentinel)
      .replace(payoutTarget, settlementTarget)
      .replace(swapSentinel, payoutTarget),
    "duplicate-read": source.replace(payoutTarget, settlementTarget),
    "hidden-write": `use std::fs;\n${source}`,
    "write-then-restore": `static mut QUERY_SCRATCH: i32 = 0;\n${source}`,
    "deferred-lazy": `use std::future::Future;\n${source}`,
    "dynamic-source": `macro_rules! query_source { () => {}; }\n${source}`,
    "computed-read-target": source.replace(
      `    "${settlementTarget}";`,
      `    concat!("settlement.read.", "settlement-by-id");`,
    ),
    "extra-output-field": source.replace(
      "    pub payout_status: String,\n}",
      "    pub payout_status: String,\n    pub extra: String,\n}",
    ),
  });
  const hostile = sources[hostileId];
  if (hostile === source) return fail("RUST_QUERY_HOSTILE_SOURCE_UNCHANGED");
  return hostile;
};
