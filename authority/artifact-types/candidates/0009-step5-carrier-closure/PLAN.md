<!-- GENERATED FILE: canonical data is plan.json. -->

# Step 5 — Artifact Type carrier closure

- Status: `candidate-complete-awaiting-owner-review`
- Authority effect: `none`
- Existing contract actions: `14` (`9` successors + `5` candidate revisions)
- New endpoint carriers: `22`
- Total work items: `36`

## Execution order

1. **repair-positive-semantic-bindings** — Revise the five unadmitted candidates so exact positive Definitions and provenance are current.
2. **author-current-contract-successors** — Author nine immutable successors; never rewrite admitted predecessor contracts.
3. **materialize-missing-endpoint-carriers** — Materialize 22 distinct candidate carriers from their admitted Definitions and exact relation endpoint roles.
4. **hostile-non-collapse** — Reject every listed neighboring concept substitution and every undeclared relation endpoint pair.
5. **refresh-derived-surfaces** — Generate a successor effective-state registry and endpoint inventory; require 50 of 50 endpoint kinds to resolve to carriers and zero referenced-no-canonical-carrier entries.
6. **owner-review** — Show all exact postimages and examples before any admission; admit only exact reviewed bytes in a later decision.

## Existing contract actions

| Current ref | Action | Target ref | Findings |
| --- | --- | --- | --- |
| `cal.artifact-type.artifact-type/v2` | `author-immutable-successor` | `cal.artifact-type.artifact-type/v3` | `legacy-contract-sections-absent` |
| `cal.artifact-type.bounded-context/v2` | `author-immutable-successor` | `cal.artifact-type.bounded-context/v3` | `validation-evidence-not-pass, legacy-contract-sections-absent` |
| `cal.artifact-type.capability-instance/v1` | `author-immutable-successor` | `cal.artifact-type.capability-instance/v2` | `legacy-contract-sections-absent` |
| `cal.artifact-type.capability-realization-binding/v1` | `author-immutable-successor` | `cal.artifact-type.capability-realization-binding/v2` | `admitted-semantic-successor-required` |
| `cal.artifact-type.context-lineage-record/v1` | `author-immutable-successor` | `cal.artifact-type.context-lineage-record/v2` | `legacy-contract-sections-absent` |
| `cal.artifact-type.context-map/v2` | `author-immutable-successor` | `cal.artifact-type.context-map/v3` | `validation-evidence-not-pass, legacy-contract-sections-absent` |
| `cal.artifact-type.context-migration-manifest/v1` | `author-immutable-successor` | `cal.artifact-type.context-migration-manifest/v2` | `legacy-contract-sections-absent` |
| `cal.artifact-type.context-profile/v1` | `revise-unadmitted-candidate-in-place` | `cal.artifact-type.context-profile/v1` | `candidate-semantic-rebind-required` |
| `cal.artifact-type.definition/v1` | `author-immutable-successor` | `cal.artifact-type.definition/v2` | `legacy-contract-sections-absent` |
| `cal.artifact-type.measurement-method/v1` | `revise-unadmitted-candidate-in-place` | `cal.artifact-type.measurement-method/v1` | `candidate-semantic-rebind-required` |
| `cal.artifact-type.measurement-result/v1` | `revise-unadmitted-candidate-in-place` | `cal.artifact-type.measurement-result/v1` | `candidate-semantic-rebind-required` |
| `cal.artifact-type.model-instance-binding/v1` | `revise-unadmitted-candidate-in-place` | `cal.artifact-type.model-instance-binding/v1` | `candidate-semantic-rebind-required` |
| `cal.artifact-type.ontology-package/v1` | `revise-unadmitted-candidate-in-place` | `cal.artifact-type.ontology-package/v1` | `definition-reference-not-admitted, definition-binding-material-not-current` |
| `cal.artifact-type.ubiquitous-language/v1` | `author-immutable-successor` | `cal.artifact-type.ubiquitous-language/v2` | `legacy-contract-sections-absent` |

## Missing endpoint carriers

