//! Fixed broker composition. This file is compiled by the unit-owned binary
//! closure; accepted predecessor Cargo/source files are not extended in place.
//! No request-supplied callback, path loader, signer, or currentness flag enters
//! the dispatch decision. Every input is read through the current host selection.
use crate::{state::{self, *},quota,members,commit,generation,roots::{self,Binding,Domain,Error,Exclusive,Result,require}};
use lab_completion_broker::{self as wire,authority};
use lab_control_store::{custody::{Held,Root as ControlRoot},ledger::{self,Ledger,HostConfirmation,Change,Outcome}};
use ed25519_dalek::SigningKey;
use serde::{Serialize,Deserialize};
use serde_json::{Value,json};
use std::{collections::BTreeMap,fs::File,time::Duration};

fn value<T:Serialize>(v:&T)->Result<Value>{serde_json::to_value(v).map_err(|_|Error("ENCODE"))}
fn control_binding(b:&Binding)->ledger::ByteBinding{ledger::ByteBinding{kind:b.kind.clone(),root_id:b.root_id.clone(),relative_path:b.relative_path.clone(),sha256:b.sha256.clone(),size_bytes:b.size_bytes}}
fn seconds_to_ns(n:u64)->Result<u64>{n.checked_mul(1_000_000_000).filter(|n|*n<=i64::MAX as u64).ok_or(Error("AUTHORITY_TIME_DOMAIN"))}

pub struct FixedControlClient {
    channel:Channel,signer:SelectedSigner,service:Binding,recipient:Caller,
}
impl FixedControlClient {
    pub fn new(channel:Channel,signer:SelectedSigner,service:Binding,recipient:Caller)->Result<Self>{
        require(service.valid()&&channel.selection().channel_binding.valid()&&signer.purpose()=="control-confirmation","CONTROL_CLIENT_SELECTION")?;
        Ok(Self{channel,signer,service,recipient})
    }
    pub fn confirm(&self,prior:&HostConfirmation,desired:&HostConfirmation,expires:u64)->Result<HostConfirmation>{
        let now=now_seconds()?;
        let request=ControlCasRequest{schema_version:"lab-broker-control-cas-request/v1".into(),service_selection_binding:self.service.clone(),
            prior:prior.clone(),desired:desired.clone(),recipient:self.recipient.clone(),channel_binding:self.channel.selection().channel_binding.clone(),
            challenge:challenge()?,not_before:now,expires_at:expires.min(now.saturating_add(60))};
        require(request.not_before<request.expires_at,"CONTROL_CAS_EXPIRED")?;
        let raw=self.channel.call(&encode(&request)?)?;
        let proof:ControlCasProof=self.signer.verify(&raw)?;
        require(proof.schema_version=="lab-broker-control-cas-proof/v1"&&proof.request==request&&proof.result=="confirmed"
            &&proof.signer_enrollment_binding==*self.signer.binding()&&proof.ordinal>0,"CONTROL_CAS_REPLY")?;
        // The exact pending checkpoint can settle after producer expiry. This
        // fresh control CAS's own interval must still be current at receipt.
        require(now_seconds()?<request.expires_at,"CONTROL_CAS_REPLY_EXPIRED_UNCERTAIN")?;
        Ok(proof.request.desired)
    }
    pub fn inspect(&self,expires:u64)->Result<(ControlInspectionProof,Option<Vec<u8>>)> {
        let now=now_seconds()?;let query=ControlInspectionRequest{schema_version:"lab-broker-control-inspection-request/v1".into(),
            service_selection_binding:self.service.clone(),recipient:self.recipient.clone(),channel_binding:self.channel.selection().channel_binding.clone(),
            challenge:challenge()?,not_before:now,expires_at:expires.min(now.saturating_add(60))};
        let raw=self.channel.call(&encode(&query)?)?;let current:ControlInspectionProof=self.signer.verify(&raw)?;
        require(current.schema_version=="lab-broker-control-inspection/v1"&&current.query==query&&now_seconds()?<query.expires_at,"CONTROL_INSPECTION_REPLY")?;
        let original=if let Some(binding)=&current.original_proof_binding {
            let original=self.channel.call(&encode(&ControlOriginalRequest{schema_version:"lab-broker-control-original-request/v1".into(),query:query.clone(),original_binding:binding.clone()})?)?;
            require(bound(&binding.root_id,&binding.relative_path,&original)?==*binding,"CONTROL_ORIGINAL_REPLY")?;
            let proof:ControlCasProof=self.signer.verify(&original)?;
            require(proof.request.desired.head==current.confirmation.head&&proof.request.desired.root==current.confirmation.root
                &&proof.ordinal==current.ordinal&&roots::hash(&original)==current.witness_sha256,"CONTROL_INSPECTION_ORIGINAL_JOIN")?;Some(original)
        }else{require(current.ordinal==0,"CONTROL_INSPECTION_MISSING_ORIGINAL")?;None};
        require(now_seconds()?<query.expires_at,"CONTROL_INSPECTION_EXPIRED")?;Ok((current,original))
    }
}
pub struct FixedPrefixClient {channel:Channel,signer:SelectedSigner}
impl FixedPrefixClient {
    pub fn new(channel:Channel,signer:SelectedSigner)->Self{Self{channel,signer}}
    fn confirm(&self,request:&PrefixRequest)->Result<VerifiedPrefix>{
        let selected=request.current_admission.as_ref().map(|a|&a.inspection.request.channel_binding).unwrap_or(&request.scope.channel_binding);
        require(selected==&self.channel.selection().channel_binding,"PREFIX_CURRENT_CHANNEL")?;let raw=self.channel.call(&encode(request)?)?;VerifiedPrefix::verify(&raw,&self.signer,request,now_seconds()?)}
    pub(crate) fn current(&self,request:&PrefixInspectionRequest,scope:&PrefixScope,binding:&Binding)->Result<CurrentPrefix>{
        let raw=self.channel.call(&encode(request)?)?;CurrentPrefix::verify(&raw,&self.signer,request,scope,binding,now_seconds()?)
    }
    pub(crate) fn original(&self,current:&CurrentPrefix,scope:&PrefixScope)->Result<VerifiedPrefix>{
        let raw=self.channel.call(&encode(&current.original_request()?)?)?;current.verify_original(&raw,&self.signer,scope)
    }
}

/// Independently selected capture original; never computed from the permit being checked.
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct MemberIdentityOriginal {pub schema_version:String,pub operation:ledger::Operation,
    pub root_id:String,pub member:String,pub identity_binding:Value}

/// Exact fixed configuration is an input selected by the independent launch,
/// never by a BrokerRequest. All referenced bytes must also be in current
/// HostFacts.selected_inputs, so changed/cross-operation selections refuse.
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct RuntimeSelection {
    pub schema_version:String,pub receipt_root_id:String,pub stage_root_id:String,
    pub generation_root_id:String,pub generation_journal_root_id:String,pub control_root_id:String,
    pub original_scope_binding:Binding,pub limits_binding:Binding,pub receipt_signer_binding:Binding,
    pub receipt_private_key_binding:Binding,pub commit_selection_binding:Option<Binding>,
    pub restart_selection_binding:Option<Binding>,pub supervisor_proof_binding:Option<Binding>,
    pub derived_selection_binding:Option<Binding>,pub global_order_binding:Binding,
}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct GlobalOrderOriginal {pub schema_version:String,pub control_root:lab_control_store::custody::Identity,
    pub authority_domain:String,pub order:Vec<String>,pub roots:Vec<roots::Selection>,pub not_before:u64,pub expires_at:u64}
/// Fixed, reachable loader for actual parent-root capabilities. The authentic
/// host observation/enrollment and nonrollback deployment are external facts;
/// parsing, exact joins, held global lock checks and root opening are here.
/// This object cannot outlive the accepted continuously held Journal rank.
pub struct FixedRootSet<'a> {roots:BTreeMap<String,roots::Root>,parents:BTreeMap<String,roots::ParentHold>,held:&'a Held<'a>,expires:u64}
impl<'a> FixedRootSet<'a>{
    pub(crate) fn load(facts:&VerifiedHostFacts,held:&'a Held<'a>,control:&ControlRoot,
        runtime:&RuntimeSelection,order_raw:&[u8])->Result<Self>{
        facts.current()?;held.nested().map_err(|_|Error("GLOBAL_CUSTODY"))?;
        require(held.rank()==lab_control_store::custody::Rank::Journal&&facts.facts().domain==Domain::Actual,"ACTUAL_GLOBAL_PARENT")?;
        require(bound(&runtime.global_order_binding.root_id,&runtime.global_order_binding.relative_path,order_raw)?==runtime.global_order_binding
            &&facts.facts().selected_inputs.contains(&runtime.global_order_binding),"GLOBAL_ORDER_ORIGINAL")?;
        let order:GlobalOrderOriginal=decode(order_raw,quota::MAX_PACKET)?;
        let now=now_seconds()?;
        require(order.schema_version=="lab-broker-global-order/v1"&&order.control_root==control.identity()
            &&order.authority_domain==facts.facts().authority_domain&&order.not_before<=now&&now<order.expires_at
            &&order.order==["source-slot","publication","replay","native","journal"]
            &&encode(&order.roots)?==encode(&facts.facts().roots)?,"GLOBAL_ORDER_SELECTION")?;
        facts.open_ledger(control,held)?;
        let mut roots=BTreeMap::new();let mut parents=BTreeMap::new();let mut physical=std::collections::BTreeSet::new();
        for s in &order.roots {
            let root=roots::Root::open(s.clone(),Domain::Actual)?;
            require(physical.insert((root.identity().device,root.identity().inode)),"GLOBAL_ROOT_ALIAS")?;
            let parent=roots::ParentHold{root:root.identity().clone(),execution_scope:s.execution_scope.clone(),namespace_epoch:s.namespace_epoch,
                alias_exclusion_binding:s.alias_exclusion_binding.clone(),ancestor_inventory_binding:s.ancestor_inventory_binding.clone(),
                acl_policy_binding:s.acl_policy_binding.clone(),global_order_binding:runtime.global_order_binding.clone()};
            require(parents.insert(s.root_id.clone(),parent).is_none()&&roots.insert(s.root_id.clone(),root).is_none(),"GLOBAL_ROOT_DUPLICATE")?;
        }
        facts.current()?;Ok(Self{roots,parents,held,expires:order.expires_at.min(facts.facts().expires_at)})
    }
    pub(crate) fn borrow(&self)->Result<BTreeMap<String,Exclusive<'_>>>{
        self.held.nested().map_err(|_|Error("GLOBAL_CUSTODY"))?;require(now_seconds()?<self.expires,"PARENT_SELECTION_EXPIRED")?;
        self.roots.iter().map(|(id,root)|Ok((id.clone(),root.under_parent(&self.parents[id])?))).collect()
    }
}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct CommitSelection {
    pub schema_version:String,pub store_binding:Binding,pub manifest_binding:Binding,
    pub expectation_binding:Binding,pub c01_store_binding:Binding,pub policy_binding:Binding,
    pub runtime_selection:commit::RuntimeCommitSelection,pub old_pointer_binding:Option<Binding>,
    pub prior:commit::PriorInventory,pub member_manifest_binding:Binding,
    pub verifier_executable:Binding,pub verifier_inputs:Vec<Binding>,pub verifier_uid:u32,
    pub reserve_binding:Binding,
}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct RestartInputs {
    pub schema_version:String,pub commit_selection_binding:Binding,pub selection:commit::RestartSelection,
    pub kind:commit::RepairKind,pub verifier:Option<commit::RepairVerifier>,pub authority_original_binding:Binding,
}
/// Exact original native supervisor evidence. This adapter verifies closed
/// terminal/custody joins without importing the still separate supervisor unit.
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct SupervisorClosure {
    pub schema_version:String,pub operation:ledger::Operation,pub execution_scope:roots::ExecutionScope,
    pub control_confirmation:HostConfirmation,pub authority_binding:Binding,
    #[serde(default,skip_serializing_if="Option::is_none")]
    pub prior_close_terminal:Option<Binding>,
    pub original_terminal_binding:Binding,pub containment_selection_binding:Binding,pub native_evidence_binding:Binding,
    pub worker_identity_binding:Binding,pub cleanup_original_binding:Binding,
    pub populated:bool,pub all_owned_children_reaped:bool,pub cleanup:String,pub outcome:String,
    pub not_before:u64,pub expires_at:u64,
}

#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct CloseLedgerTerminal {schema_version:String,operation:ledger::Operation,supervisor_closure_binding:Binding,
    native_terminal_binding:Binding,request_intent_binding:Binding,request_frame_binding:Binding,control_preimage:HostConfirmation}

