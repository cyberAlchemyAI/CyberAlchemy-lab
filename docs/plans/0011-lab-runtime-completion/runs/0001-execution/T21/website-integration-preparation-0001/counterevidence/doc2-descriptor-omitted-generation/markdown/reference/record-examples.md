[Documentation home](../README.md)

<a id="record-examples"></a>

CyberAlchemy Lab / Reference examples

# Complete record examples

Inspect the required fields, then compare a record with one precise defect.

<a id="example-standing"></a>

## What these examples establish

These complete specimens use the selected schemas and invented `example:` identities with no registry standing. Structural validation leaves acceptance, claim support and permission to their own records. The links open local JSON.

[S1](../assets/6d523a998c2e-S1.json), [E12](../assets/948c8efdfd7e-E12.json) and the [comparison receipt](../assets/664dc1db6e72-comparison.json) reproduce the fixed case: 10,000 required identifiers, 9,800 exported and 200 confirmed missing.

<a id="example-work"></a>

## Work

Selected format: [cal.artifact-type.work/v1](records/type-cal-artifact-type-work-v1.md#type-cal-artifact-type-work-v1).

[Complete JSON](../assets/05c386e3fe28-work.json) · [Contrasting JSON](../assets/435ad87501ce-work-missing-field.json)

**One defect:** the contrasting record omits `/payload/project_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "schema_version": "cyberalchemy-lab-work/v1",
  "node_id": "example:work@1",
  "kind": "work",
  "name": "Work for the Northstar investigation",
  "lifecycle_state": "candidate",
  "authority_effect": "none",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "evidence_refs": [
    "example:comparison@1"
  ],
  "challenge_route": "example:owner-review",
  "successor_refs": [],
  "relation_refs": [
    {
      "relation_kind_ref": "relation.member-of",
      "direction": "source",
      "counterpart_kind": "project",
      "counterpart_ref": "example:project@1"
    }
  ],
  "payload": {
    "project_ref": "example:project@1",
    "goal_refs": [
      "example:goal@1"
    ],
    "work_statement": "Compare required identifiers from S1 for Northstar and status=active against E12; prepare a bounded omission assessment.",
    "input_refs": [
      "example:S1",
      "example:E12",
      "example:definition-completeness@1.0.0-candidate.1"
    ],
    "output_refs": [
      "example:comparison@1",
      "example:failure-assessment@1"
    ],
    "completion_state": "comparison saved; assessment prepared; owner review pending"
  },
  "claim_ceiling": "Documentation candidate only. It grants no access, admission, deployment or incident closure."
}
````

<a id="example-operational-observation"></a>

## Operational Observation

Selected format: [cal.artifact-type.operational-observation/v1](records/type-cal-artifact-type-operational-observation-v1.md#type-cal-artifact-type-operational-observation-v1).

[Complete JSON](../assets/5bccc2d2bcd9-operational-observation.json) · [Contrasting JSON](../assets/3d3bac1b9222-operational-observation-missing-field.json)

**One defect:** the contrasting record omits `/payload/project_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "schema_version": "cyberalchemy-lab-operational-observation/v1",
  "node_id": "example:operational-observation@1",
  "kind": "operational-observation",
  "name": "Operational Observation for the Northstar investigation",
  "lifecycle_state": "candidate",
  "authority_effect": "none",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "evidence_refs": [
    "example:comparison@1"
  ],
  "challenge_route": "example:owner-review",
  "successor_refs": [],
  "relation_refs": [
    {
      "relation_kind_ref": "relation.originates-from",
      "direction": "source",
      "counterpart_kind": "source",
      "counterpart_ref": "example:source@1"
    }
  ],
  "payload": {
    "project_ref": "example:project@1",
    "action_ref": "example:compare-action@1",
    "observed_at": "2026-10-11T10:04:00Z",
    "datum": "Identifier comparison found 200 required IDs absent from E12: 9801 through 10000.",
    "method_ref": "example:identifier-difference@2",
    "evidence_refs": [
      "example:comparison@1"
    ],
    "interpretation_posture": "Omission observed in the fixed scope; cause is unresolved."
  },
  "claim_ceiling": "Documentation candidate only. It grants no access, admission, deployment or incident closure."
}
````

<a id="example-evidence-set"></a>

## Evidence Set

