<!-- GENERATED FILE: canonical data is relation-kind-instances.json and typed-relation-examples.json. -->

# Step 6 relation contract materialization

- Relation Kinds: `23`
- Exact ordered endpoint pairs: `147`
- Typed Relation examples: `23`
- Wildcards: `0`
- Authority effect: `none`

## Complete model

### `relation.member-of`

Which governed container or scope is this member part of?

Required qualifiers: `membership_role`

Example:

```json
{
  "qualifiers": {
    "membership_role": "project-scope"
  },
  "relation_evidence_refs": [
    "evidence:member-of"
  ],
  "relation_kind_ref": "relation.member-of",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "experiment-run",
    "ref": "experiment-run:definition-normalization-residue:2026-10-05",
    "version_ref": "experiment-run:definition-normalization-residue:2026-10-05@example-revision-1"
  },
  "target": {
    "kind": "project",
    "ref": "project:lab-semantic-governance",
    "version_ref": "project:lab-semantic-governance@example-revision-1"
  }
}
```

### `relation.contributes-to`

Which Product or Goal is this activity intended to advance?

Required qualifiers: `contribution_role, contribution_scope`

Example:

```json
{
  "qualifiers": {
    "contribution_role": "advance-product",
    "contribution_scope": "Governed semantic foundations"
  },
  "relation_evidence_refs": [
    "evidence:contributes-to"
  ],
  "relation_kind_ref": "relation.contributes-to",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "project",
    "ref": "project:lab-semantic-governance",
    "version_ref": "project:lab-semantic-governance@example-revision-1"
  },
  "target": {
    "kind": "product",
    "ref": "CA2-PRODUCT-CRAFT",
    "version_ref": "CA2-PRODUCT-CRAFT@example-revision-1"
  }
}
```

### `relation.uses-method`

Which Method does this subject depend on or employ?

Required qualifiers: `usage_role`

Example:

```json
{
  "qualifiers": {
    "usage_role": "measurement"
  },
  "relation_evidence_refs": [
    "evidence:uses-method"
  ],
  "relation_kind_ref": "relation.uses-method",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "measurement-result",
    "ref": "measurement-result:definition-normalization-residue-entropy:2026-10-05",
    "version_ref": "measurement-result:definition-normalization-residue-entropy:2026-10-05@example-revision-1"
  },
  "target": {
    "kind": "method",
    "ref": "measurement-method:definition-normalization-residue-entropy",
    "version_ref": "measurement-method:definition-normalization-residue-entropy@example-revision-1"
  }
}
```

### `relation.evaluates`

Which subject or proposition is being assessed?

Required qualifiers: `evaluation_role, evaluation_purpose`

Example:

```json
{
  "qualifiers": {
    "evaluation_purpose": "Test one bounded outcome proposition",
    "evaluation_role": "test-thesis-proposition"
  },
  "relation_evidence_refs": [
    "evidence:evaluates"
  ],
  "relation_kind_ref": "relation.evaluates",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "experiment-design",
    "ref": "experiment-design:definition-normalization-residue",
    "version_ref": "experiment-design:definition-normalization-residue@example-revision-1"
  },
  "target": {
    "kind": "product-thesis",
    "ref": "product-thesis:craft#outcome-authoritative-state",
    "version_ref": "product-thesis:craft#outcome-authoritative-state@example-revision-1"
  }
}
```

### `relation.realizes`

Which declared design or capability is concretely instantiated by this subject?

Required qualifiers: `realization_role, exact_target_version_ref`

Example:

```json
{
  "qualifiers": {
    "exact_target_version_ref": "experiment-design:definition-normalization-residue@1.0.0-candidate.1",
    "realization_role": "design-execution"
  },
  "relation_evidence_refs": [
    "evidence:realizes"
  ],
  "relation_kind_ref": "relation.realizes",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "experiment-run",
    "ref": "experiment-run:definition-normalization-residue:2026-10-05",
    "version_ref": "experiment-run:definition-normalization-residue:2026-10-05@example-revision-1"
  },
  "target": {
    "kind": "experiment-design",
    "ref": "experiment-design:definition-normalization-residue",
    "version_ref": "experiment-design:definition-normalization-residue@example-revision-1"
  }
}
```

### `relation.engages-inquiry`

How does this research carrier engage a Research Inquiry?

Required qualifiers: `inquiry_role`

Example:

