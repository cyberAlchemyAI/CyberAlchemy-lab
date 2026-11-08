//! Closed typed records plus canonical byte equality reject duplicate fields,
//! unknown fields, alternate encodings, floats and integers outside signed i64.
use super::{fail, Error, Result};
use serde::{de::DeserializeOwned, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
pub const MAX_INTEGER: u64 = i64::MAX as u64;
pub const MAX_BYTES: usize = 65536;
pub fn digest(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }
pub fn identifier(s: &str) -> bool {
    !s.is_empty() && s.len() <= 128 && s.bytes().all(|b| b.is_ascii_alphanumeric() || b"-_.:".contains(&b))
}
pub fn hash(s: &str) -> bool { s.len() == 64 && s.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)) }
fn valid(v: &Value, depth: usize) -> bool {
    if depth > 64 { return false; }
    match v {
        Value::Null | Value::Bool(_) => true,
        Value::Number(n) => n.as_i64().is_some(),
        // Rust strings are Unicode scalar UTF-8, including exact combining,
        // non-BMP and escaped control characters. Never normalize identity.
        Value::String(_) => true,
        Value::Array(a) => a.iter().all(|v| valid(v, depth+1)),
        Value::Object(o) => o.values().all(|v| valid(v, depth+1)),
    }
}
pub fn encode<T: Serialize>(value: &T) -> Result<Vec<u8>> {
    let value = serde_json::to_value(value).map_err(|e| Error(e.to_string()))?;
    if !valid(&value,0) { return fail("record canonical domain"); }
    let raw=serde_json::to_vec(&value).map_err(|e| Error(e.to_string()))?;
    if raw.len()>MAX_BYTES { return fail("record codec byte bound"); }
    Ok(raw)
}
pub fn decode<T: DeserializeOwned + Serialize>(raw: &[u8]) -> Result<T> {
    if raw.len()>MAX_BYTES { return fail("record codec byte bound"); }
    let value: T = serde_json::from_slice(raw).map_err(|_| Error("closed record parse".into()))?;
    if encode(&value)? != raw { return fail("noncanonical record"); }
    Ok(value)
}
