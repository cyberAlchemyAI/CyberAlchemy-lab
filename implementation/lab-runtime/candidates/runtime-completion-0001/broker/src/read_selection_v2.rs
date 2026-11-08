//! Versioned, non-authorizing R03 read join. The fixed broker must first hold the commit
//! lock, establish current disclosure authority and a confirmed pointer, and
//! fetch these exact originals through held roots. This module cannot issue
//! disclosure permission or turn an unconfirmed pointer into a selection.
use crate::{generation::{self,GenerationManifest,PointerRecord,StoreSelection,Consumer},roots::{self,Binding,Error,Result,require}};
use std::collections::BTreeSet;

/// Owned immutable projection for one selected consumer operation. A later
/// pointer replacement cannot change these fields or the member byte oracle.
///
/// ```compile_fail
/// use lab_read_join_candidate_tests::read_selection::ReadJoin;
/// fn retarget(join: &mut ReadJoin) { join.sequence = 999; }
/// ```
#[derive(Clone,Debug)]
pub struct ReadJoin {
    store_id:String,
    sequence:u64,
    manifest_binding:Binding,
    original_cut_binding:Binding,
    disclosure_binding:Binding,
    operation_id:String,
    consumer:Consumer,
    members:std::collections::BTreeMap<String,Binding>,
}

/// Joins originals after the caller's separately verified confirmation and
/// disclosure. No supplied digest, path or JSON is accepted as that authority.
/// The rich manifest and C01 projection are both required because the pointer
/// names the latter while reader members are bound by the former.
pub fn join_originals(
    store:&StoreSelection,pointer_raw:&[u8],pointer_binding:&Binding,
    rich_manifest_raw:&[u8],rich_manifest_binding:&Binding,
    c01_manifest_raw:&[u8],consumer:&Consumer,disclosure_binding:&Binding,
) -> Result<ReadJoin> {
    store.validate()?;
    require(disclosure_binding.valid()&&pointer_binding.valid()&&rich_manifest_binding.valid(),"READ_BINDING")?;
    require(pointer_raw.len()<=store.limits.max_record_bytes as usize &&
        rich_manifest_raw.len()<=store.limits.max_record_bytes as usize &&
        c01_manifest_raw.len()<=store.limits.max_record_bytes as usize,"READ_RECORD_BOUND")?;
    let pointer:PointerRecord=serde_json::from_slice(pointer_raw).map_err(|_|Error("READ_POINTER_SCHEMA"))?;
    pointer.validate()?;
    let manifest:GenerationManifest=serde_json::from_slice(rich_manifest_raw).map_err(|_|Error("READ_MANIFEST_SCHEMA"))?;
    require(generation::canonical(&pointer)?==pointer_raw && generation::canonical(&manifest)?==rich_manifest_raw,"READ_CANONICAL")?;
    require(pointer_binding.root_id==store.pointer_root_id && pointer_binding.relative_path==store.pointer_member &&
        pointer_binding.sha256==roots::hash(pointer_raw) && pointer_binding.size_bytes==pointer_raw.len() as u64 &&
        rich_manifest_binding.sha256==roots::hash(rich_manifest_raw) && rich_manifest_binding.size_bytes==rich_manifest_raw.len() as u64,
        "READ_ORIGINAL_BINDING")?;
    require(generation::c01_manifest(&manifest)?==c01_manifest_raw &&
        pointer.generation_manifest_binding.sha256==roots::hash(c01_manifest_raw) &&
        pointer.generation_manifest_binding.size_bytes==c01_manifest_raw.len() as u64,
        "READ_MANIFEST_PROJECTION")?;
    require(manifest.stage_creation_binding.valid() && manifest.member_manifest_binding.valid() &&
        manifest.original_cut_binding.valid() && manifest.reader_inventory_binding.valid() &&
        manifest.expected_replay_result_binding.valid() && roots::digest(&manifest.original_fingerprint) &&
        !manifest.source_cut.is_empty() && manifest.source_cut.chars().count()<=4096 &&
        roots::name(&manifest.generation_id).is_ok(),"READ_RICH_MANIFEST_FIELDS")?;
    require(pointer.logical_store_id==store.store_id && pointer.logical_store_id==manifest.store_id &&
        pointer.sequence==manifest.sequence && pointer.writer_epoch==manifest.writer_epoch &&
        pointer.operation_id==manifest.operation_id && pointer.predecessor_pointer_binding==manifest.predecessor_pointer_binding &&
        manifest.creation_instance==store.instance_id && manifest.schema_version=="lab-generation-manifest/v1" &&
        !manifest.generation_id.is_empty() && manifest.original_cut_binding.valid() &&
        manifest.reader_inventory_binding.sha256==roots::hash(&generation::canonical(&store.consumer_inventory)?) &&
        manifest.reader_inventory_binding.size_bytes==generation::canonical(&store.consumer_inventory)?.len() as u64,
        "READ_GENERATION_JOIN")?;
    require(store.consumer_inventory.contains(consumer) && consumer.adapter.valid() &&
        manifest.members.keys().cloned().collect::<BTreeSet<_>>()==store.member_inventory.iter().map(|m|m.relative_path.clone()).collect(),
        "READ_CONSUMER_COVERAGE")?;
    let mut total=0u64;
    for (path,binding) in &manifest.members {
        require(binding.valid() && binding.root_id==store.generations_root_id &&
            binding.relative_path==format!("{}/{path}",manifest.generation_id) &&
            binding.size_bytes<=store.limits.max_member_bytes,"READ_MEMBER_BINDING")?;
        total=total.checked_add(binding.size_bytes).ok_or(Error("READ_MEMBER_OVERFLOW"))?;
    }
    require(total<=store.limits.max_stage_bytes,"READ_MEMBER_TOTAL")?;
    Ok(ReadJoin{store_id:store.store_id.clone(),sequence:pointer.sequence,
        manifest_binding:pointer.generation_manifest_binding,
        original_cut_binding:manifest.original_cut_binding,
        disclosure_binding:disclosure_binding.clone(),
        operation_id:pointer.operation_id,consumer:consumer.clone(),members:manifest.members})
}

impl ReadJoin {
    pub fn store_id(&self)->&str {&self.store_id}
    pub fn sequence(&self)->u64 {self.sequence}
    pub fn manifest_binding(&self)->&Binding {&self.manifest_binding}
    pub fn original_cut_binding(&self)->&Binding {&self.original_cut_binding}
    pub fn consumer_binding(&self)->&Binding {&self.consumer.adapter}
    pub fn disclosure_binding(&self)->&Binding {&self.disclosure_binding}
    pub fn operation_id(&self)->&str {&self.operation_id}
    /// The adapter checks every original it consumes; retention of a join does
    /// not extend disclosure permission, which remains the caller's obligation.
    pub fn check_member(&self,consumer:&Consumer,path:&str,raw:&[u8])->Result<()> {
        require(consumer==&self.consumer && self.consumer.member_paths.iter().any(|p|p==path),"READ_MEMBER_PERMISSION")?;
        let b=self.members.get(path).ok_or(Error("READ_MEMBER_UNSELECTED"))?;
        require(raw.len() as u64==b.size_bytes && roots::hash(raw)==b.sha256,"READ_MEMBER_BYTES")
    }
}
