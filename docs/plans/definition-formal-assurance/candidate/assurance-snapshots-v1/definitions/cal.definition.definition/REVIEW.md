# Definition: typed formalization review

Candidate progress, 2026-10-08. Authority effect: none. Unit `F01-T.cal.definition.definition` has produced a source-bound static interpretation and checked its exact authored models. The task result is **PARTIAL**: whole-source translation, dependency closure, owner fidelity review and whole-definition proof remain pending. This work follows the foundations-first DAG; it does not promote a source or change the live registry.

The selected source is `cal.definition.definition@1.0.0-candidate.1`, at `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/definition/v1/definition.json`, SHA-256 `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575`. The packet accounts for 23 selected string units through 28 exact clause spans: 11 encoded, seven explanatory and ten deferred. Character coverage establishes traceability; it does not establish preservation of meaning.

## 1. Concept, artifact and logical role

This source defines the concept Definition and the conditions on a Definition artifact. It does not make an arbitrary sentence an axiom and does not turn all text in a definition record into assumptions. The translation separates a genus characterization, an explicit completeness abbreviation, property constraints, explanatory prose and obligations that require other evidence.

`Definition` membership remains a primitive predicate with necessary conditions. The draft does not supply a complete recognizer for every possible Definition. A JSON schema is a separate artifact validator. Successful validation of one source record cannot justify membership or meaning for every record in the mathematical carrier.

No selected axioms or premises were added through the assumption channel. Encoded definition clauses form the selected candidate theory T; explanation and targets do not enter T. Whether this is the correct source interpretation still requires review.

## 2. Types and signatures

The signature has 79 declarations: 15 sorts, 40 predicates or relations, 15 total functions and nine constants. Record, Identity, VersionKey, Term, Meaning, AuthorityScope, Owner, Decision and Voice have separate carriers. ArtifactType, SemanticKind, AuthorityKind, LifecyclePosture, ContextMembership and Axis complete the signature. This is classical many-sorted first-order structure with equality, Boolean connectives and explicit quantification.

Eleven functions expose record observations such as identity, version, term, meaning, scope and owner. Four functions expose the identity, version, scope and owner named by a promotion decision. The functions are total within the abstract carriers, including generic records. Their values are hypothetical observations rather than decoded canonical JSON fields. This design choice is visible and does not prove canonical field validity.

Qualified symbols bind the interpretation to the exact source version and candidate scope. The type checker rejects incompatible function arguments and result sorts. Independent model controls additionally reject an ill-sorted function value and an incomplete table for a declared total function. Nominal type separation alone supplies neither field independence nor semantic-owner agreement.

## 3. Exact version and normative meaning

For each Definition record, `AssignsNormativeMeaning(d,t,m,s)` is equivalent to the selected term, meaning and scope being exactly the corresponding function values. This establishes one assignment in that hypothetical record's exact version. It does not impose a timeless global term-to-meaning function across historical revisions.

Two Definition records with the same identity and different meanings must have different version keys. A negative model keeps the version unchanged while changing meaning and fails T; a positive model changes the version and satisfies T. Another model preserves meaning without forcing a version change. These controls explain the selected condition, but semantic meaning equality itself remains an interpretation input. Byte differences cannot decide it.

`DEF-VERSION-002` retains the need to confirm per-version uniqueness and the scope of active/current lookup uniqueness. The draft does not establish uniqueness across all owners or authority scopes, or implement semantic change detection.

## 4. Completeness, subtype and the source discrepancy

The source notation describes d as one exact Definition version. The candidate lifts that restricted domain into the broader Record carrier explicitly:

```text
DefinitionComplete(d) iff Definition(d) and the ten formal attributes(d).
Definition(d) and DefinitionComplete(d) imply all thirteen prose attributes(d).
```

The ten formal attributes are StableId, ExactScope, FormalVoice, NonNormativePlainVoice, NonNormativeDomainVoice, Boundaries, AdmittedSources, RegistryPostimage, GeneratedIndex and CurrentDriftRoute. The prose additionally names Applicability, Exclusions and PrimaryConsumers. Both source statements are retained. The resulting candidate theory forces these three additional attributes whenever a Definition has the ten formal attributes. A record with the ten attributes and missing applicability cannot satisfy the combined theory, even if its completeness flag is false.

`DEF-COMPLETE-001` records this source discrepancy. It is not a demonstrated contradiction: a complete record with all thirteen attributes supplies a satisfying model. An owner may clarify shorthand, expand the formal expression or revise the prose through the source's authority process. This draft chooses none of those repairs.

The explicit subtype prevents an unrelated generic record labelled complete from supplying the required complete-Definition witness. The corresponding negative control fails T and the relevant population requirements. This is a candidate domain-lifting decision grounded in the notation; it still needs fidelity review.

## 5. Population requirements and vacuity

There are 19 required and 16 unresolved unary population policies. The two initial requirements ask for a hypothetical Definition and a complete Definition. Given T and that complete witness, existence for the thirteen attributes and three genus properties is already entailed. The named plain and domain interpretive voices also entail an InterpretiveVoice inhabitant. These consequences explain the additional explicit requirements; they are not invented owner exemptions or actual-world existence claims.

