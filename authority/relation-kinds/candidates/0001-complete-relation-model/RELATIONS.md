<!-- GENERATED FILE: canonical data is model.json and examples.json. -->

# Complete revised Relation Kind model

This candidate presents every normalized Relation Kind needed by the current repository model. Nothing in this candidate is admitted.

**Total:** 42 = 20 preserved + 5 revised + 17 new.

## All relations

| # | Group | Relation | State | Source kinds | Target kinds | Meaning | Required qualifiers |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | context | `relation.frames` | `migration-contract-preserved` | `context` | `*` | Links a Context to the subject whose relevance and interpretation it frames. | none |
| 2 | context | `relation.fulfills-request` | `candidate-new` | `context-view` | `context-request` | Links an immutable Context View to the Context Request it fulfills. | none |
| 3 | context | `relation.projects-context` | `candidate-new` | `context-view` | `context` | Links an immutable Context View to the exact Context version it projects. | `context_version_ref`, `source_epoch` |
| 4 | context | `relation.references-bounded-context` | `migration-contract-preserved` | `context` | `bounded-context` | Links a purpose-specific Context to a DDD Bounded Context it references. | none |
| 5 | context | `relation.requests-resolution-of` | `candidate-new` | `context-request` | `context` | Links a Context Request to the exact Context version it asks to resolve. | `context_version_ref` |
| 6 | governance-and-authority | `relation.adopts` | `migration-contract-preserved` | `decision` | `*` | Links a Decision to a version or model it adopts for use in scope. | none |
| 7 | governance-and-authority | `relation.authorizes` | `migration-contract-preserved` | `decision` | `effect` | Links a Decision to the exact effect it authorizes; the edge does not execute the effect. | none |
| 8 | governance-and-authority | `relation.governed-by` | `migration-contract-preserved` | `*` | `policy`, `constitution` | Links a subject to the Policy or Constitution that governs it. | none |
| 9 | implementation-and-model | `relation.binds-implementation` | `migration-contract-preserved` | `implementation` | `ontology`, `schema` | Links an implementation to the Ontology or Schema it implements. | none |
| 10 | implementation-and-model | `relation.compiles-to` | `migration-contract-preserved` | `*` | `generated-output` | Links authored source to a generated output derived from it. | none |
| 11 | implementation-and-model | `relation.conforms-to` | `candidate-new` | `context`, `capability-instance` | `context-profile`, `governed-model`, `contract` | Declares evidence-bounded conformance of a Context or capability instance to an exact Profile, parent model, or contract. | `exact_version_ref`, `conformance_evidence_refs` |
| 12 | implementation-and-model | `relation.inherits-contract` | `candidate-new` | `capability-instance` | `contract` | Links a capability instance to an exact inherited contract, qualified by its Model Instance Binding. | `binding_ref`, `contract_version_ref` |
| 13 | implementation-and-model | `relation.instance-of` | `candidate-revised` | `implementation`, `product-capability`, `capability-instance` | `product-capability`, `product`, `governed-model` | Classifies an implementation or capability instance under an exact parent model while keeping ownership and lifecycle separate. | `parent_version_ref`, `binding_ref` |
| 14 | implementation-and-model | `relation.realizes` | `migration-contract-preserved` | `implementation` | `product-capability` | Links an implementation to the Product Capability it realizes. | none |
| 15 | lineage-and-lifecycle | `relation.originates-from` | `migration-contract-preserved` | `*` | `source` | Links an artifact to the source from which its content or identity originated. | none |
| 16 | lineage-and-lifecycle | `relation.successor-of` | `migration-contract-preserved` | `*` | `*` | Links a successor version or identity to its immediate predecessor. | none |
| 17 | lineage-and-lifecycle | `relation.supersedes` | `migration-contract-preserved` | `*` | `*` | Declares that a newer governed artifact replaces an older artifact within a stated scope. | none |
| 18 | people-and-teams | `relation.assigned-responsibility` | `migration-contract-preserved` | `person-reference`, `team` | `responsibility` | Links a Person Reference or Team to an explicitly assigned Responsibility. | none |
| 19 | people-and-teams | `relation.assigned-role` | `migration-contract-preserved` | `person-reference`, `team` | `role` | Links a Person Reference or Team to a Role through an independently governed Role Assignment record. | none |
| 20 | people-and-teams | `relation.bounded-by-authority-claim` | `candidate-new` | `role-assignment` | `authority-claim` | Links a Role Assignment to the separate Authority Claim that bounds any authority exercised through the assignment. | none |
| 21 | people-and-teams | `relation.claims-authority-over` | `migration-contract-preserved` | `authority-claim` | `*` | Links an Authority Claim to the object and scope over which authority is asserted. | none |
| 22 | people-and-teams | `relation.claims-identifier-for` | `candidate-new` | `identity-claim` | `person-reference` | Links an Identity Claim to the Person Reference for which it asserts a bounded identifier. | `assurance_level`, `claim_scope` |
| 23 | people-and-teams | `relation.defines-responsibility` | `candidate-new` | `role` | `responsibility` | Links a reusable Role to a Responsibility defined as part of that Role contract. | none |
| 24 | people-and-teams | `relation.identity-link` | `migration-contract-preserved` | `person-reference` | `person-reference` | Links two Person References asserted to refer to the same Person without merging their identities. | none |
| 25 | people-and-teams | `relation.member-of` | `migration-contract-preserved` | `person-reference` | `team` | Links a Person Reference to a Team through an independently governed Team Membership record. | none |
| 26 | people-and-teams | `relation.represents-person` | `migration-contract-preserved` | `person-reference` | `person` | Links a privacy-minimal Person Reference to the Person it denotes under bounded evidence. | none |
| 27 | product-and-project | `relation.advances-goal` | `candidate-new` | `project`, `research-inquiry`, `research-run`, `experiment-design`, `experiment-run` | `goal` | Links a Project, Research carrier, or Experiment carrier to the Goal it is intended to advance. | none |
| 28 | product-and-project | `relation.belongs-to-product` | `candidate-revised` | `product-capability`, `product-thesis`, `context` | `product` | Declares that a Product Thesis, Product Capability, or purpose-specific Context is anchored to one Product. | none |
| 29 | product-and-project | `relation.belongs-to-project` | `candidate-revised` | `research-inquiry`, `research-run`, `experiment-design`, `experiment-run`, `goal`, `work`, `evidence-set`, `capability-realization-binding`, `context` | `project` | Declares the Project scope that owns or bounds a research, experiment, goal, work, evidence, realization, or Context carrier. | none |
| 30 | product-and-project | `relation.contributes-to-product` | `candidate-new` | `project` | `product` | Links a bounded Project to the Product whose outcomes it is intended to advance. | `contribution_scope` |
| 31 | product-and-project | `relation.tests-thesis-proposition` | `candidate-new` | `experiment-design` | `product-thesis-hypothesis`, `product-thesis-outcome` | Links an Experiment Design to a Product Thesis hypothesis or outcome proposition it is designed to test. | `proposition_kind` |
| 32 | research-and-evidence | `relation.addresses-inquiry` | `candidate-new` | `research-run`, `experiment-design`, `experiment-run` | `research-inquiry` | Links a Research Run, Experiment Design, or Experiment Run to the Research Inquiry whose question it addresses. | none |
| 33 | research-and-evidence | `relation.answers-inquiry` | `candidate-new` | `finding` | `research-inquiry` | Links a Finding to the Research Inquiry whose question the Finding answers within its evidence boundary. | none |
| 34 | research-and-evidence | `relation.contradicts` | `migration-contract-preserved` | `evidence-set`, `observation`, `measurement-result` | `finding`, `identity-claim`, `authority-claim`, `hypothesis` | Declares bounded counterevidence against a Finding, hypothesis, identity claim, or authority claim. | none |
| 35 | research-and-evidence | `relation.derives-from` | `migration-contract-preserved` | `*` | `*` | Links a derived artifact, observation, result, or evidence set to the source or run from which it was produced. | none |
| 36 | research-and-evidence | `relation.evaluates` | `candidate-revised` | `evaluation`, `experiment-design`, `experiment-run` | `*` | Declares that an Evaluation or Experiment assesses a named subject without establishing adoption, realization, effectiveness, or Product value. | `evaluation_purpose` |
| 37 | research-and-evidence | `relation.executes-design` | `candidate-new` | `experiment-run` | `experiment-design` | Links an Experiment Run to the exact Experiment Design version it executes. | `design_version_ref` |
| 38 | research-and-evidence | `relation.supports` | `migration-contract-preserved` | `evidence-set`, `observation`, `measurement-result` | `finding`, `identity-claim`, `authority-claim`, `hypothesis` | Declares bounded evidence that supports a Finding, hypothesis, identity claim, or authority claim. | none |
| 39 | research-and-evidence | `relation.uses-method` | `candidate-revised` | `research-run`, `experiment-run`, `measurement-result`, `observation`, `project`, `product` | `method` | Declares the Method used by an execution, empirical record, Project, or Product; usage_role distinguishes ordinary use from a constitutive Method. | `usage_role` |
| 40 | semantic-governance | `relation.admits` | `candidate-new` | `decision` | `definition`, `artifact-type`, `relation-kind`, `other-governed-version` | Links an admission Decision to the exact governed version admitted by that decision. | `admitted_version_ref`, `admitted_sha256` |
| 41 | semantic-governance | `relation.carries-definition` | `candidate-new` | `artifact-type` | `definition` | Links an Artifact Type to the exact admitted Definition version it carries. | `definition_version_ref`, `definition_sha256` |
| 42 | semantic-governance | `relation.contains` | `candidate-new` | `ontology`, `product` | `ontology-node`, `typed-relation`, `product` | Declares governed composition, including Ontology membership and Product containment, without transferring authority between container and member. | `membership_role` |

