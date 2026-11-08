Per-relation review of all 41 inherited kinds

All proposed types, predicates and proof statements below are design hypotheses requiring exact owner review. No new inherited obligation is discharged by this document. Source strings remain opaque in accepted profiles until a new checked mapping is established.


**K00 — relation.acts-for**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/acts-for.json)

**Question:** Which Principal is this Agent Instance acting for under one exact Delegation?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** independent token-store mapping; runtime integration S07. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- delegation_ref → proposed `DelegationRevisionRef`: Resolve the exact delegation, agent and principal; retain scope/action/time/redelegation restrictions and source membership.
- scope_ref → proposed `OwnedScopeRevisionRef`: Resolve the exact scope and its owner-defined inclusion relation; prove scope/endpoint/frame agreement and preserve every ancestor restriction rather than treating a scope token as permission.
- effective_period → proposed `HalfOpenInterval`: Decode a declared interval into start/stop in one owned time domain; prove start ≤ epoch < stop and reject malformed or incomparable intervals.
- revocation_state → proposed `RevocationSnapshot`: Resolve an exact revocation record and as-of epoch; missing status remains unknown and never means unrevoked.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** identity-equivalence, ownership-transfer, unrestricted-authority. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K01 — relation.addresses-improvement-target**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/addresses-improvement-target.json)

**Question:** Which Improvement Target is this Research Inquiry intended to address?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- target_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- addressing_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** resolution, improvement, priority, authority. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K02 — relation.addresses-intent**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/addresses-intent.json)

**Question:** Which exact Intent is this governed subject intended to address?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- intent_resolution_ref → proposed `OwnedTypedReference`: Resolve the opaque source token through a versioned owner-selected catalog; prove reference role, endpoint and frame agreement. Unresolved tokens stay unsupported.
- addressing_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** satisfaction, completion, authority, membership. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K03 — relation.affects**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/affects.json)

**Question:** Which exact subject was affected, under what declared scope?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- impact_scope → proposed `OwnedScope`: Define the owned scope domain, its exact identity and permitted inclusion relation; preserve subject/target/context distinctions and forbid scope widening.
- evidence_posture → proposed `OwnedPostureCode`: Define the exact posture/mode/purpose domain and distinguish declaration, attempted action, observation and accepted evidence; do not equate a label with successful execution.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** cause, severity, blame, ownership. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K04 — relation.applies-lesson**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/applies-lesson.json)

**Question:** Which exact Operational Lesson revision was used or deliberately not used by this Lesson Application?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- lesson_revision_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- application_posture → proposed `OwnedPostureCode`: Define the exact posture/mode/purpose domain and distinguish declaration, attempted action, observation and accepted evidence; do not equate a label with successful execution.
- applicability_assessment_ref → proposed `AssessmentRevisionRef`: Resolve an assessment for this exact lesson revision, subject and frame under an owned assessment policy.
- instruction_precedence → proposed `PrecedencePolicy`: Resolve a versioned precedence policy and prove its selected ordering; no arbitrary integer or source order can silently choose the governing instruction.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** compliance, benefit, authority, method-use. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K05 — relation.asserts-identity-of**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/asserts-identity-of.json)

**Question:** What bounded identity correspondence is being asserted between these endpoints?

**Source effect:** Records representation, identity linking, or identifier claims without merging identities or authority.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- assertion_kind → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.
- claim_scope → proposed `OwnedScope`: Define the owned scope domain, its exact identity and permitted inclusion relation; preserve subject/target/context distinctions and forbid scope widening.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** identity-merge, authority-transfer, private-attribute-inference. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K06 — relation.assigned-to**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/assigned-to.json)

**Question:** Which Role or Responsibility is explicitly assigned to this assignee?

**Source effect:** Records an assignment through its lifecycle-bearing record without implying Team membership or authority.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- assignment_kind → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.
- relation_record_ref → proposed `LifecycleRelationRecordRef`: Resolve the lifecycle-bearing assignment record with exact assignee and role/responsibility revisions.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** team-membership, authority, permission, identity. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K07 — relation.binds-implementation**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/binds-implementation.json)

**Question:** Which Ontology or Schema does this implementation bind?

**Source effect:** Records an implementation-model binding without proving conformance or runtime behavior.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- binding_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** conformance, runtime-effectiveness, admission. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K08 — relation.carries-definition**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/carries-definition.json)

**Question:** Which exact Definition version supplies this Artifact Type's governed meaning?

