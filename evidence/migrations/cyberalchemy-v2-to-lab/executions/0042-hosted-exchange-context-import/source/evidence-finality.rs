use std::{collections::BTreeMap, sync::Arc, time::Duration};

use base64::{engine::general_purpose::STANDARD, Engine};
use serde::Serialize;
use serde_json::{json, Value};
use tokio::sync::RwLock;

use crate::{transition::TransitionExpectation, DEVNET_GENESIS_HASH, PROGRAM_ID};

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct FinalizedArtifactObservation {
    pub transaction_signature: String,
    pub artifact_version_id: String,
    pub recipient_wallet_public_key: String,
    pub recipient_envelope_sha256: String,
    pub revision: u64,
    pub finality: String,
}

#[derive(Clone, Default)]
pub struct MockFinalityGateway {
    observations: Arc<RwLock<BTreeMap<String, FinalizedArtifactObservation>>>,
}

impl MockFinalityGateway {
    pub async fn record(&self, observation: FinalizedArtifactObservation) {
        self.observations
            .write()
            .await
            .insert(observation.transaction_signature.clone(), observation);
    }

    async fn observe(&self, signature: &str) -> Result<FinalizedArtifactObservation, String> {
        self.observations
            .read()
            .await
            .get(signature)
            .cloned()
            .ok_or_else(|| "transaction has no finalized mock observation".to_string())
    }
}

#[derive(Clone)]
pub enum FinalityGateway {
    Mock(MockFinalityGateway),
    DevnetRpc {
        client: reqwest::Client,
        url: String,
    },
}

impl FinalityGateway {
    pub fn devnet(url: impl Into<String>) -> Self {
        Self::DevnetRpc {
            client: reqwest::Client::builder()
                .connect_timeout(Duration::from_secs(5))
                .timeout(Duration::from_secs(20))
                .build()
                .expect("bounded Devnet HTTP client configuration must be valid"),
            url: url.into(),
        }
    }

    /// Diagnostic state observation only. Never use this method to authorize a transition.
    pub async fn observe(
        &self,
        signature: &str,
        artifact_account: &str,
    ) -> Result<FinalizedArtifactObservation, String> {
        match self {
            Self::Mock(gateway) => gateway.observe(signature).await,
            Self::DevnetRpc { client, url } => {
                observe_devnet(client, url, signature, artifact_account, None).await
            }
        }
    }
    /// Effect-bearing callers must supply the exact locally prepared transition.
    pub async fn observe_transition(
        &self,
        signature: &str,
        artifact_account: &str,
        expected: &TransitionExpectation,
    ) -> Result<FinalizedArtifactObservation, String> {
        match self {
            // Explicit test double. Mock observations are not transaction evidence.
            Self::Mock(gateway) => gateway.observe(signature).await,
            Self::DevnetRpc { client, url } => {
                observe_devnet(client, url, signature, artifact_account, Some(expected)).await
            }
        }
    }
}

async fn rpc(
    client: &reqwest::Client,
    url: &str,
    method: &str,
    params: Value,
) -> Result<Value, String> {
    let response = client
        .post(url)
        .json(&json!({"jsonrpc":"2.0","id":1,"method":method,"params":params}))
        .send()
        .await
        .map_err(|error| format!("Devnet RPC unavailable: {error}"))?;
    if !response.status().is_success() {
        return Err(format!("Devnet RPC returned HTTP {}", response.status()));
    }
    let body: Value = response
        .json()
        .await
        .map_err(|error| format!("Devnet RPC response is invalid JSON: {error}"))?;
    if let Some(error) = body.get("error") {
        return Err(format!("Devnet RPC error: {error}"));
    }
    Ok(body)
}