## Repository alias and residue reconciliation

| Observed term | Disposition | Canonical relation |
| --- | --- | --- |
| `artifact-type-carries-definition or binds-definition` | `normalized` | `relation.carries-definition` |
| `decision-admits-artifact-type` | `normalized` | `relation.admits` |
| `supports-or-contradicts` | `split` | `relation.supports`, `relation.contradicts` |
| `contains_product` | `normalized-with-qualifier` | `relation.contains` |
| `coordinated_by` | `inverse-normalized` | `relation.contributes-to-product` |
| `embodies_method` | `normalized-with-usage-role` | `relation.uses-method` |
| `uses_method` | `spelling-normalized` | `relation.uses-method` |
| `pursues_goal` | `normalized` | `relation.advances-goal` |
| `may-recommend-admission` | `modeled-as-authority-scope` | `relation.claims-authority-over` |

## Examples

### 1. `relation.frames`

Links a Context to the subject whose relevance and interpretation it frames.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:frames"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.frames",
  "relation_kind_ref": "relation.frames",
  "source_ref": "context:lab-artifact-type-admission",
  "status": "candidate-example",
  "target_ref": "review:remaining-18-artifact-types"
}
```

### 2. `relation.fulfills-request`

Links an immutable Context View to the Context Request it fulfills.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:fulfills-request"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.fulfills-request",
  "relation_kind_ref": "relation.fulfills-request",
  "source_ref": "context-view:remaining-18-review:2026-10-05",
  "status": "candidate-example",
  "target_ref": "context-request:remaining-18-review"
}
```

