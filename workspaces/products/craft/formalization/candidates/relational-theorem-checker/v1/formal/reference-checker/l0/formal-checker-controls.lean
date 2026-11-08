import FixtureGraphs
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace Relational.Controls
open Relational Relational.Fixtures

theorem conformsTo_pair_1 : checkGraph (pairGraph .conformsTo .capabilityInstance .contract) = true := by decide

theorem conformsTo_pair_2 : checkGraph (pairGraph .conformsTo .capabilityInstance .governedModel) = true := by decide

theorem conformsTo_pair_3 : checkGraph (pairGraph .conformsTo .context .contextProfile) = true := by decide

theorem declaresEffectOn_pair_1 : checkGraph (pairGraph .declaresEffectOn .decision .agentCapability) = true := by decide

theorem declaresEffectOn_pair_2 : checkGraph (pairGraph .declaresEffectOn .decision .agentProfile) = true := by decide

theorem declaresEffectOn_pair_3 : checkGraph (pairGraph .declaresEffectOn .decision .artifactType) = true := by decide

theorem declaresEffectOn_pair_4 : checkGraph (pairGraph .declaresEffectOn .decision .capabilityRealizationBinding) = true := by decide

theorem declaresEffectOn_pair_5 : checkGraph (pairGraph .declaresEffectOn .decision .challengeEvent) = true := by decide

theorem declaresEffectOn_pair_6 : checkGraph (pairGraph .declaresEffectOn .decision .classificationAssignment) = true := by decide

theorem declaresEffectOn_pair_7 : checkGraph (pairGraph .declaresEffectOn .decision .communicationPreference) = true := by decide

theorem declaresEffectOn_pair_8 : checkGraph (pairGraph .declaresEffectOn .decision .definition) = true := by decide

theorem declaresEffectOn_pair_9 : checkGraph (pairGraph .declaresEffectOn .decision .delegation) = true := by decide

theorem declaresEffectOn_pair_10 : checkGraph (pairGraph .declaresEffectOn .decision .effect) = true := by decide

theorem declaresEffectOn_pair_11 : checkGraph (pairGraph .declaresEffectOn .decision .failureAssessment) = true := by decide

theorem declaresEffectOn_pair_12 : checkGraph (pairGraph .declaresEffectOn .decision .failureControlBinding) = true := by decide

theorem declaresEffectOn_pair_13 : checkGraph (pairGraph .declaresEffectOn .decision .failureMode) = true := by decide

theorem declaresEffectOn_pair_14 : checkGraph (pairGraph .declaresEffectOn .decision .failureOccurrence) = true := by decide

theorem declaresEffectOn_pair_15 : checkGraph (pairGraph .declaresEffectOn .decision .governedModel) = true := by decide

theorem declaresEffectOn_pair_16 : checkGraph (pairGraph .declaresEffectOn .decision .improvementTarget) = true := by decide

theorem declaresEffectOn_pair_17 : checkGraph (pairGraph .declaresEffectOn .decision .incident) = true := by decide

theorem declaresEffectOn_pair_18 : checkGraph (pairGraph .declaresEffectOn .decision .intentResolution) = true := by decide

theorem declaresEffectOn_pair_19 : checkGraph (pairGraph .declaresEffectOn .decision .operationalLesson) = true := by decide

theorem declaresEffectOn_pair_20 : checkGraph (pairGraph .declaresEffectOn .decision .productCapability) = true := by decide

theorem declaresEffectOn_pair_21 : checkGraph (pairGraph .declaresEffectOn .decision .relationKind) = true := by decide

theorem materializesConsequence_pair_1 : checkGraph (pairGraph .materializesConsequence .admissionTransaction .generatedOutput) = true := by decide

theorem materializesConsequence_pair_2 : checkGraph (pairGraph .materializesConsequence .admissionTransaction .projectGovernanceEventHistory) = true := by decide