```json
{
  "qualifiers": {
    "inquiry_role": "answers"
  },
  "relation_evidence_refs": [
    "evidence:engages-inquiry"
  ],
  "relation_kind_ref": "relation.engages-inquiry",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "finding",
    "ref": "finding:normalization-residue-lowered",
    "version_ref": "finding:normalization-residue-lowered@example-revision-1"
  },
  "target": {
    "kind": "research-inquiry",
    "ref": "research-inquiry:definition-normalization-residue",
    "version_ref": "research-inquiry:definition-normalization-residue@example-revision-1"
  }
}
```

### `relation.originates-from`

From which source did this identity or content originate?

Required qualifiers: `origin_role`

Example:

```json
{
  "qualifiers": {
    "origin_role": "content-source"
  },
  "relation_evidence_refs": [
    "evidence:originates-from"
  ],
  "relation_kind_ref": "relation.originates-from",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "finding",
    "ref": "finding:research-inquiry-v1-contract-gap",
    "version_ref": "finding:research-inquiry-v1-contract-gap@example-revision-1"
  },
  "target": {
    "kind": "source",
    "ref": "source:cyberalchemy-v2-definitions",
    "version_ref": "source:cyberalchemy-v2-definitions@example-revision-1"
  }
}
```

### `relation.derives-from`

From which material or governed source was this artifact derived?

Required qualifiers: `derivation_role`

Example:

```json
{
  "qualifiers": {
    "derivation_role": "context-projection"
  },
  "relation_evidence_refs": [
    "evidence:derives-from"
  ],
  "relation_kind_ref": "relation.derives-from",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "context-view",
    "ref": "context-view:remaining-18-review:2026-10-05",
    "version_ref": "context-view:remaining-18-review:2026-10-05@example-revision-1"
  },
  "target": {
    "kind": "context",
    "ref": "context:lab-artifact-type-admission",
    "version_ref": "context:lab-artifact-type-admission@example-revision-1"
  }
}
```

### `relation.evidence-bears-on`

What evidential polarity does this evidence have toward this claim?

Required qualifiers: `polarity`

Example:

```json
{
  "qualifiers": {
    "polarity": "supports"
  },
  "relation_evidence_refs": [
    "evidence:evidence-bears-on"
  ],
  "relation_kind_ref": "relation.evidence-bears-on",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "evidence-set",
    "ref": "evidence-set:definition-normalization-residue-run-2026-10-05",
    "version_ref": "evidence-set:definition-normalization-residue-run-2026-10-05@example-revision-1"
  },
  "target": {
    "kind": "finding",
    "ref": "finding:normalization-residue-lowered",
    "version_ref": "finding:normalization-residue-lowered@example-revision-1"
  }
}
```

### `relation.governed-by`

Which Policy or Constitution governs this subject?

Required qualifiers: `governance_role`

Example:

```json
{
  "qualifiers": {
    "governance_role": "source-selection"
  },
  "relation_evidence_refs": [
    "evidence:governed-by"
  ],
  "relation_kind_ref": "relation.governed-by",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "context",
    "ref": "context:lab-artifact-type-admission",
    "version_ref": "context:lab-artifact-type-admission@example-revision-1"
  },
  "target": {
    "kind": "policy",
    "ref": "policy:admitted-authority-first",
    "version_ref": "policy:admitted-authority-first@example-revision-1"
  }
}
```

### `relation.declares-effect-on`

Which exact governance effect does this Decision declare?

Required qualifiers: `effect_kind, exact_target_version_ref`

Example:

```json
{
  "qualifiers": {
    "effect_kind": "admits",
    "exact_target_version_ref": "cal.artifact-type.experiment-run/v1@1.0.0-candidate.2"
  },
  "relation_evidence_refs": [
    "evidence:declares-effect-on"
  ],
  "relation_kind_ref": "relation.declares-effect-on",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "decision",
    "ref": "decision:artifact-type-batch-admission",
    "version_ref": "decision:artifact-type-batch-admission@example-revision-1"
  },
  "target": {
    "kind": "artifact-type",
    "ref": "cal.artifact-type.experiment-run/v1",
    "version_ref": "cal.artifact-type.experiment-run/v1@example-revision-1"
  }
}
```

### `relation.instance-of`

Under which exact parent model is this subject classified?

Required qualifiers: `parent_version_ref, binding_ref`

Example:

```json
{
  "qualifiers": {
    "binding_ref": "model-instance-binding:artifact-type-reviewer",
    "parent_version_ref": "product-capability:governed-definition-admission@1.0.0-candidate.1"
  },
  "relation_evidence_refs": [
    "evidence:instance-of"
  ],
  "relation_kind_ref": "relation.instance-of",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "capability-instance",
    "ref": "capability-instance:lab-artifact-type-reviewer",
    "version_ref": "capability-instance:lab-artifact-type-reviewer@example-revision-1"
  },
  "target": {
    "kind": "product-capability",
    "ref": "product-capability:governed-definition-admission",
    "version_ref": "product-capability:governed-definition-admission@example-revision-1"
  }
}
```

