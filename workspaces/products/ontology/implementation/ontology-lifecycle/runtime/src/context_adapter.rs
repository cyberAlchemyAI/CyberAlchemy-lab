//! Ontology Lifecycle Context projection adapter.
//!
//! The adapter is a read model over one exact event-store cut. It never accepts
//! a projection as a replay source and carries no authority effect.

use crate::{AuthorityEffect, ContextProjection, ContextSelector, EventStore, ReplayFailure};
use serde::{Deserialize, Serialize};

pub const ONTOLOGY_LIFECYCLE_CONTEXT_ID: &str = "cal.context.ontology-lifecycle";
pub const ONTOLOGY_LIFECYCLE_CONTEXT_VERSION: &str = "1.0.0-candidate.1";

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ContextProjectionRequest {
    pub context_id: String,
    pub context_version: String,
    pub selector_ref: String,
    pub selector: ContextSelector,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ContextProjectionEnvelope {
    pub schema_version: String,
    pub context_id: String,
    pub context_version: String,
    pub context_status: String,
    pub authority_effect: AuthorityEffect,
    pub canonical_replay_source: bool,
    pub source_cursor: u64,
    pub source_event_set_digest: String,
    pub projection: ContextProjection,
}

#[derive(Clone, Copy, Debug)]
pub struct OntologyLifecycleContextAdapter<'a> {
    store: &'a EventStore,
}

impl<'a> OntologyLifecycleContextAdapter<'a> {
    pub fn new(store: &'a EventStore) -> Self {
        Self { store }
    }

    pub fn project(
        &self,
        request: &ContextProjectionRequest,
    ) -> Result<ContextProjectionEnvelope, ReplayFailure> {
        project_ontology_lifecycle_context(self.store, request)
    }
}

pub fn project_ontology_lifecycle_context(
    store: &EventStore,
    request: &ContextProjectionRequest,
) -> Result<ContextProjectionEnvelope, ReplayFailure> {
    require_exact_context(
        &request.context_id,
        &request.context_version,
        ONTOLOGY_LIFECYCLE_CONTEXT_ID,
        ONTOLOGY_LIFECYCLE_CONTEXT_VERSION,
    )?;
    let projection = store.context_projection(&request.selector_ref, &request.selector)?;
    Ok(ContextProjectionEnvelope {
        schema_version: "cal-context-projection-envelope/v1-candidate".to_owned(),
        context_id: ONTOLOGY_LIFECYCLE_CONTEXT_ID.to_owned(),
        context_version: ONTOLOGY_LIFECYCLE_CONTEXT_VERSION.to_owned(),
        context_status: "candidate-unadmitted".to_owned(),
        authority_effect: AuthorityEffect::None,
        canonical_replay_source: false,
        source_cursor: projection.source_cursor,
        source_event_set_digest: projection.source_event_set_digest.clone(),
        projection,
    })
}

fn require_exact_context(
    actual_id: &str,
    actual_version: &str,
    expected_id: &str,
    expected_version: &str,
) -> Result<(), ReplayFailure> {
    if actual_id != expected_id {
        return Err(ReplayFailure {
            code: "CONTEXT_ID_MISMATCH".to_owned(),
            detail: format!("expected {expected_id}; found {actual_id}"),
        });
    }
    if actual_version != expected_version {
        return Err(ReplayFailure {
            code: "CONTEXT_VERSION_MISMATCH".to_owned(),
            detail: format!("expected {expected_version}; found {actual_version}"),
        });
    }
    Ok(())
}
