# Review of each captured relation definition

All 41 selected sources were inspected and checked against their exact source hashes and the normalized registry. Each card distinguishes declaration, interpretation and theorem coverage. Source versions, all endpoint pairs and qualifier contracts are preserved in definition-inventory.json. These suggestions add no runtime semantics and discharge no unsupported item.

Only selected F0 meanings and the two separately typed stress profiles have the semantic coverage described here. Each proposed control still needs execution under its selected successor profile.

## 1. acts-for

[acts-for.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/acts-for.json)

**Source question:** Which Principal is this Agent Instance acting for under one exact Delegation?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 1 exact pairs in the inventory. **Required qualifiers:** `delegation_ref`, `scope_ref`, `effective_period`, `revocation_state`.

**Current coverage:** Separate typed direct effectiveness, restriction and revocation laws exist.

**Gap:** Legacy period/revocation strings do not map themselves to typed inputs; action and context are extra inputs.

**Improvement:** Bind exact delegation/action/context and explicit period/revocation interpretation; recorded facts also require membership.

**Required controls:** Wrong principal, expiry/revocation boundary, unresolved gate, unproved redelegation chain.

**Keep independent:** identity-equivalence, ownership-transfer, unrestricted-authority.

**Plan:** S04, S07, S18. **Findings:** I04, I07, I08.

## 2. addresses-improvement-target

[addresses-improvement-target.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/addresses-improvement-target.json)

**Source question:** Which Improvement Target is this Research Inquiry intended to address?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 1 exact pairs in the inventory. **Required qualifiers:** `target_version_ref`, `addressing_role`.

**Current coverage:** Structural inquiry-to-target declaration.

**Gap:** Target version is an opaque string; addressing is intent, not improvement.

**Improvement:** Resolve the exact target version and preserve intended addressing separately from measured outcome.

**Required controls:** Changed target revision; addressing with no improvement achieved.

**Keep independent:** resolution, improvement, priority, authority.

**Plan:** S01, S18. **Findings:** I08, I11.

## 3. addresses-intent

[addresses-intent.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/addresses-intent.json)

**Source question:** Which exact Intent is this governed subject intended to address?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 6 exact pairs in the inventory. **Required qualifiers:** `intent_resolution_ref`, `addressing_role`.

**Current coverage:** Six endpoint families can declare intended addressing of an intent.

**Gap:** Intent-resolution reference is unresolved and may name another intent.

**Improvement:** Resolve the exact resolution record and linked intent; derive IntendedAddressing only.

**Required controls:** Wrong intent in resolution; no satisfaction/completion from addressing.

**Keep independent:** satisfaction, completion, authority, membership.

**Plan:** S01, S18. **Findings:** I08, I11.

## 4. affects

[affects.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/affects.json)

**Source question:** Which exact subject was affected, under what declared scope?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 22 exact pairs in the inventory. **Required qualifiers:** `impact_scope`, `evidence_posture`.

**Current coverage:** Declared scoped impact is structurally checked.

**Gap:** Impact scope/evidence posture have no interpretation; cause/severity are separate claims.

**Improvement:** Bind exact scoped impact assessment and posture without causal or severity inference.

**Required controls:** Unsupported posture stays unknown; impact with no proved cause or severity.

**Keep independent:** cause, severity, blame, ownership.

**Plan:** S01, S18. **Findings:** I04, I08.

## 5. applies-lesson

[applies-lesson.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/applies-lesson.json)

**Source question:** Which exact Operational Lesson revision was used or deliberately not used by this Lesson Application?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 1 exact pairs in the inventory. **Required qualifiers:** `lesson_revision_ref`, `application_posture`, `applicability_assessment_ref`, `instruction_precedence`.

**Current coverage:** Lesson application names a revision, posture, applicability assessment and instruction precedence.

**Gap:** Actual application versus deliberate non-use and precedence remain uninterpreted.

**Improvement:** Define source-supported postures and independently assess applicability/precedence before AppliedLesson.

