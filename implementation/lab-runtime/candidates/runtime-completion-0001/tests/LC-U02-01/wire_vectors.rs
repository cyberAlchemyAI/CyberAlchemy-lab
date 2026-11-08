//! Bounded inert cross-language vector driver. Its key is a public fixture.
use std::io::{self,BufRead,Read};
use lab_completion_broker::{*,authority::*};
use ed25519_dalek::SigningKey;
use serde_json::json;
fn main() {
    let frame_mode=std::env::args().nth(1).as_deref()==Some("--frame");
    let key=SigningKey::from_bytes(&[7;32]);let mut stdin=io::stdin().lock();
    loop {
        let mut line=Vec::new();let count=stdin.by_ref().take((MAX_FRAME+2) as u64).read_until(b'\n',&mut line).unwrap();
        if count==0 {break;}if line.last()==Some(&b'\n'){line.pop();}
        let result=(||->Result<serde_json::Value>{
            if frame_mode {
                let frame=Frame::decode(&line)?;
                let result=serde_json::json!({"kind":"evidence","root_id":"owned-root","relative_path":"result.json",
                    "sha256":hash(b"fixture-result"),"size_bytes":14});
                let receipt=sign_receipt(&frame,"staging","PASS",None,result,"fixture-issuer",&key)?;
                Ok(json!({"ok":true,"frame_sha256":frame.wire_digest(),"authorization_core_hex":hex(&canonical(&frame.authorization_core()?)?),
                    "receipt_hex":hex(&canonical(&receipt)?)}))
            } else {
                let value=parse(&line,MAX_FRAME)?;let raw=signing_bytes(&value)?;
                let signed=signed_record(&value,"fixture-issuer",&key)?;
                Ok(json!({"ok":true,"hex":hex(&raw),"envelope_hex":hex(&canonical(&signed)?)}))
            }
        })();
        println!("{}",result.unwrap_or_else(|e|json!({"ok":false,"error":e.0})));
        if count>MAX_FRAME+1 {break;}
    }
}
