//! Finite, conservative accounting. An available-space observation is not a
//! reservation. The fixed authenticated host loader separately validates the
//! physical reserve claim; these checks bind its remaining capacity to the
//! exact observed inventory and acknowledged prefix before any allocation.
use crate::roots::{require, Error, Result};
use serde::{Deserialize, Serialize};

pub const MAX_RECORD: u64 = 1_048_576;
pub const MAX_PACKET: u64 = 65_536;
/// A sequence retains at most sixteen originals and its exclusive directory.
/// The separately reserved sixteen records/directory cover refusal/reconciliation
/// accounting. Ledger append capacity is independently reserved by Ledger.
pub const SEQUENCE_FILES: u64 = 16;
pub const CLEANUP_FILES: u64 = 16;

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Limits {
    pub schema_version: String,
    pub max_record_bytes: u64,
    pub max_response_bytes: u64,
    pub max_sequences: u64,
    pub max_stage_bytes: u64,
    pub max_member_bytes: u64,
    pub max_members: u64,
    pub max_retained_bytes: u64,
    pub max_retained_files: u64,
    pub max_stage_count: u64,
    pub max_orphan_count: u64,
    pub max_orphan_bytes: u64,
    pub max_inflight: u64,
}
impl Limits {
    pub fn validate(&self) -> Result<()> {
        require(self.schema_version == "lab-broker-quota/v1"
            && (4096..=MAX_RECORD).contains(&self.max_record_bytes)
            && (1024..=MAX_PACKET).contains(&self.max_response_bytes)
            && (1..=4096).contains(&self.max_sequences)
            && (1..=1_073_741_824).contains(&self.max_stage_bytes)
            && (1..=self.max_stage_bytes).contains(&self.max_member_bytes)
            && (1..=1024).contains(&self.max_members)
            && (self.sequence_bytes()? + self.cleanup_bytes()?..=1u64 << 40).contains(&self.max_retained_bytes)
            && (SEQUENCE_FILES + CLEANUP_FILES + 2..=100_000).contains(&self.max_retained_files)
            && (1..=4096).contains(&self.max_stage_count)
            && (1..=4096).contains(&self.max_orphan_count)
            && (self.max_stage_bytes..=1u64 << 40).contains(&self.max_orphan_bytes)
            && self.max_inflight == 1, "FINITE_BROKER_QUOTAS")
    }
    pub fn sequence_bytes(&self) -> Result<u64> {
        self.max_record_bytes.checked_mul(SEQUENCE_FILES).ok_or(Error("QUOTA_OVERFLOW"))
    }
    pub fn cleanup_bytes(&self) -> Result<u64> {
        self.max_record_bytes.checked_mul(CLEANUP_FILES).ok_or(Error("QUOTA_OVERFLOW"))
    }
    pub fn record(&self, raw: &[u8]) -> Result<()> {
        require(raw.len() as u64 <= self.max_record_bytes, "SELECTED_RECORD_BOUND")
    }
    pub fn response(&self, raw: &[u8]) -> Result<()> {
        require(raw.len() as u64 <= self.max_response_bytes, "SELECTED_RESPONSE_BOUND")
    }
}

#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Usage {
    pub retained_bytes: u64,
    /// Includes retained directories, temporary originals and failed branches.
    pub retained_inodes: u64,
    pub sequences: u64,
    pub stage_count: u64,
    /// Sum of declared immutable member lengths; charged once on first range.
    pub stage_bytes: u64,
    pub member_count: u64,
    pub orphan_count: u64,
    pub orphan_bytes: u64,
    pub inflight: u64,
}

/// These fields describe a claim, never authenticate one. The signed current
/// host selection must bind this exact object before a caller uses admission.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Remaining {
    pub inventory_sha256: String,
    pub prefix_sha256: String,
    pub bytes: u64,
    pub inodes: u64,
}

