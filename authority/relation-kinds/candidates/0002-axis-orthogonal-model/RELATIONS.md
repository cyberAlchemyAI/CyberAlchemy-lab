<!-- GENERATED FILE: canonical data is model.json and examples.json. -->

# Axis-orthogonal Relation Kind model

The initial 42-kind candidate failed semantic compression review. This successor normalizes all 42 prior relation names into 23 independently valued relation axes plus explicit qualifier axes.

**Resulting model:** 23 relation axes; 19 duplicate kinds collapsed; 42 prior names normalized; 147 exact endpoint pairs; zero wildcards.

## Axis rule

A change on one axis does not imply a change on another axis unless an explicit typed coupling, schema rule, gate, validator, or owner decision declares that bridge.

## Endpoint closure rule

Only exact ordered source_kind -> target_kind pairs declared by a Relation Kind are permitted. Wildcards and inference from separate source/target lists are forbidden. Every new connection requires an explicit candidate pair, owner review, evidence, and validation before admission.

Definition dependency: `cal.definition.typed-connection-extension-rule@1.0.0-candidate.1` (`candidate-unadmitted`; required before Relation Kind admission).

The noun names the independent semantic axis, while the Relation Kind is a directed predicate. For example, `axis.membership` is represented by `relation.member-of`.

## All relation axes

| # | Semantic axis | Directed Relation Kind | Unique question | Required qualifier axes | Absorbed previous kinds | Forbidden inference examples |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `axis.membership` | `relation.member-of` | Which governed container or scope is this member part of? | `membership_role` | `relation.belongs-to-product`, `relation.belongs-to-project`, `relation.contains`, `relation.defines-responsibility`, `relation.member-of` | `contribution`, `assignment`, `authority`, `identity-equivalence` |
| 2 | `axis.contribution` | `relation.contributes-to` | Which Product or Goal is this activity intended to advance? | `contribution_role`, `contribution_scope` | `relation.advances-goal`, `relation.contributes-to-product` | `membership`, `realization`, `evaluation-result`, `product-value` |
| 3 | `axis.method-dependency` | `relation.uses-method` | Which Method does this subject depend on or employ? | `usage_role` | `relation.uses-method` | `conformance`, `realization`, `validation`, `achievement` |
| 4 | `axis.evaluation` | `relation.evaluates` | Which subject or proposition is being assessed? | `evaluation_role`, `evaluation_purpose` | `relation.evaluates`, `relation.tests-thesis-proposition` | `support`, `contradiction`, `adoption`, `realization`, `product-value` |
| 5 | `axis.realization` | `relation.realizes` | Which declared design or capability is concretely instantiated by this subject? | `realization_role`, `exact_target_version_ref` | `relation.executes-design`, `relation.realizes` | `conformance`, `effectiveness`, `adoption`, `support` |
| 6 | `axis.inquiry-engagement` | `relation.engages-inquiry` | How does this research carrier engage a Research Inquiry? | `inquiry_role` | `relation.addresses-inquiry`, `relation.answers-inquiry` | `finding-acceptance`, `evidence-support`, `inquiry-completion` |
| 7 | `axis.origin-lineage` | `relation.originates-from` | From which source did this identity or content originate? | `origin_role` | `relation.originates-from` | `derivation`, `successor`, `authority-transfer` |
| 8 | `axis.derivation` | `relation.derives-from` | From which material or governed source was this artifact derived? | `derivation_role` | `relation.compiles-to`, `relation.derives-from`, `relation.projects-context` | `identity-equality`, `source-authority-transfer`, `admission` |
| 9 | `axis.evidence-polarity` | `relation.evidence-bears-on` | What evidential polarity does this evidence have toward this claim? | `polarity` | `relation.contradicts`, `relation.supports` | `claim-acceptance`, `decision`, `admission`, `truth` |
| 10 | `axis.governance-applicability` | `relation.governed-by` | Which Policy or Constitution governs this subject? | `governance_role` | `relation.governed-by` | `conformance`, `authorization`, `admission` |
| 11 | `axis.decision-effect` | `relation.declares-effect-on` | Which exact governance effect does this Decision declare? | `effect_kind`, `exact_target_version_ref` | `relation.admits`, `relation.adopts`, `relation.authorizes` | `effect-execution`, `cross-effect-inference`, `runtime-success` |
| 12 | `axis.classification` | `relation.instance-of` | Under which exact parent model is this subject classified? | `parent_version_ref`, `binding_ref` | `relation.instance-of` | `conformance`, `realization`, `ownership-transfer` |
| 13 | `axis.implementation-binding` | `relation.binds-implementation` | Which Ontology or Schema does this implementation bind? | `binding_role` | `relation.binds-implementation` | `conformance`, `runtime-effectiveness`, `admission` |
| 14 | `axis.conformance` | `relation.conforms-to` | Which exact contract does this subject demonstrably conform to, and under which evidence? | `conformance_scope`, `exact_version_ref`, `conformance_evidence_refs` | `relation.conforms-to` | `admission`, `runtime-conformance`, `effectiveness`, `authority` |
| 15 | `axis.contract-inheritance` | `relation.inherits-contract` | Which exact contract obligations are inherited by this instance? | `binding_ref`, `contract_version_ref` | `relation.inherits-contract` | `ownership-transfer`, `conformance`, `adoption` |
| 16 | `axis.context-framing` | `relation.frames` | Which subject does this Context frame for relevance and interpretation? | `framing_role` | `relation.frames`, `relation.references-bounded-context` | `source-authority`, `currentness`, `truth` |
| 17 | `axis.context-resolution-request` | `relation.requests-resolution-of` | Which exact Context version does this Context Request ask to resolve? | `context_version_ref` | `relation.requests-resolution-of` | `resolution`, `context-mutation`, `source-authority` |
| 18 | `axis.request-fulfillment` | `relation.fulfills-request` | Which request is this immutable output intended to fulfill? | `fulfillment_role` | `relation.fulfills-request` | `currentness`, `source-authority`, `context-mutation` |
| 19 | `axis.lifecycle-succession` | `relation.successor-of` | Which predecessor does this successor continue or replace? | `succession_effect` | `relation.successor-of`, `relation.supersedes` | `automatic-supersession`, `identity-equality`, `authority-transfer` |
| 20 | `axis.assignment` | `relation.assigned-to` | Which Role or Responsibility is explicitly assigned to this assignee? | `assignment_kind`, `relation_record_ref` | `relation.assigned-responsibility`, `relation.assigned-role` | `team-membership`, `authority`, `permission`, `identity` |
| 21 | `axis.identity-assertion` | `relation.asserts-identity-of` | What bounded identity correspondence is being asserted between these endpoints? | `assertion_kind`, `claim_scope` | `relation.claims-identifier-for`, `relation.identity-link`, `relation.represents-person` | `identity-merge`, `authority-transfer`, `private-attribute-inference` |
| 22 | `axis.authority-scope` | `relation.scopes-authority-over` | What object or assignment is bounded by this explicit Authority Claim? | `authority_role`, `scope_ref` | `relation.bounded-by-authority-claim`, `relation.claims-authority-over` | `permission-grant`, `claim-authentication`, `effect-execution` |
| 23 | `axis.semantic-contract` | `relation.carries-definition` | Which exact Definition version supplies this Artifact Type's governed meaning? | `definition_version_ref`, `definition_sha256` | `relation.carries-definition` | `admission`, `authority-transfer`, `endpoint-identity-collapse` |

