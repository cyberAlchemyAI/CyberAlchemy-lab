---
node_type: semantic-gap-audit
status: review-candidate
authority_effect: none
audit_date: 2026-10-06
target_model: .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md
source_audit: .arcanum/ontology-vault/2026-10-05-lab-complete-model-audit.md
---

# CyberAlchemy Lab missing Definitions, Artifact Types, and relationships

## Status and claim ceiling

This audit compares the current working tree with the integrated Lab target model. It includes uncommitted repository material because the authority packages and review artifacts are currently untracked or modified.

It identifies exact semantic and carrier gaps. It does not admit a Definition, Artifact Type, Relation Kind, instance, runtime, control, or consumer. “Missing” means absent from the canonical root authority surface required by the target model; migration evidence, narrative prose, runtime-local records, and review documents do not by themselves fill that gap.

## Executive result

| Surface | Current repository state | Gap against integrated model |
| --- | --- | --- |
| Definitions | 118 admitted versions, 112 current identities, plus one validated candidate extension rule | 60 explicit target terms have no exact current Definition identity; 29 have review prose and 31 still need first Definition candidates |
| Artifact Types | 55 visible descriptors across 46 identities; effective state requires decision overlays because all descriptor files still say `candidate-unadmitted` | 18 materialized migration types await admission; 30 operational/state carriers and 10 semantic/governance foundation carriers have no root package; 14 other relation endpoints need a carrier-or-removal decision |
| Relation Kinds | 23 candidate axes, 147 exact pairs, 50 endpoint kinds | No admitted general Relation Kind carrier or general Typed Relation carrier; 22 endpoint kinds have no canonical carrier; 57 pairs touch a carrierless endpoint |
| Qualifiers | 33 named required qualifier axes | No closed qualifier JSON Schemas, pair-specific value domains, or cross-qualifier constraints |
| Integrated extensions | 13 proposed new axes in the master model | Six additional semantic connections or scope decisions are still absent from the extension table |

The repository therefore has a strong semantic inventory and several mature candidates, but it does not yet have an admissible closed Lab model.

## Evidence basis

The audit read:

- `authority/definitions/registry.json` and its generated index;
- every `authority/artifact-types/**/artifact.json` descriptor;
- admission and duplicate-resolution overlays for the 26-type migration cohort;
- `authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json`;
- its endpoint inventory and validation receipts;
- the integrated model and its Actor, learning, classification, failure, and ontology reviews.

Static recounts produced:

```text
Definition registry versions:       118
Current Definition identities:      112
Later candidate Definitions:          1

Artifact Type descriptor files:      55
Artifact Type identities:            46
Distinct Artifact Type refs:         48

Candidate Relation Kinds:             23
Declared endpoint pairs:             147
Named endpoint kinds:                 50
Distinct required qualifier axes:     33
Pairs with two admitted endpoints:    32
Pairs with a carrierless endpoint:    57
```

## Definition gaps

### One materialized prerequisite remains unadmitted

`cal.definition.typed-connection-extension-rule@1.0.0-candidate.1` exists, validates, and remains candidate-unadmitted. No Relation Kind successor or new pair can be admitted under the proposed closed-world grammar until this rule is admitted.

### Twenty-nine reviewed meanings have no Definition artifact

These identities have candidate wording in the 2026-10-05 review documents. They have no canonical Definition package and do not appear in the live registry.

#### Actor, Agent, state, and memory: 13

1. `cal.definition.actor`
2. `cal.definition.agent`
3. `cal.definition.principal`
4. `cal.definition.agent-profile`
5. `cal.definition.agent-capability`
6. `cal.definition.agent-instance`
7. `cal.definition.agent-session`
8. `cal.definition.project-state`
9. `cal.definition.session-memory`
10. `cal.definition.ontology-view`
11. `cal.definition.agent-action`
12. `cal.definition.agent-assignment`
13. `cal.definition.delegation`

#### Operational learning: 6

1. `cal.definition.agent-reflection`
2. `cal.definition.operational-lesson`
3. `cal.definition.lesson-application`
4. `cal.definition.lesson-outcome-assessment`
5. `cal.definition.improvement-target`
6. `cal.definition.operational-learning-cycle`

#### Classification: 4

1. `cal.definition.classification`
2. `cal.definition.classification-scheme`
3. `cal.definition.classification-value`
4. `cal.definition.classification-assignment`