### `relation.binds-implementation`

Which Ontology or Schema does this implementation bind?

Required qualifiers: `binding_role`

Example:

```json
{
  "qualifiers": {
    "binding_role": "implements-ontology"
  },
  "relation_evidence_refs": [
    "evidence:binds-implementation"
  ],
  "relation_kind_ref": "relation.binds-implementation",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "implementation",
    "ref": "implementation:definition-validator",
    "version_ref": "implementation:definition-validator@example-revision-1"
  },
  "target": {
    "kind": "ontology",
    "ref": "ontology:artifact-governance",
    "version_ref": "ontology:artifact-governance@example-revision-1"
  }
}
```

### `relation.conforms-to`

Which exact contract does this subject demonstrably conform to, and under which evidence?

Required qualifiers: `conformance_scope, exact_version_ref, conformance_evidence_refs`

Example:

```json
{
  "qualifiers": {
    "conformance_evidence_refs": [
      "receipt:remaining-18-model-validation"
    ],
    "conformance_scope": "context-contract",
    "exact_version_ref": "context-profile:governed-review@1.0.0-candidate.2"
  },
  "relation_evidence_refs": [
    "evidence:conforms-to"
  ],
  "relation_kind_ref": "relation.conforms-to",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "context",
    "ref": "context:lab-artifact-type-admission",
    "version_ref": "context:lab-artifact-type-admission@example-revision-1"
  },
  "target": {
    "kind": "context-profile",
    "ref": "context-profile:governed-review",
    "version_ref": "context-profile:governed-review@example-revision-1"
  }
}
```

### `relation.inherits-contract`

Which exact contract obligations are inherited by this instance?

Required qualifiers: `binding_ref, contract_version_ref`

Example:

```json
{
  "qualifiers": {
    "binding_ref": "model-instance-binding:artifact-type-reviewer",
    "contract_version_ref": "contract:definition-admission-boundaries/v1"
  },
  "relation_evidence_refs": [
    "evidence:inherits-contract"
  ],
  "relation_kind_ref": "relation.inherits-contract",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "capability-instance",
    "ref": "capability-instance:lab-artifact-type-reviewer",
    "version_ref": "capability-instance:lab-artifact-type-reviewer@example-revision-1"
  },
  "target": {
    "kind": "contract",
    "ref": "contract:definition-admission-boundaries/v1",
    "version_ref": "contract:definition-admission-boundaries/v1@example-revision-1"
  }
}
```

### `relation.frames`

Which subject does this Context frame for relevance and interpretation?

Required qualifiers: `framing_role`

Example:

```json
{
  "qualifiers": {
    "framing_role": "bounded-context-reference"
  },
  "relation_evidence_refs": [
    "evidence:frames"
  ],
  "relation_kind_ref": "relation.frames",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "context",
    "ref": "context:lab-artifact-type-admission",
    "version_ref": "context:lab-artifact-type-admission@example-revision-1"
  },
  "target": {
    "kind": "bounded-context",
    "ref": "bounded-context:semantic-governance",
    "version_ref": "bounded-context:semantic-governance@example-revision-1"
  }
}
```

### `relation.requests-resolution-of`

Which exact Context version does this Context Request ask to resolve?

Required qualifiers: `context_version_ref`

Example:

```json
{
  "qualifiers": {
    "context_version_ref": "context:lab-artifact-type-admission@1.0.0-candidate.2"
  },
  "relation_evidence_refs": [
    "evidence:requests-resolution-of"
  ],
  "relation_kind_ref": "relation.requests-resolution-of",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "context-request",
    "ref": "context-request:remaining-18-review",
    "version_ref": "context-request:remaining-18-review@example-revision-1"
  },
  "target": {
    "kind": "context",
    "ref": "context:lab-artifact-type-admission",
    "version_ref": "context:lab-artifact-type-admission@example-revision-1"
  }
}
```

### `relation.fulfills-request`

Which request is this immutable output intended to fulfill?

Required qualifiers: `fulfillment_role`

Example:

```json
{
  "qualifiers": {
    "fulfillment_role": "immutable-view"
  },
  "relation_evidence_refs": [
    "evidence:fulfills-request"
  ],
  "relation_kind_ref": "relation.fulfills-request",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "context-view",
    "ref": "context-view:remaining-18-review:2026-10-05",
    "version_ref": "context-view:remaining-18-review:2026-10-05@example-revision-1"
  },
  "target": {
    "kind": "context-request",
    "ref": "context-request:remaining-18-review",
    "version_ref": "context-request:remaining-18-review@example-revision-1"
  }
}
```