Selected format: [cal.artifact-type.evidence-set/v1](records/type-cal-artifact-type-evidence-set-v1.md#type-cal-artifact-type-evidence-set-v1).

[Complete JSON](../assets/de917a73004d-evidence-set.json) · [Contrasting JSON](../assets/3554286b2676-evidence-set-missing-field.json)

**One defect:** the contrasting record omits `/payload/source_refs`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "schema_version": "cyberalchemy-lab-evidence-set/v1",
  "node_id": "example:evidence-set@1",
  "kind": "evidence-set",
  "name": "Evidence Set for the Northstar investigation",
  "lifecycle_state": "candidate",
  "authority_effect": "none",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "evidence_refs": [
    "example:comparison@1"
  ],
  "challenge_route": "example:owner-review",
  "successor_refs": [],
  "relation_refs": [
    {
      "relation_kind_ref": "relation.member-of",
      "direction": "source",
      "counterpart_kind": "project",
      "counterpart_ref": "example:project@1"
    }
  ],
  "payload": {
    "source_refs": [
      "example:S1",
      "example:E12"
    ],
    "item_refs": [
      "example:comparison@1",
      "example:operational-observation@1"
    ],
    "coverage_statement": "Identifier coverage for S1, Northstar, status=active, E12, using method 2.",
    "limitations": [
      "Values were not compared.",
      "Cause, other accounts, downstream impact and recovery were not established."
    ]
  },
  "claim_ceiling": "Documentation candidate only. It grants no access, admission, deployment or incident closure."
}
````

<a id="example-failure-occurrence"></a>

## Failure Occurrence

Selected format: [cal.artifact-type.failure-occurrence/v1](records/type-cal-artifact-type-failure-occurrence-v1.md#type-cal-artifact-type-failure-occurrence-v1).

[Complete JSON](../assets/15d6fdbeae23-failure-occurrence.json) · [Contrasting JSON](../assets/23d2f87c2914-failure-occurrence-missing-field.json)

**One defect:** the contrasting record omits `/payload/subject_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "schema_version": "cyberalchemy-lab-failure-occurrence/v1",
  "node_id": "example:failure-occurrence@1",
  "kind": "failure-occurrence",
  "name": "Failure Occurrence for the Northstar investigation",
  "lifecycle_state": "candidate",
  "authority_effect": "none",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "evidence_refs": [
    "example:comparison@1"
  ],
  "challenge_route": "example:owner-review",
  "successor_refs": [],
  "relation_refs": [
    {
      "relation_kind_ref": "relation.evidence-bears-on",
      "direction": "target",
      "counterpart_kind": "operational-observation",
      "counterpart_ref": "example:operational-observation@1"
    }
  ],
  "payload": {
    "subject_ref": "example:E12",
    "expected_boundary_ref": "example:definition-completeness@1.0.0-candidate.1",
    "observed_manifestations": [
      "200 required identifiers absent"
    ],
    "detection_evidence_refs": [
      "example:comparison@1"
    ],
    "occurrence_posture": "established in this fictional comparison",
    "cause_posture": "unresolved",
    "impact_refs": [],
    "response_action_refs": [
      "example:compare-action@1"
    ],
    "recovery_posture": "unestablished",
    "residue_refs": [
      "example:open-questions@1"
    ]
  },
  "claim_ceiling": "Documentation candidate only. It grants no access, admission, deployment or incident closure."
}
````

<a id="example-classification-assignment"></a>

## Classification Assignment

Selected format: [cal.artifact-type.classification-assignment/v1](records/type-cal-artifact-type-classification-assignment-v1.md#type-cal-artifact-type-classification-assignment-v1).

[Complete JSON](../assets/ca4f03b8ef45-classification-assignment.json) · [Contrasting JSON](../assets/d5f737c0db86-classification-assignment-missing-field.json)

**One defect:** the contrasting record omits `/payload/subject_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "schema_version": "cyberalchemy-lab-classification-assignment/v1",
  "node_id": "example:classification-assignment@1",
  "kind": "classification-assignment",
  "name": "Classification Assignment for the Northstar investigation",
  "lifecycle_state": "candidate",
  "authority_effect": "none",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "evidence_refs": [
    "example:comparison@1"
  ],
  "challenge_route": "example:owner-review",
  "successor_refs": [],
  "relation_refs": [
    {
      "relation_kind_ref": "relation.evidence-bears-on",
      "direction": "target",
      "counterpart_kind": "operational-observation",
      "counterpart_ref": "example:operational-observation@1"
    }
  ],
  "payload": {
    "subject_ref": "example:failure-occurrence@1",
    "subject_version_ref": "example:failure-occurrence@1",
    "scheme_version_ref": "example:failure-manifestation-scheme@1",
    "axis_ref": "example:observed-manifestation",
    "value_ref": "example:missing-required-identifiers",
    "basis": "Saved identifier difference; classification of manifestation only.",
    "action_ref": "example:classify-action@1",
    "method_ref": "example:classification-method@1",
    "implementation_ref": "example:manual-review@1",
    "evidence_refs": [
      "example:comparison@1"
    ],
    "effective_period": "this saved occurrence only",
    "status": "candidate"
  },
  "claim_ceiling": "Documentation candidate only. It grants no access, admission, deployment or incident closure."
}
````