## Exact 42-to-23 normalization

| Previous relation kind | Axis relation kind | Fixed qualifier values |
| --- | --- | --- |
| `relation.addresses-inquiry` | `relation.engages-inquiry` | `{"inquiry_role": "addresses"}` |
| `relation.admits` | `relation.declares-effect-on` | `{"effect_kind": "admits"}` |
| `relation.adopts` | `relation.declares-effect-on` | `{"effect_kind": "adopts"}` |
| `relation.advances-goal` | `relation.contributes-to` | `{"contribution_role": "advance-goal"}` |
| `relation.answers-inquiry` | `relation.engages-inquiry` | `{"inquiry_role": "answers"}` |
| `relation.assigned-responsibility` | `relation.assigned-to` | `{"assignment_kind": "responsibility"}` |
| `relation.assigned-role` | `relation.assigned-to` | `{"assignment_kind": "role"}` |
| `relation.authorizes` | `relation.declares-effect-on` | `{"effect_kind": "authorizes"}` |
| `relation.belongs-to-product` | `relation.member-of` | `{"membership_role": "product-anchor"}` |
| `relation.belongs-to-project` | `relation.member-of` | `{"membership_role": "project-scope"}` |
| `relation.binds-implementation` | `relation.binds-implementation` | `{}` |
| `relation.bounded-by-authority-claim` | `relation.scopes-authority-over` | `{"authority_role": "bounds-assignment", "direction_normalized": "authority-claim-to-assignment"}` |
| `relation.carries-definition` | `relation.carries-definition` | `{}` |
| `relation.claims-authority-over` | `relation.scopes-authority-over` | `{"authority_role": "claims-over"}` |
| `relation.claims-identifier-for` | `relation.asserts-identity-of` | `{"assertion_kind": "claims-identifier"}` |
| `relation.compiles-to` | `relation.derives-from` | `{"derivation_role": "compiled-output", "direction_normalized": "output-to-source"}` |
| `relation.conforms-to` | `relation.conforms-to` | `{}` |
| `relation.contains` | `relation.member-of` | `{"direction_normalized": "member-to-container", "membership_role": "composition"}` |
| `relation.contradicts` | `relation.evidence-bears-on` | `{"polarity": "contradicts"}` |
| `relation.contributes-to-product` | `relation.contributes-to` | `{"contribution_role": "advance-product"}` |
| `relation.defines-responsibility` | `relation.member-of` | `{"direction_normalized": "responsibility-to-role", "membership_role": "role-contract"}` |
| `relation.derives-from` | `relation.derives-from` | `{"derivation_role": "derived-artifact"}` |
| `relation.evaluates` | `relation.evaluates` | `{"evaluation_role": "assess-subject"}` |
| `relation.executes-design` | `relation.realizes` | `{"realization_role": "design-execution"}` |
| `relation.frames` | `relation.frames` | `{"framing_role": "subject-framing"}` |
| `relation.fulfills-request` | `relation.fulfills-request` | `{}` |
| `relation.governed-by` | `relation.governed-by` | `{}` |
| `relation.identity-link` | `relation.asserts-identity-of` | `{"assertion_kind": "identity-link"}` |
| `relation.inherits-contract` | `relation.inherits-contract` | `{}` |
| `relation.instance-of` | `relation.instance-of` | `{}` |
| `relation.member-of` | `relation.member-of` | `{"membership_role": "team-membership"}` |
| `relation.originates-from` | `relation.originates-from` | `{}` |
| `relation.projects-context` | `relation.derives-from` | `{"derivation_role": "context-projection"}` |
| `relation.realizes` | `relation.realizes` | `{"realization_role": "capability-realization"}` |
| `relation.references-bounded-context` | `relation.frames` | `{"framing_role": "bounded-context-reference"}` |
| `relation.represents-person` | `relation.asserts-identity-of` | `{"assertion_kind": "represents-person"}` |
| `relation.requests-resolution-of` | `relation.requests-resolution-of` | `{}` |
| `relation.successor-of` | `relation.successor-of` | `{"succession_effect": "continues"}` |
| `relation.supersedes` | `relation.successor-of` | `{"succession_effect": "supersedes"}` |
| `relation.supports` | `relation.evidence-bears-on` | `{"polarity": "supports"}` |
| `relation.tests-thesis-proposition` | `relation.evaluates` | `{"evaluation_role": "test-thesis-proposition"}` |
| `relation.uses-method` | `relation.uses-method` | `{}` |