**Required controls:** Deliberate non-use cannot become application; higher-priority instruction prevents unsupported compliance inference.

**Keep independent:** compliance, benefit, authority, method-use.

**Plan:** S01, S18. **Findings:** I08, I11.

## 6. asserts-identity-of

[asserts-identity-of.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/asserts-identity-of.json)

**Source question:** What bounded identity correspondence is being asserted between these endpoints?

**Declared effect:** Records representation, identity linking, or identifier claims without merging identities or authority.

**Endpoint policy:** 4 exact pairs in the inventory. **Required qualifiers:** `assertion_kind`, `claim_scope`.

**Current coverage:** Scoped identity assertions are recorded.

**Gap:** An assertion is not identity equality, authenticated identity or private-attribute evidence.

**Improvement:** Interpret a scoped asserted identity while preserving separate endpoint identities and authority.

**Required controls:** Assertion exists with no endpoint equality or transferred authority.

**Keep independent:** identity-merge, authority-transfer, private-attribute-inference.

**Plan:** S01, S18. **Findings:** I08, I09.

## 7. assigned-to

[assigned-to.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/assigned-to.json)

**Source question:** Which Role or Responsibility is explicitly assigned to this assignee?

**Declared effect:** Records an assignment through its lifecycle-bearing record without implying Team membership or authority.

**Endpoint policy:** 6 exact pairs in the inventory. **Required qualifiers:** `assignment_kind`, `relation_record_ref`.

**Current coverage:** Assignment kind and lifecycle-record reference are required.

**Gap:** Lifecycle and exact participant binding are not resolved.

**Improvement:** Check exact assignment record and selected lifecycle; keep assignment separate from membership/permission.

**Required controls:** Withdrawn or wrong-participant record cannot support current assignment.

**Keep independent:** team-membership, authority, permission, identity.

**Plan:** S01, S18. **Findings:** I04, I08.

## 8. binds-implementation

[binds-implementation.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/binds-implementation.json)

**Source question:** Which Ontology or Schema does this implementation bind?

**Declared effect:** Records an implementation-model binding without proving conformance or runtime behavior.

**Endpoint policy:** 2 exact pairs in the inventory. **Required qualifiers:** `binding_role`.

**Current coverage:** Implementation-model binding is declared.

**Gap:** Binding role gives no conformance test or runtime-effect witness.

**Improvement:** Map role and require separate implementation/model conformance evidence.

**Required controls:** Bound implementation fails conformance or runtime effectiveness.

**Keep independent:** conformance, runtime-effectiveness, admission.

**Plan:** S01, S18. **Findings:** I08, I11.

## 9. carries-definition

[carries-definition.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/carries-definition.json)

**Source question:** Which exact Definition version supplies this Artifact Type's governed meaning?

**Declared effect:** Records the semantic contract without admitting either endpoint or transferring Definition authority.

**Endpoint policy:** 1 exact pairs in the inventory. **Required qualifiers:** `definition_version_ref`, `definition_sha256`.

**Current coverage:** Definition version and digest qualifiers are required.

**Gap:** Any nonempty digest passes structural shape; definition bytes are not compared.

**Improvement:** Resolve exact definition bytes and check revision/digest as a sealed content binding.

**Required controls:** Alter bytes at displayed version; mismatched digest blocks content binding.

**Keep independent:** admission, authority-transfer, endpoint-identity-collapse.

**Plan:** S01, S18. **Findings:** I08, I09.

## 10. challenges

[challenges.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/challenges.json)

**Source question:** Which exact governed subject revision does this Challenge Event challenge?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 100 exact pairs in the inventory. **Required qualifiers:** `challenge_contract_ref`, `challenge_mode`, `challenged_version_ref`.

**Current coverage:** Challenge contract, mode and challenged version are declared.

**Gap:** References/modes are unresolved; challenge proves no contradiction or suspension.

**Improvement:** Resolve exact challenge contract/artifact revision and supported challenge mode.

**Required controls:** Wrong revision/mode; challenge alone cannot suspend or refute the challenged claim.