### `relation.successor-of`

Which predecessor does this successor continue or replace?

Required qualifiers: `succession_effect`

Example:

```json
{
  "qualifiers": {
    "succession_effect": "supersedes"
  },
  "relation_evidence_refs": [
    "evidence:successor-of"
  ],
  "relation_kind_ref": "relation.successor-of",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "artifact-type",
    "ref": "artifact-type:product-identity@2",
    "version_ref": "artifact-type:product-identity@2@example-revision-1"
  },
  "target": {
    "kind": "artifact-type",
    "ref": "artifact-type:product-identity@1",
    "version_ref": "artifact-type:product-identity@1@example-revision-1"
  }
}
```

### `relation.assigned-to`

Which Role or Responsibility is explicitly assigned to this assignee?

Required qualifiers: `assignment_kind, relation_record_ref`

Example:

```json
{
  "qualifiers": {
    "assignment_kind": "role",
    "relation_record_ref": "role-assignment:reviewer:artifact-type-reviewer"
  },
  "relation_evidence_refs": [
    "evidence:assigned-to"
  ],
  "relation_kind_ref": "relation.assigned-to",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "person-reference",
    "ref": "person-reference:repository-reviewer",
    "version_ref": "person-reference:repository-reviewer@example-revision-1"
  },
  "target": {
    "kind": "role",
    "ref": "role:artifact-type-reviewer",
    "version_ref": "role:artifact-type-reviewer@example-revision-1"
  }
}
```

### `relation.asserts-identity-of`

What bounded identity correspondence is being asserted between these endpoints?

Required qualifiers: `assertion_kind, claim_scope`

Example:

```json
{
  "qualifiers": {
    "assertion_kind": "claims-identifier",
    "claim_scope": "CyberAlchemy Lab review attribution"
  },
  "relation_evidence_refs": [
    "evidence:asserts-identity-of"
  ],
  "relation_kind_ref": "relation.asserts-identity-of",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "identity-claim",
    "ref": "identity-claim:repository-reviewer:workspace-handle",
    "version_ref": "identity-claim:repository-reviewer:workspace-handle@example-revision-1"
  },
  "target": {
    "kind": "person-reference",
    "ref": "person-reference:repository-reviewer",
    "version_ref": "person-reference:repository-reviewer@example-revision-1"
  }
}
```

### `relation.scopes-authority-over`

What object or assignment is bounded by this explicit Authority Claim?

Required qualifiers: `authority_role, scope_ref`

Example:

```json
{
  "qualifiers": {
    "authority_role": "bounds-assignment",
    "scope_ref": "scope:artifact-type-admission-recommendation"
  },
  "relation_evidence_refs": [
    "evidence:scopes-authority-over"
  ],
  "relation_kind_ref": "relation.scopes-authority-over",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "authority-claim",
    "ref": "authority-claim:may-recommend-artifact-type-admission",
    "version_ref": "authority-claim:may-recommend-artifact-type-admission@example-revision-1"
  },
  "target": {
    "kind": "role-assignment",
    "ref": "role-assignment:reviewer:artifact-type-reviewer",
    "version_ref": "role-assignment:reviewer:artifact-type-reviewer@example-revision-1"
  }
}
```

### `relation.carries-definition`

Which exact Definition version supplies this Artifact Type's governed meaning?

Required qualifiers: `definition_version_ref, definition_sha256`

Example:

```json
{
  "qualifiers": {
    "definition_sha256": "digest-bound-at-instance-time",
    "definition_version_ref": "cal.definition.experiment@1.0.0-candidate.1"
  },
  "relation_evidence_refs": [
    "evidence:carries-definition"
  ],
  "relation_kind_ref": "relation.carries-definition",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "artifact-type",
    "ref": "cal.artifact-type.experiment-run/v1",
    "version_ref": "cal.artifact-type.experiment-run/v1@example-revision-1"
  },
  "target": {
    "kind": "definition",
    "ref": "cal.definition.experiment@1.0.0-candidate.1",
    "version_ref": "cal.definition.experiment@1.0.0-candidate.1@example-revision-1"
  }
}
```

## Claim ceiling

This materializes complete candidate carriers and candidate examples. It admits no Artifact Type, Relation Kind, Typed Relation, endpoint pair, ontology assertion, consumer, or runtime.
