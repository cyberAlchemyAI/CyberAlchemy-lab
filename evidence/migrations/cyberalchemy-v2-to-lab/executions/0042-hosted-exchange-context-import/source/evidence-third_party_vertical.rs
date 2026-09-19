use axum::{
    body::Body,
    http::{Request, StatusCode},
    Router,
};
use base64::{engine::general_purpose::STANDARD, Engine};
use chacha20poly1305::{
    aead::{Aead, KeyInit},
    XChaCha20Poly1305, XNonce,
};
use cyberalchemy_kep_hosted_devnet::{
    auth::{
        access_message, artifact_message, grant_message, register_message, reissue_fulfill_message,
        reissue_request_message, sha256_hex,
    },
    model::{
        AccessRequest, Authorization, ClientErrorEventRequest, CreateArtifactRequest,
        CreateReissueRequest, FinalizeGrantRequest, FulfillReissueRequest, PrepareGrantRequest,
        RegisterIdentityRequest,
    },
    router, Application, FinalityGateway, FinalizedArtifactObservation, MockFinalityGateway,
};
use ed25519_dalek::{Signer, SigningKey};
use hpke::{
    aead::ChaCha20Poly1305, kdf::HkdfSha256, kem::X25519HkdfSha256, Deserializable, Kem, OpModeR,
    OpModeS, Serializable,
};
use http_body_util::BodyExt;
use serde::Serialize;
use serde_json::{json, Value};
use tower::ServiceExt;

type TestKem = X25519HkdfSha256;
type TestKdf = HkdfSha256;
type TestAead = ChaCha20Poly1305;