theorem materializesConsequence_pair_3 : checkGraph (pairGraph .materializesConsequence .admissionTransaction .projectSemanticEventHistory) = true := by decide

theorem materializesConsequence_pair_4 : checkGraph (pairGraph .materializesConsequence .admissionTransaction .projectState) = true := by decide

theorem all_three_kinds : checkGraph validGraph = true := by decide

theorem valid_addition : checkAddition baseGraph materializes = true := by decide

theorem conformance_coexists_with_admission : checkGraph graphWithAdmission = true := by decide

theorem distinct_effect_value : checkGraph { validGraph with assertions := [{ declares with qualifiers := .effect "adoption" "v1" }] } = true := by decide

theorem phantom_conformance_pair : checkGraph (pairGraph .conformsTo .capabilityInstance .contextProfile) = false := by decide

theorem reversed_pair : checkGraph (pairGraph .conformsTo .contract .capabilityInstance) = false := by decide

theorem phantom_effect_pair : checkGraph (pairGraph .declaresEffectOn .decision .contract) = false := by decide

theorem phantom_materialization_pair : checkGraph (pairGraph .materializesConsequence .decision .generatedOutput) = false := by decide

theorem wrong_qualifier_constructor : checkGraph { validGraph with assertions := [{ conforms with qualifiers := .effect "admission" "v1" }] } = false := by decide

theorem empty_required_qualifier : checkGraph { validGraph with assertions := [{ conforms with qualifiers := .conformance "" "v1" "assessment" }] } = false := by decide

theorem wrong_target_version : checkGraph { validGraph with assertions := [{ conforms with qualifiers := .conformance "static" "v2" "assessment" }] } = false := by decide

theorem wrong_effect_version : checkGraph { validGraph with assertions := [{ declares with qualifiers := .effect "authorization" "v2" }] } = false := by decide

theorem missing_evidence_reference : checkGraph { validGraph with assessments := [receiptAssessment] } = false := by decide

theorem stale_endpoint : checkGraph { validGraph with assertions := [{ conforms with source := ⟨"cap", "v2"⟩ }] } = false := by decide

theorem wrong_evidence_scope : checkGraph { validGraph with assessments := [{ conformanceAssessment with scope := "runtime" }, receiptAssessment] } = false := by decide

theorem unaccepted_evidence : checkGraph { validGraph with assessments := [{ conformanceAssessment with accepted := false }, receiptAssessment] } = false := by decide

theorem misbound_receipt : checkGraph { validGraph with assessments := [conformanceAssessment, { receiptAssessment with subject := decision.ref }] } = false := by decide

theorem wrong_receipt_role : checkGraph { validGraph with assertions := [{ materializes with qualifiers := .materialization "receipt" "different-role" "output-content" }] } = false := by decide

theorem wrong_output_digest : checkGraph { validGraph with assertions := [{ materializes with qualifiers := .materialization "receipt" "artifact" "different-content" }] } = false := by decide

theorem duplicate_assertion_identity : checkAddition validGraph conforms = false := by decide

theorem duplicate_node_identity : checkGraph { validGraph with nodes := cap :: validGraph.nodes } = false := by decide

theorem duplicate_assessment_identity : checkGraph { validGraph with assessments := conformanceAssessment :: validGraph.assessments } = false := by decide

theorem invalid_existing_graph : checkAddition { baseGraph with assertions := [{ conforms with id := "" }] } materializes = false := by decide

theorem invalid_unused_assessment : checkGraph { validGraph with assessments := validGraph.assessments ++ [{ conformanceAssessment with ref := "unused", subject := ⟨"missing", "v1"⟩ }] } = false := by decide

theorem admission_wrong_decision_kind : checkGraph { validGraph with admissionRoots := [{ independentRoot with decision := cap.ref }] } = false := by decide

theorem empty_node_identity : checkGraph { validGraph with nodes := [{ cap with contentIdentity := "" }, contract, decision, effect, transaction, output] } = false := by decide

end Relational.Controls