### 3. `relation.projects-context`

Links an immutable Context View to the exact Context version it projects.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:projects-context"
  ],
  "qualifiers": {
    "context_version_ref": "context:lab-artifact-type-admission@1.0.0-candidate.2",
    "source_epoch": "git-worktree:2026-10-05T15:05:00Z"
  },
  "relation_id": "example:relation.projects-context",
  "relation_kind_ref": "relation.projects-context",
  "source_ref": "context-view:remaining-18-review:2026-10-05",
  "status": "candidate-example",
  "target_ref": "context:lab-artifact-type-admission"
}
```

### 4. `relation.references-bounded-context`

Links a purpose-specific Context to a DDD Bounded Context it references.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:references-bounded-context"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.references-bounded-context",
  "relation_kind_ref": "relation.references-bounded-context",
  "source_ref": "context:lab-artifact-type-admission",
  "status": "candidate-example",
  "target_ref": "bounded-context:semantic-governance"
}
```

### 5. `relation.requests-resolution-of`

Links a Context Request to the exact Context version it asks to resolve.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:requests-resolution-of"
  ],
  "qualifiers": {
    "context_version_ref": "context:lab-artifact-type-admission@1.0.0-candidate.2"
  },
  "relation_id": "example:relation.requests-resolution-of",
  "relation_kind_ref": "relation.requests-resolution-of",
  "source_ref": "context-request:remaining-18-review",
  "status": "candidate-example",
  "target_ref": "context:lab-artifact-type-admission"
}
```

### 6. `relation.adopts`

Links a Decision to a version or model it adopts for use in scope.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:adopts"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.adopts",
  "relation_kind_ref": "relation.adopts",
  "source_ref": "decision:adopt-definition-workflow",
  "status": "candidate-example",
  "target_ref": "binding:craft:governed-definition-admission:workflow-v1"
}
```