<a id="example-failure-assessment"></a>

## Failure Assessment

Selected format: [cal.artifact-type.failure-assessment/v1](records/type-cal-artifact-type-failure-assessment-v1.md#type-cal-artifact-type-failure-assessment-v1).

[Complete JSON](../assets/4fcefe3b239d-failure-assessment.json) · [Contrasting JSON](../assets/110f924f2532-failure-assessment-missing-field.json)

**One defect:** the contrasting record omits `/payload/occurrence_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "schema_version": "cyberalchemy-lab-failure-assessment/v1",
  "node_id": "example:failure-assessment@1",
  "kind": "failure-assessment",
  "name": "Failure Assessment for the Northstar investigation",
  "lifecycle_state": "candidate",
  "authority_effect": "none",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "evidence_refs": [
    "example:comparison@1"
  ],
  "challenge_route": "example:owner-review",
  "successor_refs": [],
  "relation_refs": [
    {
      "relation_kind_ref": "relation.evidence-bears-on",
      "direction": "target",
      "counterpart_kind": "operational-observation",
      "counterpart_ref": "example:operational-observation@1"
    }
  ],
  "payload": {
    "occurrence_ref": "example:failure-occurrence@1",
    "mode_assignment_ref": "example:classification-assignment@1",
    "occurrence_posture": "established omission in E12",
    "mode_posture": "candidate classification: missing required identifiers; not a causal mechanism",
    "cause_hypothesis_refs": [],
    "impact_posture": "Output omission established; downstream uses and other accounts unresolved.",
    "containment_posture": "No containment established.",
    "recovery_posture": "No recovery established.",
    "uncertainty_refs": [
      "example:open-questions@1"
    ]
  },
  "claim_ceiling": "Documentation candidate only. It grants no access, admission, deployment or incident closure."
}
````

<a id="example-agent-assignment"></a>

## Agent Assignment

Selected format: [cal.artifact-type.agent-assignment/v1](records/type-cal-artifact-type-agent-assignment-v1.md#type-cal-artifact-type-agent-assignment-v1).

[Complete JSON](../assets/4ce8bd6029c4-agent-assignment.json) · [Contrasting JSON](../assets/8a408d7ce2c7-agent-assignment-missing-field.json)

**One defect:** the contrasting record omits `/payload/eligible_agent_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "schema_version": "cyberalchemy-lab-agent-assignment/v1",
  "node_id": "example:agent-assignment@1",
  "kind": "agent-assignment",
  "name": "Agent Assignment for the Northstar investigation",
  "lifecycle_state": "candidate",
  "authority_effect": "none",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "evidence_refs": [
    "example:comparison@1"
  ],
  "challenge_route": "example:owner-review",
  "successor_refs": [],
  "relation_refs": [
    {
      "relation_kind_ref": "relation.member-of",
      "direction": "source",
      "counterpart_kind": "project",
      "counterpart_ref": "example:project@1"
    }
  ],
  "payload": {
    "eligible_agent_ref": "example:agent-profile@1",
    "intent_ref": "example:intent@1",
    "project_ref": "example:project@1",
    "work_ref": "example:work@1",
    "owner_ref": "example:service-owner",
    "period": "2026-10-11T09:45:00Z/2026-10-11T10:15:00Z",
    "expected_output_refs": [
      "example:comparison@1",
      "example:failure-assessment@1"
    ],
    "stop_conditions": [
      "Pause if a selected view is unusable.",
      "Stop if the delegation expires or is revoked.",
      "Do not deploy or close the incident."
    ]
  },
  "claim_ceiling": "Documentation candidate only. It grants no access, admission, deployment or incident closure."
}
````

