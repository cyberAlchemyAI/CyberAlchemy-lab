<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Intent

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.intent`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.coordination`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Intent is the normalized definition identified by semantic.intent, owned within scope.coordination, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D39 without silently merging it with another target.

Bound source-semantic basis:

Intent is the declared purpose, desired capability, problem pressure, or change
direction that orients a CyberAlchemy v2 method before the exact output shape,
artifact, gate, or implementation path is fully settled.

Intent must be attributable, bounded enough to route, revisable under discovery,
and traceable to the artifacts, decisions, residue, or next routes that claim to
satisfy it. An intent may be refined, split, renamed, or rejected, but it must
not be silently replaced by an artifact or implementation convenience.

```text
An admissible intent record has at least:

```text
Intent = (source, purpose, scope, constraints, target_pressure,
          current_output_hypothesis, revision_route)
```

The `current_output_hypothesis` may change as discovery proceeds. The intent
remains traceable only if the revision route records why the output changed.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.intent | Stable normalized identity for Intent. |
| CAV2-D39 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Intent is not a requirement, not an artifact, not proof, not a command to
mutate, and not automatic scope approval. It orients work; gates, authority,
evidence, and later artifact definitions decide what can count.

### Testable conditions

- The candidate identity remains cal.definition.intent.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

Intent is what the work is trying to make possible before we know the final
shape.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Intent is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, intent is the first input to the method stack: user
corrections, stable repository objectives, definition-promotion requests,
research questions, and handoff prompts all become governable when their intent
is named and traceable. This lets the project preserve why a definition or
route exists without treating the initial wording as immutable.

### Examples

- Resolve semantic.intent by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Intent.

## Applicability

Use intent at the start of definition, design, research, planning,
implementation, validation, or handoff work. Intent keeps the work oriented
while discovery decides whether the right output is a definition, constitution,
method, work-pack, validation report, code change, or deferred question.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Intent is not a requirement, not an artifact, not proof, not a command to
mutate, and not automatic scope approval. It orients work; gates, authority,
evidence, and later artifact definitions decide what can count.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D39 | ## CAV2-D39: Intent | `c2e92ab1679fcb8123668484298c84dfaae17180c84add44f0077dbbac01f5d2` | `candidate-unadmitted` |

## Primary consumers

None declared.

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.intent@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.intent | cyberalchemy-v2:CAV2-D39 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-intent/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
