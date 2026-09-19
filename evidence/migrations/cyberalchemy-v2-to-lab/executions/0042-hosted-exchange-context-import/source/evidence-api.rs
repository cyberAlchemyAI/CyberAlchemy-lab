use std::{
    sync::{
        atomic::{AtomicU64, Ordering},
        Arc,
    },
    time::{SystemTime, UNIX_EPOCH},
};

use axum::{
    extract::{Path, State},
    http::{header::HeaderName, HeaderValue, StatusCode},
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use serde::Serialize;
use tokio::sync::RwLock;

use crate::{
    auth::{
        access_message, artifact_message, decode_base64, grant_message, register_message,
        reissue_fulfill_message, reissue_request_message, validate_id, verify_digest,
        verify_wallet_signature,
    },
    finality::FinalityGateway,
    model::{
        AccessRequest, AccessResponse, Artifact, ClientErrorEventReceipt, ClientErrorEventRequest,
        CreateArtifactRequest, CreateReissueRequest, Database, FinalizeGrantRequest,
        FulfillReissueRequest, GrantStatus, KnowledgeIdentity, OperationResponse,
        PrepareGrantRequest, PreparedGrant, RecipientEnvelope, RegisterIdentityRequest,
        ReissueRequest, ReissueStatus, SafeAttemptProjection, StateResponse,
    },
    store::Persistence,
    CAPABILITY_ID, PROGRAM_ID,
};

#[path = "file_routes.rs"]
mod file_routes;
#[path = "account_routes.rs"]
mod account_routes;

const MAX_ENCRYPTED_BYTES: usize = 4 * 1024 * 1024;
static ERROR_SEQUENCE: AtomicU64 = AtomicU64::new(1);

#[derive(Clone)]
pub struct Application {
    database: Arc<RwLock<Database>>,
    persistence: Persistence,
    finality: FinalityGateway,
    clock: Arc<dyn Fn() -> u64 + Send + Sync>,
    limits: crate::limits::Limits,
    admission: Arc<crate::limits::Admission>,
    transfers: crate::response_admission::TransferPool,
}

impl Application {
    pub async fn memory(finality: FinalityGateway) -> Self {
        Self {
            database: Arc::new(RwLock::new(Database::default())),
            persistence: Persistence::Memory,
            finality,
            limits: crate::limits::Limits::default(),
            admission: Arc::new(crate::limits::Admission::new(&crate::limits::Limits::default())),
            clock: Arc::new(crate::clock::process_clock()),
            transfers: crate::response_admission::TransferPool::new(4),
        }
    }

    pub async fn postgres(database_url: &str, finality: FinalityGateway) -> Result<Self, String> {
        let persistence = Persistence::postgres(database_url).await?;
        let database = persistence.load().await?;
        Ok(Self {
            database: Arc::new(RwLock::new(database)),
            persistence,
            finality,
            limits: crate::limits::Limits::default(),
            admission: Arc::new(crate::limits::Admission::new(&crate::limits::Limits::default())),
            clock: Arc::new(crate::clock::process_clock()),
            transfers: crate::response_admission::TransferPool::new(4),
        })
    }

    /// Inject a clock for deterministic lifecycle tests, before serving requests.
    pub fn with_clock(mut self, clock: impl Fn() -> u64 + Send + Sync + 'static) -> Self {
        self.clock = Arc::new(clock);
        self
    }

    /// Configure before serving; each application has one shared limiter.
    pub fn with_limits(mut self, limits: crate::limits::Limits) -> Self {
        self.admission = Arc::new(crate::limits::Admission::new(&limits));
        self.limits = limits;
        self
    }

    pub async fn snapshot(&self) -> Database {
        self.database.read().await.clone()
    }
}

pub fn router(application: Application) -> Router {
    Router::new()
        .merge(file_routes::routes())
        .merge(account_routes::routes())
        .route("/health", get(health))
        .route("/ready", get(readiness))
        .route("/v1/identities", post(register_identity))
        .route("/v1/artifacts", post(create_artifact))
        .route("/v1/artifacts/{artifact_id}", get(artifact_state))
        .route("/v1/artifacts/{artifact_id}/access", post(access))
        .route("/v1/grants", post(prepare_grant))
        .route("/v1/grants/{operation_id}/finalize", post(finalize_grant))
        .route("/v1/reissues", post(request_reissue))
        .route("/v1/reissues/{operation_id}/fulfill", post(fulfill_reissue))
        .route("/v1/client-errors", post(record_client_error))
        .route("/v1/client-errors/{attempt_id}", get(client_error_state))
        .layer(axum::middleware::from_fn_with_state(application.clone(), bound_request))
        .with_state(application)
}

#[derive(Serialize)]
struct Health<'a> {
    status: &'a str,
    capability_id: &'a str,
    network: &'a str,
    program_id: &'a str,
    custody: &'a str,
}