<a id="example-delegation"></a>

## Delegation

Selected format: [cal.artifact-type.delegation/v1](records/type-cal-artifact-type-delegation-v1.md#type-cal-artifact-type-delegation-v1).

The candidate describes a permission envelope, without issuing a real grant. Check the delegator’s authority and exact decision before acting.

[Complete JSON](../assets/9b4c141e3ac6-delegation.json) · [Contrasting JSON](../assets/1b30dccf324e-delegation-missing-field.json)

**One defect:** the contrasting record omits `/payload/delegator_principal_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "schema_version": "cyberalchemy-lab-delegation/v1",
  "node_id": "example:delegation@1",
  "kind": "delegation",
  "name": "Delegation for the Northstar investigation",
  "lifecycle_state": "candidate",
  "authority_effect": "none",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "evidence_refs": [
    "example:comparison@1"
  ],
  "challenge_route": "example:owner-review",
  "successor_refs": [],
  "relation_refs": [
    {
      "relation_kind_ref": "relation.declares-effect-on",
      "direction": "target",
      "counterpart_kind": "decision",
      "counterpart_ref": "example:decision@1"
    }
  ],
  "payload": {
    "delegator_principal_ref": "example:service-owner",
    "eligible_agent_ref": "example:agent-profile@1",
    "scope_refs": [
      "example:Northstar:S1:status-active:E12"
    ],
    "allowed_action_kinds": [
      "inspect-saved-inputs",
      "compare-identifiers",
      "record-candidate-through-approved-route",
      "prepare-proposal"
    ],
    "policy_refs": [
      "example:investigation-policy@1"
    ],
    "approval_gate_refs": [
      "example:owner-review@1"
    ],
    "effective_period": "2026-10-11T09:45:00Z/2026-10-11T10:15:00Z",
    "revocation_state": "not revoked in this invented scenario",
    "redelegation_allowed": false
  },
  "claim_ceiling": "Documentation candidate only. It grants no access, admission, deployment or incident closure."
}
````

<a id="example-agent-session"></a>

## Agent Session

Selected format: [cal.artifact-type.agent-session/v1](records/type-cal-artifact-type-agent-session-v1.md#type-cal-artifact-type-agent-session-v1).

[Complete JSON](../assets/4f6b86053b94-agent-session.json) · [Contrasting JSON](../assets/47bb498e2ef2-agent-session-missing-field.json)

**One defect:** the contrasting record omits `/payload/agent_instance_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "schema_version": "cyberalchemy-lab-agent-session/v1",
  "node_id": "example:agent-session@1",
  "kind": "agent-session",
  "name": "Agent Session for the Northstar investigation",
  "lifecycle_state": "candidate",
  "authority_effect": "none",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "evidence_refs": [
    "example:comparison@1"
  ],
  "challenge_route": "example:owner-review",
  "successor_refs": [],
  "relation_refs": [
    {
      "relation_kind_ref": "relation.consumes-view",
      "direction": "source",
      "counterpart_kind": "context-view",
      "counterpart_ref": "example:context-view@1"
    }
  ],
  "payload": {
    "agent_instance_ref": "example:agent-instance-12@1",
    "assignment_ref": "example:agent-assignment@1",
    "context_view_ref": "example:context-view-3@1",
    "ontology_view_ref": "example:ontology-view-3@1",
    "policy_refs": [
      "example:investigation-policy@1"
    ],
    "authority_envelope_ref": "example:delegation@1",
    "input_refs": [
      "example:S1",
      "example:E12"
    ],
    "budget_refs": [
      "example:30-minute-budget"
    ],
    "event_cursor": "example:session-12-event-7",
    "session_memory": {
      "selected_input_refs": [
        "example:S1",
        "example:E12"
      ],
      "working_record_refs": [
        "example:failure-assessment@1"
      ],
      "unresolved_questions": [
        "What caused the omission?",
        "What is the wider impact?",
        "Has recovery occurred?"
      ],
      "expires_with_session": true
    },
    "termination_state": "paused at 10:10 because task view 3 expired; end instance when session terminates"
  },
  "claim_ceiling": "Documentation candidate only. It grants no access, admission, deployment or incident closure."
}
````