**Keep independent:** suspension, reversal, contradiction-proof, authority.

**Plan:** S01, S18. **Findings:** I08, I11.

## 11. conforms-to

[conforms-to.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/conforms-to.json)

**Source question:** Which exact contract does this subject demonstrably conform to, and under which evidence?

**Declared effect:** Records scoped conformance only; it does not imply admission, implementation conformance outside scope, or runtime conformance.

**Endpoint policy:** 3 exact pairs in the inventory. **Required qualifiers:** `conformance_scope`, `exact_version_ref`, `conformance_evidence_refs`.

**Current coverage:** F0 binds an accepted assessment to exact endpoints, scope and target revision for its selected fragment.

**Gap:** Registry has plural evidence-reference strings and broader pairs; unary bridge loses target/scope.

**Improvement:** Map a selected fragment to sealed contextual ConformsTo and checked TargetKind with complete support sets.

**Required controls:** Wrong target/scope/kind/version; nonmember edge; duplicate supports; injected observation.

**Keep independent:** admission, runtime-conformance, effectiveness, authority.

**Plan:** S02, S05, S16, S18. **Findings:** I01, I03, I07, I08.

## 12. consumes-view

[consumes-view.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/consumes-view.json)

**Source question:** Which immutable Context View or Ontology View did this Agent Session actually consume?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 2 exact pairs in the inventory. **Required qualifiers:** `view_digest`, `cursor`, `consumption_purpose`.

**Current coverage:** View digest, cursor and consumption purpose are declared.

**Gap:** Digest/cursor does not establish consumed content, freshness or cursor units.

**Improvement:** Bind immutable view and cursor interpretation; expose consumption without currentness inference.

**Required controls:** Incompatible cursor interpretation; consumed stale view remains stale.

**Keep independent:** currentness, source-authority, memory-ownership, request-fulfillment.

**Plan:** S01, S18. **Findings:** I08, I09.

## 13. contributes-to

[contributes-to.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/contributes-to.json)

**Source question:** Which Product or Goal is this activity intended to advance?

**Declared effect:** Records intended contribution without proving success, realization, or value.

**Endpoint policy:** 8 exact pairs in the inventory. **Required qualifiers:** `contribution_role`, `contribution_scope`.

**Current coverage:** Intended contribution role/scope is recorded.

**Gap:** Intent does not prove actual contribution outcome, membership or value.

**Improvement:** Expose intended scoped contribution; independently assess realized outcome.

**Required controls:** Declared contribution with no measured result/value.

**Keep independent:** membership, realization, evaluation-result, product-value.

**Plan:** S01, S18. **Findings:** I08, I11.

## 14. controls

[controls.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/controls.json)

**Source question:** Which Failure Mode is this Failure Control Binding intended to control?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 1 exact pairs in the inventory. **Required qualifiers:** `control_role`, `control_version_ref`, `installation_posture`.

**Current coverage:** Control role/version/installation posture are required.

**Gap:** Planned, installed, executed and effective states are not interpreted separately.

**Improvement:** Resolve exact control version; separately witness installation and effectiveness.

**Required controls:** Planned control is not installed; installed control can be ineffective.

**Keep independent:** installation, execution, effectiveness, authority.

**Plan:** S01, S18. **Findings:** I04, I08.

## 15. declares-effect-on

[declares-effect-on.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/declares-effect-on.json)

**Source question:** Which exact governance effect does this Decision declare?

**Declared effect:** Records admission, adoption, or authorization as separate effect values and executes none of them.

**Endpoint policy:** 21 exact pairs in the inventory. **Required qualifiers:** `effect_kind`, `exact_target_version_ref`.

**Current coverage:** F0 checks exact decision endpoints and target version.

**Gap:** Effect string remains uninterpreted; source distinguishes admission/adoption/authorization and executes none.

**Improvement:** Interpret selected effect values and require effect-specific independent roots.

**Required controls:** Adoption declaration cannot supply admission/authorization; unknown effect stays uninterpreted.