async fn health() -> Json<Health<'static>> {
    Json(Health {
        status: "ok",
        capability_id: CAPABILITY_ID,
        network: "solana-devnet",
        program_id: PROGRAM_ID,
        custody: "ciphertext-only",
    })
}

async fn readiness(State(app): State<Application>) -> impl IntoResponse {
    let ready = app.persistence.ready().await;
    (if ready { StatusCode::OK } else { StatusCode::SERVICE_UNAVAILABLE },
     [(axum::http::header::CACHE_CONTROL, "no-store")],
     Json(serde_json::json!({"status": if ready { "ready" } else { "unavailable" }})))
}

#[derive(Debug)]
struct ApiError {
    status: StatusCode,
    code: &'static str,
    message: String,
}

impl ApiError {
    fn bad(code: &'static str, message: impl Into<String>) -> Self {
        Self {
            status: StatusCode::BAD_REQUEST,
            code,
            message: message.into(),
        }
    }

    fn capacity(message: impl Into<String>) -> Self {
        Self { status: StatusCode::INSUFFICIENT_STORAGE, code: "storage_capacity", message: message.into() }
    }

    fn forbidden(message: impl Into<String>) -> Self {
        Self {
            status: StatusCode::FORBIDDEN,
            code: "authorization_rejected",
            message: message.into(),
        }
    }

    fn conflict(message: impl Into<String>) -> Self {
        Self::conflict_code("state_conflict", message)
    }

    fn conflict_code(code: &'static str, message: impl Into<String>) -> Self {
        Self {
            status: StatusCode::CONFLICT,
            code,
            message: message.into(),
        }
    }

    fn missing(message: impl Into<String>) -> Self {
        Self {
            status: StatusCode::NOT_FOUND,
            code: "not_found",
            message: message.into(),
        }
    }

    fn unavailable(message: impl Into<String>) -> Self {
        Self {
            status: StatusCode::SERVICE_UNAVAILABLE,
            code: "dependency_unavailable",
            message: message.into(),
        }
    }
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let mut response = (
            self.status,
            Json(serde_json::json!({"error": self.code, "message": self.message})),
        )
            .into_response();
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|duration| duration.as_millis())
            .unwrap_or_default();
        let correlation = format!(
            "kep-{timestamp:x}-{:x}",
            ERROR_SEQUENCE.fetch_add(1, Ordering::Relaxed)
        );
        if let Ok(value) = HeaderValue::from_str(&correlation) {
            response
                .headers_mut()
                .insert(HeaderName::from_static("x-ca2-error-id"), value);
        }
        response
    }
}

fn input(error: String) -> ApiError {
    ApiError::bad("invalid_input", error)
}

fn validate_safe_text(value: &str, label: &str, max_bytes: usize) -> Result<(), ApiError> {
    if value.is_empty()
        || value.len() > max_bytes
        || value.chars().any(|character| character.is_control())
    {
        return Err(ApiError::bad(
            "invalid_client_error",
            format!("{label} is empty, too long, or contains control characters"),
        ));
    }
    Ok(())
}