| Endpoint kind | Candidate Artifact Type | Definition | Must remain distinct from |
| --- | --- | --- | --- |
| `authority-claim` | `cal.artifact-type.authority-claim/v1` | `cal.definition.authority-claim@1.0.0-candidate.1` | `identity-claim, role-assignment` |
| `constitution` | `cal.artifact-type.constitution/v1` | `cal.definition.constitution@1.0.0-candidate.1` | `policy, contract` |
| `contract` | `cal.artifact-type.contract/v1` | `cal.definition.contract@1.0.0-candidate.1` | `challenge-contract, policy` |
| `decision` | `cal.artifact-type.decision/v1` | `cal.definition.decision@1.0.0-candidate.1` | `decision-checkpoint, effect` |
| `decision-scope` | `cal.artifact-type.decision-scope/v1` | `cal.definition.decision-scope@1.0.0-candidate.1` | `decision, authority-claim` |
| `effect` | `cal.artifact-type.effect/v1` | `cal.definition.effect@1.0.0-candidate.1` | `decision, execution` |
| `evaluation` | `cal.artifact-type.evaluation/v1` | `cal.definition.evaluation@1.0.0-candidate.1` | `measurement-result, review` |
| `evidence-set` | `cal.artifact-type.evidence-set/v1` | `cal.definition.evidence-set@1.0.0-candidate.1` | `finding, observation` |
| `generated-output` | `cal.artifact-type.generated-output/v1` | `cal.definition.generated-output@1.0.0-candidate.1` | `source, evidence-set` |
| `governed-model` | `cal.artifact-type.governed-model/v1` | `cal.definition.governed-model@1.0.0-candidate.1` | `ontology, schema` |
| `hypothesis` | `cal.artifact-type.hypothesis/v1` | `cal.definition.hypothesis@1.0.0-candidate.1` | `product-thesis, premise` |
| `implementation` | `cal.artifact-type.implementation/v1` | `cal.definition.implementation@1.0.0-candidate.1` | `capability-realization-binding, schema` |
| `ontology-node` | `cal.artifact-type.ontology-node/v1` | `cal.definition.ontology-node@1.0.0-candidate.1` | `ontology, typed-relation` |
| `person` | `cal.artifact-type.person/v1` | `cal.definition.person@1.0.0-candidate.1` | `person-reference, agent` |
| `policy` | `cal.artifact-type.policy/v1` | `cal.definition.policy@1.0.0-candidate.1` | `constitution, contract` |
| `relation-kind` | `cal.artifact-type.relation-kind/v1` | `cal.definition.relation-kind@1.0.0-candidate.1` | `typed-relation, schema` |
| `responsibility` | `cal.artifact-type.responsibility/v1` | `cal.definition.responsibility@1.0.0-candidate.1` | `role, role-assignment` |
| `review` | `cal.artifact-type.review/v1` | `cal.definition.review@1.0.0-candidate.1` | `evaluation, finding` |
| `schema` | `cal.artifact-type.schema/v1` | `cal.definition.schema@1.0.0-candidate.1` | `artifact-type, contract` |
| `source` | `cal.artifact-type.source/v1` | `cal.definition.source@1.0.0-candidate.1` | `evidence-set, generated-output` |
| `typed-relation` | `cal.artifact-type.typed-relation/v1` | `cal.definition.typed-relation@1.0.0-candidate.1` | `relation-kind, ontology-node` |
| `work` | `cal.artifact-type.work/v1` | `cal.definition.work@1.0.0-candidate.1` | `project, goal` |

## Realistic examples

### STEP5-EX-01-PERSON-REFERENCE

A durable Person Reference asserts identity of a Person; the reference record and the human being remain different carriers.

```json
{
  "authority_effect": "none",
  "lifecycle_state": "candidate-example",
  "relation_kind_ref": "relation.asserts-identity-of",
  "source_kind": "person-reference",
  "source_ref": "person-reference:vrondelli",
  "target_kind": "person",
  "target_ref": "person:vrondelli"
}
```

### STEP5-EX-02-IMPLEMENTATION

One executable implementation realizes a Product Capability; the Capability Realization Binding separately records the governed connection and evidence posture.

```json
{
  "authority_effect": "none",
  "lifecycle_state": "candidate-example",
  "relation_kind_ref": "relation.realizes",
  "source_kind": "implementation",
  "source_ref": "implementation:registry-validator@beb873",
  "target_kind": "product-capability",
  "target_ref": "product-capability:effective-state-resolution"
}
```

### STEP5-EX-03-HYPOTHESIS-EVIDENCE

An Evidence Set bears on one falsifiable Hypothesis without becoming the Hypothesis or deciding its truth.

```json
{
  "authority_effect": "none",
  "lifecycle_state": "candidate-example",
  "relation_kind_ref": "relation.evidence-bears-on",
  "source_kind": "evidence-set",
  "source_ref": "evidence-set:registry-determinism",
  "target_kind": "hypothesis",
  "target_ref": "hypothesis:registry-build-is-deterministic"
}
```

### STEP5-EX-04-DECISION-EFFECT

A Decision declares an Effect on a Relation Kind; the declaration and the effect remain explicit endpoints.

```json
{
  "authority_effect": "none",
  "lifecycle_state": "candidate-example",
  "relation_kind_ref": "relation.declares-effect-on",
  "source_kind": "decision",
  "source_ref": "decision:relation-kind-admission",
  "target_kind": "relation-kind",
  "target_ref": "relation-kind:member-of"
}
```

### STEP5-EX-05-ONTOLOGY-MEMBERSHIP

A Typed Relation is a member of an Ontology, while its Relation Kind remains the reusable predicate contract.

```json
{
  "authority_effect": "none",
  "lifecycle_state": "candidate-example",
  "relation_kind_ref": "relation.member-of",
  "source_kind": "typed-relation",
  "source_ref": "typed-relation:implementation-realizes-capability:001",
  "target_kind": "ontology",
  "target_ref": "ontology:lab-integrated-model"
}
```

### STEP5-EX-06-WORK-PROJECT

A bounded Work record is a member of a Project; the Project coordinates many Work records and persists beyond any one of them.

```json
{
  "authority_effect": "none",
  "lifecycle_state": "candidate-example",
  "relation_kind_ref": "relation.member-of",
  "source_kind": "work",
  "source_ref": "work:materialize-carrier-closure",
  "target_kind": "project",
  "target_ref": "project:lab-semantic-governance"
}
```

## Completion gates

- All 14 actionable existing contracts have PASS postimages or explicit preserved predecessor dispositions.
- All 22 missing endpoint kinds have distinct schema-valid candidate carriers bound to current admitted Definitions.
- Every candidate carrier rejects authority escalation, unknown fields, missing required fields, neighboring-concept substitution, and undeclared endpoint roles.
- The successor registry reports zero semantic rebind obligations for promotable candidates and exact immutable lineage for all admitted predecessors.
- The relation endpoint inventory reports 50 named endpoint kinds, 50 canonical carriers, zero missing carriers, 147 unchanged explicit endpoint pairs, and zero wildcards.
- No Artifact Type, Relation Kind, Typed Relation instance, consumer, or runtime changes state until a later exact owner decision.

## Claim ceiling

This candidate is an execution plan for Artifact Type carrier closure. It does not revise, create, admit, supersede, or activate any Artifact Type, relation, instance, consumer, or runtime.