The admitted Classification Axis, Classification Orthogonality Invariant, and Artifact Surface Classification meanings do not supply these four identities.

#### Failure handling: 6

1. `cal.definition.failure`
2. `cal.definition.failure-mode`
3. `cal.definition.failure-occurrence`
4. `cal.definition.failure-assessment`
5. `cal.definition.failure-control-binding`
6. `cal.definition.incident`

### Thirty-one additional target meanings need first Definition candidates

These terms are load-bearing in the integrated model or its current relation endpoint universe and have no exact Definition identity or reviewed Definition candidate.

#### Semantic, work, and ontology foundation: 15

1. Intent Resolution
2. Implementation
3. Relation Kind
4. Typed Relation
5. Ontology Node
6. Ontology Edge
7. Ontology Manifest
8. Ontology Cut
9. Semantic Event History
10. Governance Event History
11. Work
12. Tool
13. Generated Output
14. Principal Reference
15. Governed Model

#### Governance and contestability: 9

1. generic Policy
2. generic Decision
3. Contract
4. Decision Scope
5. Effect
6. Review
7. Source
8. Challenge Contract
9. Challenge Event

Contestability Policy, Decision Bundle, Decision Checkpoint, and Source-Ledgered Consolidation are admitted narrower meanings. They do not define the generic concepts above.

#### General operational experience: 7

1. Operational Observation
2. Work Outcome Assessment
3. Feedback Record
4. Communication Preference
5. Preference Application Assessment
6. Drift Assessment
7. Improvement Signal

The admitted Observation meaning is Research/Experiment-specific. User Decision Preference concerns decisions, so it does not supply Communication Preference.

### Definition-to-carrier binding decisions remain open

Five specialized Artifact Types currently reuse broader or invariant Definitions:

| Artifact Type | Current semantic binding | Required decision |
| --- | --- | --- |
| Context Profile | Context | Add a positive Definition or declare a formal specialization |
| Capability Realization Binding | Product Capability | Add a positive Definition or declare a formal specialization |
| Measurement Method | Residue Measurement | Add a positive Definition or declare a formal specialization |
| Measurement Result | Residue Measurement | Add a positive Definition or declare a formal specialization |
| Model Instance Binding | Parent-Instance Authority Separation Invariant | Add a positive Definition or declare a formal specialization |

Additional unresolved Definition work:

- decide whether generic Ledger remains excluded or receives a positive Definition;
- define Withdrawal Record or declare an exact specialization;
- resolve the three `cal.*` and `craft.*` workflow Definition overlaps through specialization or succession;
- decide whether Project Identity needs a v2 Definition/carrier contract before permanent use;
- classify current Definitions without carriers as intentionally non-instantiable or carrier-required.

## Artifact Type gaps

### Eighteen existing candidates await admission

These root packages exist and remain candidate-unadmitted:

1. Finding
2. Experiment Design
3. Experiment Run
4. Observation
5. Measurement Method
6. Measurement Result
7. Ontology
8. Context
9. Context Profile
10. Context Request
11. Context View
12. Model Instance Binding
13. Person Reference
14. Identity Claim
15. Team
16. Team Membership
17. Role
18. Role Assignment

They should be revised against the final Definition and relation foundation before batch admission.

### Thirty operational and state carriers have no root package

#### Agent, state, and execution: 11

1. Agent Profile
2. Agent Capability
3. Agent Instance
4. Agent Session
5. Session Memory
6. Agent Action
7. Agent Assignment
8. Principal Reference
9. Delegation
10. Ontology View
11. Project State, or an explicit derived-state manifest/cut contract

Actor and Agent remain abstract classifications. A durable Machine Agent Artifact Type is forbidden by the current model.

#### Operational learning: 5

1. Agent Reflection
2. Operational Lesson
3. Lesson Application
4. Lesson Outcome Assessment
5. Improvement Target

#### General operational experience: 7

1. Operational Observation
2. Work Outcome Assessment
3. Feedback Record
4. Communication Preference
5. Preference Application Assessment
6. Drift Assessment
7. Improvement Signal

#### Classification: 2

1. Classification Scheme
2. Classification Assignment

Classification Axis and Classification Value may remain governed internal Scheme records until independent lifecycle, ownership, relations, or direct challenge require promotion.

#### Failure handling: 5

