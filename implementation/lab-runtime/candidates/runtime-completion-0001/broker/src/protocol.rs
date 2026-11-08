//! Bounded Linux wire and canonical records. No filesystem effects or dispatch.
//! Host enrollment/control snapshots are separate trusted inputs, never packets.
pub mod authority;

use serde::de::{self, Deserialize, Deserializer, MapAccess, SeqAccess, Visitor};
use serde_json::{Number, Value};
use sha2::{Digest, Sha256};
use std::{collections::BTreeMap, fmt, mem, os::fd::{AsRawFd, FromRawFd, OwnedFd},
          ptr, time::{Duration, Instant}};

pub const MAX_FRAME: usize = 65_536;
pub const MAX_CHUNK: usize = 32_768;
pub const MAX_PERMIT: usize = 8_192;
pub const MAX_BATCH: usize = 32;
pub const MAX_CONTROL: usize = 2_048;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Refusal(pub &'static str);
impl fmt::Display for Refusal {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { f.write_str(self.0) }
}
impl std::error::Error for Refusal {}
pub type Result<T> = std::result::Result<T, Refusal>;
pub fn need(ok: bool, code: &'static str) -> Result<()> {
    if ok { Ok(()) } else { Err(Refusal(code)) }
}

struct Strict(Value);
impl<'de> Deserialize<'de> for Strict {
    fn deserialize<D: Deserializer<'de>>(d: D) -> std::result::Result<Self, D::Error> {
        struct V;
        impl<'de> Visitor<'de> for V {
            type Value = Strict;
            fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result { f.write_str("bounded integer JSON") }
            fn visit_bool<E: de::Error>(self, x: bool) -> std::result::Result<Strict,E> { Ok(Strict(Value::Bool(x))) }
            fn visit_unit<E: de::Error>(self) -> std::result::Result<Strict,E> { Ok(Strict(Value::Null)) }
            fn visit_i64<E: de::Error>(self, x: i64) -> std::result::Result<Strict,E> { Ok(Strict(Value::Number(Number::from(x)))) }
            fn visit_u64<E: de::Error>(self, x: u64) -> std::result::Result<Strict,E> {
                if x > i64::MAX as u64 { return Err(E::custom("INTEGER_RANGE")); }
                self.visit_i64(x as i64)
            }
            fn visit_str<E: de::Error>(self, x: &str) -> std::result::Result<Strict,E> { Ok(Strict(Value::String(x.into()))) }
            fn visit_string<E: de::Error>(self, x: String) -> std::result::Result<Strict,E> { Ok(Strict(Value::String(x))) }
            fn visit_seq<A: SeqAccess<'de>>(self, mut a: A) -> std::result::Result<Strict,A::Error> {
                let mut out = Vec::new();
                while let Some(Strict(x)) = a.next_element()? { out.push(x); }
                Ok(Strict(Value::Array(out)))
            }
            fn visit_map<A: MapAccess<'de>>(self, mut a: A) -> std::result::Result<Strict,A::Error> {
                let mut out = BTreeMap::new();
                while let Some((key, Strict(x))) = a.next_entry::<String,Strict>()? {
                    if out.insert(key, x).is_some() { return Err(de::Error::custom("DUPLICATE_KEY")); }
                }
                Ok(Strict(Value::Object(out.into_iter().collect())))
            }
        }
        d.deserialize_any(V)
    }
}
fn check_depth(v: &Value, depth: usize) -> Result<()> {
    need(depth <= 64, "JSON_DEPTH")?;
    match v {
        Value::Array(a) => for x in a { check_depth(x, depth+1)?; },
        Value::Object(m) => for x in m.values() { check_depth(x, depth+1)?; },
        Value::Number(n) => { need(n.as_i64().is_some(), "INTEGER_RANGE")?; },
        _ => (),
    }
    Ok(())
}
pub fn parse(raw: &[u8], limit: usize) -> Result<Value> {
    need(limit > 0 && limit <= MAX_FRAME && raw.len() <= limit, "FRAME_LIMIT")?;
    let Strict(value) = serde_json::from_slice(raw).map_err(|_| Refusal("INVALID_JSON"))?;
    check_depth(&value, 0)?;
    Ok(value)
}
pub fn canonical(value: &Value) -> Result<Vec<u8>> {
    check_depth(value, 0)?;
    serde_json::to_vec(value).map_err(|_| Refusal("ENCODING"))
}
pub fn signing_bytes(value: &Value) -> Result<Vec<u8>> {
    text(value, "schema_version", 128)?;
    canonical(value)
}
pub fn hash(raw: &[u8]) -> String { hex(&Sha256::digest(raw)) }
pub fn hex(raw: &[u8]) -> String { raw.iter().map(|x| format!("{x:02x}")).collect() }
pub fn unhex<const N: usize>(s: &str) -> Result<[u8;N]> {
    need(s.len() == N*2 && s.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)), "HEX_ENCODING")?;
    let mut out = [0;N];
    for (i, x) in out.iter_mut().enumerate() {
        *x = u8::from_str_radix(&s[i*2..i*2+2], 16).map_err(|_| Refusal("HEX_ENCODING"))?;
    }
    Ok(out)
}
pub fn closed(v: &Value, keys: &[&str]) -> Result<()> {
    let m = v.as_object().ok_or(Refusal("CLOSED_FIELDS"))?;
    need(m.len() == keys.len() && keys.iter().all(|k| m.contains_key(*k)), "CLOSED_FIELDS")
}
pub fn text<'a>(v: &'a Value, key: &str, max: usize) -> Result<&'a str> {
    let s = v.get(key).and_then(Value::as_str).ok_or(Refusal("STRING_FIELD"))?;
    need(!s.is_empty() && s.len() <= max && !s.contains('\0'), "STRING_LIMIT")?;
    Ok(s)
}
pub fn integer(v: &Value, key: &str, min: i64, max: i64) -> Result<i64> {
    let n = v.get(key).and_then(Value::as_i64).ok_or(Refusal("INTEGER_FIELD"))?;
    need(min <= n && n <= max, "INTEGER_RANGE")?;
    Ok(n)
}
pub fn digest(v: &Value, key: &str) -> Result<()> { unhex::<32>(text(v,key,64)?).map(|_| ()) }
pub fn binding(v: &Value) -> Result<()> {
    closed(v, &["kind","root_id","relative_path","sha256","size_bytes"])?;
    need(["execution","semantic","evidence","public-package","protected-input"].contains(&text(v,"kind",32)?),"BINDING_KIND")?;
    text(v,"root_id",128)?; relative(text(v,"relative_path",1024)?)?;
    digest(v,"sha256")?;
    integer(v,"size_bytes",0,i64::MAX)?;
    Ok(())
}
/// Embedded bytes have no invented filesystem locator. Never substitute this
/// domain record for C01 ByteBinding; source identity stays full and lossless.
pub fn content_digest(raw: &[u8]) -> Value {
    serde_json::json!({"schema_version":"lab-completion-content-digest/v1","sha256":hash(raw),"size_bytes":raw.len()})
}
pub fn validate_content_digest(v:&Value)->Result<()> {
    closed(v,&["schema_version","sha256","size_bytes"])?;
    need(v["schema_version"]=="lab-completion-content-digest/v1","CONTENT_DIGEST_DOMAIN")?;
    digest(v,"sha256")?;integer(v,"size_bytes",0,i64::MAX)?;Ok(())
}
pub fn nullable_binding(v: &Value) -> Result<()> { if v.is_null() { Ok(()) } else { binding(v) } }
pub fn relative(s: &str) -> Result<()> {
    need(!s.is_empty() && s.len() <= 1024 && !s.starts_with('/') && !s.contains('\0') &&
        !s.contains('\\') && s.split('/').all(|p| !p.is_empty() && p != "." && p != ".."), "MEMBER_PATH")
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Peer { pub pid: i32, pub uid: u32, pub gid: u32 }
#[derive(Debug)]
pub struct Packet { pub bytes: Vec<u8>, pub peer: Peer }
pub struct Receiver { fd: OwnedFd, frame_limit: usize, control_limit: usize }
impl Receiver {
    pub fn new(fd: OwnedFd, frame_limit: usize, control_limit: usize) -> Result<Self> {
        need(frame_limit > 0 && frame_limit <= MAX_FRAME && control_limit > 0 && control_limit <= MAX_CONTROL,
             "RECEIVE_LIMIT")?;
        let mut kind: libc::c_int = 0;
        let mut len = mem::size_of_val(&kind) as libc::socklen_t;
        let r = unsafe { libc::getsockopt(fd.as_raw_fd(),libc::SOL_SOCKET,libc::SO_TYPE,
            (&mut kind as *mut libc::c_int).cast(),&mut len) };
        need(r == 0 && kind == libc::SOCK_SEQPACKET, "SOCKET_TYPE")?;
        let mut address: libc::sockaddr_storage = unsafe { mem::zeroed() };
        let mut alen = mem::size_of_val(&address) as libc::socklen_t;
        let r = unsafe { libc::getsockname(fd.as_raw_fd(),(&mut address as *mut libc::sockaddr_storage).cast(),&mut alen) };
        need(r == 0 && address.ss_family as i32 == libc::AF_UNIX, "SOCKET_DOMAIN")?;
        let enabled: libc::c_int = 1;
        let r = unsafe { libc::setsockopt(fd.as_raw_fd(),libc::SOL_SOCKET,libc::SO_PASSCRED,
            (&enabled as *const libc::c_int).cast(),mem::size_of_val(&enabled) as libc::socklen_t) };
        need(r == 0, "PASSCRED_UNAVAILABLE")?;
        Ok(Self {fd,frame_limit,control_limit})
    }
    pub fn receive(&self, timeout: Duration) -> Result<Packet> {
        need(!timeout.is_zero() && timeout <= Duration::from_secs(60), "RECEIVE_DEADLINE")?;
        let deadline = Instant::now()+timeout;
        loop {
            let left = deadline.saturating_duration_since(Instant::now());
            need(!left.is_zero(), "RECEIVE_TIMEOUT")?;
            let mut poll = libc::pollfd {fd:self.fd.as_raw_fd(),events:libc::POLLIN,revents:0};
            let ms = left.as_millis().max(1).min(i32::MAX as u128) as i32;
            let ready = unsafe {libc::poll(&mut poll,1,ms)};
            if ready < 0 && std::io::Error::last_os_error().raw_os_error() == Some(libc::EINTR) { continue; }
            need(ready >= 0,"POLL_FAILED")?;
            if ready == 0 { continue; }
            let mut bytes = vec![0u8;self.frame_limit];
            // usize alignment supports cmsghdr; no cast of unaligned user bytes.
            let mut control = [0usize;MAX_CONTROL/mem::size_of::<usize>()];
            let mut io = libc::iovec {iov_base:bytes.as_mut_ptr().cast(),iov_len:bytes.len()};
            let mut msg: libc::msghdr = unsafe {mem::zeroed()};
            msg.msg_iov = &mut io; msg.msg_iovlen = 1;
            msg.msg_control = control.as_mut_ptr().cast(); msg.msg_controllen = self.control_limit;
            let received = unsafe {libc::recvmsg(self.fd.as_raw_fd(),&mut msg,libc::MSG_DONTWAIT|libc::MSG_CMSG_CLOEXEC)};
            if received < 0 {
                let e = std::io::Error::last_os_error().raw_os_error();
                if e == Some(libc::EINTR) || e == Some(libc::EAGAIN) { continue; }
                return Err(Refusal("RECEIVE_FAILED"));
            }
            let used = msg.msg_controllen.min(self.control_limit);
            let raw = unsafe {std::slice::from_raw_parts(control.as_ptr().cast::<u8>(),used)};
            // Always dispose delivered rights, even when the data/control packet
            // is truncated. Never return early based on msg_flags before this.
            let credentials = parse_control(raw);
            need(msg.msg_flags & (libc::MSG_TRUNC|libc::MSG_CTRUNC) == 0,"PACKET_TRUNCATED")?;
            let peer = credentials?;
            need(received > 0 && received as usize <= self.frame_limit,"EMPTY_OR_OVERSIZE_PACKET")?;
            bytes.truncate(received as usize);
            return Ok(Packet {bytes,peer});
        }
    }
}

fn aligned(n: usize) -> Option<usize> {
    let align = mem::size_of::<usize>(); n.checked_add(align-1).map(|x| x & !(align-1))
}
// Only kernel recvmsg output reaches this parser in production. OwnedFd takes
// every delivered descriptor immediately and RAII closes them on all exits.
fn parse_control(raw: &[u8]) -> Result<Peer> {
    let header = aligned(mem::size_of::<libc::cmsghdr>()).ok_or(Refusal("CONTROL_LENGTH"))?;
    let mut offset = 0; let mut peer = None; let mut refused = false; let mut rights = Vec::new();
    while offset < raw.len() {
        if raw.len()-offset < mem::size_of::<libc::cmsghdr>() { refused=true; break; }
        let h: libc::cmsghdr = unsafe {ptr::read_unaligned(raw.as_ptr().add(offset).cast())};
        if h.cmsg_len < header { refused=true; break; }
        let end = offset.saturating_add(h.cmsg_len).min(raw.len());
        let start = offset.saturating_add(header).min(end);
        let body = &raw[start..end];
        if h.cmsg_level == libc::SOL_SOCKET && h.cmsg_type == libc::SCM_RIGHTS {
            refused = true;
            for chunk in body.chunks_exact(mem::size_of::<libc::c_int>()) {
                let fd = i32::from_ne_bytes(chunk.try_into().map_err(|_| Refusal("CONTROL_LENGTH"))?);
                if fd >= 0 { rights.push(unsafe {OwnedFd::from_raw_fd(fd)}); }
            }
        } else if h.cmsg_level == libc::SOL_SOCKET && h.cmsg_type == libc::SCM_CREDENTIALS {
            if body.len() != mem::size_of::<libc::ucred>() || peer.is_some() { refused=true; }
            else {
                let c: libc::ucred = unsafe {ptr::read_unaligned(body.as_ptr().cast())};
                if c.pid <= 0 || c.uid==u32::MAX || c.gid==u32::MAX { refused=true; }
                peer=Some(Peer {pid:c.pid,uid:c.uid,gid:c.gid});
            }
        } else { refused=true; }
        if h.cmsg_len > raw.len()-offset { refused=true; break; }
        let step = aligned(h.cmsg_len).ok_or(Refusal("CONTROL_LENGTH"))?;
        if step > raw.len()-offset {
            // The final cmsg may omit padding, but may not have a partial header.
            need(offset+h.cmsg_len == raw.len(),"CONTROL_LENGTH")?;
            offset=raw.len();
        } else { offset+=step; }
    }
    drop(rights);
    need(!refused,"ANCILLARY_REFUSED")?;
    peer.ok_or(Refusal("CREDENTIALS_REQUIRED"))
}

pub const REQUEST_FIELDS: &[&str] = &["schema_version","request_id","operation_id","sequence",
    "activation_binding","store_id","instance_id","slot_epoch","principal_ref","verb",
    "intent_binding","payload","authorization_binding"];
pub const VERBS: &[&str] = &["reserve_family","create_stage","write_member","seal_stage",
    "commit_generation","read_receipt","inspect","inspect_operation","reconcile_operation","close_family","repair_derived"];

#[derive(Debug, Clone)]
pub struct Frame { pub(crate) request: Value, pub(crate) permit: Value, pub(crate) digest: String }
impl Frame {
    pub fn decode(raw: &[u8]) -> Result<Self> {
        let value=parse(raw,MAX_FRAME)?;
        closed(&value,&["schema_version","request","permit"])?;
        need(value["schema_version"] == "lab-completion-broker-frame/v1","FRAME_VERSION")?;
        need(canonical(&value)? == raw,"NONCANONICAL_FRAME")?;
        let request=&value["request"]; closed(request,REQUEST_FIELDS)?;
        need(request["schema_version"] == "lab-completion-broker-request/v1","REQUEST_VERSION")?;
        for key in ["request_id","operation_id","store_id","instance_id","principal_ref"] { text(request,key,128)?; }
        integer(request,"sequence",0,i64::MAX)?; integer(request,"slot_epoch",1,i64::MAX)?;
        binding(&request["activation_binding"])?; binding(&request["intent_binding"])?;
        validate_content_digest(&request["authorization_binding"])?;
        need(VERBS.contains(&text(request,"verb",64)?),"UNKNOWN_VERB")?;
        let permit_raw=canonical(&value["permit"])?;
        need(permit_raw.len()<=MAX_PERMIT,"PERMIT_LIMIT")?;
        need(request["authorization_binding"] == content_digest(&permit_raw),"PERMIT_BINDING")?;
        validate_payload(request)?;
        Ok(Self {request:request.clone(),permit:value["permit"].clone(),digest:hash(raw)})
    }
    pub fn request(&self) -> &Value { &self.request }
    pub fn wire_digest(&self) -> &str { &self.digest }
    pub fn authorization_core(&self) -> Result<Value> { authorization_core(&self.request) }
}
pub fn authorization_core(request: &Value) -> Result<Value> {
    closed(request,REQUEST_FIELDS)?;
    // Explicitly closed construction; no generic stripping of arbitrary fields.
    Ok(serde_json::json!({"schema_version":"lab-completion-message-authorization-core/v1",
        "request_schema_version":request["schema_version"],"request_id":request["request_id"],
        "operation_id":request["operation_id"],"sequence":request["sequence"],
        "activation_binding":request["activation_binding"],"store_id":request["store_id"],
        "instance_id":request["instance_id"],"slot_epoch":request["slot_epoch"],
        "principal_ref":request["principal_ref"],"verb":request["verb"],
        "intent_binding":request["intent_binding"],"payload":request["payload"]}))
}
fn validate_payload(request:&Value) -> Result<()> {
    let p=&request["payload"]; let verb=text(request,"verb",64)?;
    match verb {
        "write_member" => {
            closed(p,&["root_id","member","preimage_binding","full_sha256","full_length","offset","length","chunk_sha256","bytes_base64"])?;
            text(p,"root_id",128)?; relative(text(p,"member",1024)?)?; nullable_binding(&p["preimage_binding"])?;
            digest(p,"full_sha256")?; digest(p,"chunk_sha256")?;
            let full=integer(p,"full_length",0,i64::MAX)?;
            let offset=integer(p,"offset",0,full)?;
            let length=integer(p,"length",0,MAX_CHUNK as i64)?;
            need((full==0 && offset==0 && length==0) || (full>0 && length>0),"EMPTY_MEMBER_CHUNK")?;
            need(offset.checked_add(length).is_some_and(|n|n<=full),"CHUNK_RANGE")?;
            use base64::Engine;
            let encoded=p["bytes_base64"].as_str().ok_or(Refusal("BASE64"))?;
            need(encoded.len()<=43_692,"BASE64_LIMIT")?;
            let bytes=base64::engine::general_purpose::STANDARD.decode(encoded).map_err(|_| Refusal("BASE64"))?;
            need(bytes.len()==length as usize && base64::engine::general_purpose::STANDARD.encode(&bytes)==encoded,"CHUNK_LENGTH")?;
            need(hash(&bytes)==text(p,"chunk_sha256",64)?,"CHUNK_DIGEST")?;
        },
        "reserve_family"|"create_stage" => {
            closed(p,&["root_id","stage_name","max_bytes"])?;
            text(p,"root_id",128)?; relative(text(p,"stage_name",1024)?)?;
            integer(p,"max_bytes",0,i64::MAX)?;
        },
        _ => {
            closed(p,&["root_id","subject_binding"])?;
            text(p,"root_id",128)?; binding(&p["subject_binding"])?;
        },
    }
    Ok(())
}

#[cfg(test)]
mod control_tests {
    use super::*;
    #[test] fn malformed_control_is_closed() {
        assert_eq!(parse_control(&[]),Err(Refusal("CREDENTIALS_REQUIRED")));
        assert_eq!(parse_control(&[0u8;3]),Err(Refusal("ANCILLARY_REFUSED")));
        let h=libc::cmsghdr{cmsg_len:0,cmsg_level:libc::SOL_SOCKET,cmsg_type:libc::SCM_CREDENTIALS};
        let raw=unsafe{std::slice::from_raw_parts((&h as *const libc::cmsghdr).cast::<u8>(),mem::size_of_val(&h))};
        assert_eq!(parse_control(raw),Err(Refusal("ANCILLARY_REFUSED")));
    }
    #[test] fn duplicate_and_invalid_credential_control_refuse() {
        fn credential(pid:i32,uid:u32,gid:u32)->Vec<u8> {
            let n=unsafe{libc::CMSG_SPACE(mem::size_of::<libc::ucred>() as u32)} as usize;
            let mut raw=vec![0u8;n];
            let h=libc::cmsghdr{cmsg_len:unsafe{libc::CMSG_LEN(mem::size_of::<libc::ucred>() as u32)} as usize,
                cmsg_level:libc::SOL_SOCKET,cmsg_type:libc::SCM_CREDENTIALS};
            let c=libc::ucred{pid,uid,gid};
            unsafe{ptr::write_unaligned(raw.as_mut_ptr().cast(),h);
                ptr::write_unaligned(raw.as_mut_ptr().add(aligned(mem::size_of::<libc::cmsghdr>()).unwrap()).cast(),c);}
            raw
        }
        let valid=credential(42,1,2);assert_eq!(parse_control(&valid).unwrap(),Peer{pid:42,uid:1,gid:2});
        let mut duplicate=valid.clone();duplicate.extend_from_slice(&valid);
        assert_eq!(parse_control(&duplicate),Err(Refusal("ANCILLARY_REFUSED")));
        for raw in [credential(0,1,2),credential(42,u32::MAX,2),credential(42,1,u32::MAX)] {
            assert_eq!(parse_control(&raw),Err(Refusal("ANCILLARY_REFUSED")));
        }
    }
}