<a id="example-context-view"></a>

## Context View

Selected format: [cal.artifact-type.context-view/v1](records/type-cal-artifact-type-context-view-v1.md#type-cal-artifact-type-context-view-v1).

This view expires at 10:10 UTC. Its schema can still validate afterward while the task information is unusable.

[Complete JSON](../assets/59c820db2c3f-context-view.json) · [Contrasting JSON](../assets/1f71b6823703-context-view-missing-field.json)

**One defect:** the contrasting record omits `/owner_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "authority_effect": "none",
  "kind": "context-view",
  "node_id": "example:context-view-3@1",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "status": "candidate-unadmitted",
  "request_ref": "example:context-request@1",
  "context_ref": "example:context@1",
  "context_version_ref": "example:context@3",
  "source_epoch": "example:project-epoch@3",
  "generated_at": "2026-10-11T09:50:00Z",
  "expires_at": "2026-10-11T10:10:00Z",
  "included_material": [
    {
      "source_ref": "example:S1",
      "selector": "required_ids for account=Northstar and status=active",
      "sha256": "6d523a998c2e87235ebdc788c41e8bfd7ae0d64d8ee7409b8328b2edf9a5eefb"
    },
    {
      "source_ref": "example:E12",
      "selector": "exported_ids",
      "sha256": "948c8efdfd7ee9cfc663cd03956ee361174c19e60eaa46379538fd1114bc739d"
    }
  ],
  "excluded_material": [
    {
      "source_ref": "example:other-accounts",
      "reason": "Outside the task scope."
    }
  ],
  "lineage_refs": [
    "example:project-state@3"
  ],
  "limitations": [
    "The view grants no permission.",
    "Unusable at or after its expiry."
  ],
  "selection_basis": "Task request selects the fixed input and saved output for identifier comparison.",
  "owner_route": "example:service-owner-review",
  "challenge_route": "example:view-challenge",
  "claim_ceiling": "Documentation candidate; no view generated by the Lab and no permission conveyed."
}
````

<a id="example-measurement-method"></a>

## Measurement Method

Selected format: [cal.artifact-type.measurement-method/v1](records/type-cal-artifact-type-measurement-method-v1.md#type-cal-artifact-type-measurement-method-v1).

The selected carrier is specifically for residue entropy, despite the broader semantic meaning. The separate [toy model](../assets/f9bce4589788-finite-residue-model.json) has five equally likely states, H = log₂(5) ≈ 2.322 bits. It contributes no Northstar evidence. Save the incident count in its comparison and observation.

[Complete JSON](../assets/f886d2859240-measurement-method.json) · [Contrasting JSON](../assets/7669bb311f27-measurement-method-missing-field.json)

**One defect:** the contrasting record omits `/owner_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "authority_effect": "none",
  "kind": "measurement-method",
  "node_id": "example:uniform-residue-entropy@1",
  "owner_ref": "example:model-owner",
  "scope_ref": "example:finite-residue-model@1",
  "status": "candidate-unadmitted",
  "name": "Entropy of five equally likely residue states",
  "property": "residue entropy",
  "entropy_register": "finite-microcanonical",
  "source_operation_ref": "example:toy-source-operation@1",
  "residue_type_ref": "example:five-distinguishable-residue-states@1",
  "observable_kind": "shannon-entropy",
  "mathematical_reading": "For five equally likely distinguishable states, H = -sum(p_i log2(p_i)) = log2(5).",
  "scope_kind": "finite",
  "procedure": "Select the five-state model, verify the declared equal probabilities, compute log2(5) and save the receipt.",
  "conditions": [
    "Exactly five distinct states.",
    "Each probability is 0.2.",
    "Probabilities sum to one."
  ],
  "unit": "bits",
  "uncertainty_rule": "Zero model-input uncertainty under the stated toy assumptions; floating-point result rounded to 15 decimal places.",
  "claim_status": "review",
  "authority_treatment": "non-governing",
  "interpretation": "Uncertainty among five declared model states; supplies no evidence about the Northstar omission or its cause.",
  "owner_route": "example:model-owner-review",
  "challenge_route": "example:measurement-challenge",
  "claim_ceiling": "Documentation candidate method for a toy model only; no incident measurement or authority."
}
````