**Source effect:** Records the semantic contract without admitting either endpoint or transferring Definition authority.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- definition_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- definition_sha256 → proposed `DefinitionContentCommitment`: Bind the resolved definition revision to exact content bytes under the stated hash assumption; a matching digest is not ownership or approval.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** admission, authority-transfer, endpoint-identity-collapse. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K09 — relation.challenges**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/challenges.json)

**Question:** Which exact governed subject revision does this Challenge Event challenge?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- challenge_contract_ref → proposed `OwnedTypedReference`: Resolve the opaque source token through a versioned owner-selected catalog; prove reference role, endpoint and frame agreement. Unresolved tokens stay unsupported.
- challenge_mode → proposed `OwnedPostureCode`: Define the exact posture/mode/purpose domain and distinguish declaration, attempted action, observation and accepted evidence; do not equate a label with successful execution.
- challenged_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** suspension, reversal, contradiction-proof, authority. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K10 — relation.conforms-to**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/conforms-to.json)

**Question:** Which exact contract does this subject demonstrably conform to, and under which evidence?

**Source effect:** Records scoped conformance only; it does not imply admission, implementation conformance outside scope, or runtime conformance.

**Current evidence:** literal selected F0 source meaning/context projection. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- conformance_scope: retain the proved f0-three-kind/v1 meaning and its exact evidence.
- exact_version_ref: retain the proved f0-three-kind/v1 meaning and its exact evidence.
- conformance_evidence_refs: retain the proved f0-three-kind/v1 meaning and its exact evidence.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** admission, runtime-conformance, effectiveness, authority. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K11 — relation.consumes-view**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/consumes-view.json)

**Question:** Which immutable Context View or Ontology View did this Agent Session actually consume?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- view_digest → proposed `ViewContentCommitment`: Bind consumption to an immutable view content identity; do not infer source currentness from a digest.
- cursor → proposed `ViewCursor`: Define cursor meaning in the selected view revision, including its allowed range and consumed extent; it is not a global clock.
- consumption_purpose → proposed `OwnedPostureCode`: Define the exact posture/mode/purpose domain and distinguish declaration, attempted action, observation and accepted evidence; do not equate a label with successful execution.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** currentness, source-authority, memory-ownership, request-fulfillment. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K12 — relation.contributes-to**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/contributes-to.json)

**Question:** Which Product or Goal is this activity intended to advance?

**Source effect:** Records intended contribution without proving success, realization, or value.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- contribution_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.
- contribution_scope → proposed `OwnedScope`: Define the owned scope domain, its exact identity and permitted inclusion relation; preserve subject/target/context distinctions and forbid scope widening.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** membership, realization, evaluation-result, product-value. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K13 — relation.controls**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/controls.json)

**Question:** Which Failure Mode is this Failure Control Binding intended to control?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- control_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.
- control_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- installation_posture → proposed `OwnedPostureCode`: Define the exact posture/mode/purpose domain and distinguish declaration, attempted action, observation and accepted evidence; do not equate a label with successful execution.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** installation, execution, effectiveness, authority. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K14 — relation.declares-effect-on**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/declares-effect-on.json)

**Question:** Which exact governance effect does this Decision declare?

**Source effect:** Records admission, adoption, or authorization as separate effect values and executes none of them.

**Current evidence:** literal selected F0 source meaning/context projection. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- effect_kind: retain the proved f0-three-kind/v1 meaning and its exact evidence.
- exact_target_version_ref: retain the proved f0-three-kind/v1 meaning and its exact evidence.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** effect-execution, cross-effect-inference, runtime-success. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K15 — relation.derives-from**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/derives-from.json)

**Question:** From which material or governed source was this artifact derived?

**Source effect:** Records derivation, compilation, or projection while preserving source and derived identities.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- derivation_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** identity-equality, source-authority-transfer, admission. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K16 — relation.engages-inquiry**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/engages-inquiry.json)

**Question:** How does this research carrier engage a Research Inquiry?

**Source effect:** Records whether an activity addresses or a Finding answers an Inquiry without converting either into the other.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- inquiry_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** finding-acceptance, evidence-support, inquiry-completion. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K17 — relation.evaluates**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/evaluates.json)

**Question:** Which subject or proposition is being assessed?

**Source effect:** Records evaluation scope without deciding evidence polarity, adoption, realization, or value.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- evaluation_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.
- evaluation_purpose → proposed `OwnedPostureCode`: Define the exact posture/mode/purpose domain and distinguish declaration, attempted action, observation and accepted evidence; do not equate a label with successful execution.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** support, contradiction, adoption, realization, product-value. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K18 — relation.evidence-bears-on**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/evidence-bears-on.json)

