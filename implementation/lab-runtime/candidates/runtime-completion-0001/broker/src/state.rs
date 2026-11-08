//! Fixed broker state, original-byte custody and independently confirmed
//! per-sequence prefixes. This protocol does not add control Ledger events.
use crate::{members, quota, roots::{self, Binding, Domain, Error, Exclusive, Identity, Result, require}};
use ed25519_dalek::{Signature, SigningKey, VerifyingKey};
use lab_completion_broker::{self as wire, authority};
use lab_control_store::ledger::{HostConfirmation, Operation, WriterFence};
use serde::{de::DeserializeOwned, Deserialize, Serialize};
use serde_json::{json, Value};
use std::{collections::{BTreeMap, BTreeSet}, fs::File, io::{Read, Write},
    os::{fd::{AsRawFd, FromRawFd, OwnedFd}, unix::fs::MetadataExt}, time::{Duration, Instant, SystemTime, UNIX_EPOCH}};

pub fn encode<T: Serialize>(value: &T) -> Result<Vec<u8>> {
    let value = serde_json::to_value(value).map_err(|_| Error("ENCODE"))?;
    fn valid(v: &Value, depth: usize) -> bool {
        if depth > 64 { return false; }
        match v {
            Value::Number(n) => n.as_i64().is_some(),
            Value::Array(a) => a.iter().all(|x| valid(x, depth + 1)),
            Value::Object(o) => o.values().all(|x| valid(x, depth + 1)),
            _ => true,
        }
    }
    require(valid(&value, 0), "CANONICAL_DOMAIN")?;
    serde_json::to_vec(&value).map_err(|_| Error("ENCODE"))
}
pub fn decode<T: DeserializeOwned + Serialize>(raw: &[u8], limit: u64) -> Result<T> {
    require(limit <= quota::MAX_RECORD && raw.len() as u64 <= limit, "DECODE_BOUND")?;
    let value = serde_json::from_slice(raw).map_err(|_| Error("CLOSED_RECORD"))?;
    require(encode(&value)? == raw, "CANONICAL_BYTES")?;
    Ok(value)
}
pub fn now_seconds() -> Result<u64> {
    let n = SystemTime::now().duration_since(UNIX_EPOCH).map_err(|_| Error("CLOCK"))?.as_secs();
    require(n <= i64::MAX as u64, "CLOCK_BOUND")?; Ok(n)
}
fn interval(start: u64, end: u64, now: u64) -> Result<()> {
    require(start <= now && now < end && end <= i64::MAX as u64, "CURRENT_INTERVAL")
}
pub fn bound(root: &str, path: &str, raw: &[u8]) -> Result<Binding> {
    let value = Binding { kind: "evidence".into(), root_id: root.into(), relative_path: path.into(),
        sha256: roots::hash(raw), size_bytes: raw.len() as u64 };
    require(value.valid(), "ORIGINAL_BINDING")?; Ok(value)
}
fn verify_bytes(raw: &[u8], binding: &Binding) -> Result<()> {
    require(binding.valid() && binding.size_bytes == raw.len() as u64
        && binding.sha256 == roots::hash(raw), "ORIGINAL_BYTES")
}
fn ident(s: &str) -> bool { lab_control_store::codec::identifier(s) }

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Caller { pub pid: i32, pub uid: u32, pub gid: u32 }
impl Caller {
    pub fn peer(&self) -> wire::Peer { wire::Peer { pid: self.pid, uid: self.uid, gid: self.gid } }
    fn valid(&self) -> bool { self.pid > 0 && self.uid < u32::MAX && self.gid < u32::MAX }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SignerSelection {
    pub schema_version: String, pub issuer_ref: String, pub purpose: String,
    pub algorithm: String, pub adapter: String, pub public_key: String, pub domain: Domain,
}
/// The independent expected binding comes from the fixed host launch selection,
/// never from the packet/case author. Fixture selection cannot construct Actual.
pub struct SelectedSigner { selection: SignerSelection, original: Binding, key: VerifyingKey }
impl SelectedSigner {
    pub fn select(raw: &[u8], expected: &Binding, domain: Domain, purpose: &str) -> Result<Self> {
        verify_bytes(raw, expected)?;
        let selection: SignerSelection = decode(raw, quota::MAX_PACKET)?;
        require(selection.schema_version == "lab-broker-fixed-signer/v1"
            && selection.domain == domain && selection.purpose == purpose
            && matches!(purpose, "receipt-prefix" | "broker-response" | "host-selection" | "host-profile-selection" | "control-confirmation")
            && selection.algorithm == "ed25519" && selection.adapter == "owner-hex-v1"
            && ident(&selection.issuer_ref), "SIGNER_ENROLLMENT")?;
        let bytes = wire::unhex::<32>(&selection.public_key).map_err(|_| Error("SIGNER_KEY"))?;
        let key = VerifyingKey::from_bytes(&bytes.try_into().map_err(|_| Error("SIGNER_KEY"))?)
            .map_err(|_| Error("SIGNER_KEY"))?;
        Ok(Self { selection, original: expected.clone(), key })
    }
    pub fn binding(&self) -> &Binding { &self.original }
    pub fn domain(&self) -> Domain { self.selection.domain }
    pub fn issuer(&self) -> &str { &self.selection.issuer_ref }
    pub fn purpose(&self)->&str{&self.selection.purpose}
    pub fn distinct(&self, other: &Self) -> Result<()> {
        require(self.selection.issuer_ref != other.selection.issuer_ref && self.key != other.key
            && self.original != other.original, "ISSUER_DUTY_ALIAS")
    }
    pub fn verify<T: DeserializeOwned + Serialize>(&self, raw: &[u8]) -> Result<T> {
        #[derive(Serialize, Deserialize)] #[serde(deny_unknown_fields)]
        struct Envelope { issuer_ref: String, payload: Value, signature: String }
        let env: Envelope = decode(raw, quota::MAX_PACKET)?;
        require(env.issuer_ref == self.selection.issuer_ref, "ENVELOPE_ISSUER")?;
        let sig = wire::unhex::<64>(&env.signature).map_err(|_| Error("SIGNATURE_ENCODING"))?;
        let sig = Signature::from_slice(&sig).map_err(|_| Error("SIGNATURE_ENCODING"))?;
        self.key.verify_strict(&encode(&json!({"issuer_ref":env.issuer_ref,"payload":env.payload}))?, &sig)
            .map_err(|_| Error("SIGNATURE"))?;
        let payload = serde_json::from_value(env.payload).map_err(|_| Error("CLOSED_PAYLOAD"))?;
        Ok(payload)
    }
    /// Only the fixed process key loader calls this after held-file custody and
    /// exact selection verification. A request never carries a signing key.
    pub(crate) fn signing_key(&self, raw: &[u8]) -> Result<SigningKey> {
        let text = std::str::from_utf8(raw).map_err(|_| Error("PRIVATE_KEY_FORMAT"))?;
        let b = wire::unhex::<32>(text).map_err(|_| Error("PRIVATE_KEY_FORMAT"))?;
        let key = SigningKey::from_bytes(&b.try_into().map_err(|_| Error("PRIVATE_KEY_FORMAT"))?);
        require(key.verifying_key() == self.key, "PRIVATE_KEY_ENROLLMENT")?; Ok(key)
    }
    pub(crate) fn sign<T: Serialize>(&self, key: &SigningKey, payload: &T) -> Result<Vec<u8>> {
        require(key.verifying_key() == self.key, "PRIVATE_KEY_ENROLLMENT")?;
        let v = serde_json::to_value(payload).map_err(|_| Error("ENCODE"))?;
        let raw = encode(&authority::signed_record(&v, self.issuer(), key).map_err(|_| Error("SIGN"))?)?;
        require(raw.len() <= quota::MAX_PACKET as usize, "SIGNED_PACKET_BOUND")?; Ok(raw)
    }
}

/// Stable scope is separate from changing Ledger/prefix heads. The original
/// operation's issuer/event remain untouched; no new event is consumed here.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PrefixScope {
    pub schema_version: String, pub domain: Domain, pub authority_domain: String,
    pub control_root: lab_control_store::custody::Identity,
    pub receipt_root: Identity, pub receipt_root_id: String,
    pub writer: WriterFence, pub execution_scope: roots::ExecutionScope,
    pub operation: Operation, pub recipient: Caller, pub channel_binding: Binding,
}
impl PrefixScope {
    pub fn validate(&self) -> Result<()> {
        require(self.schema_version == "lab-broker-receipt-scope/v1"
            && ident(&self.authority_domain) && ident(&self.writer.instance)
            && self.writer.epoch > 0 && self.writer.epoch <= i64::MAX as u64
            && !self.receipt_root_id.is_empty() && self.receipt_root_id.chars().count() <= 4096
            && self.execution_scope.valid() && self.recipient.valid() && self.channel_binding.valid()
            && ident(&self.operation.operation_id) && roots::digest(&self.operation.fingerprint)
            && self.operation.store_id == self.execution_scope.store_id
            && self.operation.store_instance == self.execution_scope.instance_id
            && self.operation.holder == self.execution_scope.principal_ref
            && self.operation.slot_epoch == self.execution_scope.slot_epoch, "PREFIX_SCOPE")
    }
    pub fn digest(&self) -> Result<String> { self.validate()?; Ok(roots::hash(&encode(self)?)) }
    /// History identity does not change when an admission channel, nonce or
    /// writer activation changes. Such changes require fresh authenticated
    /// selection and never create a parallel receipt namespace.
    pub fn history_key(&self) -> Result<String> {
        self.validate()?;
        Ok(roots::hash(&encode(&json!({"schema_version":"lab-broker-prefix-history-key/v1",
            "domain":self.domain,"authority_domain":self.authority_domain,
            "control_root":self.control_root,"receipt_root":self.receipt_root,
            "operation_id":self.operation.operation_id,"fingerprint":self.operation.fingerprint}))?))
    }
    pub fn check_ledger(&self, ledger: &HostConfirmation) -> Result<()> {
        self.validate()?;
        require(ledger.schema_version == "lab-host-control-confirmation/v1"
            && ledger.authority_domain == self.authority_domain && ledger.root == self.control_root
            && ledger.writer == self.writer, "PREFIX_CONTROL_JOIN")
    }
    fn check_current_lineage(&self, ledger: &HostConfirmation) -> Result<()> {
        self.validate()?;
        require(ledger.schema_version == "lab-host-control-confirmation/v1"
            && ledger.authority_domain == self.authority_domain && ledger.root == self.control_root
            && ledger.writer.epoch >= self.writer.epoch && ledger.writer.epoch <= i64::MAX as u64
            && ident(&ledger.writer.instance)
            && (ledger.writer.epoch != self.writer.epoch || ledger.writer.instance == self.writer.instance),
            "CURRENT_CONTROL_LINEAGE")
    }
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PrefixHead { pub ordinal: u64, pub entry_sha256: String }
impl PrefixHead {
    pub fn genesis(scope: &PrefixScope) -> Result<Self> {
        Ok(Self { ordinal: 0, entry_sha256: scope.digest()? })
    }
    fn valid(&self) -> bool { self.ordinal <= 4096 && roots::digest(&self.entry_sha256) }
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PrefixRequest {
    #[serde(default,skip_serializing_if="Option::is_none")]
    pub current_admission:Option<PrefixAdmission>,
    pub schema_version: String, pub scope: PrefixScope, pub prior: PrefixHead,
    pub next: PrefixHead, pub entry_binding:Binding,pub sequence: u64, pub wire_sha256: String,
    pub ledger_confirmation: HostConfirmation, pub challenge: String,
    pub not_before: u64, pub expires_at: u64,
}
impl PrefixRequest {
    pub fn validate(&self, now: u64) -> Result<()> {
        check_prefix_admission(&self.scope,&self.ledger_confirmation,self.current_admission.as_ref(),Some(now))?;
        require(self.schema_version == "lab-broker-prefix-cas-request/v1"
            && self.prior.valid() && self.next.valid()
            && self.next.ordinal == self.prior.ordinal.checked_add(1).ok_or(Error("PREFIX_OVERFLOW"))?
            && self.entry_binding.valid()&&self.entry_binding.root_id==self.scope.receipt_root_id
            &&self.entry_binding.sha256==self.next.entry_sha256
            &&[format!("sequence-{:016}/entry.json",self.next.ordinal),format!("recovery-{:016}/entry.json",self.next.ordinal)].contains(&self.entry_binding.relative_path)
            && self.sequence < i64::MAX as u64 && roots::digest(&self.wire_sha256)
            && roots::digest(&self.challenge), "PREFIX_CAS_REQUEST")?;
        interval(self.not_before, self.expires_at, now)
    }
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PrefixConfirmation {
    pub schema_version: String, pub request: PrefixRequest,
    pub signer_enrollment_binding: Binding, pub result: String,
}
pub struct VerifiedPrefix {
    pub(crate) value: PrefixConfirmation, pub(crate) original: Vec<u8>,
}
impl VerifiedPrefix {
    pub fn verify(raw: &[u8], signer: &SelectedSigner, expected: &PrefixRequest,
                  now: u64) -> Result<Self> {
        expected.validate(now)?;
        let value: PrefixConfirmation = signer.verify(raw)?;
        require(value.schema_version == "lab-broker-prefix-confirmation/v1"
            && value.request == *expected && value.signer_enrollment_binding == *signer.binding()
            && signer.domain() == expected.scope.domain && value.result == "confirmed",
            "PREFIX_CONFIRMATION_SCOPE")?;
        Ok(Self { value, original: raw.into() })
    }
    pub fn head(&self) -> &PrefixHead { &self.value.request.next }
}

/// Stable no-follow reads under an already held and selected root. Metadata,
/// read length, attachment and bytes are checked before and after use.
fn read_file(parent: &File, name: &str, root: &Identity, max: u64) -> Result<Vec<u8>> {
    require(max > 0 && max <= quota::MAX_RECORD, "READ_BOUND")?;
    let mut f = roots::open_child(parent, name, libc::O_RDONLY, 0, true)?;
    let id = roots::owned_file(&f, root.uid, root.mount_id)?;
    let before = f.metadata()?;
    require(before.len() <= max, "READ_BOUND")?;
    let mut raw = Vec::new(); Read::by_ref(&mut f).take(max + 1).read_to_end(&mut raw)?;
    let after = f.metadata()?;
    let named = roots::open_child(parent, name, libc::O_RDONLY, 0, true)?;
    require(raw.len() as u64 == before.len() && raw.len() as u64 <= max
        && roots::owned_file(&named, root.uid, root.mount_id)? == id
        && before.len() == after.len() && before.mtime() == after.mtime()
        && before.mtime_nsec() == after.mtime_nsec() && before.ctime() == after.ctime()
        && before.ctime_nsec() == after.ctime_nsec(), "ORIGINAL_CHANGED")?; Ok(raw)
}
fn put_file(parent: &File, name: &str, root: &Identity, raw: &[u8], max: u64) -> Result<()> {
    require(raw.len() as u64 <= max && max <= quota::MAX_RECORD, "WRITE_BOUND")?;
    let mut f = roots::open_child(parent, name, libc::O_WRONLY | libc::O_CREAT | libc::O_EXCL, 0o600, true)?;
    roots::owned_file(&f, root.uid, root.mount_id)?;
    f.write_all(raw)?; f.sync_all()?; parent.sync_all()?;
    require(read_file(parent, name, root, max)? == raw, "PERSISTED_ORIGINAL")
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RequestIntent {
    #[serde(default,skip_serializing_if="Option::is_none")]
    pub current_admission:Option<PrefixAdmission>,
    pub schema_version: String, pub scope_sha256: String, pub ordinal: u64,
    pub previous: PrefixHead, pub operation_id: String, pub sequence: u64,
    pub wire_sha256: String, pub original_fingerprint: String, pub verb: String,
    pub ledger_confirmation: HostConfirmation,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SequenceEntry {
    pub schema_version: String, pub intent: RequestIntent,
    pub originals: BTreeMap<String, Binding>,
    pub phase: String, pub status: String,
}
#[derive(Clone, Debug)]
pub struct RetainedSequence {
    pub entry: SequenceEntry, pub entry_binding: Binding, pub response: Vec<u8>,
    pub snapshot: Option<members::Snapshot>,
}

#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct RetainedTail {pub name:String,pub identity:Identity,pub intent:RequestIntent,pub originals:BTreeMap<String,Binding>}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct ReceiptRecoverySubject {pub schema_version:String,pub original_scope_sha256:String,pub previous:PrefixHead,
    pub operation:Operation,pub physical_root:Identity,pub tails:BTreeMap<String,RetainedTail>,pub action:String}
fn capture_tail(root:&File,name:&str,scope:&PrefixScope,limits:&quota::Limits)->Result<RetainedTail>{
    require((name.starts_with("sequence-")||name.starts_with("recovery-"))&&name.len()==25,"TAIL_DIRECTORY_NAME")?;
    let dir=roots::open_child(root,name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
    let identity=roots::owned_dir(&dir,scope.receipt_root.uid,scope.receipt_root.mount_id)?;
    let names=roots::names(&dir,quota::SEQUENCE_FILES as usize+1)?;let mut originals=BTreeMap::new();
    for leaf in &names{let raw=read_file(&dir,leaf,&scope.receipt_root,limits.max_record_bytes)?;
        originals.insert(leaf.clone(),bound(&scope.receipt_root_id,&format!("{name}/{leaf}"),&raw)?);}
    let intent:RequestIntent=decode(&read_file(&dir,"intent.json",&scope.receipt_root,limits.max_record_bytes)?,limits.max_record_bytes)?;
    let raw=read_file(&dir,"frame.json",&scope.receipt_root,limits.max_record_bytes)?;let frame=wire::Frame::decode(&raw).map_err(|_|Error("TAIL_FRAME"))?;
    require(intent.schema_version=="lab-broker-sequence-intent/v1"&&intent.scope_sha256==scope.digest()?
        &&intent.operation_id==scope.operation.operation_id&&intent.original_fingerprint==scope.operation.fingerprint
        &&intent.wire_sha256==frame.wire_digest()&&frame.request()["operation_id"]==intent.operation_id
        &&frame.request()["sequence"]==intent.sequence&&frame.request()["verb"]==intent.verb
        &&intent.sequence<i64::MAX as u64,"TAIL_CONSUMPTION_ORIGINAL")?;
    require(names==roots::names(&dir,quota::SEQUENCE_FILES as usize+1)?,"TAIL_CHANGED")?;
    Ok(RetainedTail{name:name.into(),identity,intent,originals})
}
fn selected_chain(root:&File,scope:&PrefixScope,limits:&quota::Limits,selected:&PrefixHead,
    witness:&SelectedSigner,response:&SelectedSigner,allow_tail:bool,pending:Option<&PrefixRequest>)
    ->Result<(Vec<RetainedSequence>,BTreeMap<String,RetainedTail>)>{
    let names=roots::names(root,(limits.max_sequences+limits.max_orphan_count+1) as usize)?;
    let mut proofs=BTreeMap::new();
    for name in &names{
        let dir=roots::open_child(root,name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
        roots::owned_dir(&dir,scope.receipt_root.uid,scope.receipt_root.mount_id)?;
        let leaves=roots::names(&dir,quota::SEQUENCE_FILES as usize+1)?;
        if leaves.contains(&"confirmation.json".into()){
            let proof:PrefixConfirmation=witness.verify(&read_file(&dir,"confirmation.json",&scope.receipt_root,quota::MAX_PACKET)?)?;
            proof.request.validate(proof.request.not_before)?;
            require(proof.schema_version=="lab-broker-prefix-confirmation/v1"&&proof.result=="confirmed"
                &&proof.signer_enrollment_binding==*witness.binding()&&proof.request.scope==*scope
                &&proof.request.entry_binding.relative_path==format!("{name}/entry.json"),"CHAIN_ORIGINAL_CONFIRMATION")?;
            require(proofs.insert(proof.request.next.entry_sha256.clone(),(name.clone(),proof.request,true)).is_none(),"DUPLICATE_CONFIRMED_ENTRY")?;
        }
    }
    if let Some(q)=pending{
        q.validate(q.not_before)?;
        let name=q.entry_binding.relative_path.strip_suffix("/entry.json").ok_or(Error("PENDING_ENTRY_LOCATION"))?.to_string();
        require(names.contains(&name)&&q.scope==*scope,"PENDING_ENTRY_LOCATION")?;
        if let Some((old_name,old,_))=proofs.get(&q.next.entry_sha256){require(*old==*q&&*old_name==name,"PENDING_EXISTING_CONFIRMATION")?;}
        else{proofs.insert(q.next.entry_sha256.clone(),(name,q.clone(),false));}
    }
    let mut selected_path=Vec::new();let mut cursor=selected.clone();
    while cursor.ordinal>0{
        let item=proofs.get(&cursor.entry_sha256).ok_or(Error("CONFIRMED_PREFIX_MISSING"))?;
        require(item.1.next==cursor&&selected_path.len()<limits.max_sequences as usize,"CONFIRMED_PREFIX_CHAIN")?;
        selected_path.push(item.clone());cursor=item.1.prior.clone();
    }
    require(cursor==PrefixHead::genesis(scope)?,"CONFIRMED_GENESIS")?;selected_path.reverse();
    let mut entries=Vec::new();let mut accounted=BTreeMap::new();let mut used_names=BTreeSet::new();let mut used_sequences=BTreeSet::new();
    let mut prior=cursor;
    for(name,q,confirmed)in selected_path{
        require(used_names.insert(name.clone()),"DUPLICATE_PREFIX_DIRECTORY")?;
        let dir=roots::open_child(root,&name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
        let e=load_sequence(&dir,&name,scope,limits,&prior,confirmed)?;validate_response(&e,response)?;
        verify_prefix_admission(scope,e.entry.intent.current_admission.as_ref(),witness)?;
        require(e.entry.intent.current_admission==q.current_admission,"PREFIX_ADMISSION_ORIGINAL_JOIN")?;
        require(e.entry_binding==q.entry_binding&&e.entry.intent.sequence==q.sequence&&e.entry.intent.wire_sha256==q.wire_sha256
            &&e.entry.intent.ledger_confirmation==q.ledger_confirmation&&used_sequences.insert(q.sequence),"CONFIRMED_ENTRY_SCOPE")?;
        if let Some(b)=e.entry.originals.get("orphan-inventory.json"){
            let raw=read_file(&dir,"orphan-inventory.json",&scope.receipt_root,limits.max_record_bytes)?;verify_bytes(&raw,b)?;
            let subject:ReceiptRecoverySubject=decode(&raw,limits.max_record_bytes)?;
            require(subject.schema_version=="lab-broker-receipt-recovery-subject/v1"&&subject.original_scope_sha256==scope.digest()?
                &&subject.operation==scope.operation&&subject.physical_root==scope.receipt_root&&subject.previous==prior
                &&subject.action=="quarantine"&&!subject.tails.is_empty()&&e.entry.intent.verb=="reconcile_operation"
                &&e.entry.phase=="quarantined","ORPHAN_RECOVERY_SUBJECT")?;
            for(n,t)in subject.tails{
                require(n==t.name&&n!=name&&!used_names.contains(&n)&&t.intent.sequence<q.sequence,"ORPHAN_CONSUMED_SEQUENCE")?;
                if let Some(old)=accounted.insert(n.clone(),t.clone()){require(old==t,"ORPHAN_HISTORY_CHANGED")?;}
            }
        }
        prior=q.next;entries.push(e);
    }
    let mut tails=BTreeMap::new();
    for name in &names{if !used_names.contains(name){
        let tail=capture_tail(root,name,scope,limits)?;
        require(used_sequences.insert(tail.intent.sequence),"DUPLICATE_CONSUMED_SEQUENCE")?;
        if let Some(expected)=accounted.get(name){require(*expected==tail,"RETAINED_ORPHAN_CHANGED")?;}
        else{require(allow_tail,"UNACCOUNTED_RECEIPT_TAIL")?;tails.insert(name.clone(),tail);}
    }}
    require(accounted.keys().all(|n|names.contains(n)&&!used_names.contains(n)),"RETAINED_ORPHAN_MISSING")?;
    require(names==roots::names(root,(limits.max_sequences+limits.max_orphan_count+1) as usize)?,"PREFIX_INVENTORY_CHANGED")?;
    Ok((entries,tails))
}

/// A loaded prefix alone does not offer writes. The dispatcher must additionally
/// reopen exact current Ledger, restore Stage (which verifies acknowledged byte
/// ranges), and authenticate the new per-message permit and capacity selection.
pub struct ReceiptJournal<'a> {
    hold: &'a Exclusive<'a>, scope: PrefixScope, limits: quota::Limits,
    head: PrefixHead, entries: Vec<RetainedSequence>, pending: bool, unaccounted:BTreeMap<String,RetainedTail>,
    current_admission:Option<PrefixAdmission>,
}
pub struct PendingSequence {
    dir: File, name: String, intent: RequestIntent, originals: BTreeMap<String, Binding>,
    entry: Option<SequenceEntry>, entry_binding: Option<Binding>,
}
impl PendingSequence {pub(crate) fn ordinal(&self)->u64{self.intent.ordinal}
    pub(crate) fn original_control(&self)->&HostConfirmation{&self.intent.ledger_confirmation}
    pub(crate) fn has_original(&self,name:&str)->bool{self.originals.contains_key(name)}
    pub(crate) fn original(&self,name:&str)->Result<Binding>{self.originals.get(name).cloned().ok_or(Error("PENDING_ORIGINAL_MISSING"))}
}
impl<'a> ReceiptJournal<'a> {
    pub fn open_empty(hold: &'a Exclusive<'a>, scope: PrefixScope, limits: quota::Limits) -> Result<Self> {
        hold.validate()?; scope.validate()?; limits.validate()?;
        require(*hold.root().identity() == scope.receipt_root
            && hold.root().selection().root_id == scope.receipt_root_id
            && hold.root().selection().domain == scope.domain
            && hold.root().selection().execution_scope == scope.execution_scope
            && roots::names(hold.directory(), 1)?.is_empty(), "RECEIPT_GENESIS_SELECTION")?;
        Ok(Self { hold, head: PrefixHead::genesis(&scope)?, scope, limits, entries: Vec::new(), pending: false, unaccounted:BTreeMap::new(),current_admission:None })
    }
    fn guard(&self) -> Result<()> {
        self.hold.validate()?;
        require(*self.hold.root().identity() == self.scope.receipt_root, "RECEIPT_ATTACHMENT")
    }
    pub fn head(&self) -> &PrefixHead { &self.head }
    pub fn scope(&self) -> &PrefixScope { &self.scope }
    pub fn is_pending(&self) -> bool { self.pending }
    pub fn entries(&self) -> Result<&[RetainedSequence]> {
        self.guard()?; require(!self.pending, "PENDING_SEQUENCE")?; Ok(&self.entries)
    }
    pub(crate) fn confirmed_entries(&self,witness:&SelectedSigner,response:&SelectedSigner)->Result<&[RetainedSequence]>{
        self.guard()?;
        let (entries,_)=selected_chain(self.hold.directory(),&self.scope,&self.limits,&self.head,witness,response,true,None)?;
        require(entries.len()==self.entries.len()&&entries.iter().zip(&self.entries).all(|(a,b)|a.entry_binding==b.entry_binding&&a.response==b.response),"CONFIRMED_ORIGINAL_DRIFT")?;
        Ok(&self.entries)
    }
    pub(crate) fn consumed_requests(&self)->Result<BTreeMap<u64,String>>{
        self.guard()?;let mut consumed=BTreeMap::new();
        for name in roots::names(self.hold.directory(),(self.limits.max_sequences+self.limits.max_orphan_count+1) as usize)?{
            let t=capture_tail(self.hold.directory(),&name,&self.scope,&self.limits)?;
            require(consumed.insert(t.intent.sequence,t.intent.wire_sha256).is_none(),"DUPLICATE_CONSUMED_SEQUENCE")?;
        }Ok(consumed)
    }
    pub(crate) fn recovery_subject(&self)->Result<ReceiptRecoverySubject>{
        self.guard()?;require(!self.unaccounted.is_empty(),"NO_UNACCOUNTED_TAIL")?;
        for(n,t)in &self.unaccounted{require(*t==capture_tail(self.hold.directory(),n,&self.scope,&self.limits)?,"RECOVERY_TAIL_CHANGED")?;}
        Ok(ReceiptRecoverySubject{schema_version:"lab-broker-receipt-recovery-subject/v1".into(),original_scope_sha256:self.scope.digest()?,previous:self.head.clone(),operation:self.scope.operation.clone(),physical_root:self.scope.receipt_root.clone(),tails:self.unaccounted.clone(),action:"quarantine".into()})
    }
    pub(crate) fn has_unaccounted_tail(&self)->bool{!self.unaccounted.is_empty()}

    pub fn inventory(&self) -> Result<(String, quota::Usage)> {
        self.guard()?;
        let mut rows: Vec<(String, Identity, u64, String)> = Vec::new();
        let mut usage = quota::Usage::default();
        for name in roots::names(self.hold.directory(), (self.limits.max_sequences+self.limits.max_orphan_count+1) as usize)? {
            let dir = roots::open_child(self.hold.directory(), &name, libc::O_RDONLY | libc::O_DIRECTORY, 0, true)?;
            let id = roots::owned_dir(&dir, self.scope.receipt_root.uid, self.scope.receipt_root.mount_id)?;
            usage.retained_inodes += 1; usage.sequences += 1;
            rows.push((name.clone(), id, 0, String::new()));
            for leaf in roots::names(&dir, (quota::SEQUENCE_FILES + quota::CLEANUP_FILES) as usize + 1)? {
                let raw = read_file(&dir, &leaf, &self.scope.receipt_root, self.limits.max_record_bytes)?;
                let f = roots::open_child(&dir, &leaf, libc::O_RDONLY, 0, true)?;
                rows.push((format!("{name}/{leaf}"), Identity::observe(&f)?, raw.len() as u64, roots::hash(&raw)));
                usage.retained_inodes += 1;
                usage.retained_bytes = usage.retained_bytes.checked_add(raw.len() as u64).ok_or(Error("QUOTA_OVERFLOW"))?;
            }
        }
        usage.inflight = self.pending as u64;
        Ok((roots::hash(&encode(&rows)?), usage))
    }
    pub(crate) fn begin(&mut self, frame: &wire::Frame, full_frame: &[u8], fingerprint: &str,
                       ledger: &HostConfirmation, reserve: &quota::Remaining) -> Result<PendingSequence> {
        self.begin_mode(frame,full_frame,fingerprint,ledger,reserve,false)
    }
    pub(crate) fn begin_terminal(&mut self,frame:&wire::Frame,full_frame:&[u8],fingerprint:&str,ledger:&HostConfirmation,reserve:&quota::Remaining)->Result<PendingSequence>{
        require(matches!(frame.request()["verb"].as_str(),Some("reconcile_operation"|"close_family")),"TERMINAL_VERB")?;
        self.begin_mode(frame,full_frame,fingerprint,ledger,reserve,true)
    }
    fn begin_mode(&mut self,frame:&wire::Frame,full_frame:&[u8],fingerprint:&str,ledger:&HostConfirmation,reserve:&quota::Remaining,terminal:bool)->Result<PendingSequence>{
        self.guard()?; require(!self.pending, "PENDING_SEQUENCE")?;
        check_prefix_admission(&self.scope,ledger,self.current_admission.as_ref(),Some(now_seconds()?))?;
        if self.current_admission.is_some(){require(matches!(frame.request()["verb"].as_str(),Some("reconcile_operation"|"close_family")),"RESTART_NO_PRODUCER")?;}
        require(frame.wire_digest() == roots::hash(full_frame) && frame.wire_digest() == wire::Frame::decode(full_frame).map_err(|_| Error("FRAME"))?.wire_digest()
            && frame.request()["operation_id"] == self.scope.operation.operation_id
            && fingerprint == self.scope.operation.fingerprint, "REQUEST_ORIGINAL_SCOPE")?;
        let sequence = frame.request()["sequence"].as_u64().ok_or(Error("SEQUENCE"))?;
        require(!self.consumed_requests()?.contains_key(&sequence), "SEQUENCE_ALREADY_RECORDED")?;
        require(self.unaccounted.is_empty()||frame.request()["verb"]=="reconcile_operation","TAIL_REQUIRES_RECONCILIATION")?;
        let ordinal = self.head.ordinal.checked_add(1).ok_or(Error("SEQUENCE_OVERFLOW"))?;
        let intent = RequestIntent { current_admission:self.current_admission.clone(),schema_version: "lab-broker-sequence-intent/v1".into(),
            scope_sha256: self.scope.digest()?, ordinal, previous: self.head.clone(),
            operation_id: self.scope.operation.operation_id.clone(), sequence,
            wire_sha256: frame.wire_digest().into(), original_fingerprint: fingerprint.into(),
            verb: frame.request()["verb"].as_str().ok_or(Error("VERB"))?.into(), ledger_confirmation: ledger.clone() };
        let raw = encode(&intent)?; self.limits.record(&raw)?; self.limits.record(full_frame)?;
        let (inventory, usage) = self.inventory()?;
        if terminal{
            quota::admit_cleanup(&self.limits,&usage,reserve,&inventory,&self.head.entry_sha256)?;
        }else{quota::admit(&self.limits, &usage, reserve, &inventory, &self.head.entry_sha256)?;}
        // Fence before the first syscall. An error can have retained partial bytes.
        self.pending = true;
        let name = if self.unaccounted.is_empty(){format!("sequence-{ordinal:016}")}else{format!("recovery-{ordinal:016}")};
        let dir = roots::mkdir(self.hold.directory(), &name)?;
        let mut p = PendingSequence { dir, name, intent, originals: BTreeMap::new(), entry: None, entry_binding: None };
        self.put(&mut p, "intent.json", &raw)?;
        self.put(&mut p, "frame.json", full_frame)?; Ok(p)
    }
    pub(crate) fn put(&self, pending: &mut PendingSequence, name: &str, raw: &[u8]) -> Result<Binding> {
        self.guard()?;
        require(self.pending && pending.intent.previous == self.head && pending.entry.is_none()
            && pending.originals.len() < quota::SEQUENCE_FILES as usize - 2
            && !pending.originals.contains_key(name), "PENDING_ORIGINAL_STATE")?;
        roots::name(name)?;
        let binding = bound(&self.scope.receipt_root_id, &format!("{}/{name}", pending.name), raw)?;
        self.limits.record(raw)?;
        put_file(&pending.dir, name, &self.scope.receipt_root, raw, self.limits.max_record_bytes)?;
        pending.originals.insert(name.into(), binding.clone()); Ok(binding)
    }
    pub(crate) fn member_receipt(&self, p: &mut PendingSequence, transition: &members::Transition,
                                proposed: &members::Snapshot) -> Result<members::DurableReceipt> {
        require(transition.operation_id == p.intent.operation_id && transition.fingerprint == p.intent.original_fingerprint
            && transition.sequence == p.intent.sequence && transition.wire_digest == p.intent.wire_sha256
            && transition.state_sha256 == roots::hash(&encode(proposed)?), "MEMBER_TRANSITION_SCOPE")?;
        self.put(p, "transition.json", &encode(transition)?)?;
        self.put(p, "proposed.json", &encode(proposed)?)?;
        let raw = encode(&json!({"schema_version":"lab-member-durable-receipt/v1", "transition":transition, "outcome":"durable"}))?;
        require(raw.len() <= quota::MAX_PACKET as usize, "MEMBER_RECEIPT_PROTOCOL_BOUND")?;
        let binding = self.put(p, "member-receipt.json", &raw)?;
        members::DurableReceipt::from_fixed_control(transition.clone(), raw, binding, self.scope.domain)
    }
    pub(crate) fn finish(&self, p: &mut PendingSequence, snapshot: Option<&members::Snapshot>,
                        response: &[u8], phase: &str, status: &str) -> Result<()> {
        require(matches!(phase,"absent"|"reserved"|"staging"|"sealed"|"generation-published"|"pointer-committed"|"terminal"|"quarantined"|"UNKNOWN")
            && matches!(status,"PASS"|"FAIL"|"UNKNOWN"|"REFUSED"), "ENTRY_PHASE_STATUS")?;
        self.limits.response(response)?;
        if let Some(s) = snapshot { self.put(p, "acknowledged.json", &encode(s)?)?; }
        self.put(p, "response.json", response)?;
        let entry = SequenceEntry { schema_version: "lab-broker-sequence-entry/v1".into(),
            intent: p.intent.clone(), originals: p.originals.clone(), phase: phase.into(), status: status.into() };
        let raw = encode(&entry)?; self.limits.record(&raw)?;
        let binding = bound(&self.scope.receipt_root_id, &format!("{}/entry.json", p.name), &raw)?;
        put_file(&p.dir, "entry.json", &self.scope.receipt_root, &raw, self.limits.max_record_bytes)?;
        p.entry = Some(entry); p.entry_binding = Some(binding); Ok(())
    }
    pub(crate) fn confirmation_request(&self, p: &PendingSequence, challenge: String,
                                      not_before: u64, expires_at: u64) -> Result<PrefixRequest> {
        self.guard()?;
        let entry = p.entry_binding.as_ref().ok_or(Error("ENTRY_NOT_DURABLE"))?;
        require(self.pending && p.intent.previous == self.head, "PENDING_PREFIX")?;
        let request = PrefixRequest { current_admission:p.intent.current_admission.clone(),schema_version: "lab-broker-prefix-cas-request/v1".into(), scope: self.scope.clone(),
            prior: self.head.clone(), next: PrefixHead { ordinal: p.intent.ordinal, entry_sha256: entry.sha256.clone() },
            entry_binding:entry.clone(),sequence: p.intent.sequence, wire_sha256: p.intent.wire_sha256.clone(),
            ledger_confirmation: p.intent.ledger_confirmation.clone(), challenge, not_before, expires_at };
        request.validate(now_seconds()?)?; Ok(request)
    }
    pub(crate) fn confirm(&mut self, p: PendingSequence, proof: VerifiedPrefix, response_signer: &SelectedSigner) -> Result<Vec<u8>> {
        self.guard()?;
        let binding = p.entry_binding.as_ref().ok_or(Error("ENTRY_NOT_DURABLE"))?;
        let request = &proof.value.request;
        require(self.pending && request.scope == self.scope && request.prior == self.head
            && request.next.ordinal == p.intent.ordinal && request.next.entry_sha256 == binding.sha256&&request.entry_binding==*binding
            && request.sequence == p.intent.sequence && request.wire_sha256 == p.intent.wire_sha256
            && request.ledger_confirmation == p.intent.ledger_confirmation&&request.current_admission==p.intent.current_admission, "CONFIRM_PENDING_SCOPE")?;
        interval(request.not_before, request.expires_at, now_seconds()?)?;
        put_file(&p.dir, "confirmation.json", &self.scope.receipt_root, &proof.original, self.limits.max_record_bytes)?;
        let retained = self.load_entry(&p.name, &self.head)?;
        require(response_signer.domain()==self.scope.domain && response_signer.selection.purpose=="broker-response","RESPONSE_SIGNER_DOMAIN")?;
        validate_response(&retained,response_signer)?;
        self.head = request.next.clone(); self.entries.push(retained);
        self.pending = false;self.unaccounted.clear();
        Ok(self.entries.last().unwrap().response.clone())
    }
    fn load_entry(&self, name: &str, previous: &PrefixHead) -> Result<RetainedSequence> {
        let dir=roots::open_child(self.hold.directory(),name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
        load_sequence(&dir,name,&self.scope,&self.limits,previous,true)
    }

}

#[derive(Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct CapturedMemberRecord{schema_version:String,operation:Operation,root_id:String,member:String,identity_binding:Value}
fn load_sequence(dir:&File,name:&str,scope:&PrefixScope,limits:&quota::Limits,previous:&PrefixHead,confirmed:bool)->Result<RetainedSequence>{
        roots::owned_dir(&dir, scope.receipt_root.uid, scope.receipt_root.mount_id)?;
        let raw = read_file(&dir, "entry.json", &scope.receipt_root, limits.max_record_bytes)?;
        let entry: SequenceEntry = decode(&raw, limits.max_record_bytes)?;
        let entry_binding = bound(&scope.receipt_root_id, &format!("{name}/entry.json"), &raw)?;
        require(entry.schema_version == "lab-broker-sequence-entry/v1"
            && entry.intent.schema_version == "lab-broker-sequence-intent/v1"
            && entry.intent.scope_sha256 == scope.digest()? && entry.intent.previous == *previous
            && entry.intent.ordinal == previous.ordinal + 1
            && entry.intent.operation_id == scope.operation.operation_id
            && entry.intent.original_fingerprint == scope.operation.fingerprint, "ENTRY_CHAIN_SCOPE")?;
        check_prefix_admission(scope,&entry.intent.ledger_confirmation,entry.intent.current_admission.as_ref(),None)?;
        let mut originals = BTreeMap::new();
        for (leaf, binding) in &entry.originals {
            roots::name(leaf)?;
            require(binding.root_id == scope.receipt_root_id && binding.relative_path == format!("{name}/{leaf}"), "ORIGINAL_LOCATOR")?;
            let bytes = read_file(&dir, leaf, &scope.receipt_root, limits.max_record_bytes)?;
            verify_bytes(&bytes, binding)?; originals.insert(leaf.as_str(), bytes);
        }
        require(originals.get("intent.json") == Some(&encode(&entry.intent)?), "INTENT_ORIGINAL")?;
        let frame_raw = originals.get("frame.json").ok_or(Error("FRAME_ORIGINAL_MISSING"))?;
        let frame = wire::Frame::decode(frame_raw).map_err(|_| Error("FRAME_ORIGINAL"))?;
        require(frame.wire_digest() == entry.intent.wire_sha256 && frame.request()["sequence"] == entry.intent.sequence
            && frame.request()["verb"] == entry.intent.verb && frame.request()["operation_id"] == entry.intent.operation_id,
            "FRAME_ENTRY_JOIN")?;
        if entry.intent.verb=="write_member" {
            let capture_raw=originals.get("captured-member.json").ok_or(Error("CAPTURED_MEMBER_ORIGINAL_MISSING"))?;
            let capture:CapturedMemberRecord=decode(capture_raw,quota::MAX_PACKET)?;
            let selected:Binding=decode(originals.get("captured-selection.json").ok_or(Error("CAPTURED_MEMBER_SELECTION_MISSING"))?,quota::MAX_PACKET)?;
            verify_bytes(capture_raw,&selected)?;
            let frame_value:Value=decode(frame_raw,quota::MAX_PACKET)?;
            require(capture.schema_version=="lab-broker-captured-member-identity/v1"&&capture.operation==scope.operation
                &&capture.root_id==frame.request()["payload"]["root_id"]&&capture.member==frame.request()["payload"]["member"]
                &&capture.identity_binding==authority::member_identity_binding(&frame_value["permit"]["payload"]["grant"]).map_err(|_|Error("CAPTURED_MEMBER_DIGEST"))?,"CAPTURED_MEMBER_FRAME_JOIN")?;
        }
        let response = originals.get("response.json").ok_or(Error("RESPONSE_ORIGINAL_MISSING"))?.clone();
        limits.response(&response)?;
        let snapshot = if let Some(proposed) = originals.get("proposed.json") {
            let proposed: members::Snapshot = decode(proposed, limits.max_record_bytes)?;
            let transition: members::Transition = decode(originals.get("transition.json").ok_or(Error("TRANSITION_MISSING"))?, limits.max_record_bytes)?;
            let receipt_binding = entry.originals.get("member-receipt.json").ok_or(Error("MEMBER_RECEIPT_MISSING"))?;
            let receipt = originals.get("member-receipt.json").ok_or(Error("MEMBER_RECEIPT_MISSING"))?;
            members::DurableReceipt::from_fixed_control(transition.clone(), receipt.clone(), receipt_binding.clone(), scope.domain)?;
            require(transition.state_sha256 == roots::hash(&encode(&proposed)?)
                && transition.wire_digest == entry.intent.wire_sha256 && transition.sequence == entry.intent.sequence
                && transition.operation_id == entry.intent.operation_id && transition.fingerprint == entry.intent.original_fingerprint,
                "TRANSITION_ENTRY_JOIN")?;
            let expected = derive_acknowledged(proposed, &transition, receipt_binding)?;
            let actual: members::Snapshot = decode(originals.get("acknowledged.json").ok_or(Error("ACK_SNAPSHOT_MISSING"))?, limits.max_record_bytes)?;
            require(encode(&actual)? == encode(&expected)?, "ACK_DERIVATION")?; Some(actual)
        } else {
            require(!originals.contains_key("transition.json") && !originals.contains_key("member-receipt.json")
                && !originals.contains_key("acknowledged.json"), "PARTIAL_MEMBER_EVIDENCE")?; None
        };
        let mut expected: BTreeSet<String> = entry.originals.keys().cloned().collect();
        expected.insert("entry.json".into()); if confirmed { expected.insert("confirmation.json".into()); }
        require(roots::names(&dir, quota::SEQUENCE_FILES as usize + 1)?.into_iter().collect::<BTreeSet<_>>() == expected,
            "UNEXPLAINED_SEQUENCE_ORIGINALS")?;
        Ok(RetainedSequence { entry, entry_binding, response, snapshot })
}

/// This is the precise derivation Stage::acknowledge performs; restart compares
/// the saved snapshot to this result before handing it to Stage::restore.
pub fn derive_acknowledged(mut proposed: members::Snapshot, t: &members::Transition,
                           receipt: &Binding) -> Result<members::Snapshot> {
    require(receipt.valid() && proposed.operation_id == t.operation_id && proposed.fingerprint == t.fingerprint
        && proposed.domain == t.domain && proposed.stage_identity == t.stage_identity, "ACK_DERIVE_SCOPE")?;
    let mut matching = 0;
    for member in proposed.members.values_mut() {
        for range in &mut member.ranges {
            if range.sequence == t.sequence && range.wire_digest == t.wire_digest {
                require(range.receipt_binding.is_none(), "ACK_RANGE_ALREADY_RECEIPTED")?;
                range.receipt_binding = Some(receipt.clone()); matching += 1;
            }
        }
    }
    require(if t.verb == "write_member" { matching == 1 } else { matching == 0 }, "ACK_RANGE_CARDINALITY")?;
    proposed.last_receipt_binding = Some(receipt.clone());
    if t.verb == "create_stage" { proposed.stage_binding = Some(receipt.clone()); }
    proposed.next_sequence = t.sequence.checked_add(1).ok_or(Error("SEQUENCE_OVERFLOW"))?;
    Ok(proposed)
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PrefixInspectionRequest {
    pub schema_version: String, pub history_key: String, pub recipient: Caller,
    pub channel_binding: Binding, pub challenge: String,
    pub current_ledger_confirmation: HostConfirmation,
    pub current_execution_scope: roots::ExecutionScope,
    pub not_before: u64, pub expires_at: u64,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PrefixInspection {
    pub schema_version: String, pub request: PrefixInspectionRequest,
    pub original_scope_binding: Binding, pub head: PrefixHead,
    pub signer_enrollment_binding: Binding,pub original_confirmation_binding:Option<Binding>,
}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct PrefixOriginalRequest{pub schema_version:String,pub query:PrefixInspectionRequest,pub original_binding:Binding}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct PrefixAdmission { pub inspection:PrefixInspection,pub original:Vec<u8> }
fn check_prefix_admission(scope:&PrefixScope,ledger:&HostConfirmation,admission:Option<&PrefixAdmission>,now:Option<u64>)->Result<()> {
    if let Some(a)=admission{
        let q=&a.inspection.request;scope.check_current_lineage(ledger)?;
        require(a.original.len() as u64<=quota::MAX_PACKET&&q.history_key==scope.history_key()?
            &&a.inspection.original_scope_binding.valid()&&verify_bytes(&encode(scope)?,&a.inspection.original_scope_binding).is_ok()
            &&q.current_ledger_confirmation.authority_domain==ledger.authority_domain&&q.current_ledger_confirmation.root==ledger.root
            &&q.current_ledger_confirmation.header_sha256==ledger.header_sha256&&q.current_ledger_confirmation.writer==ledger.writer
            &&q.current_ledger_confirmation.head.sequence<=ledger.head.sequence
            &&q.current_execution_scope.valid()&&q.current_execution_scope.store_id==scope.operation.store_id
            &&q.recipient.valid()&&q.channel_binding.valid(),"PREFIX_CURRENT_ADMISSION_SCOPE")?;
        if let Some(now)=now{interval(q.not_before,q.expires_at,now)?;}else{interval(q.not_before,q.expires_at,q.not_before)?;}
        Ok(())
    }else{scope.check_ledger(ledger)}
}
fn verify_prefix_admission(scope:&PrefixScope,admission:Option<&PrefixAdmission>,signer:&SelectedSigner)->Result<()> {
    if let Some(a)=admission{
        let parsed:PrefixInspection=signer.verify(&a.original)?;
        require(parsed==a.inspection&&parsed.schema_version=="lab-broker-prefix-inspection/v1"
            &&parsed.signer_enrollment_binding==*signer.binding()&&parsed.request.history_key==scope.history_key()?&&parsed.head.valid(),"PREFIX_CURRENT_ADMISSION_SIGNATURE")?;
    }Ok(())
}
pub struct CurrentPrefix { value: PrefixInspection, original: Vec<u8> }
impl CurrentPrefix {
    pub fn verify(raw: &[u8], signer: &SelectedSigner, expected: &PrefixInspectionRequest,
                  original_scope: &PrefixScope, scope_binding: &Binding, now: u64) -> Result<Self> {
        original_scope.check_current_lineage(&expected.current_ledger_confirmation)?;
        verify_bytes(&encode(original_scope)?, scope_binding)?;
        require(expected.schema_version == "lab-broker-prefix-inspection-request/v1"
            && expected.history_key == original_scope.history_key()? && expected.recipient.valid()
            && expected.current_execution_scope.valid()
            && expected.current_execution_scope.store_id == original_scope.operation.store_id
            && expected.channel_binding.valid() && roots::digest(&expected.challenge), "PREFIX_INSPECTION_REQUEST")?;
        interval(expected.not_before, expected.expires_at, now)?;
        let value: PrefixInspection = signer.verify(raw)?;
        require(value.schema_version == "lab-broker-prefix-inspection/v1" && value.request == *expected
            && value.original_scope_binding == *scope_binding && value.head.valid()
            && value.signer_enrollment_binding == *signer.binding() && signer.domain() == original_scope.domain
            && if value.head.ordinal==0{value.original_confirmation_binding.is_none()}else{value.original_confirmation_binding.as_ref().is_some_and(|b|b.valid()&&b.size_bytes<=quota::MAX_PACKET)},
            "PREFIX_INSPECTION_SCOPE")?;
        Ok(Self { value, original: raw.into() })
    }
    pub fn head(&self) -> &PrefixHead { &self.value.head }
    pub fn original(&self) -> &[u8] { &self.original }
    pub(crate) fn original_request(&self)->Result<PrefixOriginalRequest>{
        interval(self.value.request.not_before,self.value.request.expires_at,now_seconds()?)?;
        Ok(PrefixOriginalRequest{schema_version:"lab-broker-prefix-original-request/v1".into(),query:self.value.request.clone(),original_binding:self.value.original_confirmation_binding.clone().ok_or(Error("GENESIS_HAS_NO_CONFIRMATION"))?})
    }
    pub(crate) fn verify_original(&self,raw:&[u8],signer:&SelectedSigner,scope:&PrefixScope)->Result<VerifiedPrefix>{
        let expected=self.original_request()?;verify_bytes(raw,&expected.original_binding)?;
        let value:PrefixConfirmation=signer.verify(raw)?;
        require(value.schema_version=="lab-broker-prefix-confirmation/v1"&&value.signer_enrollment_binding==*signer.binding()
            &&value.result=="confirmed"&&value.request.scope==*scope&&value.request.next==self.value.head
            &&scope.history_key()?==self.value.request.history_key,"CURRENT_PREFIX_ORIGINAL_JOIN")?;
        value.request.validate(value.request.not_before)?;
        Ok(VerifiedPrefix{value,original:raw.into()})
    }
    pub(crate) fn check_admission(&self,signer:&SelectedSigner,scope:&Binding,facts:&HostFacts,recipient:&Caller,channel:&Binding)->Result<()> {
        require(self.value.signer_enrollment_binding==*signer.binding()&&self.value.original_scope_binding==*scope
            &&self.value.request.recipient==*recipient&&self.value.request.channel_binding==*channel
            &&self.value.request.current_execution_scope==facts.scope&&self.value.request.current_ledger_confirmation==facts.ledger_confirmation,"PREFIX_CURRENT_ADMISSION")?;
        interval(self.value.request.not_before,self.value.request.expires_at,now_seconds()?)
    }
}

/// Read-only restart evidence. No method on this type offers Stage or a writer
/// capability. Every unfinished original operation requires explicit recovery,
/// even if its local tree exactly matches the confirmed prefix.
pub struct RestartedPrefix<'a> { journal: ReceiptJournal<'a>, current: CurrentPrefix, ranges_verified: std::cell::Cell<bool> }
impl<'a> RestartedPrefix<'a> {
    /// Transfers only the confirmed receipt writer, never a producer Stage.
    /// The fixed Session caller keeps its restart-only dispatch fence and may
    /// append solely independently authorized recovery/terminal accounting.
    pub(crate) fn into_recovery_journal(mut self)->ReceiptJournal<'a>{self.journal.pending=false;self.journal}
    pub fn inspect(hold: &'a Exclusive<'a>, scope: PrefixScope, limits: quota::Limits,
                   current: CurrentPrefix, witness: &SelectedSigner, receipt_signer: &SelectedSigner) -> Result<Self> {
        Self::inspect_mode(hold,scope,limits,current,witness,receipt_signer,false)
    }
    pub(crate) fn inspect_recovery(hold:&'a Exclusive<'a>,scope:PrefixScope,limits:quota::Limits,current:CurrentPrefix,witness:&SelectedSigner,receipt_signer:&SelectedSigner)->Result<Self>{
        Self::inspect_mode(hold,scope,limits,current,witness,receipt_signer,true)
    }
    fn inspect_mode(hold:&'a Exclusive<'a>,scope:PrefixScope,limits:quota::Limits,current:CurrentPrefix,witness:&SelectedSigner,receipt_signer:&SelectedSigner,allow_tail:bool)->Result<Self>{
        hold.validate()?; scope.validate()?; limits.validate()?;
        require(scope.receipt_root == *hold.root().identity() && scope.receipt_root_id == hold.root().selection().root_id
            && scope.domain == hold.root().selection().domain
            && current.value.request.current_execution_scope == hold.root().selection().execution_scope
            && current.value.request.history_key == scope.history_key()?
            && current.head().ordinal <= limits.max_sequences, "RESTART_ROOT_SCOPE")?;
        interval(current.value.request.not_before, current.value.request.expires_at, now_seconds()?)?;
        let (entries,unaccounted)=selected_chain(hold.directory(),&scope,&limits,current.head(),witness,receipt_signer,allow_tail,None)?;
        let admission=PrefixAdmission{inspection:current.value.clone(),original:current.original.clone()};
        verify_prefix_admission(&scope,Some(&admission),witness)?;
        let journal = ReceiptJournal { hold, head:current.head().clone(), scope, limits, entries, pending:true,unaccounted,current_admission:Some(admission) };
        Ok(Self { journal, current, ranges_verified:std::cell::Cell::new(false) })
    }
    /// Fixed current custody may restore only an already independently
    /// confirmed original proof. Every other missing/tail state remains fenced.
    /// This never reconstructs a Stage, signs a response, CASes or adds Outcome.
    pub(crate) fn retain_missing_confirmation(hold:&Exclusive<'_>,scope:&PrefixScope,limits:&quota::Limits,
        current:&CurrentPrefix,proof:&VerifiedPrefix,witness:&SelectedSigner,response:&SelectedSigner)->Result<()> {
        hold.validate()?;scope.validate()?;limits.validate()?;
        require(current.head()==proof.head()&&proof.value.request.scope==*scope&&current.head().ordinal>0
            &&scope.receipt_root==*hold.root().identity()&&scope.receipt_root_id==hold.root().selection().root_id,"SETTLEMENT_SCOPE")?;
        current.verify_original(&proof.original,witness,scope)?;
        let (entries,_)=selected_chain(hold.directory(),scope,limits,current.head(),witness,response,true,Some(&proof.value.request))?;
        let entry=entries.last().ok_or(Error("SETTLEMENT_EMPTY"))?;
        require(entry.entry_binding==proof.value.request.entry_binding,"SETTLEMENT_EXACT_ENTRY")?;
        let name=entry.entry_binding.relative_path.strip_suffix("/entry.json").ok_or(Error("SETTLEMENT_ENTRY_PATH"))?;
        let dir=roots::open_child(hold.directory(),name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
        let names=roots::names(&dir,quota::SEQUENCE_FILES as usize+1)?;
        if !names.contains(&"confirmation.json".into()){
            limits.record(&proof.original)?;current.original_request()?;hold.validate()?;
            put_file(&dir,"confirmation.json",&scope.receipt_root,&proof.original,limits.max_record_bytes)?;
        }
        require(read_file(&dir,"confirmation.json",&scope.receipt_root,quota::MAX_PACKET)?==proof.original,"SETTLEMENT_ORIGINAL_BYTES")?;
        hold.validate()
    }
    pub fn requires_reconciliation(&self) -> bool { true }
    pub fn last_snapshot(&self) -> Option<&members::Snapshot> {
        self.journal.entries.iter().rev().find_map(|e| e.snapshot.as_ref())
    }
    pub fn validate_ranges(&self, stage_root: &'a Exclusive<'a>) -> Result<()> {
        if let Some(s) = self.last_snapshot() {
            readonly_ranges(stage_root,s,&s.stage_name,None)?;
        }
        self.ranges_verified.set(true); Ok(())
    }
    pub(crate) fn validate_published_ranges(&self,root:&Exclusive<'_>,manifest_raw:&[u8],manifest_binding:&Binding,history:&crate::commit::HistoryProof)->Result<()> {
        let snapshot=self.last_snapshot().ok_or(Error("ORIGINAL_SNAPSHOT_MISSING"))?;
        let manifest:members::Manifest=decode(manifest_raw,quota::MAX_PACKET)?;
        verify_bytes(manifest_raw,manifest_binding)?;
        require(snapshot.sealed_manifest_binding.as_ref()==Some(manifest_binding)
            &&history.pointer().is_some_and(|p|p.operation_id==snapshot.operation_id)
            &&history.generation()==manifest.generation_name,"PUBLISHED_HISTORY_SCOPE")?;
        readonly_ranges(root,snapshot,&manifest.generation_name,Some(&manifest))?;
        self.ranges_verified.set(true);Ok(())
    }
    pub fn receipt(&self, sequence: u64, verified: &authority::VerifiedDispatch) -> Result<Vec<u8>> {
        self.journal.guard()?;require(self.ranges_verified.get(),"ORIGINAL_RANGES_NOT_VERIFIED")?;
        interval(self.current.value.request.not_before, self.current.value.request.expires_at, now_seconds()?)?;
        let e = self.journal.entries.iter().find(|e| e.entry.intent.sequence == sequence).ok_or(Error("RECEIPT_NOT_CONFIRMED"))?;
        let binding = e.entry.originals.get("response.json").ok_or(Error("RESPONSE_ORIGINAL_MISSING"))?;
        match verified.decision() {
            authority::Decision::Disclosure { subject_binding, max_output_bytes } => {
                require(*subject_binding == serde_json::to_value(binding).map_err(|_| Error("ENCODE"))?
                    && e.response.len() <= *max_output_bytes
                    && verified.operation_fingerprint() == self.journal.scope.operation.fingerprint
                    && (verified.trust_domain() == authority::TrustDomain::Fixture) == (self.journal.scope.domain == Domain::Fixture),
                    "RECEIPT_DISCLOSURE_SCOPE")?;
                Ok(e.response.clone())
            }
            _ => Err(Error("FRESH_DISCLOSURE_REQUIRED")),
        }
    }
}

/// Hash original acknowledged ranges without constructing Stage or any writer
/// capability. Publication changes the location, not the original inode/range
/// history; the caller separately supplies verified immutable history above.
pub(crate) fn readonly_ranges(root:&Exclusive<'_>,snapshot:&members::Snapshot,location:&str,published:Option<&members::Manifest>)->Result<()> {
    use std::os::unix::fs::FileExt;
    root.validate()?;require(snapshot.root==*root.root().identity()&&snapshot.root_id==root.root().selection().root_id
        &&snapshot.domain==root.root().selection().domain&&snapshot.members.len()<=1024&&snapshot.directories.len()<=4096,"READ_RANGE_ROOT")?;
    if let Some(m)=published{
        require(m.schema_version=="lab-member-generation/v1"&&m.root_id==snapshot.root_id&&m.operation_id==snapshot.operation_id
            &&m.fingerprint==snapshot.fingerprint&&m.stage_identity==snapshot.stage_identity&&m.generation_name==location
            &&m.members==snapshot.members.iter().map(|(p,x)|(p.clone(),members::MemberContent{sha256:x.full_sha256.clone(),size_bytes:x.full_length})).collect(),"READ_PUBLICATION_MANIFEST")?;
    }else{require(location==snapshot.stage_name,"READ_ORIGINAL_LOCATION")?;}
    let dir=roots::open_child(root.directory(),location,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
    require(roots::owned_dir(&dir,snapshot.root.uid,snapshot.root.mount_id)?==snapshot.stage_identity,"READ_STAGE_IDENTITY")?;
    let open_dir=|path:&str|->Result<File>{let mut f=dir.try_clone()?;let mut joined=String::new();
        if !path.is_empty(){for part in roots::parts(path)?{if !joined.is_empty(){joined.push('/');}joined.push_str(part);
            f=roots::open_child(&f,part,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
            require(snapshot.directories.get(&joined)==Some(&roots::owned_dir(&f,snapshot.root.uid,snapshot.root.mount_id)?),"READ_DIRECTORY_IDENTITY")?;}}
        Ok(f)};
    for path in std::iter::once("").chain(snapshot.directories.keys().map(String::as_str)){
        let prefix=if path.is_empty(){String::new()}else{format!("{path}/")};let expected:BTreeSet<_>=snapshot.members.keys().chain(snapshot.directories.keys())
            .filter_map(|p|p.strip_prefix(&prefix)).filter(|p|!p.contains('/')).map(str::to_string).collect();
        require(roots::names(&open_dir(path)?,5121)?.into_iter().collect::<BTreeSet<_>>()==expected,"READ_RANGE_INVENTORY")?;
    }
    let mut seen=BTreeSet::new();let mut total=0u64;
    for (path,member) in &snapshot.members {
        require(member.full_length<=snapshot.max_bytes&&member.full_length<=1_073_741_824&&!member.ranges.is_empty()&&member.ranges.len()<=4096,"READ_MEMBER_BOUND")?;
        let parts=roots::parts(path)?;let parent=open_dir(&parts[..parts.len()-1].join("/"))?;let file=roots::open_child(&parent,parts.last().unwrap(),libc::O_RDONLY,0,true)?;
        require(roots::owned_file(&file,snapshot.root.uid,snapshot.root.mount_id)?==member.identity,"READ_MEMBER_IDENTITY")?;
        let before=file.metadata()?;let mut end=0u64;
        use sha2::{Digest,Sha256};let mut full=Sha256::new();
        for range in &member.ranges {require(range.offset==end&&range.length<=32768&&(range.length>0||member.full_length==0)
            &&range.sequence<snapshot.next_sequence&&seen.insert(range.sequence)&&range.receipt_binding.as_ref().is_some_and(Binding::valid),"READ_RANGE_HISTORY")?;
            let mut raw=vec![0;range.length as usize];file.read_exact_at(&mut raw,range.offset)?;require(roots::hash(&raw)==range.sha256,"READ_RANGE_BYTES")?;
            full.update(&raw);end=end.checked_add(range.length).ok_or(Error("READ_RANGE_OVERFLOW"))?;
        }
        require(end==before.len()&&end<=member.full_length&&(published.is_none()||end==member.full_length),"READ_UNEXPLAINED_TAIL")?;
        if published.is_some(){require(format!("{:x}",full.finalize())==member.full_sha256,"READ_FULL_MEMBER_BYTES")?;}
        let after=file.metadata()?;let named=roots::open_child(&parent,parts.last().unwrap(),libc::O_RDONLY,0,true)?;
        require(before.len()==after.len()&&before.mtime()==after.mtime()&&before.mtime_nsec()==after.mtime_nsec()
            &&before.ctime()==after.ctime()&&before.ctime_nsec()==after.ctime_nsec()&&roots::owned_file(&named,snapshot.root.uid,snapshot.root.mount_id)?==member.identity,"READ_MEMBER_CHANGED")?;
        total=total.checked_add(end).ok_or(Error("READ_RANGE_OVERFLOW"))?;
    }require(total<=snapshot.max_bytes,"READ_RANGE_TOTAL")?;root.validate()
}

#[derive(Serialize, Deserialize)] #[serde(deny_unknown_fields)]
struct ResponsePayload { schema_version: String, request_digest: String, operation_id: String,
    sequence: u64, durable_phase: String, status: String, error: Option<String>, result_binding: Option<Binding> }
fn validate_response(e: &RetainedSequence, signer: &SelectedSigner) -> Result<()> {
    let p: ResponsePayload = signer.verify(&e.response)?;
    require(p.schema_version == "lab-completion-broker-response/v1" && p.request_digest == e.entry.intent.wire_sha256
        && p.operation_id == e.entry.intent.operation_id && p.sequence == e.entry.intent.sequence
        && p.durable_phase == e.entry.phase && p.status == e.entry.status
        && matches!(p.status.as_str(), "PASS" | "FAIL" | "UNKNOWN" | "REFUSED")
        && p.error.as_ref().is_none_or(|s| !s.is_empty() && s.len() <= 64 && s.bytes().all(|b| b.is_ascii_uppercase() || b == b'_' || b.is_ascii_digit()))
        && p.result_binding.as_ref().is_none_or(Binding::valid), "RESPONSE_ENTRY_JOIN")?;
    if let Some(member) = e.entry.originals.get("member-receipt.json") {
        require(p.result_binding.as_ref() == Some(member), "RESPONSE_MEMBER_RECEIPT_JOIN")?;
    }
    Ok(())
}

/// Fixed host-side witness writer. Its selected high-water is an independent
/// nonrollback custody input; open never discovers a new head from filenames.
/// The witness root must be physically distinct from broker receipt/control
/// custody and installed under the separately enrolled witness identity.
pub struct PrefixWitness<'a> {
    hold: &'a Exclusive<'a>, scope: PrefixScope, scope_binding: Binding,
    head: PrefixHead, signer: &'a SelectedSigner, key: SigningKey,
    poisoned: bool, latest_request: Option<PrefixRequest>, latest_response: Option<Vec<u8>>,
}
impl<'a> PrefixWitness<'a> {
    pub(crate) fn open(hold: &'a Exclusive<'a>, scope: PrefixScope, scope_binding: Binding,
                      selected_head: PrefixHead, signer: &'a SelectedSigner, key: SigningKey) -> Result<Self> {
        hold.validate()?; scope.validate()?; verify_bytes(&encode(&scope)?, &scope_binding)?;
        require(hold.root().selection().domain == scope.domain && signer.domain() == scope.domain
            && signer.selection.purpose == "receipt-prefix" && signer.key == key.verifying_key()
            && selected_head.valid() && *hold.root().identity() != scope.receipt_root
            && !(hold.root().identity().device == scope.control_root.device && hold.root().identity().inode == scope.control_root.inode),
            "WITNESS_CUSTODY_DOMAIN")?;
        let mut w = Self { hold, head: PrefixHead::genesis(&scope)?, scope, scope_binding, signer, key,
            poisoned: false, latest_request: None, latest_response: None };
        let names = roots::names(hold.directory(), 4097)?;
        require(names.len() as u64 == selected_head.ordinal, "WITNESS_UNSELECTED_TAIL")?;
        for (i, name) in names.iter().enumerate() {
            require(*name == format!("prefix-{:016}.json", i + 1), "WITNESS_RECORD_ORDER")?;
            let raw = read_file(hold.directory(), name, hold.root().identity(), quota::MAX_PACKET)?;
            let value: PrefixConfirmation = signer.verify(&raw)?;
            let r = &value.request; r.validate(r.not_before)?;verify_prefix_admission(&w.scope,r.current_admission.as_ref(),signer)?;
            require(value.schema_version == "lab-broker-prefix-confirmation/v1" && value.result == "confirmed"
                && value.signer_enrollment_binding == *signer.binding()
                && r.scope == w.scope && r.scope.history_key()? == w.scope.history_key()?
                && r.prior == w.head && r.next.ordinal == i as u64 + 1, "WITNESS_RECORD_CHAIN")?;
            w.head = r.next.clone(); w.latest_request = Some(r.clone()); w.latest_response = Some(raw);
        }
        require(w.head == selected_head, "WITNESS_SELECTED_HIGH_WATER")?; Ok(w)
    }
    #[cfg(test)] pub(crate) fn fixture_delay(&self,point:u8,milliseconds:u64)->Result<()>{
        require(self.scope.domain==Domain::Fixture&&(1..=2).contains(&point)&&milliseconds<=5000,"FIXTURE_DELAY_BOUND")?;
        PREFIX_FIXTURE_DELAY.with(|value|value.set((point,milliseconds)));Ok(())
    }
    pub fn head(&self) -> &PrefixHead { &self.head }
    #[cfg(test)] pub(crate) fn compare_and_swap(&mut self, request: &PrefixRequest, peer: &Caller) -> Result<Vec<u8>> {
        require(self.scope.domain==Domain::Fixture,"FIXTURE_WITNESS_ONLY")?;self.cas(request,peer)
    }
    fn cas(&mut self,request:&PrefixRequest,peer:&Caller)->Result<Vec<u8>>{self.cas_until(request,peer,None)}
    fn cas_until(&mut self, request: &PrefixRequest, peer: &Caller, effective:Option<(u64,u64)>) -> Result<Vec<u8>> {
        let current=||->Result<()>{let now=now_seconds()?;request.validate(now)?;if let Some((start,end))=effective{interval(start,end,now)?;}Ok(())};
        self.hold.validate()?;current()?;
        require(!self.poisoned, "WITNESS_UNCERTAIN")?;
        request.validate(now_seconds()?)?;
        verify_prefix_admission(&self.scope,request.current_admission.as_ref(),self.signer)?;
        let recipient=request.current_admission.as_ref().map(|a|&a.inspection.request.recipient).unwrap_or(&self.scope.recipient);
        require(request.scope == self.scope && request.scope.history_key()? == self.scope.history_key()?
            && peer == recipient, "WITNESS_CALLER_SCOPE")?;
        if let Some(a)=&request.current_admission{require(a.inspection.head.ordinal<=request.prior.ordinal,"ADMISSION_PREFIX_LINEAGE")?;}
        if self.latest_request.as_ref() == Some(request) {
            return self.latest_response.clone().ok_or(Error("WITNESS_MISSING_ORIGINAL"));
        }
        require(request.prior == self.head && request.next.ordinal <= 4096, "WITNESS_CAS_PREIMAGE")?;
        let proof = PrefixConfirmation { schema_version: "lab-broker-prefix-confirmation/v1".into(),
            request: request.clone(), signer_enrollment_binding: self.signer.binding().clone(), result: "confirmed".into() };
        let raw = self.signer.sign(&self.key, &proof)?;
        current()?;
        self.poisoned = true;
        put_file(self.hold.directory(), &format!("prefix-{:016}.json", request.next.ordinal), self.hold.root().identity(), &raw, quota::MAX_PACKET)?;
        self.head = request.next.clone(); self.latest_request = Some(request.clone()); self.latest_response = Some(raw.clone());
        self.poisoned = false;
        #[cfg(test)] prefix_fixture_delay(1);
        current()?; Ok(raw)
    }
    /// Fixed server path verifies complete original response/transition bytes
    /// while borrowing no broker lock. Local entry fsync is not the external
    /// high-water: only this separately held witness may confirm the prefix.
    pub(crate) fn confirm_originals(&mut self,request:&PrefixRequest,peer:&Caller,receipt:&OriginalDirectory,
        control:&OriginalDirectory,current:&HostConfirmation,limits:&quota::Limits,response_signer:&SelectedSigner)->Result<Vec<u8>> {
        self.verify_originals(request,receipt,control,current,limits,response_signer)?;
        request.validate(now_seconds()?)?;self.cas(request,peer)
    }
    fn verify_originals(&self,request:&PrefixRequest,receipt:&OriginalDirectory,control:&OriginalDirectory,
        current:&HostConfirmation,limits:&quota::Limits,response_signer:&SelectedSigner)->Result<()> {
        receipt.guard()?;limits.validate()?;self.signer.distinct(response_signer)?;
        require(receipt.selected.root_id==self.scope.receipt_root_id&&receipt.selected.ancestors.last()==Some(&self.scope.receipt_root)
            &&receipt.selected.domain==self.scope.domain,"PREFIX_ORIGINAL_ROOT")?;
        self.scope.check_current_lineage(current)?;
        let original_control=control.control_originals(current)?;
        original_control.verify(current,self.scope.domain)?.check_operation(&self.scope.operation).map_err(|_|Error("PREFIX_ORIGINAL_OPERATION"))?;
        require(request.ledger_confirmation.writer==current.writer,"PREFIX_CURRENT_WRITER")?;
        if let Some(a)=&request.current_admission{
            verify_prefix_admission(&self.scope,Some(a),self.signer)?;
            require(a.inspection.request.current_execution_scope==receipt.selected.execution_scope,"PREFIX_CURRENT_ROOT_SCOPE")?;
            original_control.attests(&a.inspection.request.current_ledger_confirmation,current)?;
        }
        let root=receipt.chain.last().unwrap();
        let (entries,_)=selected_chain(root,&self.scope,limits,&request.next,self.signer,response_signer,request.entry_binding.relative_path.starts_with("sequence-"),Some(request))?;
        let retained=entries.last().ok_or(Error("PREFIX_FINAL_ENTRY_MISSING"))?;
        if let Some(b)=retained.entry.originals.get("control-confirmation.json"){
            let exact:HostConfirmation=decode(&receipt.read(b,quota::MAX_PACKET)?,quota::MAX_PACKET)?;
            require(exact==*current,"PREFIX_CONTROL_TRANSITION_JOIN")?;
        }else{require(request.ledger_confirmation==*current,"PREFIX_CURRENT_CONTROL_JOIN")?;}
        control.recheck_control(&original_control,current)?;receipt.guard()?;
        let again=selected_chain(root,&self.scope,limits,&request.next,self.signer,response_signer,request.entry_binding.relative_path.starts_with("sequence-"),Some(request))?.0;
        require(entries.iter().map(|e|&e.entry_binding).eq(again.iter().map(|e|&e.entry_binding)),"PREFIX_ORIGINALS_CHANGED")?;
        request.validate(now_seconds()?)
    }
    pub(crate) fn inspect(&self, request: &PrefixInspectionRequest, peer: &Caller,
                         selected_recipient: &Caller, selected_channel: &Binding,
                         selected_ledger: &HostConfirmation, selected_scope: &roots::ExecutionScope) -> Result<Vec<u8>> {
        self.hold.validate()?; require(!self.poisoned, "WITNESS_UNCERTAIN")?;
        require(request.schema_version == "lab-broker-prefix-inspection-request/v1"
            && request.history_key == self.scope.history_key()? && request.recipient == *selected_recipient
            && request.recipient == *peer && request.channel_binding == *selected_channel
            && request.current_ledger_confirmation == *selected_ledger
            && request.current_execution_scope == *selected_scope && selected_scope.valid()
            && roots::digest(&request.challenge),
            "WITNESS_INSPECTION_SELECTION")?;
        self.scope.check_current_lineage(selected_ledger)?;
        interval(request.not_before, request.expires_at, now_seconds()?)?;
        let raw=self.signer.sign(&self.key, &PrefixInspection { schema_version: "lab-broker-prefix-inspection/v1".into(),
            request: request.clone(), original_scope_binding: self.scope_binding.clone(), head: self.head.clone(),
            signer_enrollment_binding: self.signer.binding().clone(),original_confirmation_binding:self.latest_response.as_ref().map(|r|bound(&self.hold.root().selection().root_id,&format!("prefix-{:016}.json",self.head.ordinal),r)).transpose()? })?;
        interval(request.not_before,request.expires_at,now_seconds()?)?;Ok(raw)
    }
    /// Fresh current inspection authorizes only fetching the exact old signed
    /// original. It does not issue a new CAS or renew the original request.
    pub(crate) fn read_original(&self,request:&PrefixOriginalRequest,peer:&Caller,recipient:&Caller,channel:&Binding,
        ledger:&HostConfirmation,scope:&roots::ExecutionScope)->Result<Vec<u8>>{
        require(request.schema_version=="lab-broker-prefix-original-request/v1","PREFIX_ORIGINAL_REQUEST")?;
        self.inspect(&request.query,peer,recipient,channel,ledger,scope)?;
        let raw=self.latest_response.as_ref().ok_or(Error("GENESIS_HAS_NO_CONFIRMATION"))?;
        require(bound(&self.hold.root().selection().root_id,&format!("prefix-{:016}.json",self.head.ordinal),raw)?==request.original_binding,"PREFIX_ORIGINAL_SELECTION")?;
        let retained=read_file(self.hold.directory(),&format!("prefix-{:016}.json",self.head.ordinal),self.hold.root().identity(),quota::MAX_PACKET)?;
        require(retained==*raw,"PREFIX_ORIGINAL_CHANGED")?;interval(request.query.not_before,request.query.expires_at,now_seconds()?)?;Ok(retained)
    }
}

/// Independently installed current role policy. It references original stable
/// history, but never selects a new history head from a packet or filesystem.
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct PrefixServiceSelection {
    pub schema_version:String,pub domain:Domain,pub original_scope_binding:Binding,
    pub prefix_signer_binding:Binding,pub response_signer_binding:Binding,pub limits_binding:Binding,
    pub control_service_binding:Binding,pub control_signer_binding:Binding,
    pub receipt_root_id:String,pub witness_root:Identity,pub recipient:Caller,pub channel_binding:Binding,
    pub current_writer:WriterFence,pub current_execution_scope:roots::ExecutionScope,
    pub capacity_binding:Binding,pub not_before:u64,pub expires_at:u64,
}
/// A finite whole-history allocation, independently held before the first CAS.
/// Every retained confirmation (including lost replies) consumes this same pool.
/// Selection alone is not proof of actual physical reservation.
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct PrefixCapacityOriginal {
    pub schema_version:String,pub domain:Domain,pub history_key:String,pub physical_root:Identity,
    pub control_root:lab_control_store::custody::Identity,pub control_header_sha256:String,
    pub held_reservation_binding:Binding,pub max_confirmations:u64,pub reserved_bytes:u64,pub reserved_inodes:u64,
    pub not_before:u64,pub expires_at:u64,
}
impl PrefixWitness<'_> {
    /// Concrete fixed service composition. The current control fence is held by
    /// ControlWitness, not supplied by the requester or inferred from a tail.
    /// Both witnesses have distinct custody; reading control never reacquires
    /// the broker's Held. A caller can only select these services at fixed launch.
    pub(crate) fn serve_one(&mut self,channel:&Channel,host:&HostService,control:&ControlWitness<'_>)->Result<()> {
        let raw=channel.receive()?;
        let response=self.respond_selected(&raw,channel,host,control)?;
        channel.send(&response)
    }
    fn respond_selected(&mut self,raw:&[u8],channel:&Channel,host:&HostService,control:&ControlWitness<'_>)->Result<Vec<u8>> {
        self.hold.validate()?;channel.guard()?;control.hold.validate()?;
        require(!control.poisoned&&!self.poisoned,"PREFIX_SERVICE_UNCERTAIN")?;
        let before=host.originals()?;
        let template=host.read(&host.selected.template_binding,quota::MAX_PACKET)?;
        let facts:HostFacts=decode(&template,quota::MAX_PACKET)?;
        let selected_bytes=before.get(&roots::hash(&encode(&facts.current_prefix_binding)?)).ok_or(Error("PREFIX_ROLE_NOT_SELECTED"))?;
        let selected:PrefixServiceSelection=decode(selected_bytes,quota::MAX_PACKET)?;
        let source=|b:&Binding|->Result<&Vec<u8>>{before.get(&roots::hash(&encode(b)?)).ok_or(Error("PREFIX_SOURCE_NOT_SELECTED"))};
        let now=now_seconds()?;
        interval(selected.not_before,selected.expires_at,now)?;
        require(selected.schema_version=="lab-broker-prefix-service/v1"&&selected.domain==self.scope.domain
            &&host.selected.domain==self.scope.domain&&facts.domain==self.scope.domain&&facts.operation==self.scope.operation
            &&facts.authority_domain==self.scope.authority_domain&&selected.original_scope_binding==self.scope_binding
            &&selected.prefix_signer_binding==*self.signer.binding()&&selected.current_execution_scope.valid()
            &&selected.current_execution_scope==facts.scope&&selected.receipt_root_id==self.scope.receipt_root_id
            &&selected.witness_root==*self.hold.root().identity()&&selected.recipient==channel.selected.peer
            &&selected.channel_binding==channel.selected.channel_binding&&selected.recipient.valid()
            &&selected.control_service_binding==control.service_binding&&selected.control_signer_binding==*control.signer.binding()
            &&selected.current_writer==control.current.writer&&control.domain==self.scope.domain,
            "PREFIX_FIXED_SERVICE_SELECTION")?;
        self.scope.check_current_lineage(&control.current)?;
        self.signer.distinct(&host.signer)?;self.signer.distinct(control.signer)?;
        let response_signer=SelectedSigner::select(source(&selected.response_signer_binding)?,&selected.response_signer_binding,self.scope.domain,"broker-response")?;
        self.signer.distinct(&response_signer)?;control.signer.distinct(&response_signer)?;host.signer.distinct(&response_signer)?;
        let limits:quota::Limits=decode(source(&selected.limits_binding)?,quota::MAX_PACKET)?;limits.validate()?;
        require(facts.quota_binding==selected.limits_binding,"PREFIX_QUOTA_SELECTION")?;
        let receipt=host.roots.get(&selected.receipt_root_id).ok_or(Error("PREFIX_RECEIPT_ROOT"))?;
        require(receipt.selected.execution_scope==selected.current_execution_scope,"PREFIX_CURRENT_ROOT_SCOPE")?;
        // Physical endpoints may share ordinary ancestors but may not contain
        // each other: no service lock can alias a broker-held subtree.
        for root in host.roots.values(){
            let endpoint=root.selected.ancestors.last().ok_or(Error("PREFIX_ROOT_IDENTITY"))?;
            require(!root.selected.ancestors.iter().any(|id|id.device==selected.witness_root.device&&id.inode==selected.witness_root.inode)
                &&!self.hold.root().selection().ancestors.iter().any(|id|id.device==endpoint.device&&id.inode==endpoint.inode),"PREFIX_LOCK_ROOT_OVERLAP")?;
        }
        disjoint_endpoints(self.hold,control.hold)?;
        let current=control.current.clone();
        let original_control=control.control.control_originals(&current)?;
        let operation_state=original_control.verify(&current,self.scope.domain)?.operation_state(&self.scope.operation).map_err(|_|Error("PREFIX_ORIGINAL_OPERATION"))?;
        let capacity:PrefixCapacityOriginal=decode(source(&selected.capacity_binding)?,quota::MAX_PACKET)?;
        source(&capacity.held_reservation_binding)?;
        require(capacity.schema_version=="lab-broker-prefix-capacity/v1"&&capacity.domain==self.scope.domain
            &&capacity.history_key==self.scope.history_key()?&&capacity.physical_root==selected.witness_root
            &&capacity.control_root==current.root&&capacity.control_header_sha256==current.header_sha256
            &&(1..=4096).contains(&capacity.max_confirmations)
            &&capacity.reserved_bytes>=capacity.max_confirmations*quota::MAX_PACKET&&capacity.reserved_bytes<=1<<40
            &&capacity.reserved_inodes>=capacity.max_confirmations&&capacity.reserved_inodes<=100000,"PREFIX_WITNESS_CAPACITY")?;
        let value:Value=decode(raw,quota::MAX_PACKET)?;
        let version=value.get("schema_version").and_then(Value::as_str).ok_or(Error("PREFIX_SERVICE_VERB"))?;
        let cas=version=="lab-broker-prefix-cas-request/v1";
        let revocation:RevocationOriginal=decode(source(&facts.revocation_binding)?,quota::MAX_PACKET)?;
        require(revocation.schema_version=="lab-broker-host-revocation/v1"&&revocation.issuer_enrollment_binding==facts.issuer_enrollment_binding,"PREFIX_REVOCATION_SELECTION")?;
        source(&revocation.native_original_binding)?;
        let validate_live=||->Result<()>{
            let now=now_seconds()?;
            require(!revocation.revoked,"PREFIX_ISSUER_NOT_CURRENT")?;
            interval(revocation.not_before,revocation.expires_at,now)?;
            interval(facts.not_before,facts.expires_at.min(facts.activation_expires_at),now)?;
            interval(capacity.not_before,capacity.expires_at,now)
        };
        if cas{require(matches!(operation_state,OriginalOperationState::Present{..}),"PREFIX_ORIGINAL_OPERATION")?;validate_live()?;}
        let usage=owned_inventory(self.hold,capacity.reserved_inodes,capacity.reserved_bytes)?;
        require(usage.len() as u64==self.head.ordinal&&usage.iter().enumerate().all(|(i,(name,(_,size,_)))|
            name==&format!("prefix-{:016}.json",i+1)&&*size<=quota::MAX_PACKET),"PREFIX_WITNESS_INVENTORY")?;
        let bytes=usage.values().try_fold(0u64,|sum,(_,size,_)|sum.checked_add(*size).ok_or(Error("PREFIX_WITNESS_OVERFLOW")))?;
        // Every historical file is signature/chain-verified, not only counted.
        let mut prior=PrefixHead::genesis(&self.scope)?;
        for (name,(_,_,digest)) in &usage{
            let original=read_file(self.hold.directory(),name,self.hold.root().identity(),quota::MAX_PACKET)?;
            let proof:PrefixConfirmation=self.signer.verify(&original)?;
            require(roots::hash(&original)==*digest&&proof.schema_version=="lab-broker-prefix-confirmation/v1"
                &&proof.result=="confirmed"&&proof.signer_enrollment_binding==*self.signer.binding()
                &&proof.request.scope==self.scope&&proof.request.prior==prior,"PREFIX_WITNESS_ORIGINAL_CHAIN")?;
            proof.request.validate(proof.request.not_before)?;verify_prefix_admission(&self.scope,proof.request.current_admission.as_ref(),self.signer)?;
            prior=proof.request.next;
        }
        require(prior==self.head,"PREFIX_WITNESS_HIGH_WATER")?;
        let validate_source=||->Result<()>{
            require(host.originals()?==before&&host.read(&host.selected.template_binding,quota::MAX_PACKET)?==template,"PREFIX_SERVICE_PROFILE_CHANGED")?;
            control.control.recheck_control(&original_control,&current)?;channel.guard()?;
            interval(selected.not_before,selected.expires_at,now_seconds()?)
        };
        validate_source()?;
        let result=match version{
            "lab-broker-prefix-cas-request/v1"=>{
                let request:PrefixRequest=decode(raw,quota::MAX_PACKET)?;
                let (recipient,channel_binding)=request.current_admission.as_ref().map(|a|(&a.inspection.request.recipient,&a.inspection.request.channel_binding)).unwrap_or((&request.scope.recipient,&request.scope.channel_binding));
                require(*recipient==selected.recipient&&*channel_binding==selected.channel_binding,"PREFIX_RECEIVING_CHANNEL")?;
                let duplicate=self.latest_request.as_ref()==Some(&request);
                require(duplicate||(self.head.ordinal<capacity.max_confirmations&&usage.len() as u64+1<=capacity.reserved_inodes
                    &&bytes.checked_add(quota::MAX_PACKET).is_some_and(|n|n<=capacity.reserved_bytes)),"PREFIX_REMAINING_RESERVE")?;
                interval(capacity.not_before,capacity.expires_at,now_seconds()?)?;
                self.verify_originals(&request,receipt,control.control,&current,&limits,&response_signer)?;
                validate_source()?;validate_live()?;
                let start=selected.not_before.max(host.selected.not_before).max(facts.not_before).max(revocation.not_before).max(capacity.not_before);
                let end=selected.expires_at.min(host.selected.expires_at).min(facts.expires_at).min(facts.activation_expires_at).min(revocation.expires_at).min(capacity.expires_at);
                self.cas_until(&request,&channel.selected.peer,Some((start,end)))?
            },
            "lab-broker-prefix-inspection-request/v1"=>self.inspect(&decode(raw,quota::MAX_PACKET)?,&channel.selected.peer,&selected.recipient,&selected.channel_binding,&current,&selected.current_execution_scope)?,
            "lab-broker-prefix-original-request/v1"=>self.read_original(&decode(raw,quota::MAX_PACKET)?,&channel.selected.peer,&selected.recipient,&selected.channel_binding,&current,&selected.current_execution_scope)?,
            _=>return Err(Error("PREFIX_SERVICE_VERB")),
        };
        // A post-CAS expiry/error is uncertain delivery. The immutable proof
        // remains retained and fresh inspection can fetch it without re-CAS.
        #[cfg(test)] prefix_fixture_delay(2);
        validate_source()?;
        let (not_before,expires_at)=match version{
            "lab-broker-prefix-cas-request/v1"=>{let q:PrefixRequest=decode(raw,quota::MAX_PACKET)?;(q.not_before,q.expires_at)},
            "lab-broker-prefix-inspection-request/v1"=>{let q:PrefixInspectionRequest=decode(raw,quota::MAX_PACKET)?;(q.not_before,q.expires_at)},
            "lab-broker-prefix-original-request/v1"=>{let q:PrefixOriginalRequest=decode(raw,quota::MAX_PACKET)?;(q.query.not_before,q.query.expires_at)},
            _=>return Err(Error("PREFIX_SERVICE_VERB")),
        };interval(not_before,expires_at,now_seconds()?)?;if cas{validate_live()?;}Ok(result)
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ChannelSelection {
    pub schema_version: String, pub channel_binding: Binding,
    pub device: u64, pub inode: u64, pub peer: Caller,
    pub max_packet_bytes: u64, pub timeout_ms: u64,
}
/// Fixed bounded seqpacket transport. No shell, dynamic code or FD transfer;
/// every response checks kernel credentials against the installed selection.
/// A timeout after send is uncertainty, not proof that a CAS did not happen.
pub struct Channel {
    fd: OwnedFd, receiver: wire::Receiver, selected: ChannelSelection,
}
impl Channel {
    pub fn from_selected(fd: OwnedFd, selected: ChannelSelection) -> Result<Self> {
        require(selected.schema_version == "lab-broker-fixed-channel/v1" && selected.channel_binding.valid()
            && selected.peer.valid() && (1..=quota::MAX_PACKET).contains(&selected.max_packet_bytes)
            && (1..=60000).contains(&selected.timeout_ms), "CHANNEL_SELECTION")?;
        let cloned = fd.try_clone().map_err(|_| Error("CHANNEL_DUP"))?;
        let receiver = wire::Receiver::new(cloned, selected.max_packet_bytes as usize, wire::MAX_CONTROL)
            .map_err(|_| Error("CHANNEL_SOCKET"))?;
        let value = Self { fd, receiver, selected }; value.guard()?; Ok(value)
    }
    fn guard(&self) -> Result<()> {
        let mut s: libc::stat = unsafe { std::mem::zeroed() };
        require(unsafe { libc::fstat(self.fd.as_raw_fd(), &mut s) } == 0
            && s.st_mode & libc::S_IFMT == libc::S_IFSOCK
            && s.st_dev == self.selected.device && s.st_ino == self.selected.inode,
            "CHANNEL_IDENTITY")
    }
    pub fn selection(&self) -> &ChannelSelection { &self.selected }
    fn send_until(&self, raw: &[u8], deadline: Instant) -> Result<()> {
        self.guard()?; require(!raw.is_empty() && raw.len() as u64 <= self.selected.max_packet_bytes, "SEND_BOUND")?;
        loop {
            let left = deadline.saturating_duration_since(Instant::now());
            require(!left.is_zero(), "SEND_TIMEOUT_UNCERTAIN")?;
            let mut poll = libc::pollfd { fd: self.fd.as_raw_fd(), events: libc::POLLOUT, revents: 0 };
            let n = unsafe { libc::poll(&mut poll, 1, left.as_millis().max(1).min(i32::MAX as u128) as i32) };
            if n < 0 && std::io::Error::last_os_error().raw_os_error() == Some(libc::EINTR) { continue; }
            require(n >= 0, "SEND_POLL")?; if n == 0 { continue; }
            let n = unsafe { libc::send(self.fd.as_raw_fd(), raw.as_ptr().cast(), raw.len(), libc::MSG_DONTWAIT | libc::MSG_NOSIGNAL) };
            if n < 0 && matches!(std::io::Error::last_os_error().raw_os_error(), Some(libc::EINTR) | Some(libc::EAGAIN)) { continue; }
            require(n == raw.len() as isize, "SEND_UNCERTAIN")?; self.guard()?; return Ok(());
        }
    }
    pub fn send(&self, raw: &[u8]) -> Result<()> {
        self.send_until(raw, Instant::now() + Duration::from_millis(self.selected.timeout_ms))
    }
    pub fn receive(&self) -> Result<Vec<u8>> {
        self.guard()?;
        let packet = self.receiver.receive(Duration::from_millis(self.selected.timeout_ms)).map_err(|_| Error("RECEIVE_UNCERTAIN"))?;
        require(packet.peer == self.selected.peer.peer(), "CHANNEL_PEER")?; self.guard()?; Ok(packet.bytes)
    }
    pub fn call(&self, raw: &[u8]) -> Result<Vec<u8>> {
        let deadline = Instant::now() + Duration::from_millis(self.selected.timeout_ms);
        self.send_until(raw, deadline)?;
        let left = deadline.saturating_duration_since(Instant::now());
        require(!left.is_zero(), "REPLY_TIMEOUT_UNCERTAIN")?;
        let packet = self.receiver.receive(left).map_err(|_| Error("REPLY_UNCERTAIN"))?;
        require(packet.peer == self.selected.peer.peer(), "CHANNEL_PEER")?;
        self.guard()?; Ok(packet.bytes)
    }
}

/// Fresh unpredictability belongs to the fixed broker, not the request author.
pub fn challenge() -> Result<String> {
    let mut bytes = [0u8; 32]; let mut offset = 0;
    while offset < bytes.len() {
        let n = unsafe { libc::getrandom(bytes[offset..].as_mut_ptr().cast(), bytes.len() - offset, 0) };
        if n < 0 && std::io::Error::last_os_error().raw_os_error() == Some(libc::EINTR) { continue; }
        require(n > 0, "CHALLENGE_RANDOMNESS")?; offset += n as usize;
    }
    Ok(wire::hex(&bytes))
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HostQuery {
    pub schema_version: String, pub read_only:bool, pub launch_selection_binding: Binding,
    pub operation_id: String, pub original_fingerprint: String,
    pub frame_sha256: String, pub challenge: String, pub channel_binding: Binding,
    pub recipient: Caller,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RecoveryFact {
    pub authorization_binding: Value, pub subject_binding: Binding,
    pub preimages: Vec<Binding>, pub action: String, pub consumed: bool,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EffectInputs {
    pub commit:Option<Binding>,pub restart:Option<Binding>,pub supervisor:Option<Binding>,pub derived:Option<Binding>,
}
impl EffectInputs {pub fn bindings(&self)->impl Iterator<Item=&Binding>{[&self.commit,&self.restart,&self.supervisor,&self.derived].into_iter().filter_map(Option::as_ref)}}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HostFacts {
    pub schema_version: String, pub query: HostQuery, pub domain: Domain,
    pub authority_domain: String, pub operation: Operation,
    pub scope: roots::ExecutionScope, pub live_authority_scope: Value,
    pub ledger_confirmation: HostConfirmation,
    pub control_root_id: String, pub operation_state: OriginalOperationState,
    pub roots: Vec<roots::Selection>, pub quota_binding: Binding,
    pub issuer_enrollment_binding: Binding, pub revocation_binding: Binding,
    pub issuer_revoked: bool, pub observation_utc_seconds: u64,
    pub not_before: u64, pub expires_at: u64, pub activation_expires_at: u64,
    pub core_binding: Binding, pub basis_binding: Binding,
    pub selected_inputs: Vec<Binding>, pub member_identity_originals: Vec<Binding>,
    pub disclosure_subjects: Vec<Binding>, pub recovery: Option<RecoveryFact>,
    pub remaining_capacity: quota::Remaining, pub capacity_custody_binding: Binding,
    /// Additional independently selected per-physical-root reservations. These
    /// do not borrow the receipt-root byte/inode reserve.
    pub additional_capacity_bindings: Vec<Binding>,
    /// Later originals are selected by the enrolled profile manager after
    /// their causal inputs exist, never by a client or a latest-file lookup.
    pub effect_inputs:EffectInputs,
    pub capacity_root_id: String,
    pub current_prefix_binding: Binding,
}
/// Independently selected fixed-launch policy; this is never decoded from a
/// client BrokerRequest. The external launcher pins exact original bytes.
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LaunchSelection {
    pub schema_version: String, pub domain: Domain, pub authority_domain: String,
    pub operation: Operation, pub original_scope_binding: Binding,
    pub host_signer_binding: Binding, pub receipt_signer_binding: Binding,
    pub prefix_signer_binding: Binding, pub intent_signer_binding: Binding,pub control_signer_binding:Binding,pub control_service_binding:Binding,
    pub source_binding: Binding, pub profile_binding: Binding,
    pub namespace_qualification_binding: Binding,
    pub caller: Caller, pub broker_identity: Caller, pub host_channel: ChannelSelection,
    pub prefix_channel: ChannelSelection, pub control_channel:ChannelSelection,pub client_channel: ChannelSelection,
    pub allowed_root_ids: Vec<String>, pub core_binding: Binding,
    pub basis_binding: Binding, pub quota_binding: Binding,
    pub execution_scope: roots::ExecutionScope, pub max_observation_age_seconds: u64,
}
pub struct FixedHost {
    selected: LaunchSelection, original: Binding, signer: SelectedSigner, channel: Channel,
}
pub struct VerifiedHostFacts { value: HostFacts, original: Vec<u8> }
impl FixedHost {
    pub fn load(selection_raw: &[u8], expected: &Binding, host_signer_raw: &[u8], fd: OwnedFd,
                required_domain: Domain) -> Result<Self> {
        verify_bytes(selection_raw, expected)?;
        let selected: LaunchSelection = decode(selection_raw, quota::MAX_PACKET)?;
        require(selected.schema_version == "lab-broker-fixed-launch/v1" && selected.domain == required_domain
            && ident(&selected.authority_domain) && selected.caller.valid() && selected.broker_identity.valid()
            && selected.broker_identity == (Caller { pid: unsafe { libc::getpid() }, uid: unsafe { libc::geteuid() }, gid: unsafe { libc::getegid() } })
            && selected.client_channel.peer == selected.caller && selected.execution_scope.valid()
            && (1..=60).contains(&selected.max_observation_age_seconds)
            && selected.operation.store_id == selected.execution_scope.store_id
            && selected.operation.store_instance == selected.execution_scope.instance_id
            && selected.operation.slot_epoch == selected.execution_scope.slot_epoch
            && !selected.allowed_root_ids.is_empty() && selected.allowed_root_ids.len() <= 16
            && selected.allowed_root_ids.iter().collect::<BTreeSet<_>>().len() == selected.allowed_root_ids.len()
            && [&selected.original_scope_binding, &selected.host_signer_binding, &selected.receipt_signer_binding,
                &selected.prefix_signer_binding, &selected.intent_signer_binding,&selected.control_signer_binding,&selected.control_service_binding, &selected.source_binding,
                &selected.profile_binding, &selected.namespace_qualification_binding, &selected.core_binding,
                &selected.basis_binding, &selected.quota_binding].iter().all(|b| b.valid()), "FIXED_LAUNCH_SELECTION")?;
        require(selected.host_signer_binding != selected.receipt_signer_binding
            && selected.host_signer_binding != selected.prefix_signer_binding
            && selected.receipt_signer_binding != selected.prefix_signer_binding, "SIGNER_ROLE_BINDING_ALIAS")?;
        let signer = SelectedSigner::select(host_signer_raw, &selected.host_signer_binding, required_domain, "host-selection")?;
        let channel = Channel::from_selected(fd, selected.host_channel.clone())?;
        Ok(Self { selected, original: expected.clone(), signer, channel })
    }
    pub fn selection(&self) -> &LaunchSelection { &self.selected }
    pub(crate) fn check_role_keys(&self,response:&SelectedSigner,prefix:&SelectedSigner,control:&SelectedSigner,intent_raw:&[u8])->Result<()> {
        require(response.binding()==&self.selected.receipt_signer_binding&&prefix.binding()==&self.selected.prefix_signer_binding&&control.binding()==&self.selected.control_signer_binding
            &&response.purpose()=="broker-response"&&prefix.purpose()=="receipt-prefix"&&control.purpose()=="control-confirmation","FIXED_ROLE_SELECTION")?;
        let all=[&self.signer,response,prefix,control];
        for(i,a)in all.iter().enumerate(){require(a.domain()==self.selected.domain,"FIXED_ROLE_DOMAIN")?;for b in &all[i+1..]{a.distinct(b)?;}}
        let intent:Value=decode(intent_raw,8192)?;let key=intent["public_key"].as_str().ok_or(Error("INTENT_ENROLLMENT_KEY"))?;
        let key=wire::unhex::<32>(key).map_err(|_|Error("INTENT_ENROLLMENT_KEY"))?;
        require(all.iter().all(|s|s.key.as_bytes().as_slice()!=key.as_slice()),"INTENT_CUSTODY_KEY_ALIAS")
    }
    pub fn query(&self, frame: &wire::Frame) -> Result<VerifiedHostFacts> {
        let query = HostQuery { schema_version: "lab-broker-current-host-query/v1".into(),
            read_only:matches!(frame.request()["verb"].as_str(),Some("inspect"|"inspect_operation"|"read_receipt")),
            launch_selection_binding: self.original.clone(), operation_id: self.selected.operation.operation_id.clone(),
            original_fingerprint: self.selected.operation.fingerprint.clone(), frame_sha256: frame.wire_digest().into(),
            challenge: challenge()?, channel_binding: self.selected.host_channel.channel_binding.clone(),
            recipient: self.selected.broker_identity.clone() };
        let original = self.channel.call(&encode(&query)?)?;
        self.verify_facts(&original, &query, now_seconds()?)
    }
    fn verify_facts(&self, original: &[u8], query: &HostQuery, now: u64) -> Result<VerifiedHostFacts> {
        let value: HostFacts = self.signer.verify(original)?;
        require(value.schema_version == "lab-broker-current-host-facts/v1" && value.query == *query
            && value.query.launch_selection_binding == self.original && value.domain == self.selected.domain
            && (query.read_only||value.operation_state!=OriginalOperationState::Uncertain)
            && value.authority_domain == self.selected.authority_domain && value.operation == self.selected.operation
            && value.scope == self.selected.execution_scope
            && value.core_binding == self.selected.core_binding && value.basis_binding == self.selected.basis_binding
            && value.quota_binding == self.selected.quota_binding
            && value.issuer_enrollment_binding == self.selected.intent_signer_binding
            && value.revocation_binding.valid() && value.capacity_custody_binding.valid()
            && value.current_prefix_binding.valid()
            && value.observation_utc_seconds <= now
            && now - value.observation_utc_seconds <= self.selected.max_observation_age_seconds
            && value.expires_at <= value.activation_expires_at && value.activation_expires_at <= i64::MAX as u64
            && value.ledger_confirmation.authority_domain == value.authority_domain
            && value.roots.len() == self.selected.allowed_root_ids.len(), "CURRENT_HOST_FACTS")?;
        interval(value.not_before, value.expires_at, now)?;
        let ids: BTreeSet<_> = value.roots.iter().map(|r| r.root_id.as_str()).collect();
        require(ids.len() == value.roots.len() && ids == self.selected.allowed_root_ids.iter().map(String::as_str).collect()
            && value.roots.iter().all(|r| r.domain == value.domain && r.execution_scope == value.scope)
            && value.disclosure_subjects.len() <= 64 && value.disclosure_subjects.iter().all(Binding::valid)
            && value.member_identity_originals.len() <= 1024 && value.member_identity_originals.iter().all(Binding::valid)
            && value.additional_capacity_bindings.len()<=32 && value.additional_capacity_bindings.iter().all(Binding::valid)
            && value.effect_inputs.bindings().all(Binding::valid)
            && value.additional_capacity_bindings.iter().map(encode).collect::<Result<BTreeSet<_>>>()?.len()==value.additional_capacity_bindings.len()
            && value.member_identity_originals.iter().map(|b|encode(b)).collect::<Result<BTreeSet<_>>>()?.len()==value.member_identity_originals.len()
            && value.selected_inputs.len() <= 64 && value.selected_inputs.iter().all(Binding::valid)
            && value.disclosure_subjects.iter().map(|b| encode(b)).collect::<Result<BTreeSet<_>>>()?.len() == value.disclosure_subjects.len(),
            "CURRENT_ROOT_DISCLOSURE_SCOPE")?;
        if let Some(r) = &value.recovery {
            require(r.subject_binding.valid() && r.preimages.len() <= 32 && r.preimages.iter().all(Binding::valid)
                && matches!(r.action.as_str(),"reconcile_chunk"|"complete_commit"|"quarantine"|"seal_outcome"|"restore_continuity"|"close_family"),
                "CURRENT_RECOVERY_SCOPE")?;
            wire::validate_content_digest(&r.authorization_binding).map_err(|_| Error("RECOVERY_AUTHORIZATION_BINDING"))?;
        }
        Ok(VerifiedHostFacts { value, original: original.into() })
    }
}
impl VerifiedHostFacts {
    pub fn facts(&self) -> &HostFacts { &self.value }
    pub fn original(&self) -> &[u8] { &self.original }
    pub fn read_selected(&self, roots: &BTreeMap<String, &roots::Root>, binding: &Binding,
                         maximum: u64) -> Result<Vec<u8>> {
        self.current()?;
        require(binding == &self.value.core_binding || binding == &self.value.basis_binding
            || binding == &self.value.issuer_enrollment_binding || binding == &self.value.quota_binding
            || self.value.selected_inputs.contains(binding) || self.value.disclosure_subjects.contains(binding)
            || self.value.member_identity_originals.contains(binding) || self.value.additional_capacity_bindings.contains(binding)
            || self.value.effect_inputs.bindings().any(|b|b==binding), "INPUT_NOT_SELECTED")?;
        require(binding.valid() && binding.size_bytes <= maximum && maximum <= quota::MAX_RECORD, "INPUT_BOUND")?;
        let root = roots.get(&binding.root_id).ok_or(Error("INPUT_ROOT_NOT_SELECTED"))?;
        let selected_raw = encode(root.selection())?;
        let selected_roots = self.value.roots.iter().map(encode).collect::<Result<Vec<_>>>()?;
        require(selected_roots.contains(&selected_raw), "INPUT_ROOT_SELECTION")?;
        root.validate()?;
        let parts = roots::parts(&binding.relative_path)?;
        let mut directory = root.directory().try_clone()?;
        for part in &parts[..parts.len()-1] {
            directory = roots::open_child(&directory, part, libc::O_RDONLY | libc::O_DIRECTORY, 0, true)?;
            roots::owned_dir(&directory, root.identity().uid, root.identity().mount_id)?;
        }
        let raw = read_file(&directory, parts.last().unwrap(), root.identity(), maximum)?;
        verify_bytes(&raw, binding)?; root.validate()?; self.current()?; Ok(raw)
    }
    pub fn current(&self) -> Result<()> {
        interval(self.value.not_before, self.value.expires_at, now_seconds()?)
    }
    pub fn open_ledger<'a>(&self, root: &'a lab_control_store::custody::Root,
                           held: &lab_control_store::custody::Held<'_>) -> Result<lab_control_store::ledger::Ledger<'a>> {
        self.current()?;
        require(self.value.ledger_confirmation.root == root.identity(), "HOST_CONTROL_ROOT")?;
        let ledger = lab_control_store::ledger::Ledger::open(root, held, lab_control_store::ledger::TrustedSelection {
            confirmation: self.value.ledger_confirmation.clone(), posture: if self.value.domain == Domain::Fixture {
                lab_control_store::ledger::Posture::Fixture } else { lab_control_store::ledger::Posture::Actual }
        }).map_err(|_| Error("CONTROL_ORIGINALS"))?;
        require(ledger.inspect().writable, "CONTROL_UNCERTAIN")?; Ok(ledger)
    }
}

/// Fixed read-only host evidence root. Unlike the writer Root, this can read a
/// separately owned selected directory under OS-granted authority. It returns
/// bytes only to the fixed service, never an FD to the unprivileged caller.
pub struct OriginalDirectory { selected: roots::Selection, chain: Vec<File>, children:BTreeMap<String,Identity> }
impl OriginalDirectory {
    pub fn open(selected: roots::Selection, domain: Domain) -> Result<Self> {
        use std::os::unix::fs::OpenOptionsExt;
        require(selected.domain == domain && selected.execution_scope.valid()
            && selected.absolute_path.starts_with('/') && !selected.absolute_path.ends_with('/')
            && selected.alias_exclusion_binding.valid() && selected.ancestor_inventory_binding.valid()
            && selected.acl_policy_binding.valid() && selected.namespace_epoch > 0
            && selected.namespace_epoch <= i64::MAX as u64 && !selected.root_id.is_empty()
            && selected.root_id.len() <= 128, "HOST_READ_ROOT_SELECTION")?;
        let components: Vec<_> = selected.absolute_path[1..].split('/').collect();
        require(!components.is_empty() && components.len() <= 64 && selected.ancestors.len() == components.len() + 1,
            "HOST_READ_ROOT_ANCESTORS")?;
        let slash = std::fs::OpenOptions::new().read(true)
            .custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC).open("/")?;
        require(Identity::observe(&slash)? == selected.ancestors[0], "HOST_READ_ROOT_IDENTITY")?;
        let mut chain = vec![slash];
        for (i, part) in components.iter().enumerate() {
            roots::name(part)?;
            let next = roots::open_child(chain.last().unwrap(), part, libc::O_RDONLY | libc::O_DIRECTORY, 0,
                selected.ancestors[i].mount_id == selected.ancestors[i+1].mount_id)?;
            require(Identity::observe(&next)? == selected.ancestors[i+1], "HOST_READ_ROOT_IDENTITY")?;
            chain.push(next);
        }
        for held in &chain {
            let id = Identity::observe(held)?;
            require(id.mode & 0o022 == 0, "HOST_WRITABLE_ANCESTOR")?;
            roots::no_acl(held)?;
            if domain == Domain::Actual { require(id.uid == selected.administrator_uid || id.uid == selected.broker_uid,
                "HOST_NONADMIN_ANCESTOR")?; }
        }
        roots::owned_dir(chain.last().unwrap(), selected.broker_uid, selected.ancestors.last().unwrap().mount_id)?;
        Ok(Self { selected, chain, children:BTreeMap::new() })
    }
    /// Selected direct child domains (for example U08 journal). This permits
    /// only exact held identities, never arbitrary extra control-root names.
    pub fn with_children(mut self,selected:&[roots::Selection])->Result<Self>{
        for child in selected {
            if let Some(name)=child.absolute_path.strip_prefix(&(self.selected.absolute_path.clone()+"/")) {
                if name.contains('/') {continue;}
                require(!matches!(name,"header.json"|"records"|"locks")&&child.domain==self.selected.domain
                    &&child.execution_scope==self.selected.execution_scope,"CONTROL_CHILD_SELECTION")?;
                let observed=Self::open(child.clone(),child.domain)?;
                let id=Identity::observe(observed.chain.last().unwrap())?;
                require(self.children.insert(name.to_string(),id).is_none(),"CONTROL_CHILD_DUPLICATE")?;
            }
        }
        require(self.children.len()<=16,"CONTROL_CHILD_COUNT")?;self.guard()?;Ok(self)
    }
    fn guard(&self) -> Result<()> {
        let reopened = Self::open(self.selected.clone(), self.selected.domain)?;
        require(reopened.chain.iter().map(Identity::observe).collect::<Result<Vec<_>>>()?
            == self.chain.iter().map(Identity::observe).collect::<Result<Vec<_>>>()?, "HOST_READ_ROOT_DRIFT")
    }
    pub fn read(&self, binding: &Binding, maximum: u64) -> Result<Vec<u8>> {
        require(binding.valid() && binding.root_id == self.selected.root_id && binding.size_bytes <= maximum
            && maximum <= quota::MAX_RECORD, "HOST_ORIGINAL_SELECTION")?;
        self.guard()?;
        let parts = roots::parts(&binding.relative_path)?;
        let identity = self.selected.ancestors.last().unwrap();
        let mut directory = self.chain.last().unwrap().try_clone()?;
        for part in &parts[..parts.len()-1] {
            directory = roots::open_child(&directory, part, libc::O_RDONLY | libc::O_DIRECTORY, 0, true)?;
            roots::owned_dir(&directory, identity.uid, identity.mount_id)?;
        }
        let raw = read_file(&directory, parts.last().unwrap(), identity, maximum)?;
        verify_bytes(&raw, binding)?; self.guard()?; Ok(raw)
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HostServiceSelection {
    pub schema_version: String, pub domain: Domain, pub signer_binding: Binding,
    pub key_binding: Binding, pub template_binding: Binding,
    pub profile_issuer_binding: Binding, pub profile_recipient:Caller, pub profile_channel_binding:Binding,
    pub revision:u64, pub predecessor_binding:Option<Binding>,
    pub source_originals: Vec<Binding>, pub roots: Vec<roots::Selection>,
    pub recipient: Caller, pub channel_binding: Binding,
    pub not_before: u64, pub expires_at: u64,
}
/// Exact selected revocation adapter record, carried in the installed host
/// evidence store. Selection/retention of the authentic upstream native record
/// is an issuer obligation; this adapter never turns an arbitrary boolean from
/// the request into currentness. Any source-byte change fences the service until
/// a fresh independently selected host profile is installed.
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RevocationOriginal {
    pub schema_version: String, pub issuer_enrollment_binding: Binding,
    pub native_original_binding: Binding, pub revoked: bool,
    pub not_before: u64, pub expires_at: u64,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CapacityOriginal {
    pub schema_version: String, pub physical_root: Identity,
    pub control_confirmation: HostConfirmation, pub remaining: quota::Remaining,
    pub held_reservation_binding: Binding, pub not_before: u64, pub expires_at: u64,
}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct HostProfileRequest {pub schema_version:String,pub prior:Binding,pub next:Binding,pub revision:u64,
    pub recipient:Caller,pub channel_binding:Binding,pub challenge:String,pub not_before:u64,pub expires_at:u64}
#[derive(Clone,Debug,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct HostProfileReceipt {pub schema_version:String,pub request:HostProfileRequest,pub result:String}
/// Concrete serving body for the custom current-host-facts protocol. It reads
/// and rechecks every selected original on both sides of signing. It does not
/// manufacture an issuer decision, a live OS reserve, or nonrollback custody.
/// Those are installed, selected inputs subject to later host qualification.
pub struct HostService {
    selected: HostServiceSelection, original:Binding, signer: SelectedSigner, profile_issuer:SelectedSigner, key: SigningKey,
    roots: BTreeMap<String, OriginalDirectory>,
}
impl HostService {
    pub fn load(raw: &[u8], expected: &Binding, signer_original: &[u8], profile_issuer_original:&[u8], domain: Domain) -> Result<Self> {
        verify_bytes(raw, expected)?;
        let selected: HostServiceSelection = decode(raw, quota::MAX_PACKET)?;
        require(selected.schema_version == "lab-broker-host-service/v1" && selected.domain == domain
            && selected.signer_binding.valid() && selected.key_binding.valid() && selected.template_binding.valid()
            && selected.recipient.valid() && selected.channel_binding.valid()
            && selected.profile_recipient.valid() && selected.profile_channel_binding.valid()
            && selected.profile_channel_binding!=selected.channel_binding && selected.profile_issuer_binding.valid()
            && selected.revision>0 && selected.revision<=i64::MAX as u64
            && (selected.revision==1)==selected.predecessor_binding.is_none()
            && (1..=16).contains(&selected.roots.len()) && (1..=64).contains(&selected.source_originals.len())
            && selected.source_originals.iter().all(Binding::valid), "HOST_SERVICE_SELECTION")?;
        interval(selected.not_before, selected.expires_at, now_seconds()?)?;
        let signer = SelectedSigner::select(signer_original, &selected.signer_binding, domain, "host-selection")?;
        let profile_issuer=SelectedSigner::select(profile_issuer_original,&selected.profile_issuer_binding,domain,"host-profile-selection")?;
        signer.distinct(&profile_issuer)?;
        let mut roots = BTreeMap::new();
        for r in &selected.roots {
            require(!roots.contains_key(&r.root_id), "HOST_SERVICE_DUPLICATE_ROOT")?;
            roots.insert(r.root_id.clone(), OriginalDirectory::open(r.clone(), domain)?);
        }
        let key_bytes = roots.get(&selected.key_binding.root_id).ok_or(Error("KEY_ROOT"))?.read(&selected.key_binding, 64)?;
        let key = signer.signing_key(&key_bytes)?;
        let child_selections=selected.roots.clone();
        let roots=roots.into_iter().map(|(id,root)|Ok((id,root.with_children(&child_selections)?))).collect::<Result<_>>()?;
        let this = Self { selected, original:expected.clone(), signer, profile_issuer, key, roots }; this.originals()?; Ok(this)
    }
    fn read(&self, b: &Binding, maximum: u64) -> Result<Vec<u8>> {
        self.roots.get(&b.root_id).ok_or(Error("HOST_SOURCE_ROOT"))?.read(b, maximum)
    }
    fn originals(&self) -> Result<BTreeMap<String, Vec<u8>>> {
        interval(self.selected.not_before, self.selected.expires_at, now_seconds()?)?;
        let mut map = BTreeMap::new();
        for b in &self.selected.source_originals {
            let key = roots::hash(&encode(b)?);
            require(!map.contains_key(&key), "DUPLICATE_HOST_SOURCE")?;
            map.insert(key, self.read(b, quota::MAX_PACKET)?);
        }
        // Private key is rechecked but never placed in retained/public evidence.
        let key = self.read(&self.selected.key_binding, 64)?;
        self.signer.signing_key(&key)?; Ok(map)
    }
    pub fn respond(&self, raw: &[u8], peer: &Caller) -> Result<Vec<u8>> {
        let query: HostQuery = decode(raw, quota::MAX_PACKET)?;
        require(query.schema_version == "lab-broker-current-host-query/v1"
            && query.recipient == self.selected.recipient && query.recipient == *peer
            && query.channel_binding == self.selected.channel_binding
            && roots::digest(&query.challenge) && roots::digest(&query.frame_sha256), "HOST_QUERY_SCOPE")?;
        let originals = self.originals()?;
        let template_raw = self.read(&self.selected.template_binding, quota::MAX_PACKET)?;
        let mut facts: HostFacts = decode(&template_raw, quota::MAX_PACKET)?;
        require(facts.schema_version == "lab-broker-current-host-facts/v1" && facts.domain == self.selected.domain
            && facts.query.launch_selection_binding == query.launch_selection_binding
            && facts.operation.operation_id == query.operation_id && facts.operation.fingerprint == query.original_fingerprint,
            "HOST_TEMPLATE_SCOPE")?;
        let get = |binding: &Binding| -> Result<&Vec<u8>> {
            originals.get(&roots::hash(&encode(binding)?)).ok_or(Error("HOST_SOURCE_NOT_SELECTED"))
        };
        let revocation: RevocationOriginal = decode(get(&facts.revocation_binding)?, quota::MAX_PACKET)?;
        let capacity: CapacityOriginal = decode(get(&facts.capacity_custody_binding)?, quota::MAX_PACKET)?;
        let control = self.roots.get(&facts.control_root_id).ok_or(Error("CONTROL_READ_ROOT_SELECTION"))?;
        let control_originals = match control.control_originals(&facts.ledger_confirmation){
            Ok(originals)=>{
                let summary=originals.verify(&facts.ledger_confirmation,self.selected.domain)?;
                require(summary.operation_state(&facts.operation).map_err(|_|Error("HOST_ORIGINAL_OPERATION_JOIN"))?==facts.operation_state,"HOST_ORIGINAL_STATE_JOIN")?;
                Some(originals)
            },Err(error)=>{
                require(query.read_only,"CONTROL_UNCERTAIN")?;
                // Current selected root custody must still verify. Failure to
                // prove original history is a closed observation, not a new
                // head, usable operation, or weakened effect admission.
                control.guard()?;let _=error;
                facts.operation_state=OriginalOperationState::Uncertain;None
            }
        };
        let now = now_seconds()?;
        interval(revocation.not_before, revocation.expires_at, now)?;
        if !query.read_only{interval(capacity.not_before, capacity.expires_at, now)?;}
        interval(facts.not_before, facts.expires_at, now)?;
        require(revocation.schema_version == "lab-broker-host-revocation/v1"
            && revocation.issuer_enrollment_binding == facts.issuer_enrollment_binding
            && revocation.native_original_binding.valid()
            && capacity.schema_version == "lab-broker-held-capacity/v1"
            && capacity.control_confirmation == facts.ledger_confirmation
            && capacity.remaining == facts.remaining_capacity && capacity.held_reservation_binding.valid()
            && facts.roots.iter().find(|r|r.root_id==facts.capacity_root_id)
                .and_then(|r|r.ancestors.last())==Some(&capacity.physical_root),
            "HOST_NATIVE_SOURCE_JOIN")?;
        get(&revocation.native_original_binding)?;
        get(&capacity.held_reservation_binding)?;
        facts.not_before = facts.not_before.max(revocation.not_before).max(self.selected.not_before);
        facts.expires_at = facts.expires_at.min(revocation.expires_at).min(self.selected.expires_at).min(facts.activation_expires_at);
        if !query.read_only{facts.not_before=facts.not_before.max(capacity.not_before);facts.expires_at=facts.expires_at.min(capacity.expires_at);}
        interval(facts.not_before,facts.expires_at,now)?;
        let mut capacity_roots=BTreeSet::new();capacity_roots.insert((capacity.physical_root.device,capacity.physical_root.inode));
        for binding in &facts.additional_capacity_bindings {
            let reserve:CapacityOriginal=decode(get(binding)?,quota::MAX_PACKET)?;
            require(reserve.schema_version=="lab-broker-held-capacity/v1" && reserve.control_confirmation==facts.ledger_confirmation
                && facts.roots.iter().any(|r|r.ancestors.last()==Some(&reserve.physical_root))
                && capacity_roots.insert((reserve.physical_root.device,reserve.physical_root.inode))
                && reserve.held_reservation_binding.valid(),"HOST_ADDITIONAL_CAPACITY_JOIN")?;
            get(&reserve.held_reservation_binding)?;
            if !query.read_only{interval(reserve.not_before,reserve.expires_at,now)?;
                facts.not_before=facts.not_before.max(reserve.not_before);facts.expires_at=facts.expires_at.min(reserve.expires_at);}
        }
        interval(facts.not_before,facts.expires_at,now)?;
        facts.query = query; facts.observation_utc_seconds = now; facts.issuer_revoked = revocation.revoked;
        let result = self.signer.sign(&self.key, &facts)?;
        require(self.read(&self.selected.template_binding, quota::MAX_PACKET)? == template_raw
            && self.originals()? == originals, "HOST_SOURCE_CHANGED_DURING_QUERY")?;
        if let Some(originals)=&control_originals{control.recheck_control(originals,&facts.ledger_confirmation)?;}
        else{control.guard()?;require(control.control_originals(&facts.ledger_confirmation).is_err(),"UNCERTAINTY_OBSERVATION_CHANGED")?;}
        interval(facts.not_before,facts.expires_at,now_seconds()?)?;
        Ok(result)
    }
    /// Authenticated source-profile advancement. The manager is a separately
    /// enrolled role; the broker cannot update facts or choose a new head. The
    /// service has no discovery/latest fallback. Restart selects the exact
    /// current profile externally, preserving all earlier original profiles.
    pub fn reselect(&mut self,raw:&[u8],peer:&Caller,channel:&Binding)->Result<Vec<u8>>{
        let request:HostProfileRequest=self.profile_issuer.verify(raw)?;
        let now=now_seconds()?;interval(request.not_before,request.expires_at,now)?;
        require(request.schema_version=="lab-broker-host-profile-reselection/v1"
            &&request.prior==self.original && request.revision==self.selected.revision.checked_add(1).ok_or(Error("PROFILE_REVISION"))?
            &&request.recipient==self.selected.profile_recipient && request.recipient==*peer
            &&request.channel_binding==self.selected.profile_channel_binding && request.channel_binding==*channel
            &&roots::digest(&request.challenge),"HOST_PROFILE_RESELECTION")?;
        let next_raw=self.read(&request.next,quota::MAX_PACKET)?;
        let next:HostServiceSelection=decode(&next_raw,quota::MAX_PACKET)?;
        require(next.predecessor_binding.as_ref()==Some(&self.original)&&next.revision==request.revision
            &&next.domain==self.selected.domain && next.signer_binding==self.selected.signer_binding
            &&next.key_binding==self.selected.key_binding && next.profile_issuer_binding==self.selected.profile_issuer_binding
            &&next.profile_recipient==self.selected.profile_recipient && next.profile_channel_binding==self.selected.profile_channel_binding
            &&next.recipient==self.selected.recipient && next.channel_binding==self.selected.channel_binding
            &&encode(&next.roots)?==encode(&self.selected.roots)?,"HOST_PROFILE_FIXED_LINEAGE")?;
        // A future profile changes exact facts/source selections only. Root,
        // key and channel rotation needs a fresh independently reviewed launch.
        let signer_raw=self.read(&next.signer_binding,8192)?;
        let issuer_raw=self.read(&next.profile_issuer_binding,8192)?;
        let successor=Self::load(&next_raw,&request.next,&signer_raw,&issuer_raw,next.domain)?;
        interval(request.not_before,request.expires_at,now_seconds()?)?;
        let response=self.signer.sign(&self.key,&HostProfileReceipt{schema_version:"lab-broker-host-profile-reselected/v1".into(),request:request.clone(),result:"selected".into()})?;
        require(self.read(&request.next,quota::MAX_PACKET)?==next_raw,"HOST_PROFILE_CHANGED")?;
        interval(request.not_before,request.expires_at,now_seconds()?)?;
        *self=successor;Ok(response)
    }
    pub fn serve_profile_one(&mut self,channel:&Channel)->Result<()> {
        require(channel.selection().peer==self.selected.profile_recipient && channel.selection().channel_binding==self.selected.profile_channel_binding,"HOST_PROFILE_CHANNEL")?;
        let raw=channel.receive()?;let response=self.reselect(&raw,&channel.selection().peer,&channel.selection().channel_binding)?;channel.send(&response)
    }
    pub fn serve_one(&self, channel: &Channel) -> Result<()> {
        require(channel.selection().peer == self.selected.recipient
            && channel.selection().channel_binding == self.selected.channel_binding, "HOST_SERVICE_CHANNEL")?;
        let raw = channel.receive()?;
        let response = self.respond(&raw, &channel.selection().peer)?;
        channel.send(&response)
    }
}

// Read-only semantic verifier copied without algorithm edits from the accepted
// Ledger State::apply contract. Source SHA dad0ba1b18dd28b3b9625ca8759bf2c173bf54fd1af93900f934704548ab1a92.
// The build pins this original and tests cross-check all Change variants. This
// module cannot append Ledger records or invent a host confirmation.
mod native_control {
use lab_control_store::{codec, Error, Result};
use lab_control_store::ledger::ByteBinding;
use lab_control_store::ledger::{Change, Operation, Outcome, SlotPhase, ReconcileAction, HostConfirmation, Head, WriterFence, Limits};
use lab_control_store::custody::Identity;
use std::collections::{BTreeMap,BTreeSet};
use serde::{Serialize,Deserialize};
fn fail<T>(s:&str)->Result<T>{Err(Error(s.into()))}
#[derive(Clone,Debug)]
struct Store { epoch:u64,instance:String }
#[derive(Clone,Debug)]
struct Slot { epoch:u64,holder:String,phase:SlotPhase }
#[derive(Clone,Debug,Default)]
struct State { stores:BTreeMap<String,Store>,slots:BTreeMap<String,Slot>,operations:BTreeMap<String,Operation>,outcomes:BTreeMap<String,(Outcome,ByteBinding)>,events:BTreeSet<(String,String)> }
impl State {
    fn terminal(&self,id:&str)->bool { self.outcomes.get(id).is_some_and(|(o,_)|matches!(o,Outcome::Committed|Outcome::Aborted)) }
    fn apply(&mut self,c:&Change)->Result<()> {
        match c {
            Change::StoreEpoch{store_id,prior_epoch,new_epoch,instance,fence_binding}=>{
                if !codec::identifier(store_id)||!codec::identifier(instance)||!fence_binding.valid()||*new_epoch!=prior_epoch.checked_add(1).ok_or_else(||Error("epoch overflow".into()))? || *new_epoch>codec::MAX_INTEGER || self.stores.get(store_id).map_or(0,|s|s.epoch)!=*prior_epoch { return fail("store epoch/fence"); }
                if self.operations.iter().any(|(id,o)|&o.store_id==store_id&&!self.terminal(id)) { return fail("unresolved prior store operation"); }
                self.stores.insert(store_id.clone(),Store{epoch:*new_epoch,instance:instance.clone()});
            }
            Change::SlotEpoch{slot_id,prior_epoch,new_epoch,holder,slot_receipt_binding,prior_disposition_binding,containment_binding}=>{
                if !codec::identifier(slot_id)||!codec::identifier(holder)||!slot_receipt_binding.valid()||!prior_disposition_binding.valid()||!containment_binding.valid()||*new_epoch!=prior_epoch.checked_add(1).ok_or_else(||Error("epoch overflow".into()))?||*new_epoch>codec::MAX_INTEGER || self.slots.get(slot_id).map_or(0,|s|s.epoch)!=*prior_epoch { return fail("slot epoch/disposition"); }
                if self.slots.get(slot_id).is_some_and(|s|s.phase!=SlotPhase::Closed) || self.operations.iter().any(|(id,o)|&o.slot_id==slot_id&&!self.terminal(id)) { return fail("unreleased prior slot"); }
                if self.slots.values().any(|s|s.phase!=SlotPhase::Closed) { return fail("authority domain live family already held"); }
                self.slots.insert(slot_id.clone(),Slot{epoch:*new_epoch,holder:holder.clone(),phase:SlotPhase::Reserved});
            }
            Change::SlotState{slot_id,epoch,holder,state,terminal_binding}=>{
                if !terminal_binding.valid() { return fail("slot transition binding"); }
                let unresolved=self.operations.iter().any(|(id,o)|&o.slot_id==slot_id&&!self.terminal(id));
                let slot=self.slots.get_mut(slot_id).ok_or_else(||Error("unknown slot".into()))?;
                if slot.epoch!=*epoch || slot.holder!=*holder { return fail("stale slot transition"); }
                let legal=matches!((slot.phase,state),(SlotPhase::Reserved,SlotPhase::Active)|(SlotPhase::Reserved,SlotPhase::Closing)|(SlotPhase::Active,SlotPhase::Closing)|(SlotPhase::Closing,SlotPhase::Closed)|(SlotPhase::Reserved,SlotPhase::Quarantined)|(SlotPhase::Active,SlotPhase::Quarantined)|(SlotPhase::Closing,SlotPhase::Quarantined));
                if !legal || (*state==SlotPhase::Closed&&unresolved) { return fail("illegal slot transition"); }
                slot.phase=*state;
            }
            Change::Reserve{operation:o}=>{
                if [&o.operation_id,&o.store_id,&o.store_instance,&o.slot_id,&o.holder,&o.issuer,&o.host_event].iter().any(|s|!codec::identifier(s))||!codec::hash(&o.fingerprint)||!codec::hash(&o.original_request_sha256) { return fail("operation domain"); }
                if self.events.contains(&(o.issuer.clone(),o.host_event.clone())) { return fail("authority-domain event consumed"); }
                if self.operations.contains_key(&o.operation_id) { return fail("operation identity consumed; inspect only"); }
                let store=self.stores.get(&o.store_id).ok_or_else(||Error("unknown store".into()))?;
                let slot=self.slots.get(&o.slot_id).ok_or_else(||Error("unknown slot".into()))?;
                if store.epoch!=o.store_epoch||store.instance!=o.store_instance||slot.epoch!=o.slot_epoch||slot.holder!=o.holder||slot.phase!=SlotPhase::Active { return fail("stale store/slot/holder"); }
                // Stronger bounded baseline: one unresolved mutation per domain.
                // This also reserves a finite terminal budget independently of
                // how many logical stores share the replay registry.
                if self.operations.keys().any(|id|!self.terminal(id)) { return fail("domain unresolved operation"); }
                self.events.insert((o.issuer.clone(),o.host_event.clone())); self.operations.insert(o.operation_id.clone(),o.clone());
            }
            Change::Outcome{operation_id,fingerprint,result_binding,outcome}=>{
                let op=self.operations.get(operation_id).ok_or_else(||Error("unknown operation".into()))?;
                if op.fingerprint!=*fingerprint||!result_binding.valid()||self.outcomes.contains_key(operation_id) { return fail("outcome identity/duplicate"); }
                self.outcomes.insert(operation_id.clone(),(*outcome,result_binding.clone()));
            }
            Change::Reconcile{action,authority_binding,observed_head}=>{
                if !authority_binding.valid()||!codec::hash(&observed_head.sha256) { return fail("reconciliation evidence binding"); }
                match action {
                    ReconcileAction::Outcome{operation_id,fingerprint,result_binding,outcome}=>{
                        let op=self.operations.get(operation_id).ok_or_else(||Error("unknown recovery operation".into()))?;
                        if op.fingerprint!=*fingerprint||!result_binding.valid()||*outcome==Outcome::Quarantined||self.outcomes.get(operation_id).map(|v|v.0)!=Some(Outcome::Quarantined) { return fail("reconciliation outcome scope"); }
                        self.outcomes.insert(operation_id.clone(),(*outcome,result_binding.clone()));
                    }
                    ReconcileAction::Slot{slot_id,epoch,holder,terminal_binding}=>{
                        if !terminal_binding.valid()||self.operations.iter().any(|(id,o)|&o.slot_id==slot_id&&!self.terminal(id)) { return fail("reconciliation slot unresolved/evidence"); }
                        let slot=self.slots.get_mut(slot_id).ok_or_else(||Error("unknown recovery slot".into()))?;
                        if slot.epoch!=*epoch||slot.holder!=*holder||slot.phase!=SlotPhase::Quarantined { return fail("reconciliation slot scope"); }
                        slot.phase=SlotPhase::Closed;
                    }
                }
            }
        } Ok(())
    }
}

#[derive(Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct Header {schema_version:String,authority_domain:String,layout:Vec<Identity>,limits:Limits,fixture_only:bool}
#[derive(Serialize,Deserialize)] #[serde(deny_unknown_fields)]
struct Record {schema_version:String,authority_domain:String,sequence:u64,previous_sha256:String,writer:WriterFence,change:Change}
pub(super) struct Summary { state:State }
impl Summary {
    pub(super) fn operation_state(&self,operation:&Operation)->Result<super::OriginalOperationState> {
        if self.state.operations.contains_key(&operation.operation_id) {
            self.check_operation(operation)?;
            Ok(super::OriginalOperationState::Present { effect_eligible:self.effect_eligible(operation),outcome:self.state.outcomes.get(&operation.operation_id).cloned() })
        } else {
            // The same accepted Reserve semantics are evaluated without an
            // append. This proves store/slot/event/interlock eligibility only;
            // the signed original intent is still required before Reserve.
            let mut next=self.state.clone();next.apply(&Change::Reserve{operation:operation.clone()})?;
            Ok(super::OriginalOperationState::AbsentReservable)
        }
    }
    pub(super) fn check_operation(&self,operation:&Operation)->Result<()> {
        if self.state.operations.get(&operation.operation_id)!=Some(operation) {return fail("original selected operation");} Ok(())
    }
    pub(super) fn effect_eligible(&self,operation:&Operation)->bool {
        self.check_operation(operation).is_ok() && !self.state.outcomes.contains_key(&operation.operation_id)
        && self.state.slots.get(&operation.slot_id).is_some_and(|s|s.epoch==operation.slot_epoch&&s.holder==operation.holder&&s.phase==SlotPhase::Active)
        && self.state.stores.get(&operation.store_id).is_some_and(|s|s.epoch==operation.store_epoch&&s.instance==operation.store_instance)
    }
    pub(super) fn outcome(&self,id:&str)->Option<&(Outcome,ByteBinding)>{self.state.outcomes.get(id)}
    pub(super) fn slot(&self,operation:&Operation)->Result<SlotPhase>{
        self.check_operation(operation)?;let s=self.state.slots.get(&operation.slot_id).ok_or_else(||Error("unknown selected slot".into()))?;
        if s.epoch!=operation.slot_epoch||s.holder!=operation.holder{return fail("selected slot epoch/holder");}Ok(s.phase)
    }
}
pub(super) fn verify(header_raw:&[u8],records:&[Vec<u8>],selected:&HostConfirmation,layout:&[Identity],fixture:bool)->Result<Summary> {
    let header:Header=codec::decode(header_raw)?;let limits=&header.limits;
    if header.schema_version!="lab-control-header/v1" || selected.schema_version!="lab-host-control-confirmation/v1"
        || header.authority_domain!=selected.authority_domain || !codec::identifier(&header.authority_domain)
        || header.layout!=layout || layout.first()!=Some(&selected.root) || header.fixture_only!=fixture
        || codec::digest(header_raw)!=selected.header_sha256 || !codec::identifier(&selected.writer.instance)
        || selected.writer.epoch==0 || selected.writer.epoch>codec::MAX_INTEGER
        || !codec::hash(&selected.head.sha256) || !codec::hash(&selected.predecessor.sha256)
        || !(2048..=65536).contains(&limits.max_record_bytes) || !(8..=100000).contains(&limits.max_records)
        || !(6..=16).contains(&limits.reserved_records) || limits.reserved_records>=limits.max_records
        || limits.max_total_bytes<limits.max_record_bytes*8 || limits.max_total_bytes>1024*1024*1024
        || records.len() as u64>limits.max_records {return fail("selected original control header/layout/limits");}
    let mut state=State::default();let mut head=Head{sequence:0,sha256:codec::digest(header_raw)};let mut previous=head.clone();
    let mut bytes=header_raw.len() as u64;let mut prior_writer:Option<WriterFence>=None;
    for (index,raw) in records.iter().enumerate(){
        bytes=bytes.checked_add(raw.len() as u64).ok_or_else(||Error("control byte overflow".into()))?;
        if raw.len() as u64>limits.max_record_bytes || bytes>limits.max_total_bytes{return fail("control prefix bound");}
        let record:Record=codec::decode(raw)?;
        if record.schema_version!="lab-control-record/v1" || record.authority_domain!=selected.authority_domain
            || record.sequence!=index as u64+1 || record.previous_sha256!=head.sha256
            || !codec::identifier(&record.writer.instance) || record.writer.epoch==0 || record.writer.epoch>codec::MAX_INTEGER
            || record.writer.epoch>selected.writer.epoch
            || (record.writer.epoch==selected.writer.epoch && record.writer.instance!=selected.writer.instance)
            || prior_writer.as_ref().is_some_and(|p|record.writer.epoch<p.epoch || (record.writer.epoch==p.epoch&&record.writer.instance!=p.instance))
            {return fail("control original chain/writer");}
        if let Change::Reconcile{observed_head,..}=&record.change{if observed_head!=&head{return fail("control reconciliation preimage");}}
        state.apply(&record.change)?;prior_writer=Some(record.writer);previous=head;
        head=Head{sequence:record.sequence,sha256:codec::digest(raw)};
    }
    if head!=selected.head || previous!=selected.predecessor{return fail("control original selected high-water");}Ok(Summary { state })
}
}

/// Fully enumerated original Ledger view, obtained without taking any broker
/// lock. A valid prefix is not enough: inventory must equal the selected head,
/// including refusal of an otherwise valid unacknowledged tail.
pub struct ControlOriginals {
    header: Vec<u8>, records: Vec<Vec<u8>>, layout: Vec<lab_control_store::custody::Identity>,
    inventory: Vec<(String,Identity,u64,String)>,
}
impl OriginalDirectory {
    pub fn control_originals(&self, selected: &HostConfirmation) -> Result<ControlOriginals> {
        self.guard()?;
        let root = self.chain.last().unwrap(); let rid = self.selected.ancestors.last().unwrap();
        let cid = |f:&File|lab_control_store::custody::Identity::of(f).map_err(|_|Error("CONTROL_IDENTITY"));
        require(cid(root)? == selected.root && selected.head.sequence <= 100000, "CONTROL_PHYSICAL_ROOT_BOUND")?;
        let mut expected_names=vec!["header.json".to_string(),"locks".into(),"records".into()];
        expected_names.extend(self.children.keys().cloned());expected_names.sort();
        require(roots::names(root,20)?==expected_names,"CONTROL_ROOT_INVENTORY")?;
        for(name,expected)in &self.children {
            let child=roots::open_child(root,name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
            require(Identity::observe(&child)?==*expected,"CONTROL_CHILD_ATTACHMENT")?;
            roots::owned_dir(&child,rid.uid,rid.mount_id)?;
        }
        let records = roots::open_child(root,"records",libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
        let locks = roots::open_child(root,"locks",libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
        roots::owned_dir(&records,rid.uid,rid.mount_id)?;roots::owned_dir(&locks,rid.uid,rid.mount_id)?;
        let mut layout = vec![cid(root)?,cid(&records)?,cid(&locks)?];
        let lock_names = ["00-source-slot","01-publication","02-replay","03-native","04-journal"];
        require(roots::names(&locks,6)? == lock_names,"CONTROL_LOCK_INVENTORY")?;
        let mut inventory = vec![(".".into(),rid.clone(),0,String::new()),
            ("records".into(),Identity::observe(&records)?,0,String::new()),
            ("locks".into(),Identity::observe(&locks)?,0,String::new())];
        for name in lock_names {
            let raw=read_file(&locks,name,rid,65536)?;
            let f=roots::open_child(&locks,name,libc::O_RDONLY,0,true)?;
            layout.push(cid(&f)?);inventory.push((format!("locks/{name}"),Identity::observe(&f)?,raw.len() as u64,roots::hash(&raw)));
        }
        let header=read_file(root,"header.json",rid,65536)?;
        let hf=roots::open_child(root,"header.json",libc::O_RDONLY,0,true)?;
        inventory.push(("header.json".into(),Identity::observe(&hf)?,header.len() as u64,roots::hash(&header)));
        let names=roots::names(&records,100001)?;
        require(names.len() as u64 == selected.head.sequence,"CONTROL_UNSELECTED_OR_MISSING_TAIL")?;
        let mut raws=Vec::new();let mut total=header.len() as u64;
        for (index,name) in names.iter().enumerate() {
            require(*name==format!("{:016}.json",index+1),"CONTROL_RECORD_ORDER")?;
            let raw=read_file(&records,name,rid,65536)?;
            total=total.checked_add(raw.len() as u64).ok_or(Error("CONTROL_TOTAL_OVERFLOW"))?;
            require(total<=1024*1024*1024,"CONTROL_TOTAL_BOUND")?;
            let f=roots::open_child(&records,name,libc::O_RDONLY,0,true)?;
            inventory.push((format!("records/{name}"),Identity::observe(&f)?,raw.len() as u64,roots::hash(&raw)));raws.push(raw);
        }
        require(roots::names(&records,100001)?==names,"CONTROL_INVENTORY_CHANGED")?;
        self.guard()?;
        for(name,id)in &self.children {inventory.push((name.clone(),id.clone(),0,String::new()));}
        let value=ControlOriginals{header,records:raws,layout,inventory};
        value.verify(selected,self.selected.domain)?;Ok(value)
    }
    pub fn recheck_control(&self, original:&ControlOriginals, selected:&HostConfirmation)->Result<()> {
        let again=self.control_originals(selected)?;
        require(original.header==again.header && original.records==again.records && original.layout==again.layout
            && original.inventory==again.inventory,"CONTROL_ORIGINALS_CHANGED")
    }
}
impl ControlOriginals {
    pub(crate) fn slot_transition(&self,selected:&HostConfirmation,domain:Domain,operation:&Operation,root_id:&str)->Result<(lab_control_store::ledger::SlotPhase,Binding,lab_control_store::ledger::Change)>{
        use lab_control_store::ledger::{Change,ReconcileAction};
        let phase=self.verify(selected,domain)?.slot(operation).map_err(|_|Error("SELECTED_SLOT"))?;
        for(index,raw)in self.records.iter().enumerate().rev(){
            let v:Value=decode(raw,65536)?;let c:Change=serde_json::from_value(v["change"].clone()).map_err(|_|Error("SELECTED_SLOT_RECORD"))?;
            let matches=match &c{
                Change::SlotEpoch{slot_id,new_epoch,holder,..}=>slot_id==&operation.slot_id&&*new_epoch==operation.slot_epoch&&holder==&operation.holder,
                Change::SlotState{slot_id,epoch,holder,..}|Change::Reconcile{action:ReconcileAction::Slot{slot_id,epoch,holder,..},..}=>slot_id==&operation.slot_id&&*epoch==operation.slot_epoch&&holder==&operation.holder,_=>false};
            if matches{return Ok((phase,bound(root_id,&format!("records/{:016}.json",index+1),raw)?,c));}
        }Err(Error("SELECTED_SLOT_RECORD_MISSING"))
    }

    /// An earlier independently authenticated checkpoint is an exact physical
    /// prefix with a writer fence; it is not reconstructed from a row writer.
    fn attests(&self,old:&HostConfirmation,current:&HostConfirmation)->Result<()> {
        require(old.schema_version=="lab-host-control-confirmation/v1"&&old.root==current.root
            &&old.authority_domain==current.authority_domain&&old.header_sha256==current.header_sha256
            &&old.head.sequence<=current.head.sequence&&old.writer.epoch>0&&old.writer.epoch<=current.writer.epoch
            &&ident(&old.writer.instance)&&(old.writer.epoch!=current.writer.epoch||old.writer.instance==current.writer.instance),"PREFIX_ADMISSION_CONTROL_LINEAGE")?;
        let at=|n:u64|->Result<String>{if n==0{Ok(roots::hash(&self.header))}else{Ok(roots::hash(self.records.get(n as usize-1).ok_or(Error("PREFIX_ADMISSION_HEAD"))?))}};
        require(at(old.head.sequence)?==old.head.sha256&&old.predecessor.sequence==old.head.sequence.saturating_sub(1)
            &&at(old.predecessor.sequence)?==old.predecessor.sha256,"PREFIX_ADMISSION_CONTROL_HEAD")?;
        let writer=|n:u64|->Result<WriterFence>{let v:Value=decode(self.records.get(n as usize-1).ok_or(Error("PREFIX_ADMISSION_HEAD"))?,65536)?;serde_json::from_value(v["writer"].clone()).map_err(|_|Error("PREFIX_ADMISSION_WRITER"))};
        if old.head.sequence>0{let w=writer(old.head.sequence)?;require(w.epoch<=old.writer.epoch&&(w.epoch!=old.writer.epoch||w.instance==old.writer.instance),"PREFIX_ADMISSION_PHYSICAL_FENCE")?;}
        if old.head.sequence<current.head.sequence{let w=writer(old.head.sequence+1)?;require(w.epoch>=old.writer.epoch&&(w.epoch!=old.writer.epoch||w.instance==old.writer.instance),"PREFIX_ADMISSION_SUCCESSOR_FENCE")?;}
        Ok(())
    }

    fn verify(&self, selected:&HostConfirmation,domain:Domain)->Result<native_control::Summary> {
        native_control::verify(&self.header,&self.records,selected,&self.layout,domain==Domain::Fixture)
            .map_err(|_|Error("ORIGINAL_CONTROL_SEMANTICS"))
    }
    pub fn check_operation(&self,selected:&HostConfirmation,domain:Domain,operation:&Operation)->Result<bool>{
        let summary=self.verify(selected,domain)?;summary.check_operation(operation).map_err(|_|Error("ORIGINAL_OPERATION_JOIN"))?;
        Ok(summary.effect_eligible(operation))
    }
}

#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct ControlCasRequest {
    pub schema_version:String,pub service_selection_binding:Binding,
    pub prior:HostConfirmation,pub desired:HostConfirmation,pub recipient:Caller,
    pub channel_binding:Binding,pub challenge:String,pub not_before:u64,pub expires_at:u64,
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct ControlCasProof {
    pub schema_version:String,pub request:ControlCasRequest,pub ordinal:u64,
    pub previous_witness_sha256:String,pub signer_enrollment_binding:Binding,pub result:String,
}
/// This separate witness has no Ledger Held and cannot append a Ledger event.
/// Its current ordinal/head are selected from independently retained custody;
/// valid extra witness bytes are an unconfirmed tail, never a new high-water.
pub struct ControlWitness<'a> {
    hold:&'a Exclusive<'a>,control:&'a OriginalDirectory,signer:&'a SelectedSigner,key:SigningKey,
    service_binding:Binding,recipient:Caller,channel:Binding,domain:Domain,
    current:HostConfirmation,ordinal:u64,witness_sha:String,latest:Option<(ControlCasRequest,Vec<u8>)>,poisoned:bool,
}
impl<'a> ControlWitness<'a> {
    pub(crate) fn open(hold:&'a Exclusive<'a>, control:&'a OriginalDirectory, signer:&'a SelectedSigner,key:SigningKey,
        service_binding:Binding,recipient:Caller,channel:Binding,genesis:HostConfirmation,
        selected:HostConfirmation,selected_ordinal:u64,selected_witness_sha:String,
        all_broker_roots:&[Identity])->Result<Self>{
        hold.validate()?;control.guard()?;
        require(service_binding.valid()&&recipient.valid()&&channel.valid()&&selected_ordinal<=100000
            && roots::digest(&selected_witness_sha)&&signer.selection.purpose=="control-confirmation"
            && signer.key==key.verifying_key()&&signer.domain()==hold.root().selection().domain
            && control.selected.domain==signer.domain()&&all_broker_roots.iter().all(|id|
                id.device!=hold.root().identity().device||id.inode!=hold.root().identity().inode)
            && !(selected.root.device==hold.root().identity().device&&selected.root.inode==hold.root().identity().inode),
            "CONTROL_WITNESS_CUSTODY")?;
        let names=roots::names(hold.directory(),100001)?;
        require(names.len() as u64==selected_ordinal,"CONTROL_WITNESS_UNSELECTED_TAIL")?;
        let mut current=genesis.clone();let mut sha=roots::hash(&encode(&genesis)?);let mut latest=None;
        for (index,name) in names.iter().enumerate(){
            require(*name==format!("control-{:016}.json",index+1),"CONTROL_WITNESS_ORDER")?;
            let raw=read_file(hold.directory(),name,hold.root().identity(),quota::MAX_PACKET)?;
            let proof:ControlCasProof=signer.verify(&raw)?;
            require(proof.schema_version=="lab-broker-control-cas-proof/v1"&&proof.ordinal==index as u64+1
                &&proof.previous_witness_sha256==sha&&proof.signer_enrollment_binding==*signer.binding()
                &&proof.result=="confirmed"&&Self::continuity(&current,&proof.request.prior),"CONTROL_WITNESS_CHAIN")?;
            Self::validate_request(&proof.request,&proof.request.service_selection_binding,&proof.request.recipient,
                &proof.request.channel_binding,proof.request.not_before)?;
            current=proof.request.desired.clone();sha=roots::hash(&raw);latest=Some((proof.request,raw));
        }
        require(Self::continuity(&current,&selected)&&sha==selected_witness_sha,"CONTROL_WITNESS_SELECTED_HEAD")?;
        current=selected;
        Ok(Self{hold,control,signer,key,service_binding,recipient,channel,domain:signer.domain(),current,
            ordinal:selected_ordinal,witness_sha:sha,latest,poisoned:false})
    }
    fn continuity(old:&HostConfirmation,current:&HostConfirmation)->bool {
        old.schema_version==current.schema_version && old.authority_domain==current.authority_domain
        && old.root==current.root && old.header_sha256==current.header_sha256 && old.head==current.head
        && old.predecessor==current.predecessor && current.writer.epoch>=old.writer.epoch
        && current.writer.epoch<=i64::MAX as u64 && ident(&current.writer.instance)
        && (current.writer.epoch>old.writer.epoch || current.writer.instance==old.writer.instance)
    }
    fn validate_request(q:&ControlCasRequest,service:&Binding,peer:&Caller,channel:&Binding,now:u64)->Result<()> {
        require(service.valid()&&peer.valid()&&channel.valid()
            &&q.schema_version=="lab-broker-control-cas-request/v1"&&q.service_selection_binding==*service
            &&q.recipient==*peer&&q.channel_binding==*channel&&roots::digest(&q.challenge)
            &&q.prior.schema_version=="lab-host-control-confirmation/v1"&&q.desired.schema_version==q.prior.schema_version
            &&q.desired.authority_domain==q.prior.authority_domain&&q.desired.root==q.prior.root
            &&q.desired.header_sha256==q.prior.header_sha256&&q.desired.writer==q.prior.writer
            &&q.desired.predecessor==q.prior.head&&q.prior.head.sequence<100000
            &&q.desired.head.sequence==q.prior.head.sequence+1,"CONTROL_CAS_SCOPE")?;
        interval(q.not_before,q.expires_at,now)
    }
    pub(crate) fn compare_and_swap(&mut self,q:&ControlCasRequest,peer:&Caller)->Result<Vec<u8>> {
        self.hold.validate()?;require(!self.poisoned&&*peer==self.recipient,"CONTROL_WITNESS_UNCERTAIN_PEER")?;
        Self::validate_request(q,&self.service_binding,peer,&self.channel,now_seconds()?)?;
        if self.latest.as_ref().is_some_and(|(old,_)|old==q){return Ok(self.latest.as_ref().unwrap().1.clone());}
        require(q.prior==self.current&&self.ordinal<100000,"CONTROL_CAS_PREIMAGE")?;
        let originals=self.control.control_originals(&q.desired)?;
        // The proposed physical tree must extend the independently retained old
        // head exactly once; an arbitrary desired head cannot become authority.
        native_control::verify(&originals.header,&originals.records[..originals.records.len()-1],&q.prior,
            &originals.layout,self.domain==Domain::Fixture).map_err(|_|Error("CONTROL_CAS_OLD_PREFIX"))?;
        let proof=ControlCasProof{schema_version:"lab-broker-control-cas-proof/v1".into(),request:q.clone(),
            ordinal:self.ordinal+1,previous_witness_sha256:self.witness_sha.clone(),
            signer_enrollment_binding:self.signer.binding().clone(),result:"confirmed".into()};
        interval(q.not_before,q.expires_at,now_seconds()?)?;
        let raw=self.signer.sign(&self.key,&proof)?;
        self.control.recheck_control(&originals,&q.desired)?;
        interval(q.not_before,q.expires_at,now_seconds()?)?;
        self.poisoned=true;
        put_file(self.hold.directory(),&format!("control-{:016}.json",self.ordinal+1),self.hold.root().identity(),&raw,quota::MAX_PACKET)?;
        self.current=q.desired.clone();self.ordinal+=1;self.witness_sha=roots::hash(&raw);
        self.latest=Some((q.clone(),raw.clone()));self.poisoned=false;
        // A late return never erases a durable CAS. Fresh current inspection
        // can disclose the original; it does not redispatch or extend expiry.
        interval(q.not_before,q.expires_at,now_seconds()?)?;Ok(raw)
    }
    /// A fresh authenticated inspection returns the exact historical proof as
    /// an original, wrapped in a current query response. It does not re-CAS.
    pub(crate) fn inspect(&self,query:&ControlInspectionRequest,peer:&Caller)->Result<Vec<u8>>{
        self.hold.validate()?;require(!self.poisoned,"CONTROL_WITNESS_UNCERTAIN")?;
        require(query.schema_version=="lab-broker-control-inspection-request/v1"&&query.service_selection_binding==self.service_binding
            &&query.recipient==self.recipient&&query.recipient==*peer&&query.channel_binding==self.channel
            &&roots::digest(&query.challenge),"CONTROL_INSPECTION_SCOPE")?;
        interval(query.not_before,query.expires_at,now_seconds()?)?;
        let originals=self.control.control_originals(&self.current)?;
        let proof=ControlInspectionProof{schema_version:"lab-broker-control-inspection/v1".into(),query:query.clone(),
            confirmation:self.current.clone(),ordinal:self.ordinal,witness_sha256:self.witness_sha.clone(),
            original_proof_binding:self.latest.as_ref().map(|(_,raw)|bound(&self.hold.root().selection().root_id,
                &format!("control-{:016}.json",self.ordinal),raw)).transpose()?};
        interval(query.not_before,query.expires_at,now_seconds()?)?;
        let raw=self.signer.sign(&self.key,&proof)?;self.control.recheck_control(&originals,&self.current)?;
        interval(query.not_before,query.expires_at,now_seconds()?)?;Ok(raw)
    }
    pub(crate) fn read_original(&self,q:&ControlOriginalRequest,peer:&Caller)->Result<Vec<u8>> {
        require(q.schema_version=="lab-broker-control-original-request/v1","CONTROL_ORIGINAL_VERB")?;
        // A current query is authenticated before disclosing the historical
        // original; the original is returned byte-identically, not re-signed.
        self.inspect(&q.query,peer)?;
        let raw=&self.latest.as_ref().ok_or(Error("CONTROL_NO_ORIGINAL"))?.1;
        let binding=bound(&self.hold.root().selection().root_id,&format!("control-{:016}.json",self.ordinal),raw)?;
        require(q.original_binding==binding,"CONTROL_ORIGINAL_SELECTION")?;
        let retained=read_file(self.hold.directory(),&format!("control-{:016}.json",self.ordinal),self.hold.root().identity(),quota::MAX_PACKET)?;
        verify_bytes(&retained,&binding)?;interval(q.query.not_before,q.query.expires_at,now_seconds()?)?;Ok(retained)
    }
    pub fn confirmation(&self)->&HostConfirmation{&self.current}
    pub(crate) fn serve_one(&mut self,channel:&Channel)->Result<()> {
        require(channel.selection().peer==self.recipient&&channel.selection().channel_binding==self.channel,"CONTROL_SERVICE_CHANNEL")?;
        let raw=channel.receive()?;
        let value:Value=decode(&raw,quota::MAX_PACKET)?;
        let response=match value.get("schema_version").and_then(Value::as_str){
            Some("lab-broker-control-cas-request/v1")=>self.compare_and_swap(&decode(&raw,quota::MAX_PACKET)?,&channel.selection().peer)?,
            Some("lab-broker-control-inspection-request/v1")=>self.inspect(&decode(&raw,quota::MAX_PACKET)?,&channel.selection().peer)?,
            Some("lab-broker-control-original-request/v1")=>self.read_original(&decode(&raw,quota::MAX_PACKET)?,&channel.selection().peer)?,
            _=>return Err(Error("CONTROL_SERVICE_VERB")),
        };channel.send(&response)
    }
}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct ControlInspectionRequest {pub schema_version:String,pub service_selection_binding:Binding,pub recipient:Caller,
    pub channel_binding:Binding,pub challenge:String,pub not_before:u64,pub expires_at:u64}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct ControlInspectionProof {pub schema_version:String,pub query:ControlInspectionRequest,pub confirmation:HostConfirmation,
    pub ordinal:u64,pub witness_sha256:String,pub original_proof_binding:Option<Binding>}
#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)] #[serde(deny_unknown_fields)]
pub struct ControlOriginalRequest {pub schema_version:String,pub query:ControlInspectionRequest,pub original_binding:Binding}

#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]
#[serde(tag="state",rename_all="snake_case",deny_unknown_fields)]
pub enum OriginalOperationState {
    Uncertain,
    AbsentReservable,
    Present {effect_eligible:bool,outcome:Option<(lab_control_store::ledger::Outcome,lab_control_store::ledger::ByteBinding)>},
}

pub(crate) fn capture_owned_directory(hold:&Exclusive<'_>,name:&str,max_files:usize,max_bytes:u64)->Result<BTreeMap<String,Binding>>{
    hold.validate()?;roots::name(name)?;require(max_files<=64&&max_bytes<=quota::MAX_RECORD,"CAPTURE_BOUND")?;
    let dir=roots::open_child(hold.directory(),name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
    let id=roots::owned_dir(&dir,hold.root().identity().uid,hold.root().identity().mount_id)?;
    let names=roots::names(&dir,max_files+1)?;require(names.len()<=max_files,"CAPTURE_COUNT")?;
    let mut result=BTreeMap::new();
    for leaf in &names{let raw=read_file(&dir,leaf,hold.root().identity(),max_bytes)?;
        result.insert(leaf.clone(),bound(&hold.root().selection().root_id,&format!("{name}/{leaf}"),&raw)?);}
    require(roots::names(&dir,max_files+1)?==names,"CAPTURE_INVENTORY_DRIFT")?;
    let named=roots::open_child(hold.directory(),name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
    require(Identity::observe(&named)?==id,"CAPTURE_ATTACHMENT_DRIFT")?;
    for(leaf,binding)in &result{verify_bytes(&read_file(&dir,leaf,hold.root().identity(),max_bytes)?,binding)?;}
    hold.validate()?;Ok(result)
}
pub(crate) fn read_owned(hold:&Exclusive<'_>,binding:&Binding,limit:u64)->Result<Vec<u8>>{
    hold.validate()?;require(binding.root_id==hold.root().selection().root_id&&binding.valid()&&binding.size_bytes<=limit,"OWNED_READ_SELECTION")?;
    let parts=roots::parts(&binding.relative_path)?;let mut dir=hold.directory().try_clone()?;
    for part in &parts[..parts.len()-1]{dir=roots::open_child(&dir,part,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;roots::owned_dir(&dir,hold.root().identity().uid,hold.root().identity().mount_id)?;}
    let raw=read_file(&dir,parts.last().unwrap(),hold.root().identity(),limit)?;verify_bytes(&raw,binding)?;hold.validate()?;Ok(raw)
}
/// Finite known-record sizing before any sequence intent or Stage effect. The
/// input is a size model only: it cannot grant authority or create a snapshot.
impl ReceiptJournal<'_> {
    pub(crate) fn preflight(&self,frame:&wire::Frame,raw:&[u8],ledger:&HostConfirmation,
        records:&BTreeMap<String,Vec<u8>>,phase:&str,response_issuer:&str,prefix_issuer:&str,prefix_signer:&Binding)->Result<()> {
        self.guard()?;require(!self.pending&&records.len()+3<=quota::SEQUENCE_FILES as usize-2,"PREFLIGHT_COUNT")?;
        let ordinal=self.head.ordinal.checked_add(1).ok_or(Error("SEQUENCE_OVERFLOW"))?;
        let intent=RequestIntent{current_admission:self.current_admission.clone(),schema_version:"lab-broker-sequence-intent/v1".into(),scope_sha256:self.scope.digest()?,ordinal,previous:self.head.clone(),
            operation_id:self.scope.operation.operation_id.clone(),sequence:frame.request()["sequence"].as_u64().ok_or(Error("SEQUENCE"))?,
            wire_sha256:frame.wire_digest().into(),original_fingerprint:self.scope.operation.fingerprint.clone(),verb:frame.request()["verb"].as_str().ok_or(Error("VERB"))?.into(),ledger_confirmation:ledger.clone()};
        let prefix=if self.unaccounted.is_empty(){format!("sequence-{ordinal:016}")}else{format!("recovery-{ordinal:016}")};let mut originals=BTreeMap::new();
        for(name,bytes)in [("intent.json",encode(&intent)?),("frame.json",raw.into())].into_iter().chain(records.iter().map(|(n,r)|(n.as_str(),r.clone()))){
            self.limits.record(&bytes)?;require(!originals.contains_key(name),"PREFLIGHT_DUPLICATE_RECORD")?;
            originals.insert(name.into(),bound(&self.scope.receipt_root_id,&format!("{prefix}/{name}"),&bytes)?);
        }
        let result=Binding{kind:"evidence".into(),root_id:self.scope.receipt_root_id.clone(),relative_path:format!("{prefix}/publication-member-receipt.json"),sha256:"f".repeat(64),size_bytes:self.limits.max_record_bytes};
        let response=encode(&json!({"issuer_ref":response_issuer,"payload":{"schema_version":"lab-completion-broker-response/v1","request_digest":frame.wire_digest(),"operation_id":self.scope.operation.operation_id,"sequence":intent.sequence,"durable_phase":phase,"status":"REFUSED","error":"WITNESS_CONFIRMATION_UNCERTAIN","result_binding":result},"signature":"f".repeat(128)}))?;
        self.limits.response(&response)?;self.limits.record(&response)?;
        originals.insert("response.json".into(),bound(&self.scope.receipt_root_id,&format!("{prefix}/response.json"),&response)?);
        let entry=SequenceEntry{schema_version:"lab-broker-sequence-entry/v1".into(),intent:intent.clone(),originals,phase:phase.into(),status:"REFUSED".into()};
        let raw_entry=encode(&entry)?;self.limits.record(&raw_entry)?;
        let request=PrefixRequest{current_admission:intent.current_admission.clone(),schema_version:"lab-broker-prefix-cas-request/v1".into(),scope:self.scope.clone(),prior:self.head.clone(),next:PrefixHead{ordinal,entry_sha256:roots::hash(&raw_entry)},entry_binding:bound(&self.scope.receipt_root_id,&format!("{prefix}/entry.json"),&raw_entry)?,sequence:intent.sequence,wire_sha256:intent.wire_sha256,ledger_confirmation:ledger.clone(),challenge:"f".repeat(64),not_before:i64::MAX as u64-1,expires_at:i64::MAX as u64};
        let confirmation=encode(&json!({"issuer_ref":prefix_issuer,"payload":PrefixConfirmation{schema_version:"lab-broker-prefix-confirmation/v1".into(),request,signer_enrollment_binding:prefix_signer.clone(),result:"confirmed".into()},"signature":"f".repeat(128)}))?;
        self.limits.record(&confirmation)?;require(confirmation.len() as u64<=quota::MAX_PACKET,"PREFLIGHT_PREFIX_PACKET")?;Ok(())
    }
}

fn owned_parent(hold:&Exclusive<'_>,path:&str)->Result<(File,String)>{
    hold.validate()?;let parts=roots::parts(path)?;let mut dir=hold.directory().try_clone()?;
    for name in &parts[..parts.len()-1]{dir=roots::open_child(&dir,name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;roots::owned_dir(&dir,hold.root().identity().uid,hold.root().identity().mount_id)?;}
    Ok((dir,parts.last().unwrap().to_string()))
}
pub(crate) fn verify_owned_preimage(hold:&Exclusive<'_>,path:&str,preimage:Option<&Binding>,identity:Option<&Identity>,max:u64)->Result<()> {
    let(dir,leaf)=owned_parent(hold,path)?;let names=roots::names(&dir,100001)?;
    match(preimage,identity){
        (None,None)=>require(!names.contains(&leaf),"DERIVED_ABSENT_PREIMAGE"),
        (Some(b),Some(id))=>{require(b.root_id==hold.root().selection().root_id&&b.relative_path==path,"DERIVED_PREIMAGE_LOCATOR")?;
            let f=roots::open_child(&dir,&leaf,libc::O_RDONLY,0,true)?;require(roots::owned_file(&f,hold.root().identity().uid,hold.root().identity().mount_id)?==*id,"DERIVED_PREIMAGE_IDENTITY")?;
            verify_bytes(&read_file(&dir,&leaf,hold.root().identity(),max)?,b)},
        _=>Err(Error("DERIVED_PREIMAGE_PAIR")),
    }
}
pub(crate) fn replace_owned_derived(hold:&Exclusive<'_>,path:&str,temp:&str,preimage:Option<&Binding>,identity:Option<&Identity>,raw:&[u8],max:u64)->Result<Binding>{
    use std::ffi::CString;
    require(raw.len() as u64<=max&&max<=quota::MAX_RECORD,"DERIVED_CONTENT_BOUND")?;
    verify_owned_preimage(hold,path,preimage,identity,max)?;let(dir,leaf)=owned_parent(hold,path)?;
    require(temp!=leaf,"DERIVED_TEMP_ALIAS")?;put_file(&dir,temp,hold.root().identity(),raw,max)?;
    verify_owned_preimage(hold,path,preimage,identity,max)?;
    let tmp=CString::new(temp).map_err(|_|Error("DERIVED_NAME"))?;let name=CString::new(leaf.as_bytes()).map_err(|_|Error("DERIVED_NAME"))?;
    let flags=if preimage.is_none(){libc::RENAME_NOREPLACE}else{0};
    let rc=unsafe{libc::syscall(libc::SYS_renameat2,dir.as_raw_fd(),tmp.as_ptr(),dir.as_raw_fd(),name.as_ptr(),flags)};
    require(rc==0,"DERIVED_RENAME_UNCERTAIN")?;dir.sync_all()?;hold.validate()?;
    let b=bound(&hold.root().selection().root_id,path,raw)?;verify_bytes(&read_file(&dir,&leaf,hold.root().identity(),max)?,&b)?;Ok(b)
}
pub(crate) fn owned_inventory(hold:&Exclusive<'_>,maximum_files:u64,maximum_bytes:u64)->Result<BTreeMap<String,(Identity,u64,String)>>{
    fn walk(dir:&File,id:&Identity,prefix:&str,depth:u32,rows:&mut BTreeMap<String,(Identity,u64,String)>,files:u64,total:&mut u64,max:u64)->Result<()>{
        require(depth<=32,"INVENTORY_DEPTH")?;
        for leaf in roots::names(dir,files as usize+1)?{
            require((rows.len() as u64)<files,"INVENTORY_FILES")?;
            let path=if prefix.is_empty(){leaf.clone()}else{format!("{prefix}/{leaf}")};let f=roots::open_child(dir,&leaf,libc::O_RDONLY,0,true)?;
            let identity=Identity::observe(&f)?;
            if f.metadata()?.is_dir(){roots::owned_dir(&f,id.uid,id.mount_id)?;rows.insert(path.clone(),(identity,0,String::new()));walk(&f,id,&path,depth+1,rows,files,total,max)?;}
            else{use sha2::{Digest,Sha256};let mut f=f;let before=f.metadata()?;let original=roots::owned_file(&f,id.uid,id.mount_id)?;
                require(before.len()<=1_073_741_824,"INVENTORY_MEMBER_BYTES")?;
                *total=total.checked_add(before.len()).ok_or(Error("INVENTORY_OVERFLOW"))?;require(*total<=max,"INVENTORY_BYTES")?;
                let mut hash=Sha256::new();let mut read=0u64;let mut buffer=[0u8;32768];
                loop{let n=f.read(&mut buffer)?;if n==0{break;}read=read.checked_add(n as u64).ok_or(Error("INVENTORY_OVERFLOW"))?;require(read<=before.len(),"INVENTORY_MEMBER_CHANGED")?;hash.update(&buffer[..n]);}
                let after=f.metadata()?;let named=roots::open_child(dir,&leaf,libc::O_RDONLY,0,true)?;
                require(read==before.len()&&before.len()==after.len()&&before.mtime()==after.mtime()&&before.mtime_nsec()==after.mtime_nsec()
                    &&before.ctime()==after.ctime()&&before.ctime_nsec()==after.ctime_nsec()&&roots::owned_file(&named,id.uid,id.mount_id)?==original,"INVENTORY_MEMBER_CHANGED")?;
                rows.insert(path,(identity,read,wire::hex(&hash.finalize())));}
        }Ok(())
    }
    require(maximum_files<=100000&&maximum_bytes<=1<<40,"INVENTORY_LIMITS")?;hold.validate()?;
    let mut rows=BTreeMap::new();walk(hold.directory(),hold.root().identity(),"",0,&mut rows,maximum_files,&mut 0,maximum_bytes)?;hold.validate()?;Ok(rows)
}
pub(crate) fn owned_inventory_digest(hold:&Exclusive<'_>,maximum_files:u64,maximum_bytes:u64)->Result<String>{
    Ok(roots::hash(&encode(&owned_inventory(hold,maximum_files,maximum_bytes)?)?))
}

/// Conservative shared-root accounting. Only the exact live Stage identity is
/// exempt from orphan charging. Every other retained top-level object, including
/// old generations and pointer records, consumes retained/orphan capacity; this
/// does not label it deletable or prove its semantic lifecycle. Unreadable,
/// aliased or unbounded inventory refuses before allocation.
pub(crate) fn payload_usage(hold:&Exclusive<'_>,limits:&quota::Limits,active:Option<&members::Snapshot>)->Result<quota::Usage>{
    limits.validate()?;
    let rows=owned_inventory(hold,limits.max_retained_files,limits.max_retained_bytes)?;
    let mut usage=quota::Usage::default();
    let active_name=if let Some(s)=active{
        require(s.root_id==hold.root().selection().root_id
            &&rows.get(&s.stage_name).is_some_and(|r|r.0==s.stage_identity&&r.1==0&&r.2.is_empty()),"ACTIVE_STAGE_INVENTORY")?;
        Some(s.stage_name.as_str())
    }else{None};
    for(path,(_,size,digest))in &rows{
        usage.retained_inodes=usage.retained_inodes.checked_add(1).ok_or(Error("QUOTA_OVERFLOW"))?;
        usage.retained_bytes=usage.retained_bytes.checked_add(*size).ok_or(Error("QUOTA_OVERFLOW"))?;
        let top=path.split('/').next().ok_or(Error("PAYLOAD_INVENTORY_PATH"))?;
        if !path.contains('/'){
            // All retained directories consume the shared stage/generation
            // count; a regular pointer is still charged as a retained orphan.
            if digest.is_empty(){usage.stage_count=usage.stage_count.checked_add(1).ok_or(Error("QUOTA_OVERFLOW"))?;}
            if Some(top)!=active_name{usage.orphan_count=usage.orphan_count.checked_add(1).ok_or(Error("QUOTA_OVERFLOW"))?;}
        }
        if Some(top)!=active_name{usage.orphan_bytes=usage.orphan_bytes.checked_add(*size).ok_or(Error("QUOTA_OVERFLOW"))?;}
    }
    if let Some(s)=active{usage.member_count=s.members.len() as u64;
        usage.stage_bytes=s.members.values().try_fold(0u64,|n,m|n.checked_add(m.full_length).ok_or(Error("QUOTA_OVERFLOW")))?;}
    require(rows==owned_inventory(hold,limits.max_retained_files,limits.max_retained_bytes)?,"PAYLOAD_INVENTORY_CHANGED")?;
    Ok(usage)
}

/// Bounded original journal-table reader. Separate from the small sequence
/// directory capture: its larger count is explicitly selected by the original
/// native header and never widens broker frame/response/record wire bounds.
pub(crate) fn capture_original_table(hold:&Exclusive<'_>,path:&str,count:usize,per_record:u64,total_bound:u64)->Result<BTreeMap<String,Binding>>{
 require(count<=100000&&per_record<=65536&&total_bound<=1024*1024*1024,"ORIGINAL_TABLE_BOUND")?;
 hold.validate()?;let mut dir=hold.directory().try_clone()?;
 for part in roots::parts(path)? {dir=roots::open_child(&dir,part,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;roots::owned_dir(&dir,hold.root().identity().uid,hold.root().identity().mount_id)?;}
 let identity=Identity::observe(&dir)?;let names=roots::names(&dir,count+1)?;require(names.len()<=count,"ORIGINAL_TABLE_COUNT")?;
 let mut rows=BTreeMap::new();let mut total=0u64;
 for name in &names{let raw=read_file(&dir,name,hold.root().identity(),per_record)?;total=total.checked_add(raw.len() as u64).ok_or(Error("ORIGINAL_TABLE_TOTAL"))?;
  require(total<=total_bound,"ORIGINAL_TABLE_TOTAL")?;rows.insert(name.clone(),bound(&hold.root().selection().root_id,&format!("{path}/{name}"),&raw)?);}
 require(roots::names(&dir,count+1)?==names,"ORIGINAL_TABLE_CHANGED")?;
 let mut attached=hold.directory().try_clone()?;for part in roots::parts(path)?{attached=roots::open_child(&attached,part,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;}
 require(Identity::observe(&attached)?==identity,"ORIGINAL_TABLE_ATTACHMENT")?;hold.validate()?;Ok(rows)
}
pub(crate) fn verify_directory_layout(hold:&Exclusive<'_>,path:&str,expected:&Identity,names:&[&str])->Result<()> {
 hold.validate()?;let mut dir=hold.directory().try_clone()?;for part in if path.is_empty(){Vec::new()}else{roots::parts(path)?}{dir=roots::open_child(&dir,part,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;roots::owned_dir(&dir,hold.root().identity().uid,hold.root().identity().mount_id)?;}
 require(Identity::observe(&dir)?==*expected&&roots::names(&dir,names.len()+1)?==names,"SELECTED_DIRECTORY_LAYOUT")?;hold.validate()
}
pub(crate) fn historical_control_record(hold:&Exclusive<'_>,confirmation:&HostConfirmation)->Result<Vec<u8>>{
 hold.validate()?;require(hold.root().identity().device==confirmation.root.device&&hold.root().identity().inode==confirmation.root.inode,"HISTORICAL_CONTROL_PHYSICAL_ROOT")?;
 let dir=roots::open_child(hold.directory(),"records",libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;roots::owned_dir(&dir,hold.root().identity().uid,hold.root().identity().mount_id)?;
 let raw=read_file(&dir,&format!("{:016}.json",confirmation.head.sequence),hold.root().identity(),65536)?;
 require(roots::hash(&raw)==confirmation.head.sha256,"HISTORICAL_CONTROL_ORIGINAL_HASH")?;hold.validate()?;Ok(raw)
}

/// Reads only the immediate physical successor already covered by the current
/// independently selected Ledger prefix. No newer head is adopted here.
pub(crate) fn historical_control_successor(hold:&Exclusive<'_>,old:&HostConfirmation,current:&HostConfirmation)->Result<Option<Vec<u8>>>{
 hold.validate()?;require(old.root==current.root&&old.header_sha256==current.header_sha256&&old.authority_domain==current.authority_domain
  &&hold.root().identity().device==current.root.device&&hold.root().identity().inode==current.root.inode&&old.head.sequence<=current.head.sequence,"HISTORICAL_SUCCESSOR_SCOPE")?;
 if old.head.sequence==current.head.sequence{return Ok(None)}
 let dir=roots::open_child(hold.directory(),"records",libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
 roots::owned_dir(&dir,hold.root().identity().uid,hold.root().identity().mount_id)?;
 let raw=read_file(&dir,&format!("{:016}.json",old.head.sequence+1),hold.root().identity(),65536)?;hold.validate()?;Ok(Some(raw))
}

/// Only a structural uncertainty observation; never a consumption/absence proof.
pub(crate) fn receipt_structure_uncertain(hold:&Exclusive<'_>,scope:&PrefixScope,limits:&quota::Limits,
    witness:&SelectedSigner,response:&SelectedSigner)->Result<bool>{
    hold.validate()?;scope.validate()?;limits.validate()?;
    require(*hold.root().identity()==scope.receipt_root&&hold.root().selection().root_id==scope.receipt_root_id,"INSPECTION_RECEIPT_ROOT")?;
    require(witness.domain()==scope.domain&&response.domain()==scope.domain
        &&witness.selection.purpose=="receipt-prefix"&&response.selection.purpose=="broker-response","INSPECTION_SIGNER_SCOPE")?;
    witness.distinct(response)?;
    let inspect=||->Result<()>{
        let names=roots::names(hold.directory(),(limits.max_sequences+limits.max_orphan_count+1) as usize)?;
        let mut ordinals=BTreeSet::new();
        for name in names{
            let t=capture_tail(hold.directory(),&name,scope,limits)?;
            require(t.originals.contains_key("confirmation.json"),"CONFIRMATION_MISSING")?;
            let dir=roots::open_child(hold.directory(),&name,libc::O_RDONLY|libc::O_DIRECTORY,0,true)?;
            let proof:PrefixConfirmation=witness.verify(&read_file(&dir,"confirmation.json",&scope.receipt_root,quota::MAX_PACKET)?)?;
            proof.request.validate(proof.request.not_before)?;
            require(proof.schema_version=="lab-broker-prefix-confirmation/v1"&&proof.result=="confirmed"
                &&proof.signer_enrollment_binding==*witness.binding()&&proof.request.scope==*scope
                &&proof.request.entry_binding.relative_path==format!("{name}/entry.json")
                &&ordinals.insert(proof.request.next.ordinal),"INSPECTION_ORIGINAL_CONFIRMATION")?;
            // This checks a historical chain for corruption only. It neither
            // selects a current prefix nor adopts the greatest observed head.
            selected_chain(hold.directory(),scope,limits,&proof.request.next,witness,response,true,None)?;
        }Ok(())
    };
    let uncertain=inspect().is_err();hold.validate()?;Ok(uncertain)
}

/// A managed endpoint must neither contain nor be contained by any protected
/// endpoint. Compare physical inode identities across mount aliases; shared
/// ordinary ancestors alone are permitted. Selection chains are revalidated.
pub(crate) fn disjoint_endpoints(managed:&Exclusive<'_>,protected:&Exclusive<'_>)->Result<()>{
    managed.validate()?;protected.validate()?;
    let same=|a:&Identity,b:&Identity|a.device==b.device&&a.inode==b.inode;
    require(!managed.root().selection().ancestors.iter().any(|a|same(a,protected.root().identity()))
        &&!protected.root().selection().ancestors.iter().any(|a|same(a,managed.root().identity())),"DERIVED_CANNOT_WRITE_CANONICAL_CUSTODY")?;
    managed.validate()?;protected.validate()
}

// Deterministic fixture-only wall-clock delay at the actual persistence/reply
// boundary. No clock substitution, callback, authority or production symbol.
#[cfg(test)] std::thread_local!{static PREFIX_FIXTURE_DELAY:std::cell::Cell<(u8,u64)>=const{std::cell::Cell::new((0,0))};}
#[cfg(test)] fn prefix_fixture_delay(point:u8){PREFIX_FIXTURE_DELAY.with(|value|{let selected=value.get();if selected.0==point{value.set((0,0));std::thread::sleep(Duration::from_millis(selected.1));}});}
