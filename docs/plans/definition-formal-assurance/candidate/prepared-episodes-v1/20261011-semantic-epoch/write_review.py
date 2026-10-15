"""Explain all thirteen native Semantic Epoch types/logic aspects and the delivery DAG."""
from pathlib import Path
import json,re
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.semantic-epoch');load=lambda n:json.loads((u/n).read_bytes())
context=load('context.json');counts=load('denominator.json');source=load('source-checks.json');analysis=load('clause-analysis.json');model=load('model-controls.json');fresh=load('fresh-types-logic-results.json');assert all(x['exit_code']==0 and not (u/x['stderr']).read_bytes() for x in fresh)
s='''# Semantic Epoch: types and logic review

This candidate formalizes the exact current Semantic Epoch Definition. Definitions, types and logic precede consumer implementations and effects. The model preserves the immutable owner-selected meaning genus, owner assessment of material changes, an explicit predecessor and material delta, successor selection and applicable lineage. It also preserves representation-only and generated-refresh exclusions. Material semantic judgments, actual owner decisions, immutable storage and operational lineage remain independent outcomes rather than consequences of reference labels.

Schema Evolution Invariant's full 8,729-file seal and separate actual audit passed before native creation. The preflight preserved every prior file hash and all 201 original source files. It verified exact current C28 source, A04/C01/E02 receipts and the declared work-unit write scope. There are now 97 native interpretation files among 183 current identities, leaving 86 without a native interpretation. The last completed whole inventory remains 96 partial drafts and 87 missing until the present unit's full delivery. Accepted whole translations and whole-definition proofs remain zero.

## 1. Exact source, admission and the authority boundary

The selected source is cal.definition.semantic-epoch@1.0.0-candidate.1, SHA e138c57bf7a69f958ca966690428bde166ff9d2137f557a14e153e94028272e3. Current admission is CAL-DECISION-0028-CRAFT-FOUNDATION-V1. The source scope is scope:cyberalchemy-lab-semantic-versioning. Exact source selection fixes which Definition is being interpreted; it does not accept the proposed interpretation or classify any existing artifact's change. Retained candidate-authored metadata and the source's nonexecuting claim ceiling remain intact alongside the current admission overlay.

The checker binds C28's decision, authorization, manifest, validation bytes and selected Definition row. It checks the exact Definition schema and generator digests, two pure human projections and both embedded local upstream sources. Definition@1.0.0-candidate.1 and Bounded Context@2.0.0-candidate.1 remain distinct exact source references. No live producer is authenticated from their bytes, and no operational source-to-consumer map is accepted by those observations.

The source expressly defines semantic versioning meaning without classifying existing artifacts, creating lineage or selecting successors. The candidate therefore supplies declaration guards and finite interpretation witnesses. Its records do not execute a decision. Parent-Instance Authority Separation remains an explicit inference boundary: admitting a meaning, declaring an owner or nominating lineage cannot provide instance authority. Owner decisions and actual effect permission require independent evidence and remain outside the selected theory.

## 2. Sorted vocabulary and qualified references

There are 18 nonempty sorts: AssessmentReference, ArtifactReference, ArtifactIdentity, EpochReference, EpochIdentity, MaterialMeaningReference, NormativeMeaningReference, ScopeReference, ExclusionSetReference, ModelReference, ContractSetReference, RepresentationReference, OwnerReference, SelectionReference, DeltaReference, LineageReference, EvidenceReference and Token. One EMPTY Token constant supports explicit reference-handle guards. Fifty-one total functions and 135 predicate/relation signatures produce 205 declarations. Artifact, epoch, assessment and owner-selection records therefore occupy separate typed domains.

An artifact has eight semantic and representation selectors. An epoch has identity, artifact, aggregate meaning and selection selectors, plus conditionally required predecessor, delta and lineage selectors. An assessment has before/after artifact, predecessor and owner selectors, plus successor-specific fields and optional preservation evidence. Selection, delta and lineage records have their own typed fields. Seventeen typed handle functions distinguish reference presence from semantic denotation. No printed label is treated as a canonical object or an authenticated decision.

Every symbol is qualified by exact Definition version and candidate scope. The same spelling in an upstream definition does not import its interpretation. Total functions provide values for every argument in the finite supplied model; they do not make all values applicable or authentic. Exact BindingDeclared relations must agree with those selector values whenever a selected obligation uses them. Missing, conflicting, undeclared and empty-handle component controls distinguish a nominated value from a complete explicit declaration.

## 3. Epoch genus, immutability and owner selection

EpochApplicable is equivalent to EpochInScopeDeclared. Every selected epoch requires a declared nonempty reference, recorded posture, immutable posture and owner-selected posture. Its exact four base fields nominate an epoch identity, an artifact, aggregate material meaning and one owner-selection record. The artifact must have complete typed component declarations and a versioned semantic posture. Its material meaning selector must equal the epoch's meaning selector. The selection record must point back to that same epoch.

This expresses one immutable owner-selected version of an artifact's normative meaning within the candidate. EpochReference and EpochIdentity remain separate coordinates. A successor reference must differ from its predecessor reference, but global injectivity of epoch identity labels is not invented. A positive model changes one epoch identity label to match another while preserving all necessary reference-based guards. Actual uniqueness, aliases, canonical identity and aggregation policy need accepted owner maps rather than a guess from version strings.

Immutable and owner-selected predicates are declarations. They do not prove a write-protected store, a signed owner decision or successful execution of selection. The selected epoch's reference may be complete while real storage or authority is unproven. Dedicated independent outcome predicates expose this ceiling. Outside epochs remain possible without receiving selected genus obligations. The theory neither classifies every real artifact nor assumes that its finite epoch universe contains every historical or future meaning version.

## 4. Assessment scope and identity preservation

AssessmentApplicable is equivalent to AssessmentInScopeDeclared. A selected assessment declares a before artifact, an after artifact, a predecessor epoch and an owner. Both artifacts are versioned semantic records with all eight exact component fields. The assessment must be recorded and must explicitly separate semantic from representation dimensions. Its before and after ArtifactIdentity references must agree. That retains the source's identity-preserving successor condition without asserting authenticated real-world identity from a token.

ArtifactReference can differ while ArtifactIdentity remains equal. Conversely, a no-change assessment may use the same artifact reference before and after. The positive same-reference control preserves such a no-change case rather than forcing every assessment to create two objects. Identity-changing migrations require their own interpretation and source correspondence; the selected theory does not silently classify them as ordinary identity-preserving semantic successors. Scope selection remains an explicit candidate map.

The owner selector is a declared reference, separate from selection execution and authentication. A model can name an owner and record a material assessment without demonstrating that the named party reviewed it. Assessment universes, the relationship between proposals and actual revisions, evidence adequate for owner judgment and the meaning of identity-preserving change remain findings. These uncertainties are visible in the correspondence packet. They do not prevent expressing necessary guards, and they do not justify claiming sufficient source fidelity or a completed operational change assessment.

## 5. Material meaning, the short iff and owner judgment

MaterialMeaningReference is an aggregate semantic coordinate distinct from raw NormativeMeaningReference. AssessmentMaterialMeaningChangedDeclared is equivalent to unequal before/after aggregate material-meaning references. AssessmentMeaningEqualDeclared is equivalent to equal aggregate references. AssessmentNewEpochDeclared is equivalent to the material-change declaration. This preserves the formal expression's short iff. It is declaration coherence within a supplied interpretation, not a content comparison algorithm or an independent test of the real artifact's meaning.

The richer normative statement adds the owner's determination. AssessmentOwnerDeterminesMaterialChangeDeclared is equivalent to an inclusive disjunction of five material-dimension flags. The aggregate material-change declaration is equivalent to that owner-determination flag. Both source rules remain selected, so their proposed interpretation must agree. This does not hide the distinction between a mathematical inequality shorthand and the owner-assessment criterion. Precedence and the semantic map joining the two remain explicit owner-review obligations.

An assessed dimension is one of normative meaning, scope, exclusions, owned model or semantic contracts. Multiple material flags may hold together. Nothing infers a successful owner process from the presence of any flag. Materiality, normative fidelity, owner determination and identity preservation each have independent actual targets. A selected record can satisfy all necessary declared coherence while those targets remain unevidenced. A source owner must still accept what aggregate meaning and each material dimension denote in a concrete consumer.

## 6. Five coordinates and reference differences

Each material-dimension flag requires unequal references for its corresponding artifact coordinate. Normative meaning compares artifactNormativeMeaning; scope compares artifactScope; exclusions compare artifactExclusions; owned model compares artifactOwnedModel; contracts compare artifactContracts. These are necessary evidence nominations within the finite model. The criterion is inclusive OR, with separate witnesses for all five dimensions. No ordering, priority ranking or exhaustive semantic decomposition beyond those source-named dimensions is introduced.

The converse is deliberately absent: a raw coordinate-reference difference does not automatically mean material change. A positive control changes an otherwise nonmaterial assessment's scope reference while keeping aggregate meaning equal and the scope materiality flag false. Theory and requested populations still hold. The reference may represent aliasing, a different encoding or an unaccepted content map. An opaque reference inequality is inadequate to settle materiality, just as byte inequality is inadequate to establish semantic change.

These declarations require an accepted reference-to-content correspondence before a consumer can infer actual differences. Aggregate meaning equality likewise does not authenticate real equivalence. Different records could nominate the same aggregate reference incorrectly. The model rejects incoherent selected declarations but cannot discover an incorrect semantic nomination merely from a token. Required owner review covers content identity, materiality thresholds, exclusions, model ownership and semantic contracts. Those obligations remain separate from the local theorem-like coherence of the proposed records.

## 7. Representation, bytes and nonsemantic classifications

AssessmentRepresentationChangedDeclared is equivalent to unequal before/after RepresentationReference selectors. It is independent of aggregate material meaning. The baseline includes material changes without a representation-reference change, as well as representation changes without material meaning changes. AssessmentByteChangedDeclared is a separate flag and supplies neither a necessary nor a sufficient successor criterion. Positive controls permit a byte change in a no-change assessment and a material successor without a byte-change flag.

Representation-only, schema-only, encoding-only and derived-refresh classifications each require declared aggregate meaning equality and no new epoch. The baseline supplies a distinct assessment for each alternative. A representation-only assessment marked as a successor fails the formal iff and the selected exclusion. A material successor simultaneously classified as a derived refresh also fails. The model does not require every real representation change to receive one of these labels, or treat the labels as an exhaustive operational taxonomy.

The source separates Semantic Epoch from Representation Revision, generator version and schema revision. Filesystem labels cannot establish succession. Those invalid inference declarations are excluded for selected assessments and remain unconstrained outside scope. The candidate creates no arithmetic rule from v1, v2 or directory names. Actual representation and byte comparisons need their own source maps and observations. Re-encoding the same context is explanatory evidence of the distinction, rather than a universal proof about every Bounded Context migration.

## 8. Explicit predecessor and successor bindings

Every selected assessment identifies an applicable predecessor epoch whose artifact selector equals the before artifact. This obligation also applies to a no-change assessment: it has a selected semantic baseline even when no successor is declared. The predecessor reference and the baseline artifact remain distinct records with exact links. Authentic historical origin, continuity, timestamp order and whether the selected predecessor is current are independent obligations. No latest-version rule is inferred from an opaque reference.

When a new epoch is declared, the assessment must have exact successor epoch, delta, lineage and selection fields. The successor must be applicable and have a reference distinct from the predecessor. Its artifact selector must equal the after artifact. Its conditional predecessor, delta and lineage fields must match the assessment. Its selection must equal the assessment's nominated selection record. These requirements make a claimed successor inspectable without executing creation or accepting historical truth.

Negative controls replace each of these bindings, remove applicability, reuse the predecessor as the successor or point the successor to the wrong artifact. A typed field with a nonempty handle can still be inconsistent with the declared change. Exact equalities expose that mismatch. The theory does not impose an arbitrary total epoch order or prove acyclicity of all semantic dependencies. Global lineage validity and source-history completeness need accepted operational maps and independent evidence beyond these local successor records.

## 9. Owner-selection, material delta and applicable lineage

A new epoch requires a recorded owner-selection record with exact owner, selected epoch, predecessor, delta and lineage fields. The selection owner must match the assessment owner; its epoch must match the nominated successor. The remaining fields must match the assessment's predecessor, delta and lineage. The genus independently ensures that the epoch's selection points back to the epoch. This retains explicit owner selection as a necessary declaration without equating a reference with authenticated consent.

The selected delta is a recorded material delta whose before and after aggregate meaning references equal those of the assessed artifacts. A lineage record is recorded and applicable, and its before epoch, after epoch and delta match the same predecessor, successor and delta. These records keep owner selection, semantic change and lineage separate while requiring exact local coherence. Removing recorded/material/applicable posture or changing any endpoint fails the selected necessary guards.

The delta selectors do not prove that a real semantic delta faithfully represents the change. Applicable lineage posture does not create lineage, repair missing historical segments or authorize a successor. The candidate has independent targets for owner authentication, owner-selection execution, predecessor authenticity, delta fidelity, epoch creation, lineage applicability and lineage creation. Complete record declarations may coexist with all those outcomes false. A legitimate independently supported outcome is allowed; the model does not prohibit authority or real succession grounded in separate evidence.

## 10. Reviewable preservation and optional fields

A preservation claim requires exact EvidenceReference binding and EvidenceReviewableDeclared. It does not imply aggregate meaning equality. The baseline includes a claim alongside a nonmaterial representation-only change and a contested claim alongside a material successor assessment. A positive control adds a preservation claim to another material successor without making theory inconsistent. Reviewability preserves an evidence obligation; automatic equivalence from the claim is an excluded inference declaration.

The source leaves actual preservation review to evidence and judgment. The candidate therefore separates MeaningEquivalence and PreservationReview actual targets from the evidence selector and reviewable flag. Removing reviewable posture fails the necessary claim guard. Naming evidence does not authenticate it, prove adequacy or settle a dispute between a preservation claim and an owner's material assessment. The model can represent that dispute explicitly, while accepted source precedence and the real review outcome remain unresolved.

Successor-specific fields are exact only when a successor is declared; preservation evidence is exact only when a preservation claim is declared. Total selectors outside those conditions provide well-formed table values without asserting optional operational records. An unused outside delta handle can be empty without violating selected guards. Required fields and their optionality therefore remain distinct. Consumers need accepted maps for absence, proposals and contested evidence instead of treating every total-function nomination as a populated physical record.

## 11. Source correspondence and bounded source observations

All 26 nonempty source string units are mapped with exact JSON selectors and full character spans. Fifteen clauses are encoded, nine explanatory and two deferred. The explanatory units retain notation, plain-language intuition and contextual examples. The two deferred units retain authority-scope correspondence and the source's candidate claim ceiling. The entire normative clause contains all fourteen primitive theory formulas. Supporting clauses express their specific necessary requirements rather than repeating unrelated quantified obligations.

The first prepared precheck failed at the fixed verifier-step limit because extensive source-support duplication repeated the same quantified guards. The exact producer, prepared scripts, captures and failed terminal result are retained in attempt 001. The refinement preserved the complete primary theory and all fourteen primitive formulas, left every checker limit unchanged and improved selector-level correspondence. A new actual precheck passed 257 controls with a maximum of 40,834 steps. No failed native producer is substituted with that preparation evidence. The first native builder also failed before outputs because ten required demonstration populations shared identities with unresolved mapping populations. Its producer and terminal capture are retained in native attempt 001. Disjoint unresolved-population identities corrected the contract without changing theory, required demonstrations, source scope or checker limits. The corrected native producer supplies its own successful terminal evidence.

Actual native source checks verify the C28 bindings, shape, source statements, two exact 4,125-byte pure projections, both local upstream digests and source-query correspondence. Thirty-one obligations bind exact source excerpts to thirty-two independent outcome queries without selecting those targets in T. Successful bytes, shape and projection checks do not accept source denotations or real consumer behavior. Twenty-two findings retain the interpretation losses, reference maps and authority ceiling for owner review.

## 12. Finite models, hostile controls and proof limits

The native model suite contains 257 controls: 66 theory-true, 183 theory-false and eight malformed-model rejections. Positive cases retain nonmaterial raw coordinate changes, no-change assessments, independent actual outcomes, contested preservation, optional fields and epoch identity labels without unsupported injectivity. Negative cases remove or conflict with all selected field bindings, empty required handles, break owner/epoch/delta/lineage equalities, confuse semantic and representation flags or claim excluded effects from declarations.

Twenty required populations demonstrate selected and outside epochs and assessments, two selected assessments, all five material dimensions, successor and four nonsemantic alternatives, byte-only and representation-independent cases, a contested preservation successor and a no-change case. They are demonstration obligations for the finite packet. They do not require every real installation to contain all examples. Theory T and population coverage I are evaluated independently; vacuous selected guards can satisfy T while failing requested populations.

Thirty-two non-entailment queries have complete supplied T-and-I countermodels. Actual materiality, ownership, storage, lineage, authority, trust, proof and effects are not inserted into T as positive or negative assumptions. Independently supported actual outcomes remain allowed. These checks establish a bounded inference ceiling for the authored model, not a mechanized whole-definition proof or an accepted shared carrier interpretation. Runtime limits remain one million input bytes, 50,000 IR nodes, 100,000 evaluation steps and a thirty-second timeout. The produced interpretation is 214,197 bytes and its qualified IR contains 22,710 nodes, within the unchanged limits.

## 13. Detailed work DAG and remaining delivery

One illustrative material assessment changes the artifact's declared owned-model coordinate and aggregate meaning, records the owner's material determination, and nominates a distinct immutable successor with an explicit predecessor, material delta, selection and applicable lineage. Those records can satisfy the necessary theory without proving that the actual owner selected the epoch. A counterexample retains the lineage labels but points the selection at a different successor; the exact equality guard rejects it.

Another illustration changes representation while preserving aggregate meaning and declares a representation-only classification. No new epoch follows. A preservation claim may provide reviewable evidence without proving equivalence. Marking that same assessment as a new epoch fails the iff and exclusion. These examples show how types keep the artifact, epoch, owner judgment and lineage distinct, while logic checks their declared relationships. Real change classification and consumer behavior still require accepted source maps and evidence.

```mermaid
flowchart TD
 S[Exact C28 source and SEI full8729 audit] --> A[Native preflight]
 S --> T[Sorted epoch assessment owner selection delta and lineage vocabulary]
 A --> B[Native correspondence and IR]
 T --> B
 B --> I[Required populations and hostile controls]
 I --> C[Independent model and source checks]
 C --> R[Detailed thirteen-aspect review]
 R --> F[Fresh type checks and typed freeze]
 F --> V[Separate typed audit]
 V --> H[Current carrier and consumer inspection]
 H --> P[Qualified source maps and authority profiles]
 P --> D[Reachable dependencies]
 D --> J[Current whole inventory]
 J --> E[Six fresh delivery checks]
 E --> Q[Full delivery review and seal]
 Q --> N[Separate full delivery audit]
 N --> X[Next Withdrawal Record native definition]
```

The seventeen-node, seventeen-edge work DAG is acyclic and separate from the semantic dependency graph. Three fresh typed checks have terminal zero results. The sixteen-input freeze and its separate audit need their own actual results. Current carrier/consumer inspection, qualified map profiles, dependency evidence, the whole 97-draft inventory, six fresh delivery checks, full review, seal and separate full audit remain required. Withdrawal Record native creation follows that full audit.

Original scope remains 183 identities, 189 versions, 201 source files, 121 tasks, 511 planning edges, 797 SWUs and 36 frontiers. No candidate result grants canonical, private, live, publication or external authority. Source-owner acceptance, consumer correspondence, semantic cycle treatment, whole proofs and the final episode-wide aspect review remain pending. The broader goal stays active and is not redefined around this packet or the measurements already completed.

'''
for i,x in enumerate(analysis['known_losses'],1):s+='- SEP-FINDING-'+str(i).zfill(3)+': '+x+' Status: unresolved; accepted owner maps and review pending.\n\n'
s+='Actual source-bound counts: '+json.dumps(counts,sort_keys=True)+'.\n\nActual native evidence: '+json.dumps({'controls':model['control_count'],'queries':len(model['nonentailment_countermodels']),'source_checks':len(source['checks']),'source_query_obligations':len(load('source-query-obligation.json')['obligations'])},sort_keys=True)+'.\n'
assert len(re.findall(r'^## [0-9]+\.',s,re.M))==13 and len(s.split())>3000
with (u/'REVIEW.md').open('x') as f:f.write(s)
with (u/'CONTINUATION.md').open('x') as f:f.write('''# Semantic Epoch types-and-logic continuation

Exact current C28 source-bound native T/IR/correspondence and source/model observations are complete. Three fresh typed checks passed. The sixteen-input freeze and separate actual audit must supply terminal results. Working native count97 leaves86withoutT; last completed full inventory96/87. Source-owner accepted whole translations zero,whole proofs zero,source fidelity pending,semantic readiness false.

Next: current carrier/consumer/source maps,qualified profiles,reachable dependencies,whole97draft inventory and independently evaluated witnesses,sixfreshdeliverychecks,fullreview,seal and separateactualaudit. Withdrawal Record native work is gated on that full audit. Preserve8729priorfilehashes and201sourcebytes. Retain the failed prepared step-limit attempt and unchanged complete primary theory. No canonical/private/live/publication effects or accepted source-owner maps are implied.
''')
with (u/'DELIVERY-CONTEXT.md').open('x') as f:f.write('''# Semantic Epoch types-and-logic context

Selected F04-T.cal.definition.semantic-epoch follows SEI full8729-file seal and separate actual audit0. Structured context binds exact C28 source,A04/C01/E02 receipts,SWU output/write scope,source-only inspection,prior seals,prepared/native producers and the retained failed precheck. Definitions/types/logic stay first. Original183/189/201scope and121/511/797/36planningdenominators remain fixed. No actual semantic successor or lineage is selected or created.

The source's short material-meaning iff and richer owner determination criterion are both explicit. The five material dimensions are inclusive;raw label difference is not sufficient materiality. Representation,byte changes,preservation claims and actual outcomes remain separate. Preservation claims carry reviewable evidence and may coexist with contested material assessments. Conditional successor and evidence bindings do not assert unused records. Complete primary theory survived source-support refinement with unchanged checker limits.

The typed freeze contains16inputs. Full carrier/dependency/inventory evidence and full seal/audit remain pending;last full inventory96/87,working native97/86. All8729priorfiles201sources remain immutable. Source fidelity and whole translation pending;whole proofs0;semantic readinessfalse;goalactive. No canonical/private/live/publication effects.
''')
print(json.dumps({'result':'written-thirteen-aspect-SemanticEpoch-review','words':len(s.split()),'aspects':13,'findings':22,'dag_nodes':17,'dag_edges':17},indent=2))