<a id="example-measurement-result"></a>

## Measurement Result

Selected format: [cal.artifact-type.measurement-result/v1](records/type-cal-artifact-type-measurement-result-v1.md#type-cal-artifact-type-measurement-result-v1).

The selected carrier is specifically for residue entropy, despite the broader semantic meaning. The separate [toy model](../assets/f9bce4589788-finite-residue-model.json) has five equally likely states, H = log₂(5) ≈ 2.322 bits. It contributes no Northstar evidence. Save the incident count in its comparison and observation.

[Complete JSON](../assets/48c789b1f1cd-measurement-result.json) · [Contrasting JSON](../assets/032da0ecb80d-measurement-result-missing-field.json)

**One defect:** the contrasting record omits `/owner_ref`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "authority_effect": "none",
  "kind": "measurement-result",
  "node_id": "example:measurement-result@1",
  "owner_ref": "example:service-owner",
  "scope_ref": "example:finite-residue-model@1",
  "status": "candidate-unadmitted",
  "method_ref": "example:uniform-residue-entropy@1",
  "subject_ref": "example:finite-residue-model@1",
  "residue_ref": "example:five-distinguishable-residue-states@1",
  "source_operation_ref": "example:toy-source-operation@1",
  "entropy_register": "finite-microcanonical",
  "observable_kind": "shannon-entropy",
  "mathematical_reading": "H = log2(5) bits under the five-state uniform model.",
  "scope_kind": "finite",
  "value": 2.321928094887362,
  "unit": "bits",
  "uncertainty": {
    "value": 0,
    "interpretation": "No input uncertainty within the invented model; rounding applies to the floating-point representation."
  },
  "claim_status": "review",
  "authority_treatment": "non-governing",
  "observed_at": "2026-10-11T10:04:00Z",
  "evidence_ref": "example:finite-residue-model@1",
  "receipt_ref": "example:finite-model-computation@1",
  "owner_route": "example:model-owner-review",
  "challenge_route": "example:measurement-challenge",
  "claim_ceiling": "Toy-model documentation result; no incident omission measurement or accepted finding."
}
````

<a id="example-definition"></a>

## Definition

