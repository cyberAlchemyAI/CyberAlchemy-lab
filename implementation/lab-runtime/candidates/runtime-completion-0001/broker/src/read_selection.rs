//! Non-authorizing R03 read join. The fixed broker must first hold the commit
//! lock, establish current disclosure authority and a confirmed pointer, and
//! fetch these exact originals through held roots. This module cannot issue
//! disclosure permission or turn an unconfirmed pointer into a selection.
use crate::{generation::{self,GenerationManifest,PointerRecord,StoreSelection,Consumer},roots::{self,Binding,Error,Result,require}};
use std::collections::BTreeSet;

/// Owned immutable projection for one selected consumer operation. A later
/// pointer replacement cannot change these fields or the member byte oracle.
#[derive(Clone,Debug)]
pub struct ReadJoin {
    pub store_id:String,
    pub sequence:u64,
    pub manifest_binding:Binding,
    pub original_cut_binding:Binding,
    pub consumer_binding:Binding,
    pub disclosure_binding:Binding,
    pub operation_id:String,
    consumer_identity:String,
    consumer_paths:BTreeSet<String>,
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
        consumer_binding:consumer.adapter.clone(),disclosure_binding:disclosure_binding.clone(),
        operation_id:pointer.operation_id,consumer_identity:consumer.original_identity.clone(),
        consumer_paths:consumer.member_paths.iter().cloned().collect(),members:manifest.members})
}

impl ReadJoin {
    /// The adapter checks every original it consumes; retention of a join does
    /// not extend disclosure permission, which remains the caller's obligation.
    pub fn check_member(&self,consumer:&Consumer,path:&str,raw:&[u8])->Result<()> {
        require(consumer.adapter==self.consumer_binding && consumer.original_identity==self.consumer_identity &&
            consumer.member_paths.iter().cloned().collect::<BTreeSet<_>>()==self.consumer_paths &&
            self.consumer_paths.contains(path),"READ_MEMBER_PERMISSION")?;
        let b=self.members.get(path).ok_or(Error("READ_MEMBER_UNSELECTED"))?;
        require(raw.len() as u64==b.size_bytes && roots::hash(raw)==b.sha256,"READ_MEMBER_BYTES")
    }
}