### 7. `relation.authorizes`

Links a Decision to the exact effect it authorizes; the edge does not execute the effect.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:authorizes"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.authorizes",
  "relation_kind_ref": "relation.authorizes",
  "source_ref": "decision:admit-definition-v1",
  "status": "candidate-example",
  "target_ref": "effect:add-definition-to-authority-registry"
}
```

### 8. `relation.governed-by`

Links a subject to the Policy or Constitution that governs it.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:governed-by"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.governed-by",
  "relation_kind_ref": "relation.governed-by",
  "source_ref": "context:lab-artifact-type-admission",
  "status": "candidate-example",
  "target_ref": "policy:admitted-authority-first"
}
```

### 9. `relation.binds-implementation`

Links an implementation to the Ontology or Schema it implements.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:binds-implementation"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.binds-implementation",
  "relation_kind_ref": "relation.binds-implementation",
  "source_ref": "tool:definition-validator",
  "status": "candidate-example",
  "target_ref": "ontology:artifact-governance"
}
```

### 10. `relation.compiles-to`

Links authored source to a generated output derived from it.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:compiles-to"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.compiles-to",
  "relation_kind_ref": "relation.compiles-to",
  "source_ref": "authority/definitions/registry.json",
  "status": "candidate-example",
  "target_ref": "authority/definitions/DEFINITIONS-INDEX.md"
}
```

### 11. `relation.conforms-to`

Declares evidence-bounded conformance of a Context or capability instance to an exact Profile, parent model, or contract.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:conforms-to"
  ],
  "qualifiers": {
    "conformance_evidence_refs": [
      "receipt:remaining-18-model-validation"
    ],
    "exact_version_ref": "context-profile:governed-review@1.0.0-candidate.2"
  },
  "relation_id": "example:relation.conforms-to",
  "relation_kind_ref": "relation.conforms-to",
  "source_ref": "context:lab-artifact-type-admission",
  "status": "candidate-example",
  "target_ref": "context-profile:governed-review"
}
```

### 12. `relation.inherits-contract`

Links a capability instance to an exact inherited contract, qualified by its Model Instance Binding.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:inherits-contract"
  ],
  "qualifiers": {
    "binding_ref": "model-instance-binding:artifact-type-reviewer",
    "contract_version_ref": "contract:definition-admission-boundaries/v1"
  },
  "relation_id": "example:relation.inherits-contract",
  "relation_kind_ref": "relation.inherits-contract",
  "source_ref": "capability-instance:lab-artifact-type-reviewer",
  "status": "candidate-example",
  "target_ref": "contract:definition-admission-boundaries/v1"
}
```

### 13. `relation.instance-of`

Classifies an implementation or capability instance under an exact parent model while keeping ownership and lifecycle separate.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:instance-of"
  ],
  "qualifiers": {
    "binding_ref": "model-instance-binding:artifact-type-reviewer",
    "parent_version_ref": "product-capability:governed-definition-admission@1.0.0-candidate.1"
  },
  "relation_id": "example:relation.instance-of",
  "relation_kind_ref": "relation.instance-of",
  "source_ref": "capability-instance:lab-artifact-type-reviewer",
  "status": "candidate-example",
  "target_ref": "product-capability:governed-definition-admission"
}
```

### 14. `relation.realizes`

Links an implementation to the Product Capability it realizes.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:realizes"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.realizes",
  "relation_kind_ref": "relation.realizes",
  "source_ref": "workflow:governed-definition-admission/v1",
  "status": "candidate-example",
  "target_ref": "capability:craft:governed-definition-admission"
}
```

### 15. `relation.originates-from`