#[tokio::test]
async fn client_error_endpoint_accepts_bounded_redacted_evidence_only() {
    let application =
        Application::memory(FinalityGateway::Mock(MockFinalityGateway::default())).await;
    let app = router(application);
    let mut event = ClientErrorEventRequest {
        attempt_id: "attempt-blockhash-001".into(),
        operation_kind: "initialize_artifact".into(),
        stage: "devnet_submission".into(),
        error_code: "blockhash_not_found".into(),
        effect_status: "rejected_before_submission".into(),
        network: "solana-devnet".into(),
        safe_message:
            "Solana rejected this transaction before submission because its blockhash expired."
                .into(),
        diagnostic_digest: "ab".repeat(32),
        rpc_request_id: Some("rpc-request-001".into()),
        transaction_signature: None,
        reporter: "client".into(),
        registry_version: "kep-error-registry/v1".into(),
        source_layer: "transaction".into(),
        retry_disposition: "user_may_retry_fresh".into(),
        http_status: None,
        rpc_code: Some(-32002),
        transaction_error: Some("BlockhashNotFound".into()),
        instruction_index: None,
        instruction_error: None,
        program_id: None,
        custom_program_code: None,
        correlation_id: Some("browser-request-001".into()),
    };
    let (status, receipt) = call(&app, "POST", "/v1/client-errors", &event).await;
    assert_eq!(status, StatusCode::ACCEPTED);
    assert_eq!(receipt["status"], "recorded");
    let (status, projection) = call(
        &app,
        "GET",
        "/v1/client-errors/attempt-blockhash-001",
        &json!({}),
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(projection["operation_kind"], "initialize_artifact");
    assert_eq!(projection["effect_status"], "rejected_before_submission");
    assert_eq!(projection["evidence_status"], "recorded");
    assert!(projection.get("diagnostic_digest").is_none());
    assert!(projection.get("rpc_request_id").is_none());

    event.attempt_id = "attempt-cryptography-001".into();
    event.operation_kind = "open_access".into();
    event.stage = "recipient_envelope_open".into();
    event.error_code = "recipient_envelope_authentication_failed".into();
    event.effect_status = "none".into();
    event.safe_message =
        "The recipient envelope does not match the key and finalized revision.".into();
    event.source_layer = "cryptography".into();
    event.retry_disposition = "do_not_retry".into();
    event.rpc_code = None;
    event.transaction_error = None;
    let (status, receipt) = call(&app, "POST", "/v1/client-errors", &event).await;
    assert_eq!(status, StatusCode::ACCEPTED);
    assert_eq!(receipt["status"], "recorded");

    event.attempt_id = "attempt-mainnet-001".into();
    event.network = "solana-mainnet".into();
    assert_eq!(
        call(&app, "POST", "/v1/client-errors", &event).await.0,
        StatusCode::BAD_REQUEST
    );

    event.attempt_id = "attempt-unbounded-001".into();
    event.network = "solana-devnet".into();
    event.safe_message = "x".repeat(513);
    assert_eq!(
        call(&app, "POST", "/v1/client-errors", &event).await.0,
        StatusCode::BAD_REQUEST
    );
}

#[tokio::test]
async fn one_wallet_may_bind_distinct_identities_and_exact_registration_resumes() {
    let application =
        Application::memory(FinalityGateway::Mock(MockFinalityGateway::default())).await;
    let app = router(application);
    let shared_wallet = wallet(9);
    let shared_wallet_id = wallet_id(&shared_wallet);
    let (_, a_public) = TestKem::gen_keypair();
    let (_, b_public) = TestKem::gen_keypair();
    let a_public = STANDARD.encode(a_public.to_bytes());
    let b_public = STANDARD.encode(b_public.to_bytes());

    for (operation, identity, encryption_public) in [
        ("shared-register-a", "shared-identity-a", &a_public),
        ("shared-register-b", "shared-identity-b", &b_public),
    ] {
        let message =
            register_message(operation, identity, &shared_wallet_id, encryption_public, 1);
        let request = RegisterIdentityRequest {
            operation_id: operation.into(),
            identity_id: identity.into(),
            wallet_public_key: shared_wallet_id.clone(),
            encryption_public_key: encryption_public.clone(),
            encryption_key_version: 1,
            authorization: authorization(&shared_wallet, message),
        };
        assert_eq!(
            call(&app, "POST", "/v1/identities", &request).await.0,
            StatusCode::OK
        );
    }

    let resume_operation = "shared-register-a-resume";
    let resume_message = register_message(
        resume_operation,
        "shared-identity-a",
        &shared_wallet_id,
        &a_public,
        1,
    );
    let resume = RegisterIdentityRequest {
        operation_id: resume_operation.into(),
        identity_id: "shared-identity-a".into(),
        wallet_public_key: shared_wallet_id.clone(),
        encryption_public_key: a_public,
        encryption_key_version: 1,
        authorization: authorization(&shared_wallet, resume_message),
    };
    let (status, body) = call(&app, "POST", "/v1/identities", &resume).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["status"], "registered");

    let conflict_operation = "shared-register-a-conflict";
    let conflict_message = register_message(
        conflict_operation,
        "shared-identity-a",
        &shared_wallet_id,
        &b_public,
        1,
    );
    let conflict = RegisterIdentityRequest {
        operation_id: conflict_operation.into(),
        identity_id: "shared-identity-a".into(),
        wallet_public_key: shared_wallet_id,
        encryption_public_key: b_public,
        encryption_key_version: 1,
        authorization: authorization(&shared_wallet, conflict_message),
    };
    let (status, body) = call(&app, "POST", "/v1/identities", &conflict).await;
    assert_eq!(status, StatusCode::CONFLICT);
    assert_eq!(body["error"], "identity_binding_conflict");
}

fn wallet(seed: u8) -> SigningKey {
    SigningKey::from_bytes(&[seed; 32])
}

fn wallet_id(key: &SigningKey) -> String {
    bs58::encode(key.verifying_key().to_bytes()).into_string()
}

fn authorization(key: &SigningKey, message: String) -> Authorization {
    Authorization {
        signature_base64: STANDARD.encode(key.sign(message.as_bytes()).to_bytes()),
        message,
    }
}

fn envelope(
    public_key: &<TestKem as Kem>::PublicKey,
    content_key: &[u8; 32],
    aad: &[u8],
) -> Vec<u8> {
    let (encapped, mut sender) = hpke::setup_sender::<TestAead, TestKdf, TestKem>(
        &OpModeS::Base,
        public_key,
        b"CA2-KEP-HOSTED-TEST-v1",
    )
    .unwrap();
    let sealed = sender.seal(content_key, aad).unwrap();
    let encapped = encapped.to_bytes();
    let mut output = Vec::with_capacity(2 + encapped.len() + sealed.len());
    output.extend_from_slice(&(encapped.len() as u16).to_be_bytes());
    output.extend_from_slice(encapped.as_slice());
    output.extend_from_slice(&sealed);
    output
}