async fn record_client_error(
    State(app): State<Application>,
    Json(request): Json<ClientErrorEventRequest>,
) -> Result<(StatusCode, Json<ClientErrorEventReceipt>), ApiError> {
    validate_id(&request.attempt_id, "attempt_id").map_err(input)?;
    for (value, label) in [
        (&request.operation_kind, "operation_kind"),
        (&request.stage, "stage"),
        (&request.error_code, "error_code"),
    ] {
        validate_id(value, label).map_err(input)?;
    }
    if !matches!(
        request.effect_status.as_str(),
        "none"
            | "rejected_before_submission"
            | "submission_attempted_unknown"
            | "submitted_finality_unknown"
            | "finalized_failure"
            | "finalized_success"
            | "unknown"
    ) {
        return Err(ApiError::bad(
            "invalid_client_error",
            "effect_status is not recognized",
        ));
    }
    if request.network != "solana-devnet" {
        return Err(ApiError::bad(
            "invalid_client_error",
            "only solana-devnet client evidence is accepted",
        ));
    }
    if !matches!(request.reporter.as_str(), "client" | "server") {
        return Err(ApiError::bad(
            "invalid_client_error",
            "reporter must be client or server",
        ));
    }
    if request.registry_version != "kep-error-registry/v1" {
        return Err(ApiError::bad(
            "invalid_client_error",
            "registry_version is not supported",
        ));
    }
    if !matches!(
        request.source_layer.as_str(),
        "wallet"
            | "transport"
            | "http"
            | "json_rpc"
            | "transaction"
            | "instruction"
            | "program"
            | "finality"
            | "hosted_api"
            | "client_input"
            | "cryptography"
            | "unknown"
    ) {
        return Err(ApiError::bad(
            "invalid_client_error",
            "source_layer is not recognized",
        ));
    }
    if !matches!(
        request.retry_disposition.as_str(),
        "user_may_retry_fresh"
            | "wait_then_retry"
            | "refresh_state_before_retry"
            | "inspect_before_retry"
            | "do_not_retry"
    ) {
        return Err(ApiError::bad(
            "invalid_client_error",
            "retry_disposition is not recognized",
        ));
    }
    if request
        .http_status
        .is_some_and(|status| !(100..=599).contains(&status))
    {
        return Err(ApiError::bad(
            "invalid_client_error",
            "http_status is outside the HTTP status range",
        ));
    }
    validate_safe_text(&request.safe_message, "safe_message", 512)?;
    if request.diagnostic_digest.len() != 64
        || !request
            .diagnostic_digest
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit())
    {
        return Err(ApiError::bad(
            "invalid_client_error",
            "diagnostic_digest must be 32-byte hexadecimal",
        ));
    }
    if let Some(value) = request.rpc_request_id.as_deref() {
        validate_safe_text(value, "rpc_request_id", 128)?;
    }
    if let Some(value) = request.transaction_signature.as_deref() {
        validate_safe_text(value, "transaction_signature", 128)?;
    }
    for (value, label, max_bytes) in [
        (
            request.transaction_error.as_deref(),
            "transaction_error",
            256,
        ),
        (
            request.instruction_error.as_deref(),
            "instruction_error",
            256,
        ),
        (request.program_id.as_deref(), "program_id", 128),
        (request.correlation_id.as_deref(), "correlation_id", 128),
    ] {
        if let Some(value) = value {
            validate_safe_text(value, label, max_bytes)?;
        }
    }
    let mut guard = app.database.write().await;
    if let Some(existing) = guard.client_errors.get(&request.attempt_id) {
        if serde_json::to_value(existing).map_err(|_| ApiError::unavailable("Cannot compare telemetry"))?
            != serde_json::to_value(&request).map_err(|_| ApiError::unavailable("Cannot compare telemetry"))? {
            return Err(ApiError::conflict("attempt already bound to different telemetry"));
        }
        // Retry only the separate journal, whose insert is itself idempotent.
        drop(guard);
        app.persistence.record_client_error(&request).await.map_err(ApiError::unavailable)?;
        return Ok((StatusCode::ACCEPTED, Json(ClientErrorEventReceipt {attempt_id: request.attempt_id, status: "recorded".into()})));
    }
    let mut candidate = guard.clone();
    candidate
        .client_errors
        .insert(request.attempt_id.clone(), request.clone());
    app.limits.validate_growth(&guard, &candidate).map_err(ApiError::capacity)?;
    app.persistence
        .save(&candidate, "client_error_recorded", &request.attempt_id)
        .await
        .map_err(ApiError::unavailable)?;
    *guard = candidate;
    drop(guard);
    app.persistence
        .record_client_error(&request)
        .await
        .map_err(ApiError::unavailable)?;
    Ok((
        StatusCode::ACCEPTED,
        Json(ClientErrorEventReceipt {
            attempt_id: request.attempt_id,
            status: "recorded".into(),
        }),
    ))
}

async fn client_error_state(
    State(app): State<Application>,
    Path(attempt_id): Path<String>,
) -> Result<Json<SafeAttemptProjection>, ApiError> {
    validate_id(&attempt_id, "attempt_id").map_err(input)?;
    let guard = app.database.read().await;
    let event = guard
        .client_errors
        .get(&attempt_id)
        .ok_or_else(|| ApiError::missing("attempt evidence is not registered"))?;
    Ok(Json(SafeAttemptProjection::from(event)))
}

fn identity<'a>(
    database: &'a Database,
    identity_id: &str,
) -> Result<&'a KnowledgeIdentity, ApiError> {
    database
        .identities
        .get(identity_id)
        .ok_or_else(|| ApiError::missing(format!("identity {identity_id} is not registered")))
}