**Keep independent:** effect-execution, cross-effect-inference, runtime-success.

**Plan:** S01, S18. **Findings:** I08, I11.

## 16. derives-from

[derives-from.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/derives-from.json)

**Source question:** From which material or governed source was this artifact derived?

**Declared effect:** Records derivation, compilation, or projection while preserving source and derived identities.

**Endpoint policy:** 40 exact pairs in the inventory. **Required qualifiers:** `derivation_role`.

**Current coverage:** Transformation lineage role is declared.

**Gap:** Lineage alone proves no transformation correctness or safe transitive composition.

**Improvement:** Use exact transformation witness profiles and separately defined lineage composition.

**Required controls:** Provenance chain without correctness witness cannot prove equivalent content/source authority.

**Keep independent:** identity-equality, source-authority-transfer, admission.

**Plan:** S01, S18. **Findings:** I08, I09.

## 17. engages-inquiry

[engages-inquiry.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/engages-inquiry.json)

**Source question:** How does this research carrier engage a Research Inquiry?

**Declared effect:** Records whether an activity addresses or a Finding answers an Inquiry without converting either into the other.

**Endpoint policy:** 4 exact pairs in the inventory. **Required qualifiers:** `inquiry_role`.

**Current coverage:** Activities can address and findings can answer an inquiry.

**Gap:** Role hides distinct endpoint-dependent meanings; answering is not finding acceptance.

**Improvement:** Define role/pair-specific interpretation and separate accepted finding evidence.

**Required controls:** Addressing activity cannot become a finding answer; supplied answer remains unaccepted.

**Keep independent:** finding-acceptance, evidence-support, inquiry-completion.

**Plan:** S01, S18. **Findings:** I08, I11.

## 18. evaluates

[evaluates.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/evaluates.json)

**Source question:** Which subject or proposition is being assessed?

**Declared effect:** Records evaluation scope without deciding evidence polarity, adoption, realization, or value.

**Endpoint policy:** 16 exact pairs in the inventory. **Required qualifiers:** `evaluation_role`, `evaluation_purpose`.

**Current coverage:** Evaluation scope, role and purpose are recorded.

**Gap:** No result, success, evidence polarity or product value is established.

**Improvement:** Keep evaluation occurrence separate from independently witnessed results.

**Required controls:** Evaluation exists with inconclusive result and no supporting evidence.

**Keep independent:** support, contradiction, adoption, realization, product-value.

**Plan:** S01, S18. **Findings:** I08, I11.

## 19. evidence-bears-on

[evidence-bears-on.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/evidence-bears-on.json)

**Source question:** What evidential polarity does this evidence have toward this claim?

**Declared effect:** Records supporting or contradicting evidence without accepting, rejecting, or deciding the claim.

**Endpoint policy:** 72 exact pairs in the inventory. **Required qualifiers:** `polarity`.

**Current coverage:** Declared evidence polarity does not decide the claim.

**Gap:** Polarity strings do not establish exact claim/evidence binding or truth; opposite evidence may coexist.

**Improvement:** Interpret selected evidence postures and preserve separate claim decision with no explosion.

**Required controls:** Both polarities present without arbitrary truth; evidence for another claim fails binding.

**Keep independent:** claim-acceptance, decision, admission, truth.

**Plan:** S01, S18. **Findings:** I04, I08.

## 20. frames

[frames.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/frames.json)

**Source question:** Which subject does this Context frame for relevance and interpretation?

**Declared effect:** Records Context framing, including Bounded Context reference, without making the framed subject authoritative or current.

**Endpoint policy:** 5 exact pairs in the inventory. **Required qualifiers:** `framing_role`.

**Current coverage:** Context framing role is recorded.

**Gap:** Framing gives no source authority/currentness; scope is not interpreted.

**Improvement:** Bind immutable frame/context identity separately from source freshness.

**Required controls:** A valid frame can include an outdated source and confer no authority.

**Keep independent:** source-authority, currentness, truth.