## Realistic examples

### 1. `relation.member-of`

Records scoped membership or composition in member-to-container direction without transferring identity or authority.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:member-of"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "membership_role": "project-scope"
  },
  "relation_id": "example:relation.member-of",
  "relation_kind_ref": "relation.member-of",
  "source_ref": "experiment-run:definition-normalization-residue:2026-10-05",
  "target_ref": "project:lab-semantic-governance"
}
```

### 2. `relation.contributes-to`

Records intended contribution without proving success, realization, or value.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:contributes-to"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "contribution_role": "advance-product",
    "contribution_scope": "Governed semantic foundations"
  },
  "relation_id": "example:relation.contributes-to",
  "relation_kind_ref": "relation.contributes-to",
  "source_ref": "project:lab-semantic-governance",
  "target_ref": "CA2-PRODUCT-CRAFT"
}
```

### 3. `relation.uses-method`

Records Method dependency without implying conformance, realization, or success.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:uses-method"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "usage_role": "measurement"
  },
  "relation_id": "example:relation.uses-method",
  "relation_kind_ref": "relation.uses-method",
  "source_ref": "measurement-result:definition-normalization-residue-entropy:2026-10-05",
  "target_ref": "measurement-method:definition-normalization-residue-entropy"
}
```

### 4. `relation.evaluates`

Records evaluation scope without deciding evidence polarity, adoption, realization, or value.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:evaluates"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "evaluation_purpose": "Test one bounded outcome proposition",
    "evaluation_role": "test-thesis-proposition"
  },
  "relation_id": "example:relation.evaluates",
  "relation_kind_ref": "relation.evaluates",
  "source_ref": "experiment-design:definition-normalization-residue",
  "target_ref": "product-thesis:craft#outcome-authoritative-state"
}
```

### 5. `relation.realizes`