async fn register_identity(
    State(app): State<Application>,
    Json(request): Json<RegisterIdentityRequest>,
) -> Result<Json<OperationResponse>, ApiError> {
    validate_id(&request.operation_id, "operation_id").map_err(input)?;
    validate_id(&request.identity_id, "identity_id").map_err(input)?;
    if request.encryption_key_version == 0 {
        return Err(ApiError::bad(
            "invalid_key_version",
            "encryption key version must be positive",
        ));
    }
    if decode_base64(&request.encryption_public_key, "encryption public key")
        .map_err(input)?
        .len()
        != 32
    {
        return Err(ApiError::bad(
            "invalid_encryption_key",
            "encryption public key must contain 32 bytes",
        ));
    }
    let expected = register_message(
        &request.operation_id,
        &request.identity_id,
        &request.wallet_public_key,
        &request.encryption_public_key,
        request.encryption_key_version,
    );
    verify_wallet_signature(
        &request.wallet_public_key,
        &request.authorization,
        &expected,
    )
    .map_err(ApiError::forbidden)?;

    let mut guard = app.database.write().await;
    if guard.consumed_operations.contains(&request.operation_id) {
        return Err(ApiError::conflict_code(
            "operation_replay_conflict",
            "registration operation already exists",
        ));
    }
    if let Some(existing) = guard.identities.get(&request.identity_id) {
        if existing.wallet_public_key == request.wallet_public_key
            && existing.encryption_public_key == request.encryption_public_key
            && existing.encryption_key_version == request.encryption_key_version
        {
            return Ok(Json(OperationResponse {
                operation_id: request.operation_id,
                status: "registered".into(),
                revision: 0,
            }));
        }
        return Err(ApiError::conflict_code(
            "identity_binding_conflict",
            "identity exists with a different wallet or encryption-key binding",
        ));
    }
    let mut candidate = guard.clone();
    candidate.identities.insert(
        request.identity_id.clone(),
        KnowledgeIdentity {
            identity_id: request.identity_id.clone(),
            wallet_public_key: request.wallet_public_key,
            encryption_public_key: request.encryption_public_key,
            encryption_key_version: request.encryption_key_version,
        },
    );
    candidate
        .consumed_operations
        .insert(request.operation_id.clone());
    app.limits.validate_growth(&guard, &candidate).map_err(ApiError::capacity)?;
    app.persistence
        .save(&candidate, "identity_registered", &request.identity_id)
        .await
        .map_err(ApiError::unavailable)?;
    *guard = candidate;
    Ok(Json(OperationResponse {
        operation_id: request.operation_id,
        status: "registered".into(),
        revision: 0,
    }))
}

async fn create_artifact(
    State(app): State<Application>,
    Json(request): Json<CreateArtifactRequest>,
) -> Result<Json<OperationResponse>, ApiError> {
    validate_id(&request.operation_id, "operation_id").map_err(input)?;
    validate_id(&request.artifact_version_id, "artifact_version_id").map_err(input)?;
    validate_id(&request.policy_id, "policy_id").map_err(input)?;
    if request.encryption_epoch == 0 {
        return Err(ApiError::bad(
            "invalid_epoch",
            "encryption epoch must be positive",
        ));
    }
    let ciphertext = verify_digest(
        &request.ciphertext_base64,
        &request.ciphertext_sha256,
        "ciphertext",
    )
    .map_err(input)?;
    if ciphertext.is_empty() || ciphertext.len() > MAX_ENCRYPTED_BYTES {
        return Err(ApiError::bad(
            "invalid_ciphertext_size",
            "ciphertext must contain 1 to 4194304 bytes",
        ));
    }
    verify_digest(
        &request.originator_envelope_base64,
        &request.originator_envelope_sha256,
        "originator envelope",
    )
    .map_err(input)?;

    let mut guard = app.database.write().await;
    let originator = identity(&guard, &request.originator_id)?.clone();
    let expected = artifact_message(
        &request.operation_id,
        &request.originator_id,
        &request.artifact_version_id,
        &request.policy_id,
        request.encryption_epoch,
        &request.ciphertext_sha256,
        &request.originator_envelope_sha256,
    );
    verify_wallet_signature(
        &originator.wallet_public_key,
        &request.authorization,
        &expected,
    )
    .map_err(ApiError::forbidden)?;
    if guard.consumed_operations.contains(&request.operation_id)
        || guard.artifacts.contains_key(&request.artifact_version_id)
    {
        return Err(ApiError::conflict("artifact or operation already exists"));
    }
    let mut candidate = guard.clone();
    candidate.artifacts.insert(
        request.artifact_version_id.clone(),
        Artifact {
            artifact_version_id: request.artifact_version_id.clone(),
            originator_id: request.originator_id.clone(),
            policy_id: request.policy_id,
            encryption_epoch: request.encryption_epoch,
            ciphertext_base64: request.ciphertext_base64,
            ciphertext_sha256: request.ciphertext_sha256,
            owners: std::iter::once(request.originator_id.clone()).collect(),
            envelopes: std::iter::once((
                request.originator_id.clone(),
                RecipientEnvelope {
                    recipient_id: request.originator_id,
                    key_version: originator.encryption_key_version,
                    envelope_base64: request.originator_envelope_base64,
                    envelope_sha256: request.originator_envelope_sha256,
                },
            ))
            .collect(),
            revision: 0,
        },
    );
    candidate
        .consumed_operations
        .insert(request.operation_id.clone());
    app.limits.validate_growth(&guard, &candidate).map_err(ApiError::capacity)?;
    app.persistence
        .save(
            &candidate,
            "artifact_prepared",
            &request.artifact_version_id,
        )
        .await
        .map_err(ApiError::unavailable)?;
    *guard = candidate;
    Ok(Json(OperationResponse {
        operation_id: request.operation_id,
        status: "prepared".into(),
        revision: 0,
    }))
}