pub enum DispatchResult {
    /// Only an independently confirmed prefix may supply this exact original.
    Reply(Vec<u8>),
    /// U08-02 receives this typed request while this Session still owns all
    /// borrowed global locks. No stable read or committed response is available.
    PendingCold(generation::ColdRequest),
}
struct PendingCommit {sequence:PendingSequence,frame:Vec<u8>,admission:authority::ControlSnapshot,request:generation::ColdRequest}
/// Root/Held/transport lifetimes deliberately outlive this session. There is
/// no deserialization constructor for a live writer and no restarted producer.
pub struct Session<'a> {
    host:&'a FixedHost,control_rpc:&'a FixedControlClient,prefix_rpc:&'a FixedPrefixClient,
    control_root:&'a ControlRoot,held:&'a Held<'a>,roots:BTreeMap<String,&'a Exclusive<'a>>,
    selected:RuntimeSelection,selection_binding:Binding,limits:quota::Limits,
    journal:ReceiptJournal<'a>,stage:Option<members::Stage<'a>>,commit:Option<commit::Commit<'a>>,
    recovery:Option<commit::RecoveryCommit<'a>>,pending:Option<PendingCommit>,
    response_signer:SelectedSigner,response_key:SigningKey,confirmation:HostConfirmation,
    fenced:bool,restart_only:bool,
}
impl<'a> Session<'a> {
    /// Statically linked U08 glue owns the bounded loop. No request selects a
    /// callback; this method sends only fully confirmed original responses.
    /// PendingCold returns while Session and all its borrowed locks stay live.
    pub(crate) fn serve_one(&mut self,client:&Channel)->Result<Option<generation::ColdRequest>>{
        require(encode(client.selection())?==encode(&self.host.selection().client_channel)?,"FIXED_CLIENT_CHANNEL")?;
        let raw=client.receive()?;
        match self.dispatch(&raw)?{DispatchResult::Reply(raw)=>{client.send(&raw)?;Ok(None)},DispatchResult::PendingCold(request)=>Ok(Some(request))}
    }
    pub(crate) fn send_completed_cold(&mut self,client:&Channel,observation:commit::ColdObservation)->Result<()>{
        require(encode(client.selection())?==encode(&self.host.selection().client_channel)?,"FIXED_CLIENT_CHANNEL")?;
        match self.complete_cold(observation)?{DispatchResult::Reply(raw)=>client.send(&raw),_=>Err(Error("COLD_TERMINAL_REQUIRED"))}
    }
    /// A fixed verifier reports only this closed failure vocabulary. Retain
    /// the exact original request; no result/Outcome or success is fabricated.
    pub(crate) fn fail_cold(&mut self,reason:ColdFailure,elapsed_ms:u64)->Result<()> {
        require(!self.fenced&&self.pending.is_some(),"NO_LIVE_COLD_CONTINUATION")?;
        self.fenced=true;let p=self.pending.as_mut().ok_or(Error("PENDING_SEQUENCE_MISSING"))?;
        require(elapsed_ms<=86400000,"COLD_FAILURE_TIME_BOUND")?;
        let raw=encode(&json!({"schema_version":"lab-broker-pending-cold-failure/v1","request_binding":bound(&self.selected.receipt_root_id,&format!("sequence-{:016}/cold-request.json",p.sequence.ordinal()),&encode(&p.request)?)?,"reason":reason,"elapsed_ms":elapsed_ms,"effect_state":"unknown","outcome":"UNKNOWN"}))?;
        self.journal.put(&mut p.sequence,"cold-failure.json",&raw)?;Ok(())
    }
    fn root(&self,id:&str)->Result<&'a Exclusive<'a>>{self.roots.get(id).copied().ok_or(Error("ROOT_NOT_SELECTED"))}
    fn effect_input(&self,facts:&VerifiedHostFacts,role:&str)->Result<Binding>{
        let (fixed,current)=match role{"commit"=>(&self.selected.commit_selection_binding,&facts.facts().effect_inputs.commit),
            "restart"=>(&self.selected.restart_selection_binding,&facts.facts().effect_inputs.restart),
            "supervisor"=>(&self.selected.supervisor_proof_binding,&facts.facts().effect_inputs.supervisor),
            "derived"=>(&self.selected.derived_selection_binding,&facts.facts().effect_inputs.derived),_=>return Err(Error("CLOSED_EFFECT_INPUT_ROLE"))};
        let selected=current.as_ref().ok_or(Error("CURRENT_EFFECT_INPUT_REQUIRED"))?;
        require(selected.valid()&&fixed.as_ref().is_none_or(|b|b==selected),"FIXED_EFFECT_INPUT_NARROWING")?;Ok(selected.clone())
    }
    fn read(&self,facts:&VerifiedHostFacts,binding:&Binding,max:u64)->Result<Vec<u8>>{
        let roots=self.roots.iter().map(|(id,h)|(id.clone(),h.root())).collect();facts.read_selected(&roots,binding,max)
    }
    fn current_ledger(&self,facts:&VerifiedHostFacts)->Result<Ledger<'a>>{
        self.held.nested().map_err(|_|Error("GLOBAL_CUSTODY"))?;
        require(facts.facts().ledger_confirmation==self.confirmation,"CURRENT_CONTROL_SELECTION_DRIFT")?;
        let ledger=facts.open_ledger(self.control_root,self.held)?;
        let present=ledger.operation(&facts.facts().operation.operation_id);
        require(present.is_none_or(|o|o==&facts.facts().operation),"ORIGINAL_OPERATION_DRIFT")?;Ok(ledger)
    }
    /// Only fixed launch code calls this after authenticating current prefix
    /// genesis, all roots, exact role keys, and an absent original operation.
    pub(crate) fn start(host:&'a FixedHost,control_rpc:&'a FixedControlClient,prefix_rpc:&'a FixedPrefixClient,
        control_root:&'a ControlRoot,held:&'a Held<'a>,roots:BTreeMap<String,&'a Exclusive<'a>>,
        selected_raw:&[u8],selection_binding:Binding,facts:VerifiedHostFacts,current:CurrentPrefix,
        response_signer:SelectedSigner,response_key:SigningKey)->Result<Self>{
        Self::open(host,control_rpc,prefix_rpc,control_root,held,roots,selected_raw,selection_binding,facts,current,response_signer,response_key,false)
    }
    pub(crate) fn restart(host:&'a FixedHost,control_rpc:&'a FixedControlClient,prefix_rpc:&'a FixedPrefixClient,
        control_root:&'a ControlRoot,held:&'a Held<'a>,roots:BTreeMap<String,&'a Exclusive<'a>>,
        selected_raw:&[u8],selection_binding:Binding,facts:VerifiedHostFacts,current:CurrentPrefix,
        response_signer:SelectedSigner,response_key:SigningKey)->Result<Self>{
        Self::open(host,control_rpc,prefix_rpc,control_root,held,roots,selected_raw,selection_binding,facts,current,response_signer,response_key,true)
    }
    fn open(host:&'a FixedHost,control_rpc:&'a FixedControlClient,prefix_rpc:&'a FixedPrefixClient,
        control_root:&'a ControlRoot,held:&'a Held<'a>,roots:BTreeMap<String,&'a Exclusive<'a>>,
        selected_raw:&[u8],selection_binding:Binding,facts:VerifiedHostFacts,current:CurrentPrefix,
        response_signer:SelectedSigner,response_key:SigningKey,restart:bool)->Result<Self>{
        require(bound(&selection_binding.root_id,&selection_binding.relative_path,selected_raw)?==selection_binding,"RUNTIME_SELECTION_BYTES")?;
        let selected:RuntimeSelection=decode(selected_raw,quota::MAX_PACKET)?;
        require(selected.schema_version=="lab-broker-runtime-selection/v1"&&selected.global_order_binding.valid()
            &&selected.receipt_signer_binding==*response_signer.binding()&&selected.limits_binding==facts.facts().quota_binding
            &&selected.original_scope_binding==host.selection().original_scope_binding,"RUNTIME_SELECTION_JOIN")?;
        let map=roots.iter().map(|(id,h)|(id.clone(),h.root())).collect();
        let issuer_raw=facts.read_selected(&map,&facts.facts().issuer_enrollment_binding,8192)?;
        host.check_role_keys(&response_signer,&prefix_rpc.signer,&control_rpc.signer,&issuer_raw)?;
        require(encode(prefix_rpc.channel.selection())?==encode(&host.selection().prefix_channel)?
            &&encode(control_rpc.channel.selection())?==encode(&host.selection().control_channel)?
            &&control_rpc.service==host.selection().control_service_binding&&control_rpc.recipient==host.selection().broker_identity,"FIXED_SERVICE_CHANNEL_SELECTION")?;
        let selected_key=facts.read_selected(&map,&selected.receipt_private_key_binding,64)?;
        require(response_signer.signing_key(&selected_key)?.to_bytes()==response_key.to_bytes(),"FIXED_RESPONSE_PRIVATE_KEY")?;
        let scope_raw=facts.read_selected(&map,&selected.original_scope_binding,quota::MAX_PACKET)?;
        let scope:PrefixScope=decode(&scope_raw,quota::MAX_PACKET)?;scope.validate()?;
        require(scope.operation==host.selection().operation&&(!restart||scope.execution_scope.store_id==facts.facts().scope.store_id)
            &&(restart||scope.execution_scope==facts.facts().scope)
            &&scope.control_root==control_root.identity()&&(restart||scope.recipient==host.selection().broker_identity),"RUNTIME_ORIGINAL_SCOPE")?;
        current.check_admission(&prefix_rpc.signer,&selected.original_scope_binding,facts.facts(),&host.selection().broker_identity,&host.selection().prefix_channel.channel_binding)?;
        let ledger=facts.open_ledger(control_root,held)?;
        if restart{require(ledger.operation(&scope.operation.operation_id)==Some(&scope.operation),"RESTART_ORIGINAL_OPERATION")?;}
        else{require(current.head()==&PrefixHead::genesis(&scope)?,"FRESH_GENESIS_REQUIRED")?;
            require(facts.facts().operation_state==OriginalOperationState::AbsentReservable
                &&ledger.operation(&scope.operation.operation_id).is_none(),"UNFINISHED_RESTART_REQUIRES_RECONCILIATION")?;}
        let limits:quota::Limits=decode(&facts.read_selected(&map,&selected.limits_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        let receipt=roots.get(&selected.receipt_root_id).copied().ok_or(Error("RECEIPT_ROOT"))?;
        let journal=if restart{RestartedPrefix::inspect_recovery(receipt,scope,limits.clone(),current,&prefix_rpc.signer,&response_signer)?.into_recovery_journal()}
            else{ReceiptJournal::open_empty(receipt,scope,limits.clone())?};
        Ok(Self{host,control_rpc,prefix_rpc,control_root,held,roots,selected,selection_binding,limits,journal,
            stage:None,commit:None,recovery:None,pending:None,response_signer,response_key,
            confirmation:facts.facts().ledger_confirmation.clone(),fenced:false,restart_only:restart})
    }
    /// Renewal is compared with the first independently selected captured
    /// original already acknowledged in this operation's immutable prefix.
    /// A new manager profile cannot silently replace that original identity.
    fn captured_member(&self,frame:&wire::Frame,facts:&VerifiedHostFacts)->Result<(Binding,Vec<u8>,MemberIdentityOriginal)>{
        let mut selected=None;
        for binding in &facts.facts().member_identity_originals {
            let raw=self.read(facts,binding,quota::MAX_PACKET)?;
            let original:MemberIdentityOriginal=decode(&raw,quota::MAX_PACKET)?;
            require(original.schema_version=="lab-broker-captured-member-identity/v1"&&original.operation==facts.facts().operation,"CAPTURED_MEMBER_OPERATION")?;
            if original.root_id==frame.request()["payload"]["root_id"]&&original.member==frame.request()["payload"]["member"]{
                require(selected.is_none(),"CAPTURED_MEMBER_AMBIGUOUS")?;
                wire::validate_content_digest(&original.identity_binding).map_err(|_|Error("CAPTURED_MEMBER_DIGEST"))?;
                selected=Some((binding.clone(),raw,original));
            }
        }
        let selected=selected.ok_or(Error("CAPTURED_MEMBER_NOT_SELECTED"))?;
        for e in self.journal.confirmed_entries(&self.prefix_rpc.signer,&self.response_signer)?{
            if e.entry.intent.verb!="write_member"{continue}
            let rb=e.entry.originals.get("captured-member.json").ok_or(Error("CAPTURED_MEMBER_ORIGINAL_MISSING"))?;
            let raw=state::read_owned(self.root(&self.selected.receipt_root_id)?,rb,quota::MAX_PACKET)?;
            let retained:MemberIdentityOriginal=decode(&raw,quota::MAX_PACKET)?;
            if retained.root_id==selected.2.root_id&&retained.member==selected.2.member{
                let sb=e.entry.originals.get("captured-selection.json").ok_or(Error("CAPTURED_MEMBER_SELECTION_MISSING"))?;
                let original_binding:Binding=decode(&state::read_owned(self.root(&self.selected.receipt_root_id)?,sb,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
                require(original_binding==selected.0&&raw==selected.1,"CAPTURED_MEMBER_RENEWAL_CHANGED")?;
            }
        }
        Ok(selected)
    }
    fn control_snapshot(&self,frame:&wire::Frame,frame_raw:&[u8],facts:&VerifiedHostFacts,core:&Value)->Result<authority::ControlSnapshot>{
        let f=facts.facts();let now=now_seconds()?;facts.current()?;
        let disclosure=matches!(frame.request()["verb"].as_str(),Some("read_receipt"|"inspect"|"inspect_operation"));
        let entries=if disclosure{self.journal.confirmed_entries(&self.prefix_rpc.signer,&self.response_signer)?}else{self.journal.entries()?};let last=entries.last();
        let phase=if self.fenced||self.restart_only{"UNKNOWN"}else{last.map_or("absent",|e|e.entry.phase.as_str())};
        let snapshot=if disclosure||self.restart_only{entries.iter().rev().find_map(|e|e.snapshot.clone())}else{self.stage.as_ref().map(members::Stage::snapshot).transpose()?};
        let stage_binding=snapshot.as_ref().and_then(|s|s.stage_binding.as_ref()).map(value).transpose()?.unwrap_or(Value::Null);
        let requested_sequence=frame.request()["sequence"].as_u64().ok_or(Error("SEQUENCE"))?;
        let recorded=entries.iter().find(|e|e.entry.intent.sequence==requested_sequence);
        let member=frame.request()["payload"]["member"].as_str().and_then(|name|snapshot.as_ref().and_then(|s|s.members.get(name)));
        let next_offset=member.map_or(0,|m|m.ranges.iter().map(|r|r.length).sum());
        let member_binding=if frame.request()["verb"]=="write_member"{
            Some(self.captured_member(frame,facts)?.2.identity_binding)
        }else{None};
        let _=frame_raw;
        let consumed=self.journal.consumed_requests()?;
        let consumed_record=consumed.get(&requested_sequence);
        let next_sequence=consumed.keys().next_back().map_or(Ok(0),|n|n.checked_add(1).ok_or(Error("SEQUENCE_OVERFLOW")))?;
        let cumulative_bytes=snapshot.as_ref().map_or(0,|s|s.members.values().flat_map(|m|m.ranges.iter()).map(|r|r.length).sum::<u64>());
        let issuer_raw=self.read(facts,&f.issuer_enrollment_binding,8192)?;
        Ok(authority::ControlSnapshot{domain:if f.domain==Domain::Fixture{authority::TrustDomain::Fixture}else{authority::TrustDomain::Actual},caller:self.host.selection().caller.peer(),
            now:now as i64,activation_expires_at:f.activation_expires_at as i64,operation_id:f.operation.operation_id.clone(),live_scope:f.live_authority_scope.clone(),
            selected_roots:f.roots.iter().map(|r|r.root_id.clone()).collect(),issuer_currentness:authority::IssuerCurrentness{enrollment_digest:wire::content_digest(&issuer_raw),revocation_binding:value(&f.revocation_binding)?,revoked:f.issuer_revoked,checked_at:now as i64},
            disclosure_subjects:f.disclosure_subjects.iter().map(value).collect::<Result<_>>()?,recovery:f.recovery.as_ref().map(|r|Ok::<_,Error>(authority::RecoverySelection{authorization_digest:r.authorization_binding.clone(),subject_binding:value(&r.subject_binding)?,preimages:r.preimages.iter().map(value).collect::<Result<_>>()?,action:r.action.clone(),consumed:r.consumed})).transpose()?,
            recorded_request:consumed_record.map(|digest|authority::RecordedRequest{sequence:requested_sequence as i64,wire_digest:digest.clone()}),operation_fingerprint:f.operation.fingerprint.clone(),stage_binding,member_binding,
            original_deadline:core["operation_expires_at"].as_i64().ok_or(Error("ORIGINAL_DEADLINE"))?,phase:phase.into(),next_sequence:next_sequence as i64,next_offset:next_offset as i64,cumulative_bytes:cumulative_bytes as i64,
            cumulative_actions:consumed.len() as i64,acknowledgment_uncertain:if disclosure&&recorded.is_some(){false}else{self.fenced||self.journal.is_pending()},replay:recorded.and_then(|e|e.entry.originals.get("response.json").map(|b|authority::ReplayRecord{sequence:e.entry.intent.sequence as i64,wire_digest:e.entry.intent.wire_sha256.clone(),receipt_binding:value(b).unwrap_or(Value::Null)}))})
    }
}
#[derive(Clone,Copy,Debug,Serialize,Deserialize)] #[serde(rename_all="snake_case")]
pub enum ColdFailure {Timeout,SpawnRefused,TransportLost,MalformedResult,UncertainCleanup}
impl<'a> Session<'a> {
    pub fn dispatch(&mut self,raw:&[u8])->Result<DispatchResult>{
        let frame=wire::Frame::decode(raw).map_err(|_|Error("FRAME"))?;
        let disclosure=matches!(frame.request()["verb"].as_str(),Some("read_receipt"|"inspect"|"inspect_operation"));
        let recovery=matches!(frame.request()["verb"].as_str(),Some("reconcile_operation"|"close_family"));
        require(disclosure||(!self.fenced&&!self.journal.is_pending()&&self.pending.is_none()&&(!self.restart_only||recovery)),"PENDING_OR_RESTART_FENCE")?;
        let facts=self.host.query(&frame)?;
        let current_config=self.read(&facts,&self.selection_binding,quota::MAX_PACKET)?;
        require(encode(&self.selected)?==current_config,"RUNTIME_SELECTION_DRIFT")?;
        let core:Value=decode(&self.read(&facts,&facts.facts().core_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        let basis:Value=decode(&self.read(&facts,&facts.facts().basis_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        let issuer_raw=self.read(&facts,&facts.facts().issuer_enrollment_binding,8192)?;
        let domain=if facts.facts().domain==Domain::Fixture{authority::TrustDomain::Fixture}else{authority::TrustDomain::Actual};
        let issuer=authority::Enrollment::select(&issuer_raw,&facts.facts().issuer_enrollment_binding.sha256,domain).map_err(|_|Error("INTENT_ENROLLMENT"))?;
        let mut control=self.control_snapshot(&frame,raw,&facts,&core)?;
        if frame.request()["verb"]=="repair_derived" {
            // This is a separate live derived-only operation. Its phase is
            // established from the exact immutable target's original closure,
            // never from the new operation's merely reserved local receipt.
            let ledger=self.current_ledger(&facts)?;let selected=self.load_derived(&facts)?;
            self.derived_history(&facts,&ledger,&selected)?;control.phase="pointer-committed".into();
        }
        let verified=authority::verify(&frame,self.host.selection().caller.peer(),&issuer,&basis,&core,&control)
            .map_err(|e|Error(e.0))?;
        let mut ledger=self.current_ledger(&facts)?;
        let verb=frame.request()["verb"].as_str().ok_or(Error("VERB"))?;
        let terminal_accounting=self.terminal_accounting(&verified,&facts)?;
        if matches!(verified.decision(),authority::Decision::Disclosure{..}) {
            return self.disclose(&frame,&verified,&facts,&ledger).map(DispatchResult::Reply);
        }
        // Exact original envelope is checked against every current selected
        // policy before any local intent or effect is written.
        require(facts.facts().capacity_root_id==self.selected.receipt_root_id
            &&facts.facts().roots.iter().find(|r|r.root_id==self.selected.receipt_root_id)
                .is_some_and(|r|r.ancestors.last()==Some(&self.journal.scope().receipt_root)),"RECEIPT_CAPACITY_ROOT")?;
        if !terminal_accounting{self.declared_budget(&core)?;}
        let (_,mut usage)=self.journal.inventory()?;
        let active=self.stage.as_ref().map(members::Stage::snapshot).transpose()?;
        let mut payload_roots=std::collections::BTreeSet::new();
        for id in [&self.selected.stage_root_id,&self.selected.generation_root_id].into_iter().filter(|_|!terminal_accounting){
            if payload_roots.insert(id.clone()){
                let held=self.root(id)?;
                let payload=state::payload_usage(held,&self.limits,active.as_ref().filter(|s|s.root_id==*id))?;
                usage.retained_bytes=usage.retained_bytes.checked_add(payload.retained_bytes).ok_or(Error("QUOTA_OVERFLOW"))?;
                usage.retained_inodes=usage.retained_inodes.checked_add(payload.retained_inodes).ok_or(Error("QUOTA_OVERFLOW"))?;
                usage.stage_count=usage.stage_count.checked_add(payload.stage_count).ok_or(Error("QUOTA_OVERFLOW"))?;
                usage.orphan_count=usage.orphan_count.checked_add(payload.orphan_count).ok_or(Error("QUOTA_OVERFLOW"))?;
                usage.orphan_bytes=usage.orphan_bytes.checked_add(payload.orphan_bytes).ok_or(Error("QUOTA_OVERFLOW"))?;
                usage.member_count=usage.member_count.checked_add(payload.member_count).ok_or(Error("QUOTA_OVERFLOW"))?;
                usage.stage_bytes=usage.stage_bytes.checked_add(payload.stage_bytes).ok_or(Error("QUOTA_OVERFLOW"))?;
            }
        }
        let (receipt_inventory,_)=self.journal.inventory()?;
        if terminal_accounting{quota::admit_cleanup(&self.limits,&usage,&facts.facts().remaining_capacity,&receipt_inventory,&self.journal.head().entry_sha256)?;}
        else{quota::admit(&self.limits,&usage,&facts.facts().remaining_capacity,&receipt_inventory,&self.journal.head().entry_sha256)?;}
        if verb=="write_member"{
            let p=&frame.request()["payload"];let full=p["full_length"].as_u64().ok_or(Error("MEMBER_LENGTH"))?;
            let count=p["chunk_length"].as_u64().or_else(||p["length"].as_u64()).ok_or(Error("CHUNK_LENGTH"))?;
            let name=p["member"].as_str().ok_or(Error("MEMBER_NAME"))?;
            let new_member=self.stage.as_ref().map(members::Stage::snapshot).transpose()?.map_or(true,|s|!s.members.contains_key(name));
            quota::member(&self.limits,&usage,full,new_member,count)?;
            let mut narrowed=self.limits.clone();narrowed.max_sequences=narrowed.max_sequences.min(core["limits"]["max_actions"].as_u64().ok_or(Error("DECLARED_ACTIONS"))?);
            let remaining=self.remaining_chunks(&frame,raw,&core)?;
            quota::completion_positions(&narrowed,usage.sequences,remaining,false,&usage)?;
        }
        if verb!="reserve_family" && verb!="reconcile_operation" && verb!="close_family" {
            ledger.borrow_operation(self.held,&facts.facts().operation.operation_id,&facts.facts().operation.fingerprint)
                .map_err(|_|Error("CURRENT_ORIGINAL_OPERATION"))?;
        }
        if matches!(verb,"create_stage"|"write_member"|"seal_stage") {self.stage_capacity(&facts,&core)?;}
        self.preflight(&frame,raw,&facts,&core,&basis,&usage)?;
        // From this point all errors fence further mutation; no second request
        // may reinterpret missing terminal bytes as an undispatched sequence.
        let result=self.effect(&frame,raw,&verified,&facts,&mut ledger,verb,&control);
        if result.is_err(){self.fenced=true;}
        result
    }
    fn terminal_accounting(&self,verified:&authority::VerifiedDispatch,facts:&VerifiedHostFacts)->Result<bool>{
        match verified.decision(){
            authority::Decision::Recovery{action,..} if action=="close_family"=>Ok(true),
            authority::Decision::Recovery{action,..} if action=="quarantine"=>{
                let b=self.effect_input(facts,"restart")?;let raw=self.read(facts,&b,quota::MAX_RECORD)?;
                let v:Value=decode(&raw,quota::MAX_RECORD)?;
                Ok(v["schema_version"]=="lab-broker-receipt-recovery-subject/v1")
            },_=>Ok(false)
        }
    }
    fn declared_budget(&self,core:&Value)->Result<()> {
        let slots=core["output_slots"].as_array().ok_or(Error("DECLARED_MEMBERS"))?;
        require(slots.len() as u64<=self.limits.max_members,"DECLARED_MEMBER_COUNT")?;
        let chunk=core["limits"]["max_chunk_bytes"].as_u64().filter(|n|*n>0&&*n<=32768).ok_or(Error("DECLARED_CHUNK_BOUND"))?;
        let mut total=0u64;let mut positions=5u64;
        for slot in slots{let bytes=slot["max_bytes"].as_u64().ok_or(Error("DECLARED_MEMBER_BOUND"))?;
            require(bytes<=self.limits.max_member_bytes,"DECLARED_MEMBER_BOUND")?;
            total=total.checked_add(bytes).ok_or(Error("DECLARED_TOTAL_OVERFLOW"))?;
            positions=positions.checked_add(if bytes==0{1}else{(bytes-1)/chunk+1}).ok_or(Error("DECLARED_POSITION_OVERFLOW"))?;
        }
        require(total<=self.limits.max_stage_bytes && total<=core["limits"]["max_total_bytes"].as_u64().ok_or(Error("DECLARED_TOTAL"))?
            && positions<=self.limits.max_sequences && positions<=core["limits"]["max_actions"].as_u64().ok_or(Error("DECLARED_ACTIONS"))?,"DECLARED_COMPLETION_CAPACITY")
    }
    fn stage_capacity(&self,facts:&VerifiedHostFacts,core:&Value)->Result<()> {
        let root=self.root(&self.selected.stage_root_id)?;let mut selected=None;
        for binding in &facts.facts().additional_capacity_bindings {
            let reserve:CapacityOriginal=decode(&self.read(facts,binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
            if reserve.physical_root==*root.root().identity(){require(selected.is_none(),"STAGE_RESERVE_AMBIGUOUS")?;selected=Some(reserve);}
        }
        let reserve=selected.ok_or(Error("STAGE_PHYSICAL_RESERVE_REQUIRED"))?;
        let now=now_seconds()?;
        require(reserve.schema_version=="lab-broker-held-capacity/v1"&&reserve.control_confirmation==self.confirmation
            &&reserve.not_before<=now&&now<reserve.expires_at
            &&reserve.remaining.prefix_sha256==self.journal.head().entry_sha256
            &&reserve.remaining.inventory_sha256==state::owned_inventory_digest(root,self.limits.max_retained_files,self.limits.max_retained_bytes)?,"STAGE_RESERVE_CURRENT_INVENTORY")?;
        // Reserve all declared member bytes and every possible selected path
        // ancestor, plus stage/generation metadata and temporary-file margin.
        // Existing allocations are not counted as free; this conservatively
        // asks for the same finite remaining bound at each selected boundary.
        let slots=core["output_slots"].as_array().ok_or(Error("DECLARED_MEMBERS"))?;
        let mut bytes=2*self.limits.max_record_bytes;let mut inodes=4u64;
        for s in slots {bytes=bytes.checked_add(s["max_bytes"].as_u64().ok_or(Error("DECLARED_MEMBER_BOUND"))?).ok_or(Error("QUOTA_OVERFLOW"))?;
            inodes=inodes.checked_add(roots::parts(s["member"].as_str().ok_or(Error("DECLARED_MEMBER"))?)?.len() as u64+1).ok_or(Error("QUOTA_OVERFLOW"))?;}
        require(reserve.remaining.bytes>=bytes&&reserve.remaining.inodes>=inodes,"STAGE_PHYSICAL_REMAINING_RESERVE")
    }
    /// Count this proposed range plus the remaining minimum complete ranges
    /// for every declared slot. A short legal range consumes an extra position;
    /// it cannot steal the four separately held terminal/recovery positions.
    fn remaining_chunks(&self,frame:&wire::Frame,raw:&[u8],core:&Value)->Result<u64>{
        let snapshot=self.stage.as_ref().map(members::Stage::snapshot).transpose()?;
        let p=&frame.request()["payload"];let maximum=core["limits"]["max_chunk_bytes"].as_u64().filter(|n|*n>0).ok_or(Error("DECLARED_CHUNK_BOUND"))?;
        let entries=self.journal.confirmed_entries(&self.prefix_rpc.signer,&self.response_signer)?;
        let envelope:Value=decode(raw,quota::MAX_PACKET)?;
        let mut count=1u64;
        for slot in core["output_slots"].as_array().ok_or(Error("DECLARED_MEMBERS"))?{
            let name=slot["member"].as_str().ok_or(Error("DECLARED_MEMBER"))?;
            let existing=snapshot.as_ref().and_then(|s|s.members.get(name));
            let current=slot["root_id"]==p["root_id"]&&slot["member"]==p["member"];
            let mut chunk=maximum;
            if current{chunk=envelope["permit"]["payload"]["grant"]["chunk_size"].as_u64().filter(|n|*n>0&&*n<=maximum).ok_or(Error("SELECTED_MEMBER_CHUNK_BOUND"))?;}
            else if existing.is_some(){
                let mut found=None;
                for entry in entries{if entry.entry.intent.verb!="write_member"{continue}
                    let binding=entry.entry.originals.get("frame.json").ok_or(Error("MEMBER_ORIGINAL_FRAME"))?;
                    let raw=state::read_owned(self.root(&self.selected.receipt_root_id)?,binding,quota::MAX_PACKET)?;
                    let original:Value=decode(&raw,quota::MAX_PACKET)?;
                    if original["request"]["payload"]["root_id"]==slot["root_id"]&&original["request"]["payload"]["member"]==slot["member"]{
                        let value=original["permit"]["payload"]["grant"]["chunk_size"].as_u64().filter(|n|*n>0&&*n<=maximum).ok_or(Error("SELECTED_MEMBER_CHUNK_BOUND"))?;
                        require(found.is_none_or(|old|old==value),"CAPTURED_MEMBER_CHUNK_CHANGED")?;found=Some(value);
                    }
                }chunk=found.ok_or(Error("CAPTURED_MEMBER_CHUNK_MISSING"))?;
            }
            if current{
                let full=p["full_length"].as_u64().ok_or(Error("MEMBER_LENGTH"))?;
                let end=p["offset"].as_u64().and_then(|n|n.checked_add(p["length"].as_u64()?)).filter(|n|*n<=full).ok_or(Error("MEMBER_RANGE"))?;
                let left=full-end;if left>0{count=count.checked_add((left-1)/chunk+1).ok_or(Error("QUOTA_OVERFLOW"))?;}
            }else if let Some(m)=existing{
                let written=m.ranges.iter().try_fold(0u64,|n,r|n.checked_add(r.length)).ok_or(Error("QUOTA_OVERFLOW"))?;
                let left=m.full_length.checked_sub(written).ok_or(Error("MEMBER_RANGE"))?;
                if left>0{count=count.checked_add((left-1)/chunk+1).ok_or(Error("QUOTA_OVERFLOW"))?;}
            }else{let n=slot["max_bytes"].as_u64().ok_or(Error("DECLARED_MEMBER"))?;
                count=count.checked_add(if n==0{1}else{(n-1)/chunk+1}).ok_or(Error("QUOTA_OVERFLOW"))?;}
        }Ok(count)
    }
    fn disclose(&self,frame:&wire::Frame,verified:&authority::VerifiedDispatch,facts:&VerifiedHostFacts,ledger:&Ledger<'_>)->Result<Vec<u8>> {
        let authority::Decision::Disclosure{subject_binding,max_output_bytes}=verified.decision() else{return Err(Error("DISCLOSURE_REQUIRED"));};
        facts.current()?;let entries=self.journal.confirmed_entries(&self.prefix_rpc.signer,&self.response_signer)?;
        let selected:Binding=serde_json::from_value(subject_binding.clone()).map_err(|_|Error("DISCLOSURE_SUBJECT"))?;
        if frame.request()["verb"]=="read_receipt" {
            let seq=frame.request()["sequence"].as_u64().ok_or(Error("RECEIPT_SEQUENCE"))?;
            let e=entries.iter().find(|e|e.entry.intent.sequence==seq).ok_or(Error("RECEIPT_UNAVAILABLE"))?;
            require(e.entry.originals.get("response.json")==Some(&selected)&&e.response.len()<=*max_output_bytes,"RECEIPT_EXACT_DISCLOSURE")?;
            if let Some(snapshot)=entries.iter().rev().find_map(|e|e.snapshot.as_ref()) {
                if let Some(publication)=entries.iter().find(|e|e.entry.intent.verb=="commit_generation"){
                    self.historical_generation_ranges(publication,snapshot,ledger)?;
                }else{
                    state::readonly_ranges(self.root(&self.selected.stage_root_id)?,snapshot,&snapshot.stage_name,None)?;
                }
            }
            return Ok(e.response.clone());
        }
        // inspect verbs disclose a separately selected immutable observation;
        // they never allocate a mutation sequence or choose a latest filename.
        require(facts.facts().disclosure_subjects.contains(&selected),"INSPECTION_SUBJECT_NOT_SELECTED")?;
        let raw=self.read(facts,&selected,(*max_output_bytes).min(quota::MAX_PACKET as usize) as u64)?;
        let observation:InspectionOriginal=decode(&raw,quota::MAX_PACKET)?;
        require(observation.schema_version=="lab-broker-inspection-original/v1"&&observation.operation==facts.facts().operation
            &&observation.control_confirmation==self.confirmation&&observation.prefix==*self.journal.head()
            &&observation.unknown==(!ledger.inspect().writable||self.fenced||self.restart_only),"INSPECTION_CURRENT_JOIN")?;Ok(raw)
    }
    fn effect(&mut self,frame:&wire::Frame,raw:&[u8],verified:&authority::VerifiedDispatch,facts:&VerifiedHostFacts,
        ledger:&mut Ledger<'a>,verb:&str,authority_admission:&authority::ControlSnapshot)->Result<DispatchResult>{
        let mut pending=if self.terminal_accounting(verified,facts)?{
            self.journal.begin_terminal(frame,raw,&facts.facts().operation.fingerprint,&self.confirmation,&facts.facts().remaining_capacity)?
        }else{self.journal.begin(frame,raw,&facts.facts().operation.fingerprint,&self.confirmation,&facts.facts().remaining_capacity)?};
        self.journal.put(&mut pending,"host-observation.json",facts.original())?;
        let frame_original:Value=decode(raw,quota::MAX_PACKET)?;
        self.journal.put(&mut pending,"selected-inputs.json",&encode(&json!({"schema_version":"lab-broker-selected-inputs/v1",
            "core":facts.facts().core_binding,"basis":facts.facts().basis_binding,"issuer":facts.facts().issuer_enrollment_binding,
            "runtime":self.selection_binding,"host_scope":facts.facts().scope,"original_operation":facts.facts().operation}))?)?;
        match verb {
            "reserve_family"=>{
                require(ledger.operation(&facts.facts().operation.operation_id).is_none(),"ORIGINAL_RESERVATION_ALREADY_EXISTS")?;
                let proposed=ledger.append(self.held,Change::Reserve{operation:facts.facts().operation.clone()}).map_err(|_|Error("RESERVE_ORIGINAL"))?;
                let desired=proposed.requested_confirmation().clone();
                let confirmed=self.control_rpc.confirm(&self.confirmation,&desired,facts.facts().expires_at)?;
                ledger.acknowledge(self.held,proposed,confirmed.clone()).map_err(|_|Error("RESERVE_CONFIRMATION"))?;self.confirmation=confirmed;
                let result=self.journal.put(&mut pending,"control-confirmation.json",&encode(&self.confirmation)?)?;
                self.finish_sequence(pending,frame,None,Some(result),"reserved",facts.facts().expires_at)
            }
            "create_stage"|"write_member"|"seal_stage"=>{
                let action=members::Action::from_verified(raw,frame,verified)?;
                if verb=="write_member"{
                    let(binding,original,_)=self.captured_member(frame,facts)?;
                    self.journal.put(&mut pending,"captured-member.json",&original)?;
                    self.journal.put(&mut pending,"captured-selection.json",&encode(&binding)?)?;
                }
                if verb=="create_stage" {require(self.stage.is_none(),"STAGE_ALREADY_CREATED")?;self.stage=Some(members::Stage::create(self.root(&self.selected.stage_root_id)?,&action)?);}
                else if verb=="write_member" {self.stage.as_mut().ok_or(Error("STAGE_MISSING"))?.write_member(&action)?;}
                else {let selected:Binding=serde_json::from_value(frame.request()["payload"]["subject_binding"].clone()).map_err(|_|Error("MEMBER_MANIFEST_SELECTION"))?;
                    let manifest=self.read(facts,&selected,quota::MAX_PACKET)?;self.stage.as_mut().ok_or(Error("STAGE_MISSING"))?.seal(&action,&manifest)?;}
                let stage=self.stage.as_mut().ok_or(Error("STAGE_MISSING"))?;
                let receipt=self.journal.member_receipt(&mut pending,stage.pending().ok_or(Error("TRANSITION_MISSING"))?,stage.proposed_state().ok_or(Error("PROPOSED_STATE_MISSING"))?)?;
                let binding=receipt.binding().clone();stage.acknowledge(receipt)?;let snapshot=stage.snapshot()?;
                self.finish_sequence(pending,frame,Some(&snapshot),Some(binding),if verb=="seal_stage"{"sealed"}else{"staging"},facts.facts().expires_at)
            }
            "commit_generation"=>{
                let selection=self.load_commit(facts,&self.effect_input(facts,"commit")?)?;
                let (admission,inputs,member_manifest)=self.commit_inputs(facts,&selection)?;
                let stage=self.stage.take().ok_or(Error("SEALED_STAGE_REQUIRED"))?;
                let mut commit=if facts.facts().domain==Domain::Fixture {
                    commit::Commit::begin_fixture(self.root(&self.selected.generation_root_id)?,self.root(&self.selected.generation_journal_root_id)?,self.held,ledger,admission,stage,inputs)?
                }else{commit::Commit::begin_admitted(self.root(&self.selected.generation_root_id)?,self.root(&self.selected.generation_journal_root_id)?,self.held,ledger,admission,stage,inputs)?};
                let action=members::Action::from_verified(raw,frame,verified)?;commit.publish(&action,&member_manifest)?;
                let transition=commit.publication_pending().ok_or(Error("PUBLICATION_TRANSITION"))?.clone();
                let receipt_raw=encode(&json!({"schema_version":"lab-member-durable-receipt/v1","transition":transition,"outcome":"durable"}))?;
                self.journal.put(&mut pending,"publication-transition.json",&encode(&transition)?)?;
                let binding=self.journal.put(&mut pending,"publication-member-receipt.json",&receipt_raw)?;
                let receipt=members::DurableReceipt::from_fixed_control(transition,receipt_raw.clone(),binding,facts.facts().domain)?;
                commit.acknowledge_publication(receipt,&receipt_raw)?;commit.prepare_pointer()?;commit.activate_pointer()?;
                let request=commit.cold_request()?;self.journal.put(&mut pending,"cold-request.json",&encode(&request)?)?;
                self.commit=Some(commit);self.pending=Some(PendingCommit{sequence:pending,frame:raw.into(),admission:authority_admission.clone(),request:request.clone()});
                Ok(DispatchResult::PendingCold(request))
            }
            "reconcile_operation"=>self.reconcile(frame,raw,verified,facts,ledger,pending,authority_admission),
            "close_family"=>self.close_family(frame,verified,facts,ledger,pending),
            "repair_derived"=>self.repair_derived(frame,raw,verified,facts,ledger,pending),
            _=>{let _=frame_original;Err(Error("CLOSED_EFFECT_VERB"))}
        }
    }
    fn finish_sequence(&mut self,mut pending:PendingSequence,frame:&wire::Frame,snapshot:Option<&members::Snapshot>,result:Option<Binding>,phase:&str,expires:u64)->Result<DispatchResult>{
        if pending.original_control()!=&self.confirmation && !pending.has_original("control-confirmation.json") {
            self.journal.put(&mut pending,"control-confirmation.json",&encode(&self.confirmation)?)?;
        }
        let response=encode(&authority::sign_receipt(frame,phase,"PASS",None,result.map(|b|value(&b)).transpose()?.unwrap_or(Value::Null),self.response_signer.issuer(),&self.response_key).map_err(|_|Error("SIGN_RESPONSE"))?)?;
        self.journal.finish(&mut pending,snapshot,&response,phase,"PASS")?;
        let now=now_seconds()?;let request=self.journal.confirmation_request(&pending,challenge()?,now,expires.min(now.saturating_add(60)))?;
        let proof=self.prefix_rpc.confirm(&request)?;
        let original=self.journal.confirm(pending,proof,&self.response_signer)?;Ok(DispatchResult::Reply(original))
    }
    fn load_commit(&self,facts:&VerifiedHostFacts,binding:&Binding)->Result<CommitSelection>{
        let selection:CommitSelection=decode(&self.read(facts,binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        require(selection.schema_version=="lab-broker-commit-selection/v1","COMMIT_SELECTION_SCHEMA")?;Ok(selection)
    }
    fn commit_inputs(&self,facts:&VerifiedHostFacts,s:&CommitSelection)->Result<(commit::ControlAdmission<'a>,commit::Inputs,Vec<u8>)>{
        let read=|b:&Binding,max:u64|self.read(facts,b,max);
        let store:generation::StoreSelection=decode(&read(&s.store_binding,quota::MAX_RECORD)?,quota::MAX_RECORD)?;
        let manifest:generation::GenerationManifest=decode(&read(&s.manifest_binding,quota::MAX_RECORD)?,quota::MAX_RECORD)?;
        let policy=read(&s.policy_binding,quota::MAX_RECORD)?;
        let reserve:CapacityOriginal=decode(&read(&s.reserve_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        let root=self.root(&self.selected.generation_root_id)?;let journal=self.root(&self.selected.generation_journal_root_id)?;
        require(reserve.physical_root==*journal.root().identity()&&reserve.control_confirmation==self.confirmation
            &&reserve.not_before<=now_seconds()?&&now_seconds()?<reserve.expires_at,"GENERATION_CAPACITY_JOIN")?;
        read(&reserve.held_reservation_binding,quota::MAX_PACKET)?;
        require(s.runtime_selection.expires_utc_ns<=seconds_to_ns(facts.facts().expires_at)?,"COMMIT_ADMISSION_INTERVAL")?;
        let control_handle=self.root(&self.selected.control_root_id)?.directory().try_clone()?;
        let admission=if facts.facts().domain==Domain::Fixture {
            commit::ControlAdmission::fixture(self.control_root,control_handle,self.held,root,journal,self.confirmation.clone(),&policy,&s.policy_binding,s.runtime_selection.clone())?
        }else{unsafe{commit::ControlAdmission::from_fixed_host(self.control_root,control_handle,self.held,root,journal,self.confirmation.clone(),&policy,&s.policy_binding,
            s.reserve_binding.clone(),reserve.remaining.bytes,reserve.remaining.inodes,reserve.remaining.inventory_sha256.clone(),s.runtime_selection.clone())?}};
        let inputs=commit::Inputs{store,store_binding:s.store_binding.clone(),manifest,replay_expectation_original:read(&s.expectation_binding,quota::MAX_RECORD)?,
            c01_store_original:read(&s.c01_store_binding,quota::MAX_RECORD)?,old_pointer:s.old_pointer_binding.as_ref().map(|b|read(b,quota::MAX_RECORD)).transpose()?,
            prior:s.prior.clone(),verifier_executable:s.verifier_executable.clone(),verifier_inputs:s.verifier_inputs.clone(),verifier_uid:s.verifier_uid,
            commit_authority_binding:s.runtime_selection.commit_authority_binding.clone(),authority_expires_utc_ns:s.runtime_selection.expires_utc_ns};
        Ok((admission,inputs,read(&s.member_manifest_binding,quota::MAX_PACKET)?))
    }
}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct InspectionOriginal {pub schema_version:String,pub operation:ledger::Operation,pub control_confirmation:HostConfirmation,pub prefix:PrefixHead,pub unknown:bool}
impl<'a> Session<'a> {
    /// This is revalidation of one already-admitted, still-live continuation,
    /// never a dispatch capability or a recreated writable stage. The original
    /// phase/counters are held privately with that exact frame. Current issuer,
    /// revocation, scope, recovery selection and intervals are sampled again.
    /// An already appended Outcome has a separate exact settlement path.
    fn verify_continuation(&self,frame:&wire::Frame,facts:&VerifiedHostFacts)->Result<()> {
        let pending=self.pending.as_ref().ok_or(Error("PENDING_SEQUENCE_MISSING"))?;
        let f=facts.facts();facts.current()?;
        require(frame.wire_digest()==wire::Frame::decode(&pending.frame).map_err(|_|Error("PENDING_FRAME"))?.wire_digest(),"PENDING_FRAME_CHANGED")?;
        require(self.read(facts,&self.selection_binding,quota::MAX_PACKET)?==encode(&self.selected)?,"RUNTIME_SELECTION_DRIFT")?;
        let core:Value=decode(&self.read(facts,&f.core_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        let basis:Value=decode(&self.read(facts,&f.basis_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        let issuer_raw=self.read(facts,&f.issuer_enrollment_binding,8192)?;
        let domain=if f.domain==Domain::Fixture{authority::TrustDomain::Fixture}else{authority::TrustDomain::Actual};
        let issuer=authority::Enrollment::select(&issuer_raw,&f.issuer_enrollment_binding.sha256,domain).map_err(|_|Error("INTENT_ENROLLMENT"))?;
        let mut control=pending.admission.clone();
        require(control.operation_id==f.operation.operation_id&&control.operation_fingerprint==f.operation.fingerprint,
            "PENDING_OPERATION_CHANGED")?;
        control.now=now_seconds()? as i64;control.activation_expires_at=f.activation_expires_at as i64;
        control.live_scope=f.live_authority_scope.clone();control.selected_roots=f.roots.iter().map(|r|r.root_id.clone()).collect();
        control.issuer_currentness=authority::IssuerCurrentness{enrollment_digest:wire::content_digest(&issuer_raw),
            revocation_binding:value(&f.revocation_binding)?,revoked:f.issuer_revoked,checked_at:control.now};
        control.recovery=f.recovery.as_ref().map(|r|Ok::<_,Error>(authority::RecoverySelection{
            authorization_digest:r.authorization_binding.clone(),subject_binding:value(&r.subject_binding)?,
            preimages:r.preimages.iter().map(value).collect::<Result<_>>()?,action:r.action.clone(),consumed:r.consumed})).transpose()?;
        let verified=authority::verify(frame,self.host.selection().caller.peer(),&issuer,&basis,&core,&control).map_err(|e|Error(e.0))?;
        require(matches!(verified.decision(),authority::Decision::Fresh{..}|authority::Decision::Recovery{..}),"CONTINUATION_EFFECT_AUTHORITY")
    }
    /// Fixed U08-02 code in the same statically linked crate creates the opaque
    /// observation from its supervised transport. It cannot replace this
    /// pending request or release this Session's retained global capabilities.
    pub(crate) fn complete_cold(&mut self,observation:commit::ColdObservation)->Result<DispatchResult>{
        require(!self.fenced&&self.pending.is_some()&&self.journal.is_pending(),"NO_LIVE_COLD_CONTINUATION")?;
        let raw=self.pending.as_ref().unwrap().frame.clone();let frame=wire::Frame::decode(&raw).map_err(|_|Error("PENDING_FRAME"))?;
        let result=(||{
            let facts=self.host.query(&frame)?;let mut ledger=self.current_ledger(&facts)?;
            self.verify_continuation(&frame,&facts)?;
            if let Some(commit)=self.commit.as_mut(){
                commit.accept_cold(observation)?;commit.persist_outcome(&mut ledger)?;
                let desired=commit.requested_confirmation()?.clone();
                let confirmed=self.control_rpc.confirm(&self.confirmation,&desired,facts.facts().expires_at)?;
                commit.acknowledge_outcome(&mut ledger,confirmed.clone())?;self.confirmation=confirmed;
                let pointer=commit.confirmed_selection()?;
                let journal_name=commit.journal_name().to_string();
                let closure=self.capture_generation(&journal_name,&pointer,&ledger)?;
                let mut pending=self.pending.take().ok_or(Error("PENDING_SEQUENCE_MISSING"))?;
                let binding=self.journal.put(&mut pending.sequence,"generation-closure.json",&encode(&closure)?)?;
                self.finish_sequence(pending.sequence,&frame,None,Some(binding),"pointer-committed",facts.facts().expires_at)
            }else{
                let recovery=self.recovery.as_mut().ok_or(Error("PENDING_RECOVERY_MISSING"))?;
                recovery.accept_cold(&ledger,observation)?;recovery.persist_outcome(&mut ledger)?;
                let desired=recovery.requested_confirmation()?.clone();let confirmed=self.control_rpc.confirm(&self.confirmation,&desired,facts.facts().expires_at)?;
                let proof=recovery.acknowledge(&mut ledger,confirmed.clone())?;self.confirmation=confirmed;
                let mut pending=self.pending.take().ok_or(Error("PENDING_SEQUENCE_MISSING"))?;
                let binding=self.journal.put(&mut pending.sequence,"recovery-closure.json",&encode(&json!({"schema_version":"lab-broker-recovery-closure/v1","terminal":proof.terminal(),"pointer":proof.pointer(),"generation":proof.generation(),"control_confirmation":self.confirmation}))?)?;
                self.finish_sequence(pending.sequence,&frame,None,Some(binding),"pointer-committed",facts.facts().expires_at)
            }
        })();if result.is_err(){self.fenced=true;}result
    }
    fn capture_generation(&self,name:&str,pointer:&generation::PointerRecord,ledger:&Ledger<'_>)->Result<GenerationClosure>{
        let root=self.root(&self.selected.generation_journal_root_id)?;
        let originals=state::capture_owned_directory(root,name,32,self.limits.max_record_bytes)?;
        let terminal=originals.get("terminal.json").ok_or(Error("GENERATION_TERMINAL_MISSING"))?;
        require(ledger.outcome(&pointer.operation_id)==Some(&(Outcome::Committed,control_binding(terminal))),"GENERATION_ORIGINAL_OUTCOME")?;
        Ok(GenerationClosure{schema_version:"lab-broker-generation-closure/v1".into(),pointer:pointer.clone(),journal_name:name.into(),originals,control_confirmation:self.confirmation.clone()})
    }
    fn reconcile(&mut self,frame:&wire::Frame,raw:&[u8],verified:&authority::VerifiedDispatch,facts:&VerifiedHostFacts,
        ledger:&mut Ledger<'a>,mut pending:PendingSequence,authority_admission:&authority::ControlSnapshot)->Result<DispatchResult>{
        let selected_binding=&self.effect_input(facts,"restart")?;
        let selected_raw=self.read(facts,selected_binding,quota::MAX_RECORD)?;
        let selected_value:Value=decode(&selected_raw,quota::MAX_RECORD)?;
        if selected_value["schema_version"]=="lab-broker-receipt-recovery-subject/v1"{
            let subject:state::ReceiptRecoverySubject=decode(&selected_raw,quota::MAX_RECORD)?;
            let authority::Decision::Recovery{action,subject_binding,..}=verified.decision()else{return Err(Error("RECEIPT_RECOVERY_AUTHORITY"));};
            require(action=="quarantine"&&*subject_binding==value(selected_binding)?&&subject==self.journal.recovery_subject()?,"RECEIPT_RECOVERY_EXACT_SUBJECT")?;
            self.journal.put(&mut pending,"orphan-inventory.json",&selected_raw)?;
            let prior_outcome=ledger.outcome(&facts.facts().operation.operation_id).cloned();
            let terminal=encode(&json!({"schema_version":"lab-broker-orphan-terminal/v1","subject":selected_binding,
                "operation":facts.facts().operation,"original_outcome":prior_outcome,"effect_truth":"UNKNOWN","disposition":"retained-quarantined"}))?;
            let terminal_binding=self.journal.put(&mut pending,"orphan-terminal.json",&terminal)?;
            if prior_outcome.is_none(){self.append_control(ledger,Change::Outcome{operation_id:facts.facts().operation.operation_id.clone(),fingerprint:facts.facts().operation.fingerprint.clone(),result_binding:control_binding(&terminal_binding),outcome:Outcome::Quarantined},facts.facts().expires_at)?;}
            self.journal.put(&mut pending,"control-confirmation.json",&encode(&self.confirmation)?)?;
            // This receipt accounts uncertainty. It neither confirms the old
            // producer effect nor changes an existing original Outcome.
            let response=encode(&authority::sign_receipt(frame,"quarantined","UNKNOWN",Some("ORIGINAL_EFFECT_UNKNOWN"),value(&terminal_binding)?,self.response_signer.issuer(),&self.response_key).map_err(|_|Error("SIGN_RESPONSE"))?)?;
            self.journal.finish(&mut pending,None,&response,"quarantined","UNKNOWN")?;
            let now=now_seconds()?;let request=self.journal.confirmation_request(&pending,challenge()?,now,facts.facts().expires_at.min(now.saturating_add(60)))?;
            let proof=self.prefix_rpc.confirm(&request)?;
            return Ok(DispatchResult::Reply(self.journal.confirm(pending,proof,&self.response_signer)?));
        }
        let selected:RestartInputs=decode(&self.read(facts,selected_binding,quota::MAX_RECORD)?,quota::MAX_RECORD)?;
        require(selected.schema_version=="lab-broker-restart-inputs/v1"&&selected.authority_original_binding==bound(&selected.authority_original_binding.root_id,&selected.authority_original_binding.relative_path,raw)?,"RESTART_ORIGINAL_AUTHORITY")?;
        let commit_selection=self.load_commit(facts,&selected.commit_selection_binding)?;
        let(admission,_,_)=self.commit_inputs(facts,&commit_selection)?;
        let inspection=commit::RestartInspection::inspect(self.root(&self.selected.generation_root_id)?,self.root(&self.selected.generation_journal_root_id)?,self.held,ledger,admission,selected.selection)?;
        let authority=commit::RecoveryAuthority::from_verified(raw,frame,verified,selected.authority_original_binding)?;
        let mut recovery=commit::RecoveryCommit::begin(inspection,ledger,selected.kind,authority,selected.verifier)?;
        if selected.kind==commit::RepairKind::SealObservedNew {
            let request=recovery.cold_request(ledger)?;
            self.journal.put(&mut pending,"cold-request.json",&encode(&request)?)?;
            self.recovery=Some(recovery);self.pending=Some(PendingCommit{sequence:pending,frame:raw.into(),admission:authority_admission.clone(),request:request.clone()});
            Ok(DispatchResult::PendingCold(request))
        }else{
            recovery.persist_outcome(ledger)?;
            let confirmed=self.control_rpc.confirm(&self.confirmation,recovery.requested_confirmation()?,facts.facts().expires_at)?;
            let proof=recovery.acknowledge(ledger,confirmed.clone())?;self.confirmation=confirmed;
            let binding=self.journal.put(&mut pending,"recovery-closure.json",&encode(&json!({"schema_version":"lab-broker-recovery-closure/v1","terminal":proof.terminal(),"pointer":proof.pointer(),"generation":proof.generation(),"control_confirmation":self.confirmation}))?)?;
            self.recovery=Some(recovery);self.finish_sequence(pending,frame,None,Some(binding),"terminal",facts.facts().expires_at)
        }
    }
    fn append_control(&mut self,ledger:&mut Ledger<'a>,change:Change,expires:u64)->Result<()> {
        let pending=ledger.append(self.held,change).map_err(|_|Error("CONTROL_TRANSITION"))?;
        let confirmed=self.control_rpc.confirm(&self.confirmation,pending.requested_confirmation(),expires)?;
        ledger.acknowledge(self.held,pending,confirmed.clone()).map_err(|_|Error("CONTROL_ACK"))?;self.confirmation=confirmed;Ok(())
    }
    fn close_slot_transition(&self,facts:&VerifiedHostFacts,operation:&ledger::Operation)->Result<(ledger::SlotPhase,Binding,Change)>{
        let root=self.root(&self.selected.control_root_id)?;
        let path=&root.root().selection().absolute_path;
        let children:Vec<_>=self.roots.values().filter(|h|std::path::Path::new(&h.root().selection().absolute_path).parent()==Some(std::path::Path::new(path))).map(|h|h.root().selection().clone()).collect();
        let reader=OriginalDirectory::open(root.root().selection().clone(),facts.facts().domain)?.with_children(&children)?;
        let originals=reader.control_originals(&self.confirmation)?;
        originals.slot_transition(&self.confirmation,facts.facts().domain,operation,&self.selected.control_root_id)
    }
    fn verify_prior_close(&self,facts:&VerifiedHostFacts,proof:&SupervisorClosure,selected:&Binding)->Result<()> {
        let raw=self.read(facts,selected,quota::MAX_PACKET)?;let old:CloseLedgerTerminal=decode(&raw,quota::MAX_PACKET)?;
        require(old.schema_version=="lab-broker-close-ledger-terminal/v1"&&old.operation==proof.operation
            &&old.native_terminal_binding==proof.original_terminal_binding,"CLOSE_PRIOR_NATIVE_TARGET")?;
        let original:SupervisorClosure=decode(&self.read(facts,&old.supervisor_closure_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        require(original.operation==proof.operation&&original.original_terminal_binding==proof.original_terminal_binding
            &&original.containment_selection_binding==proof.containment_selection_binding&&original.native_evidence_binding==proof.native_evidence_binding
            &&original.worker_identity_binding==proof.worker_identity_binding&&original.cleanup_original_binding==proof.cleanup_original_binding
            &&!original.populated&&original.all_owned_children_reaped&&original.cleanup=="clean","CLOSE_PRIOR_SUPERVISOR_JOIN")?;
        let intent:state::RequestIntent=decode(&self.read(facts,&old.request_intent_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        let wire=self.read(facts,&old.request_frame_binding,quota::MAX_PACKET)?;let frame=wire::Frame::decode(&wire).map_err(|_|Error("CLOSE_PRIOR_FRAME"))?;
        require(intent.scope_sha256==self.journal.scope().digest()?&&intent.operation_id==proof.operation.operation_id
            &&intent.original_fingerprint==proof.operation.fingerprint&&intent.verb=="close_family"
            &&intent.ledger_confirmation==original.control_confirmation&&intent.wire_sha256==frame.wire_digest()
            &&frame.request()["verb"]=="close_family"&&frame.request()["operation_id"]==proof.operation.operation_id
            &&frame.request()["sequence"]==intent.sequence,"CLOSE_PRIOR_FRAME_JOIN")?;
        self.historical_control(&intent.ledger_confirmation,&self.confirmation)?;
        self.historical_control(&old.control_preimage,&self.confirmation)?;
        Ok(())
    }
    fn close_family(&mut self,frame:&wire::Frame,verified:&authority::VerifiedDispatch,facts:&VerifiedHostFacts,
        ledger:&mut Ledger<'a>,mut pending:PendingSequence)->Result<DispatchResult>{
        let authority::Decision::Recovery{action,subject_binding,..}=verified.decision() else{return Err(Error("CLOSE_RECOVERY_REQUIRED"));};
        let selected=&self.effect_input(facts,"supervisor")?;
        require(action=="close_family"&&*subject_binding==value(selected)?,"CLOSE_EXACT_SUBJECT")?;
        let original=self.read(facts,selected,quota::MAX_PACKET)?;let proof:SupervisorClosure=decode(&original,quota::MAX_PACKET)?;
        let now=now_seconds()?;
        require(proof.schema_version=="lab-broker-supervisor-closure/v1"&&proof.operation==facts.facts().operation
            &&proof.execution_scope==facts.facts().scope&&proof.control_confirmation==self.confirmation
            &&proof.authority_binding.valid()&&proof.authority_binding!=*selected
            &&!proof.populated&&proof.all_owned_children_reaped&&proof.cleanup=="clean"
            &&proof.not_before<=now&&now<proof.expires_at,"SUPERVISOR_CLOSURE_SCOPE")?;
        let terminal_raw=self.read(facts,&proof.original_terminal_binding,quota::MAX_PACKET)?;
        let native:NativeSupervisorTerminal=decode(&terminal_raw,quota::MAX_PACKET)?;
        native.validate(&proof,facts.facts().domain)?;
        self.verify_supervisor_originals(facts,ledger,&proof,&native)?;
        self.journal.put(&mut pending,"supervisor-original.json",&terminal_raw)?;
        let retained=self.journal.put(&mut pending,"supervisor-closure.json",&original)?;
        let operation=&proof.operation;
        if ledger.outcome(&operation.operation_id).is_none(){
            require(!self.restart_only,"RESTART_CLOSE_NEEDS_TRANSACTION_OUTCOME")?;
            require(proof.outcome=="aborted","CLOSE_CANNOT_INFER_COMMIT")?;
            self.append_control(ledger,Change::Outcome{operation_id:operation.operation_id.clone(),fingerprint:operation.fingerprint.clone(),result_binding:control_binding(&retained),outcome:Outcome::Aborted},facts.facts().expires_at)?;
        }
        require(ledger.outcome(&operation.operation_id).is_some_and(|(o,_)|matches!(o,Outcome::Aborted|Outcome::Committed)),"QUARANTINED_OUTCOME_CANNOT_RELEASE")?;
        let root=self.root(&self.selected.control_root_id)?;
        let(phase,transition_binding,transition)=self.close_slot_transition(facts,&proof.operation)?;
        let prior=match &transition{Change::SlotState{terminal_binding,..}|Change::Reconcile{action:ledger::ReconcileAction::Slot{terminal_binding,..},..}=>Some(Binding{kind:terminal_binding.kind.clone(),root_id:terminal_binding.root_id.clone(),relative_path:terminal_binding.relative_path.clone(),sha256:terminal_binding.sha256.clone(),size_bytes:terminal_binding.size_bytes}),_=>None};
        if matches!(phase,ledger::SlotPhase::Closing|ledger::SlotPhase::Closed){
            let old=prior.ok_or(Error("CLOSE_PRIOR_TERMINAL"))?;
            require(proof.prior_close_terminal.as_ref()==Some(&old),"CLOSE_CURRENT_PRIOR_SELECTION")?;
            self.verify_prior_close(facts,&proof,&old)?;
            self.journal.put(&mut pending,"prior-close-terminal.json",&self.read(facts,&old,quota::MAX_PACKET)?)?;
            self.journal.put(&mut pending,"prior-slot-transition.json",&state::read_owned(root,&transition_binding,65536)?)?;
            if phase==ledger::SlotPhase::Closing{
                self.append_control(ledger,Change::SlotState{slot_id:operation.slot_id.clone(),epoch:operation.slot_epoch,holder:operation.holder.clone(),state:ledger::SlotPhase::Closed,terminal_binding:control_binding(&old)},facts.facts().expires_at)?;
            }
        }else{
            require(proof.prior_close_terminal.is_none(),"CLOSE_UNEXPECTED_PRIOR")?;
            let terminal=CloseLedgerTerminal{schema_version:"lab-broker-close-ledger-terminal/v1".into(),operation:operation.clone(),
                supervisor_closure_binding:retained.clone(),native_terminal_binding:proof.original_terminal_binding.clone(),
                request_intent_binding:pending.original("intent.json")?,request_frame_binding:pending.original("frame.json")?,control_preimage:self.confirmation.clone()};
            let terminal_binding=self.journal.put(&mut pending,"close-terminal.json",&encode(&terminal)?)?;
            if phase==ledger::SlotPhase::Quarantined{
                let selected=ledger::TrustedReconciliation{authority_domain:self.confirmation.authority_domain.clone(),root:self.confirmation.root.clone(),writer:self.confirmation.writer.clone(),observed_head:self.confirmation.head.clone(),authority_binding:control_binding(&pending.original("frame.json")?),action:ledger::ReconcileAction::Slot{slot_id:operation.slot_id.clone(),epoch:operation.slot_epoch,holder:operation.holder.clone(),terminal_binding:control_binding(&terminal_binding)}};
                let checkpoint=ledger.reconcile(self.held,selected).map_err(|_|Error("CLOSE_SLOT_RECONCILIATION"))?;
                let confirmed=self.control_rpc.confirm(&self.confirmation,checkpoint.requested_confirmation(),facts.facts().expires_at)?;
                ledger.acknowledge(self.held,checkpoint,confirmed.clone()).map_err(|_|Error("CLOSE_SLOT_ACK"))?;self.confirmation=confirmed;
            }else{
                require(matches!(phase,ledger::SlotPhase::Reserved|ledger::SlotPhase::Active),"CLOSE_SLOT_PHASE")?;
                self.append_control(ledger,Change::SlotState{slot_id:operation.slot_id.clone(),epoch:operation.slot_epoch,holder:operation.holder.clone(),state:ledger::SlotPhase::Closing,terminal_binding:control_binding(&terminal_binding)},facts.facts().expires_at)?;
                self.append_control(ledger,Change::SlotState{slot_id:operation.slot_id.clone(),epoch:operation.slot_epoch,holder:operation.holder.clone(),state:ledger::SlotPhase::Closed,terminal_binding:control_binding(&terminal_binding)},facts.facts().expires_at)?;
            }
        }
        self.journal.put(&mut pending,"control-confirmation.json",&encode(&self.confirmation)?)?;
        self.finish_sequence(pending,frame,None,Some(retained),"terminal",facts.facts().expires_at)
    }
}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct GenerationClosure {pub schema_version:String,pub pointer:generation::PointerRecord,pub journal_name:String,
    pub originals:BTreeMap<String,Binding>,pub control_confirmation:HostConfirmation}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct NativeSupervisorTerminal {
    schema_version:String,domain:Domain,operation:ledger::Operation,attempt_id:String,
    containment_binding:Binding,actual_group_identity:roots::Identity,execution_binding:Binding,original_start_binding:Binding,historical_selection:Binding,
    start_utc_ns:u64,end_utc_ns:Option<u64>,elapsed_ns:u64,child_pid:u32,pid_start_ticks:Option<u64>,
    reason:String,exit_code:Option<i32>,signal:Option<i32>,primary_error:Option<String>,cleanup_errors:Vec<String>,
    direct_child_reaped:bool,subtree_empty:bool,inherited_descriptors_closed:bool,workload_started:Option<bool>,historical_complete:bool,
}
impl NativeSupervisorTerminal {
    fn validate(&self,proof:&SupervisorClosure,domain:Domain)->Result<()> {
        require(self.schema_version=="lab-contained-attempt-terminal/v1"&&self.domain==domain&&self.operation==proof.operation
            &&self.containment_binding==proof.containment_selection_binding&&self.direct_child_reaped&&self.subtree_empty
            &&self.inherited_descriptors_closed&&self.historical_complete&&self.cleanup_errors.is_empty()
            &&self.pid_start_ticks.is_some()&&self.child_pid>0&&self.child_pid<u32::MAX
            &&self.original_start_binding.valid()&&self.historical_selection.valid()&&self.execution_binding.valid()
            &&self.end_utc_ns.is_some_and(|end|end>=self.start_utc_ns&&end<=i64::MAX as u64),"SUPERVISOR_ORIGINAL_TERMINAL")
    }
}
impl Session<'_> {
    fn selected_input_record(&self,facts:&VerifiedHostFacts)->Result<Vec<u8>>{encode(&json!({"schema_version":"lab-broker-selected-inputs/v1",
        "core":facts.facts().core_binding,"basis":facts.facts().basis_binding,"issuer":facts.facts().issuer_enrollment_binding,
        "runtime":self.selection_binding,"host_scope":facts.facts().scope,"original_operation":facts.facts().operation}))}
    fn preflight(&self,frame:&wire::Frame,raw:&[u8],facts:&VerifiedHostFacts,_core:&Value,_basis:&Value,usage:&quota::Usage)->Result<()> {
        let verb=frame.request()["verb"].as_str().ok_or(Error("VERB"))?;
        let mut records=BTreeMap::new();records.insert("host-observation.json".into(),facts.original().into());
        records.insert("selected-inputs.json".into(),self.selected_input_record(facts)?);
        let mut future_confirmation=self.confirmation.clone();future_confirmation.head.sequence=i64::MAX as u64;
        future_confirmation.predecessor.sequence=i64::MAX as u64;future_confirmation.head.sha256="f".repeat(64);future_confirmation.predecessor.sha256="f".repeat(64);
        if matches!(verb,"commit_generation"|"repair_derived"|"reconcile_operation") {
            records.insert("control-confirmation.json".into(),encode(&future_confirmation)?);
        }
        let phase=match verb {
            "reserve_family"=>{records.insert("control-confirmation.json".into(),encode(&future_confirmation)?);"reserved"}
            "create_stage"|"write_member"|"seal_stage"=>{
                let root=self.root(&self.selected.stage_root_id)?;let sel=root.root().selection();
                let unknown=roots::Identity{device:i64::MAX as u64,inode:i64::MAX as u64,mount_id:i64::MAX as u64,uid:u32::MAX-1,gid:u32::MAX-1,mode:4095};
                let p=&frame.request()["payload"];
                let mut after=if let Some(stage)=&self.stage{stage.snapshot()?}else{
                    require(verb=="create_stage","STAGE_REQUIRED")?;
                    let mut narrowed=self.limits.clone();narrowed.max_sequences=narrowed.max_sequences.min(_core["limits"]["max_actions"].as_u64().ok_or(Error("DECLARED_ACTIONS"))?);
                    let chunk=_core["limits"]["max_chunk_bytes"].as_u64().filter(|n|*n>0).ok_or(Error("DECLARED_CHUNK_BOUND"))?;
                    let remaining=_core["output_slots"].as_array().ok_or(Error("DECLARED_MEMBERS"))?.iter().try_fold(0u64,|count,s|{
                        let n=s["max_bytes"].as_u64().ok_or(Error("DECLARED_MEMBER"))?;count.checked_add(if n==0{1}else{(n-1)/chunk+1}).ok_or(Error("QUOTA_OVERFLOW"))})?;
                    quota::completion_positions(&narrowed,usage.sequences,remaining,true,usage)?;
                    let bytes=_core["output_slots"].as_array().ok_or(Error("DECLARED_MEMBERS"))?.iter().try_fold(2*self.limits.max_record_bytes,|n,s|n.checked_add(s["max_bytes"].as_u64().ok_or(Error("DECLARED_MEMBER_BOUND"))?).ok_or(Error("QUOTA_OVERFLOW")))?;
                    require(usage.retained_bytes.checked_add(bytes).and_then(|n|n.checked_add(self.limits.sequence_bytes().ok()?+self.limits.cleanup_bytes().ok()?)).is_some_and(|n|n<=self.limits.max_retained_bytes),"PAYLOAD_LOGICAL_REMAINING_BYTES")?;
                    members::Snapshot{domain:sel.domain,root_id:sel.root_id.clone(),execution_scope:sel.execution_scope.clone(),root:root.root().identity().clone(),namespace_epoch:sel.namespace_epoch,
                        alias_binding:sel.alias_exclusion_binding.clone(),ancestor_binding:sel.ancestor_inventory_binding.clone(),acl_binding:sel.acl_policy_binding.clone(),
                        stage_name:p["stage_name"].as_str().ok_or(Error("STAGE_NAME"))?.into(),stage_identity:unknown.clone(),operation_id:facts.facts().operation.operation_id.clone(),fingerprint:facts.facts().operation.fingerprint.clone(),next_sequence:frame.request()["sequence"].as_u64().ok_or(Error("SEQUENCE"))?,max_bytes:p["max_bytes"].as_u64().ok_or(Error("STAGE_BOUND"))?,phase:members::Phase::Staging,members:BTreeMap::new(),directories:BTreeMap::new(),sealed_manifest_binding:None,last_receipt_binding:None,stage_binding:None}
                };
                let sequence=frame.request()["sequence"].as_u64().ok_or(Error("SEQUENCE"))?;
                if verb=="write_member" {
                    let(binding,original,_)=self.captured_member(frame,facts)?;
                    records.insert("captured-member.json".into(),original);
                    records.insert("captured-selection.json".into(),encode(&binding)?);
                    let path=p["member"].as_str().ok_or(Error("MEMBER_PATH"))?;let parts=roots::parts(path)?;let mut parent=String::new();
                    for part in &parts[..parts.len()-1]{if !parent.is_empty(){parent.push('/');}parent.push_str(part);after.directories.entry(parent.clone()).or_insert(unknown.clone());}
                    let member=after.members.entry(path.into()).or_insert(members::Member{identity:unknown,preimage_binding:p["preimage_binding"].clone(),full_sha256:p["full_sha256"].as_str().ok_or(Error("MEMBER_SHA"))?.into(),full_length:p["full_length"].as_u64().ok_or(Error("MEMBER_LENGTH"))?,ranges:Vec::new()});
                    member.ranges.push(members::Range{offset:p["offset"].as_u64().ok_or(Error("OFFSET"))?,length:p["length"].as_u64().ok_or(Error("LENGTH"))?,sha256:p["chunk_sha256"].as_str().ok_or(Error("CHUNK_SHA"))?.into(),sequence,wire_digest:frame.wire_digest().into(),receipt_binding:None});
                }
                if verb=="seal_stage"{after.phase=members::Phase::Sealed;after.sealed_manifest_binding=Some(serde_json::from_value(p["subject_binding"].clone()).map_err(|_|Error("MANIFEST_BINDING"))?);}
                let transition=members::Transition{schema_version:"lab-member-pending-transition/v1".into(),domain:after.domain,root_id:after.root_id.clone(),namespace_epoch:after.namespace_epoch,operation_id:after.operation_id.clone(),fingerprint:after.fingerprint.clone(),sequence,wire_digest:frame.wire_digest().into(),verb:verb.into(),stage_identity:after.stage_identity.clone(),state_sha256:roots::hash(&encode(&after)?)};
                let receipt=encode(&json!({"schema_version":"lab-member-durable-receipt/v1","transition":transition,"outcome":"durable"}))?;
                require(receipt.len()<=65536,"MEMBER_RECEIPT_ENVELOPE")?;
                let rb=bound(&self.selected.receipt_root_id,&format!("sequence-{:016}/member-receipt.json",self.journal.head().ordinal+1),&receipt)?;
                records.insert("proposed.json".into(),encode(&after)?);records.insert("transition.json".into(),encode(&transition)?);records.insert("member-receipt.json".into(),receipt);
                let acknowledged=state::derive_acknowledged(after,&transition,&rb)?;records.insert("acknowledged.json".into(),encode(&acknowledged)?);
                if verb=="seal_stage"{"sealed"}else{"staging"}
            }
            "commit_generation"=>{
                // Publication makes the formerly live stage retained and adds
                // at most one regular pointer object. Reserve these conservative
                // future orphan charges before any rename, not after commit.
                require(usage.orphan_count.checked_add(2).is_some_and(|n|n<=self.limits.max_orphan_count)
                    &&usage.orphan_bytes.checked_add(usage.stage_bytes).and_then(|n|n.checked_add(self.limits.max_record_bytes)).is_some_and(|n|n<=self.limits.max_orphan_bytes),"PUBLISHED_RETAINED_QUOTA")?;
                let s=self.load_commit(facts,&self.effect_input(facts,"commit")?)?;
                let(_,inputs,_)=self.commit_inputs(facts,&s)?;
                let snapshot=self.stage.as_ref().ok_or(Error("STAGE_REQUIRED"))?.snapshot()?;
                let transition=members::Transition{schema_version:"lab-member-pending-transition/v1".into(),domain:snapshot.domain,root_id:snapshot.root_id.clone(),namespace_epoch:snapshot.namespace_epoch,operation_id:snapshot.operation_id.clone(),fingerprint:snapshot.fingerprint.clone(),sequence:frame.request()["sequence"].as_u64().ok_or(Error("SEQUENCE"))?,wire_digest:frame.wire_digest().into(),verb:verb.into(),stage_identity:snapshot.stage_identity,state_sha256:"f".repeat(64)};
                records.insert("publication-transition.json".into(),encode(&transition)?);records.insert("publication-member-receipt.json".into(),encode(&json!({"schema_version":"lab-member-durable-receipt/v1","transition":transition,"outcome":"durable"}))?);
                let name=format!("commit-{}",facts.facts().operation.operation_id);let leaves=["manifest.json","c01-manifest.json","c01-store.json","store.json","runtime-selection.json","control-policy.json","replay-expectation.json","member-manifest.json","publication-original.json","cold-request.json","cold-result.json","native-replay-original.bin","cold-process.json","terminal.json","confirmed.json","phase-01.json","phase-02.json","phase-03.json","phase-04.json","phase-05.json","phase-06.json","phase-07.json","phase-08.json"];
                let originals=leaves.iter().map(|leaf|(leaf.to_string(),Binding{kind:"evidence".into(),root_id:self.selected.generation_journal_root_id.clone(),relative_path:format!("{name}/{leaf}"),sha256:"f".repeat(64),size_bytes:inputs.store.limits.max_record_bytes})).collect::<BTreeMap<_,_>>();
                let m=&inputs.manifest;let c01=generation::c01_manifest(m)?;
                let pointer=generation::PointerRecord{schema_version:"lab-completion-pointer-record/v1".into(),logical_store_id:m.store_id.clone(),writer_epoch:m.writer_epoch,sequence:m.sequence,predecessor_pointer_binding:m.predecessor_pointer_binding.clone(),generation_manifest_binding:bound(&self.selected.generation_journal_root_id,&format!("{name}/c01-manifest.json"),&c01)?,operation_id:m.operation_id.clone()};
                let expected:generation::ReplayExpectation=decode(&inputs.replay_expectation_original,quota::MAX_RECORD)?;
                let request=generation::ColdRequest{schema_version:"lab-generation-cold-request/v1".into(),repair_intent_binding:None,store_selection_binding:inputs.store_binding.clone(),pointer_binding:bound(&inputs.store.pointer_root_id,&inputs.store.pointer_member,&encode(&pointer)?)?,generation_manifest_binding:pointer.generation_manifest_binding.clone(),writer_profile_binding:originals["manifest.json"].clone(),member_manifest_binding:m.member_manifest_binding.clone(),original_cut_binding:m.original_cut_binding.clone(),expected_replay_result_binding:m.expected_replay_result_binding.clone(),replay_expectation:expected,verifier_executable_binding:inputs.verifier_executable,verifier_input_bindings:inputs.verifier_inputs,broker_uid:self.root(&self.selected.generation_root_id)?.root().identity().uid,worker_uid:inputs.verifier_uid,timeout_ms:inputs.store.limits.verifier_timeout_ms,max_result_bytes:inputs.store.limits.max_verifier_result_bytes};
                records.insert("cold-request.json".into(),encode(&request)?);
                records.insert("generation-closure.json".into(),encode(&GenerationClosure{schema_version:"lab-broker-generation-closure/v1".into(),pointer,journal_name:name,originals,control_confirmation:future_confirmation})?);"pointer-committed"
            }
            "close_family"=>{
                if self.restart_only{let ledger=self.current_ledger(facts)?;require(ledger.outcome(&facts.facts().operation.operation_id).is_some_and(|(o,_)|matches!(o,Outcome::Committed|Outcome::Aborted)),"RESTART_CLOSE_NEEDS_TRANSACTION_OUTCOME")?;}
                let b=&self.effect_input(facts,"supervisor")?;let raw=self.read(facts,b,quota::MAX_PACKET)?;
                let p:SupervisorClosure=decode(&raw,quota::MAX_PACKET)?;records.insert("supervisor-closure.json".into(),raw);records.insert("supervisor-original.json".into(),self.read(facts,&p.original_terminal_binding,quota::MAX_PACKET)?);
                let(phase,transition,_) = self.close_slot_transition(facts,&p.operation)?;
                if matches!(phase,ledger::SlotPhase::Closing|ledger::SlotPhase::Closed){
                    let old=p.prior_close_terminal.as_ref().ok_or(Error("CLOSE_PRIOR_TERMINAL"))?;self.verify_prior_close(facts,&p,old)?;
                    records.insert("prior-close-terminal.json".into(),self.read(facts,old,quota::MAX_PACKET)?);
                    records.insert("prior-slot-transition.json".into(),state::read_owned(self.root(&self.selected.control_root_id)?,&transition,65536)?);
                }else{
                    let future=|name:&str|Binding{kind:"evidence".into(),root_id:self.selected.receipt_root_id.clone(),relative_path:format!("sequence-{:016}/{name}",self.journal.head().ordinal+1),sha256:"f".repeat(64),size_bytes:self.limits.max_record_bytes};
                    let terminal=CloseLedgerTerminal{schema_version:"lab-broker-close-ledger-terminal/v1".into(),operation:p.operation.clone(),supervisor_closure_binding:future("supervisor-closure.json"),native_terminal_binding:p.original_terminal_binding.clone(),request_intent_binding:future("intent.json"),request_frame_binding:future("frame.json"),control_preimage:future_confirmation.clone()};
                    records.insert("close-terminal.json".into(),encode(&terminal)?);
                }
                records.insert("control-confirmation.json".into(),encode(&future_confirmation)?);"terminal"
            }
            "repair_derived"=>{
                let s=self.load_derived(facts)?;self.derived_narrow(frame,raw,_core,&s,facts)?;records.insert("derived-intent.json".into(),encode(&s)?);
                let terminal=DerivedTerminal{schema_version:"lab-broker-derived-terminal/v1".into(),operation:facts.facts().operation.clone(),selection_binding:self.effect_input(facts,"derived")?,target_pointer_binding:s.committed_pointer_binding.clone(),members:s.members.iter().map(|(p,m)|(p.clone(),Binding{kind:"evidence".into(),root_id:s.managed_root_id.clone(),relative_path:p.clone(),sha256:m.content_binding.sha256.clone(),size_bytes:m.content_binding.size_bytes})).collect(),outcome:"committed".into()};
                records.insert("derived-terminal.json".into(),encode(&terminal)?);"terminal"
            }
            "reconcile_operation"=>{
                let b=&self.effect_input(facts,"restart")?;
                let bytes=self.read(facts,b,quota::MAX_RECORD)?;let selected_value:Value=decode(&bytes,quota::MAX_RECORD)?;
                if selected_value["schema_version"]=="lab-broker-receipt-recovery-subject/v1"{
                    let subject:state::ReceiptRecoverySubject=decode(&bytes,quota::MAX_RECORD)?;
                    require(subject==self.journal.recovery_subject()?,"RECEIPT_RECOVERY_EXACT_SUBJECT")?;
                    let recovery=facts.facts().recovery.as_ref().ok_or(Error("RECEIPT_RECOVERY_AUTHORITY"))?;
                    require(recovery.action=="quarantine"&&recovery.subject_binding==*b,"RECEIPT_RECOVERY_EXACT_AUTHORITY")?;
                    let ledger=self.current_ledger(facts)?;
                    records.insert("orphan-inventory.json".into(),bytes);
                    records.insert("orphan-terminal.json".into(),encode(&json!({"schema_version":"lab-broker-orphan-terminal/v1","subject":b,"operation":facts.facts().operation,"original_outcome":ledger.outcome(&facts.facts().operation.operation_id),"effect_truth":"UNKNOWN","disposition":"retained-quarantined"}))?);
                    records.insert("control-confirmation.json".into(),encode(&future_confirmation)?);
                    return self.journal.preflight(frame,raw,&self.confirmation,&records,"quarantined",self.response_signer.issuer(),self.prefix_rpc.signer.issuer(),self.prefix_rpc.signer.binding());
                }
                let selected:RestartInputs=decode(&bytes,quota::MAX_RECORD)?;
                let s=self.load_commit(facts,&selected.commit_selection_binding)?;let(admission,_,_)=self.commit_inputs(facts,&s)?;
                let ledger=self.current_ledger(facts)?;let inspection=commit::RestartInspection::inspect(self.root(&self.selected.generation_root_id)?,self.root(&self.selected.generation_journal_root_id)?,self.held,&ledger,admission,selected.selection)?;
                let subject=inspection.repair_subject(selected.kind,selected.verifier.clone())?;self.limits.record(&subject)?;
                // The receipt store has its own selected bound. U08's larger
                // repair-record allowance cannot stand in for this envelope.
                let originals=inspection.selected_originals();
                let read_original=|name:&str|->Result<Vec<u8>>{state::read_owned(self.root(&self.selected.generation_journal_root_id)?,originals.get(name).ok_or(Error("RECOVERY_PREFLIGHT_ORIGINAL"))?,quota::MAX_RECORD)};
                let manifest:generation::GenerationManifest=decode(&read_original("manifest.json")?,quota::MAX_RECORD)?;
                let store:generation::StoreSelection=decode(&read_original("store.json")?,quota::MAX_RECORD)?;
                let runtime:commit::RuntimeCommitSelection=decode(&read_original("runtime-selection.json")?,quota::MAX_RECORD)?;
                let expected:generation::ReplayExpectation=decode(&read_original("replay-expectation.json")?,quota::MAX_RECORD)?;
                let pointer=generation::PointerRecord{schema_version:"lab-completion-pointer-record/v1".into(),logical_store_id:manifest.store_id.clone(),writer_epoch:manifest.writer_epoch,sequence:manifest.sequence,predecessor_pointer_binding:manifest.predecessor_pointer_binding.clone(),generation_manifest_binding:originals.get("c01-manifest.json").ok_or(Error("RECOVERY_PREFLIGHT_ORIGINAL"))?.clone(),operation_id:manifest.operation_id.clone()};
                let branch=format!("recovery-{}",frame.wire_digest());
                require(selected.authority_original_binding==bound(&selected.authority_original_binding.root_id,&selected.authority_original_binding.relative_path,raw)?,"RESTART_ORIGINAL_AUTHORITY")?;
                if selected.kind==commit::RepairKind::SealObservedNew{
                    let subject_value:Value=decode(&subject,quota::MAX_RECORD)?;
                    let authority=facts.facts().recovery.as_ref().ok_or(Error("RECEIPT_RECOVERY_AUTHORITY"))?;
                    let intent=encode(&json!({"schema_version":"lab-generation-repair-intent/v1","subject":subject_value,"subject_binding":authority.subject_binding,"authority_binding":selected.authority_original_binding,"root_inventory_sha256":subject_value["root_inventory_sha256"]}))?;
                    let verifier=selected.verifier.as_ref().ok_or(Error("REPAIR_VERIFIER_SELECTION"))?;
                    let request=generation::ColdRequest{schema_version:"lab-generation-repair-cold-request/v1".into(),repair_intent_binding:Some(bound(&self.selected.generation_journal_root_id,&format!("{branch}/intent.json"),&intent)?),store_selection_binding:runtime.store_binding,pointer_binding:bound(&store.pointer_root_id,&store.pointer_member,&encode(&pointer)?)?,generation_manifest_binding:pointer.generation_manifest_binding.clone(),writer_profile_binding:originals["manifest.json"].clone(),member_manifest_binding:manifest.member_manifest_binding.clone(),original_cut_binding:manifest.original_cut_binding.clone(),expected_replay_result_binding:manifest.expected_replay_result_binding.clone(),replay_expectation:expected.clone(),verifier_executable_binding:verifier.executable.clone(),verifier_input_bindings:expected.adapter_bindings,broker_uid:self.root(&self.selected.generation_root_id)?.root().identity().uid,worker_uid:verifier.worker_uid,timeout_ms:store.limits.verifier_timeout_ms,max_result_bytes:store.limits.max_verifier_result_bytes};
                    records.insert("cold-request.json".into(),encode(&request)?);
                }
                records.insert("recovery-closure.json".into(),encode(&json!({"schema_version":"lab-broker-recovery-closure/v1","terminal":Binding{kind:"evidence".into(),root_id:self.selected.generation_journal_root_id.clone(),relative_path:format!("{branch}/terminal.json"),sha256:"f".repeat(64),size_bytes:store.limits.max_repair_record_bytes},"pointer":if selected.kind==commit::RepairKind::SealObservedNew{Some(pointer)}else{None},"generation":manifest.generation_id,"control_confirmation":future_confirmation}))?);"pointer-committed"
            }
            _=>return Err(Error("PREFLIGHT_EFFECT_VERB")),
        };
        self.journal.preflight(frame,raw,&self.confirmation,&records,phase,self.response_signer.issuer(),self.prefix_rpc.signer.issuer(),self.prefix_rpc.signer.binding())
    }
}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct DerivedMember {pub preimage_binding:Option<Binding>,pub preimage_identity:Option<roots::Identity>,pub content_binding:Binding}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct DerivedSelection {
    pub schema_version:String,pub operation:ledger::Operation,pub managed_root_id:String,
    pub target_commit_selection_binding:Binding,pub target_restart_selection:commit::RestartSelection,
    pub committed_pointer_binding:Binding,pub committed_operation:ledger::Operation,
    pub members:BTreeMap<String,DerivedMember>,pub max_member_bytes:u64,pub capacity_binding:Binding,
}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct DerivedTerminal {pub schema_version:String,pub operation:ledger::Operation,pub selection_binding:Binding,
    pub target_pointer_binding:Binding,pub members:BTreeMap<String,Binding>,pub outcome:String}
impl<'a> Session<'a>{
    fn load_derived(&self,facts:&VerifiedHostFacts)->Result<DerivedSelection>{
        let b=&self.effect_input(facts,"derived")?;
        let s:DerivedSelection=decode(&self.read(facts,b,quota::MAX_RECORD)?,quota::MAX_RECORD)?;
        require(s.schema_version=="lab-broker-derived-selection/v1"&&s.operation==facts.facts().operation
            &&s.operation.operation_id!=s.committed_operation.operation_id
            &&(s.operation.issuer!=s.committed_operation.issuer||s.operation.host_event!=s.committed_operation.host_event)
            &&s.committed_pointer_binding.valid()&&!s.members.is_empty()&&s.members.len()<=1024
            &&(1..=quota::MAX_RECORD).contains(&s.max_member_bytes),"DERIVED_SEPARATE_OPERATION_SCOPE")?;
        let root=self.root(&s.managed_root_id)?;
        for id in [&self.selected.receipt_root_id,&self.selected.stage_root_id,&self.selected.generation_root_id,&self.selected.generation_journal_root_id,&self.selected.control_root_id]{
            state::disjoint_endpoints(root,self.root(id)?)?;
        }
        for(path,m)in &s.members{roots::parts(path)?;require(m.content_binding.valid()&&m.content_binding.size_bytes<=s.max_member_bytes
            &&m.preimage_binding.is_some()==m.preimage_identity.is_some()
            &&m.preimage_binding.as_ref().is_none_or(|b|b.valid()&&b.root_id==s.managed_root_id&&b.relative_path==*path),"DERIVED_MEMBER_SCOPE")?;}
        Ok(s)
    }
    /// A selected derived document can narrow the signed operation; its exact
    /// hash is not permission to expand root, slots, preimages or byte limits.
    /// Called before receipt intent allocation and again before replacement.
    fn derived_narrow(&self,frame:&wire::Frame,raw:&[u8],core:&Value,s:&DerivedSelection,facts:&VerifiedHostFacts)->Result<()> {
        require(frame.request()["payload"]["root_id"].as_str()==Some(s.managed_root_id.as_str()),"DERIVED_SIGNED_ROOT")?;
        let envelope:Value=decode(raw,quota::MAX_PACKET)?;
        let selected_limits=&envelope["permit"]["payload"]["limits"];
        let core_total=core["limits"]["max_total_bytes"].as_u64().ok_or(Error("DERIVED_SIGNED_LIMIT"))?;
        let permit_total=selected_limits["max_total_bytes"].as_u64().ok_or(Error("DERIVED_SIGNED_LIMIT"))?;
        let slots=core["output_slots"].as_array().ok_or(Error("DERIVED_SIGNED_SLOTS"))?;
        require(s.members.len() as u64<=self.limits.max_members&&s.max_member_bytes<=self.limits.max_member_bytes,"DERIVED_SELECTED_MEMBER_LIMIT")?;
        let root=self.root(&s.managed_root_id)?;
        let mut total=0u64;
        for(path,m)in &s.members{
            let slot=slots.iter().find(|slot|slot["root_id"].as_str()==Some(s.managed_root_id.as_str())&&slot["member"].as_str()==Some(path.as_str())).ok_or(Error("DERIVED_UNDECLARED_MEMBER"))?;
            let preimage=m.preimage_binding.as_ref().map(value).transpose()?.unwrap_or(Value::Null);
            require(slot["preimage_binding"]==preimage,"DERIVED_SIGNED_PREIMAGE")?;
            let maximum=slot["max_bytes"].as_u64().ok_or(Error("DERIVED_SIGNED_LIMIT"))?;
            require(m.content_binding.size_bytes<=maximum&&m.content_binding.size_bytes<=self.limits.max_member_bytes,"DERIVED_SIGNED_MEMBER_LIMIT")?;
            total=total.checked_add(m.content_binding.size_bytes).ok_or(Error("DERIVED_SIZE"))?;
            state::verify_owned_preimage(root,path,m.preimage_binding.as_ref(),m.preimage_identity.as_ref(),s.max_member_bytes)?;
        }
        require(total<=core_total&&total<=permit_total&&total<=self.limits.max_stage_bytes,"DERIVED_SIGNED_TOTAL_LIMIT")?;
        let inventory=state::owned_inventory(root,self.limits.max_retained_files,self.limits.max_retained_bytes)?;
        let retained=inventory.values().try_fold(0u64,|sum,(_,size,_)|sum.checked_add(*size).ok_or(Error("DERIVED_SIZE")))?;
        // Keep the full old tree plus each prospective temporary original in
        // the envelope; replacement is never assumed to free reserve early.
        require(retained.checked_add(total).is_some_and(|n|n<=self.limits.max_retained_bytes)
            &&(inventory.len() as u64).checked_add(s.members.len() as u64).is_some_and(|n|n<=self.limits.max_retained_files),"DERIVED_PROSPECTIVE_RETAINED_LIMIT")?;
        let capacity:CapacityOriginal=decode(&self.read(facts,&s.capacity_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        let now=now_seconds()?;
        require(capacity.physical_root==*root.root().identity()&&capacity.control_confirmation==self.confirmation
            &&capacity.not_before<=now&&now<capacity.expires_at&&capacity.remaining.inventory_sha256==roots::hash(&encode(&inventory)?)
            &&capacity.remaining.prefix_sha256==self.confirmation.head.sha256&&capacity.remaining.bytes>=total
            &&capacity.remaining.inodes>=s.members.len() as u64,"DERIVED_PROSPECTIVE_CAPACITY")?;
        self.read(facts,&capacity.held_reservation_binding,quota::MAX_PACKET)?;Ok(())
    }
    fn derived_history(&self,facts:&VerifiedHostFacts,ledger:&Ledger<'a>,s:&DerivedSelection)->Result<commit::HistoryProof>{
        require(ledger.operation(&s.committed_operation.operation_id)==Some(&s.committed_operation)
            &&ledger.outcome(&s.committed_operation.operation_id).is_some_and(|(o,_)|*o==Outcome::Committed),"DERIVED_ORIGINAL_TARGET_COMMITTED")?;
        let selected=self.load_commit(facts,&s.target_commit_selection_binding)?;
        let(admission,_,_)=self.commit_inputs(facts,&selected)?;
        let inspection=commit::RestartInspection::inspect(self.root(&self.selected.generation_root_id)?,self.root(&self.selected.generation_journal_root_id)?,self.held,ledger,admission,s.target_restart_selection.clone())?;
        // The selected target is one original operation, not two unrelated
        // individually committed histories. RestartInspection checks every
        // original; this adapter additionally joins the declared target to it.
        let originals=inspection.selected_originals();
        let terminal:HistoricalGenerationTerminal=decode(&self.read(facts,originals.get("terminal.json").ok_or(Error("DERIVED_TARGET_TERMINAL"))?,quota::MAX_RECORD)?,quota::MAX_RECORD)?;
        let manifest:generation::GenerationManifest=decode(&self.read(facts,originals.get("manifest.json").ok_or(Error("DERIVED_TARGET_MANIFEST"))?,quota::MAX_RECORD)?,quota::MAX_RECORD)?;
        let proof=inspection.already_committed(ledger)?;let pointer=proof.pointer().ok_or(Error("DERIVED_TARGET_POINTER"))?;
        require(terminal.operation==s.committed_operation&&manifest.operation_id==s.committed_operation.operation_id
            &&manifest.original_fingerprint==s.committed_operation.fingerprint&&manifest.store_id==s.committed_operation.store_id
            &&manifest.creation_instance==s.committed_operation.store_instance&&manifest.writer_epoch==s.committed_operation.store_epoch
            &&pointer.operation_id==s.committed_operation.operation_id&&pointer.logical_store_id==manifest.store_id
            &&pointer.writer_epoch==manifest.writer_epoch&&pointer.sequence==manifest.sequence
            &&pointer.generation_manifest_binding==*originals.get("c01-manifest.json").ok_or(Error("DERIVED_TARGET_MANIFEST"))?
            &&terminal.writer_profile_binding==*originals.get("manifest.json").ok_or(Error("DERIVED_TARGET_MANIFEST"))?,"DERIVED_DECLARED_TARGET_OPERATION")?;
        require(bound(&s.committed_pointer_binding.root_id,&s.committed_pointer_binding.relative_path,&encode(pointer)?)?==s.committed_pointer_binding,"DERIVED_EXACT_TARGET")?;Ok(proof)
    }
    fn repair_derived(&mut self,frame:&wire::Frame,raw:&[u8],verified:&authority::VerifiedDispatch,facts:&VerifiedHostFacts,
        ledger:&mut Ledger<'a>,mut pending:PendingSequence)->Result<DispatchResult>{
        require(matches!(verified.decision(),authority::Decision::Fresh{..}),"DERIVED_FRESH_INTENT_REQUIRED")?;
        let selected_binding=self.effect_input(facts,"derived")?;
        require(frame.request()["payload"]["subject_binding"]==value(&selected_binding)?,"DERIVED_EXACT_SUBJECT")?;
        let s=self.load_derived(facts)?;
        let core:Value=decode(&self.read(facts,&facts.facts().core_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        self.derived_narrow(frame,raw,&core,&s,facts)?;
        let proof=self.derived_history(facts,ledger,&s)?;
        let root=self.root(&s.managed_root_id)?;
        let capacity:CapacityOriginal=decode(&self.read(facts,&s.capacity_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
        let now=now_seconds()?;require(capacity.physical_root==*root.root().identity()&&capacity.control_confirmation==self.confirmation
            &&capacity.not_before<=now&&now<capacity.expires_at,"DERIVED_CAPACITY_CUSTODY")?;
        self.read(facts,&capacity.held_reservation_binding,quota::MAX_PACKET)?;
        let mut sources=BTreeMap::new();let mut total=0u64;
        for(path,m)in &s.members{
            let bytes=self.read(facts,&m.content_binding,s.max_member_bytes)?;total=total.checked_add(bytes.len() as u64).ok_or(Error("DERIVED_SIZE"))?;
            sources.insert(path.clone(),bytes);state::verify_owned_preimage(root,path,m.preimage_binding.as_ref(),m.preimage_identity.as_ref(),s.max_member_bytes)?;
        }
        require(total<=self.limits.max_stage_bytes&&capacity.remaining.bytes>=total
            &&capacity.remaining.inodes>=s.members.len() as u64,"DERIVED_REMAINING_CAPACITY")?;
        let inventory=state::owned_inventory_digest(root,self.limits.max_retained_files,self.limits.max_retained_bytes)?;
        require(capacity.remaining.inventory_sha256==inventory&&capacity.remaining.prefix_sha256==self.confirmation.head.sha256,"DERIVED_CAPACITY_INVENTORY")?;
        self.journal.put(&mut pending,"derived-intent.json",&encode(&s)?)?;
        let mut outputs=BTreeMap::new();
        for(index,(path,m))in s.members.iter().enumerate(){
            facts.current()?;ledger.borrow_operation(self.held,&s.operation.operation_id,&s.operation.fingerprint).map_err(|_|Error("DERIVED_CURRENT_OPERATION"))?;
            self.derived_history(facts,ledger,&s)?;
            // Revalidate both selected ancestor chains immediately before each
            // managed replacement. Sibling roots may share ordinary ancestors.
            for id in [&self.selected.receipt_root_id,&self.selected.stage_root_id,&self.selected.generation_root_id,&self.selected.generation_journal_root_id,&self.selected.control_root_id]{state::disjoint_endpoints(root,self.root(id)?)?;}
            let temp=format!(".derived-{}-{index:04}",s.operation.operation_id);
            let output=state::replace_owned_derived(root,path,&temp,m.preimage_binding.as_ref(),m.preimage_identity.as_ref(),&sources[path],s.max_member_bytes)?;
            outputs.insert(path.clone(),output);
        }
        let terminal=DerivedTerminal{schema_version:"lab-broker-derived-terminal/v1".into(),operation:s.operation.clone(),selection_binding:selected_binding,
            target_pointer_binding:s.committed_pointer_binding,members:outputs,outcome:"committed".into()};
        let binding=self.journal.put(&mut pending,"derived-terminal.json",&encode(&terminal)?)?;
        let _=(proof,raw);self.append_control(ledger,Change::Outcome{operation_id:s.operation.operation_id,fingerprint:s.operation.fingerprint,result_binding:control_binding(&binding),outcome:Outcome::Committed},facts.facts().expires_at)?;
        self.finish_sequence(pending,frame,None,Some(binding),"terminal",facts.facts().expires_at)
    }
}

// Versioned read-only adapter for the original supervisor records. These bytes
// are selected by current host facts; they do not construct a native Observation,
// cleanup grant or launch capability. The independent attempt checkpoint is a
// different high-water from Ledger::HostConfirmation.
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct SupervisorEvidenceSelection {
 pub schema_version:String,pub journal_root_id:String,pub journal_prefix:String,
 pub header_binding:Binding,pub checkpoint_binding:Binding,pub original_start_binding:Binding,
 pub records:Vec<Binding>,pub originals:Vec<Binding>,pub cleanup_checkpoint_binding:Binding,
 pub execution_binding:Binding,pub historical_binding:Binding,
}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct NativeJournalLimits{max_records:u64,max_original_bytes:u64,max_record_bytes:u64,max_total_bytes:u64,max_attempts:u64}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct NativeJournalHeader{schema_version:String,domain:Domain,root_id:String,root:roots::Identity,control_root:lab_control_store::custody::Identity,
 authority_domain:String,control_header_sha256:String,supervisor_root_binding:Binding,supervisor_root_identity:roots::Identity,custody_binding:Binding,limits:NativeJournalLimits}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)] #[serde(rename_all="snake_case")]
enum NativeAttemptEvent{Start,Terminal,Recovery}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct NativeAttemptRecord{schema_version:String,sequence:u64,previous_sha256:String,operation:ledger::Operation,attempt_id:String,event:NativeAttemptEvent,
 control_preimage:HostConfirmation,original_binding:Binding,original_start_binding:Binding}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct NativeAttemptCheckpoint{schema_version:String,domain:Domain,journal_root:roots::Identity,root_id:String,journal_header_sha256:String,
 predecessor:ledger::Head,head:ledger::Head,control_preimage:HostConfirmation,operation:Option<ledger::Operation>,attempt_id:Option<String>}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct NativeAttemptLimits{pids:u32,memory_bytes:u64,cpu_quota_us:u32,output_bytes:u64,runtime_ms:u64,cleanup_ms:u64}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct NativeStart{schema_version:String,operation:ledger::Operation,attempt_id:String,containment_binding:Binding,group_identity:roots::Identity,
 execution_binding:Binding,historical_selection:Binding,created_utc_ns:u64,dispatch_until_utc_ns:u64,cleanup_until_utc_ns:u64,limits:NativeAttemptLimits}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct NativeRecovery{schema_version:String,domain:Domain,operation:ledger::Operation,attempt_id:String,original_start_binding:Binding,
 original_checkpoint_binding:Binding,cleanup_authority_binding:Binding,control_preimage:HostConfirmation,group_identity:roots::Identity,
 observed_utc_ns:Option<u64>,subtree_empty:bool,direct_child_reaped:Option<bool>,pid_identity_known:bool,historical_complete:bool,
 observation_error:Option<String>,journal_append_eligible:bool,complete_group_inventory:Option<bool>,outcome:String}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct NativeCleanupAuthority{schema_version:String,domain:Domain,operation:ledger::Operation,original_start_binding:Binding,
 original_checkpoint_binding:Binding,containment_binding:Binding,group_identity:roots::Identity,current_control:HostConfirmation,
 history_binding:Binding,expires_utc_ns:u64,max_cleanup_ms:u64}
/// Current independently selected worker identity adapter, retaining its native
/// source binding. Matching a PID number alone never establishes process identity.
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct WorkerIdentityOriginal{pub schema_version:String,pub domain:Domain,pub operation:ledger::Operation,pub attempt_id:String,
 pub original_start_binding:Binding,pub group_identity:roots::Identity,pub child_pid:u32,pub pid_start_ticks:u64,
 pub native_identity_binding:Binding,pub execution_binding:Binding}
impl Session<'_>{
 fn historical_control(&self,old:&HostConfirmation,current:&HostConfirmation)->Result<()> {
  require(old.schema_version=="lab-host-control-confirmation/v1"&&old.authority_domain==current.authority_domain&&old.root==current.root&&old.header_sha256==current.header_sha256
   &&old.writer.epoch>0&&old.writer.epoch<=i64::MAX as u64&&lab_control_store::codec::identifier(&old.writer.instance)
   &&old.head.sequence>0&&old.head.sequence<=current.head.sequence&&old.predecessor.sequence.checked_add(1)==Some(old.head.sequence),"NATIVE_HISTORICAL_CONTROL")?;
  let root=self.root(&self.selected.control_root_id)?;let raw=state::historical_control_record(root,old)?;let row:Value=decode(&raw,65536)?;
  let row_writer:ledger::WriterFence=serde_json::from_value(row["writer"].clone()).map_err(|_|Error("NATIVE_CONTROL_WRITER"))?;
  // The exact original row can precede an independently attested writer
  // advance at an unchanged head. Native checkpoint selection authenticates
  // the historical fence; current accepted Ledger authenticates the chain.
  // Equal epochs must preserve identity; neither fence may go backwards.
  require(row["schema_version"]=="lab-control-record/v1"&&row["authority_domain"]==old.authority_domain
   &&row["sequence"]==old.head.sequence&&row["previous_sha256"]==old.predecessor.sha256
   &&row_writer.epoch>0&&row_writer.epoch<=old.writer.epoch&&old.writer.epoch<=current.writer.epoch
   &&(row_writer.epoch!=old.writer.epoch||row_writer.instance==old.writer.instance)
   &&(old.writer.epoch!=current.writer.epoch||old.writer.instance==current.writer.instance),"NATIVE_CONTROL_HEAD_JOIN")?;
  if let Some(raw)=state::historical_control_successor(root,old,current)?{
   let next:Value=decode(&raw,65536)?;let writer:ledger::WriterFence=serde_json::from_value(next["writer"].clone()).map_err(|_|Error("NATIVE_SUCCESSOR_WRITER"))?;
   require(next["schema_version"]=="lab-control-record/v1"&&next["authority_domain"]==old.authority_domain
    &&next["sequence"]==old.head.sequence+1&&next["previous_sha256"]==old.head.sha256
    &&writer.epoch>=old.writer.epoch&&writer.epoch<=current.writer.epoch
    &&(writer.epoch!=old.writer.epoch||writer.instance==old.writer.instance),"NATIVE_HISTORICAL_FENCE_CONTRADICTION")?;
  }Ok(())
 }
 fn verify_supervisor_originals(&self,facts:&VerifiedHostFacts,ledger:&Ledger<'_>,proof:&SupervisorClosure,terminal:&NativeSupervisorTerminal)->Result<()> {
  let selected_raw=self.read(facts,&proof.native_evidence_binding,quota::MAX_RECORD)?;
  let s:SupervisorEvidenceSelection=decode(&selected_raw,quota::MAX_RECORD)?;
  require(s.schema_version=="lab-broker-supervisor-original-selection/v1"&&!s.records.is_empty()&&s.records.len()<=4096
    &&s.journal_prefix.is_empty()&&s.records.len()==s.originals.len()&&s.original_start_binding==terminal.original_start_binding
    &&s.execution_binding==terminal.execution_binding&&s.historical_binding==terminal.historical_selection,"NATIVE_SELECTION_SCOPE")?;
  let root=self.root(&s.journal_root_id)?;
  // Only this closed, independently selected original manifest authorizes these
  // nested reads; no arbitrary Binding from the client gets a read primitive.
  let read=|binding:&Binding,max:u64|->Result<Vec<u8>> {
    require(binding.root_id==s.journal_root_id&&!binding.relative_path.starts_with('/'),"NATIVE_ORIGINAL_ROOT")?;
    state::read_owned(root,binding,max)
  };
  let header_raw=read(&s.header_binding,65536)?;let h:NativeJournalHeader=decode(&header_raw,65536)?;let l=&h.limits;
  require(h.schema_version=="lab-supervisor-attempt-journal/v1"&&h.domain==facts.facts().domain&&h.root_id==s.journal_root_id
    &&h.control_root==self.confirmation.root&&h.authority_domain==self.confirmation.authority_domain&&h.control_header_sha256==self.confirmation.header_sha256
    &&h.supervisor_root_binding==proof.containment_selection_binding&&h.custody_binding.valid()
    &&(8..=4096).contains(&l.max_records)&&(2048..=65536).contains(&l.max_original_bytes)&&(2048..=65536).contains(&l.max_record_bytes)
    &&l.max_total_bytes<=536870912&&l.max_total_bytes>=4*(l.max_original_bytes+l.max_record_bytes)&&(1..=1024).contains(&l.max_attempts)
    &&s.records.len() as u64<=l.max_records,"NATIVE_JOURNAL_HEADER")?;
  let header_loc="header.json".to_string();require(s.header_binding.relative_path==header_loc,"NATIVE_HEADER_LOCATOR")?;
  state::verify_directory_layout(root,&s.journal_prefix,&h.root,&["header.json","originals","records"])?;
  let original_rows=state::capture_original_table(root,"originals",l.max_records as usize,l.max_original_bytes,l.max_total_bytes)?;
  let record_rows=state::capture_original_table(root,"records",l.max_records as usize,l.max_record_bytes,l.max_total_bytes)?;
  require(original_rows.len()==s.originals.len()&&record_rows.len()==s.records.len(),"NATIVE_FULL_PREFIX_INVENTORY")?;
  let checkpoint_raw=self.read(facts,&s.checkpoint_binding,65536)?;let checkpoint:NativeAttemptCheckpoint=decode(&checkpoint_raw,65536)?;
  require(s.checkpoint_binding.root_id!=h.root_id,"NATIVE_CHECKPOINT_INDEPENDENCE")?;
  let mut previous=s.header_binding.sha256.clone();let mut total=header_raw.len() as u64;
  let mut starts:BTreeMap<String,(Binding,NativeStart)>=BTreeMap::new();let mut terminals=std::collections::BTreeSet::new();let mut recoveries=std::collections::BTreeSet::new();let mut last=None;let mut found=false;
  let mut retained_rows=Vec::new();
  for(index,(rb,ob))in s.records.iter().zip(&s.originals).enumerate(){
   let name=format!("{:016}.json",index+1);
   require(record_rows.get(&name)==Some(rb)&&original_rows.get(&name)==Some(ob),"NATIVE_ORIGINAL_ORDER")?;
   let rr=read(rb,l.max_record_bytes)?;let raw=read(ob,l.max_original_bytes)?;let row:NativeAttemptRecord=decode(&rr,l.max_record_bytes)?;
   total=total.checked_add((rr.len()+raw.len()) as u64).ok_or(Error("NATIVE_TOTAL"))?;require(total<=l.max_total_bytes,"NATIVE_TOTAL")?;
   require(row.schema_version=="lab-supervisor-attempt-record/v1"&&row.sequence==index as u64+1&&row.previous_sha256==previous
    &&row.original_binding==*ob&&ledger.operation(&row.operation.operation_id)==Some(&row.operation),"NATIVE_RECORD_CHAIN")?;
   self.historical_control(&row.control_preimage,&self.confirmation)?;
   match row.event {
    NativeAttemptEvent::Start=>{let start:NativeStart=decode(&raw,l.max_original_bytes)?;
     require(start.schema_version=="lab-contained-attempt-start/v1"&&start.operation==row.operation&&start.attempt_id==row.attempt_id
      &&start.containment_binding==h.supervisor_root_binding&&start.group_identity.mount_id==h.supervisor_root_identity.mount_id
      &&start.group_identity.uid==h.supervisor_root_identity.uid&&row.original_start_binding==*ob
      &&start.created_utc_ns>0&&start.created_utc_ns<start.dispatch_until_utc_ns&&start.dispatch_until_utc_ns<=start.cleanup_until_utc_ns&&start.cleanup_until_utc_ns<=i64::MAX as u64
      &&(1..=1024).contains(&start.limits.pids)&&(1024*1024..=16*1024*1024*1024).contains(&start.limits.memory_bytes)
      &&(1000..=100000).contains(&start.limits.cpu_quota_us)&&(2..=64*1024*1024).contains(&start.limits.output_bytes)
      &&(1..=86400000).contains(&start.limits.runtime_ms)&&(1..=30000).contains(&start.limits.cleanup_ms)
      &&start.execution_binding.valid()&&start.historical_selection.valid()&&!starts.contains_key(&row.operation.operation_id)
      &&!starts.values().any(|(_,s)|s.attempt_id==start.attempt_id),"NATIVE_START_SCOPE")?;
     roots::name(&start.attempt_id)?;starts.insert(row.operation.operation_id.clone(),(ob.clone(),start));
    }
    NativeAttemptEvent::Terminal=>{let t:NativeSupervisorTerminal=decode(&raw,l.max_original_bytes)?;let(b,start)=starts.get(&row.operation.operation_id).ok_or(Error("NATIVE_START_MISSING"))?;
     require(terminals.insert(row.operation.operation_id.clone())&&t.schema_version=="lab-contained-attempt-terminal/v1"&&t.domain==h.domain
      &&t.operation==row.operation&&t.attempt_id==row.attempt_id&&t.attempt_id==start.attempt_id&&row.original_start_binding==*b
      &&t.original_start_binding==*b&&t.actual_group_identity==start.group_identity&&t.execution_binding==start.execution_binding
      &&t.historical_selection==start.historical_selection&&t.containment_binding==h.supervisor_root_binding&&t.start_utc_ns>=start.created_utc_ns,"NATIVE_TERMINAL_START_JOIN")?;
     if *ob==proof.original_terminal_binding {require(raw==encode(terminal)?&&*b==s.original_start_binding,"NATIVE_SELECTED_TERMINAL")?;found=true;}
    }
    NativeAttemptEvent::Recovery=>{let r:NativeRecovery=decode(&raw,l.max_original_bytes)?;let(b,start)=starts.get(&row.operation.operation_id).ok_or(Error("NATIVE_START_MISSING"))?;
     require(recoveries.insert(row.operation.operation_id.clone())&&r.schema_version=="lab-contained-recovery-observation/v1"&&r.domain==h.domain
      &&r.operation==row.operation&&r.attempt_id==row.attempt_id&&r.attempt_id==start.attempt_id&&r.original_start_binding==*b&&row.original_start_binding==*b
      &&r.group_identity==start.group_identity&&r.control_preimage==row.control_preimage&&r.original_checkpoint_binding.valid()&&r.cleanup_authority_binding.valid()
      &&r.direct_child_reaped.is_none()&&!r.pid_identity_known&&r.outcome=="quarantined","NATIVE_RECOVERY_START_JOIN")?;
    }
   }
   previous=rb.sha256.clone();retained_rows.push(row.clone());last=Some(row);
  }
  let last=last.ok_or(Error("NATIVE_EMPTY_HISTORY"))?;
  require(found&&starts.len() as u64<=l.max_attempts&&checkpoint.schema_version=="lab-host-supervisor-checkpoint/v1"&&checkpoint.domain==h.domain
   &&checkpoint.journal_root==h.root&&checkpoint.root_id==h.root_id&&checkpoint.journal_header_sha256==s.header_binding.sha256
   &&checkpoint.head.sequence==s.records.len() as u64&&checkpoint.head.sha256==previous&&checkpoint.predecessor.sequence+1==checkpoint.head.sequence
   &&checkpoint.predecessor.sha256==last.previous_sha256&&checkpoint.operation.as_ref()==Some(&last.operation)
   &&checkpoint.attempt_id.as_ref()==Some(&last.attempt_id)&&checkpoint.control_preimage==last.control_preimage,"NATIVE_CHECKPOINT_HEAD")?;
  let authority_raw=self.read(facts,&proof.authority_binding,65536)?;let authority:NativeCleanupAuthority=decode(&authority_raw,65536)?;
  let earlier_raw=self.read(facts,&s.cleanup_checkpoint_binding,65536)?;let earlier:NativeAttemptCheckpoint=decode(&earlier_raw,65536)?;
  require(earlier.schema_version=="lab-host-supervisor-checkpoint/v1"&&earlier.domain==h.domain
   &&s.cleanup_checkpoint_binding.root_id!=h.root_id&&earlier.journal_header_sha256==checkpoint.journal_header_sha256
   &&earlier.journal_root==checkpoint.journal_root&&earlier.root_id==checkpoint.root_id
   &&earlier.head.sequence>0&&earlier.head.sequence<=checkpoint.head.sequence
   &&earlier.predecessor.sequence.checked_add(1)==Some(earlier.head.sequence)
   &&s.records[earlier.head.sequence as usize-1].sha256==earlier.head.sha256,"NATIVE_CLEANUP_CHECKPOINT")?;
  let start_row=&retained_rows[earlier.head.sequence as usize-1];
  require(start_row.event==NativeAttemptEvent::Start&&start_row.operation==proof.operation&&start_row.attempt_id==terminal.attempt_id
   &&start_row.original_binding==s.original_start_binding&&start_row.original_start_binding==s.original_start_binding
   &&earlier.predecessor.sha256==start_row.previous_sha256&&earlier.operation.as_ref()==Some(&start_row.operation)
   &&earlier.attempt_id.as_ref()==Some(&start_row.attempt_id)&&earlier.control_preimage==start_row.control_preimage,"NATIVE_CLEANUP_ORIGINAL_START_CHECKPOINT")?;
  self.historical_control(&earlier.control_preimage,&self.confirmation)?;
  require(authority.schema_version=="lab-supervisor-cleanup-selection/v1"&&authority.domain==h.domain&&authority.operation==proof.operation
   &&authority.original_start_binding==s.original_start_binding&&authority.original_checkpoint_binding==s.cleanup_checkpoint_binding
   &&authority.containment_binding==proof.containment_selection_binding&&authority.group_identity==terminal.actual_group_identity
   &&authority.current_control==self.confirmation&&authority.history_binding==s.historical_binding
   &&seconds_to_ns(now_seconds()?)?<authority.expires_utc_ns&&authority.expires_utc_ns<=i64::MAX as u64&&(1..=30000).contains(&authority.max_cleanup_ms),"NATIVE_CLEANUP_AUTHORITY")?;
  let worker:WorkerIdentityOriginal=decode(&self.read(facts,&proof.worker_identity_binding,65536)?,65536)?;
  require(worker.schema_version=="lab-broker-worker-identity/v1"&&worker.domain==h.domain&&worker.operation==proof.operation
   &&worker.attempt_id==terminal.attempt_id&&worker.original_start_binding==s.original_start_binding&&worker.group_identity==terminal.actual_group_identity
   &&worker.child_pid==terminal.child_pid&&Some(worker.pid_start_ticks)==terminal.pid_start_ticks&&worker.execution_binding==s.execution_binding,"NATIVE_WORKER_IDENTITY")?;
  self.read(facts,&worker.native_identity_binding,65536)?;self.read(facts,&s.execution_binding,65536)?;self.read(facts,&s.historical_binding,65536)?;
  require(proof.cleanup_original_binding==proof.original_terminal_binding,"NATIVE_CLEANUP_TERMINAL_SOURCE")?;
  require(self.read(facts,&proof.native_evidence_binding,quota::MAX_RECORD)?==selected_raw&&self.read(facts,&s.checkpoint_binding,65536)?==checkpoint_raw,"NATIVE_SELECTION_CHANGED")?;
  require(state::capture_original_table(root,"originals",l.max_records as usize,l.max_original_bytes,l.max_total_bytes)?==original_rows
   &&state::capture_original_table(root,"records",l.max_records as usize,l.max_record_bytes,l.max_total_bytes)?==record_rows,"NATIVE_ORIGINALS_CHANGED")?;
  facts.current()?;Ok(())
 }
}

#[cfg(test)] impl Session<'_>{pub(crate) fn fixture_observation(&self)->Result<(HostConfirmation,PrefixHead,String)>{let(inv,_)=self.journal.inventory()?;Ok((self.confirmation.clone(),self.journal.head().clone(),inv))}}

#[cfg(test)] impl Session<'_>{pub(crate) fn fixture_stage(&self)->Result<members::Snapshot>{self.stage.as_ref().ok_or(Error("NO_STAGE"))?.snapshot()}}

/// Read-only closed adapter over the pinned U08 original journal profile. It
/// returns no HistoryProof, activation, Stage, or current-pointer selection.
/// A later canonical pointer does not change these immutable historical bytes.
#[derive(Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct HistoricalGenerationTerminal{schema_version:String,operation:ledger::Operation,pointer_binding:Binding,
 generation_manifest_binding:Binding,writer_profile_binding:Binding,cold_result_binding:Binding,
 cold_process_binding:Binding,native_original_binding:Binding,phase_head:Binding}
#[derive(Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct HistoricalGenerationConfirmation{schema_version:String,operation:ledger::Operation,terminal_binding:Binding,confirmation:HostConfirmation}
#[derive(Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct HistoricalPublication{schema_version:String,transition:members::Transition,outcome:String}
impl Session<'_>{
 fn historical_generation_ranges(&self,entry:&RetainedSequence,snapshot:&members::Snapshot,ledger:&Ledger<'_>)->Result<()> {
  let closure_binding=entry.entry.originals.get("generation-closure.json").ok_or(Error("PUBLISHED_ORIGINAL_CLOSURE_MISSING"))?;
  let closure:GenerationClosure=decode(&state::read_owned(self.root(&self.selected.receipt_root_id)?,closure_binding,self.limits.max_record_bytes)?,self.limits.max_record_bytes)?;
  require(closure.schema_version=="lab-broker-generation-closure/v1"&&entry.entry.intent.verb=="commit_generation"
   &&closure.pointer.operation_id==snapshot.operation_id&&closure.pointer.operation_id==entry.entry.intent.operation_id,"HISTORICAL_PUBLICATION_SCOPE")?;
  roots::name(&closure.journal_name)?;
  let journal=self.root(&self.selected.generation_journal_root_id)?;
  require(state::capture_owned_directory(journal,&closure.journal_name,32,quota::MAX_RECORD)?==closure.originals,"HISTORICAL_EXACT_JOURNAL_INVENTORY")?;
  let mut raw=BTreeMap::new();let mut total=0u64;
  for(name,b)in &closure.originals{
   require(b.root_id==self.selected.generation_journal_root_id&&b.relative_path==format!("{}/{name}",closure.journal_name),"HISTORICAL_ORIGINAL_LOCATOR")?;
   let bytes=state::read_owned(journal,b,quota::MAX_RECORD)?;total+=bytes.len() as u64;
   require(total<=23*quota::MAX_RECORD,"HISTORICAL_ORIGINAL_TOTAL")?;raw.insert(name.clone(),bytes);
  }
  let get=|name:&str|raw.get(name).ok_or(Error("HISTORICAL_ORIGINAL_MISSING"));
  let local=|name:&str|closure.originals.get(name).cloned().ok_or(Error("HISTORICAL_BINDING_MISSING"));
  let mandatory=["manifest.json","c01-manifest.json","c01-store.json","store.json","runtime-selection.json","control-policy.json","replay-expectation.json","member-manifest.json","publication-original.json","cold-request.json","cold-result.json","native-replay-original.bin","cold-process.json","terminal.json"];
  let mut names:std::collections::BTreeSet<_>=mandatory.iter().map(|n|n.to_string()).chain((1..=6).map(|n|format!("phase-{n:02}.json"))).collect();
  let mut count=6;
  if raw.contains_key("phase-07.json"){names.insert("phase-07.json".into());count=7;}
  if raw.contains_key("confirmed.json"){require(count==7,"HISTORICAL_WRAPPER_ORDER")?;names.insert("confirmed.json".into());}
  if raw.contains_key("phase-08.json"){require(raw.contains_key("confirmed.json"),"HISTORICAL_WRAPPER_ORDER")?;names.insert("phase-08.json".into());count=8;}
  require(raw.keys().cloned().collect::<std::collections::BTreeSet<_>>()==names,"HISTORICAL_CLOSED_INVENTORY")?;
  let store:generation::StoreSelection=decode(get("store.json")?,quota::MAX_RECORD)?;store.validate()?;
  require(raw.values().all(|r|r.len() as u64<=store.limits.max_record_bytes),"HISTORICAL_ORIGINAL_SELECTED_BOUND")?;
  let manifest:generation::GenerationManifest=decode(get("manifest.json")?,store.limits.max_record_bytes)?;
  let runtime:commit::RuntimeCommitSelection=decode(get("runtime-selection.json")?,store.limits.max_record_bytes)?;
  let policy:generation::ControlPolicy=decode(get("control-policy.json")?,store.limits.max_record_bytes)?;
  require(generation::c01_store(&store)?==*get("c01-store.json")?&&generation::c01_manifest(&manifest)?==*get("c01-manifest.json")?
   &&store.c01_selection_binding.sha256==local("c01-store.json")?.sha256&&store.c01_selection_binding.size_bytes==local("c01-store.json")?.size_bytes,"HISTORICAL_C01_PROJECTIONS")?;
  require(policy.schema_version=="lab-generation-control-policy/v1"&&policy.control_root==self.confirmation.root
   &&policy.authority_domain==self.confirmation.authority_domain&&policy.header_sha256==self.confirmation.header_sha256
   &&policy.control_root_id==self.selected.control_root_id&&policy.control_root_id==store.control_root_id&&policy.writer_domain==store.writer_domain
   &&policy.journal==generation::JournalRootPolicy::from_runtime(journal.root().selection())
   &&store.control_root_binding.sha256==local("control-policy.json")?.sha256&&store.control_root_binding.size_bytes==local("control-policy.json")?.size_bytes,"HISTORICAL_CONTROL_CUSTODY")?;
  let operation=ledger.operation(&snapshot.operation_id).ok_or(Error("HISTORICAL_OPERATION_MISSING"))?;
  let terminal:HistoricalGenerationTerminal=decode(get("terminal.json")?,store.limits.max_record_bytes)?;
  require(terminal.schema_version=="lab-generation-terminal/v1"&&terminal.operation==*operation
   &&ledger.outcome(&snapshot.operation_id)==Some(&(Outcome::Committed,control_binding(&local("terminal.json")?))),"HISTORICAL_ORIGINAL_OUTCOME")?;
  require(runtime.execution_scope.valid()&&runtime.operation_id==operation.operation_id&&runtime.original_fingerprint==operation.fingerprint
   &&runtime.store_binding.sha256==local("store.json")?.sha256&&runtime.store_binding.size_bytes==local("store.json")?.size_bytes
   &&runtime.c01_store_binding==store.c01_selection_binding&&runtime.generation_manifest_binding.sha256==local("manifest.json")?.sha256
   &&runtime.generation_manifest_binding.size_bytes==local("manifest.json")?.size_bytes
   &&runtime.execution_scope.store_id==manifest.store_id&&runtime.execution_scope.instance_id==manifest.creation_instance,"HISTORICAL_RUNTIME_JOIN")?;
  require(manifest.schema_version=="lab-generation-manifest/v1"&&manifest.operation_id==operation.operation_id
   &&manifest.original_fingerprint==operation.fingerprint&&manifest.store_id==operation.store_id&&manifest.creation_instance==operation.store_instance
   &&manifest.writer_epoch==operation.store_epoch&&manifest.store_id==store.store_id&&snapshot.fingerprint==operation.fingerprint,"HISTORICAL_MANIFEST_OPERATION")?;
  let pointer=generation::PointerRecord{schema_version:"lab-completion-pointer-record/v1".into(),logical_store_id:manifest.store_id.clone(),writer_epoch:manifest.writer_epoch,
   sequence:manifest.sequence,predecessor_pointer_binding:manifest.predecessor_pointer_binding.clone(),generation_manifest_binding:local("c01-manifest.json")?,operation_id:operation.operation_id.clone()};pointer.validate()?;
  let pointer_binding=bound(&store.pointer_root_id,&store.pointer_member,&encode(&pointer)?)?;
  require(pointer==closure.pointer&&terminal.pointer_binding==pointer_binding&&terminal.generation_manifest_binding==local("c01-manifest.json")?
   &&terminal.writer_profile_binding==local("manifest.json")?&&terminal.cold_result_binding==local("cold-result.json")?
   &&terminal.cold_process_binding==local("cold-process.json")?&&terminal.native_original_binding==local("native-replay-original.bin")?
   &&terminal.phase_head==local("phase-06.json")?,"HISTORICAL_TERMINAL_JOIN")?;
  use commit::{Phase as P,Visibility as V};
  let phases=[P::Intent,P::GenerationPublished,P::PointerPrepared,P::PointerRenamed,P::PointerSynced,P::ColdVerified,P::OutcomePending,P::Confirmed];
  let vis=[V::OldCanonical,V::OldCanonical,V::OldCanonical,V::CommitUncertain,V::NewUnconfirmed,V::NewUnconfirmed,V::NewUnconfirmed,V::Confirmed];
  let mut previous=None;let mut rows=Vec::new();
  for index in 0..count{let name=format!("phase-{:02}.json",index+1);let p:commit::PhaseRecord=decode(get(&name)?,store.limits.max_record_bytes)?;
   require(p.schema_version=="lab-generation-phase/v1"&&p.sequence==index as u64+1&&p.phase==phases[index]&&p.visibility==vis[index]
    &&p.predecessor_sha256==previous&&p.operation==*operation&&p.store_selection_binding==runtime.store_binding
    &&p.runtime_selection_binding==local("runtime-selection.json")?&&p.generation_manifest_binding==local("c01-manifest.json")?
    &&p.writer_profile_binding==local("manifest.json")?&&p.pointer_binding==pointer_binding,"HISTORICAL_PHASE_CHAIN")?;
   previous=Some(local(&name)?.sha256);rows.push(p);
  }
  require(rows[0].subject_binding==Some(runtime.commit_authority_binding.clone())&&runtime.commit_authority_binding.valid()
   &&[2,3,4].iter().all(|n|rows[*n].subject_binding.is_none())&&rows[5].subject_binding==Some(local("cold-result.json")?)
   &&(count<7||rows[6].subject_binding==Some(local("terminal.json")?))&&(count<8||rows[7].subject_binding==Some(local("confirmed.json")?)),"HISTORICAL_PHASE_SUBJECTS")?;
  let publication:HistoricalPublication=decode(get("publication-original.json")?,65536)?;
  require(publication.schema_version=="lab-member-durable-receipt/v1"&&publication.outcome=="durable"
   &&publication.transition.operation_id==operation.operation_id&&publication.transition.fingerprint==operation.fingerprint
   &&publication.transition.verb=="commit_generation"&&publication.transition.stage_identity==snapshot.stage_identity
   &&publication.transition.sequence==entry.entry.intent.sequence&&publication.transition.wire_digest==entry.entry.intent.wire_sha256
   &&rows[1].subject_binding.as_ref().is_some_and(|b|b.sha256==local("publication-original.json").unwrap().sha256&&b.size_bytes==local("publication-original.json").unwrap().size_bytes),"HISTORICAL_PUBLICATION_ORIGINAL")?;
  let receipt_binding=entry.entry.originals.get("publication-member-receipt.json").ok_or(Error("HISTORICAL_PUBLICATION_RECEIPT"))?;
  require(state::read_owned(self.root(&self.selected.receipt_root_id)?,receipt_binding,65536)?==*get("publication-original.json")?,"HISTORICAL_PUBLICATION_RECEIPT_JOIN")?;
  let native:members::Manifest=decode(get("member-manifest.json")?,65536)?;
  require(manifest.member_manifest_binding.sha256==local("member-manifest.json")?.sha256&&manifest.member_manifest_binding.size_bytes==local("member-manifest.json")?.size_bytes
   &&snapshot.sealed_manifest_binding.as_ref()==Some(&manifest.member_manifest_binding)&&manifest.stage_identity==snapshot.stage_identity
   &&manifest.generation_id==native.generation_name&&store.pointer_root_id==self.selected.generation_root_id
   &&store.generations_root_id==native.root_id,"HISTORICAL_NATIVE_MANIFEST")?;
  let declared:std::collections::BTreeSet<_>=store.member_inventory.iter().map(|m|m.relative_path.clone()).collect();
  require(declared==manifest.members.keys().cloned().collect()&&declared==native.members.keys().cloned().collect(),"HISTORICAL_MEMBER_COVERAGE")?;
  for(path,b)in &manifest.members{let n=&native.members[path];require(b.valid()&&b.root_id==native.root_id&&b.relative_path==format!("{}/{path}",native.generation_name)
   &&b.sha256==n.sha256&&b.size_bytes==n.size_bytes,"HISTORICAL_MEMBER_JOIN")?;}
  let expectation:generation::ReplayExpectation=decode(get("replay-expectation.json")?,store.limits.max_record_bytes)?;expectation.validate()?;
  require(manifest.expected_replay_result_binding.sha256==local("replay-expectation.json")?.sha256&&manifest.expected_replay_result_binding.size_bytes==local("replay-expectation.json")?.size_bytes
   &&expectation.source_cut==manifest.source_cut&&expectation.original_cut_binding==manifest.original_cut_binding&&expectation.reader_inventory_binding==manifest.reader_inventory_binding
   &&expectation.member_inventory_binding.sha256==roots::hash(&encode(&store.member_inventory)?)&&expectation.member_inventory_binding.size_bytes==encode(&store.member_inventory)?.len() as u64
   &&expectation.reader_inventory_binding.sha256==roots::hash(&encode(&store.consumer_inventory)?)&&expectation.reader_inventory_binding.size_bytes==encode(&store.consumer_inventory)?.len() as u64,"HISTORICAL_EXPECTATION")?;
  let request:generation::ColdRequest=decode(get("cold-request.json")?,65536)?;
  require(request.schema_version=="lab-generation-cold-request/v1"&&request.repair_intent_binding.is_none()
   &&request.store_selection_binding==runtime.store_binding&&request.pointer_binding==pointer_binding&&request.generation_manifest_binding==local("c01-manifest.json")?
   &&request.writer_profile_binding==local("manifest.json")?&&request.member_manifest_binding==manifest.member_manifest_binding
   &&request.original_cut_binding==manifest.original_cut_binding&&request.expected_replay_result_binding==manifest.expected_replay_result_binding
   &&request.replay_expectation==expectation&&request.verifier_input_bindings==expectation.adapter_bindings
   &&request.timeout_ms==store.limits.verifier_timeout_ms&&request.max_result_bytes==store.limits.max_verifier_result_bytes,"HISTORICAL_COLD_REQUEST")?;
  let result=generation::validate_cold(&request,get("cold-result.json")?)?;
  let report=get("native-replay-original.bin")?;let process:commit::ColdProcessProof=decode(get("cold-process.json")?,65536)?;
  require(report.len()<=65536&&report.len() as u64==result.native_report_binding.size_bytes&&roots::hash(report)==result.native_report_binding.sha256
   &&process.schema_version=="lab-generation-cold-process/v1"&&process.request_sha256==result.request_sha256
   &&process.result_sha256==local("cold-result.json")?.sha256&&process.native_report_sha256==roots::hash(report)
   &&[&process.process_identity_binding,&process.confinement_binding,&process.retained_originals_binding].iter().all(|b|b.valid())
   &&process.observed_uid==request.worker_uid&&process.observed_uid!=request.broker_uid&&process.executable_binding==request.verifier_executable_binding
   &&process.elapsed_ms==result.elapsed_ms&&process.elapsed_ms<=request.timeout_ms&&process.exit_code==0&&process.cleanup=="clean","HISTORICAL_COLD_PROCESS_ORIGINAL")?;
  let check_confirmation=|conf:&HostConfirmation|->Result<()>{
   self.historical_control(conf,&self.confirmation)?;
   let row:Value=decode(&state::historical_control_record(self.root(&self.selected.control_root_id)?,conf)?,65536)?;
   require(row["change"]==value(&Change::Outcome{operation_id:operation.operation_id.clone(),fingerprint:operation.fingerprint.clone(),result_binding:control_binding(&local("terminal.json")?),outcome:Outcome::Committed})?,"HISTORICAL_EXACT_OUTCOME_RECORD")
  };
  check_confirmation(&closure.control_confirmation)?;
  if raw.contains_key("confirmed.json"){let c:HistoricalGenerationConfirmation=decode(get("confirmed.json")?,store.limits.max_record_bytes)?;
   require(c.schema_version=="lab-generation-confirmed/v1"&&c.operation==*operation&&c.terminal_binding==local("terminal.json")?,"HISTORICAL_CONFIRMATION_SCOPE")?;check_confirmation(&c.confirmation)?;
  }
  // This read checks exact immutable directory/member identities and all
  // acknowledged ranges/full hashes. It does not follow the current pointer.
  state::readonly_ranges(self.root(&self.selected.generation_root_id)?,snapshot,&native.generation_name,Some(&native))?;
  require(state::capture_owned_directory(journal,&closure.journal_name,32,quota::MAX_RECORD)?==closure.originals,"HISTORICAL_ORIGINALS_CHANGED")?;
  Ok(())
 }
}

#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct UnknownInspectionOriginal {
    pub schema_version:String,pub operation:ledger::Operation,pub original_scope_binding:Binding,
    pub selected_control_high_water:HostConfirmation,pub receipt_root:roots::Identity,
    pub receipt_inventory_sha256:Option<String>,pub reason:String,pub writable:bool,
}
/// Fixed bounded inspection route for unavailable consumption/history proof.
/// It creates no Session, Stage, PendingSequence or writable Ledger. The only
/// returned bytes are a separately selected closed original authorized by a
/// fresh disclosure permit; missing history never becomes absent history.
pub(crate) fn inspect_uncertain(host:&FixedHost,prefix:&FixedPrefixClient,raw:&[u8],roots:&BTreeMap<String,&Exclusive<'_>>,
    runtime_raw:&[u8],runtime_binding:&Binding)->Result<Vec<u8>>{
    let frame=wire::Frame::decode(raw).map_err(|_|Error("FRAME"))?;
    require(matches!(frame.request()["verb"].as_str(),Some("inspect"|"inspect_operation")),"UNCERTAIN_INSPECTION_VERB")?;
    let facts=host.query(&frame)?;let f=facts.facts();require(f.query.read_only,"READ_ONLY_HOST_OBSERVATION")?;
    let map=roots.iter().map(|(n,h)|(n.clone(),h.root())).collect();
    require(facts.read_selected(&map,runtime_binding,quota::MAX_PACKET)?==runtime_raw,"RUNTIME_SELECTION_DRIFT")?;
    let runtime:RuntimeSelection=decode(runtime_raw,quota::MAX_PACKET)?;
    require(runtime.schema_version=="lab-broker-runtime-selection/v1"&&runtime.original_scope_binding==host.selection().original_scope_binding
        &&runtime.limits_binding==f.quota_binding,"INSPECTION_RUNTIME_SCOPE")?;
    let scope:PrefixScope=decode(&facts.read_selected(&map,&runtime.original_scope_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
    scope.validate()?;require(scope.operation==f.operation&&scope.control_root==f.ledger_confirmation.root,"INSPECTION_ORIGINAL_SCOPE")?;
    let limits:quota::Limits=decode(&facts.read_selected(&map,&runtime.limits_binding,quota::MAX_PACKET)?,quota::MAX_PACKET)?;limits.validate()?;
    let receipt=roots.get(&runtime.receipt_root_id).copied().ok_or(Error("INSPECTION_RECEIPT_ROOT"))?;
    require(*receipt.root().identity()==scope.receipt_root,"INSPECTION_RECEIPT_ROOT")?;
    let response=SelectedSigner::select(&facts.read_selected(&map,&runtime.receipt_signer_binding,quota::MAX_PACKET)?,&runtime.receipt_signer_binding,f.domain,"broker-response")?;
    require(prefix.signer.binding()==&host.selection().prefix_signer_binding&&response.binding()==&host.selection().receipt_signer_binding,"INSPECTION_SIGNER_SELECTION")?;
    let reason=if f.operation_state==OriginalOperationState::Uncertain{"control-unverified"}
        else{require(state::receipt_structure_uncertain(receipt,&scope,&limits,&prefix.signer,&response)?,"NO_OBSERVED_UNCERTAINTY")?;"receipt-unverified"};
    let inventory=state::owned_inventory_digest(receipt,limits.max_retained_files,limits.max_retained_bytes).ok();
    let issuer_raw=facts.read_selected(&map,&f.issuer_enrollment_binding,8192)?;
    let domain=if f.domain==Domain::Fixture{authority::TrustDomain::Fixture}else{authority::TrustDomain::Actual};
    let issuer=authority::Enrollment::select(&issuer_raw,&f.issuer_enrollment_binding.sha256,domain).map_err(|_|Error("INTENT_ENROLLMENT"))?;
    let now=now_seconds()?;
    // These zero counters are never disclosed as measured values and are
    // unreachable by any mutation/recovery verb on this function.
    let control=authority::ControlSnapshot{domain,caller:host.selection().caller.peer(),now:now as i64,
        activation_expires_at:f.activation_expires_at as i64,operation_id:f.operation.operation_id.clone(),live_scope:f.live_authority_scope.clone(),
        selected_roots:f.roots.iter().map(|r|r.root_id.clone()).collect(),issuer_currentness:authority::IssuerCurrentness{enrollment_digest:wire::content_digest(&issuer_raw),revocation_binding:value(&f.revocation_binding)?,revoked:f.issuer_revoked,checked_at:now as i64},
        disclosure_subjects:f.disclosure_subjects.iter().map(value).collect::<Result<_>>()?,recovery:None,recorded_request:None,
        operation_fingerprint:f.operation.fingerprint.clone(),stage_binding:Value::Null,member_binding:None,original_deadline:0,
        phase:"UNKNOWN".into(),next_sequence:0,next_offset:0,cumulative_bytes:0,cumulative_actions:0,acknowledgment_uncertain:true,replay:None};
    let verified=authority::verify(&frame,host.selection().caller.peer(),&issuer,&Value::Null,&Value::Null,&control).map_err(|e|Error(e.0))?;
    let authority::Decision::Disclosure{subject_binding,max_output_bytes}=verified.decision()else{return Err(Error("DISCLOSURE_REQUIRED"));};
    let selected:Binding=serde_json::from_value(subject_binding.clone()).map_err(|_|Error("INSPECTION_SUBJECT"))?;
    let bytes=facts.read_selected(&map,&selected,(*max_output_bytes).min(quota::MAX_PACKET as usize) as u64)?;
    let observation:UnknownInspectionOriginal=decode(&bytes,quota::MAX_PACKET)?;
    require(observation.schema_version=="lab-broker-unknown-inspection/v1"&&observation.operation==f.operation
        &&observation.original_scope_binding==runtime.original_scope_binding&&observation.selected_control_high_water==f.ledger_confirmation
        &&observation.receipt_root==scope.receipt_root&&observation.receipt_inventory_sha256==inventory
        &&observation.reason==reason&&!observation.writable,"UNKNOWN_INSPECTION_EXACT_OBSERVATION")?;
    require(inventory==state::owned_inventory_digest(receipt,limits.max_retained_files,limits.max_retained_bytes).ok(),"UNKNOWN_INSPECTION_CHANGED")?;
    facts.current()?;Ok(bytes)
}