Records realization or execution without implying conformance, effectiveness, adoption, or evidence acceptance.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:realizes"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "exact_target_version_ref": "experiment-design:definition-normalization-residue@1.0.0-candidate.1",
    "realization_role": "design-execution"
  },
  "relation_id": "example:relation.realizes",
  "relation_kind_ref": "relation.realizes",
  "source_ref": "experiment-run:definition-normalization-residue:2026-10-05",
  "target_ref": "experiment-design:definition-normalization-residue"
}
```

### 6. `relation.engages-inquiry`

Records whether an activity addresses or a Finding answers an Inquiry without converting either into the other.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:engages-inquiry"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "inquiry_role": "answers"
  },
  "relation_id": "example:relation.engages-inquiry",
  "relation_kind_ref": "relation.engages-inquiry",
  "source_ref": "finding:normalization-residue-lowered",
  "target_ref": "research-inquiry:definition-normalization-residue"
}
```

### 7. `relation.originates-from`

Records origin lineage without asserting transformation, succession, or authority transfer.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:originates-from"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "origin_role": "content-source"
  },
  "relation_id": "example:relation.originates-from",
  "relation_kind_ref": "relation.originates-from",
  "source_ref": "finding:research-inquiry-v1-contract-gap",
  "target_ref": "source:cyberalchemy-v2-definitions"
}
```

### 8. `relation.derives-from`

Records derivation, compilation, or projection while preserving source and derived identities.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:derives-from"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "derivation_role": "context-projection"
  },
  "relation_id": "example:relation.derives-from",
  "relation_kind_ref": "relation.derives-from",
  "source_ref": "context-view:remaining-18-review:2026-10-05",
  "target_ref": "context:lab-artifact-type-admission"
}
```

### 9. `relation.evidence-bears-on`

Records supporting or contradicting evidence without accepting, rejecting, or deciding the claim.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:evidence-bears-on"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "polarity": "supports"
  },
  "relation_id": "example:relation.evidence-bears-on",
  "relation_kind_ref": "relation.evidence-bears-on",
  "source_ref": "evidence-set:definition-normalization-residue-run-2026-10-05",
  "target_ref": "finding:normalization-residue-lowered"
}
```

### 10. `relation.governed-by`

Records applicable governance without proving compliance or authorization.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:governed-by"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "governance_role": "source-selection"
  },
  "relation_id": "example:relation.governed-by",
  "relation_kind_ref": "relation.governed-by",
  "source_ref": "context:lab-artifact-type-admission",
  "target_ref": "policy:admitted-authority-first"
}
```

### 11. `relation.declares-effect-on`

Records admission, adoption, or authorization as separate effect values and executes none of them.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:declares-effect-on"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "effect_kind": "admits",
    "exact_target_version_ref": "cal.artifact-type.experiment-run/v1@1.0.0-candidate.2"
  },
  "relation_id": "example:relation.declares-effect-on",
  "relation_kind_ref": "relation.declares-effect-on",
  "source_ref": "decision:artifact-type-batch-admission",
  "target_ref": "cal.artifact-type.experiment-run/v1"
}
```

### 12. `relation.instance-of`

Records classification without implying conformance, ownership transfer, or realization.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:instance-of"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "binding_ref": "model-instance-binding:artifact-type-reviewer",
    "parent_version_ref": "product-capability:governed-definition-admission@1.0.0-candidate.1"
  },
  "relation_id": "example:relation.instance-of",
  "relation_kind_ref": "relation.instance-of",
  "source_ref": "capability-instance:lab-artifact-type-reviewer",
  "target_ref": "product-capability:governed-definition-admission"
}
```

### 13. `relation.binds-implementation`

Records an implementation-model binding without proving conformance or runtime behavior.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:binds-implementation"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "binding_role": "implements-ontology"
  },
  "relation_id": "example:relation.binds-implementation",
  "relation_kind_ref": "relation.binds-implementation",
  "source_ref": "implementation:definition-validator",
  "target_ref": "ontology:artifact-governance"
}
```

### 14. `relation.conforms-to`

Records scoped conformance only; it does not imply admission, implementation conformance outside scope, or runtime conformance.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:conforms-to"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "conformance_evidence_refs": [
      "receipt:remaining-18-model-validation"
    ],
    "conformance_scope": "context-contract",
    "exact_version_ref": "context-profile:governed-review@1.0.0-candidate.2"
  },
  "relation_id": "example:relation.conforms-to",
  "relation_kind_ref": "relation.conforms-to",
  "source_ref": "context:lab-artifact-type-admission",
  "target_ref": "context-profile:governed-review"
}
```

