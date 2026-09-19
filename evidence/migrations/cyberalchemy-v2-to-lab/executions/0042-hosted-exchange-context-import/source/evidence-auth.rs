use base64::{engine::general_purpose::STANDARD, Engine};
use ed25519_dalek::{Signature, VerifyingKey};
use sha2::{Digest, Sha256};

use crate::model::Authorization;

pub fn sha256_hex(bytes: &[u8]) -> String {
    hex::encode(Sha256::digest(bytes))
}

pub fn decode_base64(value: &str, label: &str) -> Result<Vec<u8>, String> {
    STANDARD
        .decode(value)
        .map_err(|_| format!("{label} is not canonical base64"))
}

pub fn verify_digest(encoded: &str, expected: &str, label: &str) -> Result<Vec<u8>, String> {
    let bytes = decode_base64(encoded, label)?;
    if sha256_hex(&bytes) != expected {
        return Err(format!("{label} digest mismatch"));
    }
    Ok(bytes)
}

pub fn verify_wallet_signature(
    wallet_public_key: &str,
    authorization: &Authorization,
    expected_message: &str,
) -> Result<(), String> {
    if authorization.message != expected_message {
        return Err("authorization message mismatch".into());
    }
    let key_bytes = bs58::decode(wallet_public_key)
        .into_vec()
        .map_err(|_| "wallet public key is not base58".to_string())?;
    let key_bytes: [u8; 32] = key_bytes
        .try_into()
        .map_err(|_| "wallet public key must contain 32 bytes".to_string())?;
    let signature_bytes = decode_base64(&authorization.signature_base64, "signature")?;
    let signature = Signature::from_slice(&signature_bytes)
        .map_err(|_| "signature must contain 64 bytes".to_string())?;
    let key = VerifyingKey::from_bytes(&key_bytes)
        .map_err(|_| "wallet public key is invalid".to_string())?;
    key.verify_strict(expected_message.as_bytes(), &signature)
        .map_err(|_| "wallet signature rejected".to_string())
}

pub fn validate_id(value: &str, label: &str) -> Result<(), String> {
    if value.is_empty()
        || value.len() > 128
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b':'))
    {
        Err(format!("{label} has invalid characters or length"))
    } else {
        Ok(())
    }
}

pub fn register_message(
    operation: &str,
    identity: &str,
    wallet: &str,
    encryption_key: &str,
    version: u64,
) -> String {
    signed_message(
        "register",
        &(operation, identity, wallet, encryption_key, version),
    )
}

pub fn artifact_message(
    operation: &str,
    identity: &str,
    artifact: &str,
    policy: &str,
    epoch: u64,
    ciphertext_digest: &str,
    envelope_digest: &str,
) -> String {
    signed_message(
        "artifact",
        &(
            operation,
            identity,
            artifact,
            policy,
            epoch,
            ciphertext_digest,
            envelope_digest,
        ),
    )
}

pub fn grant_message(
    operation: &str,
    artifact: &str,
    originator: &str,
    recipient: &str,
    revision: u64,
    envelope_digest: &str,
) -> String {
    signed_message(
        "grant",
        &(
            operation,
            artifact,
            originator,
            recipient,
            revision,
            envelope_digest,
            0,
        ),
    )
}

pub fn access_message(artifact: &str, requester: &str, revision: u64) -> String {
    signed_message("access", &(artifact, requester, revision))
}

pub fn reissue_request_message(
    operation: &str,
    artifact: &str,
    recipient: &str,
    previous_version: u64,
    replacement_key: &str,
    replacement_version: u64,
    revision: u64,
) -> String {
    signed_message(
        "reissue-request",
        &(
            operation,
            artifact,
            recipient,
            previous_version,
            replacement_key,
            replacement_version,
            revision,
        ),
    )
}

pub fn reissue_fulfill_message(
    operation: &str,
    artifact: &str,
    originator: &str,
    recipient: &str,
    revision: u64,
    envelope_digest: &str,
) -> String {
    signed_message(
        "reissue-fulfill",
        &(
            operation,
            artifact,
            originator,
            recipient,
            revision,
            envelope_digest,
        ),
    )
}

/// This candidate is bound to the canonical hosted Devnet service. Other deployments
/// must choose their own audience in both signer and verifier; no v1 fallback.
pub const SIGNING_AUDIENCE: &str = "https://kep.cyberalchemylab.com";
pub fn signed_message(action: &str, fields: &impl serde::Serialize) -> String {
    format!(
        "ca2:kep:authorization:v2:{}",
        serde_json::to_string(&(
            SIGNING_AUDIENCE,
            crate::DEVNET_GENESIS_HASH,
            crate::PROGRAM_ID,
            action,
            fields
        ))
        .expect("authorization fields serialize")
    )
}