async fn prepare_grant(
    State(app): State<Application>,
    Json(request): Json<PrepareGrantRequest>,
) -> Result<Json<OperationResponse>, ApiError> {
    validate_id(&request.operation_id, "operation_id").map_err(input)?;
    if request.knowledge_consideration_lamports != 0 {
        return Err(ApiError::bad(
            "knowledge_price_forbidden",
            "this capability permits zero knowledge consideration only",
        ));
    }
    verify_digest(
        &request.recipient_envelope_base64,
        &request.recipient_envelope_sha256,
        "recipient envelope",
    )
    .map_err(input)?;
    let mut guard = app.database.write().await;
    let originator = identity(&guard, &request.originator_id)?.clone();
    let recipient = identity(&guard, &request.recipient_id)?.clone();
    let artifact = guard
        .artifacts
        .get(&request.artifact_version_id)
        .ok_or_else(|| ApiError::missing("artifact is not registered"))?;
    if artifact.originator_id != request.originator_id
        || artifact.revision != request.expected_revision
    {
        return Err(ApiError::conflict(
            "originator or expected revision does not match current state",
        ));
    }
    if artifact.owners.contains(&request.recipient_id) {
        return Err(ApiError::conflict("recipient is already an owner"));
    }
    let expected = grant_message(
        &request.operation_id,
        &request.artifact_version_id,
        &request.originator_id,
        &request.recipient_id,
        request.expected_revision,
        &request.recipient_envelope_sha256,
    );
    verify_wallet_signature(
        &originator.wallet_public_key,
        &request.authorization,
        &expected,
    )
    .map_err(ApiError::forbidden)?;
    if guard.grants.contains_key(&request.operation_id)
        || guard.consumed_operations.contains(&request.operation_id)
    {
        return Err(ApiError::conflict("grant operation already exists"));
    }
    let mut candidate = guard.clone();
    candidate.grants.insert(
        request.operation_id.clone(),
        PreparedGrant {
            operation_id: request.operation_id.clone(),
            artifact_version_id: request.artifact_version_id,
            originator_id: request.originator_id,
            recipient_id: request.recipient_id.clone(),
            expected_revision: request.expected_revision,
            envelope: RecipientEnvelope {
                recipient_id: request.recipient_id,
                key_version: recipient.encryption_key_version,
                envelope_base64: request.recipient_envelope_base64,
                envelope_sha256: request.recipient_envelope_sha256,
            },
            status: GrantStatus::Prepared,
            transaction_signature: None,
        },
    );
    app.limits.validate_growth(&guard, &candidate).map_err(ApiError::capacity)?;
    app.persistence
        .save(&candidate, "grant_prepared", &request.operation_id)
        .await
        .map_err(ApiError::unavailable)?;
    *guard = candidate;
    Ok(Json(OperationResponse {
        operation_id: request.operation_id,
        status: "prepared".into(),
        revision: request.expected_revision,
    }))
}

async fn finalize_grant(
    State(app): State<Application>,
    Path(operation_id): Path<String>,
    Json(request): Json<FinalizeGrantRequest>,
) -> Result<Json<OperationResponse>, ApiError> {
    let expected_transition = {
        let db=app.database.read().await;
        let grant=db.grants.get(&operation_id).ok_or_else(||ApiError::missing("prepared grant is not registered"))?;
        if grant.status!=GrantStatus::Prepared {return Err(ApiError::conflict("grant is already finalized"));}
        let recipient=identity(&db,&grant.recipient_id)?;
        crate::transition::TransitionExpectation {
            artifact_id:grant.artifact_version_id.clone(), originator_wallet:identity(&db,&grant.originator_id)?.wallet_public_key.clone(),
            recipient_wallet:recipient.wallet_public_key.clone(), recipient_key_base64:recipient.encryption_public_key.clone(),
            envelope_sha256:grant.envelope.envelope_sha256.clone(), expected_revision:grant.expected_revision,
            grant_operation_id:Some(operation_id.clone()),
        }
    };
    let observation = app
        .finality
        .observe_transition(&request.transaction_signature, &request.artifact_account, &expected_transition)
        .await
        .map_err(ApiError::unavailable)?;
    let mut guard = app.database.write().await;
    let grant = guard
        .grants
        .get(&operation_id)
        .cloned()
        .ok_or_else(|| ApiError::missing("prepared grant is not registered"))?;
    if grant.status != GrantStatus::Prepared {
        return Err(ApiError::conflict("grant is already finalized"));
    }
    let recipient = identity(&guard, &grant.recipient_id)?;
    if recipient.encryption_public_key != expected_transition.recipient_key_base64
        || observation.finality != "finalized"
        || observation.artifact_version_id != grant.artifact_version_id
        || observation.recipient_wallet_public_key != recipient.wallet_public_key
        || observation.recipient_envelope_sha256 != grant.envelope.envelope_sha256
        || observation.revision != grant.expected_revision + 1
    {
        return Err(ApiError::conflict(
            "finalized observation does not match the prepared grant",
        ));
    }
    let mut candidate = guard.clone();
    let artifact = candidate
        .artifacts
        .get_mut(&grant.artifact_version_id)
        .ok_or_else(|| ApiError::missing("artifact is not registered"))?;
    if artifact.revision != grant.expected_revision
        || !artifact.owners.contains(&grant.originator_id)
    {
        return Err(ApiError::conflict(
            "artifact changed after grant preparation",
        ));
    }
    artifact.owners.insert(grant.recipient_id.clone());
    artifact
        .envelopes
        .insert(grant.recipient_id.clone(), grant.envelope.clone());
    artifact.revision = observation.revision;
    let finalized = candidate
        .grants
        .get_mut(&operation_id)
        .expect("grant exists in clone");
    finalized.status = GrantStatus::Finalized;
    finalized.transaction_signature = Some(request.transaction_signature);
    candidate.consumed_operations.insert(operation_id.clone());
    app.limits.validate_growth(&guard, &candidate).map_err(ApiError::capacity)?;
    app.persistence
        .save(&candidate, "grant_finalized", &operation_id)
        .await
        .map_err(ApiError::unavailable)?;
    *guard = candidate;
    Ok(Json(OperationResponse {
        operation_id,
        status: "finalized".into(),
        revision: observation.revision,
    }))
}

