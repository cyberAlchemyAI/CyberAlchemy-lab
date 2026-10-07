---
node_type: agent-dialogue
status: research-complete-awaiting-human-gate
authority_effect: none
date: 2026-10-05
topic: lab-complete-model-audit
---

# Parallel investigation: complete CyberAlchemy Lab model

## Central question

Does the repository currently contain a complete, coherent, enforceable Lab model joining Definitions, Artifact Types, relation semantics, Ontology, contestability, Context, Product, Project, Research, Experiment, packaging, and runtime lifecycle? If not, what exact gaps block one coordinated admission?

## Assumptions challenged

1. The 26 Artifact Types are complete and orthogonal.
2. Every admitted Definition has the correct carrier.
3. The 23 Relation Kinds and 147 endpoint pairs are complete.
4. Typed Relations and Ontology edges are correctly separated.
5. Ontology, package, and lifecycle runtime share one consistent authority model.
6. Challenge, Governance, Product, Project, Research, Experiment, and Context are integrated.
7. Every relation endpoint kind has a resolvable carrier.
8. Embedded status and decision overlays expose one reliable current state.

## Investigation design

### Agent 1: Definitions and Artifact Types

- Concern: semantic inventory, carriers, schemas, and lifecycle overlays.
- Question: what exists, what is admitted, and where do meaning and carrier shape diverge?
- Exclusions: relation semantics beyond carrier mapping; runtime mechanics beyond status effects.

### Agent 2: Relations and Ontology

- Concern: axis orthogonality, endpoint closure, Typed Relation identity, Ontology representation, and contestability.
- Question: does the 23-axis candidate form a complete enforceable connection model?
- Exclusions: runtime internals except interfaces; full product inventory except endpoints.

### Agent 3: Runtime, Product, and Context

- Concern: lifecycle runtime, migration generations, Product/Project/Research/Experiment/Context integration, and adapters.
- Question: can current admitted contracts operate as one system?
- Exclusions: redefining core Definitions or Relation Kind semantics.

### Rejected decomposition

A directory-by-directory split was rejected because it would hide contradictions that cross authority, migration, runtime, product, and evidence directories.

## Agent 1 report: Definitions and Artifact Types

### Key Findings

1. The canonical registry contains 118 admitted Definition versions across 112 current identities. A later candidate adds `cal.definition.typed-connection-extension-rule@1.0.0-candidate.1`, producing 119 visible non-fixture versions across 113 identities: 118 admitted and one unadmitted. Evidence: `docs/decisions/0053-full-definition-queue-admission/decision.json`, `authority/definitions/registry.json`, and `authority/definitions/candidates/0012-typed-connection-extension-rule/candidate.json`.

2. The 26 migration Artifact Types are one scoped cohort. Their effective state is six direct admissions, two duplicate resolutions, and 18 candidate-unadmitted packages. Product resolves to Product Identity; Project resolves to Project Identity with known field loss. Evidence: `authority/artifact-types/candidates/0004-remaining-26-materialization/candidate.json`, admission overlays under `authority/artifact-types/admissions/migration-26/v1`, and resolutions under `authority/artifact-types/resolutions/migration-26/v1`.

3. Static inventory finds 46 Artifact Type identities and 55 descriptor versions under `authority/artifact-types/**/artifact.json`, plus migration-only carriers under `evidence/migrations/**/artifact-types`. Decision 0052 admitted 26 types, 25 profiles, 25 relation kinds, and seven surfaces only within migration scope.

4. Effective status is distributed across immutable descriptors and decisions. At least 32 carrier descriptors retain stale candidate Definition posture after decision 0053. Ontology Package still says no admitted local Ontology Definition exists, although decision 0053 admitted it.

5. Several distinct carriers reuse broader Definitions: Context Profile uses Context; Capability Realization Binding uses Product Capability; Measurement Method and Result use Residue Measurement; Model Instance Binding uses an invariant. Ontology also claims a typed governed graph while its schema stores free string reference arrays.

### Gaps and inconsistencies