async fn observe_devnet(
    client: &reqwest::Client,
    url: &str,
    signature: &str,
    artifact_account: &str,
    expected: Option<&TransitionExpectation>,
) -> Result<FinalizedArtifactObservation, String> {
    if signature.is_empty() || artifact_account.is_empty() {
        return Err("transaction signature and artifact account are required".into());
    }
    let genesis = rpc(client, url, "getGenesisHash", json!([])).await?;
    if genesis.pointer("/result").and_then(Value::as_str) != Some(DEVNET_GENESIS_HASH) {
        return Err("RPC endpoint is not the exact bound Solana Devnet genesis".into());
    }

    let status = rpc(
        client,
        url,
        "getSignatureStatuses",
        json!([[signature], {"searchTransactionHistory": true}]),
    )
    .await?;
    let status = status
        .pointer("/result/value/0")
        .ok_or_else(|| "transaction status is unavailable".to_string())?;
    if !status.get("err").is_some_and(Value::is_null)
        || status.get("confirmationStatus").and_then(Value::as_str) != Some("finalized")
    {
        return Err("transaction is not successfully finalized".into());
    }

    let transaction = rpc(
        client,
        url,
        "getTransaction",
        json!([signature, {"commitment":"finalized","encoding":"json","maxSupportedTransactionVersion":0}]),
    )
    .await?;
    let verified_slot = if let Some(expected) = expected {
        let status_slot = status
            .get("slot")
            .and_then(Value::as_u64)
            .ok_or("finalized status slot missing")?;
        Some(expected.verify_transaction(&transaction, signature, artifact_account, status_slot)?)
    } else {
        None
    };
    let account_keys = transaction
        .pointer("/result/transaction/message/accountKeys")
        .and_then(Value::as_array)
        .ok_or_else(|| "finalized transaction body is unavailable".to_string())?;
    let invokes_bound_program = account_keys.iter().any(|entry| {
        entry.as_str() == Some(PROGRAM_ID)
            || entry.get("pubkey").and_then(Value::as_str) == Some(PROGRAM_ID)
    });
    if expected.is_none() && !invokes_bound_program {
        return Err("finalized transaction does not reference the bound KEP program".into());
    }

    let mut account_config = json!({"commitment":"finalized","encoding":"base64"});
    if let Some(slot) = verified_slot {
        account_config["minContextSlot"] = json!(slot);
    }
    let account = rpc(
        client,
        url,
        "getAccountInfo",
        json!([artifact_account, account_config]),
    )
    .await?;
    if let Some(slot) = verified_slot {
        if account
            .pointer("/result/context/slot")
            .and_then(Value::as_u64)
            .is_none_or(|context| context < slot)
        {
            return Err("artifact state predates verified transaction".into());
        }
    }
    let value = account
        .pointer("/result/value")
        .ok_or_else(|| "artifact account is unavailable at finalized commitment".to_string())?;
    if value.get("owner").and_then(Value::as_str) != Some(PROGRAM_ID) {
        return Err("artifact account is not owned by the bound KEP program".into());
    }
    let encoded = value
        .pointer("/data/0")
        .and_then(Value::as_str)
        .ok_or_else(|| "artifact account bytes are unavailable".to_string())?;
    let bytes = STANDARD
        .decode(encoded)
        .map_err(|_| "artifact account bytes are invalid base64".to_string())?;
    if bytes.len() != 338 || bytes[0] != 1 {
        return Err("artifact account has an unsupported layout".into());
    }
    if let Some(expected) = expected {
        if bs58::encode(&bytes[33..65]).into_string() != expected.originator_wallet
            || bytes[202..234] != expected.key_digest()?
        {
            return Err("artifact originator or recipient key commitment mismatch".into());
        }
    }
    let artifact_version_id = hex::encode(&bytes[1..33]);
    let recipient_wallet_public_key = bs58::encode(&bytes[65..97]).into_string();
    if bytes[97] != 1 {
        return Err("artifact account has no active recipient".into());
    }
    let recipient_envelope_sha256 = hex::encode(&bytes[234..266]);
    let revision = u64::from_le_bytes(
        bytes[330..338]
            .try_into()
            .map_err(|_| "artifact revision bytes are invalid".to_string())?,
    );
    Ok(FinalizedArtifactObservation {
        transaction_signature: signature.to_string(),
        artifact_version_id,
        recipient_wallet_public_key,
        recipient_envelope_sha256,
        revision,
        finality: "finalized".into(),
    })
}
