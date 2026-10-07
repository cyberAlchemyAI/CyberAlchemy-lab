<!-- GENERATED FILE: canonical data is model.json and examples.json. -->

# Definition-complete relation model

- Active Relation Kinds: `40`
- New Relation Kinds: `17`
- Endpoint kinds: `100`
- Exact ordered pairs: `538`
- Wildcards: `0`
- Authority effect: `none`

## Complete axes

| Relation Kind | Unique question | Exact pairs |
| --- | --- | ---: |
| `relation.acts-for` | Which Principal is this Agent Instance acting for under one exact Delegation? | 1 |
| `relation.addresses-improvement-target` | Which Improvement Target is this Research Inquiry intended to address? | 1 |
| `relation.addresses-intent` | Which exact Intent is this governed subject intended to address? | 6 |
| `relation.affects` | Which exact subject was affected, under what declared scope? | 22 |
| `relation.applies-lesson` | Which exact Operational Lesson revision was used or deliberately not used by this Lesson Application? | 1 |
| `relation.asserts-identity-of` | What bounded identity correspondence is being asserted between these endpoints? | 4 |
| `relation.assigned-to` | Which Role or Responsibility is explicitly assigned to this assignee? | 6 |
| `relation.binds-implementation` | Which Ontology or Schema does this implementation bind? | 2 |
| `relation.carries-definition` | Which exact Definition version supplies this Artifact Type's governed meaning? | 1 |
| `relation.challenges` | Which exact governed subject revision does this Challenge Event challenge? | 100 |
| `relation.conforms-to` | Which exact contract does this subject demonstrably conform to, and under which evidence? | 3 |
| `relation.consumes-view` | Which immutable Context View or Ontology View did this Agent Session actually consume? | 2 |
| `relation.contributes-to` | Which Product or Goal is this activity intended to advance? | 8 |
| `relation.controls` | Which Failure Mode is this Failure Control Binding intended to control? | 1 |
| `relation.declares-effect-on` | Which exact governance effect does this Decision declare? | 21 |
| `relation.derives-from` | From which material or governed source was this artifact derived? | 40 |
| `relation.engages-inquiry` | How does this research carrier engage a Research Inquiry? | 4 |
| `relation.evaluates` | Which subject or proposition is being assessed? | 16 |
| `relation.evidence-bears-on` | What evidential polarity does this evidence have toward this claim? | 72 |
| `relation.frames` | Which subject does this Context frame for relevance and interpretation? | 5 |
| `relation.fulfills-request` | Which request is this immutable output intended to fulfill? | 1 |
| `relation.governed-by` | Which Policy or Constitution governs this subject? | 23 |
| `relation.has-capability` | Which Agent Capability is declared for this Agent Profile or Agent Instance? | 2 |
| `relation.inherits-contract` | Which exact contract obligations are inherited by this instance? | 1 |
| `relation.instance-of` | Under which exact parent model is this subject classified? | 12 |
| `relation.member-of` | Which governed container or scope is this member part of? | 23 |
| `relation.occurs-during` | In which exact execution envelope did this Failure Occurrence happen? | 5 |
| `relation.originates-from` | From which source did this identity or content originate? | 7 |
| `relation.performs` | Which attributable activity is performed or attempted by this Agent Instance? | 5 |
| `relation.produces` | Which governed output was produced by this Agent Action? | 19 |
| `relation.profiled-by` | Which exact Agent Profile revision configures this Agent Instance? | 1 |
| `relation.realizes` | Which declared design or capability is concretely instantiated by this subject? | 2 |
| `relation.requests-resolution-of` | Which exact Context version does this Context Request ask to resolve? | 1 |
| `relation.responds-to` | Which Failure Occurrence or Incident is this Agent Action intended to address? | 2 |
| `relation.scopes-authority-over` | What object or assignment is bounded by this explicit Authority Claim? | 2 |
| `relation.successor-of` | Which predecessor does this successor continue or replace? | 100 |
| `relation.tests-hypothesis` | Which exact Hypothesis is this Experiment Design constructed to test? | 1 |
| `relation.uses-method` | Which Method does this subject depend on or employ? | 7 |
| `relation.uses-tool` | Which Tool or Implementation does this Agent Session or Agent Action use? | 4 |
| `relation.violates` | Which exact expected boundary does evidence indicate was not satisfied? | 4 |

## Deferred and local decisions

- `relation.subclass-of` is deferred until a reviewed hierarchical Classification Scheme requires it.
- Ontology Node subject representation remains an ontology-local exact binding.
- Agent Instance to Agent Profile uses the independent `relation.profiled-by` axis.

## Realistic examples