Links an artifact to the source from which its content or identity originated.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:originates-from"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.originates-from",
  "relation_kind_ref": "relation.originates-from",
  "source_ref": "finding:research-inquiry-v1-contract-gap",
  "status": "candidate-example",
  "target_ref": "source:cyberalchemy-v2-definitions"
}
```

### 16. `relation.successor-of`

Links a successor version or identity to its immediate predecessor.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:successor-of"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.successor-of",
  "relation_kind_ref": "relation.successor-of",
  "source_ref": "definition:product-identity@2",
  "status": "candidate-example",
  "target_ref": "definition:product-identity@1"
}
```

### 17. `relation.supersedes`

Declares that a newer governed artifact replaces an older artifact within a stated scope.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:supersedes"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.supersedes",
  "relation_kind_ref": "relation.supersedes",
  "source_ref": "artifact-type:product-identity@2",
  "status": "candidate-example",
  "target_ref": "artifact-type:product-identity@1"
}
```

### 18. `relation.assigned-responsibility`

Links a Person Reference or Team to an explicitly assigned Responsibility.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:assigned-responsibility"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.assigned-responsibility",
  "relation_kind_ref": "relation.assigned-responsibility",
  "source_ref": "team:semantic-governance",
  "status": "candidate-example",
  "target_ref": "responsibility:maintain-definition-authority"
}
```

### 19. `relation.assigned-role`

Links a Person Reference or Team to a Role through an independently governed Role Assignment record.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:assigned-role"
  ],
  "qualifiers": {
    "basis_ref": "decision:assign-artifact-type-reviewer",
    "period": "2026-10-05/open",
    "role_assignment_ref": "role-assignment:reviewer:artifact-type-reviewer",
    "state": "active"
  },
  "relation_id": "example:relation.assigned-role",
  "relation_kind_ref": "relation.assigned-role",
  "source_ref": "person-reference:repository-reviewer",
  "status": "candidate-example",
  "target_ref": "role:artifact-type-reviewer"
}
```

### 20. `relation.bounded-by-authority-claim`

Links a Role Assignment to the separate Authority Claim that bounds any authority exercised through the assignment.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:bounded-by-authority-claim"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.bounded-by-authority-claim",
  "relation_kind_ref": "relation.bounded-by-authority-claim",
  "source_ref": "role-assignment:reviewer:artifact-type-reviewer",
  "status": "candidate-example",
  "target_ref": "authority-claim:may-recommend-artifact-type-admission"
}
```

### 21. `relation.claims-authority-over`

Links an Authority Claim to the object and scope over which authority is asserted.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:claims-authority-over"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.claims-authority-over",
  "relation_kind_ref": "relation.claims-authority-over",
  "source_ref": "authority-claim:may-recommend-artifact-type-admission",
  "status": "candidate-example",
  "target_ref": "decision-scope:artifact-type-admission"
}
```

### 22. `relation.claims-identifier-for`

Links an Identity Claim to the Person Reference for which it asserts a bounded identifier.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:claims-identifier-for"
  ],
  "qualifiers": {
    "assurance_level": "self-asserted",
    "claim_scope": "CyberAlchemy Lab review attribution"
  },
  "relation_id": "example:relation.claims-identifier-for",
  "relation_kind_ref": "relation.claims-identifier-for",
  "source_ref": "identity-claim:repository-reviewer:workspace-handle",
  "status": "candidate-example",
  "target_ref": "person-reference:repository-reviewer"
}
```

### 23. `relation.defines-responsibility`

Links a reusable Role to a Responsibility defined as part of that Role contract.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:defines-responsibility"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.defines-responsibility",
  "relation_kind_ref": "relation.defines-responsibility",
  "source_ref": "role:artifact-type-reviewer",
  "status": "candidate-example",
  "target_ref": "responsibility:artifact-type-review-quality"
}
```

### 24. `relation.identity-link`

Links two Person References asserted to refer to the same Person without merging their identities.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:identity-link"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.identity-link",
  "relation_kind_ref": "relation.identity-link",
  "source_ref": "person-reference:repository-reviewer",
  "status": "candidate-example",
  "target_ref": "person-reference:workspace-reviewer-001"
}
```

### 25. `relation.member-of`