1. Failure Mode
2. Failure Occurrence
3. Failure Assessment
4. Failure Control Binding
5. Incident

Fault and Error State may initially remain defined classification values.

### Ten semantic and governance foundation carriers are required

1. Intent Resolution
2. Implementation
3. Relation Kind
4. Typed Relation
5. Decision
6. Policy
7. Authority Claim
8. Constitution
9. Evidence Set
10. Tool

Some of these appear as documents, migration-only carriers, embedded records, or runtime structures. None currently has the required canonical root Artifact Type package for the integrated model.

### Fourteen existing endpoint kinds require a carrier-or-removal decision

After accounting for the foundation carriers above, the current relation matrix still references these unresolved endpoint kinds:

1. Contract
2. Decision Scope
3. Effect
4. Evaluation
5. Generated Output
6. Governed Model
7. Hypothesis
8. Ontology Node
9. Person
10. Responsibility
11. Review
12. Schema
13. Source
14. Work

Each must receive a canonical carrier, map to an exact admitted specialization, become a governed internal record, or be removed from the admitted pair set. A named endpoint with no resolution cannot remain in a closed admitted grammar.

### Carrier posture decisions

| Concept | Recommended posture |
| --- | --- |
| Ontology Node and Ontology-local Edge | Governed internal Ontology records until independent lifecycle or cross-Ontology use requires standalone types |
| Global Ontology Edge | Digest-bound projection of one canonical Typed Relation |
| Project State | Durable aggregate with an exact manifest/cursor contract; decide whether the manifest is an Artifact Type or derived cut |
| Ontology Manifest and Ontology Cut | Identity/configuration manifest plus derived consistent-cut contract; avoid competing canonical stores |
| Principal Reference | Separate reference carrier unless the Principal Definition explicitly owns a closed reference specialization |
| Challenge Contract | Closed Policy subrecord unless independent reuse and lifecycle justify a standalone type |
| Challenge Event | Governed event record with exact subject, mode, evidence, owner route, resolution, and residue |

## Relationship gaps

### No global relation system is admitted

All 23 current axes remain candidate-only:

```text
member-of                 contributes-to
uses-method               evaluates
realizes                   engages-inquiry
originates-from            derives-from
evidence-bears-on          governed-by
declares-effect-on         instance-of
binds-implementation       conforms-to
inherits-contract          frames
requests-resolution-of     fulfills-request
successor-of               assigned-to
asserts-identity-of        scopes-authority-over
carries-definition
```

The candidate has 147 closed ordered pairs, but only 32 pairs join two admitted-current endpoint carriers. Fifty-seven pairs reference at least one endpoint with no canonical carrier.

### Qualifier closure is missing

Every current Relation Kind names required qualifier axes, producing 33 distinct qualifier names. The repository does not yet provide:

- a closed JSON Schema for each Relation Kind's qualifiers;
- allowed qualifier values per exact ordered endpoint pair;
- cross-qualifier constraints;
- rules for qualifier evolution and succession;
- a canonical relation-instance carrier;
- lifecycle resolution through admission, succession, and activation overlays.

The current no-collapse receipt proves identifier separation and hand-authored hostile examples. It does not prove semantic orthogonality or qualifier closure.

### Thirteen extensions already identified by the master model

1. `addresses-intent`
2. `acts-for`
3. `has-capability`
4. `performs`
5. `uses-tool`
6. `produces`
7. `applies-lesson`
8. `subclass-of`, conditional on a hierarchical Classification Scheme
9. `occurs-during`
10. `violates`
11. `affects`
12. `responds-to`
13. `controls`

Each needs one unique question, exact ordered pairs, qualifiers, forbidden inferences, lifecycle rules, and carrier checks under the Typed Connection Extension Rule.

### Six additional missing connections or scope decisions

| Candidate connection | Why it is still needed |
| --- | --- |
| `challenges` or equivalent: Challenge Event -> challenged subject | The model records a challenge and later Decision but does not carry the exact subject being challenged |
| `addresses-improvement-target`: Research Inquiry -> Improvement Target | `addresses-intent` answers a different question; operational improvement routing needs its own target semantics |
| `tests-hypothesis`: Experiment Design -> Hypothesis | `evaluates` and `realizes` do not state the controlled proposition being tested |
| `consumes-view`: Agent Session -> Context View or Ontology View | Request fulfillment does not establish which immutable Views a Session actually consumed |
| Agent Instance -> Agent Profile binding | Decide whether this is `conforms-to`, a specialized profile binding, or a new axis; profile use cannot be inferred from classification |
| `represents`: Ontology Node -> governed subject | Declare this ontology-local or admit a global axis; it cannot collapse into identity assertion |