async fn access(
    State(app): State<Application>,
    Path(artifact_id): Path<String>,
    Json(request): Json<AccessRequest>,
) -> Result<Json<AccessResponse>, ApiError> {
    let guard = app.database.read().await;
    if guard.files.contains_key(&artifact_id) {
        return Err(ApiError::bad(
            "file_access_required",
            "use the file access endpoint",
        ));
    }
    let requester = identity(&guard, &request.requester_id)?;
    let artifact = guard
        .artifacts
        .get(&artifact_id)
        .ok_or_else(|| ApiError::missing("artifact is not registered"))?;
    if !artifact.owners.contains(&request.requester_id) {
        return Err(ApiError::forbidden("requester is not a current owner"));
    }
    let expected = access_message(&artifact_id, &request.requester_id, artifact.revision);
    verify_wallet_signature(
        &requester.wallet_public_key,
        &request.authorization,
        &expected,
    )
    .map_err(ApiError::forbidden)?;
    let envelope = artifact
        .envelopes
        .get(&request.requester_id)
        .ok_or_else(|| ApiError::conflict("current owner has no active envelope"))?;
    Ok(Json(AccessResponse {
        artifact_version_id: artifact.artifact_version_id.clone(),
        ciphertext_base64: artifact.ciphertext_base64.clone(),
        ciphertext_sha256: artifact.ciphertext_sha256.clone(),
        recipient_envelope_base64: envelope.envelope_base64.clone(),
        recipient_envelope_sha256: envelope.envelope_sha256.clone(),
        encryption_epoch: artifact.encryption_epoch,
        revision: artifact.revision,
    }))
}

async fn request_reissue(
    State(app): State<Application>,
    Json(request): Json<CreateReissueRequest>,
) -> Result<Json<OperationResponse>, ApiError> {
    validate_id(&request.operation_id, "operation_id").map_err(input)?;
    if decode_base64(
        &request.replacement_public_key,
        "replacement encryption public key",
    )
    .map_err(input)?
    .len()
        != 32
    {
        return Err(ApiError::bad(
            "invalid_encryption_key",
            "replacement encryption public key must contain 32 bytes",
        ));
    }
    let mut guard = app.database.write().await;
    let recipient = identity(&guard, &request.recipient_id)?.clone();
    let artifact = guard
        .artifacts
        .get(&request.artifact_version_id)
        .ok_or_else(|| ApiError::missing("artifact is not registered"))?;
    if !artifact.owners.contains(&request.recipient_id)
        || artifact.revision != request.expected_revision
        || recipient.encryption_key_version != request.previous_key_version
        || request.replacement_key_version <= request.previous_key_version
    {
        return Err(ApiError::conflict(
            "reissue request does not match current owner, revision or key version",
        ));
    }
    let expected = reissue_request_message(
        &request.operation_id,
        &request.artifact_version_id,
        &request.recipient_id,
        request.previous_key_version,
        &request.replacement_public_key,
        request.replacement_key_version,
        request.expected_revision,
    );
    verify_wallet_signature(
        &recipient.wallet_public_key,
        &request.authorization,
        &expected,
    )
    .map_err(ApiError::forbidden)?;
    if guard.reissues.contains_key(&request.operation_id)
        || guard.consumed_operations.contains(&request.operation_id)
    {
        return Err(ApiError::conflict("reissue operation already exists"));
    }
    let mut candidate = guard.clone();
    candidate.reissues.insert(
        request.operation_id.clone(),
        ReissueRequest {
            operation_id: request.operation_id.clone(),
            artifact_version_id: request.artifact_version_id,
            recipient_id: request.recipient_id,
            previous_key_version: request.previous_key_version,
            replacement_public_key: request.replacement_public_key,
            replacement_key_version: request.replacement_key_version,
            expected_revision: request.expected_revision,
            status: ReissueStatus::Requested,
            transaction_signature: None,
        },
    );
    app.limits.validate_growth(&guard, &candidate).map_err(ApiError::capacity)?;
    app.persistence
        .save(&candidate, "reissue_requested", &request.operation_id)
        .await
        .map_err(ApiError::unavailable)?;
    *guard = candidate;
    Ok(Json(OperationResponse {
        operation_id: request.operation_id,
        status: "requested".into(),
        revision: request.expected_revision,
    }))
}

