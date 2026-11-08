//! Versioned acyclic generation contracts. A decoded record never grants authority.
use crate::roots::{Binding, Identity, Result, require, parts, name, digest};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

pub fn canonical<T: Serialize>(value: &T) -> Result<Vec<u8>> {
    serde_json::to_vec(&serde_json::to_value(value).map_err(|_| crate::roots::Error("ENCODE"))?)
        .map_err(|_| crate::roots::Error("ENCODE"))
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MemberRole {
    pub original_identity: String, pub relative_path: String, pub semantic_role: String,
    pub writer_adapter: Binding, pub reader_adapters: Vec<Binding>, pub commit_interpretation: String,
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Consumer {
    pub original_identity: String, pub adapter: Binding, pub member_paths: Vec<String>,
    pub commit_interpretation: String,
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Limits {
    pub max_member_bytes: u64, pub max_members: u64, pub max_stage_bytes: u64,
    pub retained_generation_bytes: u64, pub retained_generation_count: u64,
    pub retained_orphan_bytes: u64, pub retained_orphan_count: u64,
    pub journal_reserve_bytes: u64, pub journal_reserve_inodes:u64, pub max_record_bytes: u64, pub max_repair_record_bytes:u64, pub in_flight: u64,
    pub verifier_timeout_ms: u64, pub max_verifier_result_bytes: u64,
}
impl Limits {
    pub fn validate(&self) -> Result<()> {
        require(self.max_member_bytes>0 && self.max_member_bytes<=1_073_741_824 &&
            (1..=1024).contains(&self.max_members) && self.max_stage_bytes>=self.max_member_bytes &&
            self.max_stage_bytes<=1_073_741_824 && self.retained_generation_bytes>=self.max_stage_bytes &&
            self.retained_generation_bytes<=1u64<<40 && (1..=4096).contains(&self.retained_generation_count) &&
            self.retained_orphan_bytes>=self.max_stage_bytes && self.retained_orphan_bytes<=1u64<<40 &&
            (1..=4096).contains(&self.retained_orphan_count) && (4096..=1_048_576).contains(&self.max_record_bytes) &&
            (4096..=1_048_576).contains(&self.max_repair_record_bytes) && self.journal_reserve_bytes>=self.max_record_bytes*32+self.max_repair_record_bytes*12 && self.journal_reserve_bytes<=1u64<<30 && (46..=65536).contains(&self.journal_reserve_inodes) &&
            self.in_flight==1 && (1..=900_000).contains(&self.verifier_timeout_ms) &&
            (1..=65536).contains(&self.max_verifier_result_bytes), "STORE_LIMITS")
    }
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StoreSelection {
    pub schema_version: String, pub store_id: String, pub instance_id: String,
    pub writer_domain: String,
    pub pointer_root_id: String, pub pointer_member: String, pub generations_root_id: String,
    pub control_root_id:String,pub control_root_binding: Binding, pub member_inventory: Vec<MemberRole>,
    pub consumer_inventory: Vec<Consumer>, pub filesystem_profile: Binding,
    pub schema_binding: Binding, pub codec_binding: Binding, pub limits: Limits,
    pub c01_selection_binding:Binding,pub canonical_member_inventory_binding:Binding,
    pub commit_interpretation_binding:Binding,pub c01_transport_limits:TransportLimits,
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TransportLimits{pub max_frame_bytes:u64,pub lock_timeout_ms:u64,pub rpc_timeout_ms:u64,pub phase_timeout_ms:u64}
impl StoreSelection {
    pub fn validate(&self) -> Result<()> {
        self.limits.validate()?; name(&self.pointer_member)?;
        require(self.schema_version=="lab-generation-store/v2" &&
            [&self.store_id,&self.instance_id].iter().all(|s|!s.is_empty()&&s.len()<=128) &&
            !self.writer_domain.is_empty() && self.writer_domain.len()<=128 && !self.control_root_id.is_empty()&&self.control_root_id.chars().count()<=4096&&
            self.pointer_root_id==self.generations_root_id && !self.pointer_root_id.is_empty() &&
            [&self.control_root_binding,&self.filesystem_profile,&self.schema_binding,&self.codec_binding,&self.c01_selection_binding,&self.canonical_member_inventory_binding,&self.commit_interpretation_binding].iter().all(|b|b.valid())&&
            (1..=1_048_576).contains(&self.c01_transport_limits.max_frame_bytes)&&[self.c01_transport_limits.lock_timeout_ms,self.c01_transport_limits.rpc_timeout_ms,self.c01_transport_limits.phase_timeout_ms].iter().all(|n|(1..=900000).contains(n)), "STORE_SCOPE")?;
        require(self.canonical_member_inventory_binding.sha256==crate::roots::hash(&canonical(&self.member_inventory)?)&&self.canonical_member_inventory_binding.size_bytes==canonical(&self.member_inventory)?.len() as u64,"ORIGINAL_MEMBER_INVENTORY")?;
        require(!self.member_inventory.is_empty() && self.member_inventory.len() as u64<=self.limits.max_members &&
            !self.consumer_inventory.is_empty() && self.consumer_inventory.len()<=1024, "STORE_INVENTORY")?;
        let mut paths=BTreeSet::new(); let mut ids=BTreeSet::new();
        for m in &self.member_inventory {
            parts(&m.relative_path)?;
            require(!m.original_identity.is_empty() && ids.insert(&m.original_identity) && paths.insert(&m.relative_path) &&
                !m.semantic_role.is_empty() && m.writer_adapter.valid() && !m.reader_adapters.is_empty() &&
                m.reader_adapters.len()<=1024 && m.reader_adapters.iter().all(|b|b.valid()) &&
                m.commit_interpretation=="generation-pointer-v1", "MEMBER_INVENTORY")?;
        }
        let mut consumers=BTreeSet::new();
        for c in &self.consumer_inventory {
            require(!c.original_identity.is_empty() && consumers.insert(&c.original_identity) && c.adapter.valid() &&
                !c.member_paths.is_empty() && c.member_paths.iter().collect::<BTreeSet<_>>().len()==c.member_paths.len() &&
                c.member_paths.iter().all(|p|paths.contains(p)) && c.commit_interpretation=="generation-pointer-v1", "CONSUMER_INVENTORY")?;
            for path in &c.member_paths {
                require(self.member_inventory.iter().find(|m|m.relative_path==*path).unwrap().reader_adapters.contains(&c.adapter), "READER_MEMBER_JOIN")?;
            }
        }
        for m in &self.member_inventory {
            let listed: BTreeSet<Vec<u8>>=m.reader_adapters.iter().map(canonical).collect::<Result<_>>()?;
            let actual: BTreeSet<Vec<u8>>=self.consumer_inventory.iter().filter(|c|c.member_paths.contains(&m.relative_path)).map(|c|canonical(&c.adapter)).collect::<Result<_>>()?;
            require(listed.len()==m.reader_adapters.len() && listed==actual,"READER_COVERAGE")?;
        }
        Ok(())
    }
}
/// Preactivation physical custody policy. In particular this is not a runtime
/// RootSelection: no activation, review, ExecutionScope or current checkpoint.
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct JournalRootPolicy {
    pub root_id:String,pub ancestors:Vec<Identity>,pub domain:crate::roots::Domain,
    pub administrator_uid:u32,pub broker_uid:u32,pub namespace_epoch:u64,
    pub alias_exclusion_binding:Binding,pub ancestor_inventory_binding:Binding,pub acl_policy_binding:Binding,
}
impl JournalRootPolicy {
    pub fn from_runtime(s:&crate::roots::Selection)->Self {Self{root_id:s.root_id.clone(),ancestors:s.ancestors.clone(),domain:s.domain,administrator_uid:s.administrator_uid,broker_uid:s.broker_uid,namespace_epoch:s.namespace_epoch,alias_exclusion_binding:s.alias_exclusion_binding.clone(),ancestor_inventory_binding:s.ancestor_inventory_binding.clone(),acl_policy_binding:s.acl_policy_binding.clone()}}
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ControlPolicy {
    pub schema_version:String,pub control_root_id:String,pub writer_domain:String,pub authority_domain:String,
    pub control_root:lab_control_store::custody::Identity,pub header_sha256:String,
    pub journal:JournalRootPolicy,
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GenerationManifest {
    pub schema_version: String, pub store_id: String, pub creation_instance: String,
    pub writer_epoch: u64, pub sequence: u64, pub generation_id: String,
    pub predecessor_pointer_binding: Option<Binding>, pub operation_id: String,
    pub original_fingerprint: String, pub stage_creation_binding: Binding,
    pub member_manifest_binding: Binding, pub stage_identity: Identity,
    pub members: BTreeMap<String,Binding>, pub original_cut_binding: Binding,pub source_cut:String,
    pub reader_inventory_binding: Binding, pub expected_replay_result_binding: Binding,
}
/// Pre-existing expectation, selected before the manifest. The expected native
/// payload is a deterministic original replay report under these exact adapters
/// and cut. It cannot name the future generation/manifest/activation/result.
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ReplayExpectation {
    pub schema_version:String,pub original_cut_binding:Binding,pub source_cut:String,
    pub member_inventory_binding:Binding,pub reader_inventory_binding:Binding,
    pub adapter_bindings:Vec<Binding>,pub cardinalities:BTreeMap<String,u64>,
    pub native_report_sha256:String,pub native_report_size_bytes:u64,
}
impl ReplayExpectation {
    pub fn validate(&self)->Result<()>{require(self.schema_version=="lab-generation-replay-expectation/v1"&&!self.source_cut.is_empty()&&self.source_cut.chars().count()<=4096&&
        [&self.original_cut_binding,&self.member_inventory_binding,&self.reader_inventory_binding].iter().all(|b|b.valid())&&
        !self.adapter_bindings.is_empty()&&self.adapter_bindings.len()<=128&&self.adapter_bindings.iter().all(Binding::valid)&&
        self.adapter_bindings.iter().map(canonical).collect::<Result<BTreeSet<_>>>()?.len()==self.adapter_bindings.len()&&
        !self.cardinalities.is_empty()&&self.cardinalities.len()<=1024&&self.cardinalities.iter().all(|(k,v)|!k.is_empty()&&k.len()<=128&&*v<=i64::MAX as u64)&&
        digest(&self.native_report_sha256)&&self.native_report_size_bytes<=65536,"REPLAY_EXPECTATION")}
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PointerRecord {
    pub schema_version:String,pub logical_store_id:String,pub writer_epoch:u64,pub sequence:u64,
    pub predecessor_pointer_binding:Option<Binding>,pub generation_manifest_binding:Binding,pub operation_id:String,
}
impl PointerRecord {
    pub fn validate(&self)->Result<()> {
        require(self.schema_version=="lab-completion-pointer-record/v1" && !self.logical_store_id.is_empty() && self.logical_store_id.chars().count()<=4096 && !self.operation_id.is_empty() && self.operation_id.chars().count()<=4096 &&
            self.writer_epoch>0 && self.writer_epoch<=i64::MAX as u64 && self.sequence>0 && self.sequence<=i64::MAX as u64 &&
            self.generation_manifest_binding.valid() && self.predecessor_pointer_binding.as_ref().is_none_or(Binding::valid), "POINTER_SCHEMA")
    }
}
/// Versioned, deterministic writer-profile -> C01 adapter. The original C01
/// bytes are retained and compared; equal meaning is never an equal binding.
pub fn c01_store(s:&StoreSelection)->Result<Vec<u8>>{
    let mut consumers=Vec::new();for c in &s.consumer_inventory{for path in &c.member_paths{let m=s.member_inventory.iter().find(|m|&m.relative_path==path).ok_or(crate::roots::Error("CONSUMER_MEMBER"))?;consumers.push(serde_json::json!({"identity":c.original_identity,"relative_path":path,"semantic_role":m.semantic_role,"reader_adapter_binding":c.adapter,"writer_adapter_binding":m.writer_adapter,"commit_interpretation_binding":s.commit_interpretation_binding}));}}
    canonical(&serde_json::json!({"schema_version":"lab-completion-generation-store-selection/v1","logical_store_id":s.store_id,"instance_id":s.instance_id,"broker_writer_domain":s.writer_domain,"pointer_root_id":s.pointer_root_id,"pointer_member":s.pointer_member,"generations_root_id":s.generations_root_id,"control_root_id":s.control_root_id,"canonical_member_inventory_binding":s.canonical_member_inventory_binding,"canonical_consumer_inventory":consumers,"filesystem_profile_binding":s.filesystem_profile,"schema_binding":s.schema_binding,"codec_binding":s.codec_binding,"limits":{"max_frame_bytes":s.c01_transport_limits.max_frame_bytes,"max_member_bytes":s.limits.max_member_bytes,"max_member_count":s.limits.max_members,"max_stage_bytes":s.limits.max_stage_bytes,"max_retained_generation_bytes":s.limits.retained_generation_bytes,"max_retained_generation_count":s.limits.retained_generation_count,"max_retained_orphan_bytes":s.limits.retained_orphan_bytes,"max_retained_orphan_count":s.limits.retained_orphan_count,"journal_control_reserve_bytes":s.limits.journal_reserve_bytes,"max_inflight_operations":s.limits.in_flight,"lock_timeout_ms":s.c01_transport_limits.lock_timeout_ms,"rpc_timeout_ms":s.c01_transport_limits.rpc_timeout_ms,"phase_timeout_ms":s.c01_transport_limits.phase_timeout_ms}}))
}
pub fn c01_manifest(m:&GenerationManifest)->Result<Vec<u8>>{
    require(!m.source_cut.is_empty()&&m.source_cut.chars().count()<=4096,"SOURCE_CUT")?;
    canonical(&serde_json::json!({"schema_version":"lab-completion-generation-manifest/v1","logical_store_id":m.store_id,"creation_instance_id":m.creation_instance,"writer_epoch":m.writer_epoch,"sequence":m.sequence,"generation_id":m.generation_id,"predecessor_pointer_binding":m.predecessor_pointer_binding,"operation_fingerprint":m.original_fingerprint,"member_bindings":m.members.values().collect::<Vec<_>>(),"source_cut":m.source_cut,"reader_inventory_binding":m.reader_inventory_binding,"expected_replay_result_binding":m.expected_replay_result_binding}))
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ColdRequest {
    #[serde(default,skip_serializing_if="Option::is_none")]
    pub repair_intent_binding:Option<Binding>,
    pub schema_version:String,pub store_selection_binding:Binding,pub pointer_binding:Binding,
    pub generation_manifest_binding:Binding,pub writer_profile_binding:Binding,pub member_manifest_binding:Binding,
    pub original_cut_binding:Binding,pub expected_replay_result_binding:Binding,
    pub replay_expectation:ReplayExpectation,
    pub verifier_executable_binding:Binding,pub verifier_input_bindings:Vec<Binding>,
    pub broker_uid:u32,pub worker_uid:u32,pub timeout_ms:u64,pub max_result_bytes:u64,
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ColdResult {
    pub schema_version:String,pub request_sha256:String,pub executable_binding:Binding,
    pub input_bindings:Vec<Binding>,pub manifest_binding:Binding,pub original_cut_binding:Binding,
    pub expected_contract_binding:Binding,pub native_report_binding:Binding,
    pub observed_cardinalities:BTreeMap<String,u64>,pub observed_adapter_bindings:Vec<Binding>,
    pub actual_exit:Option<i32>,pub outcome:String,
    pub cleanup:String,pub workload_uid:u32,pub elapsed_ms:u64,
}
pub fn validate_cold(request:&ColdRequest,raw:&[u8])->Result<ColdResult> {
    require(match (&*request.schema_version,&request.repair_intent_binding){("lab-generation-cold-request/v1",None)=>true,("lab-generation-repair-cold-request/v1",Some(b))=>b.valid(),_=>false},"COLD_REQUEST_PROFILE")?;
    require(raw.len() as u64<=request.max_result_bytes,"COLD_RESULT_BOUND")?;
    let r:ColdResult=serde_json::from_slice(raw).map_err(|_|crate::roots::Error("COLD_RESULT_SCHEMA"))?;
    require(canonical(&r)?==raw && r.schema_version=="lab-generation-cold-result/v1" &&
        digest(&r.request_sha256) && r.request_sha256==crate::roots::hash(&canonical(request)?) &&
        r.executable_binding==request.verifier_executable_binding && r.input_bindings==request.verifier_input_bindings &&
        r.manifest_binding==request.generation_manifest_binding && r.original_cut_binding==request.original_cut_binding &&
        r.expected_contract_binding==request.expected_replay_result_binding && r.native_report_binding.valid() &&
        r.native_report_binding.sha256==request.replay_expectation.native_report_sha256&&r.native_report_binding.size_bytes==request.replay_expectation.native_report_size_bytes&&
        r.observed_cardinalities==request.replay_expectation.cardinalities&&r.observed_adapter_bindings==request.replay_expectation.adapter_bindings&&r.workload_uid==request.worker_uid &&
        r.workload_uid!=request.broker_uid && r.elapsed_ms<=request.timeout_ms &&
        r.actual_exit==Some(0) && r.outcome=="PASS" && r.cleanup=="clean","COLD_RESULT_MISMATCH")?;
    Ok(r)
}