The first four are absent semantic connections. The final two require an explicit scope decision before relation admission.

### Existing axes require new endpoint pairs

At minimum, the following pair families must be reviewed as successors to existing Relation Kinds:

| Existing Relation Kind | Missing pair families |
| --- | --- |
| `declares-effect-on` | Decision -> Intent, Operational Lesson, Classification Assignment, Failure family, Implementation, and target-specific promotion candidate |
| `governed-by` | Agent Profile/Instance/Session/Action, Schemes, Assignments, lessons, failure records, Ontology subjects, and challengeable semantic carriers -> Policy or Constitution |
| `assigned-to` | Agent Instance -> Role, Responsibility, or Agent Assignment under exact assignment semantics |
| `member-of` | Agent Assignment -> Project; Failure Occurrence -> Incident; governed node/edge records -> Ontology where membership is truly structural |
| `derives-from` | Reflections, lessons, outcome assessments, Improvement Targets, feedback, drift, and failure assessments -> exact evidence-bearing sources |
| `evaluates` | Lesson Outcome Assessment -> Lesson Application; Failure Assessment -> Failure Occurrence; Preference Application Assessment -> exact preference application |
| `evidence-bears-on` | Evidence -> occurrence, mode assignment, causal hypothesis, recovery claim, lesson claim, preference assessment, drift claim, or satisfaction proposition |
| `instance-of` | Classification-backed semantic class projections, including Failure Occurrence -> Failure Mode when an exact Classification Assignment exists |
| `successor-of` | Every new versioned Definition, Artifact Type, Scheme, Assignment, Profile, lesson, failure record, Policy, and relation contract |

### Current relation inconsistencies

1. `product-capability -> product` appears under both `member-of` and `instance-of`; Product membership is supported, while classification needs separate evidence or removal.
2. The `method` endpoint resolves to Method Binding even though Method and Method Binding have different identities and responsibilities.
3. Identity Graph and Context Map own admitted relation vocabularies but have no declared mappings into the 23-axis model.
4. Specialized bindings do not yet declare `projects-as` or `represented-by`; dual writable relation truth remains possible.
5. The Ontology schema still uses string references and cannot enforce exact Relation Kind versions, endpoint kinds, qualifiers, global/local scope, or canonical Typed Relation identity.
6. Contestability vocabularies differ across Policy, profile, and runtime contracts.
7. Intent remains disconnected from the candidate relation graph even though its Artifact Type is admitted-current.

## Required admission dependency order

1. Review and admit the Typed Connection Extension Rule.
2. Materialize and review the 60 missing Definition identities, beginning with Relation Kind, Typed Relation, Intent Resolution, Implementation, Agent/state, Classification, failure, learning, Policy, Decision, and challenge semantics.
3. Resolve the five broader-Definition specialization bindings and the Ledger, Withdrawal Record, workflow-overlap, and Project Identity questions.
4. Generate the Artifact Type effective-state registry.
5. Materialize Relation Kind and Typed Relation carriers.
6. Add qualifier schemas and pair-specific qualifier constraints to the 23 existing axes.
7. Resolve the 22 carrierless endpoints and the disconnected Intent endpoint.
8. Review the 13 known extension axes and the six additional connection/scope gaps found here.
9. Materialize the missing Agent, state, operational experience, Classification, failure, learning, Intent Resolution, Implementation, Decision, Policy, Evidence Set, and Tool carriers.
10. Revise Ontology, Ontology Package, Challenge Contract, Context adapters, and runtime bindings around one canonical relation model.
11. Rebuild the remaining-18 candidates against that foundation.
12. Admit representative end-to-end instances only after Definition, carrier, pair, qualifier, authority, evidence, challenge, and lifecycle closure passes.

## Recommended review decision

Accept this document as the gap register for the integrated Lab model. Use it to create one materialization queue with separate Definition, Artifact Type, and Relation Kind subpackages. Keep each subpackage candidate-only until the full dependency chain is reviewable and digest-bound.
