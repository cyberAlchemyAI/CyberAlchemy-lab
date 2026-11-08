//! Isolated public prototype adapters for the Governance/Ontology-Lifecycle v2 map.
//!
//! Canonical events remain in `cal-ontology-lifecycle`; this crate only validates
//! the exact v2 topology and exposes derivative projection envelopes.

use cal_ontology_lifecycle::ReplayFailure;

pub const GOVERNANCE_CONTEXT_ID: &str = "cal.context.governance";
pub const GOVERNANCE_CONTEXT_VERSION: &str = "1.1.0-candidate.1";
pub const ONTOLOGY_LIFECYCLE_CONTEXT_ID: &str = "cal.context.ontology-lifecycle";
pub const ONTOLOGY_LIFECYCLE_CONTEXT_VERSION: &str = "1.1.0-candidate.1";

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct V2ContextMapBinding {
    pub map_ref: &'static str,
    pub map_version: &'static str,
    pub source_context_ref: &'static str,
    pub target_context_ref: &'static str,
    pub direction: &'static str,
}

pub const V2_CONTEXT_MAP: V2ContextMapBinding = V2ContextMapBinding {
    map_ref: "cal.context-map.governance-ontology-lifecycle/v2",
    map_version: "2.0.0-candidate.1",
    source_context_ref: "cal.context.governance/v2",
    target_context_ref: "cal.context.ontology-lifecycle/v2",
    direction: "source-to-target",
};

fn failure(code: &str, detail: impl Into<String>) -> ReplayFailure {
    ReplayFailure {
        code: code.to_owned(),
        detail: detail.into(),
    }
}

fn require_topology(
    context_id: &str,
    context_version: &str,
    expected_id: &str,
    expected_version: &str,
    map_ref: &str,
    direction: &str,
) -> Result<(), ReplayFailure> {
    if context_id != expected_id {
        return Err(failure(
            "CONTEXT_ID_MISMATCH",
            format!("expected {expected_id}; found {context_id}"),
        ));
    }
    if context_version != expected_version {
        return Err(failure(
            "CONTEXT_VERSION_MISMATCH",
            format!("expected {expected_version}; found {context_version}"),
        ));
    }
    if map_ref != V2_CONTEXT_MAP.map_ref {
        return Err(failure(
            "CONTEXT_MAP_MISMATCH",
            format!("expected {}; found {map_ref}", V2_CONTEXT_MAP.map_ref),
        ));
    }
    if direction != V2_CONTEXT_MAP.direction {
        return Err(failure(
            "CONTEXT_DIRECTION_MISMATCH",
            format!("expected {}; found {direction}", V2_CONTEXT_MAP.direction),
        ));
    }
    Ok(())
}

pub mod ontology_lifecycle_v2 {
    use super::*;
    use cal_ontology_lifecycle::{AuthorityEffect, ContextProjection, ContextSelector, EventStore};
    use serde::{Deserialize, Serialize};

    #[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
    #[serde(deny_unknown_fields)]
    pub struct ContextProjectionRequestV2 {
        pub context_id: String,
        pub context_version: String,
        pub context_map_ref: String,
        pub direction: String,
        pub selector_ref: String,
        pub selector: ContextSelector,
    }

    #[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
    #[serde(deny_unknown_fields)]
    pub struct ContextProjectionEnvelopeV2 {
        pub schema_version: String,
        pub context_ref: String,
        pub context_map_ref: String,
        pub authority_effect: AuthorityEffect,
        pub canonical_replay_source: bool,
        pub source_cursor: u64,
        pub source_event_set_digest: String,
        pub projection: ContextProjection,
    }