pub fn admit(limits: &Limits, usage: &Usage, selected: &Remaining,
             actual_inventory: &str, actual_prefix: &str) -> Result<()> {
    limits.validate()?;
    require(crate::roots::digest(actual_inventory) && crate::roots::digest(actual_prefix)
        && selected.inventory_sha256 == actual_inventory
        && selected.prefix_sha256 == actual_prefix, "RESERVE_INVENTORY_PREFIX")?;
    require(usage.inflight == 0, "ONE_INFLIGHT")?;
    require(usage.sequences < limits.max_sequences
        && usage.stage_count <= limits.max_stage_count
        && usage.stage_bytes <= limits.max_stage_bytes
        && usage.member_count <= limits.max_members
        && usage.orphan_count <= limits.max_orphan_count
        && usage.orphan_bytes <= limits.max_orphan_bytes, "RETAINED_QUOTA")?;
    let bytes = limits.sequence_bytes()?.checked_add(limits.cleanup_bytes()?).ok_or(Error("QUOTA_OVERFLOW"))?;
    let inodes = SEQUENCE_FILES + CLEANUP_FILES + 2;
    require(selected.bytes <= i64::MAX as u64 && selected.inodes <= i64::MAX as u64
        && selected.bytes >= bytes && selected.inodes >= inodes, "PHYSICAL_REMAINING_RESERVE")?;
    require(usage.retained_bytes.checked_add(bytes).is_some_and(|x| x <= limits.max_retained_bytes)
        && usage.retained_inodes.checked_add(inodes).is_some_and(|x| x <= limits.max_retained_files),
        "LOGICAL_REMAINING_RESERVE")
}

pub fn member(limits: &Limits, usage: &Usage, full_length: u64, new_member: bool,
              chunk_length: u64) -> Result<()> {
    limits.validate()?;
    require(full_length <= limits.max_member_bytes && ((full_length == 0 && chunk_length == 0)
        || (full_length > 0 && chunk_length > 0 && chunk_length <= 32768)),
        "MEMBER_QUOTA")?;
    require(usage.stage_bytes.checked_add(if new_member { full_length } else { 0 }).is_some_and(|x| x <= limits.max_stage_bytes)
        && (!new_member || usage.member_count < limits.max_members), "STAGE_MEMBER_QUOTA")
}

/// Four mutation positions remain reserved for seal, commit, exact settlement
/// and terminal/recovery accounting. Query verbs consume no mutation position.
/// This is an admission guarantee for the selected declared chunk plan, not an
/// inference that every allowed byte limit fits every possible sequence limit.
pub fn completion_positions(limits: &Limits, used_sequences: u64, remaining_chunk_count: u64,
                            new_stage: bool, usage: &Usage) -> Result<()> {
    limits.validate()?;
    let needed = remaining_chunk_count.checked_add(4).and_then(|v| v.checked_add(new_stage as u64))
        .ok_or(Error("QUOTA_OVERFLOW"))?;
    require(used_sequences.checked_add(needed).is_some_and(|n| n <= limits.max_sequences),
        "COMPLETE_SEQUENCE_CAPACITY")?;
    require(!new_stage || usage.stage_count < limits.max_stage_count, "PROSPECTIVE_STAGE_COUNT")?;
    // One new interrupted stage could become an orphan. Reserve its full
    // selected bound before the first creation rather than after interruption.
    require(!new_stage || (usage.orphan_count < limits.max_orphan_count
        && usage.orphan_bytes.checked_add(limits.max_stage_bytes).is_some_and(|n| n <= limits.max_orphan_bytes)),
        "PROSPECTIVE_ORPHAN_RESERVE")
}

/// Cleanup uses its independently refreshed remaining reserve. Retained payload
/// quota exhaustion is the reason to reconcile, never permission to delete it
/// and never a requirement for spare producer capacity. The finite receipt
/// history ceiling and byte/inode reserve still apply; consumed reserve cannot
/// be reused indefinitely.
pub fn admit_cleanup(limits:&Limits,usage:&Usage,selected:&Remaining,inventory:&str,prefix:&str)->Result<()>{
    limits.validate()?;
    require(crate::roots::digest(inventory)&&crate::roots::digest(prefix)
        &&selected.inventory_sha256==inventory&&selected.prefix_sha256==prefix,"RESERVE_INVENTORY_PREFIX")?;
    require(usage.inflight==0&&usage.sequences<limits.max_sequences,"TERMINAL_HISTORY_BOUND")?;
    let bytes=limits.cleanup_bytes()?;let inodes=CLEANUP_FILES+1;
    require(selected.bytes<=i64::MAX as u64&&selected.inodes<=i64::MAX as u64
        &&selected.bytes>=bytes&&selected.inodes>=inodes,"TERMINAL_PHYSICAL_RESERVE")?;
    require(usage.retained_bytes.checked_add(bytes).is_some_and(|n|n<=limits.max_retained_bytes)
        &&usage.retained_inodes.checked_add(inodes).is_some_and(|n|n<=limits.max_retained_files),"TERMINAL_RETAINED_RESERVE")
}