### 15. `relation.inherits-contract`

Records inherited obligations without transferring parent ownership or proving conformance.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:inherits-contract"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "binding_ref": "model-instance-binding:artifact-type-reviewer",
    "contract_version_ref": "contract:definition-admission-boundaries/v1"
  },
  "relation_id": "example:relation.inherits-contract",
  "relation_kind_ref": "relation.inherits-contract",
  "source_ref": "capability-instance:lab-artifact-type-reviewer",
  "target_ref": "contract:definition-admission-boundaries/v1"
}
```

### 16. `relation.frames`

Records Context framing, including Bounded Context reference, without making the framed subject authoritative or current.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:frames"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "framing_role": "bounded-context-reference"
  },
  "relation_id": "example:relation.frames",
  "relation_kind_ref": "relation.frames",
  "source_ref": "context:lab-artifact-type-admission",
  "target_ref": "bounded-context:semantic-governance"
}
```

### 17. `relation.requests-resolution-of`

Records a resolution request without performing resolution or mutating Context.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:requests-resolution-of"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "context_version_ref": "context:lab-artifact-type-admission@1.0.0-candidate.2"
  },
  "relation_id": "example:relation.requests-resolution-of",
  "relation_kind_ref": "relation.requests-resolution-of",
  "source_ref": "context-request:remaining-18-review",
  "target_ref": "context:lab-artifact-type-admission"
}
```

### 18. `relation.fulfills-request`

Records request fulfillment without implying that included sources or Context remain current.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:fulfills-request"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "fulfillment_role": "immutable-view"
  },
  "relation_id": "example:relation.fulfills-request",
  "relation_kind_ref": "relation.fulfills-request",
  "source_ref": "context-view:remaining-18-review:2026-10-05",
  "target_ref": "context-request:remaining-18-review"
}
```

### 19. `relation.successor-of`

Records succession; replacement occurs only when succession_effect is supersedes.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:successor-of"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "succession_effect": "supersedes"
  },
  "relation_id": "example:relation.successor-of",
  "relation_kind_ref": "relation.successor-of",
  "source_ref": "artifact-type:product-identity@2",
  "target_ref": "artifact-type:product-identity@1"
}
```

### 20. `relation.assigned-to`

Records an assignment through its lifecycle-bearing record without implying Team membership or authority.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:assigned-to"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "assignment_kind": "role",
    "relation_record_ref": "role-assignment:reviewer:artifact-type-reviewer"
  },
  "relation_id": "example:relation.assigned-to",
  "relation_kind_ref": "relation.assigned-to",
  "source_ref": "person-reference:repository-reviewer",
  "target_ref": "role:artifact-type-reviewer"
}
```

### 21. `relation.asserts-identity-of`

Records representation, identity linking, or identifier claims without merging identities or authority.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:asserts-identity-of"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "assertion_kind": "claims-identifier",
    "claim_scope": "CyberAlchemy Lab review attribution"
  },
  "relation_id": "example:relation.asserts-identity-of",
  "relation_kind_ref": "relation.asserts-identity-of",
  "source_ref": "identity-claim:repository-reviewer:workspace-handle",
  "target_ref": "person-reference:repository-reviewer"
}
```

### 22. `relation.scopes-authority-over`

Records claimed or bounding authority without granting permission or authenticating the claim.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:scopes-authority-over"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "authority_role": "bounds-assignment",
    "scope_ref": "scope:artifact-type-admission-recommendation"
  },
  "relation_id": "example:relation.scopes-authority-over",
  "relation_kind_ref": "relation.scopes-authority-over",
  "source_ref": "authority-claim:may-recommend-artifact-type-admission",
  "target_ref": "role-assignment:reviewer:artifact-type-reviewer"
}
```

### 23. `relation.carries-definition`

Records the semantic contract without admitting either endpoint or transferring Definition authority.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:carries-definition"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "definition_sha256": "digest-bound-at-instance-time",
    "definition_version_ref": "cal.definition.experiment@1.0.0-candidate.1"
  },
  "relation_id": "example:relation.carries-definition",
  "relation_kind_ref": "relation.carries-definition",
  "source_ref": "cal.artifact-type.experiment-run/v1",
  "target_ref": "cal.definition.experiment@1.0.0-candidate.1"
}
```

## Claim ceiling

This candidate compresses the previous 42 relation names into independently valued typed coupling axes, preserves their semantic distinctions as qualifier values, and closes use to explicitly declared ordered endpoint pairs. It does not admit Relation Kinds, permit undeclared endpoint connections, merge endpoints, grant authority, accept evidence, execute decisions, or establish runtime conformance.