Policies for auxiliary statuses, standalone kinds, context-local roles, convenience projections and OwnerPromotion remain unresolved. The draft does not require an actual promotion decision merely to demonstrate consistency. A satisfiable partial population set does not discharge the unresolved policies. The theory and all selected required populations are evaluated together in each admissible positive model.

## 6. Authority and non-entailment

CanonicalAuthority requires Definition membership and an OwnerPromotion decision matching four exact observations: identity, version, owner and authority scope. Models with no promotion or a mismatch in any one observation fail the selected canonical-authority constraint. A hypothetical matching decision is a mathematical value; this work creates no real approval.

AdmittedSources is a completeness attribute, Admitted is an object status, and source admission is an external provenance fact. These meanings remain distinct. SchemaValid and EvidencePresent likewise do not substitute for owner promotion.

Four separate query descriptors ask for countermodels to Complete implying Admitted, Complete implying CanonicalAuthority, SchemaValid implying CanonicalAuthority, and EvidencePresent implying CanonicalAuthority. Each target is restricted to Definition records. One complete, valid, evidenced and unpromoted hypothetical Definition satisfies all selected T and population requirements and falsifies all four implications. These are four checked query outcomes supported by the same model, not four independent semantic models.

The targets stay outside T. Non-entailment does not mean every complete record is unadmitted: a positive control permits complete and admitted together. `DEF-ADMISSION-003` also retains the causal/process meaning of “do not perform promotion”; static countermodels do not prove runtime authorization behavior.

## 7. Voices, exclusions and relationships

Plain and domain voices are explicitly interpretive. For a Definition, an interpretive voice may neither weaken nor expand the normative voice. Negative models exhibit violations and fail the constraint. The predicates describe the required relation; they do not analyze natural-language texts or prove a translation preserves meaning.

Standalone glossary entries, ontology nodes, quotations, index rows, narratives, generated summaries and glossary hints cannot supply Definition membership by themselves. A rich Definition may contain quotations or ontology links. Context-local expressions without a shared semantic role are excluded in this source's selected applicability; this does not reject local vocabularies generally. Generated convenience labels are projections. Explicitly declared dependence between axes requires an explicit typed relation, whose canonical validity remains unresolved.

The source declares seven independent classification axes. Seven checked model pairs vary one observation of an additional generic record e while preserving the base Definition d and satisfying T and required populations. These pairs show that the selected abstract theory does not determine those generic-record observations from the other fields. They establish neither valid alternative canonical Definition records nor universal independence of canonical axes. `DEF-AXIS-004` retains allowed values, couplings and inference policy as open work.

## 8. Dependencies and composition

Three authored semantic uses point to exact current versions of Classification, Bounded Context and Typed Relation. The resulting graph has four nodes and three edges, with all three counterpart interpretation packets missing. The graph has no invented recursive fixed-point semantics or family-based semantic dependency edges. Its edge denominator requires independent review, and transitive semantic closure remains unresolved.

The generic `contextMembershipOf` observation does not implement the Bounded Context owner's membership model. A future composition must review carrier mappings and permitted relations against the counterpart definitions. Source ancestry or a linked artifact is not sufficient to infer semantic dependence or compatibility.

## 9. Actual source checks and evidence strength

Nine read-only checks use the actual Definition/v1 schema, pinned generator, source JSON, generated Markdown, proposed registry/index and live registry/index. The source schema and generator digests match. The source passes its schema. Two renders are byte-identical and match the existing projection: 4,819 bytes with SHA-256 `4afb10191db98c5ceb744e599c394a0d6d73982777b6023de194ece7ddbe49b7`. The exact source appears once in each selected proposed and current lookup surface. Two renders of one record do not prove generic renderer determinism.

The current registry records this source as admitted under `CAL-DECISION-0018-DEFINITION-AND-CTX00-PROMOTION`. The historical source's own candidate claim ceiling is preserved. Existing admission of the source does not approve the fidelity of this new formal interpretation. No canonical validator that writes authority receipts was invoked.

The independent denotation evaluator checks 49 authored model controls, the four non-entailment outcomes and seven model pairs. This is direct finite-structure evaluation, without provider enumeration. The Axis carrier has seven values and lies outside the native P02 profile's domain-size cap. No exhaustive-search, proof-kernel, unbounded theorem or full combined-theory result follows. Fresh model, dependency and source-check replays reproduce the stored evidence.

## 10. Remaining work and delivery

Ten clauses remain deferred in the static T, including applicability/scope binding, admission non-entailment, promotion process and schema/render/index obligations. The latter have supplemental actual-source evidence for this one selected input; their generic interpretation and fidelity are still pending. All four findings, sixteen population policies, three counterpart packets and attributable owner review remain open.

Five preserved attempts record a corrected diagnostic expectation, an index-column parser correction, expanded summary/hint exclusions, the completeness subtype/population revision, and an authoring syntax failure corrected before successful evidence generation. Failed attempts supply diagnostic history only.

The closeout checks retain all 662 files in the preceding sealed Axiom delivery and all 201 selected source, registry and provenance files. The full episode still covers 183 current definitions and 189 admitted source versions. There are zero owner-accepted whole translations and zero whole-definition proofs. The next independent foundational draft is Governed Model; source-owner decisions can remain pending while that bounded analysis proceeds. Final episode completion requires the remaining foundation drafts, exact dependency composition, appropriate evidence and a complete review of every formalization aspect.