fn open_envelope(
    private_key: &<TestKem as Kem>::PrivateKey,
    envelope: &[u8],
    aad: &[u8],
) -> [u8; 32] {
    let length = u16::from_be_bytes([envelope[0], envelope[1]]) as usize;
    let encapped = <TestKem as Kem>::EncappedKey::from_bytes(&envelope[2..2 + length]).unwrap();
    let mut receiver = hpke::setup_receiver::<TestAead, TestKdf, TestKem>(
        &OpModeR::Base,
        private_key,
        &encapped,
        b"CA2-KEP-HOSTED-TEST-v1",
    )
    .unwrap();
    receiver
        .open(&envelope[2 + length..], aad)
        .unwrap()
        .try_into()
        .unwrap()
}

async fn call<T: Serialize>(
    app: &Router,
    method: &str,
    uri: &str,
    payload: &T,
) -> (StatusCode, Value) {
    let response = app
        .clone()
        .oneshot(
            Request::builder()
                .method(method)
                .uri(uri)
                .header("content-type", "application/json")
                .body(Body::from(serde_json::to_vec(payload).unwrap()))
                .unwrap(),
        )
        .await
        .unwrap();
    let status = response.status();
    let bytes = response.into_body().collect().await.unwrap().to_bytes();
    let value = serde_json::from_slice(&bytes)
        .unwrap_or_else(|_| json!({"raw": String::from_utf8_lossy(&bytes)}));
    (status, value)
}