- Typed Connection Extension Rule is outside the live Definition registry.
- The remaining 18 carriers have no admission decision.
- The 25 migration profiles are scoped lookup contracts rather than repository-wide profile carriers.
- No canonical effective Artifact Type registry joins descriptors, admissions, successors, and resolutions.
- Ontology Package contains a stale semantic blocker and external `CAV2-D19` binding.
- Specialized carrier meaning is often present only in Artifact Type prose and schema.
- Withdrawal Record has no standalone Definition.
- Project duplicate resolution preserves loss of goal references, purpose references, lifecycle, owner routes, and evidence index.
- Three `cal.*` and `craft.*` workflow Definition pairs remain current without explicit specialization or succession.
- Of 112 current Definition identities, 45 are not referenced by inspected Artifact Type descriptors. Many may be intentionally non-instantiable; the repository does not classify them.

### Local tensions

- Immutable evidence versus readable current state.
- Definition-first governance versus specialized schema meaning.
- Migration completeness versus repository completeness.
- Orthogonality versus shared semantic roots.
- Ontology identity versus package identity.
- Duplicate resolution versus field-level conformance.
- Global versus local workflow namespaces.

### Questions for synthesis

1. Should the 26 queue be treated as a historical cohort under a repository-wide effective registry?
2. Must every distinct Artifact Type have a same-granularity positive Definition?
3. Should the five specialized carriers receive Definitions before remaining-18 admission?
4. Must the Typed Connection Extension Rule be admitted before Relation Kinds?
5. How should Ontology Package reconcile `CAV2-D19` with the admitted local Ontology Definition?
6. Should Ontology embed governed node/edge records or reference standalone carriers?
7. Should `craft.*` workflow meanings specialize or replace their `cal.*` counterparts?
8. Does Project Identity/v1 need a successor before complete-model admission?
9. Should immutable descriptor statuses remain with a generated effective-state projection?
10. Which uncarried Definitions are intentionally non-instantiable?

## Agent 2 report: Relations and Ontology

### Key Findings

1. The 23 Relation Kinds form a closed candidate grammar. They are not admitted or usable as a canonical relation system. The required Typed Connection Extension Rule is candidate-only, no Relation Kind Artifact Type exists, and the only Typed Relation carrier supports one Artifact Type-to-Definition profile.

2. The 147 pairs name 50 endpoint kinds; 22 have no canonical carrier. Static cross-counting finds 57 pairs with at least one carrierless endpoint and only 32 pairs with two admitted endpoints. Identity Graph owns five admitted directional signatures but is neither inventoried nor mapped by the 23-axis model.

3. The no-collapse validator is structurally tautological. It verifies unique IDs, questions, and hand-authored hostile examples, but performs no semantic inference. Qualifier domains, types, pair-specific values, and cross-qualifier constraints are absent.

4. The general Ontology schema uses free string `node_refs` and `relation_refs`. Ontology Package structures nodes and edges but accepts any relation `type_ref` and carries no global/local scope, exact Relation Kind version, endpoint kinds, qualifiers, lifecycle, authority effect, or projected Typed Relation binding.

5. Contestability cannot bind to all subjects named by its Definition. Current `governed-by` pairs are narrow, Policy edge references are unchecked strings, and challenge modes differ between profile and Policy witnesses.

### Gaps and inconsistencies

- Missing canonical carriers include Relation Kind, Typed Relation, Ontology Node, Policy, Constitution, Decision, Source, Evidence Set, Authority Claim, Contract, Schema, Implementation, Responsibility, and other endpoints.
- The endpoint universe omits several admitted governance and graph surfaces.
- Method Binding is incorrectly substituted for Method even though it separates Method, binding, and subject identities.
- The model does not define whether specialized relation artifacts are canonical instances, evidence for a generic relation, or projections.
- Product Capability embeds writable relation references while the global matrix separately permits equivalent connections.
- Required qualifier names have no closed schemas or pair-specific values.
- `product-capability -> product` appears under both membership and classification.
- Identity Graph mappings are absent and some require direction reversal.
- Ontology lacks global/local relation scope and subject representation contracts.
- Challenge bindings for node, edge, claim, and authority subjects are incomplete.
- `validation_edges` has no exact semantic interpretation.
- Representation, production, dependency, constraint, observation, drift, and coordination need explicit global/local scope decisions.
- Possible missing pairs include `ontology-package -> ontology` and `ontology -> source`.
- Effective lifecycle resolution through decision overlays is not encoded in endpoint resolution.