**Plan:** S01, S18. **Findings:** I08, I09.

## 21. fulfills-request

[fulfills-request.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/fulfills-request.json)

**Source question:** Which request is this immutable output intended to fulfill?

**Declared effect:** Records request fulfillment without implying that included sources or Context remain current.

**Endpoint policy:** 1 exact pairs in the inventory. **Required qualifiers:** `fulfillment_role`.

**Current coverage:** Operational text says fulfillment; unique_question asks which request the output is intended to fulfill.

**Gap:** Intended linkage and verified satisfaction are different meanings and are not resolved in this declaration.

**Improvement:** Resolve the meaning in the formal contract; add independent request-satisfaction evidence if that is the intended claim.

**Required controls:** Intended incomplete view cannot prove request satisfied; fulfilled view may still have stale sources.

**Keep independent:** currentness, source-authority, context-mutation.

**Plan:** S00, S01, S18. **Findings:** I11.

## 22. governed-by

[governed-by.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/governed-by.json)

**Source question:** Which Policy or Constitution governs this subject?

**Declared effect:** Records applicable governance without proving compliance or authorization.

**Endpoint policy:** 29 exact pairs in the inventory. **Required qualifiers:** `governance_role`.

**Current coverage:** Applicable governance role is recorded.

**Gap:** Role does not establish jurisdiction, current policy, compliance or authorization.

**Improvement:** Resolve exact governing artifact/scope in a selected profile, retaining independent compliance and permission checks.

**Required controls:** Governance applies while compliance/authorization are absent.

**Keep independent:** conformance, authorization, admission.

**Plan:** S01, S18. **Findings:** I04, I08.

## 23. has-capability

[has-capability.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/has-capability.json)

**Source question:** Which Agent Capability is declared for this Agent Profile or Agent Instance?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 2 exact pairs in the inventory. **Required qualifiers:** `capability_version_ref`, `declaration_basis`.

**Current coverage:** Capability version and declaration basis are declared.

**Gap:** Declared capability does not prove performance or execution authority.

**Improvement:** Bind exact capability declaration/basis and distinguish declared from demonstrated capability.

**Required controls:** Declared capability with failed task; no permission from capability alone.

**Keep independent:** authority, successful-performance, product-value.

**Plan:** S01, S18. **Findings:** I08, I11.

## 24. inherits-contract

[inherits-contract.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/inherits-contract.json)

**Source question:** Which exact contract obligations are inherited by this instance?

**Declared effect:** Records inherited obligations without transferring parent ownership or proving conformance.

**Endpoint policy:** 1 exact pairs in the inventory. **Required qualifiers:** `binding_ref`, `contract_version_ref`.

**Current coverage:** Separate typed stress propagation/origin laws and conformance independence exist.

**Gap:** Binding/version qualifier mapping is absent; condition labels do not prove activation; forwarding is same-fact only.

**Improvement:** Map exact binding/contract and distinguish PotentialNorm, ActiveNorm and Fulfillment; defer hierarchy/overrides.

**Required controls:** Wrong binding/version, false/unknown condition, conflict without explosion, inheritance without conformance.

**Keep independent:** ownership-transfer, conformance, adoption.

**Plan:** S04, S07, S18. **Findings:** I04, I05, I08.

## 25. instance-of

[instance-of.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/instance-of.json)

**Source question:** Under which exact parent model is this subject classified?

**Declared effect:** Records classification without implying conformance, ownership transfer, or realization.

**Endpoint policy:** 12 exact pairs in the inventory. **Required qualifiers:** `parent_version_ref`, `binding_ref`.

**Current coverage:** Classification parent version and binding are declared.

**Gap:** Classification binding is unresolved; classification is not conformance.

**Improvement:** Resolve exact classification assignment/parent revision and retain independent conformance.

**Required controls:** Classified instance fails conformance; wrong-parent binding cannot support classification.

**Keep independent:** conformance, realization, ownership-transfer.

**Plan:** S01, S18. **Findings:** I08, I11.

## 26. materializes-consequence

