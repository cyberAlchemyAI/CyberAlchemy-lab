<!-- GENERATED FILE: canonical data is relation-kind-instances.json. -->

# Definition-complete Relation Kind instances

- Relation Kinds: `40`
- Exact ordered endpoint pairs: `538`
- Typed Relation examples excluded from admission: `40`
- Authority effect: `none`

## `relation.acts-for`

Which Principal is this Agent Instance acting for under one exact Delegation?

Required qualifiers: `delegation_ref, scope_ref, effective_period, revocation_state`

Exact pairs: `1`

## `relation.addresses-improvement-target`

Which Improvement Target is this Research Inquiry intended to address?

Required qualifiers: `target_version_ref, addressing_role`

Exact pairs: `1`

## `relation.addresses-intent`

Which exact Intent is this governed subject intended to address?

Required qualifiers: `intent_resolution_ref, addressing_role`

Exact pairs: `6`

## `relation.affects`

Which exact subject was affected, under what declared scope?

Required qualifiers: `impact_scope, evidence_posture`

Exact pairs: `22`

## `relation.applies-lesson`

Which exact Operational Lesson revision was used or deliberately not used by this Lesson Application?

Required qualifiers: `lesson_revision_ref, application_posture, applicability_assessment_ref, instruction_precedence`

Exact pairs: `1`

## `relation.asserts-identity-of`

What bounded identity correspondence is being asserted between these endpoints?

Required qualifiers: `assertion_kind, claim_scope`

Exact pairs: `4`

## `relation.assigned-to`

Which Role or Responsibility is explicitly assigned to this assignee?

Required qualifiers: `assignment_kind, relation_record_ref`

Exact pairs: `6`

## `relation.binds-implementation`

Which Ontology or Schema does this implementation bind?

Required qualifiers: `binding_role`

Exact pairs: `2`

## `relation.carries-definition`

Which exact Definition version supplies this Artifact Type's governed meaning?

Required qualifiers: `definition_version_ref, definition_sha256`

Exact pairs: `1`

## `relation.challenges`

Which exact governed subject revision does this Challenge Event challenge?

Required qualifiers: `challenge_contract_ref, challenge_mode, challenged_version_ref`

Exact pairs: `100`

## `relation.conforms-to`

Which exact contract does this subject demonstrably conform to, and under which evidence?

Required qualifiers: `conformance_scope, exact_version_ref, conformance_evidence_refs`

Exact pairs: `3`

## `relation.consumes-view`

Which immutable Context View or Ontology View did this Agent Session actually consume?

Required qualifiers: `view_digest, cursor, consumption_purpose`

Exact pairs: `2`

## `relation.contributes-to`

Which Product or Goal is this activity intended to advance?

Required qualifiers: `contribution_role, contribution_scope`

Exact pairs: `8`

## `relation.controls`

Which Failure Mode is this Failure Control Binding intended to control?

Required qualifiers: `control_role, control_version_ref, installation_posture`

Exact pairs: `1`

## `relation.declares-effect-on`

Which exact governance effect does this Decision declare?

Required qualifiers: `effect_kind, exact_target_version_ref`

Exact pairs: `21`

## `relation.derives-from`

From which material or governed source was this artifact derived?

Required qualifiers: `derivation_role`

Exact pairs: `40`

## `relation.engages-inquiry`

How does this research carrier engage a Research Inquiry?

Required qualifiers: `inquiry_role`

Exact pairs: `4`

## `relation.evaluates`

Which subject or proposition is being assessed?

Required qualifiers: `evaluation_role, evaluation_purpose`

Exact pairs: `16`

## `relation.evidence-bears-on`

What evidential polarity does this evidence have toward this claim?

Required qualifiers: `polarity`

Exact pairs: `72`

## `relation.frames`

Which subject does this Context frame for relevance and interpretation?

Required qualifiers: `framing_role`

Exact pairs: `5`

## `relation.fulfills-request`

Which request is this immutable output intended to fulfill?

Required qualifiers: `fulfillment_role`

Exact pairs: `1`

## `relation.governed-by`

Which Policy or Constitution governs this subject?

Required qualifiers: `governance_role`

Exact pairs: `23`

## `relation.has-capability`

Which Agent Capability is declared for this Agent Profile or Agent Instance?

Required qualifiers: `capability_version_ref, declaration_basis`

Exact pairs: `2`

## `relation.inherits-contract`

Which exact contract obligations are inherited by this instance?

Required qualifiers: `binding_ref, contract_version_ref`

Exact pairs: `1`

## `relation.instance-of`

Under which exact parent model is this subject classified?

Required qualifiers: `parent_version_ref, binding_ref`

Exact pairs: `12`

## `relation.member-of`

Which governed container or scope is this member part of?

Required qualifiers: `membership_role`

Exact pairs: `23`

## `relation.occurs-during`

In which exact execution envelope did this Failure Occurrence happen?

Required qualifiers: `envelope_version_ref, temporal_scope`

Exact pairs: `5`

## `relation.originates-from`

From which source did this identity or content originate?

Required qualifiers: `origin_role`

Exact pairs: `7`

## `relation.performs`

Which attributable activity is performed or attempted by this Agent Instance?

Required qualifiers: `session_ref, participation_role, action_posture`

Exact pairs: `5`

## `relation.produces`

Which governed output was produced by this Agent Action?

Required qualifiers: `action_receipt_ref, production_role, output_posture`

Exact pairs: `19`

## `relation.profiled-by`

Which exact Agent Profile revision configures this Agent Instance?

Required qualifiers: `profile_version_ref, binding_ref`

Exact pairs: `1`

## `relation.realizes`

Which declared design or capability is concretely instantiated by this subject?

Required qualifiers: `realization_role, exact_target_version_ref`

Exact pairs: `2`

## `relation.requests-resolution-of`

Which exact Context version does this Context Request ask to resolve?

Required qualifiers: `context_version_ref`

Exact pairs: `1`

## `relation.responds-to`

Which Failure Occurrence or Incident is this Agent Action intended to address?

Required qualifiers: `response_role, intended_outcome`

Exact pairs: `2`

## `relation.scopes-authority-over`

What object or assignment is bounded by this explicit Authority Claim?

Required qualifiers: `authority_role, scope_ref`

Exact pairs: `2`

## `relation.successor-of`

Which predecessor does this successor continue or replace?

Required qualifiers: `succession_effect`

Exact pairs: `100`

## `relation.tests-hypothesis`

Which exact Hypothesis is this Experiment Design constructed to test?

Required qualifiers: `hypothesis_version_ref, test_role`

Exact pairs: `1`

## `relation.uses-method`

Which Method does this subject depend on or employ?

Required qualifiers: `usage_role`

Exact pairs: `7`

## `relation.uses-tool`

Which Tool or Implementation does this Agent Session or Agent Action use?

Required qualifiers: `tool_version_ref, invocation_contract_ref, use_role`

Exact pairs: `4`

## `relation.violates`

Which exact expected boundary does evidence indicate was not satisfied?

Required qualifiers: `boundary_version_ref, evidence_posture`

Exact pairs: `4`

## Claim ceiling

This materializes complete candidate carriers, Relation Kind records, and excluded Typed Relation examples. It admits nothing.