### Local tensions

- Closed pairs versus open qualifier semantics.
- Global Typed Relation versus domain relation carriers.
- Internal Ontology records versus independent endpoint carriers.
- Ontology edge versus artifact relation.
- Challenge route versus Contestability Policy.
- Identity Graph direction versus normalized global direction.
- Specialized binding identity versus direct relation.

### Questions for synthesis

1. Do the 23 axes cover every Lab relationship or only shared cross-domain predicates?
2. Which carrier owns each canonical relation instance?
3. How do specialized carriers project into global relations?
4. Are Ontology Node and Edge internal records or independent Artifact Types?
5. What is the exact qualifier schema for each axis and pair?
6. Is Product Capability both a member and an instance of Product?
7. How does Identity Graph map into global axes?
8. Does `challenge_route` resolve an exact Policy or only route work?
9. What semantics may populate `validation_edges`?
10. Which local concepts warrant new global axes?
11. Should admission order be extension rule, Relation Kind carrier, Relation Kinds, Typed Relation carrier, Ontology, then Policy bindings?

## Agent 3 report: Runtime, Product, and Context

### Key Findings

1. The adopted event runtime integrates only a 14-node/15-relation navigation overlay. Its migration coverage is explicitly partial. The v4 source runtime covers 21 packages, 815 nodes, 1,210 relations, and 422 documents but has Product approval only; binding admission, runtime adoption, cutover, and source retirement are absent.

2. Product Identity/v2, Product Thesis, Product Capability, and Capability Realization Binding are admitted-current, with zero admitted instances and zero consumer activations. The existing Ontology Product remains a separate v1/test-candidate package and runtime with no adapter into the admitted Product model.

3. Project and Research types are partially established. Experiment and Context integration remains candidate-only, with unresolved exact Relation Kind endpoints and string references.

4. Runtime ContextSelector/ContextProjection interfaces and the new Context Request/View contracts form two unconnected interface families. The epoch-002 Context Map implementation is admitted-inactive and migration/cutover remain unperformed.

5. Challenge mode vocabularies differ: runtime uses `evidence`, `contradiction`, and `owner_review`; Policy uses `contradict` and `request-validation`; the profile accepts only `contradict`.

### Gaps and inconsistencies

- v4 frozen candidate status differs from its later Product approval overlay.
- Ontology canonical `record.json` conflicts with event histories as mutable source of truth.
- Ontology Product package runtime has no importer/exporter for the Ontology Artifact Type or lifecycle event store.
- Experiment references are structurally strings; equality is checked only across bundled fixtures.
- Remaining-18 carriers and their exact relation endpoints remain unadmitted.
- Ontology Package relation types are locally open strings.
- Current runtime continuity is unproven in the present workspace.

### Local tensions

- Canonical identity versus canonical history.
- Generic Context versus Coordination Context.
- Closed schemas versus open references.
- Product type completeness versus operational emptiness.
- Additive migration generations versus converged successor path.

### Questions for synthesis

1. Should identity/configuration, event state, and packages/views have distinct canonical postures?
2. Should v4 succeed v2 directly or adapt into the v2 event contract?
3. Which Product instances represent Ontology Product and migration runtimes?
4. Does Context specialize, subsume, or convert to Coordination Context?
5. What owns Context Request-to-Selector and Projection-to-View translation?
6. What normalized challenge vocabulary connects Policy, profile, and runtime?
7. Must remaining-18 wait for endpoint closure?

## Synthesis: cross-layer tensions

### 1. Completeness is scoped differently in each layer

The Definition registry is nearly closed, the 26 queue is a migration cohort, the 23 axes are a candidate grammar, and the runtime is a partial migration. Each layer uses a valid local completeness claim, but those claims do not compose into repository-wide completeness.