async fn fulfill_reissue(
    State(app): State<Application>,
    Path(operation_id): Path<String>,
    Json(request): Json<FulfillReissueRequest>,
) -> Result<Json<OperationResponse>, ApiError> {
    verify_digest(
        &request.replacement_envelope_base64,
        &request.replacement_envelope_sha256,
        "replacement envelope",
    )
    .map_err(input)?;
    let expected_transition = {
        let db=app.database.read().await;
        let reissue=db.reissues.get(&operation_id).ok_or_else(||ApiError::missing("reissue request is not registered"))?;
        let artifact=db.artifacts.get(&reissue.artifact_version_id).ok_or_else(||ApiError::missing("artifact is not registered"))?;
        if artifact.originator_id!=request.originator_id {return Err(ApiError::forbidden("originator mismatch"));}
        let originator=identity(&db,&request.originator_id)?;
        verify_wallet_signature(&originator.wallet_public_key,&request.authorization,&reissue_fulfill_message(
            &operation_id,&reissue.artifact_version_id,&request.originator_id,&reissue.recipient_id,reissue.expected_revision,&request.replacement_envelope_sha256
        )).map_err(ApiError::forbidden)?;
        crate::transition::TransitionExpectation {
            artifact_id:reissue.artifact_version_id.clone(),originator_wallet:originator.wallet_public_key.clone(),
            recipient_wallet:identity(&db,&reissue.recipient_id)?.wallet_public_key.clone(),recipient_key_base64:reissue.replacement_public_key.clone(),
            envelope_sha256:request.replacement_envelope_sha256.clone(),expected_revision:reissue.expected_revision,grant_operation_id:None,
        }
    };
    let observation = app
        .finality
        .observe_transition(&request.transaction_signature, &request.artifact_account, &expected_transition)
        .await
        .map_err(ApiError::unavailable)?;
    let mut guard = app.database.write().await;
    let reissue = guard
        .reissues
        .get(&operation_id)
        .cloned()
        .ok_or_else(|| ApiError::missing("reissue request is not registered"))?;
    let is_exact_replay_candidate = reissue.status == ReissueStatus::Finalized;
    let artifact = guard
        .artifacts
        .get(&reissue.artifact_version_id)
        .ok_or_else(|| ApiError::missing("artifact is not registered"))?;
    let expected_artifact_revision = if is_exact_replay_candidate {
        reissue.expected_revision + 1
    } else {
        reissue.expected_revision
    };
    if artifact.originator_id != request.originator_id
        || artifact.revision != expected_artifact_revision
    {
        return Err(ApiError::conflict(
            "originator or artifact revision changed after request",
        ));
    }
    let originator = identity(&guard, &request.originator_id)?;
    let recipient = identity(&guard, &reissue.recipient_id)?;
    let expected = reissue_fulfill_message(
        &operation_id,
        &reissue.artifact_version_id,
        &request.originator_id,
        &reissue.recipient_id,
        reissue.expected_revision,
        &request.replacement_envelope_sha256,
    );
    verify_wallet_signature(
        &originator.wallet_public_key,
        &request.authorization,
        &expected,
    )
    .map_err(ApiError::forbidden)?;
    if observation.finality != "finalized"
        || observation.artifact_version_id != reissue.artifact_version_id
        || observation.recipient_wallet_public_key != recipient.wallet_public_key
        || observation.recipient_envelope_sha256 != request.replacement_envelope_sha256
        || observation.revision != reissue.expected_revision + 1
    {
        return Err(ApiError::conflict(
            "finalized observation does not match the requested reissue",
        ));
    }
    if is_exact_replay_candidate {
        let stored_envelope = artifact
            .envelopes
            .get(&reissue.recipient_id)
            .ok_or_else(|| ApiError::conflict("finalized reissue has no recipient envelope"))?;
        let is_exact_replay = reissue.transaction_signature.as_deref()
            == Some(request.transaction_signature.as_str())
            && stored_envelope.recipient_id == reissue.recipient_id
            && stored_envelope.key_version == reissue.replacement_key_version
            && stored_envelope.envelope_base64 == request.replacement_envelope_base64
            && stored_envelope.envelope_sha256 == request.replacement_envelope_sha256
            && recipient.encryption_public_key == reissue.replacement_public_key
            && recipient.encryption_key_version == reissue.replacement_key_version;
        if !is_exact_replay {
            return Err(ApiError::conflict(
                "finalized reissue replay does not match the committed result",
            ));
        }
        return Ok(Json(OperationResponse {
            operation_id,
            status: "finalized".into(),
            revision: observation.revision,
        }));
    }
    let mut candidate = guard.clone();
    let artifact = candidate
        .artifacts
        .get_mut(&reissue.artifact_version_id)
        .expect("artifact exists in clone");
    let owners_before = artifact.owners.clone();
    let epoch_before = artifact.encryption_epoch;
    let policy_before = artifact.policy_id.clone();
    artifact.envelopes.insert(
        reissue.recipient_id.clone(),
        RecipientEnvelope {
            recipient_id: reissue.recipient_id.clone(),
            key_version: reissue.replacement_key_version,
            envelope_base64: request.replacement_envelope_base64,
            envelope_sha256: request.replacement_envelope_sha256,
        },
    );
    artifact.revision = observation.revision;
    if artifact.owners != owners_before
        || artifact.encryption_epoch != epoch_before
        || artifact.policy_id != policy_before
    {
        return Err(ApiError::conflict(
            "reissue attempted to change protected state",
        ));
    }
    let updated_identity = candidate
        .identities
        .get_mut(&reissue.recipient_id)
        .expect("recipient exists in clone");
    updated_identity.encryption_public_key = reissue.replacement_public_key;
    updated_identity.encryption_key_version = reissue.replacement_key_version;
    let finalized = candidate
        .reissues
        .get_mut(&operation_id)
        .expect("reissue exists in clone");
    finalized.status = ReissueStatus::Finalized;
    finalized.transaction_signature = Some(request.transaction_signature);
    candidate.consumed_operations.insert(operation_id.clone());
    app.limits.validate_growth(&guard, &candidate).map_err(ApiError::capacity)?;
    app.persistence
        .save(&candidate, "reissue_finalized", &operation_id)
        .await
        .map_err(ApiError::unavailable)?;
    *guard = candidate;
    Ok(Json(OperationResponse {
        operation_id,
        status: "finalized".into(),
        revision: observation.revision,
    }))
}