Links a Person Reference to a Team through an independently governed Team Membership record.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:member-of"
  ],
  "qualifiers": {
    "basis_ref": "decision:semantic-governance-team-membership",
    "membership_ref": "team-membership:reviewer:semantic-governance",
    "period": "2026-10-05/open",
    "state": "active"
  },
  "relation_id": "example:relation.member-of",
  "relation_kind_ref": "relation.member-of",
  "source_ref": "person-reference:repository-reviewer",
  "status": "candidate-example",
  "target_ref": "team:semantic-governance"
}
```

### 26. `relation.represents-person`

Links a privacy-minimal Person Reference to the Person it denotes under bounded evidence.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:represents-person"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.represents-person",
  "relation_kind_ref": "relation.represents-person",
  "source_ref": "person-reference:repository-reviewer",
  "status": "candidate-example",
  "target_ref": "person:repository-reviewer"
}
```

### 27. `relation.advances-goal`

Links a Project, Research carrier, or Experiment carrier to the Goal it is intended to advance.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:advances-goal"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.advances-goal",
  "relation_kind_ref": "relation.advances-goal",
  "source_ref": "project:lab-semantic-governance",
  "status": "candidate-example",
  "target_ref": "goal:reduce-unresolved-definition-residue"
}
```

### 28. `relation.belongs-to-product`

Declares that a Product Thesis, Product Capability, or purpose-specific Context is anchored to one Product.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:belongs-to-product"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.belongs-to-product",
  "relation_kind_ref": "relation.belongs-to-product",
  "source_ref": "context:lab-artifact-type-admission",
  "status": "candidate-example",
  "target_ref": "CA2-PRODUCT-CRAFT"
}
```

### 29. `relation.belongs-to-project`

Declares the Project scope that owns or bounds a research, experiment, goal, work, evidence, realization, or Context carrier.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:belongs-to-project"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.belongs-to-project",
  "relation_kind_ref": "relation.belongs-to-project",
  "source_ref": "experiment-run:definition-normalization-residue:2026-10-05",
  "status": "candidate-example",
  "target_ref": "project:lab-semantic-governance"
}
```

### 30. `relation.contributes-to-product`

Links a bounded Project to the Product whose outcomes it is intended to advance.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:contributes-to-product"
  ],
  "qualifiers": {
    "contribution_scope": "Governed semantic foundations"
  },
  "relation_id": "example:relation.contributes-to-product",
  "relation_kind_ref": "relation.contributes-to-product",
  "source_ref": "project:lab-semantic-governance",
  "status": "candidate-example",
  "target_ref": "CA2-PRODUCT-CRAFT"
}
```

### 31. `relation.tests-thesis-proposition`

Links an Experiment Design to a Product Thesis hypothesis or outcome proposition it is designed to test.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:tests-thesis-proposition"
  ],
  "qualifiers": {
    "proposition_kind": "outcome"
  },
  "relation_id": "example:relation.tests-thesis-proposition",
  "relation_kind_ref": "relation.tests-thesis-proposition",
  "source_ref": "experiment-design:definition-normalization-residue",
  "status": "candidate-example",
  "target_ref": "product-thesis:craft#outcome-authoritative-state"
}
```

### 32. `relation.addresses-inquiry`

Links a Research Run, Experiment Design, or Experiment Run to the Research Inquiry whose question it addresses.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:addresses-inquiry"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.addresses-inquiry",
  "relation_kind_ref": "relation.addresses-inquiry",
  "source_ref": "experiment-design:definition-normalization-residue",
  "status": "candidate-example",
  "target_ref": "research-inquiry:definition-normalization-residue"
}
```

### 33. `relation.answers-inquiry`

Links a Finding to the Research Inquiry whose question the Finding answers within its evidence boundary.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:answers-inquiry"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.answers-inquiry",
  "relation_kind_ref": "relation.answers-inquiry",
  "source_ref": "finding:normalization-residue-lowered",
  "status": "candidate-example",
  "target_ref": "research-inquiry:definition-normalization-residue"
}
```

### 34. `relation.contradicts`

Declares bounded counterevidence against a Finding, hypothesis, identity claim, or authority claim.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:contradicts"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.contradicts",
  "relation_kind_ref": "relation.contradicts",
  "source_ref": "observation:normalization-regression",
  "status": "candidate-example",
  "target_ref": "finding:normalization-residue-lowered"
}
```

### 35. `relation.derives-from`

