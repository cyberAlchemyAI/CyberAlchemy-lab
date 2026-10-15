# Complete current contract planning coverage

Status: inventory and proposed consumer mapping; authority effect: none.

Selected registries: 121 current Artifact Types / 143 registered versions; 41 Relation Kinds; 189 Definition versions / 183 current identities.

[Machine matrix](contract-coverage.json) records exact schema selectors/digests, root/payload required fields, descriptor relation roles, and every declared Relation Kind endpoint pair/qualifier contract. Each current carrier has planned consumer tasks. This proves inventory coverage, not workflow execution or instance conformance. Definition semantic revisions are not proposed automatically; C02 resolves selected semantic fit and exact references.

## Every current Artifact Type

| Coverage | Exact current carrier | Proposed consumer tasks |
| --- | --- | --- |
| TYPE-001 | `cal.artifact-type.admission-transaction/v1` | C07, C02 |
| TYPE-002 | `cal.artifact-type.agent-action/v1` | W02, C08 |
| TYPE-003 | `cal.artifact-type.agent-assignment/v1` | W02, C08 |
| TYPE-004 | `cal.artifact-type.agent-capability/v1` | W02, C08 |
| TYPE-005 | `cal.artifact-type.agent-instance/v1` | W02, C08 |
| TYPE-006 | `cal.artifact-type.agent-profile/v1` | W02, C08 |
| TYPE-007 | `cal.artifact-type.agent-reflection/v1` | W02, C08 |
| TYPE-008 | `cal.artifact-type.agent-session/v1` | W02, C08 |
| TYPE-009 | `cal.artifact-type.artifact-type/v3` | C02, W01 |
| TYPE-010 | `cal.artifact-type.artifact-type-registry/v2` | C02, W01 |
| TYPE-011 | `cal.artifact-type.artifact-type-request/v1` | C02, W01 |
| TYPE-012 | `cal.artifact-type.authority-boundary/v1` | C07, C02 |
| TYPE-013 | `cal.artifact-type.authority-claim/v1` | W02, C08 |
| TYPE-014 | `cal.artifact-type.bounded-context/v3` | C08, W01, O03 |
| TYPE-015 | `cal.artifact-type.canonical-package-manifest/v1` | O04, O05, R06 |
| TYPE-016 | `cal.artifact-type.capability-instance/v2` | R01, R04 |
| TYPE-017 | `cal.artifact-type.capability-realization-binding/v2` | R01, R04 |
| TYPE-018 | `cal.artifact-type.challenge-contract/v1` | W05, O02 |
| TYPE-019 | `cal.artifact-type.challenge-event/v1` | W05, O02 |
| TYPE-020 | `cal.artifact-type.classification-assignment/v1` | W05, O02 |
| TYPE-021 | `cal.artifact-type.classification-scheme/v1` | W05, O02 |
| TYPE-022 | `cal.artifact-type.classification-value/v1` | W05, O02 |
| TYPE-023 | `cal.artifact-type.communication-preference/v1` | W01, R03 |
| TYPE-024 | `cal.artifact-type.constitution/v1` | C02, W01 |
| TYPE-025 | `cal.artifact-type.context/v1` | C08, W01, O03 |
| TYPE-026 | `cal.artifact-type.context-lineage-record/v2` | C08, W01, O03 |
| TYPE-027 | `cal.artifact-type.context-map/v3` | C08, W01, O03 |
| TYPE-028 | `cal.artifact-type.context-migration-manifest/v2` | O04, O05, R06 |
| TYPE-029 | `cal.artifact-type.context-profile/v1` | C08, W01, O03 |
| TYPE-030 | `cal.artifact-type.context-request/v1` | C08, W01, O03 |
| TYPE-031 | `cal.artifact-type.context-view/v1` | C08, W01, O03 |
| TYPE-032 | `cal.artifact-type.contract/v1` | C02, W01 |
| TYPE-033 | `cal.artifact-type.coordination-context/v2` | W01, W03 |
| TYPE-034 | `cal.artifact-type.decision/v2` | C07, C02 |
| TYPE-035 | `cal.artifact-type.decision-bundle/v1` | C07, C02 |
| TYPE-036 | `cal.artifact-type.decision-checkpoint/v1` | C07, C02 |
| TYPE-037 | `cal.artifact-type.decision-scope/v2` | C07, C02 |
| TYPE-038 | `cal.artifact-type.definition/v2` | C02, W01 |
| TYPE-039 | `cal.artifact-type.definition-registry/v1` | C02, W01 |
| TYPE-040 | `cal.artifact-type.delegation/v1` | W02, C08 |
| TYPE-041 | `cal.artifact-type.drift-assessment/v1` | C02, W01 |
| TYPE-042 | `cal.artifact-type.drift-audit/v1` | C02, W01 |
| TYPE-043 | `cal.artifact-type.effect/v1` | C07, C02 |
| TYPE-044 | `cal.artifact-type.evaluation/v1` | W04 |
| TYPE-045 | `cal.artifact-type.evaluation-profile/v1` | W04 |
| TYPE-046 | `cal.artifact-type.evidence-set/v1` | W05, O02 |
| TYPE-047 | `cal.artifact-type.experiment-design/v1` | W04 |
| TYPE-048 | `cal.artifact-type.experiment-run/v1` | W04 |
| TYPE-049 | `cal.artifact-type.failure-assessment/v1` | W05, O02 |
| TYPE-050 | `cal.artifact-type.failure-control-binding/v1` | W05, O02 |
| TYPE-051 | `cal.artifact-type.failure-mode/v1` | W05, O02 |
| TYPE-052 | `cal.artifact-type.failure-occurrence/v1` | W05, O02 |
| TYPE-053 | `cal.artifact-type.feedback-record/v1` | W01, R03 |
| TYPE-054 | `cal.artifact-type.finding/v1` | W05, O02 |
| TYPE-055 | `cal.artifact-type.foundation-manifest/v1` | O04, O05, R06 |
| TYPE-056 | `cal.artifact-type.generated-output/v2` | C07, C02 |
| TYPE-057 | `cal.artifact-type.goal/v1` | W01, W03 |
| TYPE-058 | `cal.artifact-type.governance-event-history/v1` | O01, O02, O03 |
| TYPE-059 | `cal.artifact-type.governed-model/v1` | C02, W01 |
| TYPE-060 | `cal.artifact-type.hypothesis/v1` | W04 |
| TYPE-061 | `cal.artifact-type.identity-claim/v1` | W02, C08 |
| TYPE-062 | `cal.artifact-type.identity-graph/v1` | W02, C08 |
| TYPE-063 | `cal.artifact-type.identity-lineage/v1` | W02, C08 |
| TYPE-064 | `cal.artifact-type.implementation/v1` | C08, W03, R04 |
| TYPE-065 | `cal.artifact-type.improvement-signal/v1` | W06 |
| TYPE-066 | `cal.artifact-type.improvement-target/v1` | W06 |
| TYPE-067 | `cal.artifact-type.incident/v1` | W05, O02 |
| TYPE-068 | `cal.artifact-type.intent/v1` | W01, W03 |
| TYPE-069 | `cal.artifact-type.intent-resolution/v1` | W01, W03 |
| TYPE-070 | `cal.artifact-type.lesson-application/v1` | W06 |
| TYPE-071 | `cal.artifact-type.lesson-outcome-assessment/v1` | W06 |
| TYPE-072 | `cal.artifact-type.lifecycle-profile/v1` | C02, W01 |
| TYPE-073 | `cal.artifact-type.measurement-method/v1` | W04 |
| TYPE-074 | `cal.artifact-type.measurement-result/v1` | W04 |
| TYPE-075 | `cal.artifact-type.method-binding/v1` | W04 |
| TYPE-076 | `cal.artifact-type.model-instance-binding/v1` | C02, W01 |
| TYPE-077 | `cal.artifact-type.observation/v1` | W05, O02 |
| TYPE-078 | `cal.artifact-type.ontology/v1` | O01, O02, O03 |
| TYPE-079 | `cal.artifact-type.ontology-cut/v1` | O01, O02, O03 |
| TYPE-080 | `cal.artifact-type.ontology-edge/v1` | O01, O02, O03 |
| TYPE-081 | `cal.artifact-type.ontology-manifest/v1` | O01, O02, O03 |
| TYPE-082 | `cal.artifact-type.ontology-node/v2` | O01, O02, O03 |
| TYPE-083 | `cal.artifact-type.ontology-package/v1` | O01, O02, O03 |
| TYPE-084 | `cal.artifact-type.ontology-view/v1` | O01, O02, O03 |
| TYPE-085 | `cal.artifact-type.operational-lesson/v1` | W06 |
| TYPE-086 | `cal.artifact-type.operational-observation/v1` | W05, O02 |
| TYPE-087 | `cal.artifact-type.owner-registry/v1` | W02, C08 |
| TYPE-088 | `cal.artifact-type.person/v1` | W02, C08 |
| TYPE-089 | `cal.artifact-type.person-reference/v1` | W02, C08 |
| TYPE-090 | `cal.artifact-type.policy/v2` | C07, C02 |
| TYPE-091 | `cal.artifact-type.preference-application-assessment/v1` | W01, R03 |
| TYPE-092 | `cal.artifact-type.principal/v1` | W02, C08 |
| TYPE-093 | `cal.artifact-type.principal-reference/v1` | W02, C08 |
| TYPE-094 | `cal.artifact-type.product-capability/v1` | R01, R04 |
| TYPE-095 | `cal.artifact-type.product-identity/v2` | R01, R04 |
| TYPE-096 | `cal.artifact-type.product-thesis/v1` | R01, R04 |
| TYPE-097 | `cal.artifact-type.project-governance-event-history/v2` | C07, C02 |
| TYPE-098 | `cal.artifact-type.project-identity/v1` | C02, W01 |
| TYPE-099 | `cal.artifact-type.project-semantic-event-history/v2` | C07, C02 |
| TYPE-100 | `cal.artifact-type.project-state/v2` | C07, C02 |
| TYPE-101 | `cal.artifact-type.relation-kind/v2` | C02, C14, W01, O01 |
| TYPE-102 | `cal.artifact-type.repository-migration-manifest/v1` | C02, W01 |
| TYPE-103 | `cal.artifact-type.research-inquiry/v1` | W04 |
| TYPE-104 | `cal.artifact-type.research-run/v1` | W04 |
| TYPE-105 | `cal.artifact-type.responsibility/v1` | W02, C08 |
| TYPE-106 | `cal.artifact-type.review/v1` | C07, C02 |
| TYPE-107 | `cal.artifact-type.role/v1` | W02, C08 |
| TYPE-108 | `cal.artifact-type.role-assignment/v1` | W02, C08 |
| TYPE-109 | `cal.artifact-type.schema/v1` | C02, W01 |
| TYPE-110 | `cal.artifact-type.semantic-event-history/v1` | O01, O02, O03 |
| TYPE-111 | `cal.artifact-type.source/v1` | O04, O05, R06 |
| TYPE-112 | `cal.artifact-type.source-admission/v1` | O04, O05, R06 |
| TYPE-113 | `cal.artifact-type.team/v1` | W02, C08 |
| TYPE-114 | `cal.artifact-type.team-membership/v1` | W02, C08 |
| TYPE-115 | `cal.artifact-type.tool/v1` | W02 |
| TYPE-116 | `cal.artifact-type.typed-relation/v3` | C02, C14, W01, O01 |
| TYPE-117 | `cal.artifact-type.ubiquitous-language/v2` | C02, W01 |
| TYPE-118 | `cal.artifact-type.user-decision-preference/v1` | W01, R03 |
| TYPE-119 | `cal.artifact-type.work/v1` | W01, W03 |
| TYPE-120 | `cal.artifact-type.work-outcome-assessment/v1` | W01, W03 |
| TYPE-121 | `cal.artifact-type.workflow-decision-profile/v1` | C02, W01 |