### `relation.acts-for`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "delegation_ref": "example-delegation_ref",
    "effective_period": "example-effective_period",
    "revocation_state": "example-revocation_state",
    "scope_ref": "example-scope_ref"
  },
  "relation_id": "typed-relation:example-acts-for",
  "relation_kind_ref": "relation.acts-for",
  "source_ref": "agent-instance:example-001",
  "target_ref": "principal:example-001"
}
```

### `relation.addresses-improvement-target`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "addressing_role": "example-addressing_role",
    "target_version_ref": "example-target_version_ref"
  },
  "relation_id": "typed-relation:example-addresses-improvement-target",
  "relation_kind_ref": "relation.addresses-improvement-target",
  "source_ref": "research-inquiry:example-001",
  "target_ref": "improvement-target:example-001"
}
```

### `relation.addresses-intent`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "addressing_role": "example-addressing_role",
    "intent_resolution_ref": "example-intent_resolution_ref"
  },
  "relation_id": "typed-relation:example-addresses-intent",
  "relation_kind_ref": "relation.addresses-intent",
  "source_ref": "agent-assignment:example-001",
  "target_ref": "intent:example-001"
}
```

### `relation.affects`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "evidence_posture": "example-evidence_posture",
    "impact_scope": "example-impact_scope"
  },
  "relation_id": "typed-relation:example-affects",
  "relation_kind_ref": "relation.affects",
  "source_ref": "failure-occurrence:example-001",
  "target_ref": "agent-capability:example-001"
}
```

### `relation.applies-lesson`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "applicability_assessment_ref": "example-applicability_assessment_ref",
    "application_posture": "example-application_posture",
    "instruction_precedence": "example-instruction_precedence",
    "lesson_revision_ref": "example-lesson_revision_ref"
  },
  "relation_id": "typed-relation:example-applies-lesson",
  "relation_kind_ref": "relation.applies-lesson",
  "source_ref": "lesson-application:example-001",
  "target_ref": "operational-lesson:example-001"
}
```

### `relation.asserts-identity-of`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "assertion_kind": "example-assertion_kind",
    "claim_scope": "example-claim_scope"
  },
  "relation_id": "typed-relation:example-asserts-identity-of",
  "relation_kind_ref": "relation.asserts-identity-of",
  "source_ref": "identity-claim:example-001",
  "target_ref": "person-reference:example-001"
}
```

### `relation.assigned-to`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "assignment_kind": "example-assignment_kind",
    "relation_record_ref": "example-relation_record_ref"
  },
  "relation_id": "typed-relation:example-assigned-to",
  "relation_kind_ref": "relation.assigned-to",
  "source_ref": "agent-instance:example-001",
  "target_ref": "responsibility:example-001"
}
```

### `relation.binds-implementation`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "binding_role": "example-binding_role"
  },
  "relation_id": "typed-relation:example-binds-implementation",
  "relation_kind_ref": "relation.binds-implementation",
  "source_ref": "implementation:example-001",
  "target_ref": "ontology:example-001"
}
```

### `relation.carries-definition`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "definition_sha256": "example-definition_sha256",
    "definition_version_ref": "example-definition_version_ref"
  },
  "relation_id": "typed-relation:example-carries-definition",
  "relation_kind_ref": "relation.carries-definition",
  "source_ref": "artifact-type:example-001",
  "target_ref": "definition:example-001"
}
```

### `relation.challenges`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "challenge_contract_ref": "example-challenge_contract_ref",
    "challenge_mode": "example-challenge_mode",
    "challenged_version_ref": "example-challenged_version_ref"
  },
  "relation_id": "typed-relation:example-challenges",
  "relation_kind_ref": "relation.challenges",
  "source_ref": "challenge-event:example-001",
  "target_ref": "agent-action:example-001"
}
```

### `relation.conforms-to`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "conformance_evidence_refs": "example-conformance_evidence_refs",
    "conformance_scope": "example-conformance_scope",
    "exact_version_ref": "example-exact_version_ref"
  },
  "relation_id": "typed-relation:example-conforms-to",
  "relation_kind_ref": "relation.conforms-to",
  "source_ref": "capability-instance:example-001",
  "target_ref": "contract:example-001"
}
```

### `relation.consumes-view`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "consumption_purpose": "example-consumption_purpose",
    "cursor": "example-cursor",
    "view_digest": "example-view_digest"
  },
  "relation_id": "typed-relation:example-consumes-view",
  "relation_kind_ref": "relation.consumes-view",
  "source_ref": "agent-session:example-001",
  "target_ref": "context-view:example-001"
}
```

