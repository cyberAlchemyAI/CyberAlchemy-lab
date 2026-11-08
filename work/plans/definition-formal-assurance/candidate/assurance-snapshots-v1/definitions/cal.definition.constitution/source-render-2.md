<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Constitution

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.constitution`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Constitution is the normalized definition identified by semantic.constitution, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D58 without silently merging it with another target.

Bound source-semantic basis:

A constitution is an **owner-scoped, selector-bound, composable authority
artifact** that turns axioms and invariants into reusable governance rules and
policies for named kinds of governed subject. Those subjects may be artifacts,
tasks or workflows, repository-owned agent actions, system operations or state
transitions, validation surfaces, or authority movements.

A constitution must declare its scope, subject kinds, selectors, owner route,
authority level, rules and policies, precedence and composition behavior,
validation modes or bindings, downstream effect, challenge route, and retirement
or split conditions. It constrains a subject only after an owner decision adopts
the exact constitution version and scope and the subject matches its selectors.
A candidate, selected, or context-loaded constitution does not govern by those
facts alone.

```text
```text
Constitution C =
  (id, version, scope, subject_kinds, selectors, rules, policies,
   precedence, composition, owner_route, authority_level,
   validation_bindings, downstream_effect, challenge_route,
   retirement_or_split_rule)

subject_kinds(C) subset-of
  { artifact, task_or_workflow, repository_owned_agent_action,
    system_operation_or_state_transition, validation_surface,
    authority_movement }

applies(C, subject) <->
  promoted(C) and version_exact_owner_adoption(C) and
  subject in scope(C) and selector_matches(C, subject)

validation_mode(rule) in { deterministic, review, hybrid, none-yet }
candidate(C) or selected(C) or context_loaded(C) =/=> applies(C, subject)
```

Schema handle: `CAV2-D58-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary);
no machine validator is activated by this definition.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.constitution | Stable normalized identity for Constitution. |
| CAV2-D58 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- A constitution is **not** an axiom (`CAV2-D53`), invariant (`CAV2-D54`),
discipline (`CAV2-D50`), decision, validator, gate (`CAV2-D37`), evidence, or
proof. Axiom grounds; invariant states what must remain true; governance rule or
policy operationalizes; discipline stewards a recurring practice; owner decision
adopts; constitution carries the adopted constraints; validator or gate checks or
performs enforcement. Authority (`CAV2-D34`) scopes every part of that graph.

Promoting this term creates Definition authority for the meaning of
`constitution`. It does not promote any constitution artifact, adopt a rule or
policy, activate a validation binding, or authorize an effect.

### Testable conditions

- The candidate identity remains cal.definition.constitution.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

A constitution is a named rulebook for named things. It says which rules apply,
to what, under whose authority, and how conflicts and checks work. It is not a
universal prompt for every person, agent, repository, or external system.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Constitution is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, Constitution is one closed authority kind in
[AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md). The candidate
[Stable Repository Constitution](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
is an instance candidate; this definition does not promote or activate it. A
repository constitution cannot override system, developer, host, external-owner,
or other higher-precedence authority outside its declared scope.

### Examples

- Resolve semantic.constitution by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Constitution.

## Applicability

Use a constitution when a recurring class of future subjects needs the same
authoritative constraints, ownership, precedence, examples, and validation
expectations. Keep one-off advice, observations, and owner decisions outside it.
A discipline may gather evidence and route a constitution proposal, but cannot
author or adopt the constitution. A validator may check an adopted rule, but
cannot supply the authority that the constitution and owner decision provide.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- A constitution is **not** an axiom (`CAV2-D53`), invariant (`CAV2-D54`),
discipline (`CAV2-D50`), decision, validator, gate (`CAV2-D37`), evidence, or
proof. Axiom grounds; invariant states what must remain true; governance rule or
policy operationalizes; discipline stewards a recurring practice; owner decision
adopts; constitution carries the adopted constraints; validator or gate checks or
performs enforcement. Authority (`CAV2-D34`) scopes every part of that graph.

Promoting this term creates Definition authority for the meaning of
`constitution`. It does not promote any constitution artifact, adopt a rule or
policy, activate a validation binding, or authorize an effect.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D58 | ## CAV2-D58: Constitution | `19b1102f8a412f59fe7ec9e30ac474898ba662d117495f02e7b7a2110096a135` | `candidate-unadmitted` |

## Primary consumers

- semantic.axiom
- semantic.invariant

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.constitution@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.constitution | cyberalchemy-v2:CAV2-D58 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-constitution/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