    #[derive(Clone, Copy, Debug)]
    pub struct OntologyLifecycleContextAdapterV2<'a> {
        store: &'a EventStore,
    }
    impl<'a> OntologyLifecycleContextAdapterV2<'a> {
        pub fn new(store: &'a EventStore) -> Self {
            Self { store }
        }
        pub fn project(
            &self,
            request: &ContextProjectionRequestV2,
        ) -> Result<ContextProjectionEnvelopeV2, ReplayFailure> {
            project_ontology_lifecycle_context_v2(self.store, request)
        }
    }

    pub fn project_ontology_lifecycle_context_v2(
        store: &EventStore,
        request: &ContextProjectionRequestV2,
    ) -> Result<ContextProjectionEnvelopeV2, ReplayFailure> {
        require_topology(
            &request.context_id,
            &request.context_version,
            ONTOLOGY_LIFECYCLE_CONTEXT_ID,
            ONTOLOGY_LIFECYCLE_CONTEXT_VERSION,
            &request.context_map_ref,
            &request.direction,
        )?;
        let projection = store.context_projection(&request.selector_ref, &request.selector)?;
        Ok(ContextProjectionEnvelopeV2 {
            schema_version: "cal-context-projection-envelope/v2-prototype".to_owned(),
            context_ref: V2_CONTEXT_MAP.target_context_ref.to_owned(),
            context_map_ref: V2_CONTEXT_MAP.map_ref.to_owned(),
            authority_effect: AuthorityEffect::None,
            canonical_replay_source: false,
            source_cursor: projection.source_cursor,
            source_event_set_digest: projection.source_event_set_digest.clone(),
            projection,
        })
    }
}

pub mod governance_v2 {
    use super::*;
    use cal_ontology_lifecycle::{
        AuthorityEffect, ContextProjection, ContextSelector, EventStore, GovernedOntologyNodeView,
        SubjectKind,
    };
    use serde::{Deserialize, Serialize};

    #[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
    #[serde(deny_unknown_fields)]
    pub struct GovernanceProjectionRequestV2 {
        pub context_id: String,
        pub context_version: String,
        pub context_map_ref: String,
        pub direction: String,
        pub selector_ref: String,
        pub selector: ContextSelector,
    }

    #[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
    #[serde(deny_unknown_fields)]
    pub struct GovernanceProjectionEnvelopeV2 {
        pub schema_version: String,
        pub context_ref: String,
        pub context_map_ref: String,
        pub authority_effect: AuthorityEffect,
        pub canonical_replay_source: bool,
        pub source_cursor: u64,
        pub source_event_set_digest: String,
        pub projection: ContextProjection,
        pub governed_nodes: Vec<GovernedOntologyNodeView>,
    }

    #[derive(Clone, Copy, Debug)]
    pub struct GovernanceContextAdapterV2<'a> {
        store: &'a EventStore,
    }
    impl<'a> GovernanceContextAdapterV2<'a> {
        pub fn new(store: &'a EventStore) -> Self {
            Self { store }
        }
        pub fn project(
            &self,
            request: &GovernanceProjectionRequestV2,
        ) -> Result<GovernanceProjectionEnvelopeV2, ReplayFailure> {
            project_governance_context_v2(self.store, request)
        }
    }

    pub fn project_governance_context_v2(
        store: &EventStore,
        request: &GovernanceProjectionRequestV2,
    ) -> Result<GovernanceProjectionEnvelopeV2, ReplayFailure> {
        require_topology(
            &request.context_id,
            &request.context_version,
            GOVERNANCE_CONTEXT_ID,
            GOVERNANCE_CONTEXT_VERSION,
            &request.context_map_ref,
            &request.direction,
        )?;
        let projection = store.context_projection(&request.selector_ref, &request.selector)?;
        let mut governed_nodes = request
            .selector
            .required_subject_set
            .iter()
            .filter(|x| x.subject_kind == SubjectKind::Node)
            .map(|x| {
                store.governed_node_view(
                    x,
                    request.selector.semantic_cursor,
                    Some(request.selector_ref.clone()),
                )
            })
            .collect::<Result<Vec<_>, _>>()?;
        governed_nodes.sort_by(|a, b| a.identity.cmp(&b.identity));
        Ok(GovernanceProjectionEnvelopeV2 {
            schema_version: "cal-governance-projection-envelope/v2-prototype".to_owned(),
            context_ref: V2_CONTEXT_MAP.source_context_ref.to_owned(),
            context_map_ref: V2_CONTEXT_MAP.map_ref.to_owned(),
            authority_effect: AuthorityEffect::None,
            canonical_replay_source: false,
            source_cursor: projection.source_cursor,
            source_event_set_digest: projection.source_event_set_digest.clone(),
            projection,
            governed_nodes,
        })
    }
}