### `relation.contributes-to`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "contribution_role": "example-contribution_role",
    "contribution_scope": "example-contribution_scope"
  },
  "relation_id": "typed-relation:example-contributes-to",
  "relation_kind_ref": "relation.contributes-to",
  "source_ref": "agent-action:example-001",
  "target_ref": "goal:example-001"
}
```

### `relation.controls`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "control_role": "example-control_role",
    "control_version_ref": "example-control_version_ref",
    "installation_posture": "example-installation_posture"
  },
  "relation_id": "typed-relation:example-controls",
  "relation_kind_ref": "relation.controls",
  "source_ref": "failure-control-binding:example-001",
  "target_ref": "failure-mode:example-001"
}
```

### `relation.declares-effect-on`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "effect_kind": "example-effect_kind",
    "exact_target_version_ref": "example-exact_target_version_ref"
  },
  "relation_id": "typed-relation:example-declares-effect-on",
  "relation_kind_ref": "relation.declares-effect-on",
  "source_ref": "decision:example-001",
  "target_ref": "agent-capability:example-001"
}
```

### `relation.derives-from`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "derivation_role": "example-derivation_role"
  },
  "relation_id": "typed-relation:example-derives-from",
  "relation_kind_ref": "relation.derives-from",
  "source_ref": "agent-reflection:example-001",
  "target_ref": "agent-action:example-001"
}
```

### `relation.engages-inquiry`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "inquiry_role": "example-inquiry_role"
  },
  "relation_id": "typed-relation:example-engages-inquiry",
  "relation_kind_ref": "relation.engages-inquiry",
  "source_ref": "experiment-design:example-001",
  "target_ref": "research-inquiry:example-001"
}
```

### `relation.evaluates`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "evaluation_purpose": "example-evaluation_purpose",
    "evaluation_role": "example-evaluation_role"
  },
  "relation_id": "typed-relation:example-evaluates",
  "relation_kind_ref": "relation.evaluates",
  "source_ref": "evaluation:example-001",
  "target_ref": "capability-realization-binding:example-001"
}
```

### `relation.evidence-bears-on`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "polarity": "example-polarity"
  },
  "relation_id": "typed-relation:example-evidence-bears-on",
  "relation_kind_ref": "relation.evidence-bears-on",
  "source_ref": "evidence-set:example-001",
  "target_ref": "authority-claim:example-001"
}
```

### `relation.frames`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "framing_role": "example-framing_role"
  },
  "relation_id": "typed-relation:example-frames",
  "relation_kind_ref": "relation.frames",
  "source_ref": "context:example-001",
  "target_ref": "bounded-context:example-001"
}
```

### `relation.fulfills-request`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "fulfillment_role": "example-fulfillment_role"
  },
  "relation_id": "typed-relation:example-fulfills-request",
  "relation_kind_ref": "relation.fulfills-request",
  "source_ref": "context-view:example-001",
  "target_ref": "context-request:example-001"
}
```

### `relation.governed-by`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "governance_role": "example-governance_role"
  },
  "relation_id": "typed-relation:example-governed-by",
  "relation_kind_ref": "relation.governed-by",
  "source_ref": "agent-action:example-001",
  "target_ref": "policy:example-001"
}
```

### `relation.has-capability`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "capability_version_ref": "example-capability_version_ref",
    "declaration_basis": "example-declaration_basis"
  },
  "relation_id": "typed-relation:example-has-capability",
  "relation_kind_ref": "relation.has-capability",
  "source_ref": "agent-instance:example-001",
  "target_ref": "agent-capability:example-001"
}
```

### `relation.inherits-contract`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "binding_ref": "example-binding_ref",
    "contract_version_ref": "example-contract_version_ref"
  },
  "relation_id": "typed-relation:example-inherits-contract",
  "relation_kind_ref": "relation.inherits-contract",
  "source_ref": "capability-instance:example-001",
  "target_ref": "contract:example-001"
}
```

### `relation.instance-of`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "binding_ref": "example-binding_ref",
    "parent_version_ref": "example-parent_version_ref"
  },
  "relation_id": "typed-relation:example-instance-of",
  "relation_kind_ref": "relation.instance-of",
  "source_ref": "agent-action:example-001",
  "target_ref": "classification-value:example-001"
}
```

### `relation.member-of`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "membership_role": "example-membership_role"
  },
  "relation_id": "typed-relation:example-member-of",
  "relation_kind_ref": "relation.member-of",
  "source_ref": "agent-action:example-001",
  "target_ref": "agent-session:example-001"
}
```

### `relation.occurs-during`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "envelope_version_ref": "example-envelope_version_ref",
    "temporal_scope": "example-temporal_scope"
  },
  "relation_id": "typed-relation:example-occurs-during",
  "relation_kind_ref": "relation.occurs-during",
  "source_ref": "failure-occurrence:example-001",
  "target_ref": "agent-action:example-001"
}
```

### `relation.originates-from`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "origin_role": "example-origin_role"
  },
  "relation_id": "typed-relation:example-originates-from",
  "relation_kind_ref": "relation.originates-from",
  "source_ref": "artifact-type:example-001",
  "target_ref": "source:example-001"
}
```