[materializes-consequence.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/materializes-consequence.json)

**Source question:** Which declared deterministic consequence did this Admission Transaction materialize?

**Declared effect:** Records a deterministic output created while atomically applying an already authorized Decision Bundle; it grants no additional authority and proves no semantic correctness.

**Endpoint policy:** 4 exact pairs in the inventory. **Required qualifiers:** `application_receipt_ref`, `consequence_role`, `output_digest`.

**Current coverage:** F0 binds transaction/output/role/digest to a supplied accepted receipt.

**Gap:** Source also describes deterministic output and atomic authorized application; F0 does not prove those properties.

**Improvement:** Keep receipt-bound materialization as supported fragment; separately classify atomicity/prior authorization/determinism as unsupported operational requirements.

**Required controls:** Wrong digest/receipt fails; supplied receipt alone cannot prove atomic commit or correctness.

**Keep independent:** new-authorization, semantic-correctness, runtime-activation, external-effect.

**Plan:** S01, S18. **Findings:** I08, I09, I12.

## 27. member-of

[member-of.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/member-of.json)

**Source question:** Which governed container or scope is this member part of?

**Declared effect:** Records scoped membership or composition in member-to-container direction without transferring identity or authority.

**Endpoint policy:** 24 exact pairs in the inventory. **Required qualifiers:** `membership_role`.

**Current coverage:** Scoped member-to-container membership/composition is structurally checked.

**Gap:** Role/container semantics are opaque; cycle constraints are relation-specific.

**Improvement:** Interpret selected membership roles; choose container-specific cycle policy only if required.

**Required controls:** Membership without permission/assignment; do not impose a universal relation-cycle ban.

**Keep independent:** contribution, assignment, authority, identity-equivalence.

**Plan:** S01, S18. **Findings:** I08, I11.

## 28. occurs-during

[occurs-during.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/occurs-during.json)

**Source question:** In which exact execution envelope did this Failure Occurrence happen?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 5 exact pairs in the inventory. **Required qualifiers:** `envelope_version_ref`, `temporal_scope`.

**Current coverage:** Envelope version and temporal scope are declared.

**Gap:** Opaque scope is not interval containment or an exact version binding.

**Improvement:** Interpret exact envelope and occurrence interval under a selected temporal profile.

**Required controls:** Outside/boundary interval, wrong envelope revision; no cause/recovery from occurrence.

**Keep independent:** cause, blame, severity, recovery.

**Plan:** S01, S18. **Findings:** I04, I08.

## 29. originates-from

[originates-from.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/originates-from.json)

**Source question:** From which source did this identity or content originate?

**Declared effect:** Records origin lineage without asserting transformation, succession, or authority transfer.

**Endpoint policy:** 7 exact pairs in the inventory. **Required qualifiers:** `origin_role`.

**Current coverage:** Origin lineage role is declared.

**Gap:** Origin is not derivation, succession or authority transfer; composition is unspecified.

**Improvement:** Keep origin lineage separate from transformation and define exact permitted composition when required.

**Required controls:** Same origin with different identities; no authority transfer through lineage.

**Keep independent:** derivation, successor, authority-transfer.

**Plan:** S01, S18. **Findings:** I08, I09.

## 30. performs

[performs.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/performs.json)

**Source question:** Which attributable activity is performed or attempted by this Agent Instance?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 5 exact pairs in the inventory. **Required qualifiers:** `session_ref`, `participation_role`, `action_posture`.

**Current coverage:** Session, participation role and action posture are declared.

**Gap:** Participation, attempt and successful action are not independently interpreted.

**Improvement:** Resolve exact session/posture; separate observed participation, successful action and approval.

**Required controls:** Failed/attempted action cannot become success/approval; wrong session fails mapping.

**Keep independent:** ownership, approval, admission, successful-effect.

**Plan:** S01, S18. **Findings:** I04, I08.

## 31. produces

[produces.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/produces.json)

