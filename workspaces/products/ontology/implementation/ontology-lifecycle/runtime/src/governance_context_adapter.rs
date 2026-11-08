//! Governance Context projection adapter.
//!
//! Governance meaning remains owned by the Governance Context. This adapter
//! only joins exact governance events to semantic events selected from the same
//! event-store cut; it cannot create or infer an owner decision.

use crate::{
    AuthorityEffect, ContextProjection, ContextSelector, EventStore, GovernedOntologyNodeView,
    ReplayFailure, SubjectKind,
};
use serde::{Deserialize, Serialize};

pub const GOVERNANCE_CONTEXT_ID: &str = "cal.context.governance";
pub const GOVERNANCE_CONTEXT_VERSION: &str = "1.0.0-candidate.1";

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ExactGovernanceProjectionRequest {
    pub context_id: String,
    pub context_version: String,
    pub selector_ref: String,
    pub selector: ContextSelector,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct GovernanceProjectionEnvelope {
    pub schema_version: String,
    pub context_id: String,
    pub context_version: String,
    pub context_status: String,
    pub authority_effect: AuthorityEffect,
    pub canonical_replay_source: bool,
    pub source_cursor: u64,
    pub source_event_set_digest: String,
    pub projection: ContextProjection,
    pub governed_nodes: Vec<GovernedOntologyNodeView>,
}

#[derive(Clone, Copy, Debug)]
pub struct GovernanceContextAdapter<'a> {
    store: &'a EventStore,
}

impl<'a> GovernanceContextAdapter<'a> {
    pub fn new(store: &'a EventStore) -> Self {
        Self { store }
    }

    pub fn project(
        &self,
        request: &ExactGovernanceProjectionRequest,
    ) -> Result<GovernanceProjectionEnvelope, ReplayFailure> {
        project_governance_context(self.store, request)
    }
}

pub fn project_governance_context(
    store: &EventStore,
    request: &ExactGovernanceProjectionRequest,
) -> Result<GovernanceProjectionEnvelope, ReplayFailure> {
    require_governance_context(&request.context_id, &request.context_version)?;
    let projection = store.context_projection(&request.selector_ref, &request.selector)?;

    let mut governed_nodes = request
        .selector
        .required_subject_set
        .iter()
        .filter(|identity| identity.subject_kind == SubjectKind::Node)
        .map(|identity| {
            store.governed_node_view(
                identity,
                request.selector.semantic_cursor,
                Some(request.selector_ref.clone()),
            )
        })
        .collect::<Result<Vec<_>, _>>()?;
    governed_nodes.sort_by(|left, right| left.identity.cmp(&right.identity));

    Ok(GovernanceProjectionEnvelope {
        schema_version: "cal-governance-projection-envelope/v1-candidate".to_owned(),
        context_id: GOVERNANCE_CONTEXT_ID.to_owned(),
        context_version: GOVERNANCE_CONTEXT_VERSION.to_owned(),
        context_status: "candidate-unadmitted".to_owned(),
        authority_effect: AuthorityEffect::None,
        canonical_replay_source: false,
        source_cursor: projection.source_cursor,
        source_event_set_digest: projection.source_event_set_digest.clone(),
        projection,
        governed_nodes,
    })
}

fn require_governance_context(actual_id: &str, actual_version: &str) -> Result<(), ReplayFailure> {
    if actual_id != GOVERNANCE_CONTEXT_ID {
        return Err(ReplayFailure {
            code: "CONTEXT_ID_MISMATCH".to_owned(),
            detail: format!("expected {GOVERNANCE_CONTEXT_ID}; found {actual_id}"),
        });
    }
    if actual_version != GOVERNANCE_CONTEXT_VERSION {
        return Err(ReplayFailure {
            code: "CONTEXT_VERSION_MISMATCH".to_owned(),
            detail: format!("expected {GOVERNANCE_CONTEXT_VERSION}; found {actual_version}"),
        });
    }
    Ok(())
}