### 2. Authority state cannot be read from one place

Immutable candidate descriptors preserve evidence while decisions change effective status. This is legitimate governance, but consumers lack a generated resolver. The older Artifact Type registry is already stale for Product Identity/v1, and Ontology Package retains a stale Definition blocker.

### 3. Connection closure exists only at the endpoint-name level

The pair matrix blocks wildcard expansion, yet endpoint carriers, qualifier domains, lifecycle resolution, and canonical relation instances remain open. Identity Graph, Context Map, and specialized bindings already own relations, so global relation authority must be defined as a projection contract rather than assumed.

### 4. Ontology is the integration junction and currently the weakest schema

The admitted Ontology meaning is rich, the runtime mechanics are strong, and the package is partially structured. The general carrier between them is a refs-only schema. It cannot enforce typed graph state, contestability, or global/local relation scope.

### 5. Product and Research modeling is ahead of operational use

Product and Research types are admitted, but no instances or consumers realize the model. Experiment and Context types remain candidate-only, leaving the full learning loop structurally described but operationally empty.

### 6. One coordinated release requires ordered subdecisions

The extension rule, carrier Definitions, effective registry, Relation Kind carrier, qualifier schemas, Typed Relation carrier, Ontology revision, Policy normalization, runtime adapters, and remaining-18 carriers have dependency order. A single release envelope can bind them, while each authority effect remains an explicit atomic subdecision.

## Human gate notes

Recommended synthesis decisions:

1. Treat the 26 types as a migration cohort under a repository-wide effective-state registry.
2. Allow shared Definitions only through explicit specialization contracts.
3. Admit the Typed Connection Extension Rule before the relation foundation.
4. Use one canonical global Typed Relation identity and digest-bound mappings from specialized carriers.
5. Keep Ontology Node and Edge as governed internal records unless independent lifecycle requirements justify standalone Artifact Types.
6. Split Ontology canonicality into manifest identity/configuration, event histories for mutable state, and derived cuts/packages/views.
7. Normalize Challenge Contract modes before Policy and Ontology admission.
8. Select one runtime successor and require Context and package adapters.

### Follow-up correction: Intent realization

Subsequent review found that the admitted Intent carrier is explicitly listed as having no Relation Kind connection, while its `satisfaction_refs` are free strings and Implementation has no canonical carrier. The integrated model was corrected to require an Intent Resolution or Decision, an `addresses-intent` axis, a closed `decision -> intent` lifecycle-effect pair, a governed Implementation carrier, the existing `implementation -> product-capability` realization pair, and an evidence-backed Intent satisfaction decision.

### Follow-up correction: Actor and Agent

Further review found no admitted Actor or Agent Definition, no Agent operational Artifact Type family, and no Actor or Agent endpoint in the global relation model. Person is explicitly distinct from Agent, while the imported Ontology Product contains local Human Participant, Work Owner, Machine Collaborator, and Ontology Steward actor nodes. The integrated model introduces separate Profile, Capability, Instance, Session, Action, Assignment, Principal, and Delegation records. The full review is preserved at `.arcanum/ontology-vault/2026-10-05-actor-agent-model-review.md`.

### Follow-up correction: ephemeral Machine Agent and memory ownership

The Agent model was tightened after owner feedback. Actor and Agent are abstract classifications. A Machine Agent is a concrete ephemeral Agent Instance created for one Session and terminated with it. It has no hidden cross-session identity or memory. Durable long-term memory belongs to Project State and reaches each new Session through exact Context and Ontology Views. Short-term working memory belongs only to the Session and expires with it. Only explicitly persisted artifacts, events, receipts, or evidence may survive as governed Project State.

### Follow-up correction: operational lessons from Agent work

Useful learning from an Agent Session must pass through a governed Project State workflow. Attributable work produces Observations, feedback, receipts, Evidence, Findings, or Residue; an Agent Reflection may derive a scoped Operational Lesson candidate; a later new Machine Agent can see an eligible exact revision only through its Context and Ontology Views. Lesson selection, actual application, outcome assessment, and target-specific promotion remain separate records. Silence, dispatch, task completion, or Agent self-report cannot establish improvement, and no lesson authorizes autonomous Profile, Policy, Definition, validator, Implementation, or serving changes. The full review is preserved at `.arcanum/ontology-vault/2026-10-05-agent-operational-learning-model-review.md`.