**Source question:** Which governed output was produced by this Agent Action?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 19 exact pairs in the inventory. **Required qualifiers:** `action_receipt_ref`, `production_role`, `output_posture`.

**Current coverage:** Action receipt, production role and output posture are declared.

**Gap:** No generic receipt-to-action/output binding or acceptance proof exists.

**Improvement:** Check selected production receipt and distinguish produced, accepted, correct and effective.

**Required controls:** Receipt for another output; rejected or incorrect produced output.

**Keep independent:** acceptance, correctness, admission, authority-effect.

**Plan:** S01, S18. **Findings:** I08, I09.

## 32. profiled-by

[profiled-by.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/profiled-by.json)

**Source question:** Which exact Agent Profile revision configures this Agent Instance?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 1 exact pairs in the inventory. **Required qualifiers:** `profile_version_ref`, `binding_ref`.

**Current coverage:** Profile version and binding are declared.

**Gap:** No exact subject/profile binding resolution or inherited authority semantics exists.

**Improvement:** Resolve exact binding/revision without capability or identity-continuity inference.

**Required controls:** Wrong profile revision; valid link without capability/authority.

**Keep independent:** conformance, capability, authority, identity-continuity.

**Plan:** S01, S18. **Findings:** I08, I11.

## 33. realizes

[realizes.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/realizes.json)

**Source question:** Which declared design or capability is concretely instantiated by this subject?

**Declared effect:** Records realization or execution without implying conformance, effectiveness, adoption, or evidence acceptance.

**Endpoint policy:** 2 exact pairs in the inventory. **Required qualifiers:** `realization_role`, `exact_target_version_ref`.

**Current coverage:** Realization/execution role and target revision are declared.

**Gap:** Operational execution claims exceed a link; effectiveness/conformance need separate witnesses.

**Improvement:** Define role-specific realization witness and retain separate success/conformance/effectiveness.

**Required controls:** Attempted link cannot prove execution; realized artifact may fail conformance.

**Keep independent:** conformance, effectiveness, adoption, support.

**Plan:** S01, S18. **Findings:** I08, I11.

## 34. requests-resolution-of

[requests-resolution-of.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/requests-resolution-of.json)

**Source question:** Which exact Context version does this Context Request ask to resolve?

**Declared effect:** Records a resolution request without performing resolution or mutating Context.

**Endpoint policy:** 1 exact pairs in the inventory. **Required qualifiers:** `context_version_ref`.

**Current coverage:** Resolution request names a context version.

**Gap:** Version string is not semantically bound; a request does not execute resolution.

**Improvement:** Resolve exact context revision and expose only a recorded request.

**Required controls:** Unresolved request with no context mutation; wrong revision fails mapping.

**Keep independent:** resolution, context-mutation, source-authority.

**Plan:** S01, S18. **Findings:** I08, I11.

## 35. responds-to

[responds-to.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/responds-to.json)

**Source question:** Which Failure Occurrence or Incident is this Agent Action intended to address?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 2 exact pairs in the inventory. **Required qualifiers:** `response_role`, `intended_outcome`.

**Current coverage:** Response role and intended outcome are declared.

**Gap:** Intended outcome is not actual recovery, causal diagnosis or closure.

**Improvement:** Interpret response intent and independently assess recovery.

**Required controls:** Response executed with incident still open; no automatic recovery/cause fact.

**Keep independent:** recovery-success, cause, closure, authority.

**Plan:** S01, S18. **Findings:** I08, I11.

## 36. scopes-authority-over

[scopes-authority-over.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/scopes-authority-over.json)

**Source question:** What governed scope is bounded by this explicit Authority Claim or Authority Boundary?

**Declared effect:** Records an explicit authority subject's bounded scope without granting permission, authenticating the subject, or executing an effect.

**Endpoint policy:** 3 exact pairs in the inventory. **Required qualifiers:** `authority_role`, `scope_ref`.

**Current coverage:** An authority subject's bounded scope is declared.

**Gap:** Role/scope do not authenticate subject, grant permission or execute an effect.

**Improvement:** Resolve exact scope contract and keep subject authentication/permission evidence separate.

