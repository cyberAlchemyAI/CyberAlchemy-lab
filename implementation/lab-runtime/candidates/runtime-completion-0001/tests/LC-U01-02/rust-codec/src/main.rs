//! Independent executable encoding/signature vectors; isolated fixture key only.
use std::{collections::BTreeMap, fmt, io::{self, BufRead}};
use serde::de::{self, Deserialize, Deserializer, MapAccess, SeqAccess, Visitor};
use serde_json::{Value, Number};
use ed25519_dalek::{Signer, SigningKey};

struct Strict(Value);
impl<'de> Deserialize<'de> for Strict {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        struct V;
        impl<'de> Visitor<'de> for V {
            type Value = Strict;
            fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result { f.write_str("closed integer JSON") }
            fn visit_bool<E: de::Error>(self, v: bool) -> Result<Strict,E> { Ok(Strict(Value::Bool(v))) }
            fn visit_unit<E: de::Error>(self) -> Result<Strict,E> { Ok(Strict(Value::Null)) }
            fn visit_i64<E: de::Error>(self, v: i64) -> Result<Strict,E> { Ok(Strict(Value::Number(Number::from(v)))) }
            fn visit_u64<E: de::Error>(self, v: u64) -> Result<Strict,E> {
                if v > i64::MAX as u64 { return Err(E::custom("integer range")); }
                self.visit_i64(v as i64)
            }
            fn visit_str<E: de::Error>(self, v: &str) -> Result<Strict,E> { Ok(Strict(Value::String(v.to_owned()))) }
            fn visit_string<E: de::Error>(self, v: String) -> Result<Strict,E> { Ok(Strict(Value::String(v))) }
            fn visit_seq<A: SeqAccess<'de>>(self, mut a: A) -> Result<Strict,A::Error> {
                let mut v = Vec::new();
                while let Some(Strict(x)) = a.next_element()? { v.push(x); }
                Ok(Strict(Value::Array(v)))
            }
            fn visit_map<A: MapAccess<'de>>(self, mut a: A) -> Result<Strict,A::Error> {
                let mut m = BTreeMap::new();
                while let Some((k, Strict(v))) = a.next_entry::<String,Strict>()? {
                    if m.insert(k, v).is_some() { return Err(de::Error::custom("duplicate")); }
                }
                Ok(Strict(Value::Object(m.into_iter().collect())))
            }
        }
        d.deserialize_any(V)
    }
}
fn hex(raw: &[u8]) -> String { raw.iter().map(|b| format!("{b:02x}")).collect() }
fn depth(v: &Value, n: usize) -> bool {
    if n > 64 { return false; }
    match v { Value::Array(a) => a.iter().all(|x| depth(x,n+1)),
        Value::Object(m) => m.values().all(|x| depth(x,n+1)), _ => true }
}
fn main() {
    for line in io::stdin().lock().lines() {
        let Ok(line) = line else { break; };
        let result = serde_json::from_str::<Strict>(&line);
        match result {
            Ok(Strict(v)) if line.len() <= 65536 && depth(&v,0)
                && v.get("schema_version").and_then(Value::as_str).map(|s| !s.is_empty()).unwrap_or(false) => {
                let raw = serde_json::to_vec(&v).unwrap();
                let key = SigningKey::from_bytes(&[7u8;32]); // deterministic fixture only
                let signature = key.sign(&raw);
                println!("{}", serde_json::json!({"ok":true,"hex":hex(&raw),"signature_hex":hex(&signature.to_bytes())}));
            },
            _ => println!("{{\"ok\":false}}")
        }
    }
}