Selected format: [cal.artifact-type.definition/v2](records/type-cal-artifact-type-definition-v2.md#type-cal-artifact-type-definition-v2).

The criterion binds snapshot, account, filters and output. Source posture, index synchronization and acceptance still need review. The all-zero generator digest marks an unresolved binding and must be replaced with the actual selected Definition generator digest before reliance. Correct values are outside identifier coverage.

[Complete JSON](../assets/bcca827cd23a-definition.json) · [Contrasting JSON](../assets/d7521435a944-definition-missing-field.json)

**One defect:** the contrasting record omits `/scope/applicability`. The selected schema rejects that omission.

### Read the complete specimen

````json
{
  "schema_version": "cyberalchemy-lab-definition/v2",
  "definition_id": "example.definition.export-identifier-completeness",
  "version": "1.0.0-candidate.1",
  "term": "Export identifier completeness",
  "aliases": [],
  "classification": {
    "artifact_type_ref": "cal.artifact-type.definition/v2",
    "semantic_kind": "definition",
    "authority_kind": "semantic-authority",
    "lifecycle_posture_ref": "example:candidate-authored"
  },
  "semantic_owner_ref": "example:service-owner",
  "scope": {
    "authority_scope_ref": "example:Northstar:S1:status-active:E12",
    "applicability": "Identifier coverage of an export E from fixed snapshot S, declared account A and filters F.",
    "exclusions": [
      "Value accuracy.",
      "Live-source consistency.",
      "Access permission.",
      "Incident recovery or closure."
    ]
  },
  "voices": {
    "scientific_formal": {
      "normative_statement": "For a fixed input snapshot S, account A, filters F and output E, export identifier completeness holds exactly when every identifier required by S, A and F appears in E.",
      "formal_expression": "CompleteIds(S,A,F,E) iff RequiredIds(S,A,F) subseteq ExportedIds(E).",
      "notation": [
        {
          "symbol": "S",
          "meaning": "Fixed input snapshot"
        },
        {
          "symbol": "A",
          "meaning": "Declared account"
        },
        {
          "symbol": "F",
          "meaning": "Declared filters"
        },
        {
          "symbol": "E",
          "meaning": "Saved export output"
        }
      ],
      "boundary_conditions": [
        "S, A, F and E must be fixed and identified before applying the criterion.",
        "Extra identifiers require a separate exclusivity criterion."
      ],
      "testable_conditions": [
        "For S1, Northstar, status=active and E12, the saved comparison has 200 missing required identifiers."
      ]
    },
    "plain_language": {
      "normative": false,
      "explanation": "Every required row identifier for the chosen account and filters must appear in the output."
    },
    "domain_context": {
      "normative": false,
      "workspace_ref": "example:Northstar-investigation",
      "explanation": "The Northstar agent uses this proposed criterion to examine the saved export.",
      "examples": [
        "S1, Northstar, status=active, E12: incomplete by identifier coverage."
      ]
    }
  },
  "boundaries": [
    "S, A, F and E must be fixed and identified before applying the criterion.",
    "Extra identifiers require a separate exclusivity criterion."
  ],
  "source_refs": [],
  "primary_consumer_refs": [
    "example:work@1",
    "example:failure-assessment@1"
  ],
  "index_entry": {
    "index_ref": "example:proposed-definition-index",
    "entry_id": "example.definition.export-identifier-completeness"
  },
  "drift_route": {
    "owner_ref": "example:service-owner",
    "audit_ref": "example:definition-drift-review",
    "challenge_ref": "example:definition-challenge"
  },
  "source_direction": {
    "canonical": "definition.json",
    "human_projection": "DEFINITION.md",
    "projection_policy": "generated-only",
    "generator_ref": "cal.generator.definition-markdown/v2",
    "generator_sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "schema_ref": "cal.schema.definition/v2",
  "schema_digest": "269591e7f0dd7c1c077579dd874599ba08fa8e17df10fa262d936f8ad5519181",
  "evidence_refs": [
    "example:criterion-proposal"
  ],
  "residue_refs": [
    "example:source-posture-and-owner-acceptance-pending",
    "example:definition-generator-digest-unresolved"
  ],
  "typed_relations": [],
  "claim_ceiling": "Schema-complete documentation specimen. Admitted source posture, registry synchronization and an exact owner decision still require independent review."
}
````

<a id="connection-examples"></a>

## Read a declared connection

A local connection reference still needs its complete assertion. The patterns below take ordered kinds and qualifiers from the selected rule. They supply no permission.

### member-of

`work` → **member-of** → `project`

````json
{
  "membership_role": "incident investigation"
}
````

**Counterexample:** reversing these endpoint kinds fails the declared ordered signature. An arrow drawn in an explanatory diagram does not declare a new connection.

### evidence-bears-on

`operational-observation` → **evidence-bears-on** → `failure-assessment`

````json
{
  "polarity": "supports scoped occurrence only"
}
````

**Counterexample:** reversing these endpoint kinds fails the declared ordered signature. An arrow drawn in an explanatory diagram does not declare a new connection.

### acts-for

`agent-instance` → **acts-for** → `principal`

````json
{
  "delegation_ref": "example:delegation@1",
  "scope_ref": "example:Northstar:S1:status-active:E12",
  "effective_period": "09:45–10:15 UTC",
  "revocation_state": "not revoked in the scenario"
}
````

**Counterexample:** reversing these endpoint kinds fails the declared ordered signature. An arrow drawn in an explanatory diagram does not declare a new connection.

### consumes-view

`agent-session` → **consumes-view** → `context-view`

````json
{
  "view_digest": "Northstar bounded investigation",
  "cursor": "Northstar bounded investigation",
  "consumption_purpose": "identifier comparison"
}
````

**Counterexample:** reversing these endpoint kinds fails the declared ordered signature. An arrow drawn in an explanatory diagram does not declare a new connection.

<a id="definition-boundary"></a>

## Recognize a semantic boundary

Suppose the required identifiers are all present while several email values are wrong. Identifier coverage is satisfied; value accuracy still needs its own criterion. The example exposes a claim boundary rather than a malformed record.

[Prepare an incident assessment →](../how-to/prepare-incident-assessment.md)