Links a derived artifact, observation, result, or evidence set to the source or run from which it was produced.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:derives-from"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.derives-from",
  "relation_kind_ref": "relation.derives-from",
  "source_ref": "observation:definition-normalization-residue-classes",
  "status": "candidate-example",
  "target_ref": "experiment-run:definition-normalization-residue:2026-10-05"
}
```

### 36. `relation.evaluates`

Declares that an Evaluation or Experiment assesses a named subject without establishing adoption, realization, effectiveness, or Product value.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:evaluates"
  ],
  "qualifiers": {
    "evaluation_purpose": "Measure one bounded residue signal"
  },
  "relation_id": "example:relation.evaluates",
  "relation_kind_ref": "relation.evaluates",
  "source_ref": "experiment-run:definition-normalization-residue:2026-10-05",
  "status": "candidate-example",
  "target_ref": "capability:craft:governed-definition-admission"
}
```

### 37. `relation.executes-design`

Links an Experiment Run to the exact Experiment Design version it executes.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:executes-design"
  ],
  "qualifiers": {
    "design_version_ref": "experiment-design:definition-normalization-residue@1.0.0-candidate.1"
  },
  "relation_id": "example:relation.executes-design",
  "relation_kind_ref": "relation.executes-design",
  "source_ref": "experiment-run:definition-normalization-residue:2026-10-05",
  "status": "candidate-example",
  "target_ref": "experiment-design:definition-normalization-residue"
}
```

### 38. `relation.supports`

Declares bounded evidence that supports a Finding, hypothesis, identity claim, or authority claim.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:supports"
  ],
  "qualifiers": {},
  "relation_id": "example:relation.supports",
  "relation_kind_ref": "relation.supports",
  "source_ref": "evidence-set:definition-normalization-residue-run-2026-10-05",
  "status": "candidate-example",
  "target_ref": "finding:normalization-residue-lowered"
}
```

### 39. `relation.uses-method`

Declares the Method used by an execution, empirical record, Project, or Product; usage_role distinguishes ordinary use from a constitutive Method.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:uses-method"
  ],
  "qualifiers": {
    "usage_role": "measurement"
  },
  "relation_id": "example:relation.uses-method",
  "relation_kind_ref": "relation.uses-method",
  "source_ref": "measurement-result:definition-normalization-residue-entropy:2026-10-05",
  "status": "candidate-example",
  "target_ref": "measurement-method:definition-normalization-residue-entropy"
}
```

### 40. `relation.admits`

Links an admission Decision to the exact governed version admitted by that decision.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:admits"
  ],
  "qualifiers": {
    "admitted_sha256": "digest-bound-at-decision-time",
    "admitted_version_ref": "cal.artifact-type.experiment-run/v1@1.0.0-candidate.2"
  },
  "relation_id": "example:relation.admits",
  "relation_kind_ref": "relation.admits",
  "source_ref": "decision:artifact-type-batch-admission",
  "status": "candidate-example",
  "target_ref": "cal.artifact-type.experiment-run/v1"
}
```

### 41. `relation.carries-definition`

Links an Artifact Type to the exact admitted Definition version it carries.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:carries-definition"
  ],
  "qualifiers": {
    "definition_sha256": "digest-bound-at-instance-time",
    "definition_version_ref": "cal.definition.experiment@1.0.0-candidate.1"
  },
  "relation_id": "example:relation.carries-definition",
  "relation_kind_ref": "relation.carries-definition",
  "source_ref": "cal.artifact-type.experiment-run/v1",
  "status": "candidate-example",
  "target_ref": "cal.definition.experiment@1.0.0-candidate.1"
}
```

### 42. `relation.contains`

Declares governed composition, including Ontology membership and Product containment, without transferring authority between container and member.

```json
{
  "authority_effect": "none",
  "evidence_refs": [
    "evidence:contains"
  ],
  "qualifiers": {
    "membership_role": "governed-node"
  },
  "relation_id": "example:relation.contains",
  "relation_kind_ref": "relation.contains",
  "source_ref": "ontology:artifact-governance",
  "status": "candidate-example",
  "target_ref": "cal.definition.artifact-type"
}
```

## Claim ceiling

This candidate defines a complete normalized Relation Kind review surface for the current Artifact Type model and repository relation residue. It does not admit Relation Kinds, endpoint artifacts, examples, identities, authority, evidence claims, or effects.