#[tokio::test]
async fn two_independent_identities_complete_grant_decryption_and_reissue() {
    let gateway = MockFinalityGateway::default();
    let application = Application::memory(FinalityGateway::Mock(gateway.clone())).await;
    let app = router(application.clone());
    let a_wallet = wallet(1);
    let b_wallet = wallet(2);
    assert_ne!(a_wallet.verifying_key(), b_wallet.verifying_key());
    let a_wallet_id = wallet_id(&a_wallet);
    let b_wallet_id = wallet_id(&b_wallet);
    let (a_private, a_public) = TestKem::gen_keypair();
    let (b_private, b_public) = TestKem::gen_keypair();
    let (b2_private, b2_public) = TestKem::gen_keypair();
    let a_public_b64 = STANDARD.encode(a_public.to_bytes());
    let b_public_b64 = STANDARD.encode(b_public.to_bytes());
    let b2_public_b64 = STANDARD.encode(b2_public.to_bytes());

    for (operation, identity, wallet_key, wallet_public, encryption_public) in [
        (
            "register-a",
            "identity-a",
            &a_wallet,
            &a_wallet_id,
            &a_public_b64,
        ),
        (
            "register-b",
            "identity-b",
            &b_wallet,
            &b_wallet_id,
            &b_public_b64,
        ),
    ] {
        let message = register_message(operation, identity, wallet_public, encryption_public, 1);
        let request = RegisterIdentityRequest {
            operation_id: operation.into(),
            identity_id: identity.into(),
            wallet_public_key: wallet_public.clone(),
            encryption_public_key: encryption_public.clone(),
            encryption_key_version: 1,
            authorization: authorization(wallet_key, message),
        };
        assert_eq!(
            call(&app, "POST", "/v1/identities", &request).await.0,
            StatusCode::OK
        );
    }

    let artifact_id = "31".repeat(32);
    let policy_id = "32".repeat(32);
    let plaintext = b"KEP-HOST-D3: plaintext and private keys remain client-held";
    let content_key = [42_u8; 32];
    let nonce = [7_u8; 24];
    let cipher = XChaCha20Poly1305::new_from_slice(&content_key).unwrap();
    let content_nonce = XNonce::try_from(nonce.as_slice()).unwrap();
    let ciphertext = cipher
        .encrypt(&content_nonce, plaintext.as_slice())
        .unwrap();
    let mut ciphertext_with_nonce = nonce.to_vec();
    ciphertext_with_nonce.extend_from_slice(&ciphertext);
    let a_envelope = envelope(&a_public, &content_key, artifact_id.as_bytes());
    let b_envelope = envelope(&b_public, &content_key, artifact_id.as_bytes());
    let ciphertext_b64 = STANDARD.encode(&ciphertext_with_nonce);
    let a_envelope_b64 = STANDARD.encode(&a_envelope);
    let ciphertext_digest = sha256_hex(&ciphertext_with_nonce);
    let a_envelope_digest = sha256_hex(&a_envelope);
    let create_message = artifact_message(
        "create-artifact",
        "identity-a",
        &artifact_id,
        &policy_id,
        1,
        &ciphertext_digest,
        &a_envelope_digest,
    );
    let create = CreateArtifactRequest {
        operation_id: "create-artifact".into(),
        artifact_version_id: artifact_id.clone(),
        originator_id: "identity-a".into(),
        policy_id,
        encryption_epoch: 1,
        ciphertext_base64: ciphertext_b64.clone(),
        ciphertext_sha256: ciphertext_digest.clone(),
        originator_envelope_base64: a_envelope_b64,
        originator_envelope_sha256: a_envelope_digest,
        authorization: authorization(&a_wallet, create_message),
    };
    assert_eq!(
        call(&app, "POST", "/v1/artifacts", &create).await.0,
        StatusCode::OK
    );

    let b_envelope_b64 = STANDARD.encode(&b_envelope);
    let b_envelope_digest = sha256_hex(&b_envelope);
    let grant_auth_message = grant_message(
        "grant-a-b",
        &artifact_id,
        "identity-a",
        "identity-b",
        0,
        &b_envelope_digest,
    );
    let mut grant = PrepareGrantRequest {
        operation_id: "grant-a-b".into(),
        artifact_version_id: artifact_id.clone(),
        originator_id: "identity-a".into(),
        recipient_id: "identity-b".into(),
        expected_revision: 0,
        recipient_envelope_base64: b_envelope_b64,
        recipient_envelope_sha256: b_envelope_digest.clone(),
        knowledge_consideration_lamports: 0,
        authorization: authorization(&b_wallet, grant_auth_message.clone()),
    };
    assert_eq!(
        call(&app, "POST", "/v1/grants", &grant).await.0,
        StatusCode::FORBIDDEN
    );
    grant.authorization = authorization(&a_wallet, grant_auth_message);
    assert_eq!(
        call(&app, "POST", "/v1/grants", &grant).await.0,
        StatusCode::OK
    );

    let pre_access_message = access_message(&artifact_id, "identity-b", 0);
    let pre_access = AccessRequest {
        requester_id: "identity-b".into(),
        authorization: authorization(&b_wallet, pre_access_message),
    };
    assert_eq!(
        call(
            &app,
            "POST",
            &format!("/v1/artifacts/{artifact_id}/access"),
            &pre_access
        )
        .await
        .0,
        StatusCode::FORBIDDEN
    );

    gateway
        .record(FinalizedArtifactObservation {
            transaction_signature: "devnet-grant-finalized".into(),
            artifact_version_id: artifact_id.clone(),
            recipient_wallet_public_key: b_wallet_id.clone(),
            recipient_envelope_sha256: b_envelope_digest,
            revision: 1,
            finality: "finalized".into(),
        })
        .await;
    let finalize = FinalizeGrantRequest {
        transaction_signature: "devnet-grant-finalized".into(),
        artifact_account: "mock-artifact-account".into(),
    };
    assert_eq!(
        call(&app, "POST", "/v1/grants/grant-a-b/finalize", &finalize)
            .await
            .0,
        StatusCode::OK
    );

    let access_auth_message = access_message(&artifact_id, "identity-b", 1);
    let access_request = AccessRequest {
        requester_id: "identity-b".into(),
        authorization: authorization(&b_wallet, access_auth_message),
    };
    let (status, access) = call(
        &app,
        "POST",
        &format!("/v1/artifacts/{artifact_id}/access"),
        &access_request,
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    let delivered_envelope = STANDARD
        .decode(access["recipient_envelope_base64"].as_str().unwrap())
        .unwrap();
    let delivered_ciphertext = STANDARD
        .decode(access["ciphertext_base64"].as_str().unwrap())
        .unwrap();
    let opened_key = open_envelope(&b_private, &delivered_envelope, artifact_id.as_bytes());
    let opened_cipher = XChaCha20Poly1305::new_from_slice(&opened_key).unwrap();
    let delivered_nonce = XNonce::try_from(&delivered_ciphertext[..24]).unwrap();
    let opened = opened_cipher
        .decrypt(&delivered_nonce, &delivered_ciphertext[24..])
        .unwrap();
    assert_eq!(opened, plaintext);

    let request_message = reissue_request_message(
        "reissue-b",
        &artifact_id,
        "identity-b",
        1,
        &b2_public_b64,
        2,
        1,
    );
    let reissue = CreateReissueRequest {
        operation_id: "reissue-b".into(),
        artifact_version_id: artifact_id.clone(),
        recipient_id: "identity-b".into(),
        previous_key_version: 1,
        replacement_public_key: b2_public_b64,
        replacement_key_version: 2,
        expected_revision: 1,
        authorization: authorization(&b_wallet, request_message),
    };
    assert_eq!(
        call(&app, "POST", "/v1/reissues", &reissue).await.0,
        StatusCode::OK
    );

    let b2_envelope = envelope(&b2_public, &content_key, artifact_id.as_bytes());
    let b2_envelope_b64 = STANDARD.encode(&b2_envelope);
    let b2_envelope_digest = sha256_hex(&b2_envelope);
    gateway
        .record(FinalizedArtifactObservation {
            transaction_signature: "devnet-reissue-finalized".into(),
            artifact_version_id: artifact_id.clone(),
            recipient_wallet_public_key: b_wallet_id.clone(),
            recipient_envelope_sha256: b2_envelope_digest.clone(),
            revision: 2,
            finality: "finalized".into(),
        })
        .await;
    let fulfill_message = reissue_fulfill_message(
        "reissue-b",
        &artifact_id,
        "identity-a",
        "identity-b",
        1,
        &b2_envelope_digest,
    );
    let fulfill = FulfillReissueRequest {
        originator_id: "identity-a".into(),
        replacement_envelope_base64: b2_envelope_b64,
        replacement_envelope_sha256: b2_envelope_digest.clone(),
        transaction_signature: "devnet-reissue-finalized".into(),
        artifact_account: "mock-artifact-account".into(),
        authorization: authorization(&a_wallet, fulfill_message),
    };
    assert_eq!(
        call(&app, "POST", "/v1/reissues/reissue-b/fulfill", &fulfill)
            .await
            .0,
        StatusCode::OK
    );
    let (replay_status, replay_result) =
        call(&app, "POST", "/v1/reissues/reissue-b/fulfill", &fulfill).await;
    assert_eq!(replay_status, StatusCode::OK);
    assert_eq!(replay_result["status"], "finalized");
    assert_eq!(replay_result["revision"], 2);

    gateway
        .record(FinalizedArtifactObservation {
            transaction_signature: "devnet-reissue-mismatched-replay".into(),
            artifact_version_id: artifact_id.clone(),
            recipient_wallet_public_key: b_wallet_id,
            recipient_envelope_sha256: b2_envelope_digest,
            revision: 2,
            finality: "finalized".into(),
        })
        .await;
    let mut mismatched_replay = fulfill.clone();
    mismatched_replay.transaction_signature = "devnet-reissue-mismatched-replay".into();
    assert_eq!(
        call(
            &app,
            "POST",
            "/v1/reissues/reissue-b/fulfill",
            &mismatched_replay,
        )
        .await
        .0,
        StatusCode::CONFLICT
    );

    let access2_message = access_message(&artifact_id, "identity-b", 2);
    let access2_request = AccessRequest {
        requester_id: "identity-b".into(),
        authorization: authorization(&b_wallet, access2_message),
    };
    let (status, access2) = call(
        &app,
        "POST",
        &format!("/v1/artifacts/{artifact_id}/access"),
        &access2_request,
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    let delivered_b2 = STANDARD
        .decode(access2["recipient_envelope_base64"].as_str().unwrap())
        .unwrap();
    let opened_b2_key = open_envelope(&b2_private, &delivered_b2, artifact_id.as_bytes());
    let opened_b2_cipher = XChaCha20Poly1305::new_from_slice(&opened_b2_key).unwrap();
    let opened_b2 = opened_b2_cipher
        .decrypt(&delivered_nonce, &delivered_ciphertext[24..])
        .unwrap();
    assert_eq!(opened_b2, plaintext);

    let snapshot = application.snapshot().await;
    let artifact = snapshot.artifacts.get(&artifact_id).unwrap();
    assert_eq!(
        artifact.owners.iter().cloned().collect::<Vec<_>>(),
        vec!["identity-a", "identity-b"]
    );
    assert_eq!(artifact.revision, 2);
    assert_eq!(artifact.encryption_epoch, 1);
    let persisted = serde_json::to_vec(&snapshot).unwrap();
    assert!(!persisted
        .windows(plaintext.len())
        .any(|window| window == plaintext));
    assert!(!persisted
        .windows(a_private.to_bytes().len())
        .any(|window| window == a_private.to_bytes().as_slice()));
    assert!(!persisted
        .windows(b_private.to_bytes().len())
        .any(|window| window == b_private.to_bytes().as_slice()));

    println!("PASS third-party vertical: {{A}} -> {{A,B}}, B decrypted exact bytes, reissue revision 2 preserved owners and epoch");
}