### Follow-up correction: classifications

The Lab already admits Classification Axis, Classification Orthogonality Invariant, and Artifact Surface Classification Definitions, but it lacks general Classification Scheme and Classification Assignment carriers. The integrated model now gives every Scheme versioned axes, values, cardinality, mappings, compatibility, owner, and challenge rules; every Assignment binds an exact subject revision to one Scheme, Axis, and Value with Agent Action, Method, Implementation, evidence, lifecycle, and decision provenance. Actor kind, lesson kind, trigger kind, target work kind, evidence posture, and generalization level remain independent. Classification does not establish identity, conformance, lifecycle transition, authority, membership, realization, applicability, or success. The full review is preserved at `.arcanum/ontology-vault/2026-10-05-classification-model-review.md`.

### Follow-up correction: failure modes

The repository has admitted Observation, Finding, Residue, Measurement, Validation, Invariant, Method, and Workflow meanings, plus local Agent Reasoning runtime failure and recovery records, but no general Failure Mode carrier. The integrated model now separates design-time Failure Mode, one observed Failure Occurrence, an evidence-bounded Failure Assessment, and a Failure Control Binding for prevent, detect, contain, recover, or compensate. Incident is an optional coordinated response envelope. Failure classification uses governed Schemes and Assignments; a repeated symptom, reason code, exception, retry, replayed notification, user correction, or Agent explanation cannot establish recurrence or cause. Recovery can leave degraded state, unknown effects, and Residue. The full review is preserved at `.arcanum/ontology-vault/2026-10-05-failure-mode-model-review.md`.

### Follow-up integration: failure to operational learning

The complete Lab model now includes the full feedback loop from expected boundary and Failure Mode through signal, Failure Occurrence, Failure Assessment, Agent Reflection, Operational Lesson, later View selection, Lesson Application, Lesson Outcome Assessment, Improvement Target, Research or Experiment, Finding, owner Decision, target-specific change, and Failure Control Binding. It explicitly preserves the Session boundary: the Machine Agent and Session Memory expire, while governed failure and lesson records survive in Project State and reach a new Agent only through Context and Ontology Views. The integrated two-Session example and record-ownership table are in `.arcanum/ontology-vault/2026-10-05-lab-complete-model-audit.md`.

### Follow-up correction: other operational experience

Failure is only one operational-learning input. The complete model now separately routes successful outcomes, corrections, changed requirements, communication and decision preferences, Research and Experiment results, challenges, drift, residue, near misses, improvement opportunities, and unknown external effects. Each first enters its owning canonical record; only an evidence- and scope-bounded future-behavior hypothesis proceeds through Reflection into an Operational Lesson. The model adds candidate needs for Operational Observation, Work Outcome Assessment, Feedback Record, Communication Preference, Preference Application Assessment, Drift Assessment, and Improvement Signal because the admitted Observation meaning is Research/Experiment-specific and no general carriers currently cover these routes. Immediate correction, Intent revision, Context refresh, recovery, containment, and challenge handling remain independent of lesson formation.

No admission or implementation mutation was performed during this investigation.

## Follow-up artifacts

- `.arcanum/ontology-vault/2026-10-05-lab-integrated-model.md`
- `.arcanum/ontology-vault/2026-10-05-lab-complete-model-audit.md`
- `.arcanum/ontology-vault/2026-10-05-definition-artifact-relation-interaction-review.md`
- `.arcanum/ontology-vault/2026-10-05-agent-operational-learning-model-review.md`
- `.arcanum/ontology-vault/2026-10-05-classification-model-review.md`
- `.arcanum/ontology-vault/2026-10-05-failure-mode-model-review.md`
- `authority/artifact-types/candidates/0005-remaining-18-complete-model/MODEL.md`
- `authority/relation-kinds/candidates/0002-axis-orthogonal-model/RELATIONS.md`