**Required controls:** Scope declaration without issuer authentication/permission; no new inference root.

**Keep independent:** permission-grant, claim-authentication, effect-execution.

**Plan:** S01, S18. **Findings:** I01, I08.

## 37. successor-of

[successor-of.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/successor-of.json)

**Source question:** Which predecessor does this successor continue or replace?

**Declared effect:** Records succession; replacement occurs only when succession_effect is supersedes.

**Endpoint policy:** 100 exact pairs in the inventory. **Required qualifiers:** `succession_effect`.

**Current coverage:** Source records succession and says replacement only when succession_effect is supersedes.

**Gap:** Generic strings do not interpret supersedes or execute lifecycle change; competing successors lack policy.

**Improvement:** Define succession-effect declaration meaning first; actual replacement requires checked lifecycle/currentness transition.

**Required controls:** Non-superseding successor keeps predecessor current; competing supersedes need explicit policy.

**Keep independent:** automatic-supersession, identity-equality, authority-transfer.

**Plan:** S01, S18. **Findings:** I04, I11.

## 38. tests-hypothesis

[tests-hypothesis.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/tests-hypothesis.json)

**Source question:** Which exact Hypothesis is this Experiment Design constructed to test?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 1 exact pairs in the inventory. **Required qualifiers:** `hypothesis_version_ref`, `test_role`.

**Current coverage:** Hypothesis revision and test role are declared.

**Gap:** Design, execution and result are not separated; test does not establish truth.

**Improvement:** Bind exact hypothesis/test record with attempted/executed/result/evidence stages.

**Required controls:** Planned/failed test cannot prove support; tested hypothesis can remain undecided.

**Keep independent:** support, contradiction, truth, successful-execution.

**Plan:** S01, S18. **Findings:** I08, I11.

## 39. uses-method

[uses-method.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/uses-method.json)

**Source question:** Which Method does this subject depend on or employ?

**Declared effect:** Records Method dependency without implying conformance, realization, or success.

**Endpoint policy:** 7 exact pairs in the inventory. **Required qualifiers:** `usage_role`.

**Current coverage:** Method dependency/usage role is declared.

**Gap:** Use does not prove method compliance, realization, validation or achievement.

**Improvement:** Interpret usage role and independently assess compliance/outcome.

**Required controls:** Method referenced but not followed; no validated result from use alone.

**Keep independent:** conformance, realization, validation, achievement.

**Plan:** S01, S18. **Findings:** I08, I11.

## 40. uses-tool

[uses-tool.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/uses-tool.json)

**Source question:** Which Tool or Implementation does this Agent Session or Agent Action use?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 4 exact pairs in the inventory. **Required qualifiers:** `tool_version_ref`, `invocation_contract_ref`, `use_role`.

**Current coverage:** Tool revision, invocation contract and use role are declared.

**Gap:** Version/contract are unresolved and no successful execution/authority witness exists.

**Improvement:** Bind exact invocation contract/tool and separate execution receipt if claiming invocation.

**Required controls:** Wrong tool/contract or failed invocation; no conformance/ownership from use.

**Keep independent:** realization, conformance, ownership, authority.

**Plan:** S01, S18. **Findings:** I08, I11.

## 41. violates

[violates.json](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/violates.json)

**Source question:** Which exact expected boundary does evidence indicate was not satisfied?

**Declared effect:** Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

**Endpoint policy:** 4 exact pairs in the inventory. **Required qualifiers:** `boundary_version_ref`, `evidence_posture`.

**Current coverage:** Boundary revision and evidence posture are declared.

**Gap:** Declaration does not establish checked breach, severity or confirmed failure.

**Improvement:** Resolve exact boundary/scoped evidence; distinguish asserted and checked breach.

**Required controls:** Wrong-boundary evidence or unconfirmed report; cause/severity remain absent.

**Keep independent:** cause, severity, authority, automatic-failure-confirmation.

**Plan:** S01, S18. **Findings:** I04, I08.