## Every current Relation Kind

All entries are checked by C02/W01/O01 for selected endpoints, qualifiers, typed-axis non-collapse and local/global separation. No new connection is inferred from this mapping.

| Coverage | Relation Kind | Typed axis | Exact pairs | Required qualifier axes |
| --- | --- | --- | --- | --- |
| REL-001 | `relation.acts-for` | `axis.bounded-representation` | 1 | delegation_ref, scope_ref, effective_period, revocation_state |
| REL-002 | `relation.addresses-improvement-target` | `axis.improvement-target-addressing` | 1 | target_version_ref, addressing_role |
| REL-003 | `relation.addresses-intent` | `axis.intent-addressing` | 6 | intent_resolution_ref, addressing_role |
| REL-004 | `relation.affects` | `axis.scoped-impact` | 22 | impact_scope, evidence_posture |
| REL-005 | `relation.applies-lesson` | `axis.lesson-application` | 1 | lesson_revision_ref, application_posture, applicability_assessment_ref, instruction_precedence |
| REL-006 | `relation.asserts-identity-of` | `axis.identity-assertion` | 4 | assertion_kind, claim_scope |
| REL-007 | `relation.assigned-to` | `axis.assignment` | 6 | assignment_kind, relation_record_ref |
| REL-008 | `relation.binds-implementation` | `axis.implementation-binding` | 2 | binding_role |
| REL-009 | `relation.carries-definition` | `axis.semantic-contract` | 1 | definition_version_ref, definition_sha256 |
| REL-010 | `relation.challenges` | `axis.contestability-target` | 100 | challenge_contract_ref, challenge_mode, challenged_version_ref |
| REL-011 | `relation.conforms-to` | `axis.conformance` | 3 | conformance_scope, exact_version_ref, conformance_evidence_refs |
| REL-012 | `relation.consumes-view` | `axis.view-consumption` | 2 | view_digest, cursor, consumption_purpose |
| REL-013 | `relation.contributes-to` | `axis.contribution` | 8 | contribution_role, contribution_scope |
| REL-014 | `relation.controls` | `axis.failure-control` | 1 | control_role, control_version_ref, installation_posture |
| REL-015 | `relation.declares-effect-on` | `axis.decision-effect` | 21 | effect_kind, exact_target_version_ref |
| REL-016 | `relation.derives-from` | `axis.derivation` | 40 | derivation_role |
| REL-017 | `relation.engages-inquiry` | `axis.inquiry-engagement` | 4 | inquiry_role |
| REL-018 | `relation.evaluates` | `axis.evaluation` | 16 | evaluation_role, evaluation_purpose |
| REL-019 | `relation.evidence-bears-on` | `axis.evidence-polarity` | 72 | polarity |
| REL-020 | `relation.frames` | `axis.context-framing` | 5 | framing_role |
| REL-021 | `relation.fulfills-request` | `axis.request-fulfillment` | 1 | fulfillment_role |
| REL-022 | `relation.governed-by` | `axis.governance-applicability` | 29 | governance_role |
| REL-023 | `relation.has-capability` | `axis.agent-capability-declaration` | 2 | capability_version_ref, declaration_basis |
| REL-024 | `relation.inherits-contract` | `axis.contract-inheritance` | 1 | binding_ref, contract_version_ref |
| REL-025 | `relation.instance-of` | `axis.classification` | 12 | parent_version_ref, binding_ref |
| REL-026 | `relation.materializes-consequence` | `axis.transaction-consequence-materialization` | 4 | application_receipt_ref, consequence_role, output_digest |
| REL-027 | `relation.member-of` | `axis.membership` | 24 | membership_role |
| REL-028 | `relation.occurs-during` | `axis.occurrence-envelope` | 5 | envelope_version_ref, temporal_scope |
| REL-029 | `relation.originates-from` | `axis.origin-lineage` | 7 | origin_role |
| REL-030 | `relation.performs` | `axis.agent-performance-attribution` | 5 | session_ref, participation_role, action_posture |
| REL-031 | `relation.produces` | `axis.attributable-production` | 19 | action_receipt_ref, production_role, output_posture |
| REL-032 | `relation.profiled-by` | `axis.agent-profile-binding` | 1 | profile_version_ref, binding_ref |
| REL-033 | `relation.realizes` | `axis.realization` | 2 | realization_role, exact_target_version_ref |
| REL-034 | `relation.requests-resolution-of` | `axis.context-resolution-request` | 1 | context_version_ref |
| REL-035 | `relation.responds-to` | `axis.operational-response` | 2 | response_role, intended_outcome |
| REL-036 | `relation.scopes-authority-over` | `axis.authority-scope` | 3 | authority_role, scope_ref |
| REL-037 | `relation.successor-of` | `axis.lifecycle-succession` | 100 | succession_effect |
| REL-038 | `relation.tests-hypothesis` | `axis.hypothesis-testing` | 1 | hypothesis_version_ref, test_role |
| REL-039 | `relation.uses-method` | `axis.method-dependency` | 7 | usage_role |
| REL-040 | `relation.uses-tool` | `axis.tool-use` | 4 | tool_version_ref, invocation_contract_ref, use_role |
| REL-041 | `relation.violates` | `axis.boundary-violation` | 4 | boundary_version_ref, evidence_posture |