### `relation.performs`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "action_posture": "example-action_posture",
    "participation_role": "example-participation_role",
    "session_ref": "example-session_ref"
  },
  "relation_id": "typed-relation:example-performs",
  "relation_kind_ref": "relation.performs",
  "source_ref": "agent-instance:example-001",
  "target_ref": "agent-action:example-001"
}
```

### `relation.produces`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "action_receipt_ref": "example-action_receipt_ref",
    "output_posture": "example-output_posture",
    "production_role": "example-production_role"
  },
  "relation_id": "typed-relation:example-produces",
  "relation_kind_ref": "relation.produces",
  "source_ref": "agent-action:example-001",
  "target_ref": "agent-reflection:example-001"
}
```

### `relation.profiled-by`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "binding_ref": "example-binding_ref",
    "profile_version_ref": "example-profile_version_ref"
  },
  "relation_id": "typed-relation:example-profiled-by",
  "relation_kind_ref": "relation.profiled-by",
  "source_ref": "agent-instance:example-001",
  "target_ref": "agent-profile:example-001"
}
```

### `relation.realizes`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "exact_target_version_ref": "example-exact_target_version_ref",
    "realization_role": "example-realization_role"
  },
  "relation_id": "typed-relation:example-realizes",
  "relation_kind_ref": "relation.realizes",
  "source_ref": "experiment-run:example-001",
  "target_ref": "experiment-design:example-001"
}
```

### `relation.requests-resolution-of`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "context_version_ref": "example-context_version_ref"
  },
  "relation_id": "typed-relation:example-requests-resolution-of",
  "relation_kind_ref": "relation.requests-resolution-of",
  "source_ref": "context-request:example-001",
  "target_ref": "context:example-001"
}
```

### `relation.responds-to`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "intended_outcome": "example-intended_outcome",
    "response_role": "example-response_role"
  },
  "relation_id": "typed-relation:example-responds-to",
  "relation_kind_ref": "relation.responds-to",
  "source_ref": "agent-action:example-001",
  "target_ref": "failure-occurrence:example-001"
}
```

### `relation.scopes-authority-over`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "authority_role": "example-authority_role",
    "scope_ref": "example-scope_ref"
  },
  "relation_id": "typed-relation:example-scopes-authority-over",
  "relation_kind_ref": "relation.scopes-authority-over",
  "source_ref": "authority-claim:example-001",
  "target_ref": "decision-scope:example-001"
}
```

### `relation.successor-of`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "succession_effect": "example-succession_effect"
  },
  "relation_id": "typed-relation:example-successor-of",
  "relation_kind_ref": "relation.successor-of",
  "source_ref": "agent-action:example-001",
  "target_ref": "agent-action:example-001"
}
```

### `relation.tests-hypothesis`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "hypothesis_version_ref": "example-hypothesis_version_ref",
    "test_role": "example-test_role"
  },
  "relation_id": "typed-relation:example-tests-hypothesis",
  "relation_kind_ref": "relation.tests-hypothesis",
  "source_ref": "experiment-design:example-001",
  "target_ref": "hypothesis:example-001"
}
```

### `relation.uses-method`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "usage_role": "example-usage_role"
  },
  "relation_id": "typed-relation:example-uses-method",
  "relation_kind_ref": "relation.uses-method",
  "source_ref": "agent-action:example-001",
  "target_ref": "method:example-001"
}
```

### `relation.uses-tool`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "invocation_contract_ref": "example-invocation_contract_ref",
    "tool_version_ref": "example-tool_version_ref",
    "use_role": "example-use_role"
  },
  "relation_id": "typed-relation:example-uses-tool",
  "relation_kind_ref": "relation.uses-tool",
  "source_ref": "agent-action:example-001",
  "target_ref": "implementation:example-001"
}
```

### `relation.violates`

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Example demonstrates the exact pair and qualifiers only.",
  "evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "lifecycle_state": "candidate",
  "owner_ref": "role:relation-owner",
  "qualifiers": {
    "boundary_version_ref": "example-boundary_version_ref",
    "evidence_posture": "example-evidence_posture"
  },
  "relation_id": "typed-relation:example-violates",
  "relation_kind_ref": "relation.violates",
  "source_ref": "failure-occurrence:example-001",
  "target_ref": "challenge-contract:example-001"
}
```

## Claim ceiling

This candidate closes the reviewed global relation surface for the definition-complete Artifact Type model. It admits no Relation Kind, Typed Relation, Artifact Type, instance, ontology assertion, consumer, or runtime.