async fn artifact_state(
    State(app): State<Application>,
    Path(artifact_id): Path<String>,
) -> Result<Json<StateResponse>, ApiError> {
    let guard = app.database.read().await;
    let artifact = guard
        .artifacts
        .get(&artifact_id)
        .ok_or_else(|| ApiError::missing("artifact is not registered"))?;
    Ok(Json(StateResponse {
        artifact_version_id: artifact.artifact_version_id.clone(),
        owners: artifact.owners.clone(),
        revision: artifact.revision,
        encryption_epoch: artifact.encryption_epoch,
    }))
}

async fn bound_request(
    State(app): State<Application>, request: axum::extract::Request, next: axum::middleware::Next,
) -> Response {
    if let Some(axum::extract::ConnectInfo(clock)) = request.extensions().get::<axum::extract::ConnectInfo<crate::transport::TransferClock>>() {
        if clock.wait_idle().await.is_err() { return ApiError::unavailable("Connection closed; retry on a new connection.").into_response(); }
    }
    if matches!(request.uri().path(), "/health" | "/ready") { return next.run(request).await; }
    let limited = |retry: u64| {
        (StatusCode::TOO_MANY_REQUESTS, [("retry-after", retry.to_string()), ("cache-control", "no-store".into())],
         Json(serde_json::json!({"error":"request_capacity","message":"Service is busy. Wait before trying again."}))).into_response()
    };
    let _permit = match app.admission.permits.clone().try_acquire_owned() {
        Ok(permit) => permit, Err(_) => return limited(1),
    };
    let telemetry = request.uri().path() == "/v1/client-errors";
    if let Err(retry) = app.admission.admit(&app.limits, telemetry) { return limited(retry); }
    // Bound slow/oversized request bodies without cancelling a database write.
    // The permit is acquired before reading any body bytes.
    let body_limit = match request.uri().path() {
        "/v1/files" => crate::files::MAX_FILE_REQUEST,
        "/v1/account/write" => 1_500_000,
        _ => 2 * 1024 * 1024,
    };
    let (parts, body) = request.into_parts();
    let bytes = match tokio::time::timeout(std::time::Duration::from_secs(15), axum::body::to_bytes(body, body_limit)).await {
        Err(_) => return (StatusCode::REQUEST_TIMEOUT, Json(serde_json::json!({"error":"request_timeout","message":"Request body timed out."}))).into_response(),
        Ok(Err(_)) => return (StatusCode::PAYLOAD_TOO_LARGE, Json(serde_json::json!({"error":"request_body_rejected","message":"Request body is invalid or exceeds its limit."}))).into_response(),
        Ok(Ok(bytes)) => bytes,
    };
    next.run(axum::extract::Request::from_parts(parts, axum::body::Body::from(bytes))).await
}