**Question:** What evidential polarity does this evidence have toward this claim?

**Source effect:** Records supporting or contradicting evidence without accepting, rejecting, or deciding the claim.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- polarity → proposed `EvidencePolarity`: Use an owner-defined support/contradict domain; polarity toward a claim is distinct from truth or acceptance of that claim.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** claim-acceptance, decision, admission, truth. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K19 — relation.frames**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/frames.json)

**Question:** Which subject does this Context frame for relevance and interpretation?

**Source effect:** Records Context framing, including Bounded Context reference, without making the framed subject authoritative or current.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- framing_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** source-authority, currentness, truth. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K20 — relation.fulfills-request**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/fulfills-request.json)

**Question:** Which request is this immutable output intended to fulfill?

**Source effect:** Records request fulfillment without implying that included sources or Context remain current.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- fulfillment_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** currentness, source-authority, context-mutation. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K21 — relation.governed-by**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/governed-by.json)

**Question:** Which Policy or Constitution governs this subject?

**Source effect:** Records applicable governance without proving compliance or authorization.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- governance_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** conformance, authorization, admission. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K22 — relation.has-capability**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/has-capability.json)

**Question:** Which Agent Capability is declared for this Agent Profile or Agent Instance?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- capability_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- declaration_basis → proposed `DeclarationBasis`: Resolve the source basis for the capability declaration; a declaration does not prove successful performance or permission.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** authority, successful-performance, product-value. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K23 — relation.inherits-contract**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/inherits-contract.json)

**Question:** Which exact contract obligations are inherited by this instance?

**Source effect:** Records inherited obligations without transferring parent ownership or proving conformance.

**Current evidence:** independent token-store mapping; runtime integration S07. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- binding_ref → proposed `BindingRevisionRef`: Resolve a relation-specific binding record with exact roles, endpoint revisions, owner and lifecycle; shared spelling does not make binding meanings interchangeable.
- contract_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** ownership-transfer, conformance, adoption. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K24 — relation.instance-of**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/instance-of.json)

**Question:** Under which exact parent model is this subject classified?

**Source effect:** Records classification without implying conformance, ownership transfer, or realization.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- parent_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- binding_ref → proposed `BindingRevisionRef`: Resolve a relation-specific binding record with exact roles, endpoint revisions, owner and lifecycle; shared spelling does not make binding meanings interchangeable.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** conformance, realization, ownership-transfer. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K25 — relation.materializes-consequence**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/materializes-consequence.json)

**Question:** Which declared deterministic consequence did this Admission Transaction materialize?

**Source effect:** Records a deterministic output created while atomically applying an already authorized Decision Bundle; it grants no additional authority and proves no semantic correctness.

**Current evidence:** literal selected F0 source meaning/context projection. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- application_receipt_ref: retain the proved f0-three-kind/v1 meaning and its exact evidence.
- consequence_role: retain the proved f0-three-kind/v1 meaning and its exact evidence.
- output_digest: retain the proved f0-three-kind/v1 meaning and its exact evidence.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** new-authorization, semantic-correctness, runtime-activation, external-effect. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K26 — relation.member-of**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/member-of.json)

**Question:** Which governed container or scope is this member part of?

**Source effect:** Records scoped membership or composition in member-to-container direction without transferring identity or authority.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- membership_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** contribution, assignment, authority, identity-equivalence. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K27 — relation.occurs-during**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/occurs-during.json)

**Question:** In which exact execution envelope did this Failure Occurrence happen?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- envelope_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- temporal_scope → proposed `OwnedScope`: Define the owned scope domain, its exact identity and permitted inclusion relation; preserve subject/target/context distinctions and forbid scope widening.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** cause, blame, severity, recovery. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K28 — relation.originates-from**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/originates-from.json)

**Question:** From which source did this identity or content originate?

**Source effect:** Records origin lineage without asserting transformation, succession, or authority transfer.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- origin_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** derivation, successor, authority-transfer. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K29 — relation.performs**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/performs.json)

**Question:** Which attributable activity is performed or attempted by this Agent Instance?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- session_ref → proposed `SessionRevisionRef`: Resolve the exact attributable session and its frame; name matching alone does not authenticate the actor.
- participation_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.
- action_posture → proposed `OwnedPostureCode`: Define the exact posture/mode/purpose domain and distinguish declaration, attempted action, observation and accepted evidence; do not equate a label with successful execution.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** ownership, approval, admission, successful-effect. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K30 — relation.produces**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/produces.json)

**Question:** Which governed output was produced by this Agent Action?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- action_receipt_ref → proposed `ActionReceiptRevisionRef`: Resolve an exact action/output receipt with owner and provenance; distinguish local execution evidence from external-world authenticity.
- production_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.
- output_posture → proposed `OwnedPostureCode`: Define the exact posture/mode/purpose domain and distinguish declaration, attempted action, observation and accepted evidence; do not equate a label with successful execution.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** acceptance, correctness, admission, authority-effect. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K31 — relation.profiled-by**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/profiled-by.json)

**Question:** Which exact Agent Profile revision configures this Agent Instance?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- profile_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- binding_ref → proposed `BindingRevisionRef`: Resolve a relation-specific binding record with exact roles, endpoint revisions, owner and lifecycle; shared spelling does not make binding meanings interchangeable.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** conformance, capability, authority, identity-continuity. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K32 — relation.realizes**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/realizes.json)

**Question:** Which declared design or capability is concretely instantiated by this subject?

**Source effect:** Records realization or execution without implying conformance, effectiveness, adoption, or evidence acceptance.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- realization_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.
- exact_target_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** conformance, effectiveness, adoption, support. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K33 — relation.requests-resolution-of**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/requests-resolution-of.json)

**Question:** Which exact Context version does this Context Request ask to resolve?

**Source effect:** Records a resolution request without performing resolution or mutating Context.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- context_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** resolution, context-mutation, source-authority. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K34 — relation.responds-to**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/responds-to.json)

**Question:** Which Failure Occurrence or Incident is this Agent Action intended to address?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- response_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.
- intended_outcome → proposed `DeclaredOutcome`: Resolve a versioned declared outcome; stating the desired result cannot establish that it happened.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** recovery-success, cause, closure, authority. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K35 — relation.scopes-authority-over**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/scopes-authority-over.json)

**Question:** What governed scope is bounded by this explicit Authority Claim or Authority Boundary?

**Source effect:** Records an explicit authority subject's bounded scope without granting permission, authenticating the subject, or executing an effect.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- authority_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.
- scope_ref → proposed `OwnedScopeRevisionRef`: Resolve the exact scope and its owner-defined inclusion relation; prove scope/endpoint/frame agreement and preserve every ancestor restriction rather than treating a scope token as permission.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** permission-grant, claim-authentication, effect-execution. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K36 — relation.successor-of**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/successor-of.json)

**Question:** Which predecessor does this successor continue or replace?

**Source effect:** Records succession; replacement occurs only when succession_effect is supersedes.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- succession_effect → proposed `SuccessionEffect`: Distinguish continues from supersedes; prove replacement requires the supersedes value and the separately qualified lifecycle operation.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** automatic-supersession, identity-equality, authority-transfer. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K37 — relation.tests-hypothesis**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/tests-hypothesis.json)

**Question:** Which exact Hypothesis is this Experiment Design constructed to test?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- hypothesis_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- test_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** support, contradiction, truth, successful-execution. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K38 — relation.uses-method**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/uses-method.json)

**Question:** Which Method does this subject depend on or employ?

**Source effect:** Records Method dependency without implying conformance, realization, or success.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- usage_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** conformance, realization, validation, achievement. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K39 — relation.uses-tool**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/uses-tool.json)

**Question:** Which Tool or Implementation does this Agent Session or Agent Action use?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- tool_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- invocation_contract_ref → proposed `OwnedTypedReference`: Resolve the opaque source token through a versioned owner-selected catalog; prove reference role, endpoint and frame agreement. Unresolved tokens stay unsupported.
- use_role → proposed `OwnedRoleCode`: Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** realization, conformance, ownership, authority. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.

**K40 — relation.violates**

[Exact source declaration](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/violates.json)

**Question:** Which exact expected boundary does evidence indicate was not satisfied?

**Source effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Current evidence:** No additional implemented semantic fragment; the wider improvement is deferred. This does not discharge the source-wide remainder.

**Proposed qualifier interpretations:**

- boundary_version_ref → proposed `ExactRevisionRef`: Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.
- evidence_posture → proposed `OwnedPostureCode`: Define the exact posture/mode/purpose domain and distinguish declaration, attempted action, observation and accepted evidence; do not equate a label with successful execution.

**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.

**Forbidden conclusions requiring separate meaning and evidence:** cause, severity, authority, automatic-failure-confirmation. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.

**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.
